"""Module for comparing bbox data."""

from __future__ import annotations

import nuke

from nuketesting.checks.base_classes import Check


class HasSameBbox(Check):
    ERROR_TYPE = AssertionError

    def __init__(self, node_a: nuke.Node, node_b: nuke.Node) -> None:
        """Check that both nodes have the same bounding box.

        Args:
            node_a: First node to check.
            node_b: Second node that will be checked.
        """
        self.node_a = node_a
        self.node_b = node_b
        self.all_mismatches = []

    def check(self) -> bool:
        bbox_a = self.node_a.bbox()
        bbox_b = self.node_b.bbox()
        values_a = [bbox_a.x(), bbox_a.y(), bbox_a.x() + bbox_a.w(), bbox_a.y() + bbox_a.h()]
        values_b = [bbox_b.x(), bbox_b.y(), bbox_b.x() + bbox_b.w(), bbox_b.y() + bbox_b.h()]
        self.all_mismatches = _get_mismatching_information(values_a, values_b)
        return len(self.all_mismatches) == 0

    def report(self) -> str:
        return (
            f"Node '{self.node_a.name()}' and node '{self.node_b.name()}' have mismatches in their bbox: "
            f"{' and '.join(self.all_mismatches)}"
        )


def _get_mismatching_information(values_a: list[int], values_b: list[int]) -> list[str]:
    """Get a list of messages about mismatching values.

    Args:
        values_a: four values representing left, bottom, right and top of the bounding-box.
        values_b: four values representing left, bottom, right and top of the bounding-box.

    Returns:
        The corresponding messages for found mismatches.
    """
    if len(values_a) != len(values_b):
        msg = f"Can't safely compare {len(values_a)} values to {len(values_b)} values."
        raise ValueError(msg)
    attributes = ["on the left side", "at the bottom", "on the right side", "at the top"]
    all_messages = []
    for a, b, msg in zip(values_a, values_b, attributes):
        if a != b:
            all_messages.append(msg)
    return all_messages


class HasBboxShape(Check):
    ERROR_TYPE = AssertionError

    def __init__(self, node: nuke.Node, shape: list[int] | nuke.Box | str) -> None:
        """Check that the node bbox matches the provided shape.

        Args:
            node: The node to check.
            shape: A bounding box shape in the order [left, bottom, right, top]
                Strings are supported but need to follow the same ordering. Each value separated by a whitespace.
        """
        self.node = node
        self.shape = shape
        self._mismatches = []
        self._values_a = []
        self._values_b = []

    def check(self) -> bool:
        bbox_a = self.node.bbox()
        self._values_a = [bbox_a.x(), bbox_a.y(), bbox_a.x() + bbox_a.w(), bbox_a.y() + bbox_a.h()]
        self._values_b = []

        required_value_count = 4
        if isinstance(self.shape, list):
            if len(self.shape) != required_value_count:
                msg = f"Expected four values for bounding box check, you provided {len(self.shape)}."
                raise ValueError(msg)

            if not all(isinstance(entry, int) for entry in self.shape):
                msg = f"Only list of ints supported, you provided: '{self.shape}'"
                raise TypeError(msg)
            self._values_b = self.shape

        elif isinstance(self.shape, nuke.Box):
            self._values_b = [self.shape.x(), self.shape.y(), self.shape.r(), self.shape.t()]

        elif isinstance(self.shape, str):
            split = self.shape.split(" ")
            if len(split) != required_value_count:
                msg = f"Expected four values for bounding box check, you provided {len(split)}."
                raise ValueError(msg)
            try:
                self._values_b = [int(elem) for elem in split]
            except ValueError as e:
                msg = f"Expected string containing only numeric values. You provided '{self.shape}'"
                raise TypeError(msg) from e
        else:
            msg = f"The type '{type(self.shape)}' is not supported."
            raise TypeError(msg)

        self._mismatches = _get_mismatching_information(self._values_a, self._values_b)
        return len(self._mismatches) == 0

    def report(self) -> str:
        return (
            f"Node '{self.node.name()}' does not match the required bounding box: '{self.shape}':\n"
            f"BBox '{self._values_a}' != '{self._values_b}'.\n"
            f"The missmatches are: {' and '.join(self._mismatches)}"
        )
