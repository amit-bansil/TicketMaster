import os.path as path
import sys
import subprocess
import webbrowser
import http.client as httplib
import base64
import json
import re
from urllib.parse import urlparse

import sublime
import sublime_plugin

# Add this dir to path
sys.path.append(path.dirname(__file__))
import uicopy

# TODO autoclose issues [github.com/amit-bansil/TicketMaster/issues/19]
# TODO fix crash on select all [github.com/amit-bansil/TicketMaster/issues/13]
# TODO handle network errors [github.com/amit-bansil/TicketMaster/issues/14]

ISSUE_LINK_REGEX = re.compile(r"""
 \[(            # capture everything after an open bracket
 github\.com\/  # that starts with github.com
 [^\]]*         # followed by everything that isn't a close bracket
 )\]            # followed by a close bracket (outside the capturing group)
""", re.VERBOSE)

ISSUE_REGEX     = 'TODO\:?(.*)'
GITHUB_DOMAIN   = 'github.com/'
REPO_SSH_PREFIX = 'git@github.com:'
ISSUE_API_URL_PATTERN = 'https://api.' + GITHUB_DOMAIN + 'repos/{repo}/issues'
NEW_ISSUE_URL_PATTERN = GITHUB_DOMAIN + '{repo}/issues/new'
GIT_SUFFIX      = '.git'
LS_REMOTE_CMD   = 'git ls-remote --get-url'.split()
TOKEN_URL       = GITHUB_DOMAIN + 'settings/tokens/new?scopes=repo,public_repo'
TOKEN_KEY       = 'tm-github-token'

PREFERENCES_FILE = 'Preferences.sublime-settings'


class CreateissueCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        something_happened = False
        # deal with case where use has selected multiple edits
        for regionOfLines in view.sel():
            splitRegionsOfLines = view.split_by_newlines(regionOfLines)
            # reverse lines or edits to selection will interfere with lookups
            for lineSubRegion in reversed(splitRegionsOfLines):
                fullLineRegion = view.line(lineSubRegion)
                line = view.substr(fullLineRegion)
                issue_url = extract_issue_link(line)

                if issue_url:
                    open_url(issue_url)
                    something_happened = True
                else:
                    title = extract_issue_title(line)
                    if title:
                        self.push_issue(edit, fullLineRegion.end(), title)
                        something_happened = True

        if not something_happened:
            open_url(NEW_ISSUE_URL_PATTERN.format(repo=self.get_github_repo()))

    def push_issue(self, edit, point, title):
        github_token = self.get_github_token()
        create_url = ISSUE_API_URL_PATTERN.format(repo=self.get_github_repo())

        res = authenticated_post(create_url, github_token, {'title': title})
        res_body = res.read().decode('utf-8')
        if res.status == 201:
            try:
                res_params = json.loads(res_body)
            except ValueError:
                panic(uicopy.PANIC_INVALID_GITHUB_JSON)

            issue = res_params.get('html_url')
            # Write url in file
            issue_link = ' [{}]'.format(issue[len('https://'):])
            self.view.insert(edit, point, issue_link)
        else:
            panic(uicopy.PANIC_PUSH_ISSUE_FAILS.format({
                'status': res.status,
                'body'  : res_body
            }))

    def get_github_repo(self):
        file_dir = self.get_file_directory()

        try:
            output = subprocess.check_output(LS_REMOTE_CMD, cwd=file_dir)
        except CalledProcessError:
            panic(uicopy.PANIC_GIT_LS_REMOTE_FAILS.format(file_dir=file_dir))

        output = output.decode('utf-8')
        output = trim_suffix(output, GIT_SUFFIX)
        https_repo = trim_prefix(output, 'https://' + GITHUB_DOMAIN)
        ssh_repo   = trim_prefix(output, REPO_SSH_PREFIX)

        if https_repo:
            return https_repo
        elif ssh_repo:
            return ssh_repo
        else:
            msg = uicopy.PANIC_UPSTREAM_REPO_NOT_GITHUB
            panic(msg.format(output=output))

    def get_file_directory(self):
        filepath = self.view.file_name()
        if not filepath:
            panic(uicopy.PANIC_NOT_SAVED)

        return path.dirname(filepath)

    def get_github_token(self):
        settings = sublime.load_settings(PREFERENCES_FILE)
        token = settings.get(TOKEN_KEY, None)

        if token:
            return token
        else:
            panic(uicopy.PANIC_NOT_SETUP)


def extract_issue_title(line):
    matches = re.findall(ISSUE_REGEX, line)
    if matches:
        return matches[-1]
    else:
        return None


def extract_issue_link(line):
    matches = re.findall(ISSUE_LINK_REGEX, line)
    if matches:
        return matches[-1]
    else:
        return None


class SetuptokenCommand(sublime_plugin.WindowCommand):

    def run(self):
        sublime.message_dialog(uicopy.PROMPT_INPUT_TOKEN)
        self.window.show_input_panel(uicopy.INPUT_TOKEN_LABEL,
                                     "", self.save, None, None)
        open_url(TOKEN_URL)

    def save(self, token):
        settings = sublime.load_settings(PREFERENCES_FILE)
        settings.set(TOKEN_KEY, token)
        sublime.save_settings(PREFERENCES_FILE)


class RemovetokenCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        settings = sublime.load_settings(PREFERENCES_FILE)
        settings.erase(TOKEN_KEY)
        sublime.save_settings(PREFERENCES_FILE)

#utility functions

def open_url(url):
    webbrowser.open_new_tab('https://' + url)


def panic(error):
    sublime.error_message("Error: " + error)
    raise Exception(error)


def authenticated_post(url, token, params=None):
    if params:
        params = json.dumps(params)
    else:
        params = {}

    auth_token = '{0}:{1}'.format(token, '').encode('utf-8')
    encoded_auth_token = base64.b64encode(auth_token)  # TODO fix bug
    auth_string = 'Basic {0}'.format(encoded_auth_token.decode('utf-8'))

    headers = {
        'Authorization': auth_string,
        'Content-type': 'application/x-www-form-urlencoded',
        'User-Agent': 'ticketmaster'
    }

    options = {
        'params': params,
        'ssl': True,
        'headers': headers
    }

    return request('POST', url, options)


def request(method, url, options=None):
    options = options or {}

    url = urlparse(url)
    host = url.netloc
    path = url.path

    if 'ssl' in options:
        conn = httplib.HTTPSConnection(host)
    else:
        conn = httplib.HTTPConnection(host)

    body = options.get('body', options.get('params', ''))
    headers = options.get('headers', {})

    conn.request(method, path, body, headers)
    return conn.getresponse()


def trim_suffix(string, suffix):
    return string[:-len(suffix) - 1]


def trim_prefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return None
