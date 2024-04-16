from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from NukeTestRunner.run_tests import Runner


@pytest.mark.parametrize(
    "tests_path", ["/test", ".", "C:\\windows\\path", "test.py", "gizmo_test.nk"]
)
@patch.object(Path, "exists", MagicMock(return_value=True))
@patch("subprocess.check_call")
def test_subprocess_command(process_mock: MagicMock, tests_path: str) -> None:
    """Test the testrunner configuration"""
    runner = Runner(nuke_executable="nuke", test_files=tests_path)

    runner.execute_tests()

    process_mock.assert_called_with(["nuke", "-t", runner.TEST_SCRIPT, tests_path])


@pytest.mark.parametrize("wrong_path", ["does/not/exist/nuke", "nuke", "bla"])
def test_wrong_nuke_path(wrong_path: str) -> None:
    """Test that the runner won't accept paths that don't exist."""
    with pytest.raises(AssertionError, match="Provided nuke path does not exist."):
        Runner(nuke_executable=wrong_path, test_files="")


@patch.object(Path, "exists", MagicMock(return_value=True))
@pytest.mark.parametrize("wrong_path", ["bla", "nuke/executable", "nike"])
def test_existing_path_not_nuke(wrong_path: str) -> None:
    """Test that the nuke executable needs to end on nuke."""
    with pytest.raises(
        AssertionError, match="Provided nuke path is not pointing to a nuke executable."
    ):
        Runner(wrong_path, test_files="")


@patch.object(Path, "exists", MagicMock(return_value=True))
@pytest.mark.parametrize(
    ("is_windows", "wrong_path"),
    [(True, "nuke.sh"), (False, "nuke.exe"), (False, "nuke.bat")],
)
@patch.object(Runner, "is_windows")
def test_wrong_operating_system(
    is_windows_mock: PropertyMock, is_windows: bool, wrong_path: str
) -> None:
    """Test that system incompatible extensions won't be executed."""
    is_windows_mock.return_value = is_windows
    with pytest.raises(OSError, match="Provided path is incompatible with your os."):
        Runner(wrong_path, test_files="")


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
        (False, "Nuke.sh"),
        (True, "nuke.bat"),
        (True, "nuke"),
        (False, "nuke"),
    ],
)
@patch.object(Runner, "is_windows")
def test_allowed_nuke_path(
    is_windows_mock: MagicMock, is_windows: bool, allowed_path: str
) -> None:
    """Test that normal nuke paths are allowed.

    Assuming that some studios use aliases for nuke or special
    shell scripts, we need to support these for the execution
    as well.
    """
    is_windows_mock.return_value = is_windows
    runner = Runner(nuke_executable=allowed_path, test_files="")
    assert isinstance(runner, Runner)
