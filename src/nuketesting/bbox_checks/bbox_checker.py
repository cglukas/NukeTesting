"""Module for comparing bbox data."""

from __future__ import annotations

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

    all_messages = __get_missmatching_information(values_a, values_b)

    if all_messages:
        msg = f"Node '{node_a.name()}' and node '{node_b.name()}' have mismatches in their bbox: {' and '.join(all_messages)}"
        raise AssertionError(msg)


def __get_missmatching_information(values_a: list[int], values_b: list[int]) -> list[str]:
    """Get a list of messages about missmatching values.

    Args:
        values_a: four values representing left, bottom, right and top of the boundingbox.
        values_b: four values representing left, bottom, right and top of the boundingbox.

    Returns:
        The corresponding messages for found missmatches.
    """
    attributes = ["on the left side", "at the bottom", "on the right side", "at the top"]
    all_messages = []
    for a, b, msg in zip(values_a, values_b, attributes):
        if a != b:
            all_messages.append(msg)
    return all_messages


def assert_bbox_shape(node: nuke.Node, shape: list[int] | nuke.Box | str) -> None:
    """Assert that the node bbox matches the provided shape.

    Args:
        node: The node to check.
        shape: A bounding box shape in the order [left, bottom, right, top]
            Strings are supported but need to follow the same ordering. Each value separated by a whitespace.
    """
    bbox_a = node.bbox()
    values_a = [bbox_a.x(), bbox_a.y(), bbox_a.x() + bbox_a.w(), bbox_a.y() + bbox_a.h()]
    values_b = []

    required_value_count = 4
    if isinstance(shape, list):
        if len(shape) != required_value_count:
            msg = f"Expected four values for bounding box check, you provided {len(shape)}."
            raise ValueError(msg)

        if not all(isinstance(entry, int) for entry in shape):
            msg = f"Only list of ints supported, you provided: '{shape}'"
            raise TypeError(msg)
        values_b = shape

    elif isinstance(shape, nuke.Box):
        values_b = [shape.x(), shape.y(), shape.r(), shape.t()]

    elif isinstance(shape, str):
        split = shape.split(" ")
        if len(split) != required_value_count:
            msg = f"Expected four values for bounding box check, you provided {len(split)}."
            raise ValueError(msg)
        try:
            values_b = [int(elem) for elem in split]
        except ValueError as e:
            msg = f"Expected string containing only numeric values. You provided '{shape}'"
            raise TypeError(msg) from e
    else:
        msg = f"The type '{type(shape)}' is not supported."
        raise TypeError(msg)

    all_messages = __get_missmatching_information(values_a, values_b)

    if all_messages:
        msg = (
            f"Node '{node.name()}' does not match the required bounding box: '{shape}':\n"
            f"BBox '{values_a}' != '{values_b}'.\n"
            f"The missmatches are: {' and '.join(all_messages)}"
        )
        raise AssertionError(msg)
