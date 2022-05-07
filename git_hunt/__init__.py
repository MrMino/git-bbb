from __future__ import annotations

import sys
from pathlib import Path

from prompt_toolkit.lexers import PygmentsLexer

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.buffer import Buffer, Document
from prompt_toolkit.layout import (
    Layout,
    VSplit,
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

    def create_margin(
        self, winfo: WindowRenderInfo, width: int, height: int
    ) -> StyleAndTextTuples:
        start = winfo.vertical_scroll
        return [
            ("", self.shas[n] + "\n") for n in range(start, start + height)
        ]

    def get_width(self, _) -> int:
        # Add one for padding
        return MAX_SHA_CHARS_SHOWN + 1


def __main__():
    path = Path(sys.argv[1])
    blame_output = git_blame(path)
    blames = parse_git_blame_output(blame_output)
    output = "".join([b.content for b in blames])
    output = output.rstrip("\n")  # Do not want to render empty line at the end

    # FIXME: PageUp & PageDown keys scroll only one window
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

    pygments_lexer = PygmentsLexer.from_filename(path)

    source_buffer = Buffer(name="source", read_only=True)
    source_document = Document(output, cursor_position=0)
    source_buffer.set_document(source_document, bypass_readonly=True)
    source_buffer_control = BufferControl(source_buffer, lexer=pygments_lexer)

    layout = Layout(
        VSplit(
            [
                Window(
                    left_margins=[
                        CommitSHAMargin([b.sha for b in blames]),
                        NumberedMargin(),
                    ],
                    content=source_buffer_control,
                ),
            ],
            padding=1,
            padding_char="│",
        )
    )

    app = Application(
        full_screen=True,
        layout=layout,
        key_bindings=kb,
        mouse_support=True,
    )

    app.run()
