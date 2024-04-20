from pathlib import Path

NUKE_TESTING_FOLDER = Path(__file__).parent.parent

NUKE_DEPENDENCY_FOLDER = NUKE_TESTING_FOLDER / "nuke_dependencies"
REQUIREMENT_TXT = NUKE_TESTING_FOLDER / "requirements.txt"

RUN_TESTS_SCRIPT = NUKE_TESTING_FOLDER / "NukeTestRunner" / "run_pytest.py"
