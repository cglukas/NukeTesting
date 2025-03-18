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
