"""Test the run test utility."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from nuke_test_runner._cli.main import main
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

    with patch("nuke_test_runner._cli.main.TestRunArguments") as test_run_arguments_mock:
        cli_testrunner.invoke(main, ["-n", "nuke_path"])

    test_run_arguments_mock.assert_called_once_with(
        nuke_executable="nuke_path",
        test_directory=".",
        config=None,
        interactive=True,
        pytest_args=(),
        runner_name=None,
    )


def test_pass_all_arguments_to_data_object() -> None:
    """Test simple pass of arguments to dataclass."""
    cli_testrunner = CliRunner()

    with patch("nuke_test_runner._cli.main.TestRunArguments") as test_run_arguments_mock:
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
        test_directory="test_dir",
        config="config/path.json",
        interactive=False,
        pytest_args=("-v test", "-x"),
        runner_name="Boomer",
    )


# def test_create_runner(runner: MagicMock) -> None:
#     """Test that a runner instance is created from the user path."""
#     cli_testrunner = CliRunner()

#     cli_testrunner.invoke(main, ["-n nuke_path"])

#     runner.assert_called_with("nuke_path", ".")


# def test_runner_executed(runner: MagicMock) -> None:
#     """Test that the runner is executed."""
#     instance = runner.return_value
#     cli_testrunner = CliRunner()

#     cli_testrunner.invoke(main, ["-n nuke_path"])

#     instance.execute_tests.assert_called_once_with(".")


# def test_runner_executed_with_test_path(runner: MagicMock) -> None:
#     """Test that the runner is executed."""
#     instance = runner.return_value
#     cli_testrunner = CliRunner()

#     cli_testrunner.invoke(main, ["-n nuke_path", "-t test_path"])

#     instance.execute_tests.assert_called_once_with("test_path")


# def test_exit_code_forwarding(runner: MagicMock, sys_exit: MagicMock) -> None:
#     """Test that the return code of the runner is forwarded to the caller."""
#     instance = runner.return_value
#     instance.execute_tests.return_value = 1928
#     cli_testrunner = CliRunner()

#     cli_testrunner.invoke(main, ["-n nuke_path"])

#     sys_exit.assert_called_with(1928)


# @patch("run_tests.find_configuration", MagicMock(spec=str))
# @patch("run_tests.load_runners")
# def test_config_file_loaded(load_config: MagicMock, runner: MagicMock) -> None:
#     """Test that runners from the config are prioritized."""
#     my_runner = MagicMock(spec=Runner)
#     load_config.return_value = {"my_runner": my_runner}

#     cli_testrunner = CliRunner()
#     cli_testrunner.invoke(main, ["-n nuke_path", "-c runner.json"])

#     run_tests("my_runner", "test_path")

#     my_runner.execute_tests.assert_called_with("test_path")


# @patch("run_tests.find_configuration")
# @patch("run_tests.load_runners")
# def test_search_for_config_used(load_config: MagicMock, find_config: MagicMock, runner: MagicMock) -> None:
#     """Test that the test file is used to find the config."""
#     run_tests("my_runner", "path/to/test.py")

#     find_config.assert_called_once_with(Path("path/to/test.py"))
#     load_config.assert_called_once_with(find_config.return_value)


# @pytest.mark.nuke()
# @pytest.mark.slow()
# @pytest.mark.parametrize(
#     ("test", "code"),
#     [("test_failing", 1), ("test_passing", 0), ("not_existing", 4)],
# )
# def test_commandline(test: str, code: int) -> None:
#     """Test that the script can be executed from the commandline."""
#     run_file = inspect.getfile(run_tests)
#     call = [sys.executable, run_file]
#     tests_folder = constants.NUKE_TESTING_FOLDER / "tests"
#     reference_test = tests_folder / f"reference_tests.py::{test}"

#     call.extend(["nuke", str(reference_test)])

#     print(call)
#     process = subprocess.run(call, stdout=subprocess.PIPE, check=False)
#     # Used for debugging subprocess output:
#     print(process.stdout.decode())

#     assert process.returncode == code


# @pytest.mark.parametrize(
#     ("args", "message"),
#     [
#         ([], "Missing argument 'INTERPRETER'"),
#         (["."], "Missing argument 'TESTS'"),
#     ],
# )
# def test_commandline_missing_parameters(args: list[str], message: str) -> None:
#     """Test that the nuke path and the tests are required."""
#     run_file = inspect.getfile(run_tests)
#     call = [sys.executable, run_file]

#     call.extend(args)
#     process = subprocess.run(call, stderr=subprocess.PIPE, check=False)

#     assert message in process.stderr.decode()
