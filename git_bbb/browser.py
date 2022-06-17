from __future__ import annotations

from collections import defaultdict

from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.buffer import Buffer, Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.processors import TabsProcessor
from prompt_toolkit.layout import (
    HSplit,
    Window,
    BufferControl,
    FormattedTextControl,
    Margin,
    NumberedMargin,
    FloatContainer,
    Float,
    ConditionalMargin,
    ConditionalContainer,
)
from prompt_toolkit.widgets import SearchToolbar

from .git_plumbing import STAGING_SHA, Git
from .undo_redo import RevStack, RevBrowseInfo
from .key_bindings import generate_bindings

from typing import TYPE_CHECKING, List, Optional, Dict

if TYPE_CHECKING:
    from pathlib import Path
    from prompt_toolkit.layout import WindowRenderInfo
    from prompt_toolkit.formatted_text import StyleAndTextTuples
    from .git_plumbing import BlameLine


MAX_SHA_CHARS_SHOWN = 12
UTF_HORIZONTAL_BAR = "—"
UTF_UPPER_LEFT_CORNER = "┌"
UTF_VERTICAL_BAR = "│"
UTF_VERTICAL_T_R = "├"
UTF_LOWER_LEFT_CORNER = "└"
UTF_RIGHT_ARROW = "➢"


class Statusbar(Window):
    def __init__(self, text, style=None):
        self._control = FormattedTextControl(text, style=style)
        super().__init__(content=self._control, style=style, height=1)

    @property
    def text(self):
        return self._control.text

    @text.setter
    def text(self, new_text):
        self._control.text = new_text


