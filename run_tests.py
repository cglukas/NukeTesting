"""Wrapper for running tests from the commandline."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import NoReturn

import click

from nuke_test_runner.runner import Runner


def run_tests(executable: str | Path, tests: str | Path) -> NoReturn:
    """Run the tests.

    Args:
        executable: path to the nuke executable.
        tests: path to the test file/folder.
    """
    runner = Runner(executable)
    sys.exit(runner.execute_tests(tests))


@click.command()
@click.argument("executable", type=str)
@click.argument("tests", type=str)
def main(executable: str, tests: str) -> NoReturn:
    """Run the test files with nuke.

    Args:
        executable: path to the nuke executable which will execute the tests.
        tests: path to the test/ test folder.
    """
    run_tests(executable, tests)


if __name__ == '__main__':
    main()
