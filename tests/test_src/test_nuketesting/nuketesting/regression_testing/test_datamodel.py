"""Tests for the datamodel of the regression testing.

Abbreviations:
    RTC: RegressionTestCase
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from junitparser import Error, Failure, Skipped, TestCase

from nuketesting.regression_testing.datamodel import (
    RegressionTestCase,
    TestStatus,
    convert_test_result_to_status,
    load_from_folder,
    save_to_folder,
)

if TYPE_CHECKING:
    from junitparser.junitparser import Result


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


def test_dict_and_set_support(rtc: RegressionTestCase) -> None:
    """Test that regression test cases can be used as dict/set keys."""
    assert {rtc}
    assert {rtc: rtc}


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


@patch("logging.debug")
def test_load_from_folder_missing_file(logger: MagicMock) -> None:
    """Test that missing files are logged and ignored."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        folder = Path(tmp_dir)
        (folder / "TestName.nk").write_text("test")
        (folder / "TestName.exr").write_text("test")

        test_cases = load_from_folder(folder)

        assert len(test_cases) == 0
        logger.assert_called_with('Not all test files found for test case "%s"', "TestName")


def test_save_to_folder(rtc: RegressionTestCase) -> None:
    """Test that RegressionTestCases can be saved to a folder."""
    with tempfile.TemporaryDirectory() as tmp_folder:
        folder = Path(tmp_folder)

        expected_file = save_to_folder(rtc, folder)

        assert expected_file.read_text() == f'{{"title": "{rtc.title}", "description": "{rtc.description}"}}'


@pytest.mark.parametrize(
    ("results", "status"),
    [
        ([], TestStatus.PASSED),
        ([Skipped()], TestStatus.SKIPPED),
        ([Error()], TestStatus.ERROR),
        ([Failure()], TestStatus.FAILED),
    ],
)
def test_status_conversion(results: list[Result], status: TestStatus) -> None:
    """Test that test cases from junit can be translated in our test status class."""
    case = TestCase()
    case.result = results
    assert convert_test_result_to_status(case) == status
