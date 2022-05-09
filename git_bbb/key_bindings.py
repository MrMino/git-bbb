from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.scroll import (
    scroll_half_page_down,
    scroll_half_page_up,
    scroll_one_line_down,
    scroll_one_line_up,
)

from .browser import browse_blame_briskly


def generate_bindings(browser, ignore_revs_file) -> KeyBindings:
    kb = KeyBindings()

    @kb.add("enter")
    def warp(event):
        # TODO: this code shouldn't be in keybinding function
        blame = browser.current_blame_line
        new_file_path = blame.previous_filename
        new_rev = blame.sha
        browse_blame_briskly(browser, new_file_path, new_rev, ignore_revs_file)

    @kb.add("q", eager=True)
    def exit(event):
        event.app.exit()

    @kb.add("j")
    @kb.add("down")
    def scroll_down(event):
        browser.cursor_down()

    @kb.add("k")
    @kb.add("up")
    def scroll_up(event):
        browser.cursor_up()

    @kb.add("g", "g")
    @kb.add("<")
    def go_to_first_line(event):
        browser.go_to_first_line()

    @kb.add("G")
    @kb.add(">")
    def go_to_last_line(event):
        browser.go_to_last_line()

    kb.add("J")(scroll_one_line_down)
    kb.add("s-down")(scroll_one_line_down)
    kb.add("K")(scroll_one_line_up)
    kb.add("s-up")(scroll_one_line_up)
    kb.add("c-d")(scroll_half_page_down)
    kb.add("c-u")(scroll_half_page_up)

    return kb