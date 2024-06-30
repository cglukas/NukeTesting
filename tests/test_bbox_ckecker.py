import pytest

nuke = pytest.importorskip("nuke")

from bbox_checks.bbox_ckecker import assert_same_bbox


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
