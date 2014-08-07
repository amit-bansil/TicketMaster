import sublime, sublime_plugin, webbrowser
import os.path as path
import subprocess, traceback

import re

ISSUE_LINK_REGEX = (
	'\[(' + # capture everything after an open bracket
	'github\.com\/' + # that starts with github.com
	'[^\]]*' + # followed by everything that isn't a close bracket
	')\]') # followed by a close bracket (outside the capturing group)

ISSUE_REGEX = 'TODO\:?(.*)'

SSH_PREFIX = 'git@github.com:'
HTTPS_PREFIX = 'https://'
GITHUB_PREFIX = 'github.com/'
GIT_SUFFIX = '.git'

TOKEN_URL = 'https://github.com/settings/tokens/new?scopes=repo,public_repo'

class CreateissueCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		
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

		
		# Write url in file
		self.view.insert(edit, point, "aba zaba")

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