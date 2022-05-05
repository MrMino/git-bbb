import re
import sys
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List

from prompt_toolkit.lexers import PygmentsLexer

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.scroll import (
    scroll_one_line_down,
    scroll_one_line_up,
)
from prompt_toolkit.buffer import Buffer, Document
from prompt_toolkit.layout import (
    Layout,
    Window,
    BufferControl,
)


@dataclass
class BlameLine:
    content: str

    sha: str
    summary: str
    is_boundary: bool

    previous_sha: Optional[str]
    previous_filename: Optional[str]

    repeats: Optional[int]

    original_filename: str
    original_line_number: int
    final_line_number: int

    author_name: str
    author_mail: str
    author_time: int
    author_tz: str

    committer_name: str
    committer_mail: str
    committer_time: int
    committer_tz: str

    @classmethod
    def from_groupdict(cls, **fields):
        # Conversions for non-str fields
        repeats = fields["repeats"]
        if repeats is not None:
            fields["repeats"] = int(repeats)

        fields["is_boundary"] = (
            True if fields["is_boundary"] is not None else False
        )

        fields["original_line_number"] = int(fields["original_line_number"])
        fields["final_line_number"] = int(fields["final_line_number"])
        fields["author_time"] = int(fields["author_time"])
        fields["committer_time"] = int(fields["committer_time"])

        return BlameLine(**fields)


def git_blame(path: Path) -> str:
    return subprocess.check_output(
        ["git", "blame", "--line-porcelain", str(path)]
    ).decode("utf-8")


def parse_git_blame_output(blame_output: str) -> List[BlameLine]:
    BLAME_HEADER_REGEX = re.compile(
        r"(?P<sha>[a-z0-9]{40})"
        r" "
        r"(?P<original_line_number>[0-9]+)"
        r" "
        r"(?P<final_line_number>[0-9]+)"
        r"( (?P<repeats>[0-9]+)\n|\n)"
        r"author (?P<author_name>.*)\n"
        r"author-mail (?P<author_mail>.*)\n"
        r"author-time (?P<author_time>\d+)\n"
        r"author-tz (?P<author_tz>\+\d{4})\n"
        r"committer (?P<committer_name>.*)\n"
        r"committer-mail (?P<committer_mail>.*)\n"
        r"committer-time (?P<committer_time>\d+)\n"
        r"committer-tz (?P<committer_tz>\+\d{4})\n"
        r"summary (?P<summary>.*)\n"
        r"(?P<is_boundary>boundary\n)?"
        r"(previous "
        r"(?P<previous_sha>[a-z0-9]+)"
        r" "
        r"(?P<previous_filename>.*)"
        r"\n)?"
        r"filename (?P<original_filename>.*)\n"
        r"\t(?P<content>.*\n)"
    )

    blames = [
        BlameLine.from_groupdict(**m.groupdict())
        for m in BLAME_HEADER_REGEX.finditer(blame_output)
    ]

    return blames


def __main__():
    path = Path(sys.argv[1])
    blame_output = git_blame(path)
    blames = parse_git_blame_output(blame_output)
    output = "".join([b.content for b in blames])

    kb = KeyBindings()

    @kb.add("q", eager=True)
    def exit(event):
        event.app.exit()

    @kb.add("j")
    @kb.add("down")
    def scroll_down(event):
        scroll_one_line_down(event)

    @kb.add("k")
    @kb.add("up")
    def scroll_up(event):
        scroll_one_line_up(event)

    pygments_lexer = PygmentsLexer.from_filename(path)

    source_buffer = Buffer(name="source", read_only=True)
    source_document = Document(output, cursor_position=0)
    source_buffer.set_document(source_document, bypass_readonly=True)

    layout = Layout(
        Window(
            content=BufferControl(source_buffer, lexer=pygments_lexer),
        )
    )

    app = Application(
        full_screen=True,
        layout=layout,
        key_bindings=kb,
        mouse_support=True,
    )

    app.run()
