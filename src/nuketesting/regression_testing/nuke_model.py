"""Datamodel for nuke specific functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import nuke

if TYPE_CHECKING:
    from nuketesting.regression_testing.datamodel import RegressionTestCase


def load_expected(test_case: RegressionTestCase) -> nuke.Node:
    """Load the expected output in a read node.

    Args:
        test_case: The test case with an existing ``expected_output``.

    Returns:
        A read node with the file loaded.

    """
    return nuke.nodes.Read(file=test_case.expected_output.as_posix(), raw=True)


def load_nodes(test_case: RegressionTestCase) -> nuke.Node:
    """Load the nodes of the test case.

    Args:
        test_case: The test case with an existing ``nuke_script``.

    Returns:
        The ``RegressionCheck`` node.

    """
    nuke.nodePaste(str(test_case.nuke_script))
    return nuke.toNode("RegressionCheck")
