"""Pytest discovery policy for Round 3 contracts.

The exact item taxonomy remains the authority used by the dedicated Round 3
runner.  Ordinary pytest discovery uses the separately owner-approved source
policy loaded here.  Keeping the two concerns separate prevents a newly added
test source from silently becoming a required current-route test.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parents[4]
ROUND3_DIR = REPO_ROOT / "Iris" / "_docs" / "round3"
TAXONOMY_PATH = ROUND3_DIR / "round3_test_taxonomy.json"
SOURCE_POLICY_PATH = ROUND3_DIR / "round3_pytest_source_classification.json"
DENOMINATOR_PATH = ROUND3_DIR / "round3_full_discovery_denominator.json"
VALID_CONTRACTS = {"current", "historical", "diagnostic", "all"}
SOURCE_CLASSES = VALID_CONTRACTS - {"all"} | {"excluded"}

_COLLECT_REPORTS: dict[str, dict[str, Any]] = {}


def pytest_addoption(parser):
    parser.addoption(
        "--round3-contract",
        action="store",
        default="current",
        choices=sorted(VALID_CONTRACTS),
        help="Round 3 source contract to collect; default: current.",
    )
    parser.addoption(
        "--round3-additional-source",
        action="append",
        default=[],
        help=(
            "Exact repository-relative test source additionally selected by "
            "a tracked validation contract."
        ),
    )
    parser.addoption(
        "--round3-enforce-denominator",
        action="store_true",
        default=False,
        help="Fail closed unless collected source coverage equals the approved denominator.",
    )
    parser.addoption(
        "--round3-denominator-receipt",
        action="store",
        default=None,
        help="Optional external path for the collection/execution denominator receipt.",
    )


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required Round 3 policy file is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Round 3 policy must be a JSON object: {path}")
    return payload


@lru_cache(maxsize=1)
def _taxonomy() -> dict[str, Any]:
    return _read_json(TAXONOMY_PATH)


@lru_cache(maxsize=1)
def _source_policy_payload() -> dict[str, Any]:
    payload = _read_json(SOURCE_POLICY_PATH)
    if payload.get("schema_version") != "round3-pytest-source-classification-v1":
        raise RuntimeError("Unsupported Round 3 source-classification schema")
    approval = payload.get("owner_approval")
    if not isinstance(approval, dict) or approval.get("approved") is not True:
        raise RuntimeError("Round 3 source classification lacks owner approval")
    return payload


def _normalize_source(value: str) -> str:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise RuntimeError(f"Unsafe Round 3 source path: {value}")
    normalized = candidate.as_posix()
    if normalized != value or not normalized.endswith(".py"):
        raise RuntimeError(f"Non-canonical Round 3 source path: {value}")
    return normalized


def _taxonomy_source_classes() -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for row in _taxonomy().get("rows", []):
        if row.get("state") != "ok":
            continue
        source = _normalize_source(row["source_file"])
        classification = row.get("contract_class")
        if classification not in VALID_CONTRACTS - {"all"}:
            raise RuntimeError(
                f"Invalid exact taxonomy class for {source}: {classification}"
            )
        result.setdefault(source, set()).add(classification)
    return result


@lru_cache(maxsize=1)
def _source_policy() -> dict[str, str]:
    payload = _source_policy_payload()
    mixed_defaults = {
        _normalize_source(row["source_file"]): row["default_classification"]
        for row in payload.get("mixed_sources", [])
    }
    result: dict[str, str] = {}
    for source, classes in _taxonomy_source_classes().items():
        if len(classes) == 1:
            result[source] = next(iter(classes))
            continue
        default = mixed_defaults.get(source)
        if default not in classes:
            joined = ",".join(sorted(classes))
            raise RuntimeError(
                f"Mixed taxonomy source requires an approved default: {source} ({joined})"
            )
        result[source] = default

    for row in payload.get("reviewed_sources", []):
        source = _normalize_source(row["source_file"])
        classification = row.get("classification")
        if classification not in SOURCE_CLASSES - {"excluded"}:
            raise RuntimeError(f"Invalid reviewed source class for {source}: {classification}")
        if not row.get("reason"):
            raise RuntimeError(f"Reviewed source lacks a reason: {source}")
        result[source] = classification

    for row in payload.get("planned_sources", []):
        source = _normalize_source(row["source_file"])
        classification = row.get("classification")
        if classification not in SOURCE_CLASSES - {"excluded"}:
            raise RuntimeError(f"Invalid planned source class for {source}: {classification}")
        result[source] = classification

    for row in payload.get("additional_sources", []):
        source = _normalize_source(row["source_file"])
        classification = row.get("classification")
        if classification not in SOURCE_CLASSES - {"excluded"}:
            raise RuntimeError(f"Invalid additional source class for {source}: {classification}")
        result[source] = classification

    required_exclusion_fields = {"reason", "alternative_validation", "owner", "reviewed_at"}
    for row in payload.get("excluded_sources", []):
        source = _normalize_source(row["source_file"])
        missing = sorted(field for field in required_exclusion_fields if not row.get(field))
        if missing:
            raise RuntimeError(f"Excluded source {source} lacks fields: {', '.join(missing)}")
        result[source] = "excluded"
    return result


@lru_cache(maxsize=1)
def _item_overrides() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for source_row in _source_policy_payload().get("mixed_sources", []):
        source = _normalize_source(source_row["source_file"])
        overrides: dict[str, str] = {}
        for row in source_row.get("item_overrides", []):
            test_id = row.get("test_id")
            classification = row.get("classification")
            if not test_id or classification not in VALID_CONTRACTS - {"all"}:
                raise RuntimeError(f"Invalid mixed item override in {source}")
            if test_id in overrides:
                raise RuntimeError(f"Duplicate mixed item override: {test_id}")
            overrides[test_id] = classification
        result[source] = overrides
    return result


@lru_cache(maxsize=1)
def _actual_controlled_sources() -> set[str]:
    description_sources = {
        _source_file_for_path(path)
        for path in TESTS_DIR.glob("test_*.py")
        if path.is_file()
    }
    payload = _source_policy_payload()
    auxiliary = {
        _normalize_source(row["source_file"])
        for key in ("additional_sources", "excluded_sources")
        for row in payload.get(key, [])
        if (REPO_ROOT / row["source_file"]).is_file()
    }
    return description_sources | auxiliary


def _validate_policy_inventory() -> None:
    payload = _source_policy_payload()
    policy = _source_policy()
    actual = _actual_controlled_sources()
    planned = {
        _normalize_source(row["source_file"])
        for row in payload.get("planned_sources", [])
    }
    clean_checkout_optional = {
        _normalize_source(row["source_file"])
        for row in payload.get("reviewed_sources", [])
        if row.get("clean_checkout_optional") is True
    }
    unclassified = sorted(actual - policy.keys())
    vanished = sorted(
        source
        for source in policy.keys() - actual
        if source not in _taxonomy_source_classes()
        and source not in planned
        and source not in clean_checkout_optional
    )
    if unclassified or vanished:
        parts = []
        if unclassified:
            parts.append("unclassified=" + ", ".join(unclassified))
        if vanished:
            parts.append("vanished=" + ", ".join(vanished))
        raise RuntimeError("Round 3 source classification is incomplete: " + "; ".join(parts))


def _contract(config) -> str:
    value = config.getoption("--round3-contract", default="current")
    if value not in VALID_CONTRACTS:
        raise RuntimeError(f"Unsupported --round3-contract value: {value}")
    return value


def _source_file_for_path(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


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


def _additional_source_files(config) -> frozenset[str]:
    sources = set()
    for value in config.getoption("--round3-additional-source", default=[]):
        candidate = Path(value)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise RuntimeError(f"Unsafe --round3-additional-source value: {value}")
        resolved = (REPO_ROOT / candidate).resolve()
        try:
            source_file = _source_file_for_path(resolved)
        except ValueError as exc:
            raise RuntimeError(f"Additional source is outside the repository: {value}") from exc
        if source_file != candidate.as_posix():
            raise RuntimeError(f"Additional source is not canonical: {value}")
        sources.add(source_file)
    return frozenset(sources)


def _classification_for_item(source: str, test_id: str) -> str | None:
    return _item_overrides().get(source, {}).get(test_id, _source_policy().get(source))


def _is_controlled_test(path: Path) -> bool:
    try:
        source = _source_file_for_path(path)
    except ValueError:
        return False
    return source in _actual_controlled_sources()


def pytest_configure(config):
    _COLLECT_REPORTS.clear()
    _validate_policy_inventory()
    if config.getoption("--round3-enforce-denominator", default=False):
        denominator = _read_json(DENOMINATOR_PATH)
        if denominator.get("schema_version") != "round3-full-discovery-denominator-v1":
            raise RuntimeError("Unsupported Round 3 denominator schema")
        if denominator.get("source_classification") != SOURCE_POLICY_PATH.relative_to(REPO_ROOT).as_posix():
            raise RuntimeError("Round 3 denominator points at a different source policy")


def pytest_ignore_collect(collection_path=None, path=None, config=None):
    raw_path = collection_path if collection_path is not None else path
    if raw_path is None or config is None:
        return None
    candidate = Path(str(raw_path))
    if not candidate.name.startswith("test_") or candidate.suffix != ".py":
        return None
    try:
        source = _source_file_for_path(candidate)
    except ValueError:
        return None
    classification = _source_policy().get(source)
    if classification is None:
        return None
    if classification == "excluded":
        return True
    contract = _contract(config)
    if contract == "all" or source in _additional_source_files(config):
        return None
    if source in _item_overrides():
        return None
    if classification != contract:
        return True
    return None


def pytest_collectreport(report):
    raw_path = getattr(report, "fspath", None)
    if raw_path is None:
        nodeid = str(getattr(report, "nodeid", "")).split("::", 1)[0]
        if not nodeid.endswith(".py"):
            return
        raw_path = REPO_ROOT / nodeid
    candidate = Path(str(raw_path))
    try:
        source = _source_file_for_path(candidate)
    except ValueError:
        return
    if source not in _source_policy():
        return
    if report.failed:
        _COLLECT_REPORTS[source] = {
            "state": "collection_error",
            "node_count": 0,
            "error_identity": str(report.longrepr).splitlines()[-1],
        }
    elif report.passed and report.when == "collect":
        _COLLECT_REPORTS[source] = {
            "state": "collected",
            "node_count": len(getattr(report, "result", ()) or ()),
            "error_identity": None,
        }


def _expected_sources(contract: str) -> set[str]:
    policy = _source_policy()
    if contract == "all":
        return {source for source, value in policy.items() if value != "excluded" and (REPO_ROOT / source).is_file()}
    return {source for source, value in policy.items() if value == contract and (REPO_ROOT / source).is_file()}


def _write_receipt(config, items, selected_sources: set[str], errors: list[str]) -> None:
    destination = config.getoption("--round3-denominator-receipt", default=None)
    if not destination:
        return
    path = Path(destination)
    if not path.is_absolute():
        raise RuntimeError("--round3-denominator-receipt must be an absolute external path")
    path.parent.mkdir(parents=True, exist_ok=True)
    excluded = []
    for row in _source_policy_payload().get("excluded_sources", []):
        if (REPO_ROOT / row["source_file"]).is_file():
            excluded.append({
                "source_file": row["source_file"],
                "reason": row["reason"],
                "alternative_validation": row["alternative_validation"],
            })
    payload = {
        "schema_version": "round3-denominator-execution-receipt-v1",
        "contract": _contract(config),
        "enforced": bool(config.getoption("--round3-enforce-denominator", default=False)),
        "selected_node_count": len(items),
        "selected_sources": sorted(selected_sources),
        "collect_reports": {key: _COLLECT_REPORTS[key] for key in sorted(_COLLECT_REPORTS)},
        "excluded_sources": excluded,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pytest_collection_modifyitems(config, items):
    contract = _contract(config)
    additional_sources = _additional_source_files(config)
    selected = []
    deselected = []
    unknown_sources: set[str] = set()

    for item in items:
        item_path = Path(str(item.path))
        if not _is_controlled_test(item_path):
            selected.append(item)
            continue
        source = _source_file_for_path(item_path)
        if source not in _source_policy():
            unknown_sources.add(source)
            selected.append(item)
            continue
        if source in additional_sources or contract == "all":
            selected.append(item)
            continue
        classification = _classification_for_item(source, _item_test_id(item))
        if classification == contract:
            selected.append(item)
        else:
            deselected.append(item)

    if unknown_sources:
        raise RuntimeError(
            "Round 3 source classification is stale; unknown sources: "
            + ", ".join(sorted(unknown_sources))
        )

    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected

    if not config.getoption("--round3-enforce-denominator", default=False):
        return

    selected_sources = {
        _source_file_for_path(Path(str(item.path)))
        for item in items
        if _is_controlled_test(Path(str(item.path)))
    }
    expected = _expected_sources(contract)
    errors: list[str] = []
    missing = sorted(expected - selected_sources)
    unexpected = sorted(selected_sources - expected - additional_sources)
    collection_errors = sorted(
        source
        for source, row in _COLLECT_REPORTS.items()
        if source in expected and row["state"] == "collection_error"
    )
    if missing:
        errors.append("missing included sources: " + ", ".join(missing))
    if unexpected:
        errors.append("unexpected selected sources: " + ", ".join(unexpected))
    if collection_errors:
        errors.append("included-source collection errors: " + ", ".join(collection_errors))
    if contract == "all" and deselected:
        errors.append(f"all-contract policy deselected {len(deselected)} items")

    _write_receipt(config, items, selected_sources, errors)
    if errors:
        raise RuntimeError("Round 3 denominator enforcement failed: " + "; ".join(errors))
