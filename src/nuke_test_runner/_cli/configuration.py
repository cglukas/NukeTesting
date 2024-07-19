"""Runner configuration package.

This is used to load test runners from the configuration file.
Runner configuration is expected to be in the format:
{
    runner_name: {
        "nuke_directory": path to nuke directory,
        "nuke_args": [list of arguments for nuke],
        "interactive": true to run interactive, false to run native python,
        "tests": path to test directory (can be splitted by ::),
        "pytest_args": [list of arguments to pass to pytest]
    }
}
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from nuke_test_runner._cli.runner import Runner, RunnerException

if TYPE_CHECKING:
    from pathlib import Path


def load_runners(filepath: Path) -> dict[str, Runner]:
    """Load all runners specified in the config file.

    Notes:
        If the file does not exist, an empty dictionary will be returned.

    Args:
        filepath: the config filepath.

    Returns:
        dictionary of runner name and loaded runner.
    """
    if not filepath.exists():
        return {}

    data = json.loads(filepath.read_text())

    result = {}
    for name, config in data.items():
        try:
            result[name] = Runner(config["exe"], config["args"])
        except RunnerException as err:  # noqa: PERF203
            print(f"Skipping config '{name}' because of Error: {err}")  # noqa: T201

    return result
