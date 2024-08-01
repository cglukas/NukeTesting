"""Script that gets executed by nuke to run tests.

This script will be run through the `Runner` class. It adds pytest to the available packages and executes
pytest with all provided arguments.
"""

import inspect
import sys
from pathlib import Path
from typing import NoReturn


def run_tests(pytest_arguments: list[str]) -> NoReturn:
    """Run pytest with the provided arguments.

    Note:
        This function will exit the calling instance.

    Args:
        pytest_arguments:
    """
    this_file = Path(inspect.getfile(run_tests))
    project_folder = this_file.parent.parent
    sys.path.insert(0, str(project_folder))
    from datamodel.constants import NUKE_DEPENDENCY_FOLDER

    sys.path.insert(0, str(NUKE_DEPENDENCY_FOLDER))
    import pytest

    sys.exit(pytest.main(pytest_arguments))


if __name__ == "__main__":
    # We need to cut of the filepath of this python file in the arguments:
    reduced_args = sys.argv[1:]
    run_tests(reduced_args)
