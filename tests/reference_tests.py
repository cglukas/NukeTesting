"""File with reference tests for checking testrunner execution."""


def test_failing() -> None:
    """A test that is always failing."""
    assert False


def test_passing() -> None:
    """A test that is always passing."""
    assert True
