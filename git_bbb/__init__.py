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
)

from .git_plumbing import (
    git_blame,
    parse_git_blame_output,
    default_ignore_revs,
)
from .browser import CommitSHAMargin

import logging

logger = logging.getLogger(__name__)


def run(path, rev, ignore_revs_file):
    if ignore_revs_file is None:
        ignore_revs_file = default_ignore_revs()

    blame_output = git_blame(path, rev, ignore_revs_file)
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
    source_buffer_control = BufferControl(
        source_buffer,
        lexer=pygments_lexer,
        include_default_input_processors=False,
    )

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
