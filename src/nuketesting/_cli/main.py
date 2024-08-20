"""Script to parse CLI args and invoke the test runner."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

import click

from nuketesting._cli.configuration import find_configuration, load_runners
from nuketesting._cli.runner import Runner


class CLICommandError(Exception):
    """Exception to raise when provided commands are invalid."""


@dataclass
class CLIRunArguments:
    """Object to store all passed arguments into a single dataclass and run."""

    test_directory: Path
    """Directory specified by user to test. Defaults to current directory."""
    pytest_args: tuple[str] = ()
    """Additional arguments to forward to pytest."""
    nuke_executable: Path | None = None
    """Path to Nuke executable."""
    config: Path | None = None
    """Config JSON to override everything and have a predefined test run."""
    runner_name: str | None = None
    """Optional name of a runner to run. This will only run the runner with the name."""
    run_in_terminal_mode: bool = True
    """Run tests in Nuke using the native terminal mode or using the current Python interpreter."""

    def __post_init__(self) -> None:
        """Post initialize checks for the arguments."""
        if not self.nuke_executable and not self.config:
            msg = "Neither a config or a Nuke executable is provided."
            raise CLICommandError(msg)

        if self.nuke_executable:
            self.nuke_executable = Path(self.nuke_executable)
        if self.test_directory:
            self.test_directory = Path(self.test_directory)
        if self.config:
            self.config = Path(self.config)


def _run_tests(arguments: CLIRunArguments) -> NoReturn:
    """Execute the provided arguments.

    Arguments: dataclass containing all passed cli arguments to run
    """
    runner = None

    search_start = Path(str(arguments.test_directory).split("::")[0])

    config = arguments.config or find_configuration(search_start)
    if config:
        runners = load_runners(config)
        runner = runners.get(arguments.runner_name or arguments.nuke_executable)

    runner = runner or Runner(
        arguments.nuke_executable,
        pytest_args=arguments.pytest_args,
        run_in_terminal_mode=arguments.run_in_terminal_mode,
    )
    sys.exit(runner.execute_tests(arguments.test_directory))


@click.command()
@click.option(
    "--nuke-executable",
    "-n",
    "nuke_executable",
    required=False,
    type=click.Path(),
    help="Path to the executable of Nuke.",
)
@click.option(
    "--test-path",
    "-t",
    "test_path",
    required=False,
    default=".",
    type=click.Path(),
    help="Directory to test. This defaults to the current directory and "
    "will search for tests in that folder recursively like pytest does.",
)
@click.option(
    "--config",
    "-c",
    "config",
    required=False,
    type=click.Path(),
    help="Specify a json to read as config to use for the tests.",
)
@click.option(
    "--runner-name",
    "-r",
    "runner_name",
    required=False,
    type=str,
    help="Only run the runners in the config specified with this name",
)
@click.option(
    "--run-in-terminal-mode",
    "--terminal",
    "terminal",
    default=True,
    type=bool,
    help="Launch a Nuke interpreter to run the tests in. This defaults to True.",
)
@click.option(
    "--pytest-arg",
    "-p",
    "pytest_arg",
    multiple=True,
    help="Specify an arg to forward to pytest. You can add as many of these as you want.",
)
def main(  # noqa: PLR0913
    nuke_executable: click.Path,
    test_path: click.Path,
    config: click.Path,
    terminal: bool,
    pytest_arg: list,
    runner_name: str,
) -> NoReturn:
    """Nuke Test Runner CLI Interface.

    This bootstraps Nuke within the test runner to be able to run
    pytest like usual, with all Nuke dependencies.

    `nuke-executable` is the filepath to the nuke executable.
    If you provided a "runner.json" configuration,
    you can also reference the runner by its configured name.

    `test-path` is the folder of file of the tests you want to execute.
    Use the pytest folder/file.py::class::method notation to run single tests.
    For further options consult the pytest documentation.

    If you don't specify the test-path it will use the current directory
    like pytest does.

    """
    try:
        test_run_arguments = CLIRunArguments(
            nuke_executable=nuke_executable,
            test_directory=test_path,
            config=config,
            run_in_terminal_mode=terminal,
            pytest_args=tuple(pytest_arg),
            runner_name=runner_name,
        )
        _run_tests(test_run_arguments)

    except CLICommandError as e:
        ctx = click.get_current_context()
        ctx.fail(f"{e!s}\n\nCheck out the help above for additinal support.")
        ctx.exit()


if __name__ == "__main__":
    main()
