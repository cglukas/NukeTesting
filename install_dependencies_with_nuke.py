"""Installation file for and installing the project dependencies for the nuke interpreter.

Run this script with nuke to install the project dependencies for your nuke interpreter.
You can execute this script with nuke by running:
path/to/nuke[.exe] -t install_dependencies_with_nuke.py

Make sure you have a working internet connection.
"""

import os
import subprocess
import sys
from pathlib import Path

from nuke_test_runner.datamodel.constants import NUKE_DEPENDENCY_FOLDER, REQUIREMENT_TXT


def install_dependencies() -> None:
    """Install the dependencies into the testrunner dependencies folder."""
    # We can't use "sys.executable" as it does not point to the python interpreter on windows.
    nuke_folder = Path(sys.exec_prefix)
    python_interpreter = "python.exe" if os.name == "nt" else "python"
    python = nuke_folder / python_interpreter

    print("Install with pip...")  # noqa: T201
    subprocess.check_call(
        [
            python,
            "-m",
            "pip",
            "install",
            "--target",
            str(NUKE_DEPENDENCY_FOLDER),
            "-r",
            str(REQUIREMENT_TXT),
        ]
    )


if __name__ == "__main__":
    install_dependencies()
