#!/bin/env python
import sys
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class BlameLine:
    content: str

    sha: str
    previous_sha: Optional[str]
    summary: str

    original_filename: str
    original_line_number: int
    final_line_number: int

    author_name: str
    author_email: str
    author_time: int
    author_tz: str

    committer_name: str
    committer_email: str
    committer_time: int
    committer_tz: str


def git_blame(path: Path) -> str:
    return subprocess.check_output(
        ["git", "blame", "--line-porcelain", str(path)]
    ).decode("utf-8")


def __main__():
    path = Path(sys.argv[1])
    blame = git_blame(path)
    print(blame)
