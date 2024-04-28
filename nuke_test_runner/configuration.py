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
