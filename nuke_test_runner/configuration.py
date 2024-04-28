"""Runner configuration package.

This is used to load test runners from the configuration file.
Runner configuration is expected to be in the format:
{
    runner_name: {
        "exe": path to nuke,
        "args": [list of arguments for nuke]
    }
}
"""
from __future__ import annotations

import json
from contextlib import suppress
from pathlib import Path

from nuke_test_runner.runner import Runner, RunnerException


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
        with suppress(RunnerException):
            result[name] = Runner(config["exe"], config["args"])

    return result


def find_configuration(start_path: Path) -> Path | None:
    """Find a configuration file that is part of the current test.

    This will return the first configuration that is found.
    It will traverse the directories up to find a "runners.json".

    Args:
        start_path: the starting directory/file where the search begins.

    Returns:
        The found "runners.json" or None.
    """
    if start_path.is_file():
        path = start_path.parent
    else:
        path = start_path

    while path.parent:
        config = path / "runners.json"
        if config.exists():
            return config
        path = path.parent
    return None
