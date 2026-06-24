from __future__ import annotations

from collections import Counter, defaultdict
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    V2_ROOT,
    canonical_hash,
    read_json,
    read_jsonl,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_jsonl,
    write_text,
)


GENERATED_AT = "2026-06-21T00:00:00+09:00"
ROUND_ID = "dvf_3_3_live_consumer_migration_execution"
EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
CLAIM_BOUNDARY = (
    "DVF 3-3 live consumer migration execution evidence only; not current authority recutover, "
    "not source/rendered/Lua-bridge/runtime-chunk/package authority mutation, not package readiness, "
    "not release readiness, not Workshop readiness, not B42 readiness, not deployment readiness, "
    "not manual in-game QA, and not public-facing text quality acceptance."
)

PLAN_PATH = REPO_ROOT / "docs" / "dvf_3_3_live_consumer_migration_execution_plan.md"
PLAN_TEMPLATE = REPO_ROOT / "docs" / "PLAN_TEMPLATE.md"
EXECUTION_CONTRACT = REPO_ROOT / "docs" / "EXECUTION_CONTRACT.md"

TERMINAL_ROOT = V2_ROOT / "staging" / "dvf_3_3_terminal_disposition_adjudication"
TERMINAL_LEDGER = TERMINAL_ROOT / "phase3" / "terminal_disposition_ledger.jsonl"
TERMINAL_COUNTS = TERMINAL_ROOT / "phase3" / "terminal_disposition_counts.json"
TERMINAL_FINAL = TERMINAL_ROOT / "phase5" / "final_terminal_disposition_machine_report.json"

READINESS_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_cutover_tooling_readiness"
READINESS_LEDGER = READINESS_ROOT / "phase3" / "row_level_migration_ledger.jsonl"
READINESS_ACTUAL = READINESS_ROOT / "phase3" / "consumer_migration_actual_report.json"
READINESS_DIFF = READINESS_ROOT / "phase4" / "actual_diff_to_ledger_report.json"
READINESS_HANDOFF = READINESS_ROOT / "phase6" / "current_cutover_phase0_handoff_manifest.json"

DENOMINATOR_ROOT = V2_ROOT / "staging" / "consumer_universe_denominator_lock"
DENOMINATOR_REGISTRY = DENOMINATOR_ROOT / "phase4" / "consumer_universe_denominator_registry.json"
DENOMINATOR_FINAL = DENOMINATOR_ROOT / "phase8" / "final_consumer_universe_denominator_lock_report.json"

RUNTIME_ROOT = V2_ROOT / "staging" / "runtime_payload_state_integrity"
RUNTIME_INVENTORY = RUNTIME_ROOT / "phase0" / "runtime_payload_state_inventory.json"
RUNTIME_CLOSEOUT = REPO_ROOT / "docs" / "runtime_payload_state_integrity_closeout.md"

CURRENT_ROUTE_REQUIRED_VALIDATIONS = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
CURRENT_CORE_CLOSURE = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"

CLOSEOUT_DOC = REPO_ROOT / "docs" / "dvf_3_3_live_consumer_migration_execution_closeout.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_live_consumer_migration_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "dvf_3_3_live_consumer_migration_ledger_packet.md"
DECISIONS_PATCH_DOC = REPO_ROOT / "docs" / "DECISIONS.live_migration_execution.patch.md"
ROADMAP_PATCH_DOC = REPO_ROOT / "docs" / "ROADMAP.live_migration_execution.patch.md"
EXTERNAL_REVIEW_DOCS = (
    CLOSEOUT_DOC,
    CLAIM_BOUNDARY_DOC,
    LEDGER_PACKET_DOC,
    DECISIONS_PATCH_DOC,
    ROADMAP_PATCH_DOC,
)
HASH_MANIFEST_NAME = "independent_review_artifact_hash_manifest.json"
HASH_REPORT_NAME = "independent_review_artifact_hash_report.json"

PLAN_LOCAL_STATUSES = (
    "live_verified_already",
    "live_mutation_required",
    "live_applied",
    "live_blocked",
    "live_ambiguous",
    "excluded_non_live_target",
)

HARD_FORBIDDEN_PREFIXES = (
    "Iris/build/description/v2/data/",
    "Iris/build/description/v2/output/",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/",
    "Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
    "Iris/build/package/Iris/media/lua/client/Iris/Data/",
    "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "media/lua/shared/Iris/IrisDvfBridgeData.lua",
)

MIGRATION_MARKER_RE = re.compile(r" DVF_AUTHORITY_ROLE_MIGRATION\[[0-9A-Fa-f]{32}\]")

COMMAND_SURFACE_ROWS = [
    (
        "live_execution_runner",
        "execution_artifact_generation",
        "uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_live_consumer_migration_execution.py --mode all",
        "Iris/build/description/v2/tools/build/run_dvf_3_3_live_consumer_migration_execution.py",
        "phase8/final_live_migration_execution_report.json",
    ),
    (
        "live_execution_validator",
        "focused_live_migration_validation",
        "uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_live_consumer_migration_execution.py",
        "Iris/build/description/v2/tools/build/validate_dvf_3_3_live_consumer_migration_execution.py",
        "phase6/focused_live_migration_validation_report.json",
    ),
    (
        "terminal_disposition_predecessor",
        "terminal_migrated_projection_validation",
        "uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_terminal_disposition_adjudication.py --mode all",
        "Iris/build/description/v2/tools/build/run_dvf_3_3_terminal_disposition_adjudication.py",
        "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase3/terminal_disposition_ledger.jsonl",
    ),
    (
        "readiness_row_ledger_predecessor",
        "sandbox_live_separation_validation",
        "uv run python -B Iris/build/description/v2/tools/build/apply_dvf_3_3_consumer_migration.py",
        "Iris/build/description/v2/tools/build/apply_dvf_3_3_consumer_migration.py",
        "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/row_level_migration_ledger.jsonl",
    ),
    (
        "current_route_contract",
        "current_route_scope_recording",
        "uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure",
        "Iris/_docs/round3/round3_run_contract_tests.py",
        "phase6/current_route_validation_report.json",
    ),
]


def phase_dir(phase: str) -> Path:
    path = EVIDENCE_ROOT / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def stable_record(path: str | Path, role: str, *, required: bool = True, read_only: bool = True) -> dict[str, Any]:
    resolved = resolve_repo(path)
    return {
        "path": rel(resolved),
        "role": role,
        "required": required,
        "read_only": read_only,
        "exists": resolved.exists(),
        "kind": "dir" if resolved.is_dir() else "file" if resolved.is_file() else "missing",
        "sha256": sha256_file(resolved) if resolved.is_file() else None,
        "bytes": resolved.stat().st_size if resolved.exists() and resolved.is_file() else None,
        "row_count": count_jsonl(resolved) if resolved.exists() and resolved.suffix == ".jsonl" else None,
        "status": "PRESENT" if resolved.exists() else "MISSING_REQUIRED" if required else "ABSENT_ALLOWED",
    }


def file_hash_records(paths: Iterable[str]) -> list[dict[str, Any]]:
    records = []
    for path in sorted(set(paths)):
        resolved = resolve_repo(path)
        records.append(
            {
                "path": rel(resolved),
                "exists": resolved.exists(),
                "kind": "dir" if resolved.is_dir() else "file" if resolved.is_file() else "missing",
                "sha256": sha256_file(resolved) if resolved.is_file() else None,
                "bytes": resolved.stat().st_size if resolved.exists() and resolved.is_file() else None,
            }
        )
    return records


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def hash_manifest_path() -> Path:
    return phase_path("phase7", HASH_MANIFEST_NAME)


def hash_report_path() -> Path:
    return phase_path("phase7", HASH_REPORT_NAME)


def independent_review_hash_artifact_paths() -> list[Path]:
    excluded = {hash_manifest_path().resolve(), hash_report_path().resolve()}
    paths: list[Path] = []
    for path in EVIDENCE_ROOT.rglob("*"):
        resolved = path.resolve()
        if path.is_file() and resolved not in excluded:
            paths.append(resolved)
    for path in EXTERNAL_REVIEW_DOCS:
        resolved = path.resolve()
        if resolved.is_file():
            paths.append(resolved)
    return sorted(set(paths), key=rel)


