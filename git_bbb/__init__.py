
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout

from .git_plumbing import default_ignore_revs
from .browser import Browser, browse_blame_briskly
from .key_bindings import generate_bindings

import logging

logger = logging.getLogger(__name__)


def run(path, rev, ignore_revs_file):
    if ignore_revs_file is None:
        ignore_revs_file = default_ignore_revs()

    browser = Browser()
    browse_blame_briskly(browser, path, rev, ignore_revs_file)

    layout = Layout(browser)
    key_bindings = generate_bindings(browser)

    app = Application(
        full_screen=True,
        layout=layout,
        key_bindings=key_bindings,
        mouse_support=True,
    )

    app.run()
