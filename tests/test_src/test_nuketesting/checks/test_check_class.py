"""Tests for the check class."""

import pytest

from nuketesting.checks.base_classes import Check


class TestAbstractClass:
    """Test that the abstract methods need to be implemented."""

    def test_report_required(self) -> None:
        """Test that the `report` method is required."""

        class MyCheck(Check):
            def __init__(self):
                super().__init__(True)

        with pytest.raises(TypeError, match="Can't instantiate abstract class MyCheck with abstract method report"):
            MyCheck()

    def test_init_required(self) -> None:
        """Test that the `report` method is required."""

        class MyCheck(Check):
            def report(self) -> str:
                return "test"

        with pytest.raises(TypeError, match="Can't instantiate abstract class MyCheck with abstract method __init__"):
            MyCheck(True)
