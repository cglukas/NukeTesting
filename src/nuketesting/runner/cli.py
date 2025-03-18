"""Script to parse CLI args and invoke the test runner."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

import click

from nuketesting.runner.configuration import find_configuration, load_runners
from nuketesting.runner.runner import Runner


class CLICommandError(Exception):
    """Exception to raise when provided commands are invalid."""


NO_CONFIG_FOUND_ERROR = CLICommandError("No config found.")

RUNNER_AND_EXE_PROVIDED_ERROR = CLICommandError("Only provide nuke executable or runner configuration/name.")

RUNNER_OR_EXE_MISSING_ERROR = CLICommandError("Neither a runner or a Nuke executable is provided.")


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
    if not arguments.nuke_executable and not arguments.runner_name:
        raise RUNNER_OR_EXE_MISSING_ERROR
    if arguments.nuke_executable and (arguments.config or arguments.runner_name):
        raise RUNNER_AND_EXE_PROVIDED_ERROR

    if arguments.nuke_executable:
        runner = Runner(
            arguments.nuke_executable,
            pytest_args=arguments.pytest_args,
            run_in_terminal_mode=arguments.run_in_terminal_mode,
        )
        sys.exit(runner.execute_tests(arguments.test_directory))
        return  # Unreachable but required for unittest which won't exit with sys.exit.

    search_start = Path(str(arguments.test_directory).split("::")[0])
    config = arguments.config or find_configuration(search_start)
    if not config:
        raise NO_CONFIG_FOUND_ERROR

    try:
        runners = load_runners(config)
    except FileNotFoundError as e:
        msg = f"Config file '{config}' not found."
        raise CLICommandError(msg) from e

    try:
        runner = runners[arguments.runner_name]
    except KeyError as e:
        msg = f"Runner '{arguments.runner_name}' not found. Available runners: {','.join(runners)} "
        raise CLICommandError(msg) from e

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
    help="Specify a json to read as config to use for the tests. "
    "By default, a 'runners.json' file is searched within the folders of the test path.",
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

    The `test-path` is the folder or file of the tests you want to execute.
    Use the pytest folder/file.py::class::method notation to run single tests.
    For further options consult the pytest documentation.

    If you don't specify the test-path it will use the current directory
    like pytest does.

    Use the `nuke-executable` argument to specify the location of your nuke executable.

    If you like to store the `nuke-executable` and some additional configuration,
    you can create a runners.json file and reference created runners with the `runner-name` argument:

    NukeTestrunner --config runners.json --runner-name nuke15 --test-path /tests

    If a "runners.json" is saved within the folder tree of the test path, it will be automatically loaded.
    Then you can use a shorter command:

    NukeTestrunner --runner-name nuke15 --test-path /tests

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
        context = click.get_current_context()
        context.fail(f"{e!s}\n\nCheck out the help above for additional support.")
        context.exit()


if __name__ == "__main__":
    main()
