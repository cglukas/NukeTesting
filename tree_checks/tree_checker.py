from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import nuke


def is_connected(from_node: nuke.Node, to_node: nuke.Node, at: None | int = None) -> bool:
    """Check if a connection between the ``from_node`` to the ``to_node`` exists.

    Args:
        from_node: Node that should be connected to an input of ``to_node``.
        to_node: The node where the ``from_node`` is connected to.
        at: Specific index to check.

    Returns:
        ``True`` if the two nodes are connected, else ``False``.
    """
    if at is None:
        return any(from_node is to_node.input(i) for i in range(to_node.inputs()))
    if at < 0 or at > to_node.maximumInputs():
        msg = f"The specified input index '{at}' is not available for this node: '{to_node.name()}'"
        raise IndexError(msg)
    return to_node.input(at) is from_node
