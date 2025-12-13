"""Module for base classes of the checks package."""

from __future__ import annotations

import abc


class Check(abc.ABC):
    """Base class for any check operation.

    This class is the base for any check inside the `nuketesting` package.
    It groups the checking and reporting in one place which reduces duplicated checks and forwarding of arguments.

    Each `Check` instance needs to implement the `check` and `report` function.

    Usage example:
        A simple two object comparison can be implemented like this:
        >>> class SimpleCheck(Check):
        ...     ERROR_TYPE = ValueError
        ...     def __init__(self, a, b) -> None:
        ...         self.a = a
        ...         self.b = b
        ...     def check(self) -> bool:
        ...         return self.a == self.b
        ...     def report(self) -> str:
        ...         return f"Check that {self.a} == {self.b}"

        Use this check in your production code:
        >>> if SimpleCheck(1, 1):
        ...        print("SimpleCheck passed")
        SimpleCheck passed

        Note that the actuall check is done during the boolean conversion and not during initialization.
        The example above can also be done by this:
        >>> check = SimpleCheck(1, 1)
        >>> if check.check():
        ...        print("SimpleCheck passed")
        SimpleCheck passed

        If you want to use the check as a guard clause or to raise a meaningful exception, use the `raise_` method.
        >>> SimpleCheck(1, 2).raise_()
        Traceback (most recent call last):
        ...
        ValueError: Check that 1 == 2

        You can also use this check in your unittest code:
        >>> check = SimpleCheck(1, 2)
        >>> assert check.check(), check.report()
        Traceback (most recent call last):
        ...
        AssertionError: Check that 1 == 2

        >>> check = SimpleCheck(1, 2)
        >>> assert check, check.report()
        Traceback (most recent call last):
        ...
        AssertionError: Check that 1 == 2

    Warning:
        The check is always performed when the ``check`` method is called or if the object is **cast to a boolean**.

    """

    ERROR_TYPE = ValueError

    @abc.abstractmethod
    def report(self) -> str:
        """Get extra information about the performed check and the result."""

    @abc.abstractmethod
    def check(self) -> bool:
        """Perform the check and return ``True`` if the check passed."""

    def __bool__(self) -> bool:
        """Get the truth-state of the check."""
        return self.check()

    def __eq__(self, other: bool | Check) -> bool:
        """Compare the check result to another result or boolean."""
        if not isinstance(other, (bool, Check)):
            return False

        return self.check() == bool(other)

    def __repr__(self) -> str:
        """Get the check report to represent the performed check."""
        return self.report()

    def raise_(self) -> None:
        """Raise an error if the check result is `False`."""
        if self.check():
            return
        raise self.ERROR_TYPE(self.report())
