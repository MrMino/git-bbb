import click
import pathlib
import sys

from . import run


@click.command(name=sys.argv[0])
@click.option(
    "--rev",
    default="HEAD",
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
        exists=True, readable=True, dir_okay=False, path_type=pathlib.Path
    ),
)
def git_bbb(path, rev):
    run(path, rev)
