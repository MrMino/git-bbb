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

### Features ✨

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
- <kbd>Enter</kbd> to switch (_warp_) to the highlighted revision.
- <kbd>S</kbd> runs `git show` for the commit indicated by the cursor.
- <kbd>u</kbd> to go back to the previously viewed revision - a.k.a. _undo_.
- <kbd>ctrl</kbd>+<kbd>r</kbd> to _redo_ previous warp.
- <kbd>H</kbd> & <kbd>J</kbd> move the whole document view up and down
- <kbd>gg</kbd> and <kbd>G</kbd> will make git bbb go to the first and last
  line, respectively
- <kbd>Ctrl</kbd>+<kbd>d</kbd> and <kbd>Ctrl</kbd>+<kbd>u</kbd> will scroll
  half a page up and down, respectively
- <kbd>Page Up</kbd> & <kbd>Page Down</kbd> do what they are supposed to do
- <kbd>q</kbd> to quit
- ...many more to come
