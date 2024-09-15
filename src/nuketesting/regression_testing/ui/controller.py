"""Controller for the regression test user interface."""

from __future__ import annotations

import logging

import nuke
from junitparser import Error, TestCase
from nukescripts import PythonPanel, registerPanel

from nuketesting.regression_testing.datamodel import RegressionTestCase, load_from_folder
from nuketesting.regression_testing.processor import get_test_results, run_regression_tests
from nuketesting.regression_testing.ui.ui import RegressionTestPanel, TestEntry, TestStatus


class Controller:
    """Controller for the regression panel."""

    def __init__(self) -> None:
        """Initialize the controller."""
        self.__panel = RegressionTestPanel()
        self.__panel.FOLDER_CHANGED.connect(self.__load_tests)
        self.__panel.RUN_ALL_PRESSED.connect(self.__run_all_tests)
        self.__test_cases: dict[RegressionTestCase, TestStatus] = {}

    def __load_tests(self) -> None:
        """Load the tests from the user selected folder."""
        try:
            self.__test_cases.clear()
            for case in load_from_folder(self.__panel.folder):
                self.__test_cases[case] = TestStatus.NotRun
        except FileNotFoundError as e:
            # User entered non existing path.
            logging.getLogger("NukeTesting").debug(e)
            return

        self.__set_test_cases()

    def __set_test_cases(self) -> None:
        """Update the test cases of the panel."""
        self.__panel.clear_tests()
        passed = 0
        failed = 0
        for case, status in self.__test_cases.items():
            entry = TestEntry(test_name=case.title, test_status=status)
            if status == TestStatus.PASSED:
                passed += 1
            elif status == TestStatus.FAILED:
                failed += 1
            self.__panel.add_test(entry)

        self.__panel.passing = passed
        self.__panel.failing = failed

    def __run_all_tests(self) -> None:
        """Run all tests."""
        result = run_regression_tests(self.__test_cases.keys())
        if not result:
            return
        results = get_test_results(self.__test_cases.keys(), result)
        for test, result in results.items():
            self.__test_cases[test] = self.__convert_test_result_to_status(result)
        self.__set_test_cases()

    @staticmethod
    def __convert_test_result_to_status(result: TestCase) -> TestStatus:
        """Convert the test run from pytest to a test status."""
        if not result:
            return TestStatus.NotRun
        if result.is_passed:
            return TestStatus.PASSED
        if result.is_skipped:
            return TestStatus.SKIPPED
        if Error in result.result:
            return TestStatus.ERROR
        return TestStatus.FAILED

    def makeUI(self) -> RegressionTestPanel:  # noqa: N802 Name is dictated by foundry
        """Instantiate the panel.

        Called by the nuke panel creation process. Name needs to be ``makeUI``.
        """
        return self.__panel


def register_in_nuke() -> None:
    """Register the user interface inside nuke."""
    name = "Regression Test Panel"
    panel_id = "nuketesting.ui.regression"

    class NukePanel(PythonPanel):
        """Implementation of the nuke python panel for the regression panel."""

        def __init__(self):
            super().__init__(name, panel_id)
            main_package, *sub_packages = Controller.__module__.split(".")
            knob = nuke.PyCustom_Knob(
                name, "", f"__import__(\"{main_package}\").{'.'.join(sub_packages)}.{Controller.__name__}()"
            )
            self.addKnob(knob)

    def create_and_add_panel() -> NukePanel:
        """Instantiate the panel."""
        return NukePanel().addToPane()

    menu = nuke.menu("Pane")
    menu.addCommand(name, create_and_add_panel)
    registerPanel(panel_id, create_and_add_panel)
