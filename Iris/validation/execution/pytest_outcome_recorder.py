"""Write deterministic pytest collection and outcome records externally."""

from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest


RESULT_PATH_ENV = "IRIS_CLEAN_CHECKOUT_PYTEST_RESULT"
_collected: list[dict[str, str]] = []
_reports: dict[str, list[dict[str, Any]]] = defaultdict(list)
_collection_errors: list[dict[str, str]] = []


def _relative_source(item: pytest.Item, root: Path) -> str:
    path = Path(str(item.path)).resolve()
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def pytest_collection_finish(session: pytest.Session) -> None:
    root = Path(str(session.config.rootpath)).resolve()
    _collected[:] = [
        {
            "node_id": item.nodeid,
            "source_path": _relative_source(item, root),
        }
        for item in session.items
    ]


def pytest_collectreport(report: pytest.CollectReport) -> None:
    if report.failed:
        _collection_errors.append(
            {
                "node_id": report.nodeid,
                "message": str(report.longrepr),
            }
        )


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    _reports[report.nodeid].append(
        {
            "phase": report.when,
            "outcome": report.outcome,
            "was_xfail": bool(getattr(report, "wasxfail", False)),
        }
    )


def _outcome(node_id: str, collect_only: bool) -> str:
    if collect_only:
        return "collected"
    reports = _reports.get(node_id, [])
    if any(report["outcome"] == "failed" for report in reports):
        return "failed"
    call_reports = [
        report for report in reports if report["phase"] == "call"
    ]
    if any(report["outcome"] == "passed" for report in call_reports):
        return "passed"
    if any(report["outcome"] == "skipped" for report in reports):
        return "skipped"
    return "not_run"


def pytest_sessionfinish(
    session: pytest.Session, exitstatus: int
) -> None:
    raw_path = os.environ.get(RESULT_PATH_ENV)
    if not raw_path:
        raise RuntimeError(f"{RESULT_PATH_ENV} is required")
    target = Path(raw_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    collect_only = bool(session.config.option.collectonly)
    rows = [
        {
            **row,
            "outcome": _outcome(row["node_id"], collect_only),
        }
        for row in _collected
    ]
    counts = {
        state: sum(row["outcome"] == state for row in rows)
        for state in (
            "collected",
            "passed",
            "failed",
            "skipped",
            "not_run",
        )
    }
    expected = "collected" if collect_only else "passed"
    status = (
        "PASS"
        if int(exitstatus) == 0
        and not _collection_errors
        and rows
        and all(row["outcome"] == expected for row in rows)
        else "FAIL"
    )
    payload = {
        "schema_version": "iris-clean-checkout-pytest-result-v1",
        "mode": "collect_only" if collect_only else "execute",
        "status": status,
        "pytest_version": pytest.__version__,
        "exit_status": int(exitstatus),
        "identity_rows": rows,
        "collection_errors": _collection_errors,
        "counts": counts,
    }
    encoded = (
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    temporary.write_bytes(encoded)
    os.replace(temporary, target)
