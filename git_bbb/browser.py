from __future__ import annotations

from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.layout import Margin
from prompt_toolkit.buffer import Buffer, Document
from prompt_toolkit.layout.processors import TabsProcessor
from prompt_toolkit.layout import (
    HSplit,
    Window,
    BufferControl,
    FormattedTextControl,
    NumberedMargin,
)

from .git_plumbing import (
    git_show,
    git_blame,
    parse_git_blame_output,
)


from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from prompt_toolkit.layout import WindowRenderInfo
    from prompt_toolkit.formatted_text import StyleAndTextTuples
    from .git_plumbing import BlameLine


MAX_SHA_CHARS_SHOWN = 12
STAGING_SHA = "0" * 40
UTF_HORIZONTAL_BAR = "—"
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
    def __init__(self):
        self._current_sha: str = None
        self._blame_lines = []
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
        )

        self._sha_list_margin = CommitSHAMargin()

        self._statusbar = Statusbar("", style="bg:#333")
        super().__init__(
            [
                Window(
                    left_margins=[
                        CursorMargin(),
                        self._sha_list_margin,
                        PaddingMargin(1),
                        NumberedMargin(),
                    ],
                    content=self._source_buffer_control,
                    always_hide_cursor=True,
                ),
                self._statusbar,
            ]
        )

    def browse_blame(
        self,
        current_sha: str,
        blame_lines: List[BlameLine],
        lexer: PygmentsLexer,
        current_line: int,
    ):
        self._current_sha = current_sha
        self._blame_lines = blame_lines

        self._update_statusbar()

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

    # FIXME: this also needs to run on mouse presses
    def _update_statusbar(self):
        blame = self.current_blame_line
        if blame.sha != STAGING_SHA:
            summary = blame.summary
        else:
            summary = "(Uncommitted) " + blame.summary
        statusbar_content = [
            ("#777 bold", f"{UTF_LOWER_LEFT_CORNER} "),
            ("#ffe100", summary),
        ]
        self._statusbar.text = statusbar_content

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

    def run_git_show_for_line(self):
        # FIXME: this makes the screen filcker temporarily with the contents of
        # the terminal as seen before running the app. It's distracting and
        # ugly.
        run_in_terminal(lambda: git_show(self.current_blame_line.sha))


class CursorMargin(Margin):
    def create_margin(
        self, winfo: WindowRenderInfo, _: int, height: int
    ) -> StyleAndTextTuples:
        current_row = winfo.cursor_position.y
        cursor: StyleAndTextTuples = [("#ffe100 bold", f"{UTF_RIGHT_ARROW}\n")]
        above: StyleAndTextTuples = [("", " \n")] * current_row
        below: StyleAndTextTuples = [("#777", "│\n")] * (height - current_row)
        return above + cursor + below

    def get_width(self, _) -> int:
        return 2


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


def browse_blame_briskly(browser, ignore_revs_file, rev, path, current_line=1):
    blame_output = git_blame(path, rev, ignore_revs_file)
    blames = parse_git_blame_output(blame_output)
    pygments_lexer = PygmentsLexer.from_filename(path)
    browser.browse_blame(rev, blames, pygments_lexer, current_line)
