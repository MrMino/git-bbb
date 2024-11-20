import click
import pathlib
import sys

from . import run


@click.command(name=sys.argv[0])
@click.option(
    "--ignore-revs-file",
    required=False,
    default=None,
    metavar="ignore-revs-file",
    help=(
        "Ignore revisions listed in file. See git-blame manual for more "
        "information. By default, '.git-ignore-revs' from the repository root "
        "is used, if it exists."
    ),
    type=click.Path(
        exists=True,
        readable=True,
        dir_okay=False,
    ),
)
@click.option(
    "--rev",
    default=None,
    show_default=True,
    metavar="revision",
    help=(
        "Repository revision to use for browsing (e.g. branch name or commit "
        "SHA). See the manual of git-rev-parse for information about possible "
        "values."
    ),
)
@click.argument(
    "path",
    metavar="file",
    type=click.Path(
        # FIXME: the checks here need to be done based on the revision;
        # different revisions may contain different file paths, not necesasrily
        # corresponding to any existing files in the current work tree.
        exists=True,
        readable=True,
        dir_okay=False,
        path_type=pathlib.Path,
        resolve_path=True,
    ),
)
def git_bbb(path, rev, ignore_revs_file):
    run(path, rev, ignore_revs_file)
