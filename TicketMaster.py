import sublime, sublime_plugin, webbrowser

import re

ISSUE_LINK_REGEX = (
	'\[(' + # capture everything after an open bracket
	'github\.com\/' + # that starts with github.com
	'[^\]]*' + # followed by everything that isn't a close bracket
	')\]') # followed by a close bracket (outside the capturing group)

ISSUE_REGEX = 'TODO\:?(.*)'

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
		pass

	def push_issue(self, edit, point, title):
		print(title, edit, point)
		self.view.insert(edit, point, "aba zaba")

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
	webbrowser.open_new_tab('https://' + url)