"""Processing module for regression tests."""

from __future__ import annotations

import tempfile
from collections.abc import Iterable
from pathlib import Path

import nuke
from junitparser import JUnitXml, TestCase

from nuketesting._cli.runner import Runner
from nuketesting.image_checks.sample_comparator import SampleComparator
from nuketesting.regression_testing.datamodel import RegressionTestCase, load_expected, load_nodes

__all__ = ["run_regression_tests", "get_test_results"]

DATA_TRANSFER_FILE = Path.home() / ".rtc_data_transfer"


def pytest_generate_tests(metafunc) -> None:
    """Dynamically parametrize the test function with test cases of the test case file.

    Args:
        metafunc: pytest test function.
    """
    if "case" not in metafunc.fixturenames:
        return

    lines = DATA_TRANSFER_FILE.read_text("utf-8")
    all_test_cases = [RegressionTestCase.from_json(line) for line in lines.split("\n")]

    ids = [case.id for case in all_test_cases]
    metafunc.parametrize("case", all_test_cases, ids=ids)


def test_regression_tests(case: RegressionTestCase) -> None:
    """Test the regression test.

    This function is the main check for regression tests. It's loading the nuke script and rendering and compares them.
    Each test case is loaded by ``pytest_generate_tests`` which also parametrizes this function.

    The pixel tolerance is hardcoded to ``0.0001``. So a discrepancy lower than this is considered as equal.

    Args:
        case: A regression test case to check.
    """
    expected = load_expected(case)
    check_node = load_nodes(case)

    SampleComparator.assert_equal(check_node, expected, tolerance=0.0001)


def run_regression_tests(test_cases: list[RegressionTestCase]) -> JUnitXml | None:
    """Run the regression test cases and generate a report.

    Args:
        test_cases: All tests to execute.

    Returns:
        The report.
    """
    if not test_cases:
        msg = "Expected list of test cases, but got none."
        raise ValueError(msg)
    if not isinstance(test_cases, Iterable):
        msg = f"Expected list of test cases, but got {type(test_cases)}"
        raise ValueError(msg)
    if not all(isinstance(case, RegressionTestCase) for case in test_cases):
        msg = f"Expected list of test cases, but got {[type(case) for case in test_cases]}"
        raise ValueError(msg)

    try:
        DATA_TRANSFER_FILE.write_text("\n".join([case.to_json() for case in test_cases]), encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp_folder:
            report = Path(tmp_folder) / "regression_test_report.xml"

            # These args are important to use the same license as the main instance:
            nuke_executable, *nuke_args = nuke.rawArgs
            allowed_args = ["--nc", "--nukex", "--nukestudio"]
            filtered_nuke_args = [arg for arg in nuke_args if arg in allowed_args]

            runner = Runner(
                nuke_executable,
                filtered_nuke_args,
                pytest_args=(f"--junit-xml={report!s}",),
                run_in_terminal_mode=True,
            )
            # Using the function __name__ attribute to enable easier refactoring:
            runner.execute_tests(__file__ + f"::{test_regression_tests.__name__}")

            return JUnitXml.fromfile(report)
    finally:
        DATA_TRANSFER_FILE.unlink()


def get_test_results(test_cases: list[RegressionTestCase], report: JUnitXml) -> list[TestCase]:
    """Get the test case results from the report.

    Args:
        test_cases: All test cases to consider.
        report: Loaded JUnit report.

    Returns:
        The test case results.
    """
    pytest_suite = next(iter(report))
    test_names = [_get_test_name_in_report(case) for case in test_cases]
    return [case for case in pytest_suite if case.name in test_names]


def _get_test_name_in_report(test_case: RegressionTestCase) -> str:
    """Get the name of the test case in the report."""
    return f"{test_regression_tests.__name__}[{test_case.id}]"
