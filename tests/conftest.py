"""Global test configuration."""

try:
    import nuke
except ModuleNotFoundError:
    nuke = None
from pathlib import Path

import pytest

from nuketesting._cli.configuration import find_configuration

nuke_test = pytest.mark.skipif(not find_configuration(Path(Path.cwd())))


@pytest.fixture(autouse=True)
def _clean_nuke() -> None:
    """Clean nuke project after each test."""
    yield
    if nuke:
        nuke.scriptClear()


def pytest_runtest_setup(item) -> None:
    """Set up pytest for each test.

    Hook for skipping/manipulating tests before execution.
    This is called by pytest for each test item.
    """
    _check_nuke_marker(item)


def _check_nuke_marker(item):
    """Mark a tests as skip if the nuke marker is set but no runner config."""
    has_nuke_marker = next(item.iter_markers("nuke"), None)
    # TODO(lukas): We are going to search the config for each test with a "nuke" marker.
    #  This could lead to some performance penalties. On the other hand allows this a per test
    #  runner. We might need this.
    if has_nuke_marker and not find_configuration(Path(item.path)):
        pytest.skip("Test requires a setup runners.json to be executed.")
