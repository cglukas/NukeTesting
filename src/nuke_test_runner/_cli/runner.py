from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from nuke_test_runner import main
from nuke_test_runner.datamodel.constants import RUN_TESTS_SCRIPT


class RunnerException(Exception):  # noqa: N818
    """Exception class for testrunner related exceptions."""


class Runner:
    """Testrunner for nuke.

    This class will handle the passing of arguments to nuke and pytest.
    """

    TEST_SCRIPT: Path = RUN_TESTS_SCRIPT

    def __init__(
        self,
        nuke_directory: Path | str,
        executable_args: list[str] | None = None,
        pytest_args: tuple[str] | None = None,
        interactive: bool = True,
    ):
        """Initialize the testrunner with the test config.

        Args:
            nuke_executable: path to the nuke executable.
            executable_args: optional list of arguments forwarded to the nuke executable.
        """
        nuke_path = Path(nuke_directory)
        self._check_nuke_directory(nuke_path)

        self._nuke_directory = nuke_path
        self._executable_args = executable_args if isinstance(executable_args, list) else []
        self._pytest_args = pytest_args
        self._interactive = interactive

    def _check_nuke_directory(self, directory: Path) -> None:
        """Check that the nuke path is executable on the current system.

        Args:
            nuke_path: path to the nuke executable.

        Raises:
            RunnerException if path is not executable.
        """
        if not directory.exists():
            msg = f"Provided nuke path '{directory}' does not exist."
            raise RunnerException(msg)

    def _find_nuke_executable(self) -> Path | None:
        return ""

    def execute_tests(self, test_path: str | Path) -> int:
        """Run the testrunner with provided arguments.

        Args:
            test_path: filepath to the tests. Can be relative to the current working directory.
                       Individual tests can be executed with the file.py::TestClass::test_function
                       syntax. For more details consult the pytest documentation.
        """
        return self._execute_interactive(test_path) if self._interactive else self._execute_native(test_path)

    def _execute_interactive(self, test_path: str | Path) -> int:
        executable = self._find_nuke_executable()
        packages_directory = Path(pytest.__file__).parent
        try:
            subprocess.check_call(
                [
                    str(executable),
                    *self._executable_args,
                    "-t",
                    f"--packages_directory {packages_directory!s}",
                    f"--test_dir {test_path!s}",
                    f"--pytest_args {self._pytest_args}",
                ]
            )
        except subprocess.CalledProcessError as err:
            return err.returncode
        return 0

    def _execute_native(self, test_path: str | Path) -> int:
        sys.path.insert(self._nuke_directory)
        try:
            import nuke  # noqa: F401
        except ImportError as error:
            msg = "Could not import Nuke from specified Nuke installation."
            raise RunnerException(msg) from error

        arguments = [test_path]
        arguments.extend(self._pytest_args)

        return main([arguments])

    @staticmethod
    def _is_windows() -> bool:
        """Check if the operating system is windows."""
        return os.name == "nt"
