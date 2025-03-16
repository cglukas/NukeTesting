"""Module for handling debugging inside the nuke runner."""

from __future__ import annotations

import inspect
import os
import sys
from pathlib import Path

DEBUG_ENV_HOST = "NUKE_RUNNER_DEBUG_HOST"
DEBUG_ENV_PORT = "NUKE_RUNNER_DEBUG_PORT"
DEBUG_ENV_PYDEVD_SRC = "NUKE_RUNNER_DEBUG_PYDEVD_SRC"


def get_debug_info() -> dict[str, str]:
    """Get the current debugger configuration for adding it to the run environment.

    Examples:
        Provide debug information for subprocesses that want to reconnect to the current debugging session:
        >>> import subprocess
        >>> env = os.environ.copy() # Don't change the current env
        >>> env.update(get_debug_info())
        >>> subprocess.call("echo test", env=env)
    """
    try:
        import pydevd

        setup = pydevd.SetupHolder.setup
        return {
            DEBUG_ENV_HOST: str(setup["client"]),
            DEBUG_ENV_PORT: str(setup["port"]),
            DEBUG_ENV_PYDEVD_SRC: str(Path(inspect.getfile(pydevd)).parent),
        }
    except ImportError:
        # The program is not debugged, or it's not debugged through PyCharm/LiClipse.
        return {}


def try_reconnect_to_debugger() -> None:
    """Try to connect to an active debugging session by using previously stored debug information of the environment.

    Notes:
        This method only works together with the `get_debug_info` which collects required information of the debug
        configuration. This information needs to be available in the environment of the child process so that this
        method can try to establish a connection.
    """
    pydevd_src = os.getenv(DEBUG_ENV_PYDEVD_SRC)
    if not pydevd_src:
        return

    sys.path.append(pydevd_src)
    import pydevd

    debug_host = os.environ[DEBUG_ENV_HOST]
    debug_port = os.environ[DEBUG_ENV_PORT]

    pydevd.settrace(
        host=debug_host,
        port=int(debug_port),
        suspend=False,
    )
