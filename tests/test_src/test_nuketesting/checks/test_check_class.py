"""Tests for the check class."""

from __future__ import annotations

from typing import Any

import pytest
from typing_extensions import override

from nuketesting.checks.base_classes import Check


class TestAbstractClass:
    """Test that the abstract methods need to be implemented."""

    def test_report_required(self) -> None:
        """Test that the `report` method is required."""

        class MyCheck(Check):
            def check(self):
                return True

        with pytest.raises(TypeError, match="Can't instantiate abstract class MyCheck.+report"):
            MyCheck()

    def test_check_required(self) -> None:
        """Test that the `report` method is required."""

        class MyCheck(Check):
            def report(self) -> str:
                return "test"

        with pytest.raises(TypeError, match="Can't instantiate abstract class MyCheck.+check"):
            MyCheck()


class PassTroughCheck(Check):
    """A check that will forward the input value."""

    def __init__(self, result: bool) -> None:
        self.__result = result

    @override
    def check(self) -> bool:
        return self.__result

    @override
    def report(self) -> str:
        return "A PassThroughCheck instance."


class TestBooleanConversion:
    """Test that a check can be converted to a boolean."""

    @pytest.mark.parametrize("result", [True, False])
    def test_boolean_conversion(self, result: bool) -> None:
        """Test that the check result is converted to the boolean state."""
        assert bool(PassTroughCheck(result)) == result

    @pytest.mark.parametrize("result", [True, False])
    def test_boolean_comparison(self, result: bool) -> None:
        """Test that the check result is converted to the boolean state."""
        assert PassTroughCheck(result) == result
        assert PassTroughCheck(result) != (not result)
        assert PassTroughCheck(result) == PassTroughCheck(result)
        assert PassTroughCheck(result) != (not PassTroughCheck(result))

    @pytest.mark.parametrize("unsupported", [ValueError, object(), 1, None, "False"])
    def test_comparison_with_unsupported_types(self, unsupported: Any) -> None:
        """Test that the check returns False for unsupported comparisons.

        This is a design decision based on the behavior of other python objects.
        """
        assert (PassTroughCheck(True) == unsupported) is False


class CheckWithCustomReport(Check):
    """A check that will forward the input to the report method."""

    def __init__(self, text: str, result: bool = True):
        self.result = result
        self.text = text

    @override
    def check(self) -> bool:
        return self.result

    @override
    def report(self) -> str:
        return self.text


class TestReporting:
    """Test that the check can be reported."""

    def test_representation(self) -> None:
        """Test that the representation of the instance uses the reporting."""
        instance = CheckWithCustomReport("Test message")
        assert instance.report() == "Test message"
        assert str(instance) == "Test message"
        assert repr(instance) == "Test message"

    @pytest.mark.parametrize("result", [True, False])
    def test_representation_is_result_independent(self, result: bool) -> None:
        """Test that the report and result are not dependent on each other by default."""
        instance = CheckWithCustomReport("Test message", result=result)

        assert instance.report() == "Test message"
        assert str(instance) == "Test message"
        assert repr(instance) == "Test message"


class TestAssertion:
    """Test that checks can raise AssertionErrors."""

    @pytest.mark.parametrize("error", [ValueError, RuntimeError, TypeError])
    def test_raise_assertion(self, error: type[Exception]) -> None:
        """Test that the `as_assertion` method raises an AssertionError if the check failed."""
        CheckWithCustomReport.ERROR_TYPE = error

        with pytest.raises(error):
            CheckWithCustomReport("", result=False).raise_()

    def test_no_assertion(self) -> None:
        """Test that passed check raise no AssertionError when the `as_assertion` method is called."""
        CheckWithCustomReport("", result=True).raise_()

    @pytest.mark.parametrize("report", ["test", "some other test"])
    def test_assertion_uses_report(self, report: str) -> None:
        """Test that the configured report is used in the assertion message."""
        CheckWithCustomReport.ERROR_TYPE = ValueError

        with pytest.raises(ValueError, match=report):
            CheckWithCustomReport(report, result=False).raise_()
