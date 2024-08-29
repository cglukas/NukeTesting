"""Tests for the datamodel of the regression testing.

Abbreviations:
    RTC: RegressionTestCase
"""

import tempfile
from pathlib import Path

import pytest

nuke = pytest.importorskip("nuke")
from nuketesting.image_checks.sample_comparator import SampleComparator
from nuketesting.regression_testing.datamodel import (
    RegressionTestCase,
    load_expected,
    load_from_folder,
    load_nodes,
    save_to_folder,
)


@pytest.fixture
def rtc() -> RegressionTestCase:
    """Create a simple regression test case."""
    return RegressionTestCase(
        title="Test Case Title",
        description="custom description",
        nuke_script="path/snippet.nk",
        expected_output="path/expected.exr",
    )


def test_regression_test_case(rtc: RegressionTestCase) -> None:
    """Test that all attributes for a regression test case can be set."""
    assert isinstance(rtc.nuke_script, Path)
    assert isinstance(rtc.expected_output, Path)


def test_regression_test_case_serialisation(rtc: RegressionTestCase) -> None:
    """Test that test cases can be stored and later loaded from text."""
    json_data = rtc.to_json()

    deserialized = RegressionTestCase.from_json(json_data)

    assert deserialized == rtc


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


def test_load_from_folder() -> None:
    """Test that all testcase files are loaded into test cases."""
    arbitrary_number_of_cases = 4

    with tempfile.TemporaryDirectory() as tmp_dir:
        folder = Path(tmp_dir)
        for i in range(arbitrary_number_of_cases):
            (folder / f"test{i}.nk").write_text("test")
            (folder / f"test{i}.exr").write_text("test")
            (folder / f"test{i}.json").write_text('{"title":"test", "description":"test description"}')

        # Actual test call:
        test_cases = load_from_folder(folder)

        assert len(test_cases) == arbitrary_number_of_cases

        example_testcase = test_cases[0]
        assert example_testcase.title == "test"
        assert example_testcase.description == "test description"
        assert example_testcase.nuke_script.name == "test0.nk"
        assert example_testcase.expected_output.name == "test0.exr"


def test_save_to_folder(rtc: RegressionTestCase) -> None:
    """Test that RegressionTestCases can be saved to a folder."""
    with tempfile.TemporaryDirectory() as tmp_folder:
        folder = Path(tmp_folder)

        expected_file = save_to_folder(rtc, folder)

        assert expected_file.read_text() == f'{{"title": "{rtc.title}", "description": "{rtc.description}"}}'
