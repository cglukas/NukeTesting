from __future__ import annotations

import pytest

nuke = pytest.importorskip("nuke")

from unittest.mock import MagicMock

from bbox_checks.bbox_ckecker import assert_bbox_shape, assert_same_bbox


def test_assert_same_bbox() -> None:
    """Test that the same node will pass the test."""
    constant = nuke.nodes.Constant()
    assert_same_bbox(constant, constant)


@pytest.fixture()
def reference() -> nuke.Node:
    """Get a crop node with the default bounding box of x=0 y=0 r=2048 t=1556."""
    return nuke.nodes.Crop(box="0 0 2048 1556")


@pytest.mark.parametrize(
    ("bbox", "message"),
    [
        ("0 0 1900 1556", "on the right side"),
        ("100 0 2048 1556", "on the left side"),
        ("0 0 2048 1000", "at the top"),
        ("0 200 2048 1556", "at the bottom"),
    ],
)
def test_assert_same_bbox_single_missmatch(reference: nuke.Node, bbox: str, message: str) -> None:
    """Test that mismatches on a single side are reported."""
    crop = nuke.nodes.Crop(box=bbox)
    with pytest.raises(AssertionError, match=message):
        assert_same_bbox(reference, crop)


@pytest.mark.parametrize(("bbox", "message"), [("0 0 2000 1000", ["at the top", "on the right"])])
def test_assert_same_bbox_multiple_missmatch(reference: nuke.Node, bbox: str, message: list[str]) -> None:
    """Test that multiple mismatches are listed in the message."""
    crop = nuke.nodes.Crop(box=bbox)
    with pytest.raises(AssertionError) as error:
        assert_same_bbox(reference, crop)

    for msg in message:
        assert error.match(msg)


@pytest.mark.parametrize("shape", [[0, 0, 1920, 1080], nuke.Box(x=0, y=0, r=1920, t=1080), "0 0 1920 1080"])
def test_assert_bbox_shape(shape: list[int] | nuke.Box | str) -> None:
    """Test that the bbox can be compared to a manual definition."""
    reference = nuke.nodes.Crop(
        box="0 0 1920 1080",
        crop=False,  # Prevent nuke from adding an extra black pixel around the image, thereby increasing the bbox.
    )
    assert_bbox_shape(reference, shape)


class TestAssertBBoxShapeWrongInput:
    """Test concerning possible wrong inputs for the function."""

    @pytest.mark.parametrize(
        ("wrong_string", "exception"),
        [("", ValueError), ("1 1 1", ValueError), ("a 1 1 1", TypeError), ("1 1 1 1 1", ValueError)],
    )
    def test_strings(self, wrong_string: str, exception: type) -> None:
        """Test that wrong values in strings raise exceptions."""
        node = MagicMock(spec=nuke.Node)
        with pytest.raises(exception):
            assert_bbox_shape(node, wrong_string)

    @pytest.mark.parametrize(
        ("wrong_list", "exception"),
        [([], ValueError), ([1, 1, 1], ValueError), ([1, "1", 1, 1], TypeError), ([1, 1, 1, 1, 1], ValueError)],
    )
    def test_lists(self, wrong_list: list, exception: type) -> None:
        """Test that wrong values or length of lists raise exceptions."""
        node = MagicMock(spec=nuke.Node)
        with pytest.raises(exception):
            assert_bbox_shape(node, wrong_list)

    @pytest.mark.parametrize("wrong_instance", [object(), MagicMock(), (), set(), {}])
    def test_wrong_type(self, wrong_instance: object) -> None:
        """Test that unsupported types raise type errors."""
        node = MagicMock(spec=nuke.Node)
        with pytest.raises(TypeError):
            assert_bbox_shape(node, wrong_instance)
