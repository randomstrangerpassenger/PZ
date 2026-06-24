"""Pytest collection guard for script-style Iris build tests."""
from __future__ import annotations

from pathlib import Path


ACTIVE_PYTEST_FILES = {
    "test_evidence_pipeline_cross_track.py",
}

TESTS_DIR = Path(__file__).resolve().parent

collect_ignore = sorted(
    path.name
    for path in TESTS_DIR.glob("test_*.py")
    if path.name not in ACTIVE_PYTEST_FILES
)


def pytest_ignore_collect(collection_path=None, path=None, config=None):
    raw_path = collection_path if collection_path is not None else path
    if raw_path is None:
        return False

    candidate = Path(str(raw_path)).resolve()
    if candidate.parent != TESTS_DIR:
        return False
    if candidate.suffix != ".py" or not candidate.name.startswith("test_"):
        return False
    return candidate.name not in ACTIVE_PYTEST_FILES
