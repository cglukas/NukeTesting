"""Test the run test utility."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, call, patch

import click
import pytest
from click.testing import CliRunner

from nuketesting.runner.main import CLICommandError, CLIRunArguments, _run_tests, main
from nuketesting.runner.runner import Runner

pytest.importorskip(
    "nuketesting.runner",
    reason="This module is not importable by the nuke runtime. "
    "Skip tests of this module when executing them with nuke.",
)


@pytest.fixture
def runner() -> MagicMock:
    """Mock for the runner class."""
    with patch("nuketesting.runner.main.Runner", spec=Runner) as runner_mock:
        yield runner_mock


@pytest.fixture(autouse=True)
def sys_exit() -> MagicMock:
    """Mock the sys.exit for the testrunner tests."""
    with patch("sys.exit") as good_bye:
        yield good_bye


class TestArgumentParsing:
    """Tests for argument parsing."""

    def test_pass_arguments_to_data_object(self) -> None:
        """Test simple pass of arguments to dataclass."""
        cli_testrunner = CliRunner()

        with patch("nuketesting.runner.main.CLIRunArguments") as test_run_arguments_mock:
            cli_testrunner.invoke(main, ["-n", "nuke_path"])

        test_run_arguments_mock.assert_called_once_with(
            nuke_executable="nuke_path",
            test_directory=".",
            config=None,
            run_in_terminal_mode=True,
            pytest_args=(),
            runner_name=None,
        )

    def test_pass_all_arguments_to_data_object(self) -> None:
        """Test passing of all possible arguments to dataclass object."""
        cli_testrunner = CliRunner()
        test_cli_run_arguments = MagicMock(spec=CLIRunArguments)
        expected_cli_return_value = MagicMock()
        test_cli_run_arguments.return_value = expected_cli_return_value
        with patch("nuketesting.runner.main.CLIRunArguments", test_cli_run_arguments), patch(
            "nuketesting.runner.main._run_tests"
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

    def test_no_arguments_will_fail(self) -> None:
        """Test that no arguments will cause click to print fail message."""
        cli_testrunner = CliRunner()

        with patch.object(click.Context, "fail") as fail_message:
            cli_testrunner.invoke(main, [])

        fail_message.assert_called()


class TestCLIRunArguments:
    """Test cases for the CLI datastruct."""

    def test_run_arguments_convert_to_path(self) -> None:
        """Test that the CLIRunArguments converts the paths to pathlib."""
        test_cli_run_arguments = CLIRunArguments("test", (), "executable", "config")

        assert test_cli_run_arguments.test_directory == Path("test")
        assert test_cli_run_arguments.nuke_executable == Path("executable")
        assert test_cli_run_arguments.config == Path("config")


class TestRunnerExecution:
    """Testcases for the execution of the testrunner."""

    def test_runner_executed(self, runner: MagicMock) -> None:
        """Test that the runner is executed."""
        instance = runner.return_value
        cli_testrunner = CliRunner()

        cli_testrunner.invoke(main, ["-n", "nuke_path"])

        instance.execute_tests.assert_called_once_with(Path())

    def test_exit_code_forwarding(self, runner: MagicMock, sys_exit: MagicMock) -> None:
        """Test that the return code of the runner is forwarded to the caller."""
        instance = runner.return_value
        instance.execute_tests.return_value = 1928
        cli_testrunner = CliRunner()

        cli_testrunner.invoke(main, ["-n", "nuke_path"])

        assert sys_exit.call_args_list[0] == call(
            1928
        )  # As the CLIRunner object from click is returning 0 as exit code always.


class TestConfigOptions:
    """Tests for the configuration loading."""

    @patch("nuketesting.runner.main.find_configuration")
    @patch("nuketesting.runner.main.load_runners")
    def test_config_auto_loaded(self, load_config: MagicMock, find_config: MagicMock, runner: MagicMock) -> None:
        """Test that runner configuration is searched if `runner_name` is provided."""
        my_runner = MagicMock(spec=Runner)
        load_config.return_value = {"my_runner": my_runner}

        arguments = CLIRunArguments(".", runner_name="my_runner")
        _run_tests(arguments)
        my_runner.execute_tests.assert_called_with(Path())
        find_config.assert_called_once_with(Path())

    @patch("nuketesting.runner.main.find_configuration", MagicMock(spec=str))
    @patch("nuketesting.runner.main.load_runners")
    def test_config_file_preferred_with_specified_json(self, load_config: MagicMock, runner: MagicMock) -> None:
        """Test that runners from the json are prioritized."""
        my_runner = MagicMock(spec=Runner)
        load_config.return_value = {"my_runner": my_runner}

        arguments = CLIRunArguments(".", config="test.json", runner_name="my_runner")
        _run_tests(arguments)

        load_config.assert_called_once_with(Path("test.json"))

    @patch("nuketesting.runner.main.find_configuration", MagicMock(spec=str))
    @patch("nuketesting.runner.main.load_runners")
    def test_runner_not_in_config(self, load_config: MagicMock, runner: MagicMock) -> None:
        """Test that runners from the json are prioritized."""
        my_runner = MagicMock(spec=Runner)
        load_config.return_value = {"my_runner": my_runner}

        arguments = CLIRunArguments(".", runner_name="wrong_runner")
        with pytest.raises(CLICommandError, match="Runner 'wrong_runner' not found."):
            _run_tests(arguments)

    @patch("nuketesting.runner.main.find_configuration")
    def test_no_config_found(self, find_config: MagicMock, runner: MagicMock) -> None:
        """Test that runners from the json are prioritized."""
        find_config.return_value = None
        arguments = CLIRunArguments(".", runner_name="test")

        with pytest.raises(CLICommandError, match="No config found."):
            _run_tests(arguments)

    def test_config_does_not_exist(self, runner: MagicMock) -> None:
        """Test that not existing configs raise an error.

        It's important that a CLICommandError is raised instead of a FileNotFoundError
        because they will be formatted nicely for users.
        """
        arguments = CLIRunArguments(".", config="test", runner_name="test")

        with pytest.raises(CLICommandError, match="Config file '.+' not found."):
            _run_tests(arguments)

    @patch("nuketesting.runner.main.find_configuration")
    @patch("nuketesting.runner.main.load_runners")
    def test_search_for_config_used(self, load_config: MagicMock, find_config: MagicMock, runner: MagicMock) -> None:
        """Test that the test file is used to find the config."""
        arguments = CLIRunArguments(
            "path/to/test.py",
            runner_name="something",
        )
        _run_tests(arguments)

        find_config.assert_called_once_with(Path("path/to/test.py"))
        load_config.assert_called_once_with(find_config.return_value)

    @patch("nuketesting.runner.main.find_configuration")
    @patch("nuketesting.runner.main.load_runners")
    def test_config_ignored(self, load_config: MagicMock, find_config: MagicMock, runner: MagicMock) -> None:
        """Test that the config is ignored if a nuke executable is provided."""
        arguments = CLIRunArguments(
            "path/to/test.py",
            nuke_executable="something",
        )
        _run_tests(arguments)

        find_config.assert_not_called()
        load_config.assert_not_called()

    @pytest.mark.parametrize(
        "invalid_kwargs",
        [
            {"nuke_executable": "something", "runner_name": "something_else"},
            {"nuke_executable": "something", "config": "some config"},
            {"nuke_executable": "something", "runner_name": "something_else", "config": "some config"},
        ],
    )
    def test_executable_and_runner_provided(self, invalid_kwargs: dict[str, str], runner: MagicMock) -> None:
        """Test that providing a runner name and an executable raises an error.

        We can't decide what to prioritise. The configured runner or the nuke executable.
        The user needs to decide instead.
        """
        arguments = CLIRunArguments("path/to/test.py", **invalid_kwargs)
        with pytest.raises(
            CLICommandError,
            match="Only provide nuke executable or runner configuration/name.",
        ):
            _run_tests(arguments)
