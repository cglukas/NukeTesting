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


def test_is_connected_at() -> None:
    """Test that connection can be checked for a specific input."""
    a = nuke.nodes.NoOp()
    b = nuke.nodes.Switch(inputs=[None, None, a])  # Has multiple inputs.

    assert is_connected(a, b)
    assert is_connected(a, b, at=2)
    assert not is_connected(a, b, at=0)
    assert not is_connected(a, b, at=1)


@pytest.mark.parametrize("index", [-1, 2, 3])
def test_is_connected_at_out_of_range(index: int) -> None:
    """Test that it raises an exception if inputs outside the available range are checked."""
    a = nuke.nodes.NoOp()
    b = nuke.nodes.NoOp()
    with pytest.raises(IndexError):
        assert not is_connected(a, b, at=index)
