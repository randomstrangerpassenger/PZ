"""Classify advisory full-suite failures without weakening current ownership."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


PRIORITY = {
    "diagnostic": 1,
    "historical": 2,
    "unknown": 3,
    "excluded-contract-drift": 4,
    "current": 5,
    "modified": 6,
    "mandatory": 7,
}
IN_SCOPE_CLASSES = {"mandatory", "modified", "current", "unknown", "excluded-contract-drift"}


def source_from_nodeid(nodeid: str) -> str | None:
    source = nodeid.split("::", 1)[0].replace("\\", "/")
    return source if source.endswith(".py") else None


def classify_failure(
    failure: dict[str, Any],
    *,
    source_classes: dict[str, str],
    mixed_sources: set[str],
    modified_paths: set[str],
    mandatory_test_ids: set[str],
) -> str:
    nodeid = str(failure.get("nodeid", ""))
    source = str(failure.get("source_file") or source_from_nodeid(nodeid) or "")
    test_id = failure.get("test_id")
    if test_id in mandatory_test_ids or nodeid in mandatory_test_ids:
        return "mandatory"
    if source in modified_paths:
        return "modified"
    if failure.get("source_level") and source in mixed_sources:
        return "unknown"
    classification = source_classes.get(source)
    if classification == "excluded":
        return "excluded-contract-drift"
    if classification in {"current", "historical", "diagnostic"}:
        return classification
    return "unknown"


def classify_report(
    failures: Iterable[dict[str, Any]],
    *,
    source_classes: dict[str, str],
    mixed_sources: set[str],
    modified_paths: set[str],
    mandatory_test_ids: set[str],
    requested_downgrades: dict[str, str] | None = None,
) -> dict[str, Any]:
    rows = []
    for failure in failures:
        classification = classify_failure(
            failure,
            source_classes=source_classes,
            mixed_sources=mixed_sources,
            modified_paths=modified_paths,
            mandatory_test_ids=mandatory_test_ids,
        )
        requested = (requested_downgrades or {}).get(str(failure.get("nodeid", "")))
        if requested is not None and PRIORITY.get(requested, -1) < PRIORITY[classification]:
            raise ValueError(
                f"Manual downgrade is forbidden: {classification} -> {requested} "
                f"for {failure.get('nodeid')}"
            )
        if requested is not None and PRIORITY.get(requested, -1) >= PRIORITY[classification]:
            classification = requested
        rows.append({**failure, "classification": classification})
    blocking = any(row["classification"] in IN_SCOPE_CLASSES for row in rows)
    return {
        "schema_version": "round3-pytest-failure-classification-v1",
        "failures": rows,
        "scoped_status": "unvalidated_but_in_scope" if blocking else "out_of_scope",
        "configured_full_suite_pass": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = classify_report(
        payload.get("failures", []),
        source_classes=dict(payload.get("source_classes", {})),
        mixed_sources=set(payload.get("mixed_sources", [])),
        modified_paths=set(payload.get("modified_paths", [])),
        mandatory_test_ids=set(payload.get("mandatory_test_ids", [])),
        requested_downgrades=dict(payload.get("requested_downgrades", {})),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