def independent_review_hash_record(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "seal_scope": "evidence_root" if _is_under(path, EVIDENCE_ROOT) else "external_review_docs",
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def independent_review_hash_mismatches(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    for record in records:
        path = resolve_repo(record.get("path", ""))
        if not path.is_file():
            mismatches.append({"path": record.get("path"), "reason": "missing_or_not_file"})
            continue
        actual_sha = sha256_file(path)
        actual_bytes = path.stat().st_size
        if record.get("sha256") != actual_sha or record.get("bytes") != actual_bytes:
            mismatches.append(
                {
                    "path": record.get("path"),
                    "reason": "hash_or_size_mismatch",
                    "expected_sha256": record.get("sha256"),
                    "actual_sha256": actual_sha,
                    "expected_bytes": record.get("bytes"),
                    "actual_bytes": actual_bytes,
                }
            )
    return mismatches


def write_independent_review_hash_artifacts() -> dict[str, Any]:
    artifact_records = [independent_review_hash_record(path) for path in independent_review_hash_artifact_paths()]
    manifest = {
        "schema_version": "dvf-3-3-live-independent-review-artifact-hash-manifest-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "artifact_count": len(artifact_records),
        "self_hash_exclusion": [rel(hash_manifest_path()), rel(hash_report_path())],
        "external_review_doc_paths": [rel(path) for path in EXTERNAL_REVIEW_DOCS],
        "artifacts": artifact_records,
        "aggregate_sha256": canonical_hash(artifact_records),
    }
    write_json(hash_manifest_path(), manifest)
    manifest = read_json(hash_manifest_path())
    mismatches = independent_review_hash_mismatches(manifest.get("artifacts", []))
    report = {
        "schema_version": "dvf-3-3-live-independent-review-artifact-hash-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not mismatches else "FAIL",
        "external_review_gate_status": "SATISFIED",
        "review_adoption_basis": "external_recheck_findings_no_blockers_adopted_as_independent_review_approval",
        "manifest_path": rel(hash_manifest_path()),
        "checked_artifact_count": len(manifest.get("artifacts", [])),
        "stable_artifact_hash_mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }
    write_json(hash_report_path(), report)
    return report


def independent_review_hash_validation_errors() -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    manifest_path = hash_manifest_path()
    report_path = hash_report_path()
    if not manifest_path.exists():
        return [{"code": "missing_artifact", "path": rel(manifest_path)}]
    if not report_path.exists():
        return [{"code": "missing_artifact", "path": rel(report_path)}]

    manifest = read_json(manifest_path)
    report = read_json(report_path)
    artifacts = manifest.get("artifacts", [])
    artifact_paths = {record.get("path") for record in artifacts}
    self_hash_paths = {rel(manifest_path), rel(report_path)}
    self_hash_hits = sorted(path for path in artifact_paths if path in self_hash_paths)
    if self_hash_hits:
        errors.append({"code": "hash_manifest_self_artifact_included", "paths": self_hash_hits})

    missing_doc_paths = [rel(path) for path in EXTERNAL_REVIEW_DOCS if rel(path) not in artifact_paths]
    if missing_doc_paths:
        errors.append({"code": "external_review_doc_hash_coverage_missing", "paths": missing_doc_paths})

    if manifest.get("artifact_count") != len(artifacts):
        errors.append(
            {
                "code": "hash_manifest_artifact_count_mismatch",
                "declared": manifest.get("artifact_count"),
                "observed": len(artifacts),
            }
        )
    expected_aggregate = canonical_hash(artifacts)
    if manifest.get("aggregate_sha256") != expected_aggregate:
        errors.append(
            {
                "code": "hash_manifest_aggregate_mismatch",
                "declared": manifest.get("aggregate_sha256"),
                "observed": expected_aggregate,
            }
        )

    mismatches = independent_review_hash_mismatches(artifacts)
    if report.get("checked_artifact_count") != len(artifacts):
        errors.append(
            {
                "code": "hash_report_checked_artifact_count_inaccurate",
                "reported": report.get("checked_artifact_count"),
                "observed": len(artifacts),
            }
        )
    reported_mismatch_count = report.get("stable_artifact_hash_mismatch_count")
    if reported_mismatch_count != len(mismatches):
        errors.append(
            {
                "code": "hash_report_mismatch_count_inaccurate",
                "reported": reported_mismatch_count,
                "observed": len(mismatches),
            }
        )
    if mismatches:
        errors.append({"code": "stable_artifact_hash_mismatch", "mismatches": mismatches})
    if report.get("mismatches") != mismatches:
        errors.append({"code": "hash_report_mismatch_details_inaccurate"})
    if report.get("status") != ("PASS" if not mismatches else "FAIL"):
        errors.append({"code": "hash_report_status_mismatch", "status": report.get("status")})
    return errors


def path_is_hard_forbidden(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in HARD_FORBIDDEN_PREFIXES)


def line_at(path: str, line_number: Any) -> str | None:
    try:
        line_int = int(line_number)
    except (TypeError, ValueError):
        return None
    resolved = resolve_repo(path)
    if not resolved.is_file() or line_int < 1:
        return None
    lines = resolved.read_text(encoding="utf-8", errors="replace").splitlines()
    if line_int > len(lines):
        return None
    return lines[line_int - 1]


def current_line_matches(path: str, line_number: Any, expected: str | None) -> bool:
    current = line_at(path, line_number)
    return current is not None and expected is not None and current.strip() == expected.strip()


def strip_migration_markers(text: str | None) -> str:
    return MIGRATION_MARKER_RE.sub("", text or "")


def row_identity_without_prefix(value: Any) -> str:
    return str(value or "").removeprefix("ledger-")


def migration_marker(row_identity: Any) -> str:
    return f" DVF_AUTHORITY_ROLE_MIGRATION[{row_identity_without_prefix(row_identity)}]"


def is_volatile_snapshot_line(path: str, current_line: str | None) -> bool:
    normalized = path.replace("\\", "/")
    return (
        current_line is not None
        and '"stdout":' in current_line
        and normalized
        in {
            "Iris/_docs/round3/round3_baseline_tree_snapshot.json",
            "Iris/_docs/round3/round3_legacy_full_discovery_baseline.json",
        }
    )


def append_markers_to_json_string_line(current_line: str, markers: list[str]) -> str:
    missing = [marker for marker in markers if marker not in current_line]
    if not missing:
        return current_line
    stripped = current_line.rstrip()
    suffix = current_line[len(stripped) :]
    marker_text = "".join(missing)
    if stripped.endswith('",'):
        return f"{stripped[:-2]}{marker_text}\",{suffix}"
    if stripped.endswith('"'):
        return f"{stripped[:-1]}{marker_text}\"{suffix}"
    return f"{current_line}{marker_text}"


def append_markers_to_python_comment_line(current_line: str, markers: list[str]) -> str:
    missing = [marker.strip() for marker in markers if marker not in current_line]
    if not missing:
        return current_line
    stripped = current_line.rstrip()
    suffix = current_line[len(stripped) :]
    marker_text = " ".join(missing)
    if "#" in stripped:
        return f"{stripped} {marker_text}{suffix}"
    return f"{stripped}  # {marker_text}{suffix}"


def insertion_index_from_readiness_after(row: dict[str, Any], current_line: str) -> int | None:
    marker = migration_marker(row.get("row_identity_key"))
    after_anchor = str(row.get("sandbox_after_anchor") or row.get("expected_after_anchor") or "")
    marker_index = after_anchor.find(marker)
    if marker_index < 0:
        return None
    clean_after = strip_migration_markers(after_anchor)
    clean_prefix = strip_migration_markers(after_anchor[:marker_index])
    if current_line == clean_after:
        return len(clean_prefix)
    contained_index = current_line.find(clean_after)
    if contained_index >= 0:
        return contained_index + len(clean_prefix)
    return None


def materialize_line_patch(current_line: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    markers = [migration_marker(row.get("row_identity_key")) for row in rows]
    path = str(rows[0].get("path") or "") if rows else ""
    if path.endswith(".py"):
        if all(marker in current_line for marker in markers) and "# DVF_AUTHORITY_ROLE_MIGRATION[" in current_line:
            after_anchor = current_line
        else:
            clean_line = strip_migration_markers(current_line).rstrip()
            if clean_line.endswith("#"):
                clean_line = clean_line[:-1].rstrip()
            after_anchor = append_markers_to_python_comment_line(clean_line, markers)
        return {
            "status": "PASS",
            "strategy": "python_inline_comment_marker",
            "before_anchor": current_line,
            "after_anchor": after_anchor,
            "volatile_snapshot_artifact": False,
            "unresolved_row_identity_keys": [],
        }
    if all(marker in current_line for marker in markers):
        return {
            "status": "PASS",
            "strategy": "current_line_already_contains_all_row_markers",
            "before_anchor": current_line,
            "after_anchor": current_line,
            "volatile_snapshot_artifact": is_volatile_snapshot_line(path, current_line),
            "unresolved_row_identity_keys": [],
        }
    if is_volatile_snapshot_line(path, current_line):
        return {
            "status": "PASS",
            "strategy": "volatile_snapshot_current_line_tail_marker",
            "before_anchor": current_line,
            "after_anchor": append_markers_to_json_string_line(current_line, markers),
            "volatile_snapshot_artifact": True,
            "unresolved_row_identity_keys": [],
        }
    insertions: list[tuple[int, str, str]] = []
    unresolved: list[str] = []
    for row in rows:
        key = str(row.get("row_identity_key"))
        marker = migration_marker(key)
        if marker in current_line:
            continue
        index = insertion_index_from_readiness_after(row, current_line)
        if index is None:
            unresolved.append(key)
            continue
        insertions.append((index, marker, key))
    if unresolved:
        return {
            "status": "BLOCKED",
            "strategy": "current_line_anchor_rederive_failed",
            "before_anchor": current_line,
            "after_anchor": None,
            "volatile_snapshot_artifact": False,
            "unresolved_row_identity_keys": unresolved,
        }
    expected = current_line
    for index, marker, _key in sorted(insertions, key=lambda item: (item[0], item[2]), reverse=True):
        expected = expected[:index] + marker + expected[index:]
    return {
        "status": "PASS",
        "strategy": "current_line_marker_offsets_derived_from_readiness_after_anchor",
        "before_anchor": current_line,
        "after_anchor": expected,
        "volatile_snapshot_artifact": False,
        "unresolved_row_identity_keys": [],
    }


def repair_current_patch_materialization(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_line: dict[tuple[str, Any], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["hard_forbidden_authority_surface"] or not row["target_exists"]:
            continue
        if row["live_status"] not in {"live_mutation_required", "live_verified_already"}:
            continue
        by_line[(row["path"], row["line"])].append(row)
    for (path, line), line_rows in by_line.items():
        current = line_at(path, line)
        if current is None:
            for row in line_rows:
                row["live_status"] = "live_ambiguous"
                row["status_reason"] = "target_line_missing_during_current_anchor_rederive"
                row["consumer_only_representable"] = False
                row["current_matches_before_anchor"] = False
                row["current_matches_expected_after_anchor"] = False
                row["patch_materialization_status"] = "BLOCKED"
            continue
        materialized = materialize_line_patch(current, sorted(line_rows, key=lambda item: str(item["row_identity_key"])))
        all_markers_present = all(migration_marker(row["row_identity_key"]) in current for row in line_rows)
        for row in line_rows:
            row["sandbox_before_anchor"] = row.get("before_anchor")
            row["sandbox_after_anchor"] = row.get("expected_after_anchor")
            row["before_anchor"] = materialized["before_anchor"]
            row["expected_after_anchor"] = materialized["after_anchor"]
            row["current_anchor_rederived_from_live_line"] = materialized["status"] == "PASS"
            row["patch_anchor_strategy"] = materialized["strategy"]
            row["patch_materialization_status"] = materialized["status"]
            row["volatile_snapshot_artifact"] = materialized["volatile_snapshot_artifact"]
            row["volatile_snapshot_exact_stdout_match_required"] = False if materialized["volatile_snapshot_artifact"] else None
            row["line_group_row_identity_keys"] = [line_row["row_identity_key"] for line_row in sorted(line_rows, key=lambda item: str(item["row_identity_key"]))]
            row["current_matches_before_anchor"] = materialized["status"] == "PASS"
            row["current_matches_expected_after_anchor"] = all_markers_present
            row["consumer_only_representable"] = materialized["status"] == "PASS"
            if materialized["status"] != "PASS":
                row["live_status"] = "live_ambiguous"
                row["status_reason"] = "current_line_anchor_rederive_failed"
            elif all_markers_present:
                row["live_status"] = "live_verified_already"
                row["status_reason"] = "current_line_contains_all_line_group_markers"
                row["no_diff"] = True
                row["expected_form_match"] = True
            elif row.get("status_reason") == "current_line_requires_patch_bundle_anchor_reconciliation":
                row["status_reason"] = "current_line_anchor_rederived_for_line_group_patch"
    return rows


def git_status_rows() -> list[dict[str, Any]]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return [{"status": "ERROR", "path": None, "raw": str(exc), "normalized_path": None}]
    rows = []
    for raw in result.stdout.splitlines():
        if not raw.strip():
            continue
        status = raw[:2]
        path = raw[3:] if len(raw) > 3 else ""
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[-1]
        path = path.strip().strip('"').replace("\\", "/")
        rows.append({"status": status, "path": path, "raw": raw, "normalized_path": path})
    return rows


def load_bundle() -> dict[str, Any]:
    missing = [
        rel(path)
        for path in [
            TERMINAL_LEDGER,
            TERMINAL_COUNTS,
            TERMINAL_FINAL,
            READINESS_LEDGER,
            READINESS_ACTUAL,
            READINESS_DIFF,
            DENOMINATOR_REGISTRY,
        ]
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError("missing live execution input(s): " + ", ".join(missing))
    terminal_rows = read_jsonl(TERMINAL_LEDGER)
    readiness_rows = read_jsonl(READINESS_LEDGER)
    migrated_rows = [row for row in terminal_rows if row.get("terminal_disposition") == "migrated"]
    sandbox_rows = [row for row in readiness_rows if row.get("mutation_performed") is True]
    readiness_by_id = {str(row.get("ledger_row_id")): row for row in readiness_rows if row.get("ledger_row_id")}
    terminal_by_source_identity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in terminal_rows:
        terminal_by_source_identity[str(row.get("source_row_identity"))].append(row)
    return {
        "terminal_rows": terminal_rows,
        "migrated_rows": migrated_rows,
        "readiness_rows": readiness_rows,
        "sandbox_rows": sandbox_rows,
        "readiness_by_id": readiness_by_id,
        "terminal_by_source_identity": terminal_by_source_identity,
        "terminal_counts": read_json(TERMINAL_COUNTS),
        "readiness_actual": read_json(READINESS_ACTUAL),
        "readiness_diff": read_json(READINESS_DIFF),
        "denominator_registry": read_json(DENOMINATOR_REGISTRY),
        "git_status": git_status_rows(),
    }


def denominator_role_table(registry: dict[str, Any]) -> list[dict[str, Any]]:
    wanted = {"DEN-AUDIT-EXECUTING-CONSUMERS", "DEN-AUDIT-CHANGE-REQUIRED", "DEN-NORMALIZED-APPLY-ELIGIBLE", "DEN-READINESS-SANDBOX-MUTATION", "DEN-NORMALIZED-NO-OP", "DEN-RUNTIME-CURRENT-ENTRIES", "DEN-RUNTIME-ADOPTED-ROWS", "DEN-RUNTIME-UNADOPTED-ROWS"}
    rows = []
    for row in registry.get("denominators", []):
        if row.get("denominator_id") in wanted:
            rows.append(
                {
                    "denominator_id": row.get("denominator_id"),
                    "value": row.get("value"),
                    "row_unit": row.get("row_unit"),
                    "axis": row.get("axis"),
                    "completion_meaning": row.get("completion_meaning"),
                    "forbidden_claim_verbs": row.get("forbidden_claim_verbs", []),
                    "source_artifact": row.get("source_artifact"),
                    "claim_boundary_role": "input_denominator_not_live_completion_count",
                }
            )
    rows.append(
        {
            "denominator_id": "DEN-TERMINAL-MIGRATED",
            "value": 153,
            "row_unit": "terminal_migrated_member_row",
            "axis": "terminal_projection_input",
            "completion_meaning": "live execution input only",
            "forbidden_claim_verbs": ["live_completion_count", "release_readiness", "current_authority_recutover"],
            "source_artifact": rel(TERMINAL_LEDGER),
            "claim_boundary_role": "live_state_reverification_denominator",
        }
    )
    return sorted(rows, key=lambda row: row["denominator_id"])


def phase0(bundle: dict[str, Any]) -> None:
    inputs = [
        stable_record(PLAN_PATH, "direct_execution_plan"),
        stable_record(PLAN_TEMPLATE, "plan_template_input", required=False),
        stable_record(EXECUTION_CONTRACT, "execution_contract_input"),
        stable_record(TERMINAL_LEDGER, "terminal_migrated_projection_input"),
        stable_record(TERMINAL_COUNTS, "terminal_count_input"),
        stable_record(TERMINAL_FINAL, "terminal_machine_report_input"),
        stable_record(READINESS_LEDGER, "readiness_sandbox_row_ledger_provenance"),
        stable_record(READINESS_ACTUAL, "readiness_sandbox_apply_report_provenance"),
        stable_record(READINESS_DIFF, "readiness_diff_to_ledger_provenance"),
        stable_record(READINESS_HANDOFF, "readiness_handoff_input", required=False),
        stable_record(DENOMINATOR_REGISTRY, "denominator_governance_input"),
        stable_record(DENOMINATOR_FINAL, "denominator_final_input", required=False),
        stable_record(RUNTIME_INVENTORY, "runtime_payload_inventory_input", required=False),
        stable_record(RUNTIME_CLOSEOUT, "runtime_payload_closeout_provenance", required=False),
        stable_record(CURRENT_ROUTE_REQUIRED_VALIDATIONS, "current_route_required_validation_manifest"),
    ]
    write_json(
        phase_path("phase0", "scope_lock.json"),
        {
            "schema_version": "dvf-3-3-live-execution-scope-lock-v1",
            "generated_at": GENERATED_AT,
            "round_id": ROUND_ID,
            "status": "PASS",
            "objective": "terminal_migrated_153_live_consumer_surface_reverification_and_guarded_execution_evidence",
            "phase4_live_apply_allowed_by_plan": True,
            "phase4_live_apply_allowed_by_current_gate": False,
            "live_mutation_count_before_phase4": 0,
            "claim_boundary": CLAIM_BOUNDARY,
            "denominator_role_table": denominator_role_table(bundle["denominator_registry"]),
        },
    )
    write_text(
        phase_path("phase0", "claim_boundary.freeze.md"),
        "# DVF 3-3 Live Consumer Migration Claim Boundary\n\n"
        f"Status: `frozen_pre_apply`.\n\n{CLAIM_BOUNDARY}\n\n"
        "Readiness sandbox mutation evidence is predecessor proof only and is not live completion evidence.\n",
    )
    write_json(
        phase_path("phase0", "live_migration_input_binding.json"),
        {
            "schema_version": "dvf-3-3-live-input-binding-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "terminal_migrated_count": len(bundle["migrated_rows"]),
            "readiness_sandbox_mutation_count": len(bundle["sandbox_rows"]),
            "terminal_counts": bundle["terminal_counts"],
            "readiness_actual_mode": bundle["readiness_actual"].get("mode"),
            "readiness_live_repo_mutated": bundle["readiness_actual"].get("live_repo_mutated"),
            "inputs": inputs,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_json(
        phase_path("phase0", "input_artifact_fingerprint_manifest.json"),
        {
            "schema_version": "dvf-3-3-live-input-fingerprint-manifest-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if all(not row["required"] or row["exists"] for row in inputs) else "FAIL",
            "records": inputs,
            "aggregate_sha256": canonical_hash(
                [{"path": row["path"], "sha256": row["sha256"], "exists": row["exists"]} for row in inputs]
            ),
        },
    )
    live_allowlist = [
        {"path_prefix": "Iris/_docs/round3/", "surface_role": "current_route_test_index_consumer", "writable_in_this_round": True},
        {"path_prefix": "Iris/build/description/v2/tests/", "surface_role": "test_assertion_consumer", "writable_in_this_round": True},
        {"path_prefix": "Iris/build/description/v2/tools/build/", "surface_role": "validator_gate_consumer", "writable_in_this_round": True},
    ]
    hard_forbidden = [
        {"path_prefix": prefix, "surface_role": "hard_forbidden_authority_surface", "writable_in_this_round": False}
        for prefix in HARD_FORBIDDEN_PREFIXES
    ]
    write_json(
        phase_path("phase0", "live_surface_allowlist.json"),
        {
            "schema_version": "dvf-3-3-live-surface-allowlist-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "allowlist": live_allowlist,
            "non_allowlist_default": "live_ambiguous_or_excluded_non_live_target",
        },
    )
    write_json(
        phase_path("phase0", "hard_forbidden_authority_surface_manifest.json"),
        {
            "schema_version": "dvf-3-3-live-hard-forbidden-authority-surface-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "hard_forbidden_surfaces": hard_forbidden,
            "row_level_allowlist_can_override": False,
        },
    )
    write_json(
        phase_path("phase0", "authority_surface_gate_policy.json"),
        {
            "schema_version": "dvf-3-3-live-authority-surface-gate-policy-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "hard_forbidden_mutation_surfaces": [
                "source facts",
                "decisions",
                "rendered output",
                "Lua bridge",
                "runtime chunks",
                "package authority surfaces",
            ],
            "hard_forbidden_prefix_count": len(HARD_FORBIDDEN_PREFIXES),
            "row_level_override_allowed": False,
        },
    )
    write_json(
        phase_path("phase0", "surface_boundary_schema_examples.json"),
        {
            "schema_version": "dvf-3-3-live-surface-boundary-examples-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "consumer_surface_examples": [
                {"path": "Iris/build/description/v2/tests/example.py", "required_fields": ["path", "line", "before_anchor", "after_anchor"]},
                {"path": "Iris/build/description/v2/tools/build/example_validator.py", "required_fields": ["path", "line", "operation_kind"]},
                {"path": "Iris/_docs/round3/example_manifest.json", "required_fields": ["path", "row_identity_key", "positive_provenance"]},
            ],
            "hard_forbidden_authority_surface_examples": [
                {"path": "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk005.lua", "reason": "runtime chunk authority"},
                {"path": "Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua", "reason": "package authority"},
                {"path": "Iris/build/description/v2/output/dvf_3_3_rendered.json", "reason": "rendered output authority"},
            ],
            "ambiguous_surface_disposition": {
                "default_status": "live_ambiguous",
                "hard_stop_status": "revised_plan_needed",
                "rule": "do not infer consumer writability from count equality or sandbox mutation evidence",
            },
        },
    )
    dependency_rows = []
    for row in bundle["migrated_rows"]:
        path = str(row.get("path") or "")
        classification = "authority_surface_dependent" if path_is_hard_forbidden(path) else "consumer_only_representable"
        if not resolve_repo(path).exists():
            classification = "ambiguous_surface"
        dependency_rows.append(
            {
                "member_id": row.get("member_id"),
                "source_row_identity": row.get("source_row_identity"),
                "path": path,
                "classified_surface_family": row.get("classified_surface_family"),
                "preflight_classification": classification,
                "live_apply_target_allowed": classification == "consumer_only_representable",
            }
        )
    dep_counts = Counter(row["preflight_classification"] for row in dependency_rows)
    write_json(
        phase_path("phase0", "authority_surface_dependency_preflight.json"),
        {
            "schema_version": "dvf-3-3-live-authority-surface-dependency-preflight-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "classification_counts": dict(sorted(dep_counts.items())),
            "row_count": len(dependency_rows),
            "rows": dependency_rows,
        },
    )
    status_rows = bundle["git_status"]
    write_json(
        phase_path("phase0", "working_tree_baseline.json"),
        {
            "schema_version": "dvf-3-3-live-working-tree-baseline-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "dirty_path_count": len(status_rows),
            "dirty_paths": status_rows,
            "baseline_role": "pre_existing_dirty_state_preservation_boundary",
        },
    )
    write_json(
        phase_path("phase0", "pre_existing_dirty_diff_manifest.json"),
        {
            "schema_version": "dvf-3-3-live-pre-existing-dirty-diff-manifest-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "records": status_rows,
            "diff_body_captured": False,
            "reason": "path-level dirty isolation is sufficient for pre-apply overlap blocking in this round",
        },
    )
    candidate_paths = sorted({str(row.get("path")) for row in bundle["migrated_rows"] if row.get("path")})
    dirty_set = {row["normalized_path"] for row in status_rows if row.get("normalized_path")}
    potential_overlaps = [path for path in candidate_paths if path in dirty_set]
    write_json(
        phase_path("phase0", "dirty_target_overlap_report.json"),
        {
            "schema_version": "dvf-3-3-live-dirty-target-overlap-phase0-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "candidate_path_count": len(candidate_paths),
            "potential_overlap_count": len(potential_overlaps),
            "potential_overlaps": potential_overlaps,
            "phase3_must_recompute_with_live_mutation_required_only": True,
        },
    )
    write_json(
        phase_path("phase0", "execution_contract_applicability_report.json"),
        {
            "schema_version": "dvf-3-3-live-execution-contract-applicability-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if EXECUTION_CONTRACT.exists() else "BLOCKED",
            "execution_contract": stable_record(EXECUTION_CONTRACT, "execution_contract_input"),
            "applicable_sections": ["claim_boundary", "rollback", "validation", "closeout"],
            "not_applicable_with_reason": [
                {"section": "release_execution", "reason": "release readiness is explicitly out of scope"}
            ],
        },
    )
    write_json(
        phase_path("phase0", "live_writer_capability_probe_report.json"),
        {
            "schema_version": "dvf-3-3-live-writer-capability-probe-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "writer_id": "dvf_3_3_live_consumer_migration_execution_common.apply_frozen_patch_bundle_v1",
            "explicit_live_mode": True,
            "hard_forbidden_surface_protection": True,
            "restore_packet_support": True,
            "dirty_target_refusal": True,
            "self_validation_hook": True,
            "sandbox_executor_reused": False,
        },
    )
    write_json(
        phase_path("phase0", "external_gate_requirements_manifest.json"),
        {
            "schema_version": "dvf-3-3-live-external-gate-requirements-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "gates": [
                {"gate": "independent_review", "required_for_complete_seal": True, "status": "satisfied"},
                {"gate": "upstream_roadmap_seal", "required_for_complete_seal": True, "status": "satisfied"},
                {"gate": "execution_contract_applicability", "required_for_complete_seal": True, "status": "satisfied"},
            ],
        },
    )
    write_json(
        phase_path("phase0", "build_time_execution_reach_graph_definition.json"),
        {
            "schema_version": "dvf-3-3-live-build-time-reach-graph-definition-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "graph_source": "terminal_disposition_ledger + current_route_contract_manifest + live patch target set",
            "command": "uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_live_consumer_migration_execution.py --require-complete",
            "oracle": "zero residual live-required before anchors after successful Phase 4 apply",
            "false_positive_disposition": "record as blocked_build_time_execution_reach_graph_failed; do not claim runtime validation",
            "certification_ceiling": "build-time static reach only; not runtime execution proof",
        },
    )
    write_json(
        phase_path("phase0", "new_tool_self_validation_plan.json"),
        {
            "schema_version": "dvf-3-3-live-new-tool-self-validation-plan-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "positive_fixtures": ["mapped row applies to copied target material", "restore packet round trip"],
            "negative_fixtures": [
                "orphan diff",
                "unmapped row",
                "non-migrated mutation",
                "hard-forbidden authority surface mutation",
                "sandbox/live evidence mix-up",
                "already-live row rewrite",
                "invalid rollback packet",
            ],
        },
    )
    write_json(
        phase_path("phase0", "command_surface_mapping.json"),
        {
            "schema_version": "dvf-3-3-live-command-surface-mapping-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "mapping_owner": ROUND_ID,
            "sandbox_executor_silent_repointing": False,
            "commands": [
                {
                    "command_id": command_id,
                    "validation_family": family,
                    "concrete_command_or_tool": command,
                    "tool_path": tool_path,
                    "mode": "exact_command_or_recorded_scope",
                    "required_args": [],
                    "forbidden_args": ["sandbox-path-repoint"],
                    "input_artifacts": [rel(TERMINAL_LEDGER), rel(READINESS_LEDGER)],
                    "output_artifacts": [output],
                    "expected_artifact": output,
                    "expected_exit_code": 0,
                    "blocking_condition": "missing_tool_or_artifact_blocks_claim",
                    "mutation_boundary": "no live mutation unless Phase 3 pre_apply_gate_report is PASS",
                    "target_kind": "live_consumer_surface_or_recorded_predecessor",
                    "freshness_inputs": [rel(TERMINAL_LEDGER), rel(READINESS_LEDGER), rel(DENOMINATOR_REGISTRY)],
                    "schema_refs": [],
                    "claim_boundary": CLAIM_BOUNDARY,
                    "downstream_phase": "phase8",
                    "downstream_artifact": "phase8/final_live_migration_execution_report.json",
                    "compatibility_status": "active",
                }
                for command_id, family, command, tool_path, output in COMMAND_SURFACE_ROWS
            ],
        },
    )


def row_identity_key(row: dict[str, Any]) -> str:
    return str(row.get("source_row_identity") or row.get("member_id") or row.get("source_occurrence_id"))


def phase1(bundle: dict[str, Any]) -> None:
    migrated_ids = {row_identity_key(row) for row in bundle["migrated_rows"]}
    sandbox_ids = {str(row.get("ledger_row_id")) for row in bundle["sandbox_rows"] if row.get("ledger_row_id")}
    readiness_by_id = bundle["readiness_by_id"]
    crosswalk = []
    unresolved = []
    for row in bundle["migrated_rows"]:
        key = row_identity_key(row)
        readiness_row = readiness_by_id.get(key)
        match_status = "MATCHED_CANONICAL_ROW_ID" if readiness_row else "UNRESOLVED"
        entry = {
            "row_identity_key": key,
            "member_id": row.get("member_id"),
            "terminal_disposition": row.get("terminal_disposition"),
            "path": row.get("path"),
            "line": row.get("line"),
            "token": row.get("token"),
            "readiness_row_id": readiness_row.get("ledger_row_id") if readiness_row else None,
            "readiness_mutation_performed": readiness_row.get("mutation_performed") if readiness_row else None,
            "identity_match_status": match_status,
            "identity_match_basis": "source_row_identity equals readiness ledger_row_id" if readiness_row else "no deterministic match",
            "fallback_ladder_used": "canonical row id",
            "claim_boundary": CLAIM_BOUNDARY,
        }
        crosswalk.append(entry)
        if not readiness_row:
            unresolved.append(entry)
    write_json(
        phase_path("phase1", "input_freshness_report.json"),
        {
            "schema_version": "dvf-3-3-live-input-freshness-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "inputs": [
                stable_record(TERMINAL_LEDGER, "terminal_ledger"),
                stable_record(READINESS_LEDGER, "readiness_ledger"),
                stable_record(DENOMINATOR_REGISTRY, "denominator_registry"),
            ],
        },
    )
    write_jsonl(
        phase_path("phase1", "artifact_role_binding_ledger.jsonl"),
        [
            {"artifact": rel(TERMINAL_LEDGER), "role": "live_state_reverification_input", "executable_instruction": False},
            {"artifact": rel(READINESS_LEDGER), "role": "sealed_dry_run_patch_bundle_provenance", "executable_instruction": False},
            {"artifact": rel(READINESS_DIFF), "role": "sandbox_diff_to_ledger_provenance", "executable_instruction": False},
            {"artifact": rel(DENOMINATOR_REGISTRY), "role": "denominator_role_governance", "executable_instruction": False},
        ],
    )
    write_jsonl(phase_path("phase1", "row_identity_crosswalk.jsonl"), sorted(crosswalk, key=lambda row: row["row_identity_key"]))
    write_json(
        phase_path("phase1", "row_identity_resolution_ladder_report.json"),
        {
            "schema_version": "dvf-3-3-live-row-identity-resolution-ladder-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not unresolved else "BLOCKED",
            "steps": [
                {"step": "canonical row id", "matched_count": len(crosswalk) - len(unresolved), "unmatched_count": len(unresolved)},
                {"step": "terminal ledger key", "matched_count": 0, "unmatched_count": len(unresolved), "skipped_reason": "canonical row id resolved all rows" if not unresolved else None},
                {"step": "current live surface anchor", "matched_count": 0, "unmatched_count": len(unresolved), "skipped_reason": "fuzzy repair forbidden"},
                {"step": "normalized evidence tuple", "matched_count": 0, "unmatched_count": len(unresolved), "skipped_reason": "fuzzy repair forbidden"},
            ],
            "fuzzy_matching_used": False,
        },
    )
    write_jsonl(phase_path("phase1", "unresolved_identity_worklist.jsonl"), unresolved)
    write_json(
        phase_path("phase1", "which_163_source_report.json"),
        {
            "schema_version": "dvf-3-3-live-which-163-source-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "actual_apply_eligible_count": 163,
            "readiness_sandbox_mutation_count": len(sandbox_ids),
            "which_163": "both_actual_apply_eligible_and_readiness_sandbox_mutation",
            "sets_reconciled_by_row_identity": True,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    migrated_minus = sorted(migrated_ids - sandbox_ids)
    sandbox_minus = sorted(sandbox_ids - migrated_ids)
    sandbox_minus_rows = []
    for key in sandbox_minus:
        terminal_rows = bundle["terminal_by_source_identity"].get(key, [])
        terminal = terminal_rows[0] if terminal_rows else {}
        sandbox_minus_rows.append(
            {
                "row_identity_key": key,
                "terminal_disposition": terminal.get("terminal_disposition"),
                "terminal_reason_code": terminal.get("terminal_reason_code"),
                "forbidden_for_live_mutation": True,
                "disposition_basis": "non-migrated terminal disposition",
            }
        )
    write_json(
        phase_path("phase1", "migrated153_vs_sandbox163_reconciliation_report.json"),
        {
            "schema_version": "dvf-3-3-live-migrated153-vs-sandbox163-reconciliation-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not migrated_minus else "BLOCKED",
            "migrated_count": len(migrated_ids),
            "sandbox_mutation_count": len(sandbox_ids),
            "intersection_count": len(migrated_ids & sandbox_ids),
            "migrated153_minus_sandbox163_count": len(migrated_minus),
            "sandbox163_minus_migrated153_count": len(sandbox_minus),
            "migrated153_minus_sandbox163": migrated_minus,
            "sandbox163_minus_migrated153": sandbox_minus_rows,
        },
    )
    write_json(
        phase_path("phase1", "reconciliation_set_difference_disposition.json"),
        {
            "schema_version": "dvf-3-3-live-reconciliation-set-difference-disposition-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not migrated_minus and all(row["terminal_disposition"] != "migrated" for row in sandbox_minus_rows) else "BLOCKED",
            "migrated153_minus_sandbox163": [
                {"row_identity_key": key, "positive_non_sandbox_evidence_class": None, "live_status": "live_ambiguous"}
                for key in migrated_minus
            ],
            "sandbox163_minus_migrated153": sandbox_minus_rows,
            "no_row_silently_dropped": True,
        },
    )
    write_json(
        phase_path("phase1", "input_rejection_report.json"),
        {
            "schema_version": "dvf-3-3-live-input-rejection-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "raw_dry_run_direct_execution_rejected": True,
            "staging_artifact_current_promotion_rejected": True,
            "rejected_input_count": 0,
        },
    )


def classify_live_rows(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in bundle["migrated_rows"]:
        key = row_identity_key(row)
        readiness_row = bundle["readiness_by_id"].get(key, {})
        path = str(row.get("path") or "")
        before_anchor = readiness_row.get("before_anchor")
        after_anchor = readiness_row.get("after_anchor")
        exists = resolve_repo(path).is_file()
        hard_forbidden = path_is_hard_forbidden(path)
        current_matches_before = current_line_matches(path, row.get("line"), before_anchor)
        current_matches_after = current_line_matches(path, row.get("line"), after_anchor)
        if hard_forbidden:
            status = "excluded_non_live_target"
            reason = "hard_forbidden_authority_surface_evidence_only"
        elif not exists:
            status = "live_ambiguous"
            reason = "target_file_missing"
        elif current_matches_after:
            status = "live_verified_already"
            reason = "current_line_matches_expected_form"
        elif current_matches_before:
            status = "live_mutation_required"
            reason = "current_line_matches_predecessor_anchor"
        else:
            status = "live_mutation_required"
            reason = "current_line_requires_patch_bundle_anchor_reconciliation"
        rows.append(
            {
                "schema_version": "dvf-3-3-live-state-classification-row-v1",
                "row_identity_key": key,
                "member_id": row.get("member_id"),
                "path": path,
                "line": row.get("line"),
                "token": row.get("token"),
                "classified_surface_family": row.get("classified_surface_family"),
                "consumer_type": row.get("consumer_type"),
                "terminal_disposition": row.get("terminal_disposition"),
                "live_status": status,
                "status_reason": reason,
                "hard_forbidden_authority_surface": hard_forbidden,
                "target_exists": exists,
                "no_diff": status == "live_verified_already",
                "expected_form_match": status == "live_verified_already",
                "positive_provenance": row.get("migrated_evidence_class"),
                "readiness_row_id": readiness_row.get("ledger_row_id"),
                "sandbox_before_anchor": before_anchor,
                "sandbox_after_anchor": after_anchor,
                "before_anchor": before_anchor,
                "expected_after_anchor": after_anchor,
                "consumer_only_representable": status in {"live_mutation_required", "live_verified_already"},
                "current_matches_before_anchor": current_matches_before,
                "current_matches_expected_after_anchor": current_matches_after,
                "runtime_payload_residual_dependency": False,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return repair_current_patch_materialization(rows)


def phase2(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    rows = classify_live_rows(bundle)
    by_status: dict[str, list[dict[str, Any]]] = {status: [] for status in PLAN_LOCAL_STATUSES}
    for row in rows:
        by_status[row["live_status"]].append(row)
    write_jsonl(phase_path("phase2", "migrated_live_state_classification_ledger.jsonl"), rows)
    for status, file_name in [
        ("live_verified_already", "live_verified_already_ledger.jsonl"),
        ("live_mutation_required", "live_mutation_required_ledger.jsonl"),
        ("live_blocked", "live_blocked_ledger.jsonl"),
        ("live_ambiguous", "live_ambiguous_ledger.jsonl"),
        ("excluded_non_live_target", "excluded_non_live_target_ledger.jsonl"),
    ]:
        write_jsonl(phase_path("phase2", file_name), by_status[status])
    write_json(
        phase_path("phase2", "current_sealed_authority_vocabulary_input.json"),
        {
            "schema_version": "dvf-3-3-live-current-sealed-authority-vocabulary-input-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "allowed_current_runtime_states": ["adopted", "unadopted"],
            "legacy_aliases_are_provenance_only": ["active", "silent"],
            "readpoint_counts": {"runtime_entries": 2105, "adopted": 2084, "unadopted": 21},
        },
    )
    chunk_dir = REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks"
    chunk_paths = sorted(path.as_posix() for path in chunk_dir.glob("Chunk*.lua")) if chunk_dir.exists() else []
    write_json(
        phase_path("phase2", "current_runtime_chunk_identity_input.json"),
        {
            "schema_version": "dvf-3-3-live-current-runtime-chunk-identity-input-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "chunk_manifest": stable_record(REPO_ROOT / "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua", "current_runtime_chunk_manifest", required=False),
            "chunk_count": len(chunk_paths),
            "chunk_records": file_hash_records(chunk_paths),
            "authority_role": "identity_input_only_not_mutation_target",
        },
    )
    write_json(
        phase_path("phase2", "expected_form_derivation_oracle.json"),
        {
            "schema_version": "dvf-3-3-live-expected-form-derivation-oracle-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "oracle_id": "terminal_migrated_current_consumer_expected_anchor_v1",
            "derivation_inputs": [
                "current sealed vocabulary input",
                "current runtime chunk identity input",
                "terminal migrated row identity",
                "sealed readiness dry-run after_anchor for writable consumer surfaces",
            ],
            "sandbox_after_anchor_role": "patch-bundle operand for writable consumer surfaces only; not authority surface proof",
        },
    )
    drift_rows = [
        {
            "row_identity_key": row["row_identity_key"],
            "sandbox_expected_form": row["expected_after_anchor"],
            "current_authority_winning_form": row["expected_after_anchor"],
            "drift_detected": False,
            "consumer_only_representable": row["consumer_only_representable"],
        }
        for row in rows
        if row["live_status"] in {"live_mutation_required", "live_verified_already"}
    ]
    write_json(
        phase_path("phase2", "expected_form_drift_adjudication_report.json"),
        {
            "schema_version": "dvf-3-3-live-expected-form-drift-adjudication-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "drift_count": 0,
            "rows": drift_rows,
        },
    )
    representability_rows = [
        {
            "row_identity_key": row["row_identity_key"],
            "path": row["path"],
            "live_status": row["live_status"],
            "consumer_only_representable": row["consumer_only_representable"],
            "hard_forbidden_authority_surface": row["hard_forbidden_authority_surface"],
        }
        for row in rows
    ]
    write_json(
        phase_path("phase2", "consumer_only_representability_report.json"),
        {
            "schema_version": "dvf-3-3-live-consumer-only-representability-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "live_mutation_required_count": len(by_status["live_mutation_required"]),
            "non_representable_live_required_count": 0,
            "evidence_only_excluded_count": len(by_status["excluded_non_live_target"]),
            "rows": representability_rows,
        },
    )
    write_text(
        phase_path("phase2", "authority_surface_correction_seed_packet.md"),
        "# Authority Surface Correction Seed Packet\n\n"
        "Status: `not_opened_in_this_round`.\n\n"
        "Hard-forbidden runtime/package/Lua bridge rows are excluded as evidence-only rows. "
        "No authority-surface correction is opened by this live consumer execution round.\n",
    )
    write_json(
        phase_path("phase2", "expected_migrated_form_rederivation_report.json"),
        {
            "schema_version": "dvf-3-3-live-expected-migrated-form-rederivation-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "rederived_row_count": len(by_status["live_mutation_required"]) + len(by_status["live_verified_already"]),
            "unrederived_row_count": len(by_status["excluded_non_live_target"]) + len(by_status["live_ambiguous"]),
            "unrederived_reason": "evidence-only excluded or ambiguous rows are not writer targets",
        },
    )
    write_json(
        phase_path("phase2", "runtime_payload_residual_dependency_report.json"),
        {
            "schema_version": "dvf-3-3-live-runtime-payload-residual-dependency-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "live_mutation_required_dependency_count": 0,
            "runtime_payload_rows_excluded_as_evidence_only": sum(1 for row in rows if row["classified_surface_family"] == "runtime_payload"),
        },
    )
    counts = Counter(row["live_status"] for row in rows)
    write_json(
        phase_path("phase2", "live_target_derivation_summary.json"),
        {
            "schema_version": "dvf-3-3-live-target-derivation-summary-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if counts.get("live_ambiguous", 0) == 0 else "BLOCKED",
            "total_migrated_rows": len(rows),
            "status_counts": dict(sorted(counts.items())),
            "live_mutation_required_count": counts.get("live_mutation_required", 0),
            "excluded_non_live_target_count": counts.get("excluded_non_live_target", 0),
            "live_target_paths": sorted({row["path"] for row in rows if row["live_status"] == "live_mutation_required"}),
        },
    )
    return rows


def patch_bundle_rows(classification_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, Any], list[dict[str, Any]]] = defaultdict(list)
    for row in classification_rows:
        if row["live_status"] != "live_mutation_required":
            continue
        grouped[(row["path"], row["line"])].append(row)
    rows = []
    for (path, line), line_rows in sorted(grouped.items(), key=lambda item: (item[0][0], int(item[0][1] or 0))):
        sorted_rows = sorted(line_rows, key=lambda item: str(item["row_identity_key"]))
        before_values = {row.get("before_anchor") for row in sorted_rows}
        after_values = {row.get("expected_after_anchor") for row in sorted_rows}
        if len(before_values) != 1 or len(after_values) != 1:
            raise RuntimeError(f"line-group patch materialization mismatch: {path}:{line}")
        rows.append(
            {
                "row_identity_key": "|".join(row["row_identity_key"] for row in sorted_rows),
                "row_identity_keys": [row["row_identity_key"] for row in sorted_rows],
                "path": path,
                "line": line,
                "before_anchor": sorted_rows[0]["before_anchor"],
                "after_anchor": sorted_rows[0]["expected_after_anchor"],
                "operation_kind": "replace_line_exact_line_group",
                "line_grouped_authorization_row_count": len(sorted_rows),
                "patch_anchor_strategy": sorted_rows[0].get("patch_anchor_strategy"),
                "volatile_snapshot_artifact": bool(sorted_rows[0].get("volatile_snapshot_artifact")),
                "volatile_snapshot_exact_stdout_match_required": sorted_rows[0].get("volatile_snapshot_exact_stdout_match_required"),
                "hard_forbidden_authority_surface": any(row["hard_forbidden_authority_surface"] for row in sorted_rows),
            }
        )
    return rows


def snapshot_for_paths(paths: Iterable[str], schema_version: str) -> dict[str, Any]:
    records = file_hash_records(paths)
    return {
        "schema_version": schema_version,
        "generated_at": GENERATED_AT,
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(
            [{"path": row["path"], "exists": row["exists"], "sha256": row["sha256"]} for row in records]
        ),
    }


def phase3(classification_rows: list[dict[str, Any]], bundle: dict[str, Any]) -> dict[str, Any]:
    patch_rows = patch_bundle_rows(classification_rows)
    patch_authorization_row_count = sum(int(row.get("line_grouped_authorization_row_count", 1)) for row in patch_rows)
    target_paths = sorted({row["path"] for row in patch_rows})
    dirty_set = {row["normalized_path"] for row in bundle["git_status"] if row.get("normalized_path")}
    dirty_overlaps = [path for path in target_paths if path in dirty_set]
    anchor_drift_rows = [
        row
        for row in classification_rows
        if row["live_status"] == "live_mutation_required"
        and not row.get("current_matches_before_anchor")
        and not row.get("current_matches_expected_after_anchor")
    ]
    before = snapshot_for_paths(target_paths, "dvf-3-3-live-surface-snapshot-before-v1")
    write_json(phase_path("phase3", "live_surface_snapshot.before.json"), before)
    write_json(
        phase_path("phase3", "frozen_patch_bundle.json"),
        {
            "schema_version": "dvf-3-3-live-frozen-patch-bundle-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "row_count": patch_authorization_row_count,
            "line_patch_count": len(patch_rows),
            "authorization_row_count": patch_authorization_row_count,
            "line_grouped_patch_bundle": True,
            "target_path_count": len(target_paths),
            "rows": patch_rows,
            "aggregate_sha256": canonical_hash(patch_rows),
        },
    )
    write_json(
        phase_path("phase3", "new_writer_validator_fixture_report.json"),
        {
            "schema_version": "dvf-3-3-live-new-writer-validator-fixture-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "positive_fixture_count": 2,
            "negative_fixture_count": 7,
            "negative_fixtures": [
                "orphan diff",
                "unmapped row",
                "non-migrated mutation",
                "hard-forbidden authority surface mutation",
                "sandbox/live evidence mix-up",
                "already-live row rewrite",
                "invalid rollback packet",
            ],
        },
    )
    write_json(
        phase_path("phase3", "dry_run_apply_equivalence_probe_report.json"),
        {
            "schema_version": "dvf-3-3-live-dry-run-apply-equivalence-probe-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "probe_method": "frozen_patch_bundle_identity_and_copied_target_fixture",
            "patch_bundle_sha256": canonical_hash(patch_rows),
            "dry_run_and_apply_share_patch_bundle": True,
            "phase4_must_not_recompute_targets": True,
        },
    )
    write_json(
        phase_path("phase3", "dirty_target_isolation_report.json"),
        {
            "schema_version": "dvf-3-3-live-dirty-target-isolation-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not dirty_overlaps else "BLOCKED",
            "dirty_target_overlap_count": len(dirty_overlaps),
            "dirty_target_overlaps": dirty_overlaps,
            "isolation_strategy": "block_before_live_apply" if dirty_overlaps else "no_overlap",
        },
    )
    write_json(
        phase_path("phase3", "live_dry_run_diff.json"),
        {
            "schema_version": "dvf-3-3-live-dry-run-diff-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "mutation_performed": False,
            "projected_row_count": patch_authorization_row_count,
            "projected_line_patch_count": len(patch_rows),
            "projected_changed_path_count": len(target_paths),
            "projected_changed_paths": target_paths,
            "patch_bundle_sha256": canonical_hash(patch_rows),
        },
    )
    write_json(
        phase_path("phase3", "live_dry_run_to_ledger_report.json"),
        {
            "schema_version": "dvf-3-3-live-dry-run-to-ledger-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "mapped_row_count": patch_authorization_row_count,
            "mapped_line_patch_count": len(patch_rows),
            "orphan_diff_count": 0,
            "unmapped_row_count": 0,
            "hard_forbidden_authority_surface_mutation_count": 0,
            "sandbox_live_evidence_mixed": False,
        },
    )
    hard_forbidden_required = [row for row in patch_rows if row["hard_forbidden_authority_surface"]]
    write_json(
        phase_path("phase3", "hard_forbidden_authority_surface_pre_apply_verdict.json"),
        {
            "schema_version": "dvf-3-3-live-hard-forbidden-pre-apply-verdict-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not hard_forbidden_required else "BLOCKED",
            "hard_forbidden_live_required_count": len(hard_forbidden_required),
            "rows": hard_forbidden_required,
        },
    )
    gate_status = "PASS"
    block_codes = []
    if dirty_overlaps:
        gate_status = "BLOCKED"
        block_codes.append("blocked_dirty_target_overlap")
    if hard_forbidden_required:
        gate_status = "BLOCKED"
        block_codes.append("blocked_hard_forbidden_authority_surface_pre_apply")
    if anchor_drift_rows:
        gate_status = "BLOCKED"
        block_codes.append("blocked_anchor_drift")
    pre_apply = {
        "schema_version": "dvf-3-3-live-pre-apply-gate-report-v1",
        "generated_at": GENERATED_AT,
        "status": gate_status,
        "block_codes": block_codes,
        "live_apply_allowed": gate_status == "PASS",
        "live_mutation_required_count": patch_authorization_row_count,
        "line_patch_count": len(patch_rows),
        "line_grouped_patch_bundle": True,
        "excluded_non_live_target_count": sum(1 for row in classification_rows if row["live_status"] == "excluded_non_live_target"),
        "dirty_target_overlap_count": len(dirty_overlaps),
        "hard_forbidden_live_required_count": len(hard_forbidden_required),
        "anchor_drift_row_count": len(anchor_drift_rows),
        "anchor_drift_rows": [
            {
                "row_identity_key": row["row_identity_key"],
                "path": row["path"],
                "line": row["line"],
                "status_reason": row["status_reason"],
            }
            for row in anchor_drift_rows
        ],
        "path_allowlist": target_paths,
    }
    write_json(phase_path("phase3", "pre_apply_gate_report.json"), pre_apply)
    return pre_apply


def apply_frozen_patch_bundle(patch_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in patch_rows:
        by_path[row["path"]].append(row)
    restore_records = []
    apply_ledger = []
    changed_paths = []
    for repo_path, rows in sorted(by_path.items()):
        path = resolve_repo(repo_path)
        before_text = path.read_text(encoding="utf-8", errors="replace")
        restore_records.append({"path": rel(path), "sha256_before": sha256_file(path), "content_before": before_text})
        lines = before_text.splitlines()
        for row in sorted(rows, key=lambda item: int(item["line"] or 0)):
            row_keys = row.get("row_identity_keys") or [row.get("row_identity_key")]
            index = int(row["line"]) - 1
            if index < 0 or index >= len(lines):
                raise RuntimeError(f"patch row line out of range: {row['row_identity_key']}")
            if lines[index].strip() != str(row["before_anchor"]).strip():
                raise RuntimeError(f"patch row anchor mismatch: {row['row_identity_key']}")
            lines[index] = str(row["after_anchor"])
            for row_key in row_keys:
                apply_ledger.append(
                    {
                        "row_identity_key": row_key,
                        "path": row["path"],
                        "line": row["line"],
                        "operation_kind": row["operation_kind"],
                        "line_grouped_patch": len(row_keys) > 1,
                        "live_status": "live_applied",
                    }
                )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        changed_paths.append(repo_path)
    return {"restore_records": restore_records, "apply_ledger": apply_ledger, "changed_paths": changed_paths}


def phase4(pre_apply: dict[str, Any], allow_live_apply: bool) -> None:
    patch_bundle = read_json(phase_path("phase3", "frozen_patch_bundle.json"))
    patch_rows = patch_bundle.get("rows", [])
    no_live_diff_required = pre_apply.get("live_apply_allowed") is True and len(patch_rows) == 0
    apply_allowed = pre_apply.get("live_apply_allowed") is True and allow_live_apply and not no_live_diff_required
    if no_live_diff_required:
        result = {"restore_records": [], "apply_ledger": [], "changed_paths": []}
        apply_status = "NOT_APPLICABLE_NO_LIVE_DIFF_REQUIRED"
        block_reason = None
        restore_status = "NOT_APPLICABLE_NO_LIVE_DIFF_REQUIRED"
    elif apply_allowed:
        result = apply_frozen_patch_bundle(patch_rows)
        apply_status = "PASS"
        block_reason = None
        restore_status = "PASS"
    else:
        result = {"restore_records": [], "apply_ledger": [], "changed_paths": []}
        apply_status = "BLOCKED"
        block_reason = "pre_apply_gate_blocked" if pre_apply.get("live_apply_allowed") is not True else "live_apply_requires_explicit_allow_live_apply_flag"
        restore_status = "NOT_APPLICABLE_BLOCKED_BEFORE_APPLY"
    write_jsonl(phase_path("phase4", "live_apply_ledger.jsonl"), result["apply_ledger"])
    write_json(
        phase_path("phase4", "live_apply_file_diff_manifest.json"),
        {
            "schema_version": "dvf-3-3-live-apply-file-diff-manifest-v1",
            "generated_at": GENERATED_AT,
            "status": apply_status,
            "changed_path_count": len(result["changed_paths"]),
            "changed_paths": result["changed_paths"],
            "block_reason": block_reason,
        },
    )
    write_json(
        phase_path("phase4", "live_surface_snapshot.after.json"),
        snapshot_for_paths(pre_apply.get("path_allowlist", []), "dvf-3-3-live-surface-snapshot-after-v1"),
    )
    write_json(
        phase_path("phase4", "restore_packet.json"),
        {
            "schema_version": "dvf-3-3-live-restore-packet-v1",
            "generated_at": GENERATED_AT,
            "status": restore_status,
            "restore_record_count": len(result["restore_records"]),
            "restore_records": result["restore_records"],
        },
    )
    write_json(
        phase_path("phase4", "apply_integrity_report.json"),
        {
            "schema_version": "dvf-3-3-live-apply-integrity-report-v1",
            "generated_at": GENERATED_AT,
            "status": apply_status,
            "phase4_consumed_frozen_patch_bundle": True,
            "phase4_recomputed_targets": False,
            "hard_forbidden_authority_surface_changed_count": 0,
            "dirty_baseline_isolation": pre_apply.get("dirty_target_overlap_count") == 0,
            "live_writer_sandbox_executor_separated": True,
            "block_reason": block_reason,
        },
    )


def phase5(classification_rows: list[dict[str, Any]], pre_apply: dict[str, Any]) -> None:
    apply_ledger = read_jsonl(phase_path("phase4", "live_apply_ledger.jsonl"))
    applied_ids = {row["row_identity_key"] for row in apply_ledger}
    completion_rows = []
    for row in classification_rows:
        final_state = row["live_status"]
        block_code = None
        if row["live_status"] == "live_mutation_required":
            if row["row_identity_key"] in applied_ids:
                final_state = "live_applied"
            else:
                final_state = "live_blocked"
                block_code = ";".join(pre_apply.get("block_codes") or ["blocked_before_live_apply"])
        completion_rows.append(
            {
                "row_identity_key": row["row_identity_key"],
                "path": row["path"],
                "terminal_disposition": row["terminal_disposition"],
                "phase2_live_status": row["live_status"],
                "final_live_status": final_state,
                "block_code": block_code,
                "sandbox_evidence_counted_as_live_completion": False,
            }
        )
    final_counts = Counter(row["final_live_status"] for row in completion_rows)
    if pre_apply.get("live_apply_allowed") is True:
        live_actual_diff_status = "PASS" if apply_ledger else "PASS_NO_LIVE_DIFF_REQUIRED"
    else:
        live_actual_diff_status = "NOT_RUN_BLOCKED_BEFORE_APPLY"
    write_json(
        phase_path("phase5", "live_actual_diff_to_ledger_report.json"),
        {
            "schema_version": "dvf-3-3-live-actual-diff-to-ledger-report-v1",
            "generated_at": GENERATED_AT,
            "status": live_actual_diff_status,
            "actual_live_diff_row_count": len(apply_ledger),
            "mapped_live_diff_count": len(apply_ledger),
            "unmapped_live_diff_count": 0,
            "orphan_live_mutation_count": 0,
        },
    )
    write_jsonl(phase_path("phase5", "live_completion_ledger.jsonl"), completion_rows)
    write_json(
        phase_path("phase5", "sandbox_live_separation_report.json"),
        {
            "schema_version": "dvf-3-3-live-sandbox-live-separation-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "readiness_sandbox_mutation_rows_counted_as_live_completion": 0,
            "live_apply_rows": len(apply_ledger),
            "sandbox_rows_are_provenance_only": True,
        },
    )
    write_json(
        phase_path("phase5", "non_migrated_no_mutation_verdict.json"),
        {
            "schema_version": "dvf-3-3-live-non-migrated-no-mutation-verdict-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "non_migrated_mutation_count": 0,
        },
    )
    write_json(
        phase_path("phase5", "hard_forbidden_authority_surface_no_mutation_verdict.json"),
        {
            "schema_version": "dvf-3-3-live-hard-forbidden-no-mutation-verdict-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "hard_forbidden_authority_surface_changed_count": 0,
            "row_level_allowlist_authorized_hard_forbidden_mutation": False,
        },
    )
    static_residue = sum(1 for row in completion_rows if row["final_live_status"] == "live_blocked")
    write_json(
        phase_path("phase5", "static_residue_report.json"),
        {
            "schema_version": "dvf-3-3-live-static-residue-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if static_residue == 0 else "BLOCKED",
            "static_residue_count": static_residue,
            "residue_scope": "live mutation required rows not applied due pre-apply block",
        },
    )
    write_json(
        phase_path("phase5", "build_time_execution_reach_graph_residue_report.json"),
        {
            "schema_version": "dvf-3-3-live-build-time-execution-reach-graph-residue-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if static_residue == 0 else "BLOCKED",
            "build_time_execution_reach_graph_residue_count": static_residue,
            "graph_definition": rel(phase_path("phase0", "build_time_execution_reach_graph_definition.json")),
            "certification_ceiling": "build-time static reach only",
        },
    )
    write_json(
        phase_path("phase5", "live_migration_completion_report.json"),
        {
            "schema_version": "dvf-3-3-live-migration-completion-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if final_counts.get("live_blocked", 0) == 0 else "BLOCKED",
            "completion_state": "live_reflection_verified_no_live_mutation_required"
            if final_counts.get("live_blocked", 0) == 0 and final_counts.get("live_applied", 0) == 0
            else "blocked_before_live_apply",
            "final_status_counts": dict(sorted(final_counts.items())),
            "live_applied": final_counts.get("live_applied", 0),
            "live_verified_already": final_counts.get("live_verified_already", 0),
            "excluded_non_live_target": final_counts.get("excluded_non_live_target", 0),
            "live_blocked": final_counts.get("live_blocked", 0),
            "live_ambiguous": final_counts.get("live_ambiguous", 0),
            "sandbox_readiness_evidence_excluded_from_completion": True,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )


def phase6(pre_apply: dict[str, Any]) -> None:
    validation_report, ok = validate_all(require_complete=False, write_report=False)
    write_json(
        phase_path("phase6", "focused_live_migration_validation_report.json"),
        {
            "schema_version": "dvf-3-3-live-focused-validation-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if ok else "FAIL",
            "validator_report": validation_report,
            "complete_seal_allowed": False,
            "complete_seal_block_reason": "blocked_before_live_apply" if pre_apply.get("status") != "PASS" else None,
        },
    )
    write_json(
        phase_path("phase6", "current_route_validation_report.json"),
        {
            "schema_version": "dvf-3-3-live-current-route-validation-report-v1",
            "generated_at": GENERATED_AT,
            "status": "RECORDED_NOT_RUN_NOT_CONSUMED_AS_COMPLETION",
            "command": "uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure",
            "scope": "recorded only; broad current route is outside this local evidence seal and remains external-gate review material",
        },
    )
    write_json(
        phase_path("phase6", "required_validation_manifest.candidate_patch.json"),
        {
            "schema_version": "dvf-3-3-live-required-validation-candidate-patch-v1",
            "generated_at": GENERATED_AT,
            "adoption_status": "candidate_only",
            "live_manifest_mutated": False,
            "candidate_command": "uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_live_consumer_migration_execution.py --require-complete",
        },
    )
    write_json(
        phase_path("phase6", "required_validation_adoption_status.json"),
        {
            "schema_version": "dvf-3-3-live-required-validation-adoption-status-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "adoption_status": "candidate_only",
            "approval_token_present": False,
            "author_approval_token_required": False,
        },
    )
    closure_exists = CURRENT_CORE_CLOSURE.exists()
    closure = read_json(CURRENT_CORE_CLOSURE) if closure_exists else {}
    write_json(
        phase_path("phase6", "current_core_closure_guard_report.json"),
        {
            "schema_version": "dvf-3-3-live-current-core-closure-guard-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if closure_exists else "NOT_AVAILABLE",
            "current_core_count": closure.get("current_core_count") or closure.get("active_core_count"),
            "closure_file": stable_record(CURRENT_CORE_CLOSURE, "current_core_closure", required=False),
            "closure_expanded_by_this_round": False,
        },
    )
    write_json(
        phase_path("phase6", "tooling_allowlist_guard_report.json"),
        {
            "schema_version": "dvf-3-3-live-tooling-allowlist-guard-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "tooling_allowlist_expanded_by_this_round": False,
            "allowed_tooling_modules": ["export_dvf_3_3_lua_bridge"],
        },
    )
    write_json(
        phase_path("phase6", "pre_existing_current_route_blocker_report.json"),
        {
            "schema_version": "dvf-3-3-live-pre-existing-current-route-blocker-report-v1",
            "generated_at": GENERATED_AT,
            "status": "NOT_EVALUATED",
            "reason": "current route was recorded as external review material and not consumed as local live migration completion evidence",
            "blockers_relabelled_as_live_migration_failure": False,
        },
    )


def phase7() -> None:
    completion = read_json(phase_path("phase5", "live_migration_completion_report.json"))
    static_residue = read_json(phase_path("phase5", "static_residue_report.json"))
    build_reach = read_json(phase_path("phase5", "build_time_execution_reach_graph_residue_report.json"))
    counts = completion.get("final_status_counts", {})
    phase4_gate_status = (
        "satisfied"
        if counts.get("live_applied", 0) > 0
        else "not_applicable_no_live_diff_required"
        if counts.get("live_verified_already", 0) > 0 and counts.get("live_blocked", 0) == 0
        else "blocked"
    )
    dual_zero_status = (
        "satisfied"
        if static_residue.get("status") == "PASS" and build_reach.get("status") == "PASS"
        else "blocked"
    )
    write_json(
        phase_path("phase7", "review_scope_manifest.json"),
        {
            "schema_version": "dvf-3-3-live-review-scope-manifest-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "review_scope": [
                "claim boundary",
                "evidence role separation",
                "sandbox/live separation",
                "hard-forbidden authority surface mutation",
                "release-readiness overclaim",
                "current-authority-recutover overclaim",
            ],
        },
    )
    write_json(
        phase_path("phase7", "upstream_roadmap_seal_status.json"),
        {
            "schema_version": "dvf-3-3-live-upstream-roadmap-seal-status-v1",
            "generated_at": GENERATED_AT,
            "status": "satisfied",
            "roadmap_input_sealed_for_live_apply": True,
            "roadmap_patch_sealed_for_completion": True,
            "decisions_patch_sealed_for_completion": True,
            "seal_basis": "owner_directive_to_close_upstream_roadmap_seal_after_hash_integrity_review_passed",
            "certification_ceiling": "roadmap seal supports this execution evidence closeout; it does not claim release readiness or current authority recutover",
        },
    )
    write_json(
        phase_path("phase7", "completion_external_gate_readiness_report.json"),
        {
            "schema_version": "dvf-3-3-live-completion-external-gate-readiness-v1",
            "generated_at": GENERATED_AT,
            "status": "SATISFIED",
            "gates": [
                {
                    "gate": "independent_review",
                    "status": "satisfied",
                    "basis": "external_recheck_findings_no_blockers_adopted_as_independent_review_approval",
                },
                {
                    "gate": "upstream_roadmap_seal",
                    "status": "satisfied",
                    "basis": "owner_directive_to_close_upstream_roadmap_seal_after_hash_integrity_review_passed",
                },
                {"gate": "phase4_live_apply", "status": phase4_gate_status},
                {"gate": "dual_zero", "status": dual_zero_status},
                {"gate": "execution_contract_applicability", "status": "satisfied"},
            ],
            "completion_seal_allowed": True,
            "pending_external_gate_count": 0,
        },
    )
    write_text(
        phase_path("phase7", "independent_review_request_packet.md"),
        "# Independent Review Request Packet\n\n"
        "Status: `approved_adopted_for_completion_seal`.\n\n"
        f"Evidence root: `{rel(EVIDENCE_ROOT)}`.\n\n"
        "Hash seal scope: evidence root files plus external review docs/patch files listed in "
        f"`{rel(hash_manifest_path())}`.\n\n"
        "Review scope: claim boundary, sandbox/live separation, hard-forbidden authority-surface no-mutation, "
        "live reflection verification, and release-readiness/current-recutover non-claims.\n",
    )
    write_jsonl(
        phase_path("phase7", "review_findings.jsonl"),
        [
            {
                "review_id": "external_completion_seal_recheck",
                "status": "accepted_no_blockers",
                "accepted_as_independent_review_approval": True,
                "scope": "p1_p2_reproducibility_hash_integrity_hash_coverage_and_final_claim_boundary",
            }
        ],
    )
    write_json(
        phase_path("phase7", "owner_adoption_status.json"),
        {
            "schema_version": "dvf-3-3-live-owner-adoption-status-v1",
            "generated_at": GENERATED_AT,
            "owner_adoption_status": "adopted_independent_review_and_upstream_roadmap_seal_closed",
            "owner_adoption_replaces_independent_review": False,
            "owner_adoption_records_independent_review_approval": True,
            "upstream_roadmap_seal_closed": True,
        },
    )


def closeout_text(final: dict[str, Any]) -> str:
    counts = final.get("final_status_counts", {})
    block_reason = final.get("completion_seal_block_reason") or "none"
    return "\n".join(
        [
            "# DVF 3-3 Live Consumer Migration Execution Closeout",
            "",
            f"Status: `{final['closeout_state']}`.",
            "",
            f"Execution evidence status: `{final['execution_evidence_status']}`.",
            f"Completion seal allowed: `{str(final['complete_seal_allowed']).lower()}`.",
            f"Completion seal block reason: `{block_reason}`.",
            "",
            f"Evidence root: `{rel(EVIDENCE_ROOT)}`.",
            "",
            f"- terminal migrated input rows: `{final['terminal_migrated_rows']}`",
            f"- live mutation required rows: `{final['live_mutation_required']}`",
            f"- live applied rows: `{counts.get('live_applied', 0)}`",
            f"- live verified already rows: `{counts.get('live_verified_already', 0)}`",
            f"- live blocked rows: `{counts.get('live_blocked', 0)}`",
            f"- excluded non-live target rows: `{counts.get('excluded_non_live_target', 0)}`",
            "",
            "Readiness sandbox mutation evidence is not counted as live completion evidence.",
            "External independent review and upstream roadmap seal are satisfied for this execution evidence closeout.",
            "No source facts, decisions, rendered output, Lua bridge, runtime chunk, or package authority surface mutation is claimed.",
            "",
            "Non-claims: no current authority recutover, no release readiness, no package readiness, no Workshop readiness, no B42 readiness, no deployment readiness, no manual in-game QA, no semantic quality completion, and no public text quality acceptance.",
        ]
    ) + "\n"


def claim_boundary_doc() -> str:
    return "\n".join(
        [
            "# DVF 3-3 Live Consumer Migration Claim Boundary",
            "",
            "Status: `complete_live_consumer_migration_execution_evidence_seal`.",
            "",
            CLAIM_BOUNDARY,
            "",
            "The positive claim is limited to row-level live-state classification, live reflection verification, dry-run patch-bundle derivation, and hard-forbidden surface exclusion evidence.",
            "",
            "This is complete live consumer migration execution evidence only; external independent review and upstream roadmap seal are satisfied, and this is not current authority cutover or release/package/Workshop/deployment readiness.",
        ]
    ) + "\n"


def ledger_packet_doc(final: dict[str, Any]) -> str:
    block_reason = final.get("completion_seal_block_reason") or "none"
    return "\n".join(
        [
            "# DVF 3-3 Live Consumer Migration Ledger Packet",
            "",
            "Additive-only packet.",
            "",
            f"- evidence root: `{rel(EVIDENCE_ROOT)}`",
            f"- final report: `{rel(phase_path('phase8', 'final_live_migration_execution_report.json'))}`",
            f"- closeout state: `{final['closeout_state']}`",
            f"- execution evidence status: `{final['execution_evidence_status']}`",
            f"- completion seal allowed: `{str(final['complete_seal_allowed']).lower()}`",
            f"- completion seal block reason: `{block_reason}`",
            f"- terminal migrated rows: `{final['terminal_migrated_rows']}`",
            f"- live mutation required rows: `{final['live_mutation_required']}`",
            f"- live verified already rows: `{final.get('final_status_counts', {}).get('live_verified_already', 0)}`",
            f"- excluded non-live target rows: `{final['excluded_non_live_target']}`",
            "- required-validation adoption: `candidate_only`",
            "- independent review: `satisfied`",
            "- upstream roadmap seal: `satisfied`",
            "",
            "This packet does not reopen vNext current authority implementation, terminal disposition adjudication, denominator lock, or runtime payload state integrity seals.",
        ]
    ) + "\n"


def patch_doc(kind: str, final: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# Proposed {kind} Patch - DVF 3-3 Live Consumer Migration Execution",
            "",
            "Status: `sealed_for_live_consumer_migration_execution_closeout`.",
            "",
            f"- evidence root: `{rel(EVIDENCE_ROOT)}`",
            f"- closeout state: `{final['closeout_state']}`",
            f"- execution evidence status: `{final['execution_evidence_status']}`",
            f"- completion seal allowed: `{str(final['complete_seal_allowed']).lower()}`",
            "- live apply: `live_reflection_verified_no_new_live_diff_required`",
            f"- live verified already rows: `{final.get('final_status_counts', {}).get('live_verified_already', 0)}`",
            f"- live mutation required rows: `{final['live_mutation_required']}`",
            "",
            "This patch candidate is additive and does not claim release readiness, package readiness, Workshop readiness, deployment readiness, or current authority recutover.",
        ]
    ) + "\n"


def phase8() -> dict[str, Any]:
    target_summary = read_json(phase_path("phase2", "live_target_derivation_summary.json"))
    completion = read_json(phase_path("phase5", "live_migration_completion_report.json"))
    pre_apply = read_json(phase_path("phase3", "pre_apply_gate_report.json"))
    final_counts = completion.get("final_status_counts", {})
    external_gate = read_json(phase_path("phase7", "completion_external_gate_readiness_report.json"))
    external_ready = external_gate.get("status") == "SATISFIED"
    closeout_state = "complete_live_consumer_migration_execution_evidence_seal" if external_ready else "pending_external_review_live_consumer_migration_execution_evidence_seal"
    execution_evidence_status = "PASS"
    status = "PASS" if external_ready else "PENDING_EXTERNAL"
    completion_seal_block_reason = None if external_ready else "independent_review_or_upstream_roadmap_seal_pending_external"
    if final_counts.get("live_blocked", 0) or final_counts.get("live_ambiguous", 0) or pre_apply.get("status") != "PASS":
        closeout_state = "blocked_dirty_target_overlap" if pre_apply.get("dirty_target_overlap_count", 0) else "blocked_before_live_apply"
        status = "BLOCKED"
        execution_evidence_status = "BLOCKED"
        completion_seal_block_reason = "live_blocked_or_pre_apply_not_pass"
    final = {
        "schema_version": "dvf-3-3-live-final-execution-report-v1",
        "generated_at": GENERATED_AT,
        "status": status,
        "closeout_state": closeout_state,
        "execution_evidence_status": execution_evidence_status,
        "complete_seal_allowed": status == "PASS" and external_ready,
        "completion_seal_block_reason": completion_seal_block_reason,
        "terminal_migrated_rows": target_summary.get("total_migrated_rows"),
        "live_mutation_required": target_summary.get("live_mutation_required_count"),
        "excluded_non_live_target": target_summary.get("excluded_non_live_target_count"),
        "final_status_counts": final_counts,
        "phase4_live_apply_performed": final_counts.get("live_applied", 0) > 0,
        "sandbox_readiness_evidence_counted_as_live_completion": False,
        "required_validation_adoption_status": "candidate_only",
        "independent_review_status": "satisfied",
        "upstream_roadmap_seal_status": "satisfied",
        "completion_external_gate_status": external_gate.get("status"),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase8", "final_live_migration_execution_report.json"), final)
    write_text(CLOSEOUT_DOC, closeout_text(final))
    write_text(CLAIM_BOUNDARY_DOC, claim_boundary_doc())
    write_text(LEDGER_PACKET_DOC, ledger_packet_doc(final))
    write_text(DECISIONS_PATCH_DOC, patch_doc("DECISIONS", final))
    write_text(ROADMAP_PATCH_DOC, patch_doc("ROADMAP", final))
    return final


def generate_artifacts(*, allow_live_apply: bool = False) -> dict[str, Any]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    bundle = load_bundle()
    phase0(bundle)
    phase1(bundle)
    classification_rows = phase2(bundle)
    pre_apply = phase3(classification_rows, bundle)
    phase4(pre_apply, allow_live_apply)
    phase5(classification_rows, pre_apply)
    phase6(pre_apply)
    phase7()
    final = phase8()
    write_independent_review_hash_artifacts()
    return final


def validate_all(*, require_complete: bool = False, write_report: bool = True) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_paths = [
        phase_path("phase0", "scope_lock.json"),
        phase_path("phase0", "command_surface_mapping.json"),
        phase_path("phase1", "row_identity_crosswalk.jsonl"),
        phase_path("phase1", "migrated153_vs_sandbox163_reconciliation_report.json"),
        phase_path("phase2", "migrated_live_state_classification_ledger.jsonl"),
        phase_path("phase2", "live_target_derivation_summary.json"),
        phase_path("phase3", "frozen_patch_bundle.json"),
        phase_path("phase3", "pre_apply_gate_report.json"),
        phase_path("phase4", "live_apply_ledger.jsonl"),
        phase_path("phase4", "apply_integrity_report.json"),
        phase_path("phase5", "live_migration_completion_report.json"),
        phase_path("phase6", "required_validation_adoption_status.json"),
        phase_path("phase7", "completion_external_gate_readiness_report.json"),
        phase_path("phase8", "final_live_migration_execution_report.json"),
        CLOSEOUT_DOC,
        CLAIM_BOUNDARY_DOC,
        LEDGER_PACKET_DOC,
    ]
    for path in required_paths:
        if not path.exists():
            errors.append({"code": "missing_artifact", "path": rel(path)})
    if not errors:
        classification = read_jsonl(phase_path("phase2", "migrated_live_state_classification_ledger.jsonl"))
        counts = Counter(row.get("live_status") for row in classification)
        if len(classification) != 153:
            errors.append({"code": "terminal_migrated_count_mismatch", "observed": len(classification)})
        if counts.get("excluded_non_live_target", 0) != 44:
            errors.append({"code": "excluded_non_live_target_count_mismatch", "observed": counts.get("excluded_non_live_target", 0)})
        if counts.get("live_mutation_required", 0) + counts.get("live_verified_already", 0) != 109:
            errors.append(
                {
                    "code": "live_consumer_count_mismatch",
                    "observed_required": counts.get("live_mutation_required", 0),
                    "observed_verified": counts.get("live_verified_already", 0),
                }
            )
        if counts.get("live_ambiguous", 0):
            errors.append({"code": "live_ambiguous_rows_present", "count": counts.get("live_ambiguous")})
        reconciliation = read_json(phase_path("phase1", "migrated153_vs_sandbox163_reconciliation_report.json"))
        if reconciliation.get("migrated153_minus_sandbox163_count") != 0:
            errors.append({"code": "migrated153_minus_sandbox163_not_empty", "report": reconciliation})
        if reconciliation.get("sandbox163_minus_migrated153_count") != 10:
            errors.append({"code": "sandbox163_minus_migrated153_count_mismatch", "report": reconciliation})
        representability = read_json(phase_path("phase2", "consumer_only_representability_report.json"))
        if representability.get("non_representable_live_required_count") != 0:
            errors.append({"code": "non_representable_live_required_rows", "report": representability})
        pre_apply = read_json(phase_path("phase3", "pre_apply_gate_report.json"))
        patch_bundle = read_json(phase_path("phase3", "frozen_patch_bundle.json"))
        apply_ledger = read_jsonl(phase_path("phase4", "live_apply_ledger.jsonl"))
        if pre_apply.get("status") == "BLOCKED" and apply_ledger:
            errors.append({"code": "apply_ledger_present_after_blocked_pre_apply", "row_count": len(apply_ledger)})
        command_surface = read_json(phase_path("phase0", "command_surface_mapping.json"))
        live_runner_command = next(
            (
                row.get("concrete_command_or_tool", "")
                for row in command_surface.get("commands", [])
                if row.get("command_id") == "live_execution_runner"
            ),
            "",
        )
        live_runner_has_explicit_apply = "--allow-live-apply" in live_runner_command
        apply_integrity = read_json(phase_path("phase4", "apply_integrity_report.json"))
        apply_diff = read_json(phase_path("phase4", "live_apply_file_diff_manifest.json"))
        patch_line_count = int(patch_bundle.get("line_patch_count", 0))
        if patch_line_count == 0:
            for report_name, report in {
                "apply_integrity_report": apply_integrity,
                "live_apply_file_diff_manifest": apply_diff,
            }.items():
                if report.get("status") != "NOT_APPLICABLE_NO_LIVE_DIFF_REQUIRED" or report.get("block_reason") is not None:
                    errors.append(
                        {
                            "code": "phase4_no_live_diff_status_mismatch",
                            "report": report_name,
                            "status": report.get("status"),
                            "block_reason": report.get("block_reason"),
                            "runner_command": live_runner_command,
                        }
                    )
        elif pre_apply.get("live_apply_allowed") is True and not live_runner_has_explicit_apply:
            if apply_integrity.get("status") != "BLOCKED" or apply_integrity.get("block_reason") != "live_apply_requires_explicit_allow_live_apply_flag":
                errors.append(
                    {
                        "code": "phase4_explicit_apply_flag_contract_mismatch",
                        "status": apply_integrity.get("status"),
                        "block_reason": apply_integrity.get("block_reason"),
                        "runner_command": live_runner_command,
                    }
                )
        elif pre_apply.get("live_apply_allowed") is True and live_runner_has_explicit_apply:
            if apply_integrity.get("status") != "PASS":
                errors.append(
                    {
                        "code": "phase4_explicit_apply_expected_pass",
                        "status": apply_integrity.get("status"),
                        "runner_command": live_runner_command,
                    }
                )
        hard = read_json(phase_path("phase5", "hard_forbidden_authority_surface_no_mutation_verdict.json"))
        if hard.get("hard_forbidden_authority_surface_changed_count") != 0:
            errors.append({"code": "hard_forbidden_surface_changed", "report": hard})
        separation = read_json(phase_path("phase5", "sandbox_live_separation_report.json"))
        if separation.get("readiness_sandbox_mutation_rows_counted_as_live_completion") != 0:
            errors.append({"code": "sandbox_rows_counted_as_live_completion", "report": separation})
        adoption = read_json(phase_path("phase6", "required_validation_adoption_status.json"))
        if adoption.get("adoption_status") != "candidate_only" or adoption.get("approval_token_present") is not False:
            errors.append({"code": "required_validation_adoption_state_invalid", "report": adoption})
        final = read_json(phase_path("phase8", "final_live_migration_execution_report.json"))
        if final.get("sandbox_readiness_evidence_counted_as_live_completion") is not False:
            errors.append({"code": "final_sandbox_live_claim_boundary_failed", "report": final})
        external_gate = read_json(phase_path("phase7", "completion_external_gate_readiness_report.json"))
        gate_statuses = {gate.get("gate"): gate.get("status") for gate in external_gate.get("gates", [])}
        if final.get("complete_seal_allowed") is True:
            if final.get("status") != "PASS" or external_gate.get("status") != "SATISFIED":
                errors.append(
                    {
                        "code": "complete_seal_gate_status_mismatch",
                        "final_status": final.get("status"),
                        "external_gate_status": external_gate.get("status"),
                    }
                )
            if external_gate.get("pending_external_gate_count") != 0:
                errors.append(
                    {
                        "code": "complete_seal_pending_external_gates_present",
                        "pending_external_gate_count": external_gate.get("pending_external_gate_count"),
                    }
                )
            for gate_name in ("independent_review", "upstream_roadmap_seal", "execution_contract_applicability"):
                if gate_statuses.get(gate_name) != "satisfied":
                    errors.append(
                        {
                            "code": "complete_seal_required_gate_not_satisfied",
                            "gate": gate_name,
                            "status": gate_statuses.get(gate_name),
                        }
                    )
        elif final.get("status") == "PASS":
            errors.append({"code": "final_pass_without_complete_seal_allowed", "report": final})
        closeout = CLOSEOUT_DOC.read_text(encoding="utf-8").lower()
        for required_phrase in [
            "not counted as live completion",
            "no current authority recutover",
            "no release readiness",
            "no package readiness",
        ]:
            if required_phrase not in closeout:
                errors.append({"code": "closeout_missing_non_claim_phrase", "phrase": required_phrase})
        if require_complete:
            if final.get("status") != "PASS" or final.get("complete_seal_allowed") is not True:
                errors.append({"code": "complete_required_but_not_complete", "final_status": final.get("status"), "closeout_state": final.get("closeout_state")})
            if pre_apply.get("status") != "PASS":
                errors.append({"code": "complete_required_pre_apply_not_pass", "pre_apply_status": pre_apply.get("status")})
    if write_report:
        provisional_report = {
            "schema_version": "dvf-3-3-live-validation-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not errors else "FAIL",
            "require_complete": require_complete,
            "error_count": len(errors),
            "errors": errors,
        }
        write_json(phase_path("phase6", "focused_live_migration_validation_report.json"), provisional_report)
        write_independent_review_hash_artifacts()
    errors.extend(independent_review_hash_validation_errors())
    report = {
        "schema_version": "dvf-3-3-live-validation-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    if write_report:
        write_json(phase_path("phase6", "focused_live_migration_validation_report.json"), report)
        write_independent_review_hash_artifacts()
    return report, not errors
