import sys
from pathlib import Path

from prompt_toolkit.lexers import PygmentsLexer

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.buffer import Buffer, Document
from prompt_toolkit.formatted_text import FormattedText, to_formatted_text
from prompt_toolkit.data_structures import Point
from prompt_toolkit.layout import (
    Layout,
    VSplit,
    Window,
    BufferControl,
    FormattedTextControl,
)

from .git_plumbing import git_blame, parse_git_blame_output

import logging

logger = logging.getLogger(__name__)
MAX_SHA_CHARS_SHOWN = 16


def __main__():
    path = Path(sys.argv[1])
    blame_output = git_blame(path)
    blames = parse_git_blame_output(blame_output)
    output = "".join([b.content for b in blames])
    output = output.rstrip("\n")  # Do not want to render empty line at the end
    sha_list = "\n".join([b.sha[:MAX_SHA_CHARS_SHOWN] for b in blames])

    # FIXME: PageUp & PageDown keys scroll only one window
    kb = KeyBindings()

    @kb.add("q", eager=True)
    def exit(event):
        event.app.exit()

    @kb.add("j")
    @kb.add("down")
    def scroll_down(event):
        source_buffer_control.move_cursor_down()
        line_numbers_buffer_control.move_cursor_down()

    @kb.add("k")
    @kb.add("up")
    def scroll_up(event):
        source_buffer_control.move_cursor_up()
        line_numbers_buffer_control.move_cursor_up()

    pygments_lexer = PygmentsLexer.from_filename(path)

    # TODO: ~maybe~ replace this with FormattedTextControl?
    source_buffer = Buffer(name="source", read_only=True)
    source_document = Document(output, cursor_position=0)
    source_buffer.set_document(source_document, bypass_readonly=True)
    source_buffer_control = BufferControl(source_buffer, lexer=pygments_lexer)

    commits_text = FormattedText(to_formatted_text(sha_list))
    commits_text_control = FormattedTextControl(
        commits_text,
        get_cursor_position=lambda: Point(
            0, source_buffer.document.cursor_position_row
        ),
    )

    # TODO: replace with prompt_toolkit.layout.NumberedMargin
    line_numbers_buffer = Buffer(name="line_numbers", read_only=True)
    line_numbers_document = Document(
        "\n".join([str(n) for n in range(len(blames))]), cursor_position=0
    )
    line_numbers_buffer.set_document(
        line_numbers_document, bypass_readonly=True
    )
    line_numbers_buffer_control = BufferControl(line_numbers_buffer)

    layout = Layout(
        VSplit(
            [
                Window(
                    content=commits_text_control,
                    width=MAX_SHA_CHARS_SHOWN,
                ),
                Window(
                    content=line_numbers_buffer_control,
                    dont_extend_width=True,
                    width=3,
                ),
                Window(
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
