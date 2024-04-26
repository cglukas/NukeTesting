from __future__ import annotations
import os
import subprocess
from pathlib import Path

from datamodel.constants import RUN_TESTS_SCRIPT


class RunnerException(Exception):
    """Exception class for testrunner related exceptions."""


class Runner:
    """Testrunner for nuke.

    This class will handle the passing of arguments to nuke and pytest.
    """

    TEST_SCRIPT: Path = RUN_TESTS_SCRIPT

    def __init__(self, nuke_executable: Path | str, test_files: Path | str):
        """Initialize the testrunner with the test config.

        Args:
            nuke_executable: path to the nuke executable.
            test_files: path to the test files.
        """
        nuke_path = Path(nuke_executable)
        self._check_nuke_executable(nuke_path)

        self._executable = nuke_path
        self._test_files = test_files

    def _check_nuke_executable(self, nuke_path: Path):
        """Check that the nuke path is executable on the current system.

        Args:
            nuke_path: path to the nuke executable.

        Raises:
            RunnerException if path is not executable.
        """
        if not nuke_path.exists():
            msg = "Provided nuke path does not exist."
            raise RunnerException(msg)
        if not nuke_path.stem.lower().startswith("nuke"):
            msg = "Provided nuke path is not pointing to a nuke executable."
            raise RunnerException(msg)
        if (self.is_windows() and nuke_path.suffix == ".sh") or (
                not self.is_windows() and nuke_path.suffix in [".exe", ".bat"]
        ):
            msg = "Provided path is incompatible with your os."
            raise RunnerException(msg)

    def execute_tests(self) -> int:
        """Run the testrunner with provided arguments."""
        try:
            subprocess.check_call([str(self._executable), "-t", str(self.TEST_SCRIPT), str(self._test_files)])
        except subprocess.CalledProcessError as err:
            return err.returncode
        return 0

    @staticmethod
    def is_windows() -> bool:
        """Check if the operating system is windows."""
        return os.name == "nt"
