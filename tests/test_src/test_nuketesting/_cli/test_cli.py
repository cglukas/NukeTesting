"""Test the run test utility."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from click.testing import CliRunner
from nuketesting._cli.main import CLICommandError, CLIRunArguments, _run_tests, main
from nuketesting._cli.runner import Runner

pytest.importorskip(
    "nuketesting._cli",
    reason="This module is not importable by the nuke runtime. "
    "Skip tests of this module when executing them with nuke.",
)


@pytest.fixture()
def runner() -> MagicMock:
    """Mock for the runner class."""
    with patch("nuketesting._cli.main.Runner", spec=Runner) as runner_mock:
        yield runner_mock


@pytest.fixture(autouse=True)
def sys_exit() -> MagicMock:
    """Mock the sys.exit for the testrunner tests."""
    with patch("sys.exit") as good_bye:
        yield good_bye


def test_pass_arguments_to_data_object() -> None:
    """Test simple pass of arguments to dataclass."""
    cli_testrunner = CliRunner()

    with patch("nuketesting._cli.main.CLIRunArguments") as test_run_arguments_mock:
        cli_testrunner.invoke(main, ["-n", "nuke_path"])

    test_run_arguments_mock.assert_called_once_with(
        nuke_executable="nuke_path",
        test_directory=".",
        config=None,
        run_in_terminal_mode=True,
        pytest_args=(),
        runner_name=None,
    )


def test_pass_all_arguments_to_data_object() -> None:
    """Test passing of all possible arguments to dataclass object."""
    cli_testrunner = CliRunner()
    test_cli_run_arguments = MagicMock(spec=CLIRunArguments)
    expected_cli_return_value = MagicMock()
    test_cli_run_arguments.return_value = expected_cli_return_value
    with patch("nuketesting._cli.main.CLIRunArguments", test_cli_run_arguments), patch(
        "nuketesting._cli.main._run_tests"
    ) as run_tests_mock:
        cli_testrunner.invoke(
            main,
            [
                "-n",
                "nuke_path",
                "-t",
                "test_dir",
                "-c",
                "config/path.json",
                "--terminal",
                "false",
                "-p",
                "-v test",
                "-p",
                "-x",
                "-r",
                "Boomer",
            ],
        )

    test_cli_run_arguments.assert_called_once_with(
        nuke_executable="nuke_path",
        test_directory="test_dir",
        config="config/path.json",
        run_in_terminal_mode=False,
        pytest_args=("-v test", "-x"),
        runner_name="Boomer",
    )
    run_tests_mock.assert_called_once_with(expected_cli_return_value)


def test_run_arguments_convert_to_path() -> None:
    """Test that the CLIRunArguments converts the paths to pathlib."""
    test_cli_run_arguments = CLIRunArguments("test", (), "executable", "config")

    assert test_cli_run_arguments.test_directory == Path("test")
    assert test_cli_run_arguments.nuke_executable == Path("executable")
    assert test_cli_run_arguments.config == Path("config")


def test_exception_when_not_enough_arguments() -> None:
    """Test to raise a TestRunCommandError when neither exe or config is provided."""
    with pytest.raises(CLICommandError, match="Neither a config or a Nuke executable is provided."):
        CLIRunArguments(".")


def test_runner_executed(runner: MagicMock) -> None:
    """Test that the runner is executed."""
    instance = runner.return_value
    cli_testrunner = CliRunner()

    cli_testrunner.invoke(main, ["-n", "nuke_path"])

    instance.execute_tests.assert_called_once_with(Path())


def test_exit_code_forwarding(runner: MagicMock, sys_exit: MagicMock) -> None:
    """Test that the return code of the runner is forwarded to the caller."""
    instance = runner.return_value
    instance.execute_tests.return_value = 1928
    cli_testrunner = CliRunner()

    cli_testrunner.invoke(main, ["-n", "nuke_path"])

    assert sys_exit.call_args_list[0] == call(
        1928
    )  # As the CLIRunner object from click is returning 0 as exit code always.


@patch("nuketesting._cli.main.find_configuration", MagicMock(spec=str))
@patch("nuketesting._cli.main.load_runners")
def test_config_file_loaded(load_config: MagicMock, runner: MagicMock) -> None:
    """Test that runners from the config are prioritized."""
    my_runner = MagicMock(spec=Runner)
    load_config.return_value = {"my_runner": my_runner}

    arguments = CLIRunArguments(".", nuke_executable="test.exe", runner_name="my_runner")
    _run_tests(arguments)
    my_runner.execute_tests.assert_called_with(Path())


@patch("nuketesting._cli.main.find_configuration", MagicMock(spec=str))
@patch("nuketesting._cli.main.load_runners")
def test_config_file_preferred_with_specified_json(load_config: MagicMock, runner: MagicMock) -> None:
    """Test that runners from the json are prioritized."""
    my_runner = MagicMock(spec=Runner)
    load_config.return_value = {"my_runner": my_runner}

    arguments = CLIRunArguments(".", config="test.json", runner_name="my_runner")
    _run_tests(arguments)

    load_config.assert_called_once_with(Path("test.json"))


@patch("nuketesting._cli.main.find_configuration")
@patch("nuketesting._cli.main.load_runners")
def test_search_for_config_used(load_config: MagicMock, find_config: MagicMock, runner: MagicMock) -> None:
    """Test that the test file is used to find the config."""
    arguments = CLIRunArguments(
        "path/to/test.py",
        nuke_executable="something",
    )
    _run_tests(arguments)

    find_config.assert_called_once_with(Path("path/to/test.py"))
    load_config.assert_called_once_with(find_config.return_value)
