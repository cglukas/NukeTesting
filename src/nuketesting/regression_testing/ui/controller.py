"""Controller for the regression test user interface."""

from __future__ import annotations

import logging

import nuke
from junitparser import Error
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
        self.__test_cases = []

    def __load_tests(self) -> None:
        """Load the tests from the user selected folder."""
        try:
            self.__test_cases = load_from_folder(self.__panel.folder)
        except FileNotFoundError as e:
            # User entered non existing path.
            logging.getLogger("NukeTesting").debug(e)
            return

        self.__set_test_cases(self.__test_cases)

    def __set_test_cases(self, test_cases: list[RegressionTestCase], results: list | None = None):
        self.__panel.clear_tests()
        results = results or [None] * len(test_cases)

        for case, result in zip(test_cases, results):
            entry = TestEntry()
            entry.test_name = case.title
            if not result:
                entry.test_status = TestStatus.NotRun
            elif result.is_passed:
                entry.test_status = TestStatus.PASSED
            elif result.is_skipped:
                entry.test_status = TestStatus.SKIPPED
            elif Error in result.result:
                entry.test_status = TestStatus.ERROR
            else:
                entry.test_status = TestStatus.FAILED
            self.__panel.add_test(entry)

    def __run_all_tests(self) -> None:
        """Run all tests."""
        result = run_regression_tests(self.__test_cases)
        if not result:
            return
        results = get_test_results(self.__test_cases, result)
        self.__set_test_cases(self.__test_cases, results)

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
