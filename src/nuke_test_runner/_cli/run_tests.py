"""Script to parse CLI args and invoke the test runner."""

from typing import NoReturn

import click


@click.command()
@click.option("--nuke_dir", "-n", "nuke_dir", required=False, type=click.Path())
@click.option("--test_dir", "-t", "test_dir", required=False, type=click.Path())
@click.option("--config", "-c", "config", required=False, type=click.Path())
@click.option("--run_interactive", "-i", "interactive", default=False, type=bool)
@click.option("--pytest_arg", "-p", "pytest_arg", multiple=True)
def main(
    nuke_dir: click.Path, test_dir: click.Path, config: click.Path, interactive: bool, pytest_arg: list
) -> NoReturn:
    """Run the test files with nuke.

    INTERPRETER is the filepath to the nuke executable.
    If you provided a "runner.json" configuration,
    you can also reference the runner by its configured name.

    TESTS is the folder of file of the tests you want to execute.
    Use the pytest folder/file.py::class::method notation to run single tests.
    For further options consult the pytest documentation.
    \f

    Args:
        interpreter: name of the configured interpreter or the path to the nuke executable.
        tests: path to the test/ test folder.
    """


if __name__ == "__main__":
    main()
