# Ticket Master

GitHub Issues for Sublime.

Ticket Master allows you to create/open GitHub issues from Sublime Text by simply typing TODO comments.

## Installation/Usage

 1. Install [Package Control](https://sublime.wbond.net/installation)

 1. Run `Install Package` from the [Command Palette](http://sublime-text-unofficial-documentation.readthedocs.org/en/latest/reference/command_palette.html)

 1. Select `TicketMaster`

 1. Type a comment in your file starting with `TODO`

 1. Run `TicketMaster: Create/Open Issue` from the Command Palette.

 1. Follow the directions to setup TicketMaster. The token you create will be local to your machine and can be deleted any time with the `TicketMaster: Remove Token` command.

 1. An issue will be created in GitHub and a link will be placed at the end of your comment

 1. If desired, run `TicketMaster: Create/Open Issue` again on a line that is already linked to an issue to launch the GitHub issue tracker.

 1. If you use this frequently you may want to create a keyboard shortcut. Do this by selecting `Key Bindings - User` from the `Preferences` menu and entering the following:
 ```
 [
 	<any existing bindings>,
 	{"keys": ["ctrl+shift+i"], "command": "createissue"}]
 ]
 ```

## Extra Features

 * If you just want to create an issue without a TODO tag run `TicketMaster: Create/Open Issue` on a line that doesn't contain the text TODO

 * You can submit mutliple TODOs at once by selecting all the lines in a file and running `TicketMaster: Create/Open Issue`

## Status

This is an early alpha. Please contact Amit at amit@amit-bansil.com with feedback.

## Coming Soon

Close issues from Sublime

Unit Tests

## Terms

Use of this library is subject to a 100% service charge.

```
Burns: [chuckles] And to think, Smithers: you laughed when I bought
	  TicketMaster. "Nobody's going to pay a 100% service charge."
Smithers: Well, it's a policy that ensures a healthy mix of the rich
	  and the ignorant, sir.
```
