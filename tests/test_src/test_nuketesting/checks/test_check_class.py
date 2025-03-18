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

        with pytest.raises(TypeError, match="Can't instantiate abstract class MyCheck with abstract method[s]* report"):
            MyCheck()

    def test_init_required(self) -> None:
        """Test that the `report` method is required."""

        class MyCheck(Check):
            def report(self) -> str:
                return "test"

        with pytest.raises(
            TypeError, match="Can't instantiate abstract class MyCheck with abstract method[s]* __init__"
        ):
            MyCheck(True)


class PassTroughCheck(Check):
    """A check that will forward the input value."""

    def __init__(self, result: bool) -> None:
        super().__init__(result)

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


class CheckWithCustomReport(Check):
    """A check that will forward the input to the report method."""

    def __init__(self, text: str, result: bool = True):
        super().__init__(result)
        self.text = text

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

    def test_raise_assertion(self) -> None:
        """Test that the `as_assertion` method raises an AssertionError if the check failed."""

        with pytest.raises(AssertionError):
            CheckWithCustomReport("", result=False).as_assertion()

    def test_no_assertion(self) -> None:
        """Test that passed check raise no AssertionError when the `as_assertion` method is called."""
        CheckWithCustomReport("", result=True).as_assertion()

    @pytest.mark.parametrize("report", ["test", "some other test"])
    def test_assertion_uses_report(self, report: str) -> None:
        """Test that the configured report is used in the assertion message."""
        with pytest.raises(AssertionError, match=report):
            CheckWithCustomReport(report, result=False).as_assertion()
