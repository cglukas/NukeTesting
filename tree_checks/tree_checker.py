import nuke


def is_connected(from_node: nuke.Node, to_node: nuke.Node) -> bool:
    """Check if a connection between the ``from_node`` to the ``to_node`` exists.

    Args:
        from_node: Node that should be connected to an input of ``to_node``.
        to_node: The node where the ``from_node`` is connected to.

    Returns:
        ``True`` if the two nodes are connected, else ``False``.
    """
    return any(from_node is to_node.input(i) for i in range(to_node.inputs()))
