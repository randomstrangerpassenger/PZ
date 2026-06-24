"""Pytest default collection route for Round 3 current-contract tests."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parents[4]
TAXONOMY_PATH = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_test_taxonomy.json"
VALID_CONTRACTS = {"current", "historical", "diagnostic", "all"}


def pytest_addoption(parser):
    parser.addoption(
        "--round3-contract",
        action="store",
        default="current",
        choices=sorted(VALID_CONTRACTS),
        help="Round 3 description-v2 test contract to collect; default: current.",
    )


@lru_cache(maxsize=1)
def _taxonomy() -> dict[str, object]:
    if not TAXONOMY_PATH.exists():
        raise RuntimeError(f"Round 3 taxonomy is missing: {TAXONOMY_PATH}")
    return json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))


def _contract(config) -> str:
    value = config.getoption("--round3-contract", default="current")
    if value not in VALID_CONTRACTS:
        raise RuntimeError(f"Unsupported --round3-contract value: {value}")
    return value


def _source_file_for_path(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


@lru_cache(maxsize=None)
def _source_files_for_contract(contract: str) -> frozenset[str]:
    if contract == "all":
        return frozenset()
    rows = _taxonomy()["rows"]
    return frozenset(
        row["source_file"]
        for row in rows
        if row["contract_class"] == contract and row["state"] == "ok"
    )


@lru_cache(maxsize=None)
def _known_source_files() -> frozenset[str]:
    return frozenset(row["source_file"] for row in _taxonomy()["rows"])


@lru_cache(maxsize=None)
def _test_ids_for_contract(contract: str) -> frozenset[str]:
    if contract == "all":
        return frozenset()
    rows = _taxonomy()["rows"]
    return frozenset(
        row["test_id"]
        for row in rows
        if row["contract_class"] == contract and row["state"] == "ok"
    )


def _item_test_id(item) -> str:
    path = Path(str(item.path))
    stem = path.stem
    parts = item.nodeid.split("::")[1:]
    if not parts:
        return stem
    leaf = parts[-1].split("[", 1)[0]
    if len(parts) >= 2:
        parent = parts[-2].split("[", 1)[0]
        return f"{stem}.{parent}.{leaf}"
    return f"{stem}.{leaf}"


def _is_description_v2_test(path: Path) -> bool:
    resolved = path.resolve()
    return (
        resolved.parent == TESTS_DIR
        and resolved.suffix == ".py"
        and resolved.name.startswith("test_")
    )


def pytest_ignore_collect(collection_path=None, path=None, config=None):
    raw_path = collection_path if collection_path is not None else path
    if raw_path is None or config is None:
        return False
    candidate = Path(str(raw_path))
    if not _is_description_v2_test(candidate):
        return False
    contract = _contract(config)
    if contract == "all":
        return False
    source_file = _source_file_for_path(candidate)
    if source_file not in _known_source_files():
        return False
    return source_file not in _source_files_for_contract(contract)


def pytest_collection_modifyitems(config, items):
    contract = _contract(config)
    if contract == "all":
        return

    allowed_ids = _test_ids_for_contract(contract)
    selected = []
    deselected = []
    unknown = []

    for item in items:
        item_path = Path(str(item.path))
        if not _is_description_v2_test(item_path):
            selected.append(item)
            continue
        test_id = _item_test_id(item)
        if test_id in allowed_ids:
            selected.append(item)
            continue
        source_file = _source_file_for_path(item_path)
        if source_file not in _known_source_files():
            unknown.append(test_id)
            selected.append(item)
            continue
        deselected.append(item)

    if unknown:
        joined = ", ".join(sorted(unknown))
        raise RuntimeError(
            "Round 3 taxonomy is stale; collected unknown description-v2 tests: "
            f"{joined}"
        )

    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected
