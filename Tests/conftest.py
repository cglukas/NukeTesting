try:
    import nuke
except ModuleNotFoundError:
    nuke = None
import pytest


@pytest.fixture(autouse=True)
def _clean_nuke() -> None:
    """Clean nuke project after each test."""
    yield
    if nuke:
        nuke.scriptClear()
