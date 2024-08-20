"""Script that gets executed by nuke to run tests.

This script will be run through the `Runner` class. It adds pytest to the available packages and executes
pytest with all provided arguments.
"""
# ! It is important here not to import anything not available in default Nuke,
# ! as this is not bootstrapped yet.

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NoReturn


class BootstrapError(Exception):
    """Exception to raise during bootstrap."""


def _run_tests(packages_directory: str, test_directory: str, pytest_arguments: list[str]) -> NoReturn:
    """Run pytest with the provided arguments.

    Note:
        This function will exit the calling instance and forward the exitcode from pytest.

    Args:
        packages_directory directories that should be added to the PATH with necessary python packages.
        test_directory: directory to run pytest on
        pytest_arguments: additional arguments to pass to pytest. For example -v for verbose, etc.
    """
    for path in packages_directory.split(":"):
        if not Path(path).is_dir():
            msg = f"Package directory does not exist: '{path}'."
            raise BootstrapError(msg)
        sys.path.append(path)

    import pytest

    if "nuke" in sys.modules:
        import nuke

        nuke.tprint("Inserted packages for the NukeTestRunner successfully. Starting tests...")

    arguments = [test_directory]
    if pytest_arguments:
        arguments.extend(pytest_arguments)
    sys.exit(pytest.main(arguments))


def _parse_args(args: list[str]) -> argparse.Namespace:
    """Parse provided arguments."""
    parser = argparse.ArgumentParser(
        prog="NukeTestBootstrapper",
        description=(
            "Internal CLI interface to wrap Nuke to run the tests. "
            "Do not use this directly. Use the CLI nuke-testrunner instead."
        ),
    )
    parser.add_argument("--test_dir")
    parser.add_argument("--packages_directory")
    parser.add_argument("--pytest_arg", action="append")
    return parser.parse_args(args)


def main() -> NoReturn:
    """Main pytest bootstrap entrypoint"""
    parsed_arguments = _parse_args(sys.argv[1:])
    _run_tests(
        packages_directory=parsed_arguments.packages_directory,
        pytest_arguments=parsed_arguments.pytest_arg,
        test_directory=parsed_arguments.test_dir,
    )


if __name__ == "__main__":
    main()
