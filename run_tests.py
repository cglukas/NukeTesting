"""Wrapper for running tests from the commandline."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NoReturn

import click

from _cli.configuration import find_configuration, load_runners
from _cli.runner import Runner


def run_tests(interpreter: str | Path, tests: str | Path) -> NoReturn:
    """Run the tests.

    Args:
        interpreter: name of the configured interpreter or the path to the nuke executable.
        tests: path to the test file/folder.
    """
    runner = None

    if isinstance(interpreter, str):
        search_start = Path(tests.split("::")[0])
        config = find_configuration(search_start)
        if config:
            runners = load_runners(config)
            runner = runners.get(interpreter)

    runner = runner or Runner(interpreter)
    sys.exit(runner.execute_tests(tests))


@click.command()
@click.argument("interpreter", type=str)
@click.argument("tests", type=str)
def main(interpreter: str, tests: str) -> NoReturn:
    """Run the test files with nuke.

    INTERPRETER is the filepath to the nuke executable.
    If you provided a "runner.json" configuration,
    you can also reference the runner by its configured name.

    TESTS is the folder of file of the tests you want to execute.
    Use the pytest folder/file.py::class::method notation to run single tests.
    For further options consult the pytest documentation.
    \f

    Args:
        interpreter: name of the configured interpreter or the path to the nuke executable.
        tests: path to the test/ test folder.
    """
    run_tests(interpreter, tests)


if __name__ == "__main__":
    main()
