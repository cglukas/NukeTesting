from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

from nuketesting.runner.run_pytest_bootstrapped import BootstrapError, _parse_args, _run_tests


# noinspection PyUnreachableCode
@patch("nuketesting.runner.run_pytest_bootstrapped.Path.is_dir", MagicMock(return_value=True))
@patch("pytest.main", MagicMock(return_value=0))
@pytest.mark.parametrize(
    "test_directories",
    [
        ["first/dir", "second/dir"],
        ["first/dir", "second/dir", "third/directory"],
    ],
)
def test__run_tests_path_insertion(test_directories: list[str]) -> None:
    """Test path insertion to add both nuketesting directory and pytest."""
    test_directories_combined = ";".join(test_directories)

    with patch("nuketesting.runner.run_pytest_bootstrapped.sys") as sys_mock:
        _run_tests(test_directories_combined, "", [])

    for test_directory in test_directories:
        expected_call = call(test_directory)
        assert expected_call in sys_mock.path.append.call_args_list


# noinspection PyUnreachableCode
@patch("nuketesting.runner.run_pytest_bootstrapped.sys")
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


# noinspection PyUnreachableCode
def test__run_tests_forward_exit_code() -> None:
    """Test the forwarding of the exit code of the pytest run."""
    with patch("nuketesting.runner.run_pytest_bootstrapped.sys") as sys_mock, patch("pytest.main", return_value=1):
        _run_tests("", "", [])

    sys_mock.exit.assert_called_once_with(1)


@patch("nuketesting.runner.run_pytest_bootstrapped.sys")
@patch("pytest.main", return_value=0)
@patch("nuketesting.runner.run_pytest_bootstrapped.Path.is_dir", return_value=False)
def test__run_with_non_existing_path(sys_mock, pytest_mock, is_dir_mock) -> None:
    with pytest.raises(BootstrapError, match="Package directory does not exist: 'non/existing/directory'"):
        _run_tests("non/existing/directory", "", [])


@pytest.mark.parametrize(
    ("test_directory", "test_packages", "test_pytest_args"),
    [
        ("test_dir", "test_packages", []),
        ("test_dir", "test_packages", ["-x"]),
        ("test_dir", "test_packages", ["-x", "--help"]),
    ],
)
def test__parse_args(test_directory: str, test_packages: str, test_pytest_args: list[str]) -> None:
    """Test arguments to be parsed from provided arguments"""
    test_arguments = ["--test_dir", test_directory, "--packages_directory", test_packages] + [
        f"--pytest_arg={argument}" for argument in test_pytest_args
    ]

    parsed_arguments = _parse_args(test_arguments)

    assert parsed_arguments.test_dir == test_directory
    assert parsed_arguments.packages_directory == test_packages
    if test_pytest_args:
        assert parsed_arguments.pytest_arg == test_pytest_args
