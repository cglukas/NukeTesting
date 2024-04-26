from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from nuke_test_runner.runner import Runner, RunnerException


@pytest.mark.parametrize(
    "tests_path",
    ["/test", ".", "C:\\windows\\path", "test.py", "gizmo_test.nk"],
)
@patch.object(Path, "exists", MagicMock(return_value=True))
@patch("subprocess.check_call")
def test_subprocess_command(process_mock: MagicMock, tests_path: str) -> None:
    """Test the testrunner configuration"""
    runner = Runner(nuke_executable="nuke")

    runner.execute_tests(tests_path)

    process_mock.assert_called_with(
        ["nuke", "-t", str(runner.TEST_SCRIPT), str(tests_path)]
    )


@pytest.mark.parametrize("args", [["-nc"], ["-x"], ["-nc", "-x"]])
@patch.object(Runner, "_check_nuke_executable", MagicMock())
@patch("subprocess.check_call")
def test_additional_executable_arguments(
    process_mock: MagicMock, args
) -> None:
    """Test that arguments can be provided for the executable."""
    runner = Runner(
        nuke_executable="nuke",executable_args=args
    )

    runner.execute_tests("")

    process_mock.assert_called_with(
        ["nuke", *args, "-t", str(runner.TEST_SCRIPT), ""]
    )


@pytest.mark.parametrize("wrong_path", ["does/not/exist/nuke", "nuke", "bla"])
def test_wrong_nuke_path(wrong_path: str) -> None:
    """Test that the runner won't accept paths that don't exist."""
    with pytest.raises(
        RunnerException, match="Provided nuke path does not exist."
    ):
        Runner(nuke_executable=wrong_path)


@patch.object(Path, "exists", MagicMock(return_value=True))
@pytest.mark.parametrize("wrong_path", ["bla", "nuke/executable", "nike"])
def test_existing_path_not_nuke(wrong_path: str) -> None:
    """Test that the nuke executable needs to end on nuke."""
    with pytest.raises(
        RunnerException,
        match="Provided nuke path is not pointing to a nuke executable.",
    ):
        Runner(wrong_path)


@patch.object(Path, "exists", MagicMock(return_value=True))
@pytest.mark.parametrize(
    ("is_windows", "wrong_path"),
    [(True, "nuke.sh"), (False, "nuke.exe"), (False, "nuke.bat")],
)
@patch.object(Runner, "_is_windows")
def test_wrong_operating_system(
    is_windows_mock: PropertyMock, is_windows: bool, wrong_path: str
) -> None:
    """Test that system incompatible extensions won't be executed."""
    is_windows_mock.return_value = is_windows
    with pytest.raises(
        RunnerException, match="Provided path is incompatible with your os."
    ):
        Runner(wrong_path)


@patch.object(Path, "exists", MagicMock(return_value=True))
@pytest.mark.parametrize(
    ("is_windows", "allowed_path"),
    [
        (False, "/path/to/Nuke"),
        (True, "/path/to/Nuke"),
        (False, "/lower/nuke"),
        (True, "/lower/nuke"),
        (True, "windows\\nuke.exe"),
        (True, "Nuke.exe"),
        (True, "Nuke15.0.exe"),
        (False, "Nuke.sh"),
        (True, "nuke.bat"),
        (True, "nuke"),
        (False, "nuke"),
    ],
)
@patch.object(Runner, "_is_windows")
def test_allowed_nuke_path(
    is_windows_mock: MagicMock, is_windows: bool, allowed_path: str
) -> None:
    """Test that normal nuke paths are allowed.

    Assuming that some studios use aliases for nuke or special
    shell scripts, we need to support these for the execution
    as well.
    """
    is_windows_mock.return_value = is_windows
    runner = Runner(nuke_executable=allowed_path)
    assert isinstance(runner, Runner)
