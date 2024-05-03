"""Test the run test utility."""
import inspect
import subprocess
import sys
from unittest.mock import patch, MagicMock

import pytest

from datamodel import constants
from run_tests import run_tests
from nuke_test_runner.runner import Runner


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


@pytest.mark.nuke
@pytest.mark.slow
@pytest.mark.parametrize(
    ("test", "code"),
    [("test_failing", 1), ("test_passing", 0), ("not_existing", 4)],
)
def test_commandline(test: str, code: int) -> None:
    """Test that the script can be executed from the commandline."""
    run_file = inspect.getfile(run_tests)
    call = [sys.executable, run_file]
    reference_test = (
        constants.NUKE_TESTING_FOLDER / "tests" / f"reference_tests.py::{test}"
    )
    # FIXME [lukas] replace a static path of the nuke executable.
    call.extend(
        [r"C:\Program Files\Nuke15.0v3\Nuke15.0.exe", str(reference_test)]
    )
    print(call)
    process = subprocess.run(call, stdout=subprocess.PIPE)
    # Used for debugging subprocess output:
    print(process.stdout.decode())

    assert process.returncode == code


@pytest.mark.parametrize(
    ("args", "message"), [([], "Missing argument 'EXECUTABLE'"), (["."], "Missing argument 'TESTS'")]
)
def test_commandline_missing_parameters(args: list[str], message: str) -> None:
    """Test that the nuke path and the tests are required."""
    run_file = inspect.getfile(run_tests)
    call = [sys.executable, run_file]

    call.extend(args)
    process = subprocess.run(call, stderr=subprocess.PIPE)

    assert message in process.stderr.decode()
