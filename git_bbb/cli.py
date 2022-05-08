import click
import pathlib
import sys

from . import run


@click.command(name=sys.argv[0])
@click.argument(
    "path",
    metavar="file",
    type=click.Path(
        exists=True, readable=True, dir_okay=False, path_type=pathlib.Path
    ),
)
def git_bbb(path):
    run(path)
