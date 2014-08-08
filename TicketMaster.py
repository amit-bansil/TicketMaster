import sublime, sublime_plugin
import os.path as path
import subprocess
import webbrowser
import traceback
import http.client as httplib
import base64
import json
import re

from urllib.parse import urlparse

ISSUE_LINK_REGEX = (
	'\[(' + # capture everything after an open bracket
	'github\.com\/' + # that starts with github.com
	'[^\]]*' + # followed by everything that isn't a close bracket
	')\]') # followed by a close bracket (outside the capturing group)

ISSUE_REGEX = 'TODO\:?(.*)'

SSH_PREFIX = 'git@github.com:'
HTTPS_PREFIX = 'https://'
GITHUB_API_PREFIX = 'api.'
GITHUB_PREFIX = 'github.com/'
GIT_SUFFIX = '.git'

TOKEN_URL = 'github.com/settings/tokens/new?scopes=repo,public_repo'
TOKEN_KEY = 'tm-github-token'

PREFERENCES_FILE = 'Preferences.sublime-settings'

class CreateissueCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		
		# Check if the user is already logged in.
		print(self.get_github_token())

		view = self.view
		something_happened = False
		for regionOfLines in view.sel():
			# must reverse lines or edits to selection will interfere with lookups
			for lineSubRegion in reversed(view.split_by_newlines(regionOfLines)):
				fullLineRegion = view.line(lineSubRegion)
				line = view.substr(fullLineRegion)
				issue_url = extract_issue_link(line)

				if issue_url:
					open_url(issue_url) 
					something_happened = True
				else:
					title = extract_issue_title(line)
					print('title', title)
					if title:
						self.push_issue(edit, fullLineRegion.end(), title)
						something_happened = True

		if not something_happened:
			self.create_new_issue()

	def create_new_issue(self):
		url = GITHUB_PREFIX + self.get_github_repo() + "/issues/new"
		open_url(url)

	def push_issue(self, edit, point, title):

		token = self.get_github_token()
		url = HTTPS_PREFIX + GITHUB_API_PREFIX + GITHUB_PREFIX + "repos/" + self.get_github_repo() + "/issues"

		print(url)

		res = authenticated_post(url, token, json.dumps({'title':title}))
		res_body = res.read().decode('utf-8')
		print(res_body)

		if res.status == 201:
			try:
				res_params = json.loads(res_body) 
				issue = res_params.get('html_url')
				print(issue)
				# Write url in file
				self.view.insert(edit, point, ' [{}]'.format(issue[len(HTTPS_PREFIX):]))
			except:
				panic("Crash reading github JSON")
		else:
			panic("Problem connecting to Github: (Error {0}) {1}".format(res.status, res_body))

	def get_github_repo(self):
		file_dir = self.get_file_directory()
		try: 
			output = subprocess.check_output(["git", "ls-remote","--get-url"], cwd=file_dir)
			output = output.decode("utf-8")
			if output.startswith(HTTPS_PREFIX+GITHUB_PREFIX):
				output = output[len(HTTPS_PREFIX)+len(GITHUB_PREFIX):]
			elif output.startswith(SSH_PREFIX):
				output = output[len(SSH_PREFIX):]
			else:
				panic("Upstream remote is not a github repository. Got " + output + " instead.")

			return output[:-len(GIT_SUFFIX)-1]

		except:
			traceback.print_exc()
			print(file_dir)
			panic("Couldn't determine github repository based on ls-remote. " +
				"Try running: git ls-remote --get-url in "+file_dir)

	def get_file_directory(self):
		filepath = self.view.file_name()
		if not filepath:
			panic("File hasn't been saved")

		return path.dirname(filepath)

	def get_github_token(self):
		s = sublime.load_settings(PREFERENCES_FILE)
		t = s.get(TOKEN_KEY, None)

		if not t:
			panic("You need to setup Ticket Master running the Setup command.")
		return t

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

def open_url(url):
	webbrowser.open_new_tab(HTTPS_PREFIX + url)

def panic(error):
	sublime.error_message("Ticket Master Error: " + error)
	raise Exception(error)

class SetuptokenCommand(sublime_plugin.WindowCommand):
	def run(self):
		sublime.message_dialog("You are being redirected to Github. Create a token with that scope and paste it in the box below.")
		self.window.show_input_panel("Your github token: ", "", self.save, None, None)
		open_url(TOKEN_URL)

	def save(self, token):
		s = sublime.load_settings(PREFERENCES_FILE)
		t = s.set(TOKEN_KEY, token)
		sublime.save_settings(PREFERENCES_FILE)

class RemovetokenCommand(sublime_plugin.ApplicationCommand):
	def run(self):
		s = sublime.load_settings(PREFERENCES_FILE)
		s.erase(TOKEN_KEY)
		sublime.save_settings(PREFERENCES_FILE)

def request(method, url, options=None):
	options = options or {}

	url = urlparse(url)
	host = url.netloc
	path = url.path

	if options.get('ssl'):
		conn = httplib.HTTPSConnection(host)
	else:
		conn = httplib.HTTPConnection(host)

	body = options.get('body', options.get('params', ''))
	headers = options.get('headers', {})

	conn.request(method, path, body, headers)
	return conn.getresponse()

def authenticated_post(url, token, params=None):
	params = params or {}

	print('{0}:{1}'.format(token, ''))
	print('{0}:{1}'.format(token, '').encode('utf-8'))

	encoded_userpass = base64.b64encode('{0}:{1}'.format(token, '').encode('utf-8')) #TODO fix bug
	auth_string = 'Basic {0}'.format(encoded_userpass.decode('utf-8'))

	options = {'params': params,
			   'ssl': True,
			   'headers': {'Authorization': auth_string,
						   'Content-type': 'application/x-www-form-urlencoded',
						   'User-Agent': 'ticketmaster'}}

	print(options)

	return request('POST', url, options)
