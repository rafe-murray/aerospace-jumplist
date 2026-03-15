# Aerospace Jumplist

## Motivation

I am an avid (neo)vim user, and vim has a nice feature called the jumplist. It
allows you to go back through the different locations you've been at in
different files using `<C-o>` to go back and `<C-i>` to go forward through the
jump list. This is a python utility to bring a similar functionality to
Aerospace.

## Installation

Clone the repo

```bash
git clone git@github.com:rafe-murray/aerospace-jumplist
```

Ensure the correct directory and files are created

```bash
mkdir ~/.aerospace_jumplist
cd ~/.aerospace_jumplist
touch head list is_internal_jump
cd -
```

## Usage

The python script exposes four commands: `clear`, `push`, `go-back` and
`go-forward`. `clear` clears the entire jumplist. `push` adds a single workspace
to the jumplist by id. If there are entries in the jumplist after the current
selection, they are removed. `go-back` navigates to the workspace one entry up
in the jumplist. `go-forward` navigates to the workspace one entry forward in
the jumplist. Note that both `go-back` and `go-forward` will interface with
`aerospace` directly, so this is not portable to other similar WMs.

To get a similar experience to vim's jumplist, add the following lines to your
`~/.aerospace.toml`:

```toml

after-startup-command = [
  'exec-and-forget python3 /path/to/repo/aerospace_jumplist.py clear'
]

# Push the history to the jumplist every time the workspace changes
exec-on-workspace-change = [
  '/bin/bash',
  '-c',
  'python3 /path/to/repo/aerospace_jumplist.py push $AEROSPACE_FOCUSED_WORKSPACE'
]

...

[mode.main.binding]
    alt-o = 'exec-and-forget python3 /path/to/repo/aerospace_jumplist.py go-back'
    alt-i = 'exec-and-forget python3 /path/to/repo/aerospace_jumplist.py go-forward'
```
