from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any

from _dvf_3_3_vnext_common import (
    IRIS_ROOT,
    LIVE_DATA_DIR,
    LIVE_OUTPUT_DIR,
    REPO_ROOT,
    RUNTIME_CHUNK_DIR,
    V2_ROOT,
    canonical_hash,
    file_record,
    read_json,
    read_jsonl,
    rel,
    sha256_file,
    write_json,
)


EVIDENCE_ROOT = V2_ROOT / "staging" / "dvf_3_3_current_route_baseline_source_overlay_repair"
AUTHORIZATION_DOC = REPO_ROOT / "docs" / "dvf_3_3_current_route_baseline_source_overlay_repair_authorization.md"
ALLOWLIST = EVIDENCE_ROOT / "phase6" / "exact_target_allowlist_draft.json"
MANIFEST = LIVE_DATA_DIR / "dvf_3_3_input_manifest.json"

SOURCE_FACTS = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_vnext_rejected_delta_correction_reparity"
    / "phase5"
    / "corrected_input_snapshot"
    / "dvf_3_3_facts.corrected.jsonl"
)
SOURCE_DECISIONS = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_vnext_rejected_delta_correction_reparity"
    / "phase5"
    / "corrected_input_snapshot"
    / "dvf_3_3_decisions.corrected.normalized.jsonl"
)
TARGET_FACTS = LIVE_DATA_DIR / "dvf_3_3_facts.jsonl"
TARGET_DECISIONS = LIVE_DATA_DIR / "dvf_3_3_decisions.jsonl"
FORBIDDEN_OVERLAY = LIVE_DATA_DIR / "dvf_3_3_overlay_support.jsonl"
FORBIDDEN_RENDERED = LIVE_OUTPUT_DIR / "dvf_3_3_rendered.json"
FORBIDDEN_PACKAGE_CHUNK_DIR = (
    IRIS_ROOT / "build" / "package" / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks"
)

AUTHORIZED_PAIRS = (
    ("facts", SOURCE_FACTS, TARGET_FACTS),
    ("decisions", SOURCE_DECISIONS, TARGET_DECISIONS),
)
FORBIDDEN_TARGETS = (
    FORBIDDEN_OVERLAY,
    FORBIDDEN_RENDERED,
    RUNTIME_CHUNK_DIR,
    FORBIDDEN_PACKAGE_CHUNK_DIR,
)


def row_count(path: Path) -> int:
    return len(read_jsonl(path))


def manifest_expectations() -> dict[str, dict[str, Any]]:
    manifest = read_json(MANIFEST)
    return {
        "facts": {
            "path": manifest["facts"]["path"],
            "row_count": manifest["facts"]["row_count"],
            "sha256": manifest["facts"]["sha256"],
        },
        "decisions": {
            "path": manifest["decisions"]["path"],
            "row_count": manifest["decisions"]["row_count"],
            "sha256": manifest["decisions"]["sha256"],
        },
    }


def source_record(kind: str, source: Path, expectations: dict[str, dict[str, Any]]) -> dict[str, Any]:
    expected = expectations[kind]
    return {
        **file_record(source, f"authorized_{kind}_source"),
        "row_count": row_count(source),
        "expected_row_count": expected["row_count"],
        "expected_sha256": expected["sha256"],
        "row_count_matches_manifest": row_count(source) == expected["row_count"],
        "sha256_matches_manifest": sha256_file(source) == expected["sha256"],
    }


def target_record(kind: str, target: Path, expectations: dict[str, dict[str, Any]]) -> dict[str, Any]:
    expected = expectations[kind]
    exists = target.exists()
    count = row_count(target) if exists else None
    digest = sha256_file(target)
    return {
        **file_record(target, f"authorized_{kind}_target"),
        "row_count": count,
        "expected_row_count": expected["row_count"],
        "expected_sha256": expected["sha256"],
        "row_count_matches_manifest": count == expected["row_count"],
        "sha256_matches_manifest": digest == expected["sha256"],
    }