class Browser(HSplit):
    def __init__(self, git: Git, rev: str, path: Path, initial_lineno: int):
        self._git = git
        self._undo_redo_stack = RevStack(RevBrowseInfo(rev, path))
        self._lineno_cache: Dict[str, int] = defaultdict(lambda: 1)
        self._content = ""
        self._current_sha: Optional[str] = None
        self._current_path: Optional[Path] = None
        self._blame_lines: List[BlameLine] = []
        self._shas: List[str] = []

        self._search_buffer = Buffer(multiline=False)
        self._search_toolbar = SearchToolbar(
            self._search_buffer,
            vi_mode=True,
        )
        self._source_buffer = Buffer(
            name="source",
            read_only=True,
            on_cursor_position_changed=lambda _: self._update_statusbar(),
        )
        self._source_buffer_control = BufferControl(
            self._source_buffer,
            include_default_input_processors=False,
            input_processors=[
                # TODO: make the amount of spaces for a tab configurable
                TabsProcessor(char1=" ", char2=" "),
            ],
            search_buffer_control=self._search_toolbar.control,
            key_bindings=generate_bindings(self),
        )

        self._sha_list_margin = CommitSHAMargin()
        self._cursor_margin = CursorMargin()

        browsing_empty_file = Condition(lambda: self.empty_file)
        not_browsing_empty_file = Condition(lambda: not self.empty_file)

        self._empty_file_float = Float(
            ConditionalContainer(
                Window(FormattedTextControl(self._empty_file_text)),
                filter=browsing_empty_file,
            ),
        )

        self._statusbar = Statusbar("", style="bg:#333")
        super().__init__(
            [
                FloatContainer(
                    content=Window(
                        left_margins=[
                            ConditionalMargin(
                                self._cursor_margin,
                                filter=not_browsing_empty_file,
                            ),
                            ConditionalMargin(
                                self._sha_list_margin, not_browsing_empty_file
                            ),
                            PaddingMargin(1),
                            ConditionalMargin(
                                NumberedMargin(),
                                filter=not_browsing_empty_file,
                            ),
                        ],
                        content=self._source_buffer_control,
                        always_hide_cursor=True,
                    ),
                    floats=[self._empty_file_float],
                ),
                self._statusbar,
                self._search_toolbar,
            ]
        )

        self._browse_blame(rev, path, initial_lineno)

    def _empty_file_text(self):
        revision = (
            self._current_sha if self._current_sha is not None else "HEAD"
        )
        return f"File is empty in this revision ({revision})."

    @property
    def empty_file(self) -> bool:
        """True if the file we are browsing is empty in current revision."""
        return not bool(self._blame_lines)

    def _browse_blame(
        self,
        rev: str,
        path: Path,
        line_no: int,
    ):
        blame_lines = self._git.blame(path, rev)
        self._current_path = path
        self._current_sha = rev
        self._blame_lines = blame_lines
        self._shas = [b.sha for b in self._blame_lines]

        output = "".join([b.content for b in self._blame_lines])
        output = output.rstrip("\n")  # Do not render empty line at the end
        self._content = output

        lexer = PygmentsLexer.from_filename(str(path))
        self._source_buffer_control.lexer = lexer

        self._sha_list_margin.shas = self._shas
        self._cursor_margin.shas = self._shas

        # XXX: Do not save Documents - they are immutable and as soon as cursor
        # position changes, the actual document in the buffer is changed to a
        # different one.
        source_document = Document(output, cursor_position=0)
        self._source_buffer.set_document(source_document, bypass_readonly=True)

        # Line indexes are counted from 0, line numbers - from 1.
        self.current_line = line_no - 1

        # XXX: statusbar has to be updated _after_ updating the cursor
        # position, otherwise the row might be too high for
        # self.current_blame_line, which will lead to an IndexError.
        self._update_statusbar()

    # FIXME: this also needs to run on mouse presses
    def _update_statusbar(self):
        blame = self.current_blame_line
        if blame is None:
            # File is empty for current revision
            summary = "(empty file)"
        elif blame.sha != STAGING_SHA:
            summary = blame.summary
        else:
            summary = "(Uncommitted) " + blame.summary
        statusbar_content = [
            ("#ffe100", summary),
        ]
        self._statusbar.text = statusbar_content

    @property
    def current_blame_line(self) -> Optional[BlameLine]:
        if self.empty_file:
            return None
        else:
            return self._blame_lines[self.current_line]

    @property
    def cursor_sha(self):
        return self._shas[self.current_line]

    @property
    def current_line(self) -> int:
        """Line index the current document, for the line the cursor is on."""
        return self._source_buffer.document.cursor_position_row

    @current_line.setter
    def current_line(self, row):
        new_cursor_position = (
            self._source_buffer.document.translate_row_col_to_index(
                row,
                0,
            )
        )
        self._source_buffer.cursor_position = new_cursor_position

    def warp(self):
        self._save_lineno_checkpoint()
        blame = self.current_blame_line
        new_file_path = blame.original_filename
        new_rev = blame.sha
        new_lineno = blame.original_line_number
        self._browse_blame(new_rev, new_file_path, new_lineno)
        self._add_undo_point()

    def warp_previous(self):
        self._save_lineno_checkpoint()
        blame = self.current_blame_line
        new_file_path = blame.previous_filename
        new_rev = blame.previous_sha
        new_lineno = blame.original_line_number
        self._browse_blame(new_rev, new_file_path, new_lineno)
        self._add_undo_point()

    def _add_undo_point(self):
        path = self._current_path
        rev = self._current_sha
        rev_info = RevBrowseInfo(rev, path)
        self._undo_redo_stack.do(rev_info)

    def _save_lineno_checkpoint(self):
        lineno = self.current_line + 1
        self._lineno_cache[self._current_sha] = lineno

    def cursor_down(self, count=1):
        for _ in range(count):
            self._source_buffer_control.move_cursor_down()

    def cursor_up(self, count=1):
        for _ in range(count):
            self._source_buffer_control.move_cursor_up()

    def go_to_first_line(self):
        self._source_buffer.cursor_position = 0

    def go_to_last_line(self):
        self._source_buffer.cursor_position = len(self._content)

    def run_git_show_for_line(self):
        # FIXME: this makes the screen filcker temporarily with the contents of
        # the terminal as seen before running the app. It's distracting and
        # ugly.
        run_in_terminal(lambda: self._git.show(self.current_blame_line.sha))

    def go_to_next_line_of_current_sha(self, wrap=True):
        try:
            move_to = self._shas.index(self.cursor_sha, self.current_line + 1)
        except ValueError:
            move_to = None

        if move_to is None and wrap:
            try:
                self.go_to_first_line_of_current_sha()
            except ValueError:
                pass

        if move_to is None:
            move_to = self.current_line

        self.current_line = move_to

    def go_to_previous_line_of_current_sha(self, wrap=True):
        try:
            move_to = (
                len(self._shas)
                - self._shas[::-1].index(
                    self.cursor_sha, (len(self._shas) - self.current_line)
                )
                - 1
            )
        except ValueError:
            move_to = None

        if move_to is None and wrap:
            try:
                self.go_to_last_line_of_current_sha()
            except ValueError:
                pass

        if move_to is None:
            move_to = self.current_line

        self.current_line = move_to

    def go_to_first_line_of_current_sha(self):
        self.current_line = self._shas.index(self.cursor_sha)

    def go_to_last_line_of_current_sha(self):
        self.current_line = (
            len(self._shas) - self._shas[::-1].index(self.cursor_sha) - 1
        )

    def undo(self) -> None:
        self._save_lineno_checkpoint()
        rev_info = self._undo_redo_stack.undo()
        if rev_info is None:
            return

        rev, file_path = rev_info
        lineno = self._lineno_cache[rev]
        self._browse_blame(rev, file_path, lineno)

    def redo(self) -> None:
        self._save_lineno_checkpoint()
        rev_info = self._undo_redo_stack.redo()
        if rev_info is None:
            return

        rev, file_path = rev_info
        lineno = self._lineno_cache[rev]
        self._browse_blame(rev, file_path, lineno)


