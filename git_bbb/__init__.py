from prompt_toolkit.lexers import PygmentsLexer

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout

from .git_plumbing import (
    git_blame,
    parse_git_blame_output,
    default_ignore_revs,
)
from .browser import Browser
from .key_bindings import generate_bindings

import logging

logger = logging.getLogger(__name__)


def run(path, rev, ignore_revs_file):
    if ignore_revs_file is None:
        ignore_revs_file = default_ignore_revs()

    blame_output = git_blame(path, rev, ignore_revs_file)
    blames = parse_git_blame_output(blame_output)

    pygments_lexer = PygmentsLexer.from_filename(path)

    browser = Browser()
    key_bindings = generate_bindings(browser)

    browser.browse_blame(blames, pygments_lexer, cursor_position=0)

    layout = Layout(browser)

    app = Application(
        full_screen=True,
        layout=layout,
        key_bindings=key_bindings,
        mouse_support=True,
    )

    app.run()