def directory_fingerprint(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_dir():
        return {"file_count": None, "aggregate_sha256": None, "files": []}
    rows = [
        {
            "path": rel(child),
            "sha256": sha256_file(child),
            "bytes": child.stat().st_size,
        }
        for child in sorted(path.rglob("*"))
        if child.is_file()
    ]
    return {
        "file_count": len(rows),
        "aggregate_sha256": canonical_hash(rows),
        "files": rows,
    }


def path_state_record(path: Path, role: str) -> dict[str, Any]:
    record = file_record(path, role)
    if path.exists() and path.is_file() and path.suffix == ".jsonl":
        record["row_count"] = row_count(path)
    if path.exists() and path.is_dir():
        record.update(directory_fingerprint(path))
    return record


def state_fingerprint(record: dict[str, Any]) -> str | None:
    return record.get("aggregate_sha256") or record.get("sha256")


def read_allowlist() -> dict[str, Any]:
    if not ALLOWLIST.exists():
        raise RuntimeError(f"allowlist is missing: {rel(ALLOWLIST)}")
    payload = read_json(ALLOWLIST)
    if not isinstance(payload, dict):
        raise RuntimeError(f"allowlist must be a JSON object: {rel(ALLOWLIST)}")
    return payload


def paths_from_rows(rows: Any) -> set[str]:
    if not isinstance(rows, list):
        return set()
    paths = set()
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("path"), str):
            paths.add(row["path"])
    return paths


def assert_authorized_scope() -> dict[str, Any]:
    if not AUTHORIZATION_DOC.exists():
        raise RuntimeError(f"authorization document is missing: {rel(AUTHORIZATION_DOC)}")
    allowlist = read_allowlist()
    expected_sources = {rel(source) for _, source, _ in AUTHORIZED_PAIRS}
    expected_targets = {rel(target) for _, _, target in AUTHORIZED_PAIRS}
    expected_forbidden = {rel(path) for path in FORBIDDEN_TARGETS}
    actual_sources = paths_from_rows(allowlist.get("authorized_source_artifacts"))
    actual_targets = paths_from_rows(allowlist.get("live_write_targets"))
    actual_forbidden = paths_from_rows(allowlist.get("excluded_targets"))
    checks = {
        "execution_authorized": allowlist.get("execution_authorized") is True,
        "requires_separate_authorization_cleared": allowlist.get("requires_separate_authorization") is False,
        "authorization_doc_matches": allowlist.get("authorization_doc") == rel(AUTHORIZATION_DOC),
        "authorized_source_set_matches": actual_sources == expected_sources,
        "authorized_target_set_matches": actual_targets == expected_targets,
        "forbidden_target_set_covers_required": expected_forbidden.issubset(actual_forbidden),
        "overlay_not_in_write_targets": rel(FORBIDDEN_OVERLAY) not in actual_targets,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"allowlist validation failed: {failed}")
    actual_target_paths = {target.resolve() for _, _, target in AUTHORIZED_PAIRS}
    expected_target_paths = {TARGET_FACTS.resolve(), TARGET_DECISIONS.resolve()}
    if actual_target_paths != expected_target_paths:
        raise RuntimeError(f"authorized target set drifted: {sorted(str(path) for path in actual_target_paths)}")
    if any(target.resolve() == (LIVE_DATA_DIR / "dvf_3_3_overlay_support.jsonl").resolve() for _, _, target in AUTHORIZED_PAIRS):
        raise RuntimeError("overlay support is forbidden in this reconnect writer")
    return {
        "status": "PASS",
        "allowlist_path": rel(ALLOWLIST),
        "checks": checks,
        "authorized_source_paths": sorted(expected_sources),
        "authorized_target_paths": sorted(expected_targets),
        "required_forbidden_targets": sorted(expected_forbidden),
    }