class CursorMargin(Margin):
    WIDTH = 2
    CURSOR = ("#ffe100 bold", f"{UTF_RIGHT_ARROW}\n")
    PIPE_STYLE = "bold #7777ee"

    def __init__(self):
        self._shas = []
        self._max_height = 0

    @property
    def shas(self):
        return self._shas

    @shas.setter
    def shas(self, shas: List[str]):
        self._shas = shas
        self._max_height = len(shas)

    def create_margin(
        self, winfo: WindowRenderInfo, _: int, height: int
    ) -> StyleAndTextTuples:
        lines_above = winfo.cursor_position.y
        lines_below = height - lines_above - 1
        current_line = lines_above

        current_row = winfo.ui_content.cursor_position.y
        current_sha = self.shas[current_row]
        pipes = self.render_pipes(current_sha)
        margin = pipes[
            current_row - lines_above : current_row + lines_below + 1
        ]
        margin[current_line] = self.CURSOR
        return margin

    def render_pipes(self, cursor_sha: str) -> StyleAndTextTuples:
        """Render a pipeline that shows where current sha is in the file."""
        row_has_current_sha = [cursor_sha == sha for sha in self.shas]
        first_row_with_same_sha = row_has_current_sha.index(True)
        last_row_with_same_sha = (
            len(self.shas) - row_has_current_sha[::-1].index(True) - 1
        )

        pipes: StyleAndTextTuples

        # Empty characters before the first SHA
        pipes = [("", "\n")] * first_row_with_same_sha

        # + and | pipes
        for is_current in row_has_current_sha[
            first_row_with_same_sha : last_row_with_same_sha + 1
        ]:
            pipe_char = UTF_VERTICAL_T_R if is_current else UTF_VERTICAL_BAR
            pipes.append((self.PIPE_STYLE, pipe_char + "\n"))

        # Corners for the first and last sha
        pipes[first_row_with_same_sha] = (
            self.PIPE_STYLE,
            UTF_UPPER_LEFT_CORNER + "\n",
        )
        pipes[last_row_with_same_sha] = (
            self.PIPE_STYLE,
            UTF_LOWER_LEFT_CORNER + "\n",
        )

        return pipes

    def get_width(self, _) -> int:
        return self.WIDTH


class CommitSHAMargin(Margin):
    WIDTH = MAX_SHA_CHARS_SHOWN

    def __init__(self):
        self._shas = []
        self._max_height = 0

    @property
    def shas(self):
        return self._shas

    @shas.setter
    def shas(self, shas: List[str]):
        self._shas = shas
        self._max_height = len(shas)

    def create_margin(
        self, winfo: WindowRenderInfo, width: int, height: int
    ) -> StyleAndTextTuples:
        start = winfo.vertical_scroll
        end = min(start + self._max_height, start + height)
        current_row = winfo.ui_content.cursor_position.y
        current_sha = self.shas[current_row]
        if current_sha == STAGING_SHA:
            current_sha = None

        # TODO: mouse click on the margin should change cursor position
        margin_text: StyleAndTextTuples = [
            (
                (
                    "#7777ee"
                    if self.shas[n] == current_sha
                    else "#777"
                    if self.shas[n] == STAGING_SHA
                    else ""
                ),
                (
                    self.shas[n] + "\n"
                    if self.shas[n] != STAGING_SHA
                    else UTF_HORIZONTAL_BAR * self.WIDTH + "\n"
                ),
            )
            for n in range(start, end)
        ]
        self._highlight_current_line(winfo, margin_text)

        return margin_text

    @staticmethod
    def _highlight_current_line(
        winfo: WindowRenderInfo, rows: StyleAndTextTuples
    ):
        current_row = winfo.cursor_position.y
        text = rows[current_row][1]
        rows[current_row] = ("#ffe100 bold", text)

    def get_width(self, _) -> int:
        return self.WIDTH


class PaddingMargin(Margin):
    def __init__(self, width: int):
        self.width = width

    def create_margin(
        self, _: WindowRenderInfo, width: int, height: int
    ) -> StyleAndTextTuples:
        return [("", " " * min(width, self.width))] * height

    def get_width(self, _) -> int:
        return self.width
