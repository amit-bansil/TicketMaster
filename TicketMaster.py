import sublime, sublime_plugin, webbrowser

import re

ISSUE_LINK_REGEX = ('\[(' + # capture everything after an open bracket
				    'github\.com\/' + # that starts with github.com
				    '[^\]]*' + # followed by everything that isn't a close bracket
				    ')\]') # followed by a close bracket (outside the capturing group)



class CreateissueCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		something_happened = False
		for region in view.sel():
			lines = view.line(region)
			lines = view.substr(lines)

			for aline in lines.split('\n'):			
				
				issue_url = extract_issue_link(aline)

				if issue_url:
					open_url(issue_url) 
					something_happened = True
				else:
					title = extract_issue_title(aline)
					if title:
						push_issue(atitle) 
						something_happened = True

		if not something_happened:
			push_issue(None)



def extract_issue_link(lines):
	return re.findall(ISSUE_LINK_REGEX, lines)[-1]

def open_url(url):
	webbrowser.open_new_tab('https://' + url)