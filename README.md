<p align="center"><h2>Brisk Blame Browser for Git</h2></p>

![PyPI](https://img.shields.io/pypi/v/git-bbb?style=for-the-badge)
![GitHub](https://img.shields.io/github/license/mrmino/git-bbb?style=for-the-badge)

`git-bbb` is a wraper around `git blame`, that let's you seamlessly warp
between different revisions.

### Features ⚡

The project is in its early stages of development, many features are still to
be worked out. For now, the most notable features are:

 - Colorized syntax (thanks, [Pygments](https://pygments.org/)!)
 - Seamlessly go to the revision from a blame line in just one keypress
 - Uses `.git-ignore-revs` file as an input to `--ignore-revs-file` by default
 - Vi style bindings

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
- <kbd>H</kbd> & <kbd>J</kbd> move the whole document view up and down
- <kbd>gg</kbd> and <kbd>G</kbd> will make git bbb go to the first and last
  line, respectively
- <kbd>Ctrl</kbd>+<kbd>d</kbd> and <kbd>Ctrl</kbd>+<kbd>u</kbd> will scroll
  half a page up and down, respectively
- <kbd>Page Up</kbd> & <kbd>Page Down</kbd> do what they are supposed to do
- <kbd>Enter</kbd> to switch to the highlighted revision
- <kbd>q</kbd> to quit
- ...many more to come
