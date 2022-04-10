#!/bin/env python
import sys
import subprocess
from pathlib import Path


def git_blame(path: Path):
    return subprocess.check_output(["git", "blame", str(path)])


def __main__():
    path = Path(sys.argv[1])
    blame = git_blame(path)
    print(blame.decode('utf-8'))
