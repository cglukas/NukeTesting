"""Tests for the constant values."""

from nuke_test_runner.datamodel.constants import (
    NUKE_DEPENDENCY_FOLDER,
    NUKE_TESTING_FOLDER,
    REQUIREMENT_TXT,
)


def test_requirements_txt() -> None:
    """Test that the requirements constant points to an existing file."""
    assert REQUIREMENT_TXT.exists()


def test_dependencies_folder() -> None:
    """Test that the dependencies folder is part of the project folder."""
    assert NUKE_DEPENDENCY_FOLDER.suffix == "", "The dependency folder is no folder!"
    assert str(NUKE_TESTING_FOLDER) in str(
        NUKE_DEPENDENCY_FOLDER
    ), "The dependency folder is not a sub-folder of the testing project."
