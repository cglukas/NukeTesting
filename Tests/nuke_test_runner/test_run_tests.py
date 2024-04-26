"""Test the run test utility."""
from unittest.mock import patch, MagicMock

import pytest

from nuke_test_runner.run_tests import run_tests
from nuke_test_runner.runner import Runner


@pytest.fixture()
def runner() -> MagicMock:
    with patch(
        "nuke_test_runner.run_tests.Runner", spec=Runner
    ) as runner_mock:
        yield runner_mock


@pytest.fixture(autouse=True)
def sys_exit() -> MagicMock:
    """Mock the sys.exit for the testrunner tests."""
    with patch("sys.exit") as good_bye:
        yield good_bye


def test_create_runner(runner: MagicMock) -> None:
    """Test that a runner instance is created from the user path."""
    run_tests("nuke_path", ["."])

    runner.assert_called_with("nuke_path", ["."])


def test_runner_executed(runner: MagicMock) -> None:
    """Test that the runner is executed."""
    instance = runner.return_value
    run_tests("nuke_path", ["."])

    instance.execute_tests.assert_called_once()


def test_exit_code_forwarding(runner: MagicMock, sys_exit: MagicMock) -> None:
    """Test that the return code of the runner is forwarded to the caller."""
    instance = runner.return_value
    instance.execute_tests.return_value = 1928

    run_tests("nuke_path", ["."])

    sys_exit.assert_called_with(1928)
