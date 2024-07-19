"""Test the run test utility."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from click.testing import CliRunner
from nuke_test_runner._cli.main import CLICommandError, CLIRunArguments, main
from nuke_test_runner._cli.runner import Runner

pytest.importorskip(
    "nuke_test_runner._cli",
    reason="This module is not importable by the nuke runtime. "
    "Skip tests of this module when executing them with nuke.",
)


@pytest.fixture()
def runner() -> MagicMock:
    """Mock for the runner class."""
    with patch("nuke_test_runner._cli.main.Runner", spec=Runner) as runner_mock:
        yield runner_mock


@pytest.fixture(autouse=True)
def sys_exit() -> MagicMock:
    """Mock the sys.exit for the testrunner tests."""
    with patch("sys.exit") as good_bye:
        yield good_bye


def test_pass_arguments_to_data_object() -> None:
    """Test simple pass of arguments to dataclass."""
    cli_testrunner = CliRunner()

    with patch("nuke_test_runner._cli.main.CLIRunArguments") as test_run_arguments_mock:
        cli_testrunner.invoke(main, ["-n", "nuke_path"])

    test_run_arguments_mock.assert_called_once_with(
        nuke_executable="nuke_path",
        test_directories=".",
        config=None,
        run_interactive=True,
        pytest_args=(),
        runner_name=None,
    )


def test_pass_all_arguments_to_data_object() -> None:
    """Test passing of all possible arguments to dataclass object."""
    cli_testrunner = CliRunner()

    with patch("nuke_test_runner._cli.main.CLIRunArguments") as test_run_arguments_mock:
        cli_testrunner.invoke(
            main,
            [
                "-n",
                "nuke_path",
                "-t",
                "test_dir",
                "-c",
                "config/path.json",
                "-i",
                "false",
                "-p",
                "-v test",
                "-p",
                "-x",
                "-r",
                "Boomer",
            ],
        )

    test_run_arguments_mock.assert_called_once_with(
        nuke_executable="nuke_path",
        test_directories="test_dir",
        config="config/path.json",
        run_interactive=False,
        pytest_args=("-v test", "-x"),
        runner_name="Boomer",
    )


def test_exception_when_not_enough_arguments() -> None:
    """Test to raise a TestRunCommandError when neither exe or config is provided."""
    with pytest.raises(CLICommandError, match="Neither a config or a Nuke executable is provided."):
        CLIRunArguments(".")


def test_runner_executed(runner: MagicMock) -> None:
    """Test that the runner is executed."""
    instance = runner.return_value
    cli_testrunner = CliRunner()

    cli_testrunner.invoke(main, ["-n nuke_path"])

    instance.execute_tests.assert_called_once_with(".")


def test_exit_code_forwarding(runner: MagicMock, sys_exit: MagicMock) -> None:
    """Test that the return code of the runner is forwarded to the caller."""
    instance = runner.return_value
    instance.execute_tests.return_value = 1928
    cli_testrunner = CliRunner()

    cli_testrunner.invoke(main, ["-n", "nuke_path"])

    assert sys_exit.call_args_list[0] == call(1928)  # As CLIRunner is returning 0 automatically.


@patch("nuke_test_runner._cli.main.find_configuration", MagicMock(spec=str))
@patch("nuke_test_runner._cli.main.load_runners")
def test_config_file_loaded(load_config: MagicMock, runner: MagicMock) -> None:
    """Test that runners from the config are prioritized."""
    my_runner = MagicMock(spec=Runner)
    load_config.return_value = {"my_runner": my_runner}

    arguments = CLIRunArguments(".", config="test.json", runner_name="my_runner")
    arguments.run_tests()
    my_runner.execute_tests.assert_called_with(".")


@patch("nuke_test_runner._cli.main.find_configuration")
@patch("nuke_test_runner._cli.main.load_runners")
def test_search_for_config_used(load_config: MagicMock, find_config: MagicMock, runner: MagicMock) -> None:
    """Test that the test file is used to find the config."""
    arguments = CLIRunArguments(
        "path/to/test.py",
        nuke_executable="something",
    )
    arguments.run_tests()

    find_config.assert_called_once_with(Path("path/to/test.py"))
    load_config.assert_called_once_with(find_config.return_value)
