"""Module for base classes of the checks package."""

import abc


class Check(abc.ABC):
    """Base class for any check operation.

    This class is the base for any check inside the `nuketesting` package.
    It groups the checking and reporting in one place which reduced duplicated checks and forwarding of arguments.

    Each inherited check shall be by initializing the check class. The result then needs to be passed to the
    `__init__` of this class. This allows the boolean evaluation so that the check can be used inside test, assertions,
    other checks or event production code.

    Besides the constraint on the __init__ a check also needs to implement the `report` method. This is used for
    the class representation and for generating assertion errors if the `assert` method is invoked.
    """

    @abc.abstractmethod
    def __init__(self, result: bool) -> None:
        """Set the result of the check."""

    @abc.abstractmethod
    def report(self) -> str:
        """Get extra information about the performed check and the result."""
