from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

import pytest

import nuke_test_runner
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
        nuke_executable: Path | str,
        executable_args: list[str] | None = None,
        pytest_args: tuple[str] | None = None,
        interactive: bool = True,
    ):
        """Initialize the testrunner with the test config.

        Args:
            nuke_executable: path to the nuke executable.
            executable_args: optional list of arguments forwarded to the nuke executable.
        """
        self._nuke_executable: Path = Path(nuke_executable)
        self._check_nuke_executable(self._nuke_executable)

        self._executable_args = executable_args if isinstance(executable_args, list) else []
        self._pytest_args: tuple[str] = pytest_args
        self._interactive: bool = interactive

    def _check_nuke_executable(self, executable: Path) -> None:
        """Check that the nuke path is a valid path on the current system.

        Args:
            nuke_path: path to the nuke installation directory.

        Raises:
            RunnerException if path is not executable.
        """
        if not executable.exists():
            msg = f"Provided nuke path '{executable}' does not exist."
            raise RunnerException(msg)

    def _find_nuke_python_package(self) -> Path | None:
        """Find the Nuke Python package based on the executable directory.

        Raises:
            RunnerException: when run on MacOS

        Returns:
            path to site packages of Nuke.
        """
        if platform.system().lower() == "darwin":
            msg = "On MacOS the tests can only run in interactive mode."
            raise RunnerException(msg)
        return self._nuke_executable.parent / "lib" / "site-packages"

    def execute_tests(self, test_path: str | Path) -> int:
        """Run the testrunner with provided arguments.

        Args:
            test_path: filepath to the tests. Can be relative to the current working directory.
                       Individual tests can be executed with the file.py::TestClass::test_function
                       syntax. For more details consult the pytest documentation.
        """
        return self._execute_interactive(test_path) if self._interactive else self._execute_native(test_path)

    def _get_packages_directory(self) -> Path:
        """Get the PATH to the packages locations necessary for running tests."""
        packages_directory = Path(pytest.__file__).parent.parent
        testrunner_directory = Path(nuke_test_runner.__file__).parent.parent
        return f"{packages_directory!s}:{testrunner_directory!s}"

    def _execute_interactive(self, test_path: str | Path) -> int:
        """Execute the tests using the Nuke interpreter.

        Args:
            test_path: path to tests

        Returns:
            int: exitcode of tests
        """
        packages_directory = self._get_packages_directory()
        try:
            arguments = [
                str(self._nuke_executable),
                *self._executable_args,
                "-t",
                f"'{self.TEST_SCRIPT!s}'",
                f"--packages_directory '{packages_directory!s}'",
                f"--test_dir '{test_path!s}'",
            ]
            if self._pytest_args:
                pytest_args = [f'--pytest_arg "{arg}"' for arg in self._pytest_args]
                arguments.extend(pytest_args)

            subprocess.check_call(arguments)
        except subprocess.CalledProcessError as err:
            return err.returncode
        return 0

    def _execute_native(self, test_path: str | Path) -> int:
        """Execute tests within the current interpreter

        Args:
            test_path: _description_

        Raises:
            RunnerException: _description_

        Returns:
            int: _description_
        """
        sys.path.insert(str(self._find_nuke_python_package()))
        try:
            import nuke  # noqa: F401
        except ImportError as error:
            msg = "Could not import Nuke from specified Nuke installation."
            raise RunnerException(msg) from error

        arguments = [test_path]

        if self._pytest_args:
            pytest_args = [f'--pytest_arg "{arg}"' for arg in self._pytest_args]
            arguments.extend(pytest_args)

        return nuke_test_runner.main([arguments])

    @staticmethod
    def _is_windows() -> bool:
        """Check if the operating system is windows."""
        return platform.system() == "Windows"
