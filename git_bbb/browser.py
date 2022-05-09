from __future__ import annotations

from prompt_toolkit.layout import Margin

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from prompt_toolkit.layout import WindowRenderInfo
    from prompt_toolkit.formatted_text import StyleAndTextTuples


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
