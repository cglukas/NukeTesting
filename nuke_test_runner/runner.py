from __future__ import annotations

import os
import subprocess
from pathlib import Path

from datamodel.constants import RUN_TESTS_SCRIPT


class RunnerException(Exception):  # noqa: N818
    """Exception class for testrunner related exceptions."""


class Runner:
    """Testrunner for nuke.

    This class will handle the passing of arguments to nuke and pytest.
    """

    TEST_SCRIPT: Path = RUN_TESTS_SCRIPT

    def __init__(
        self,
        nuke_executable: Path | str,
        executable_args: list[str] | None = None,
    ):
        """Initialize the testrunner with the test config.

        Args:
            nuke_executable: path to the nuke executable.
            executable_args: optional list of arguments forwarded to the nuke executable.
        """
        nuke_path = Path(nuke_executable)
        self._check_nuke_executable(nuke_path)

        self._executable = nuke_path
        self._ececutable_args = executable_args if isinstance(executable_args, list) else []

    def _check_nuke_executable(self, nuke_path: Path):
        """Check that the nuke path is executable on the current system.

        Args:
            nuke_path: path to the nuke executable.

        Raises:
            RunnerException if path is not executable.
        """
        if not nuke_path.exists():
            msg = f"Provided nuke path '{nuke_path}' does not exist."
            raise RunnerException(msg)
        if not nuke_path.stem.lower().startswith("nuke"):
            msg = f"Provided nuke path is not pointing to a nuke executable: '{nuke_path.stem}'"
            raise RunnerException(msg)
        if (self._is_windows() and nuke_path.suffix == ".sh") or (
            not self._is_windows() and nuke_path.suffix in [".exe", ".bat"]
        ):
            msg = "Provided path is incompatible with your os."
            raise RunnerException(msg)

    def execute_tests(self, test_path: str | Path) -> int:
        """Run the testrunner with provided arguments.

        Args:
            test_path: filepath to the tests. Can be relative to the current working directory.
                       Individual tests can be executed with the file.py::TestClass::test_function
                       syntax. For more details consult the pytest documentation.
        """
        try:
            subprocess.check_call(
                [
                    str(self._executable),
                    *self._ececutable_args,
                    "-t",
                    str(self.TEST_SCRIPT),
                    str(test_path),
                ]
            )
        except subprocess.CalledProcessError as err:
            return err.returncode
        return 0

    @staticmethod
    def _is_windows() -> bool:
        """Check if the operating system is windows."""
        return os.name == "nt"
