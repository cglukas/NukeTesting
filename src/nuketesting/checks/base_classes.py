"""Module for base classes of the checks package."""

from __future__ import annotations

import abc


class Check(abc.ABC):
    """Base class for any check operation.

    This class is the base for any check inside the `nuketesting` package.
    It groups the checking and reporting in one place which reduced duplicated checks and forwarding of arguments.

    Each inherited check shall be by initializing the check class. The result then needs to be passed to the
    `__init__` of this class. This allows the boolean evaluation so that the check can be used inside test, assertions,
    other checks or event production code.

    Besides the constraint on the __init__ a check also needs to implement the `report` method. This is used for
    the class representation and for generating assertion errors if the `as_assertion` method is invoked.
    """

    @abc.abstractmethod
    def __init__(self, result: bool) -> None:
        """Set the result of the check."""
        self.__result = result

    @abc.abstractmethod
    def report(self) -> str:
        """Get extra information about the performed check and the result."""

    def __bool__(self) -> bool:
        """Get the truth-state of the check."""
        return self.__result

    def __eq__(self, other: bool | Check) -> bool:
        """Compare the check result to another result or boolean."""
        return self.__result == bool(other)

    def __repr__(self) -> str:
        """Get the check report to represent the performed check."""
        return self.report()

    def as_assertion(self) -> None:
        """Raise an `AssertionError` if the check result is `False`

        Raises:
            AssertionError
        """
        if self.__result:
            return
        raise AssertionError(self.report())
