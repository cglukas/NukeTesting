"""Tests for nuke specific actions."""

import tempfile
from pathlib import Path

import pytest

nuke = pytest.importorskip("nuke")

from nuketesting.image_checks.sample_comparator import SampleComparator
from nuketesting.regression_testing.datamodel import RegressionTestCase
from nuketesting.regression_testing.nuke_model import load_expected, load_nodes


@pytest.fixture(scope="module")
def nuke_rtc() -> RegressionTestCase:
    """Create a valid regression test case.

    This will render one frame.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        folder = Path(tmp_dir)
        checker = nuke.nodes.CheckerBoard2(format="square_256")
        output = nuke.nodes.Output(name="RegressionCheck", inputs=[checker])
        expected_output = folder / "expected_output.exr"
        # Don't use '.nk' file ending here. It will mess with the NC version of nuke.
        nuke_script_nk = folder / "nuke_script.tmp"
        write = nuke.nodes.Write(
            inputs=[output],
            channels="all",
            file=str(expected_output.as_posix()),
            file_type="exr",
            raw=True,
        )
        nuke.render(write, 0, 0)
        nuke.scriptSave(str(nuke_script_nk))
        nuke.scriptClear()
        yield RegressionTestCase(
            title="Unit Test",
            description="Demo regression test for unit testing",
            nuke_script=nuke_script_nk,
            expected_output=expected_output,
        )


def test_load_nodes(nuke_rtc: RegressionTestCase) -> None:
    """Test that nodes can be loaded from the RTC."""
    nodes_in_fixture = 3

    load_nodes(nuke_rtc)

    assert len(nuke.allNodes()) == nodes_in_fixture


def test_load_expected(nuke_rtc: RegressionTestCase) -> None:
    """Test that the expected output can be loaded to a read node."""
    read = load_expected(nuke_rtc)

    assert read.Class() == "Read"
    assert read["file"].value() == nuke_rtc.expected_output.as_posix()


def test_full_construction(nuke_rtc: RegressionTestCase) -> None:
    """Test that the rtc will pass an equality check."""
    expected = load_expected(nuke_rtc)
    check_node = load_nodes(nuke_rtc)

    SampleComparator.assert_equal(check_node, expected, tolerance=0.0001)
