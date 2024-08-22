"""Tests for the metadata checker."""

import pytest

nuke = pytest.importorskip("nuke")

from nuketesting.metadata_checks.metadata_checker import assert_has_metadata


@pytest.fixture()
def metadata_node(request) -> nuke.Node:
    """Get a modify metadata node.

    Can be used in combination with an parametrize decorator:
    >>> @pytest.mark.parametrize("metadata_node", [{"a": 1}], indirect="metadata_node")
    This will set the dictionary as metadata.

    Nested dictionaries are not supported! They will be converted to strings.
    """
    param = request.param
    if param and isinstance(param, dict):
        metadata = " ".join((f'{{set "{key}" "{value}"}}' for key, value in param.items()))
        return nuke.nodes.ModifyMetaData(metadata=metadata)
    return nuke.nodes.ModifyMetaData()


@pytest.mark.parametrize("metadata_node", [{"a b": 1, "c": "text with space"}], indirect=("metadata_node",))
def test_metadata_fixture(metadata_node: nuke.Node):
    """Test that the metadata fixture sets the medatata."""
    assert metadata_node.metadata() == {"a b": "1", "c": "text with space"}


@pytest.mark.parametrize("metadata_node", [{"a b": 1, "c": "text with space"}], indirect=("metadata_node",))
def test_assert_has_metadata(metadata_node: nuke.Node):
    """Test that partial checks on metadata are possible."""
    assert_has_metadata(metadata_node, {"a b": "1"})
    with pytest.raises(AssertionError):
        assert_has_metadata(metadata_node, {"a b": "2"})
