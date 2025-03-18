"""Tests for the check class."""

from __future__ import annotations

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


class TestBooleanConversion:
    """Test that a check can be converted to a boolean."""

    @pytest.fixture
    def pass_check(self) -> type[Check]:
        """Get a check that will forward the input value."""

        class PassTroughCheck(Check):
            def __init__(self, result: bool) -> None:
                super().__init__(result)

            def report(self) -> str:
                return "A PassThroughCheck instance."

        return PassTroughCheck

    @pytest.mark.parametrize("result", [True, False])
    def test_boolean_conversion(self, result: bool, pass_check: type[Check]) -> None:
        """Test that the check result is converted to the boolean state."""
        assert bool(pass_check(result)) == result

    @pytest.mark.parametrize("result", [True, False])
    def test_boolean_comparison(self, result: bool, pass_check: type[Check]) -> None:
        """Test that the check result is converted to the boolean state."""
        assert pass_check(result) == result
        assert pass_check(result) != (not result)
        assert pass_check(result) == pass_check(result)
        assert pass_check(result) != (not pass_check(result))


class TestReporting:
    """Test that the check can be reported."""

    @pytest.fixture
    def report_check(self) -> type[Check]:
        """Get a check that will forward the input to the report method."""

        class ReportCheck(Check):
            def __init__(self, text: str, result: bool = True):
                super().__init__(result)
                self.text = text

            def report(self) -> str:
                return self.text

        return ReportCheck

    def test_representation(self, report_check: type[Check]) -> None:
        """Test that the representation of the instance uses the reporting."""
        instance = report_check("Test message")
        assert instance.report() == "Test message"
        assert str(instance) == "Test message"
        assert repr(instance) == "Test message"

    @pytest.mark.parametrize("result", [True, False])
    def test_representation_is_result_independant(self, result: bool, report_check: type[Check]) -> None:
        """Test that the report and result are not dependent on each other by default."""
        instance = report_check("Test message", result=result)

        assert instance.report() == "Test message"
        assert str(instance) == "Test message"
        assert repr(instance) == "Test message"
