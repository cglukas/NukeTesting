"""Tests for the tree checker."""

import pytest

nuke = pytest.importorskip("nuke")

from tree_checks.tree_checker import is_connected


def test_is_connected() -> None:
    """Test that connected nodes can be checked."""
    a = nuke.nodes.NoOp()
    b = nuke.nodes.NoOp(inputs=[a])
    c = nuke.nodes.NoOp()

    assert is_connected(a, b)
    assert not is_connected(
        b, a
    ), "Connection check should be directional. Reversing the arguments should invert the result."

    assert not is_connected(a, c), "Unconnected nodes should return False."
    assert not is_connected(None, c), "The unconnected case should return False."
