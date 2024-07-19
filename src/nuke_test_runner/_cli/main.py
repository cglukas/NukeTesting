"""Script to parse CLI args and invoke the test runner."""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

import click

from nuke_test_runner._cli.configuration import find_configuration, load_runners
from nuke_test_runner._cli.runner import Runner

logger = logging.getLogger(__name__)


class CLICommandError(Exception):
    """Exception to raise when provided commands are invalid."""


@dataclass
class CLIRunArguments:
    """Object to store all passed arguments into a single dataclass and run."""

    test_directories: click.Path
    """Directory specified by user to test. Defaults to current directory."""
    pytest_args: tuple[str]
    """Additional arguments to forward to pytest."""
    nuke_executable: click.Path | None = None
    """Path to Nuke executable."""
    config: click.Path | None = None
    """Config JSON to override everything and have a predefined test run."""
    runner_name: str | None = None
    """Optional name of a runner to run. This will only run the runners with this name."""
    run_interactive: bool = True
    """Run tests interactive in Nuke or using the current Python interpreter."""

    def __post_init__(self) -> None:
        """Post initialize checks for the arguments."""
        if not self.nuke_executable and not self.config:
            msg = "Neither a config or a Nuke executable is provided."
            raise CLICommandError(msg)

    def run_tests(self) -> NoReturn:
        """Execute the provided arguments."""
        runner = None

        search_start = Path(str(self.test_directories).split("::")[0])
        config = find_configuration(search_start)
        if config:
            runners = load_runners(config)
            runner = runners.get(self.runner_name or self.nuke_executable)

        runner = runner or Runner(self.nuke_executable, pytest_args=self.pytest_args, interactive=self.run_interactive)
        sys.exit(runner.execute_tests(self.test_directories))


@click.command()
@click.option("--nuke_executable", "-n", "nuke_executable", required=False, type=click.Path())
@click.option("--test_dir", "-t", "test_dir", required=False, default=".", type=click.Path())
@click.option("--config", "-c", "config", required=False, type=click.Path())
@click.option("--runner_name", "-r", "runner_name", required=False, type=str)
@click.option("--run_interactive", "-i", "interactive", default=True, type=bool)
@click.option("--pytest_arg", "-p", "pytest_arg", multiple=True)
def main(
    nuke_executable: click.Path,
    test_dir: click.Path,
    config: click.Path,
    interactive: bool,
    pytest_arg: list,
    runner_name: str,
) -> NoReturn:
    test_run_arguments = CLIRunArguments(
        nuke_executable=nuke_executable,
        test_directories=test_dir,
        config=config,
        run_interactive=interactive,
        pytest_args=pytest_arg,
        runner_name=runner_name,
    )
    test_run_arguments.run_tests()


if __name__ == "__main__":
    main()
