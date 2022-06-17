<h1 align="center">Brisk Blame Browser for Git ⚡</h3>
<p align="center">
<img src="https://img.shields.io/pypi/v/git-bbb?style=for-the-badge" alt="PyPI"/>
<img src="https://img.shields.io/github/license/mrmino/git-bbb?style=for-the-badge", alt="GitHub License"/>
<a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge" alt="Code style: black"/>
</a>
</p>

<p align="center">
 <code>git-bbb</code> is a wraper around <code>git blame</code>, that lets you seamlessly warp
between different revisions.
</p>

<p align="center">
 <img src="https://user-images.githubusercontent.com/6691643/169922563-053608fc-c169-43b6-a55a-1bb5d6a1b8c4.png" alt="Git-bbb screenshot"/>
</p>

### Features ✨

 - Sensible TUI made with [Prompt
   Toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
 - Syntax highlighting thanks to [Pygments](https://pygments.org/)!)
 - Seamlessly switches between revisions in just one keypress
 - Shows you where the lines of a commit are in the file
 - Uses `.git-ignore-revs` file as an input to `--ignore-revs-file` by default
 - Vi style key bindings
 - Search functionality
 - _Coming soon: customizability via `git config`_
 - _Coming soon: seamlessly browse through file history, even if it was moved
   multiple times_
 - _Coming soon: highlight contributions made by a given author_

### Installation

```
# Install git-bbb via pip
pip install git-bbb
```

### Usage

```
# Installing git-bbb will add a "git bbb" command
git bbb file/in/the/repo
```

### Key bindings

- Use <kbd>h</kbd> & <kbd>j</kbd> or <kbd>↓</kbd> & <kbd>↑</kbd> to move to the
  next/previous blame line
- <kbd>Enter</kbd> to switch (_warp_) to the highlighted revision, or
  <kbd>P</kbd> to go to its ancestor.
- <kbd>S</kbd> runs `git show` for the commit indicated by the cursor.
- <kbd>u</kbd> to go back to the previously viewed revision - a.k.a. _undo_.
- <kbd>ctrl</kbd>+<kbd>r</kbd> to _redo_ previous warp.
- <kbd>ctrl</kbd>+<kbd>J</kbd> & <kbd>ctrl</kbd>+<kbd>K</kbd> move the whole
  document view up and down
- Stepping between the lines of the currently highlighted revision:
  <kbd>H</kbd> - first, <kbd>L</kbd> - last, <kbd>J</kbd> - next,
  <kbd>K</kbd> - previous.
- <kbd>gg</kbd> and <kbd>G</kbd> will make git bbb go to the first and last
  line, respectively
- <kbd>Ctrl</kbd>+<kbd>d</kbd> and <kbd>Ctrl</kbd>+<kbd>u</kbd> will scroll
  half a page up and down, respectively
- <kbd>Page Up</kbd> & <kbd>Page Down</kbd> do what they are supposed to do
- <kbd>/</kbd> & <kbd>?</kbd> to search through file contents. This works
  mostly in the same way as in Vi(m). Use <kbd>n</kbd> and <kbd>N</kbd> to
  cycle through results.
- <kbd>q</kbd> to quit
- ...many more to come