def validate_sources(expectations: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    records = [source_record(kind, source, expectations) for kind, source, _ in AUTHORIZED_PAIRS]
    failures = [
        record
        for record in records
        if not record["exists"] or not record["row_count_matches_manifest"] or not record["sha256_matches_manifest"]
    ]
    if failures:
        raise RuntimeError(f"authorized source validation failed: {[record['path'] for record in failures]}")
    return records


def snapshot_record(kind: str, target: Path, snapshot: Path) -> dict[str, Any]:
    return {
        "kind": kind,
        "source_target": rel(target),
        "snapshot_path": rel(snapshot),
        "snapshot_sha256": sha256_file(snapshot),
        "snapshot_row_count": row_count(snapshot) if snapshot.exists() else None,
    }


def snapshot_prewrite_targets(phase: Path) -> list[dict[str, Any]]:
    snapshot_dir = phase / "prewrite_snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshots: list[dict[str, Any]] = []
    for kind, _, target in AUTHORIZED_PAIRS:
        snapshot = snapshot_dir / target.name
        if target.exists() and not snapshot.exists():
            shutil.copyfile(target, snapshot)
        snapshots.append(snapshot_record(kind, target, snapshot))
    return snapshots


def snapshot_current_run_targets(run_dir: Path) -> list[dict[str, Any]]:
    snapshot_dir = run_dir / "prewrite_snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=False)
    snapshots: list[dict[str, Any]] = []
    for kind, _, target in AUTHORIZED_PAIRS:
        snapshot = snapshot_dir / target.name
        if target.exists():
            shutil.copyfile(target, snapshot)
        snapshots.append(snapshot_record(kind, target, snapshot))
    return snapshots


def next_run_dir(phase: Path) -> Path:
    runs = phase / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    existing = [
        int(path.name.removeprefix("run_"))
        for path in runs.iterdir()
        if path.is_dir() and path.name.startswith("run_") and path.name.removeprefix("run_").isdigit()
    ]
    return runs / f"run_{max(existing, default=0) + 1:03d}"


def materialize_authorized_pairs() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for _, source, target in AUTHORIZED_PAIRS:
        before_sha = sha256_file(target)
        source_sha = sha256_file(source)
        if before_sha == source_sha:
            action = "skipped_already_matching"
        else:
            shutil.copyfile(source, target)
            action = "copied"
        results.append(
            {
                "source": rel(source),
                "target": rel(target),
                "action": action,
                "before_sha256": before_sha,
                "source_sha256": source_sha,
                "after_sha256": sha256_file(target),
            }
        )
    return results


def run(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase = root / "phase8_authorized_live_reconnect"
    phase.mkdir(parents=True, exist_ok=True)
    allowlist_validation = assert_authorized_scope()
    expectations = manifest_expectations()
    source_records = validate_sources(expectations)
    forbidden_before = [path_state_record(path, "forbidden_live_target_before") for path in FORBIDDEN_TARGETS]
    before_records = [target_record(kind, target, expectations) for kind, _, target in AUTHORIZED_PAIRS]
    snapshots = snapshot_prewrite_targets(phase)
    run_dir = next_run_dir(phase)
    current_run_snapshots = snapshot_current_run_targets(run_dir)

    materialization_results = materialize_authorized_pairs()

    after_records = [target_record(kind, target, expectations) for kind, _, target in AUTHORIZED_PAIRS]
    forbidden_after = [path_state_record(path, "forbidden_live_target_after") for path in FORBIDDEN_TARGETS]
    forbidden_unchanged = all(
        state_fingerprint(before) == state_fingerprint(after)
        for before, after in zip(forbidden_before, forbidden_after, strict=True)
    )
    status = "PASS" if all(
        record["row_count_matches_manifest"] and record["sha256_matches_manifest"] for record in after_records
    ) and forbidden_unchanged else "FAIL"
    report = {
        "schema_version": "dvf-3-3-authorized-live-source-reconnect-v1",
        "status": status,
        "authorization_doc": rel(AUTHORIZATION_DOC),
        "allowlist_validation": allowlist_validation,
        "manifest": rel(MANIFEST),
        "authorized_scope": "live_facts_decisions_only",
        "authorized_source_records": source_records,
        "prewrite_target_records": before_records,
        "immutable_initial_prewrite_snapshots": snapshots,
        "current_run_evidence_dir": rel(run_dir),
        "current_run_prewrite_snapshots": current_run_snapshots,
        "materialization_results": materialization_results,
        "postwrite_target_records": after_records,
        "live_write_targets": [rel(target) for _, _, target in AUTHORIZED_PAIRS],
        "forbidden_live_targets_not_written": [rel(path) for path in FORBIDDEN_TARGETS],
        "forbidden_target_records_before": forbidden_before,
        "forbidden_target_records_after": forbidden_after,
        "forbidden_targets_unchanged": forbidden_unchanged,
        "full_current_route_pass_claimed": False,
    }
    write_json(phase / "authorized_live_source_reconnect_report.json", report)
    return report


def main() -> int:
    report = run()
    print(f"authorized live source reconnect: {rel(EVIDENCE_ROOT)} status={report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
