"""Data model for the regression testing package."""

from __future__ import annotations

import itertools
import json
import logging
import operator
from dataclasses import asdict, dataclass
from pathlib import Path

import nuke


@dataclass(frozen=True)
class RegressionTestCase:
    """Dataclass for a single regression test case."""

    title: str
    """A user defined title for the test."""
    description: str
    """A detailed description about the test."""
    nuke_script: str | Path
    """The path to the nuke script that represents the test case."""
    expected_output: str | Path
    """The path to the image file that was initially produced by the nuke script."""

    def __post_init__(self):
        """Convert strings to paths."""
        object.__setattr__(self, "nuke_script", Path(self.nuke_script))
        object.__setattr__(self, "expected_output", Path(self.expected_output))

    @property
    def id(self) -> str:
        """The unique test case id for identifying the tests in test runs."""
        return self.title.replace(" ", "")

    def to_json(self) -> str:
        """Create a serializable dictionary of the test case data."""
        data = asdict(self)
        data["nuke_script"] = str(self.nuke_script)
        data["expected_output"] = str(self.expected_output)
        return json.dumps(data)

    @classmethod
    def from_json(cls, data: str) -> RegressionTestCase:
        """Create a test case instance from the serialized data.

        Args:
            data: The data dictionary as string.

        Returns:
            Instance with the data.

        """
        return cls(**json.loads(data))


def load_nodes(test_case: RegressionTestCase) -> nuke.Node:
    """Load the nodes of the test case.

    Args:
        test_case: The test case with an existing ``nuke_script``.

    Returns:
        The ``RegressionCheck`` node..

    """
    nuke.nodePaste(str(test_case.nuke_script))
    return nuke.toNode("RegressionCheck")


def load_expected(test_case: RegressionTestCase) -> nuke.Node:
    """Load the expected output in a read node.

    Args:
        test_case: The test case with an existing ``expected_output``.

    Returns:
        A read node with the file loaded.

    """
    return nuke.nodes.Read(file=test_case.expected_output.as_posix(), raw=True)


def load_from_folder(folder: str | Path) -> list[RegressionTestCase]:
    """Load all test cases from folder.

    Args:
        folder: Path to the folder with the test cases.

    Returns:
        List of test cases.

    """
    folder = Path(folder)
    sorted_by_name = sorted(folder.iterdir(), key=(operator.attrgetter("name")))
    number_of_test_case_files = 3

    all_test_cases = []
    for group_name, files in itertools.groupby(sorted_by_name, key=(operator.attrgetter("stem"))):
        # The files are sorted alphabetically by name including the  suffix. '.exr' >  '.json' > '.nk'
        grouped_files = list(files)
        if len(grouped_files) != number_of_test_case_files:
            logging.debug('Not all test files found for test case "%s"', group_name)
            continue
        exr_file, json_file, nk_file = grouped_files

        test_details = json.loads(json_file.read_text("utf-8"))
        all_test_cases.append(
            RegressionTestCase(
                title=test_details["title"],
                description=test_details["description"],
                nuke_script=nk_file,
                expected_output=exr_file,
            )
        )

    return all_test_cases


def save_to_folder(test_case: RegressionTestCase, output_folder: Path) -> Path:
    """Save the test case information in the folder.

    Args:
        test_case: Test case to save.
        output_folder: Output folder where the test case files are stored.

    Returns:
        The created information json file.

    """
    info_file = output_folder / f"{test_case.id}.json"
    data = {"title": test_case.title, "description": test_case.description}
    info_file.write_text(json.dumps(data))
    return info_file
