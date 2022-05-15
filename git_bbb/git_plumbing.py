"""Code that handles fetching information from git.

Blame-related functionality is done by us instead of gitpython, becase the
latter doesn't have all of the necessary functionality.
"""
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path

import git


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


def git_show(rev: Optional[str]):
    cmd = ["git", "show"]
    env = os.environ.copy()
    # FIXME: Delta will set Less with --quit-on-eof by default
    #
    # This behavior would have to be sidestepped by implementing .gitconfig
    # settings for git-bbb, so that one can specify a pager for git-bbb
    # separately to git-show:
    #
    #     [pager]
    #         show = delta
    #         bbb = delta --paging=always
    #
    # This could also be achieved if Delta took options by an environment
    # variable. It is preferrable, but (? most likely ?) so not implemented in
    # Delta yet.
    env["DELTA_PAGER"] = "less -+F"
    if rev:
        cmd += [rev]
    subprocess.run(cmd, env=env)


def git_blame(
    path: Path, rev: Optional[str], ignore_revs_file: Optional[str]
) -> str:
    cmd = ["git", "blame", "--line-porcelain"]
    if ignore_revs_file is not None:
        cmd += ["--ignore-revs-file", ignore_revs_file]
    if rev is not None:
        cmd += [rev, "--"]
    cmd += [str(path)]
    # TODO: show proper error messages when this fails
    return subprocess.check_output(cmd).decode("utf-8")


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


DEFAULT_IGNORE_REVS_PATH = Path(".git-ignore-revs")


def default_ignore_revs() -> Optional[str]:
    """Check if default ignore-revs file is available, return its path if so."""
    repo = git.Repo(search_parent_directories=True)
    worktree_path = repo.working_tree_dir

    if worktree_path is None:
        # We are in a bare repository
        return None

    default_file_path = worktree_path / DEFAULT_IGNORE_REVS_PATH

    if not default_file_path.exists():
        return None
    if not default_file_path.is_file():
        return None

    return str(default_file_path)
