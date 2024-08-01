from unittest.mock import call, patch

import pytest
from nuketesting._cli.run_pytest_bootstrapped import _run_tests


@pytest.mark.parametrize(
    "test_directories",
    [
        ["first/dir", "second/dir"],
        ["first/dir", "second/dir", "third/directory"],
    ],
)
def test__run_tests_path_insertion(test_directories: list[str]) -> None:
    """Test path insertion to add both nuketesting directory and pytest."""
    test_directories_combined = ":".join(test_directories)

    with patch("nuketesting._cli.run_pytest_bootstrapped.sys") as sys_mock:
        with patch("pytest.main", return_value=0):
            _run_tests(test_directories_combined, "", [])

    for test_directory in test_directories:
        expected_call = call(0, test_directory)
        assert expected_call in sys_mock.path.insert.call_args_list


@pytest.mark.parametrize(
    ("test_directory", "test_pytest_args", "expected_arguments"),
    [
        ("my_test_directory", [], ["my_test_directory"]),
        ("my_test_directory", ["-v"], ["my_test_directory", "-v"]),
        ("my_test_directory", ["-v", "--hey"], ["my_test_directory", "-v", "--hey"]),
    ],
)
def test__run_tests_pytest_args(
    test_directory: str, test_pytest_args: list[str], expected_arguments: list[str]
) -> None:
    """Test argument forwarding to the pytest main call."""
    with patch("nuketesting._cli.run_pytest_bootstrapped.sys"):
        with patch("pytest.main", return_value=0) as pytest_mock:
            _run_tests("", test_directory, test_pytest_args)

    pytest_mock.assert_called_once_with(expected_arguments)


def test__run_tests_forward_exit_code() -> None:
    """Test the forwarding of the exit code of the pytest run."""
    with patch("nuketesting._cli.run_pytest_bootstrapped.sys") as sys_mock:
        with patch("pytest.main", return_value=1):
            _run_tests("", "", [])

    sys_mock.exit.assert_called_once_with(1)
