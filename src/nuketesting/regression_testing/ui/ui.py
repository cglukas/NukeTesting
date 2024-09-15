"""The classes for the panel to view test results and organize them."""

import sys
from enum import Enum

from PySide2 import QtCore, QtWidgets


class TestStatus(str, Enum):
    """The status that a test can have after execution."""

    PASSED = "passed"
    SKIPPED = "skipped"
    NotRun = "not run"
    FAILED = "failed"
    ERROR = "error"

    def get_color(self) -> str:
        """Get the color for the status."""
        mapping = {
            self.PASSED: "green",
            self.FAILED: "red",
            self.ERROR: "purple",
            self.SKIPPED: "gray",
            self.NotRun: "gray",
        }
        return mapping[self]


class SmallButton(QtWidgets.QPushButton):
    """A custom button that is the same as ``QPushButton`` but with a predefined with of ``30``."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the PushButton and set the with to ``30``."""
        super().__init__(*args, **kwargs)
        self.setFixedWidth(30)


class TestEntry(QtWidgets.QWidget):
    """A UI for a single test entry.

    Displaying name and status and providing buttons for further actions.
    """

    def __init__(
        self, test_name: str = "", test_status: TestStatus = TestStatus.NotRun, parent: QtWidgets.QWidget = None
    ) -> None:
        """Initialize a test entry widget.

        Args:
            test_name: Name of the test case.
            test_status: Status of the test run. See ``TestStatus``.
            parent: parent widget.

        """
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.__test_name = QtWidgets.QLabel()
        self.test_name = test_name
        layout.addWidget(self.__test_name)

        self.__test_status = QtWidgets.QLabel()
        self.test_status = test_status
        layout.addWidget(self.__test_status)

        self.run_test = QtWidgets.QPushButton(text="Run")
        layout.addWidget(self.run_test)

        # Horizontal spacer
        layout.addWidget(QtWidgets.QLabel("|"))

        self.get_info = SmallButton(text="Info")
        layout.addWidget(self.get_info)
        self.edit_test = SmallButton(text="Edit")
        layout.addWidget(self.edit_test)
        self.remove_test = SmallButton(text="X")
        layout.addWidget(self.remove_test)

    @property
    def test_name(self) -> str:
        """Get the test name."""
        return self.__test_name.text()

    @test_name.setter
    def test_name(self, new_name: str) -> None:
        """Set the test name."""
        self.__test_name.setText(new_name)

    @property
    def test_status(self) -> TestStatus:
        """Get the test status."""
        return TestStatus(self.__test_status.text())

    @test_status.setter
    def test_status(self, new_status: TestStatus) -> None:
        """Set the test status."""
        new_status = TestStatus(new_status)
        self.__test_status.setText(new_status)
        self.__test_status.setStyleSheet(f"font-weight: bold; color:{new_status.get_color()}")


class RegressionTestPanel(QtWidgets.QWidget):
    """Main panel for regression test overview."""

    FOLDER_CHANGED = QtCore.Signal()
    """Signal when the folder is changed."""
    RUN_ALL_PRESSED = QtCore.Signal()
    """Signal when the run all button is pressed."""

    def __init__(self, parent=None) -> None:
        """Initialize the testing panel."""
        super().__init__(parent)
        header = QtWidgets.QVBoxLayout()
        top_row = QtWidgets.QHBoxLayout()
        self.__folder = QtWidgets.QLineEdit()
        self.__folder.textEdited.connect(self.FOLDER_CHANGED)
        top_row.addWidget(self.__folder)

        select_folder = QtWidgets.QPushButton("Select Folder")
        select_folder.clicked.connect(self.__select_folder)
        top_row.addWidget(select_folder)
        header.addLayout(top_row)

        bottom_row = QtWidgets.QHBoxLayout()
        self.run_all = QtWidgets.QPushButton("Run All")
        self.run_all.clicked.connect(self.RUN_ALL_PRESSED.emit)
        bottom_row.addWidget(self.run_all)

        bottom_row.addWidget(QtWidgets.QLabel("Passing:"))
        self.__passing = QtWidgets.QLabel("0")
        bottom_row.addWidget(self.__passing)

        bottom_row.addWidget(QtWidgets.QLabel("Failing:"))
        self.__failing = QtWidgets.QLabel("0")
        bottom_row.addWidget(self.__failing)
        header.addLayout(bottom_row)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addLayout(header)

        self.__test_entries = QtWidgets.QVBoxLayout()
        self.__test_entry_widgets = []
        """Container to group the test entries."""
        self.layout().addLayout(self.__test_entries)

    def clear_tests(self) -> None:
        """Remove all test entries from the panel."""
        for widget in self.__test_entry_widgets:
            widget: QtWidgets.QWidget
            self.__test_entries.removeWidget(widget)
            widget.setParent(None)

    @property
    def folder(self) -> str:
        """The folder for the regression tests."""
        return self.__folder.text()

    @folder.setter
    def folder(self, folder: str) -> None:
        self.__folder.setText(folder)

    @property
    def failing(self) -> int:
        """Get the count of failing tests."""
        return int(self.__failing.text())

    @failing.setter
    def failing(self, number: int) -> None:
        self.__failing.setText(str(number))

    @property
    def passing(self) -> int:
        """Get the count of passing tests."""
        return int(self.__passing.text())

    @passing.setter
    def passing(self, number: int) -> None:
        self.__passing.setText(str(number))

    def add_test(self, test: TestEntry) -> None:
        """Add a test to the list of tests.

        Args:
            test: test widget.

        """
        self.__test_entry_widgets.append(test)
        self.__test_entries.addWidget(test)

    def __select_folder(self) -> None:
        """Show a dialog to select a folder."""
        self.folder = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self, caption="Select folder of regression tests."
        )
        self.FOLDER_CHANGED.emit()


def __run():
    app = QtWidgets.QApplication()

    window = RegressionTestPanel()
    for status in TestStatus:
        widget = TestEntry()
        widget.test_name = "Test Name"
        widget.test_status = status

        window.add_test(widget)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Used for developing only.
    # TODO(lukas): Remove before release. (I will totally forget this one XD)
    __run()
