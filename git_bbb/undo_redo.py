from __future__ import annotations

from collections import namedtuple

from typing import Optional


RevBrowseInfo = namedtuple("RevBrowseInfo", ["rev", "file_path"])


# todo: unittest
class RevStack:
    """Undo/redo stack for revs."""

    def __init__(self, starting_rev: RevBrowseInfo):
        self.stack = [starting_rev]
        self.stack_pointer = 0

    def undo(self) -> Optional[RevBrowseInfo]:
        """Return previous rev, or None if current rev is the starting one."""
        assert self.stack
        if self.stack_pointer != 0:
            self.stack_pointer -= 1
        else:
            return None

        return self.stack[self.stack_pointer]

    def redo(self) -> Optional[RevBrowseInfo]:
        """Return previously undone rev, or None if there's nothing to redo."""
        assert self.stack
        if self.stack_pointer != len(self.stack) - 1:
            self.stack_pointer += 1
        else:
            return None

        return self.stack[self.stack_pointer]

    @property
    def current(self) -> RevBrowseInfo:
        return self.stack[self.stack_pointer]

    def do(self, rev_info: RevBrowseInfo):
        """Add rev to the stack after current position, remove undone revs."""
        # Skip if we haven't changed revs
        if rev_info.rev == self.current.rev:
            return

        self.stack_pointer += 1
        self.stack = self.stack[: self.stack_pointer]
        self.stack.append(rev_info)
