from __future__ import annotations
import os
import subprocess
from pathlib import Path


class NukeRunner:
    """Testrunner for nuke.

    This class will handle the passing of arguments to nuke and pytest.
    """

    TEST_SCRIPT: Path = Path(".")  # TODO decide on a test path

    def __init__(self, nuke_executable: Path | str, test_files: Path | str):
        """Initialize the testrunner with the test config.

        Args:
            nuke_executable: path to the nuke executable.
            test_files: path to the test files.
        """
        nuke_path = Path(nuke_executable)
        assert nuke_path.exists(), "Provided nuke path does not exist."
        assert (
            nuke_path.stem.lower() == "nuke"
        ), "Provided nuke path is not pointing to a nuke executable."
        if (self.is_windows() and nuke_path.suffix == ".sh") or (
            not self.is_windows() and nuke_path.suffix in [".exe", ".bat"]
        ):
            msg = "Provided path is incompatible with your os."
            raise OSError(msg)

        self._executable = nuke_path
        self._test_files = test_files

    def execute_tests(self) -> int:
        """Run the testrunner with provided arguments."""
        try:
            subprocess.check_call(["nuke", "-t", self.TEST_SCRIPT, self._test_files])
        except subprocess.CalledProcessError as err:
            return err.returncode
        return 0

    @staticmethod
    def is_windows() -> bool:
        """Check if the operating system is windows."""
        return os.name == "nt"
