# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project **DOES NOT** adhere to Semantic Versioning. Versioning is based
on the willingness of the author to come up with any and stick to it. 

## [Unreleased]

### Added

* There's now a separate margin that shows current cursor position.

### Changed

* Tabs will now be rendered using 4 spaces, instead of showing up as `^I`. This
  will be made configurable in the future.

## [0.0.3] - 2022-05-15
### Added

* Statusbar now shows the summary of the indicated commit.
* <kbd>S</kbd> will run `git show` for the current line

### Fixed

* Bbb will show unstaged changes if `--rev` is not given.
* Statusbar now longer extends above 1 line when browsing short files.

### Changed

* Undo / redo will now go back to the line on which the cursor was after a warp.

## [0.0.2] - 2022-05-12
### Added

* A status bar that shows currently viewed rev.
* Undo/redo functionality, bound to <kbd>u</kbd> and <kbd>ctrl+r</kbd>
  keys, respectively.

## [0.0.1] - 2022-05-08

This is the first version of `git-bbb`, with the most basic functionality
covered. The project has been in the works for a month now, many things are
still to be added.

[0.0.3]: https://github.com/mrmino/git-bbb/releases/tag/v0.0.3
[0.0.2]: https://github.com/mrmino/git-bbb/releases/tag/v0.0.2
[0.0.1]: https://github.com/mrmino/git-bbb/releases/tag/v0.0.1
