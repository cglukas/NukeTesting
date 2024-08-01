"""Test the run test utility."""

from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from datamodel import constants
from _cli.runner import Runner

pytest.importorskip(
    "run_tests",
    reason="This module is not importable by the nuke runtime. "
    "Skip tests of this module when executing them with nuke.",
)

from run_tests import run_tests


@pytest.fixture()
def runner() -> MagicMock:
    """Mock for the runner class."""
    with patch("run_tests.Runner", spec=Runner) as runner_mock:
        yield runner_mock


@pytest.fixture(autouse=True)
def sys_exit() -> MagicMock:
    """Mock the sys.exit for the testrunner tests."""
    with patch("sys.exit") as good_bye:
        yield good_bye


def test_create_runner(runner: MagicMock) -> None:
    """Test that a runner instance is created from the user path."""
    run_tests("nuke_path", ".")

    runner.assert_called_with("nuke_path")


def test_runner_executed(runner: MagicMock) -> None:
    """Test that the runner is executed."""
    instance = runner.return_value
    run_tests("nuke_path", ".")

    instance.execute_tests.assert_called_once_with(".")


def test_exit_code_forwarding(runner: MagicMock, sys_exit: MagicMock) -> None:
    """Test that the return code of the runner is forwarded to the caller."""
    instance = runner.return_value
    instance.execute_tests.return_value = 1928

    run_tests("nuke_path", ".")

    sys_exit.assert_called_with(1928)


@patch("run_tests.find_configuration", MagicMock(spec=str))
@patch("run_tests.load_runners")
def test_config_file_loaded(load_config: MagicMock, runner: MagicMock) -> None:
    """Test that runners from the config are prioritized."""
    my_runner = MagicMock(spec=Runner)
    load_config.return_value = {"my_runner": my_runner}

    run_tests("my_runner", "test_path")

    my_runner.execute_tests.assert_called_with("test_path")


@patch("run_tests.find_configuration")
@patch("run_tests.load_runners")
def test_search_for_config_used(load_config: MagicMock, find_config: MagicMock, runner: MagicMock) -> None:
    """Test that the test file is used to find the config."""
    run_tests("my_runner", "path/to/test.py")

    find_config.assert_called_once_with(Path("path/to/test.py"))
    load_config.assert_called_once_with(find_config.return_value)


@pytest.mark.nuke()
@pytest.mark.slow()
@pytest.mark.parametrize(
    ("test", "code"),
    [("test_failing", 1), ("test_passing", 0), ("not_existing", 4)],
)
def test_commandline(test: str, code: int) -> None:
    """Test that the script can be executed from the commandline."""
    run_file = inspect.getfile(run_tests)
    call = [sys.executable, run_file]
    tests_folder = constants.NUKE_TESTING_FOLDER / "tests"
    reference_test = tests_folder / f"reference_tests.py::{test}"

    call.extend(["nuke", str(reference_test)])

    print(call)  # noqa: T201
    process = subprocess.run(call, stdout=subprocess.PIPE, check=False)
    # Used for debugging subprocess output:
    print(process.stdout.decode())  # noqa: T201

    assert process.returncode == code


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ([], "Missing argument 'INTERPRETER'"),
        (["."], "Missing argument 'TESTS'"),
    ],
)
def test_commandline_missing_parameters(args: list[str], message: str) -> None:
    """Test that the nuke path and the tests are required."""
    run_file = inspect.getfile(run_tests)
    call = [sys.executable, run_file]

    call.extend(args)
    process = subprocess.run(call, stderr=subprocess.PIPE, check=False)

    assert message in process.stderr.decode()
