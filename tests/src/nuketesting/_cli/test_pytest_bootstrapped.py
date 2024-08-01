from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest
from nuketesting._cli.run_pytest_bootstrapped import _run_tests


@patch("pytest.main", return_value=0)
@pytest.mark.parametrize(
    "test_directories",
    [
        ["first/dir", "second/dir"],
        ["first/dir", "second/dir", "third/directory"],
    ],
)
def test__run_tests_path_insertion(pytest_mock: MagicMock, test_directories: list[str]) -> None:
    """Test path insertion to add both nuketesting directory and pytest."""
    test_directories_combined = ":".join(test_directories)

    with patch("nuketesting._cli.run_pytest_bootstrapped.sys") as sys_mock:
        _run_tests(test_directories_combined, "", [])

    for test_directory in test_directories:
        expected_call = call(test_directory)
        assert expected_call in sys_mock.path.append.call_args_list


@patch("nuketesting._cli.run_pytest_bootstrapped.sys")
@pytest.mark.parametrize(
    ("test_directory", "test_pytest_args", "expected_arguments"),
    [
        ("my_test_directory", [], ["my_test_directory"]),
        ("my_test_directory", ["-v"], ["my_test_directory", "-v"]),
        ("my_test_directory", ["-v", "--hey"], ["my_test_directory", "-v", "--hey"]),
    ],
)
def test__run_tests_pytest_args(
    sys_mock: MagicMock,
    test_directory: str,
    test_pytest_args: list[str],
    expected_arguments: list[str],
) -> None:
    """Test argument forwarding to the pytest main call."""
    with patch("pytest.main", return_value=0) as pytest_mock:
        _run_tests("", test_directory, test_pytest_args)

    pytest_mock.assert_called_once_with(expected_arguments)


def test__run_tests_forward_exit_code() -> None:
    """Test the forwarding of the exit code of the pytest run."""
    with patch("nuketesting._cli.run_pytest_bootstrapped.sys") as sys_mock, patch("pytest.main", return_value=1):
        _run_tests("", "", [])

    sys_mock.exit.assert_called_once_with(1)
