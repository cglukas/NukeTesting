from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple
from unittest.mock import MagicMock, patch

import pytest
from nuketesting._cli.runner import Runner, RunnerException
from nuketesting.datamodel.constants import RUN_TESTS_SCRIPT


@patch("nuketesting._cli.runner.Path.is_dir", return_value=True)
@pytest.mark.parametrize(
    ("test_platform", "test_executable", "test_python_version"),
    [
        ("Windows", Path("example_dir/Nuke15.1.exe"), (3, 9)),
        ("Linux", Path("example_dir/Nuke15.1"), (3, 10)),
    ],
)
def test_find_nuke_python_package(
    is_dir_mock: MagicMock,
    test_platform: str,
    test_executable: str,
    test_python_version: tuple[int, int],
) -> None:
    """Test to find the Nuke python package."""
    with patch("nuketesting._cli.runner.Runner._check_nuke_executable"):
        runner = Runner(nuke_executable=test_executable)

    python_version_mock = MagicMock(spec=NamedTuple)
    python_version_mock.major = test_python_version[0]
    python_version_mock.minor = test_python_version[1]
    python_version_folder = f"python{python_version_mock.major}.{python_version_mock.minor}"

    with patch("nuketesting._cli.runner.platform.system", return_value=test_platform), patch(
        "nuketesting._cli.runner.sys.version_info", python_version_mock
    ):
        assert runner._find_nuke_python_package() == Path("example_dir/lib/") / python_version_folder / "site-packages"


@patch("nuketesting._cli.runner.Runner._check_nuke_executable")
def test_find_nuke_python_package_macos(executable_mock: MagicMock) -> None:
    """Test to raise an exception on MacOS as this functionality is not
    supported with third party interpreters.

    (https://learn.foundry.com/nuke/content/comp_environment/script_editor/nuke_python_module.html)
    """
    runner = Runner(nuke_executable="example_executable")

    with patch("nuketesting._cli.runner.platform.system", return_value="Darwin"), pytest.raises(
        RunnerException,
        match="On MacOS the tests can only run in terminal mode.",
    ):
        runner._find_nuke_python_package()  # noqa: SLF001


@patch("nuketesting._cli.runner.platform.system", return_value="linux")
@patch("nuketesting._cli.runner.Path.is_dir", return_value=False)
@pytest.mark.parametrize(
    "test_python_version",
    [
        (3, 9),
        (3, 6),
        (1, 2),
    ],
)
def test_find_nuke_python_package_not_found(platform_mock, mock_is_dir, test_python_version):
    """Test to raise an exception if folder is not found."""
    with patch("nuketesting._cli.runner.Runner._check_nuke_executable"):
        runner = Runner(nuke_executable="example_executable")

    python_version_mock = MagicMock(spec=NamedTuple)
    python_version_mock.major = test_python_version[0]
    python_version_mock.minor = test_python_version[1]

    expected_message = (
        "The current python version does not match the Nuke version. "
        f"This is Python: {python_version_mock.major}.{python_version_mock.minor}. "
        "Please run in terminal mode instead."
    )

    with patch("nuketesting._cli.runner.sys.version_info", python_version_mock), pytest.raises(
        RunnerException, match=expected_message
    ):
        runner._find_nuke_python_package()


@pytest.mark.parametrize(
    "tests_path",
    ["/test", ".", "C:\\windows\\path", "test.py", "gizmo_test.nk"],
)
@patch.object(Path, "exists", MagicMock(return_value=True))
@patch("subprocess.call")
def test_subprocess_command(process_mock: MagicMock, tests_path: str) -> None:
    """Test the testrunner configuration"""
    runner = Runner(nuke_executable="nuke")

    with patch(
        "nuketesting._cli.runner.Runner._get_packages_directory",
        return_value="test_packages",
    ):
        runner.execute_tests(tests_path)

    process_mock.assert_called_with(
        [
            "nuke",
            "-t",
            str(RUN_TESTS_SCRIPT),
            "--packages_directory",
            "test_packages",
            "--test_dir",
            str(tests_path),
        ]
    )


@pytest.mark.parametrize("args", [["-nc"], ["-x"], ["-nc", "-x"]])
@patch.object(Runner, "_check_nuke_executable", MagicMock())
@patch("subprocess.check_call")
def test_additional_executable_arguments(process_mock: MagicMock, args) -> None:
    """Test that arguments can be provided for the executable."""
    runner = Runner(nuke_executable="nuke", executable_args=args)

    with patch(
        "nuketesting._cli.runner.Runner._get_packages_directory",
        return_value="test_packages",
    ):
        runner.execute_tests("")

    process_mock.assert_called_with(
        [
            "nuke",
            *args,
            "-t",
            str(RUN_TESTS_SCRIPT),
            "--packages_directory",
            "test_packages",
            "--test_dir",
            "",
        ]
    )


@patch.object(Runner, "_check_nuke_executable", MagicMock())
@patch("subprocess.check_call")
def test_pytest_args(process_mock: MagicMock) -> None:
    """Test to forward pytest arguments."""
    runner = Runner(nuke_executable="nuke", pytest_args=("-x", "-v something"))

    with patch(
        "nuketesting._cli.runner.Runner._get_packages_directory",
        return_value="test_packages",
    ):
        runner.execute_tests("")

    process_mock.assert_called_with(
        [
            "nuke",
            "-t",
            str(RUN_TESTS_SCRIPT),
            "--packages_directory",
            "test_packages",
            "--test_dir",
            "",
            "--pytest_arg=-x",
            "--pytest_arg=-v something",
        ]
    )


@pytest.mark.parametrize("wrong_path", ["does/not/exist/nuke", "nuke", "bla"])
def test_wrong_nuke_path(wrong_path: str) -> None:
    """Test that the runner won't accept paths that don't exist."""
    with pytest.raises(
        RunnerException,
        match=re.escape(f"Provided nuke path '{Path(wrong_path)}' does not exist."),
    ):
        Runner(nuke_executable=wrong_path)


def test_get_packages_directory() -> None:
    """Test the returning of the nuketesting and pytest packages.

    This will find the pip installed packages and pass them to Nuke.
    """

    runner = Runner(nuke_executable="")

    with patch("pytest.__file__", "some/directory/pytest/__init__.py"), patch(
        "nuketesting.__file__", "some/other_directory/testrunner/__init__.py"
    ):
        result = runner._get_packages_directory()  # noqa: SLF001

    assert result == "some/directory:some/other_directory"
