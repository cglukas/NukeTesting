"""Entry-point for running the Nuke test runner from your interpreter."""

from __future__ import annotations

import pytest


def main(*args) -> int | pytest.ExitCode:
    """Execute the nuke test runner and forward all args to pytest.

    ```
    import nuke_test_runner
    nuke_test_runner.main(["-x", "mytestdir"])
    ```

    While this is possible, it is recommended to use the cli instead. As
    for example reloads don't work well during the same instance of Python.

    For information about the arguments that can be passed here,
    refer to the pytest docs.

    https://docs.pytest.org/en/7.1.x/how-to/usage.html
    """
    return pytest.main(list(args))
