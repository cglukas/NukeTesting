"""The classes for the panel to view test results and organize them."""

import sys
from enum import Enum

from PySide2 import QtWidgets


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

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        """Initialize a test entry widget.

        Args:
        ----
            parent: parent widget.

        """
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.__test_name = QtWidgets.QLabel()
        layout.addWidget(self.__test_name)
        self.__test_status = QtWidgets.QLabel()
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

    def __init__(self, parent=None) -> None:
        """Initialize the testing panel."""
        super().__init__(parent)
        header = QtWidgets.QHBoxLayout()
        self.run_all = QtWidgets.QPushButton("Run All")
        header.addWidget(self.run_all)

        header.addWidget(QtWidgets.QLabel("Passing:"))
        self.__passing = QtWidgets.QLabel("0")
        header.addWidget(self.__passing)

        header.addWidget(QtWidgets.QLabel("Failing:"))
        self.__failing = QtWidgets.QLabel("0")
        header.addWidget(self.__failing)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addLayout(header)

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
        self.layout().addWidget(test)


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
