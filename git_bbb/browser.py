from __future__ import annotations

from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.layout import Margin
from prompt_toolkit.buffer import Buffer, Document
from prompt_toolkit.layout import (
    HSplit,
    Window,
    BufferControl,
    NumberedMargin,
)

from .git_plumbing import (
    git_blame,
    parse_git_blame_output,
)


from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from prompt_toolkit.layout import WindowRenderInfo
    from prompt_toolkit.formatted_text import StyleAndTextTuples
    from .git_plumbing import BlameLine


class Browser(HSplit):
    def __init__(self):
        self._blame_lines = []
        self._source_buffer = Buffer(name="source", read_only=True)
        self._source_buffer_control = BufferControl(
            self._source_buffer,
            include_default_input_processors=False,
        )

        self._sha_list_margin = CommitSHAMargin()

        super().__init__(
            [
                Window(
                    left_margins=[
                        self._sha_list_margin,
                        PaddingMargin(1),
                        NumberedMargin(),
                    ],
                    content=self._source_buffer_control,
                    always_hide_cursor=True,
                ),
            ]
        )

    def browse_blame(
        self,
        blame_lines: List[BlameLine],
        lexer: PygmentsLexer,
        current_line: int,
    ):
        self._blame_lines = blame_lines

        output = "".join([b.content for b in self._blame_lines])
        output = output.rstrip("\n")  # Do not render empty line at the end
        self._content = output

        self._source_buffer_control.lexer = lexer
        self._sha_list_margin.shas = [b.sha for b in self._blame_lines]
        # XXX: Do not save Documents - they are immutable and as soon as cursor
        # position changes, the actual document in the buffer is changed to a
        # different one.
        source_document = Document(output, cursor_position=0)
        self._source_buffer.set_document(source_document, bypass_readonly=True)

        new_cursor_position = source_document.translate_row_col_to_index(
            # Cursor row position is counted from 0, while line numbers are
            # counted from 1, hence the -1 below.
            current_line - 1,
            0,
        )
        self._source_buffer.cursor_position = new_cursor_position

    @property
    def current_blame_line(self) -> BlameLine:
        return self._blame_lines[
            self._source_buffer.document.cursor_position_row
        ]

    def cursor_down(self):
        self._source_buffer_control.move_cursor_down()

    def cursor_up(self):
        self._source_buffer_control.move_cursor_up()

    def go_to_first_line(self):
        self._source_buffer.cursor_position = 0

    def go_to_last_line(self):
        self._source_buffer.cursor_position = len(self._content)


MAX_SHA_CHARS_SHOWN = 12


class CommitSHAMargin(Margin):
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
        # TODO: mouse click on the margin should change cursor position
        margin_text: StyleAndTextTuples = [
            ("", self.shas[n] + "\n") for n in range(start, end)
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
        return MAX_SHA_CHARS_SHOWN


class PaddingMargin(Margin):
    def __init__(self, width: int):
        self.width = width

    def create_margin(
        self, _: WindowRenderInfo, width: int, height: int
    ) -> StyleAndTextTuples:
        return [("", " " * min(width, self.width))] * height

    def get_width(self, _) -> int:
        return self.width


def browse_blame_briskly(browser, path, rev, ignore_revs_file, current_line=1):
    blame_output = git_blame(path, rev, ignore_revs_file)
    blames = parse_git_blame_output(blame_output)
    pygments_lexer = PygmentsLexer.from_filename(path)
    browser.browse_blame(blames, pygments_lexer, current_line)
