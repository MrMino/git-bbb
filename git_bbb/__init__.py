"""
Git-bbb: Brisk Blame Browser for Git.
"""

from prompt_toolkit import Application
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.layout import Layout
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.styles import get_style_by_name

from .git_plumbing import Git
from .browser import Browser

import logging

logger = logging.getLogger(__name__)


def run(path, rev, ignore_revs_file):
    git = Git(ignore_revs_file)

    browser = Browser(git, rev, path, initial_lineno=1)
    layout = Layout(browser)

    # TODO: make this configurable
    pygments_style = "monokai"
    app = Application(
        full_screen=True,
        layout=layout,
        mouse_support=True,
        style=style_from_pygments_cls(get_style_by_name(pygments_style)),
    )

    app.editing_mode = EditingMode.VI

    app.run()
