"""
Git-bbb: Brisk Blame Browser for Git.
"""
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.styles import get_style_by_name

from .git_plumbing import default_ignore_revs
from .browser import Browser, browse_blame_briskly
from .key_bindings import generate_bindings
from .undo_redo import RevStack, RevBrowseInfo

import logging

logger = logging.getLogger(__name__)


def run(path, rev, ignore_revs_file):
    if ignore_revs_file is None:
        ignore_revs_file = default_ignore_revs()

    rev_info = RevBrowseInfo(rev, path, 1)
    undo_redo_stack = RevStack(rev_info)

    browser = Browser()
    browse_blame_briskly(browser, ignore_revs_file, rev, path)

    layout = Layout(browser)
    # TODO: make a class for git blame parser and keep ignore-revs path in it,
    # instead of passing it around alone.
    key_bindings = generate_bindings(
        browser, undo_redo_stack, ignore_revs_file
    )

    # TODO: make this configurable
    pygments_style = "monokai"
    app = Application(
        full_screen=True,
        layout=layout,
        key_bindings=key_bindings,
        mouse_support=True,
        style=style_from_pygments_cls(get_style_by_name(pygments_style)),
    )

    app.run()
