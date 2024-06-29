"""Tests for the sample comparator."""

import pytest

from image_checks.sample_comparator import SampleComparator

nuke = pytest.importorskip("nuke")


@pytest.fixture()
def comparator() -> SampleComparator:
    """Create a default comparator instance."""
    return SampleComparator()


@pytest.fixture()
def white() -> nuke.Node:
    """Create a white constant."""
    return nuke.nodes.Constant(color=1)


@pytest.fixture()
def black() -> nuke.Node:
    """Create a black constant."""
    return nuke.nodes.Constant(color=0)


@pytest.fixture()
def noise() -> nuke.Node:
    return nuke.nodes.Noise()


@pytest.fixture()
def uv() -> nuke.Node:
    """Create a uv grid."""
    red = nuke.nodes.Ramp(output="red")
    red["p0"].setValue([0, 0])
    red["p1"].setValue([0, red.format().t()])
    green = nuke.nodes.Ramp(output="green", inputs=[red])
    green["p0"].setValue([0, 0])
    green["p1"].setValue([green.format().r(), 0])
    return green


def test_sample_comparator_equal(noise: nuke.Node, comparator: SampleComparator) -> None:
    """Test that the comparator identifies equal inputs as equal."""
    comparator.assert_equal(noise, noise)


def test_sample_comparator_equal_big_mismatch(
    white: nuke.Node,
    black: nuke.Node,
    comparator: SampleComparator,
) -> None:
    """Test that strong mismatches raise assertion errors."""
    with pytest.raises(AssertionError):
        comparator.assert_equal(white, black)


@pytest.mark.parametrize(
    ("x", "y"),
    [(0, 0), (10, 10), (127, 312), (2047, 1555)],
)
def test_sample_comparator_equal_pixel_mismatch(
    x: int,
    y: int,
    black: nuke.Node,
    comparator: SampleComparator,
) -> None:
    """Test that a single pixel mismatch can be found."""
    # This will create a bright red pixel at the coordinates:
    red_dot = nuke.nodes.Expression(expr0=f"x=={x} && y=={y}")

    with pytest.raises(AssertionError):
        comparator.assert_equal(black, red_dot)


@pytest.mark.parametrize("channel", ["red", "green", "blue", "depth", "mask"])
def test_sample_comparator_equal_pixel_channels(
    channel: str,
    black: nuke.Node,
    white: nuke.Node,
    comparator: SampleComparator,
) -> None:
    """Test that inequality can be found in all channels."""
    # Limit the output to the single channel:
    white["channels"].setValue(channel)

    with pytest.raises(AssertionError):
        comparator.assert_equal(black, white)


def test_sample_comparator_equal_different_format(
    uv: nuke.Node,
    black: nuke.Node,
    comparator: SampleComparator,
) -> None:
    """Test that different bboxes will fail the tests."""
    # The impulse filtering is necessary so that the test fails before the implementation existed.
    format1 = nuke.nodes.Reformat(
        format="HD_720",
        resize="none",
        center=False,
        filter="impulse",
        inputs=[uv],
    )
    format2 = nuke.nodes.Reformat(
        format="square_1K",
        resize="none",
        center=False,
        filter="impulse",
        inputs=[uv],
    )

    with pytest.raises(AssertionError):
        comparator.assert_equal(format1, format2)


@pytest.mark.parametrize(
    ("width", "height"),
    [(1, 100), (100, 1), (123, 456), (256, 256), (1, 1), (1001, 2001)],
)
def test_sample_comparator_equal_outer_corner_different_formats(
    width: int,
    height: int,
    black: nuke.Node,
    comparator: SampleComparator,
) -> None:
    """Test that the comparator detects wrong pixels in the top right corner."""
    reformat = nuke.nodes.Reformat(type="to box", box_fixed=True, box_width=width, box_height=height, inputs=[black])
    expr = nuke.nodes.Expression(expr0=f"x=={width - 1} && y=={height - 1}", inputs=[reformat])
    nuke.scriptSave(r"C:\Users\Lukas\AppData\Roaming\JetBrains\PyCharmCE2022.3\scratches\scratch_2.txt")
    with pytest.raises(AssertionError):
        comparator.assert_equal(reformat, expr)
