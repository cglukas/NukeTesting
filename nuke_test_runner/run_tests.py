"""Wrapper for running tests from the commandline."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import NoReturn

from nuke_test_runner.runner import Runner


def run_tests(executable: str | Path, tests: list[str | Path]) -> NoReturn:
    """Run the tests.

    Args:
        executable:
        tests:
    """
    runner = Runner(executable, tests)
    sys.exit(runner.execute_tests())
