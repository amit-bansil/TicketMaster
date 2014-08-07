import sublime, sublime_plugin, webbrowser

import re

ISSUE_LINK_REGEX = ('\[(' + # capture everything after an open bracket
				    'github\.com\/' + # that starts with github.com
				    '[^\]]*' + # followed by everything that isn't a close bracket
				    ')\]') # followed by a close bracket (outside the capturing group)

class CreateissueCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		for region in view.sel():
			lines = view.line(region)
			lines = view.substr(lines)

			issue_urls = extract_issue_links(lines)
			if issue_urls:
				for url in issue_urls:
					open_url(url) 
			else:
				titles = extract_issue_titles(lines)
				if titles:
					for atitle in titles:
						push_issue(atitle) 
				else:
					push_issue(None)



def extract_issue_links(lines):
	return re.findall(ISSUE_LINK_REGEX, lines)

def open_url(url):
	webbrowser.open_new_tab('https://' + url)