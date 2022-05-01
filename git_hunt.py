#!/bin/env python
import re
import sys
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class BlameLine:
    content: str

    sha: str
    previous_sha: Optional[str]
    summary: str
    is_boundary: bool

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
        # FIXME: this fails, probably due to escaped space characters?
        r"""
        # This is on a single line, separated by spaces.
        # The number of repeats is only shown for the first occurrence of a
        # commit.
        (?P<sha>[a-z0-9]{40})
        \ (?P<original_line_number>[0-9]+)
        \ (?P<final_line_number>[0-9]+)
        ( (?P<repeats>[0-9]+)\n|\n)

        author (?P<author_name>.*)\n
        author-mail (?P<author_mail>.*)\n
        author-time (?P<author_time>\d+)\n
        author-tz (?P<author_tz>\+\d{4})\n

        committer (?P<committer_name>.*)\n
        committer-mail (?P<committer_mail>.*)\n
        committer-time (?P<committer_time>\d+)\n
        committer-tz (?P<committer_tz>\+\d{4})\n

        summary (?P<summary>.*)\n

        # The string "boundary" is only shown if a line comes from a boundary
        # commit.
        (?P<is_boundary>boundary\n)?

        # SHA "previous" only shows up if a line has been modified, as opposed
        # to just added.
        (previous (?P<previous_sha>[a-z0-9]+)\n)?

        # Filename might be different from the current one, e.g. in case
        # someone used 'git mv'.
        filename (?P<original_filename>.*)\n

        # The actual content is prepended with tab character.
        \t(?P<content>.*\n)
        """,
        re.MULTILINE | re.VERBOSE
    )

    blames = [
        BlameLine.from_groupdict(**m.groupdict())
        for m in BLAME_HEADER_REGEX.finditer(blame_output, re.MULTILINE)
    ]

    return blames


def __main__():
    path = Path(sys.argv[1])
    blame_output = git_blame(path)
    blame_lines = parse_git_blame_output(blame_output)
    print(blame_lines)
