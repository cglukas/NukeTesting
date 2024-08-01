from pathlib import Path

NUKE_TESTING_FOLDER = Path(__file__).parent.parent

RUN_TESTS_SCRIPT = NUKE_TESTING_FOLDER / "_cli" / "run_pytest_bootstrapped.py"
