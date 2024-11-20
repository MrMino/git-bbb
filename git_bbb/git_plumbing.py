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
import git.cmd


DEFAULT_IGNORE_REVS_PATH = Path(".git-ignore-revs")
STAGING_SHA = "0" * 40
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
    r"author-tz (?P<author_tz>[+-]\d{4})\n"
    r"committer (?P<committer_name>.*)\n"
    r"committer-mail (?P<committer_mail>.*)\n"
    r"committer-time (?P<committer_time>\d+)\n"
    r"committer-tz (?P<committer_tz>[+-]\d{4})\n"
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


@dataclass
class BlameLine:
    content: str

    sha: str
    summary: str
    is_boundary: bool

    previous_sha: Optional[str]
    previous_filename: Optional[Path]

    repeats: Optional[int]

    original_filename: Path
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

        fields["original_filename"] = Path(fields["original_filename"])
        if fields["previous_filename"] is not None:
            fields["previous_filename"] = Path(fields["previous_filename"])

        return BlameLine(**fields)


class Git:
    def __init__(self, ignore_revs_file: Optional[str] = None):
        if ignore_revs_file is None:
            ignore_revs_file = self.configured_ignore_revs()
        if ignore_revs_file is None:
            ignore_revs_file = self.default_ignore_revs()

        self.ignore_revs_file = ignore_revs_file

        self.repo_path = self.show_toplevel()

    @staticmethod
    def default_ignore_revs() -> Optional[str]:
        """Return the path to default ignore-revs file, if available."""
        # TODO: either use git_show_toplevel here and remove dependency on
        # gitpython, or reuse repo.working_tree_dir where git_show_toplevel is
        # used.
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

    @staticmethod
    def configured_ignore_revs() -> Optional[str]:
        """Return the path to the ignore-revs file as configured in Git config.

        Uses 'blame.ignoreRevsFile' option. Returns None if the option is not set.
        """
        config = git.cmd.Git().config(
            "--default", "", "--get", "blame.ignoreRevsFile"
        )
        if not config:
            return None

        configured_file_path = Path(config)
        if not configured_file_path.exists():
            return None
        if not configured_file_path.is_file():
            return None
        return str(configured_file_path)

    def show(self, rev: Optional[str]):
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
        # variable. It is preferrable, but (? most likely ?) so not implemented
        # in Delta yet.
        env["DELTA_PAGER"] = "less -+F"
        if rev:
            cmd += [rev]
        subprocess.run(cmd, env=env)

    def blame(self, path: Path, rev: Optional[str]) -> List[BlameLine]:
        """Run git blame.

        Global configuration will be discarded except for
        'blame.ignoreRevsFile', which will be used if the specified path
        exists.

        Runs git blame on a given path, in a given revision. If revision is not
        given, shows blame that includes currently staged changes (same as "git
        blame path/to/file" would).

        If revision is equal to STAGING_SHA, i.e. is a string of zeroes,
        currently staged changes are removed by setting rev to the one that the
        current HEAD points to.
        """
        if not path.is_absolute():
            path = (self.repo_path / path).resolve()

        if rev == STAGING_SHA:
            # Get rid of unstaged changes.
            rev = self.rev_parse_head()

        cmd = ["git", "blame", "--line-porcelain"]
        if self.ignore_revs_file is not None:
            cmd += ["--ignore-revs-file", self.ignore_revs_file]
        if rev is not None:
            cmd += [rev, "--"]
        cmd += [str(path)]

        # Prevents Git from reading global config
        env = {"HOME": ""}

        # TODO: show proper error messages when this fails
        blame_output = subprocess.check_output(cmd, env=env).decode("utf-8")
        blames = [
            BlameLine.from_groupdict(**m.groupdict())
            for m in BLAME_HEADER_REGEX.finditer(blame_output)
        ]

        return blames

    def show_toplevel(self):
        """Get absolute path to the repository we're in currently."""
        cmd = ["git", "rev-parse", "--show-toplevel"]
        return Path(subprocess.check_output(cmd).decode("utf-8").strip())

    def rev_parse_head(self) -> str:
        """Get current commit SHA.

        Can be used to get rid of unstaged changes.
        """
        cmd = ["git", "rev-parse", "HEAD"]
        return subprocess.check_output(cmd).decode("utf-8").strip()
