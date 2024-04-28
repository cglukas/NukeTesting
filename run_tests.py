"""Wrapper for running tests from the commandline."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import NoReturn

import click

from datamodel.constants import RUNNER_CONFIGURATION_FILE
from nuke_test_runner.configuration import load_runners
from nuke_test_runner.runner import Runner


def run_tests(interpreter: str | Path, tests: str | Path) -> NoReturn:
    """Run the tests.

    Args:
        interpreter: name of the configured interpreter or the path to the nuke executable.
        tests: path to the test file/folder.
    """
    runner = None
    if isinstance(interpreter, str):
        runners = load_runners(RUNNER_CONFIGURATION_FILE)
        runner = runners.get(interpreter)

    runner = runner or Runner(interpreter)
    sys.exit(runner.execute_tests(tests))


@click.command()
@click.argument("interpreter", type=str)
@click.argument("tests", type=str)
def main(interpreter: str, tests: str) -> NoReturn:
    """Run the test files with nuke.

    Args:
        interpreter: name of the configured interpreter or the path to the nuke executable.
        tests: path to the test/ test folder.
    """
    run_tests(interpreter, tests)


if __name__ == "__main__":
    main()
