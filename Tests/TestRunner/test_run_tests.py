from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from Testrunner.run_tests import NukeRunner


@pytest.mark.parametrize("tests_path", ["/test", ".", "C:\\windows\\path"])
@patch.object(Path, "exists", MagicMock(return_value=True))
@patch("subprocess.check_call")
def test_subprocess_command(process_mock: MagicMock, tests_path: str) -> None:
    """Test the testrunner configuration"""
    runner = NukeRunner(nuke_executable="nuke", test_files=tests_path)

    runner.execute_tests()

    process_mock.assert_called_with(["nuke", "-t", runner.TEST_SCRIPT, tests_path])


@pytest.mark.parametrize("wrong_path", ["does/not/exist/nuke", "nuke", "bla"])
def test_wrong_nuke_path(wrong_path: str) -> None:
    """Test that the runner won't accept paths that don't exist."""
    with pytest.raises(AssertionError, match="Provided nuke path does not exist."):
        NukeRunner(nuke_executable=wrong_path, test_files="")


@patch.object(Path, "exists", MagicMock(return_value=True))
@pytest.mark.parametrize("wrong_path", ["bla", "nuke/executable", "nike"])
def test_existing_path_not_nuke(wrong_path: str) -> None:
    """Test that the nuke executable needs to end on nuke."""
    with pytest.raises(
        AssertionError, match="Provided nuke path is not pointing to a nuke executable."
    ):
        NukeRunner(wrong_path, test_files="")


@patch.object(Path, "exists", MagicMock(return_value=True))
@pytest.mark.parametrize(
    ("allowed_path"),
    [
        "/path/to/Nuke",
        "/lower/nuke",
        "windows\\nuke.exe",
        "Nuke.exe",
        "Nuke.sh",
        "nuke.bat",
        "nuke",
    ],
)
def test_allowed_nuke_path(allowed_path: str) -> None:
    """Test that normal nuke paths are allowed.

    Assuming that some studios use aliases for nuke or special
    shell scripts, we need to support these for the execution
    as well.
    """
    runner = NukeRunner(nuke_executable=allowed_path, test_files="")
    assert isinstance(runner, NukeRunner)
