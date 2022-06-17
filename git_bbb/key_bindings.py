import os

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.scroll import (
    scroll_half_page_down,
    scroll_half_page_up,
    scroll_one_line_down,
    scroll_one_line_up,
)
from prompt_toolkit.filters import Condition
from prompt_toolkit.utils import suspend_to_background_supported


def generate_bindings(browser) -> KeyBindings:
    kb = KeyBindings()

    # TODO: reset

    @kb.add("c-z", filter=Condition(suspend_to_background_supported))
    def suspend_to_background(event):
        event.app.suspend_to_background()

    @kb.add("enter")
    def warp(event):
        browser.warp()

    @kb.add("P")
    def warp_previous(event):
        browser.warp_previous()

    @kb.add("q", eager=True)
    def exit(event):
        event.app.exit()

    @kb.add("j")
    @kb.add("down")
    def scroll_down(event):
        browser.cursor_down(count=event.arg)

    @kb.add("k")
    @kb.add("up")
    def scroll_up(event):
        browser.cursor_up(count=event.arg)

    @kb.add("g", "g")
    @kb.add("<")
    def go_to_first_line(event):
        browser.go_to_first_line()

    @kb.add("G")
    @kb.add(">")
    def go_to_last_line(event):
        browser.go_to_last_line()

    @kb.add("D", "B", "G", filter=Condition(lambda: "DEBUG" in os.environ))
    def set_trace(event):
        import ipdb  # type: ignore

        ipdb.set_trace()
        browser  # Needs to be here so that we can access it in the debugger

    # TODO: Vi-style n-times moving
    kb.add("c-j")(scroll_one_line_down)
    kb.add("s-down")(scroll_one_line_down)
    kb.add("c-k")(scroll_one_line_up)
    kb.add("s-up")(scroll_one_line_up)
    kb.add("c-d")(scroll_half_page_down)
    kb.add("c-u")(scroll_half_page_up)

    @kb.add("u")
    def undo(event):
        browser.undo()

    @kb.add("c-r")
    def redo(event):
        browser.redo()

    @kb.add("S")
    def use_git_show(event):
        browser.run_git_show_for_line()

    @kb.add("J")
    def next_line_of_this_sha(event):
        # TODO: Vi-style n-times moving
        browser.go_to_next_line_of_current_sha()

    @kb.add("K")
    def previous_line_of_this_sha(event):
        # TODO: Vi-style n-times moving
        browser.go_to_previous_line_of_current_sha()

    @kb.add("L")
    def first_line_of_this_sha(event):
        browser.go_to_last_line_of_current_sha()

    @kb.add("H")
    def last_line_of_this_sha(event):
        browser.go_to_first_line_of_current_sha()

    return kb
