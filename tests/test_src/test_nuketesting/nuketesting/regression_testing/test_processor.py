"""Tests for the processor of the regression testing module."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from junitparser import JUnitXml

nuke = pytest.importorskip("nuke")

from nuketesting.regression_testing.datamodel import RegressionTestCase, load_from_folder
from nuketesting.regression_testing.processor import get_test_results, run_regression_tests


@pytest.fixture(scope="session")
def rtc() -> RegressionTestCase:
    """Get the sample regression test case from the test data."""
    sample_folder = Path(__file__).parent / "test_data/sample_rtc"
    return load_from_folder(sample_folder)[0]


@pytest.mark.nuke
def test_report(rtc: RegressionTestCase) -> None:
    """Test that the run function returns a JUnit XML report file."""
    result = run_regression_tests([rtc])
    assert isinstance(result, JUnitXml)


@pytest.mark.parametrize(
    "wrong_args",
    [[], [None], 6, [RegressionTestCase("title", "description", "nuke_script", "expected_output"), "second_wrong"]],
)
@patch("subprocess.call")
def test_no_subprocess_on_empty_list(call_mock: MagicMock, wrong_args: Any) -> None:
    """Test that empty test cases will not start subprocesses."""
    with pytest.raises(ValueError, match="Expected list of test cases"):
        run_regression_tests(wrong_args)
    call_mock.assert_not_called()


@pytest.mark.nuke
def test_rtc_in_report(rtc: RegressionTestCase) -> None:
    """Test that the report contains information about the rtc."""
    report = run_regression_tests([rtc])
    test_results = get_test_results([rtc], report)

    assert test_results[rtc].is_passed
