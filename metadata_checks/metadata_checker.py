"""Module for metadata checks."""

import nuke


def assert_has_metadata(node: nuke.Node, metadata: dict[str, str]) -> None:
    """Check that the node has the metadata set.

    Args:
        node: Node to check.
        metadata: key-value pairs of required metadata.
                  Only strings are supported by nukes metadata system.

    Raises:
        AssertionError: The required metadata is not set.
    """
    node_metadata = node.metadata()
    for key, value in metadata.items():
        if not isinstance(key, str):
            msg = f"Expected string key, got {type(key)}: '{key}'."
            raise TypeError(msg)
        if not isinstance(value, str):
            msg = f"Expected string value, got {type(value)}: '{value}'."
            raise TypeError(msg)

        if key not in node_metadata:
            msg = f"The metadata key '{key}' is not set in the metadata of '{node.name()}'."
            raise AssertionError(msg)
        if value != node_metadata[key]:
            msg = (
                f"The value for '{key}' differs from the required value!\n"
                f"Required: '{value}'\n"
                f"Set on node: '{node_metadata[key]}'"
            )
            raise AssertionError(msg)
