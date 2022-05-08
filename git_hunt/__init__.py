from __future__ import annotations

from prompt_toolkit.lexers import PygmentsLexer

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.scroll import (
    scroll_half_page_down,
    scroll_half_page_up,
    scroll_one_line_down,
    scroll_one_line_up,
)
from prompt_toolkit.buffer import Buffer, Document
from prompt_toolkit.layout import (
    Layout,
    Window,
    BufferControl,
    NumberedMargin,
    Margin,
)

from .git_plumbing import git_blame, parse_git_blame_output


from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from prompt_toolkit.layout import WindowRenderInfo
    from prompt_toolkit.formatted_text import StyleAndTextTuples

import logging

logger = logging.getLogger(__name__)
MAX_SHA_CHARS_SHOWN = 16


class CommitSHAMargin(Margin):
    def __init__(self, shas: List[str]):
        self.shas = shas
        self.max_height = len(shas)

    def create_margin(
        self, winfo: WindowRenderInfo, width: int, height: int
    ) -> StyleAndTextTuples:
        start = winfo.vertical_scroll
        end = min(start + self.max_height, start + height)
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


def run(path):
    blame_output = git_blame(path)
    blames = parse_git_blame_output(blame_output)
    output = "".join([b.content for b in blames])
    output = output.rstrip("\n")  # Do not render empty line at the end

    kb = KeyBindings()

    @kb.add("q", eager=True)
    def exit(event):
        event.app.exit()

    @kb.add("j")
    @kb.add("down")
    def scroll_down(event):
        source_buffer_control.move_cursor_down()

    @kb.add("k")
    @kb.add("up")
    def scroll_up(event):
        source_buffer_control.move_cursor_up()

    @kb.add("g", "g")
    @kb.add("<")
    def go_to_first_line(event):
        source_buffer.cursor_position = 0

    @kb.add("G")
    @kb.add(">")
    def go_to_last_line(event):
        source_buffer.cursor_position = len(output)

    kb.add("J")(scroll_one_line_down)
    kb.add("s-down")(scroll_one_line_down)
    kb.add("K")(scroll_one_line_up)
    kb.add("s-up")(scroll_one_line_up)
    kb.add("c-d")(scroll_half_page_down)
    kb.add("c-u")(scroll_half_page_up)

    pygments_lexer = PygmentsLexer.from_filename(path)

    source_buffer = Buffer(name="source", read_only=True)
    source_document = Document(output, cursor_position=0)
    source_buffer.set_document(source_document, bypass_readonly=True)
    source_buffer_control = BufferControl(source_buffer, lexer=pygments_lexer)

    layout = Layout(
        Window(
            # TODO: padding between margins
            left_margins=[
                CommitSHAMargin([b.sha for b in blames]),
                NumberedMargin(),
            ],
            content=source_buffer_control,
            always_hide_cursor=True,
        ),
    )

    app = Application(
        full_screen=True,
        layout=layout,
        key_bindings=kb,
        mouse_support=True,
    )

    app.run()
