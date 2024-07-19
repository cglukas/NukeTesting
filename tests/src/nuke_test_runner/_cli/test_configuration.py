"""Tests for loading runners from configurations."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest
from nuke_test_runner._cli.configuration import find_configuration, load_runners
from nuke_test_runner._cli.runner import Runner, RunnerException


@pytest.fixture()
def runner_mock() -> MagicMock:
    """Get a mock of the runner."""
    with patch("nuke_test_runner._cli.configuration.Runner", spec=Runner) as runner:
        yield runner


@pytest.fixture()
def config_file() -> MagicMock:
    """Get a mock for the config file.

    Use "config_file.read_text.return_value" to configure the content of the config file.
    """
    return MagicMock(spec=Path)


def test_load_single_runner(runner_mock: MagicMock, config_file: MagicMock) -> None:
    """Test that a runner is loaded from a single config."""
    config = {"test": {"exe": "test.exe", "args": ["-test"]}}
    config_file.read_text.return_value = json.dumps(config)

    runner = load_runners(config_file)

    runner_mock.assert_called_once_with("test.exe", ["-test"])
    assert runner["test"] is runner_mock.return_value, "Runner was not added to the output"


@pytest.mark.parametrize("names", [("nuke", "nukeX"), ("nuke-nc", "n", "studio")])
def test_load_multiple_runners(runner_mock: MagicMock, config_file: MagicMock, names: tuple[str]) -> None:
    """Test that multiple runners can be loaded from the config."""
    config = {name: {"exe": name, "args": [name]} for name in names}
    config_file.read_text.return_value = json.dumps(config)

    runners = load_runners(config_file)

    for name in names:
        assert runners[name]
        runner_mock.assert_any_call(name, [name])


def test_load_runners_with_errors(runner_mock: MagicMock, config_file: MagicMock) -> None:
    """Test that wrongly configured runners are not preventing other runners from loading."""
    names = ["correct", "mistake", "correct2"]
    config = {name: {"exe": name, "args": [name]} for name in names}
    config_file.read_text.return_value = json.dumps(config)
    runner_mock.side_effect = [None, RunnerException("Test exception"), None]

    runners = load_runners(config_file)

    assert "correct" in runners
    assert "correct2" in runners
    assert "mistake" not in runners


def test_config_file_does_not_exist(runner_mock: MagicMock, config_file: MagicMock) -> None:
    """Test that an empty dictionary is returned if the files does not exist."""
    config_file.exists.return_value = False

    assert load_runners(config_file) == {}


@pytest.mark.parametrize(
    "start_path",
    [".", "sub1/sub2/", "sub1/test.py", "test.py", "sub1/sub2/test.py"],
)
def test_find_config(start_path: str) -> None:
    """Test that the config can be found in the parent folder."""
    with TemporaryDirectory() as tmp_dir:
        cwd = Path(tmp_dir)
        test_file = cwd / start_path
        if test_file.is_file():
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("Test")
        else:
            test_file.mkdir(parents=True, exist_ok=True)

        config = cwd / "runners.json"
        config.write_text("config")

        assert find_configuration(test_file) == config


def test_find_config_root_dir_loop() -> None:
    """Test that the find config won't loop endlessly if it reaches the root."""
    assert find_configuration(Path(Path(__file__).anchor)) is None
