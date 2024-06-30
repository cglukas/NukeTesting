"""Module for comparing bbox data."""

import nuke


def assert_same_bbox(node_a: nuke.Node, node_b: nuke.Node) -> None:
    """Assert that both nodes have the same bounding box.

    Args:
        node_a: First node to check.
        node_b: Second node that will be checked.

    Raises:
        AssertionError: The bounding boxed do not match.
    """
    bbox_a = node_a.bbox()
    bbox_b = node_b.bbox()
    values_a = [bbox_a.x(), bbox_a.y(), bbox_a.x() + bbox_a.w(), bbox_a.y() + bbox_a.h()]
    values_b = [bbox_b.x(), bbox_b.y(), bbox_b.x() + bbox_b.w(), bbox_b.y() + bbox_b.h()]

    attributes = ["on the left side", "at the bottom", "on the right side", "at the top"]
    all_messages = []
    for a, b, msg in zip(values_a, values_b, attributes):
        if a != b:
            all_messages.append(msg)

    if all_messages:
        msg = f"Node '{node_a.name()}' and node '{node_b.name()}' have mismatches in their bbox: {'and'.join(all_messages)}"
        raise AssertionError(msg)
