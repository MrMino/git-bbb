# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project **DOES NOT** adhere to Semantic Versioning. Versioning is based
on the willingness of the author to come up with any and stick to it. 

## [Unreleased]

### Fixed

* Fixed keybinding collision introduced in [v0.0.8]: scrolling document view is
  now done via <kbd>ctrl</kbd>+<kbd>j</kbd> & <kbd>ctrl</kbd>+<kbd>k</kbd>
  instead of <kbd>J</kbd> & <kbd>K</kbd> .

## [v0.0.8]

### Added

* Pressing <kbd>P</kbd> will now warp to the ancestor of the indicated commit.

### Changed

* Keybindings for traveling between lines of the SHA under cursor are now
  <kbd>H</kbd>, <kbd>L</kbd>, <kbd>K</kbd>, and <kbd>J</kbd>
* Undo & redo functionality now behaves more in line with what the user would
  expect: cursor position is saved per browsed rev and restored going back or
  forth in browsing history.

## [0.0.7]

### Added

* Search! <kbd>/</kbd> and <kbd>?</kbd> will now trigger a vi-style searchbar
  that searches through the blame lines. <kbd>N</kbd> and <kbd>n</kbd> can be
  used to cycle through results.
* When browsing a file that is empty in the given revision, a placeholder text
  containing currently opened revision will show up.

### Fixed

* Browsing a file that is empty for the given revision will no longer lead to
  an `IndexError`.

## [0.0.6] - 2022-05-25

### Added

* It is now possible to suspend `git-bbb` using <kbd>ctrl</kbd>+<kbd>z</kbd>

### Fixed

* `git-bbb` will now properly parse timezones west of Greenwich.

## [0.0.5] - 2022-05-24

### Added

* Added the keybindings for traveling between lines of the SHA under cursor:
    * <kbd>{</kbd> - first,
    * <kbd>}</kbd> - last,
    * <kbd>]</kbd> - next,
    * <kbd>[</kbd> - previous,
* Vi-style moves using numbers before navigation keys is now supported for
  moving cursor up & down.
* Attempting to warp onto a line with unstaged changes will warp onto current
  `HEAD`.

### Changed

* The leftmost margin now draws lines towards other places where current sha
  is, instead of hinting down at the statusbar.

### Fixed

* Fixed issues with running `git-bbb` from a directory other than repository
  root.
* Warping on a line near the end of the file will no longer raise `IndexError`.
* Warping on a line with unstaged changes no longer raises an exception.

## [0.0.4] - 2022-05-17

### Added

* There's now a separate margin that shows current cursor position.
* Browser now highlights other lines from the currently indicated commit.
* Package metadata, most notably `requires-python` which will prevent
  installation under incompatible versions of Python.

### Changed

* Code highlighting style has been changed to
  [Monokai](https://pygments.org/styles/). This will be configurable in the
  future, but for now it is used as a sane default.
* Tabs will now be rendered using 4 spaces, instead of showing up as `^I`. This
  will be made configurable in the future.
* Uncommitted lines will no longer show up with a "000..." SHA.

### Removed

* Statusbar no longer shows the SHA of the commit - it was unnecessarily
  duplicated.

### Fixed

* Clicking on a line will now properly update the statusbar.

## [0.0.3] - 2022-05-15
### Added

* Statusbar now shows the summary of the indicated commit.
* <kbd>S</kbd> will run `git show` for the current line

### Fixed

* Git-bbb will show unstaged changes if `--rev` is not given.
* Statusbar no longer extends above 1 line when browsing short files.

### Changed

* Undo / redo will now go back to the line on which the cursor was after a warp.

## [0.0.2] - 2022-05-12
### Added

* A status bar that shows currently viewed rev.
* Undo/redo functionality, bound to <kbd>u</kbd> and
  <kbd>ctrl</kbd>+<kbd>+r</kbd> keys, respectively.

## [0.0.1] - 2022-05-08

This is the first version of `git-bbb`, with the most basic functionality
covered. The project has been in the works for a month now, many things are
still to be added.

[0.0.8]: https://github.com/mrmino/git-bbb/releases/tag/v0.0.8
[0.0.7]: https://github.com/mrmino/git-bbb/releases/tag/v0.0.7
[0.0.6]: https://github.com/mrmino/git-bbb/releases/tag/v0.0.6
[0.0.5]: https://github.com/mrmino/git-bbb/releases/tag/v0.0.5
[0.0.4]: https://github.com/mrmino/git-bbb/releases/tag/v0.0.4
[0.0.3]: https://github.com/mrmino/git-bbb/releases/tag/v0.0.3
[0.0.2]: https://github.com/mrmino/git-bbb/releases/tag/v0.0.2
[0.0.1]: https://github.com/mrmino/git-bbb/releases/tag/v0.0.1
