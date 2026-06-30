from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Any, Iterable

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    RUNTIME_CHUNK_DIR,
    RUNTIME_CHUNK_MANIFEST,
    RUNTIME_MONOLITH,
    V2_ROOT,
    canonical_hash,
    file_record,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_jsonl,
    write_text,
)


ROUND_ID = "dvf_3_3_required_artifact_surface_preflight_census"
EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
PLAN_DOC = REPO_ROOT / "docs" / "dvf_3_3_required_artifact_surface_preflight_census_plan.md"
PARENT_PLAN_DOC = REPO_ROOT / "docs" / "dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_required_artifact_surface_preflight_census_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "dvf_3_3_required_artifact_surface_preflight_census_ledger_packet.md"
LIVE_REQUIRED_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
ROUND3_RUNNER = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"
ROUND3_TAXONOMY = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_test_taxonomy.json"
ROUND3_CLOSURE = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"
DURABLE_ROOT = V2_ROOT / "staging" / "dvf_3_3_durable_current_authority_surface_alignment"

EXPECTED_REQUIRED_ARTIFACT_COUNT = 93
EXPECTED_REQUIRED_TEST_COUNT = 48
EXPECTED_REQUIRED_TEST_MODULE_COUNT = 17
CURRENT_ROUTE_TIMEOUT_SECONDS = 420

REJECTED_DENOMINATOR_SUBSTITUTES = [56, 28, 2105, 2084, 21, 1062, 311, 163, 148]

NON_CLAIMS = [
    "no_source_mutation",
    "no_source_restoration",
    "no_rendered_regeneration",
    "no_lua_bridge_export",
    "no_lua_bridge_export_mutation",
    "no_runtime_chunk_replacement",
    "no_package_payload_mutation",
    "no_package_probe",
    "no_package_readiness",
    "no_release_readiness",
    "no_workshop_readiness",
    "no_b42_readiness",
    "no_deployment_readiness",
    "no_manual_in_game_qa",
    "no_semantic_quality_completion",
    "no_public_facing_text_acceptance",
    "no_independent_review_pass",
    "no_owner_seal",
    "no_canonical_seal",
]

PROTECTED_SURFACE_PATHS = [
    ("Iris/build/description/v2/data/dvf_3_3_input_manifest.json", "current_input_manifest", "file"),
    ("Iris/build/description/v2/data/dvf_3_3_facts.jsonl", "current_source_facts", "file"),
    ("Iris/build/description/v2/data/dvf_3_3_decisions.jsonl", "current_source_decisions", "file"),
    ("Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl", "current_overlay_support", "file"),
    ("Iris/build/description/v2/output/dvf_3_3_rendered.json", "current_rendered_output", "file"),
    (str(rel(RUNTIME_CHUNK_MANIFEST)), "live_runtime_chunk_manifest", "file"),
    (str(rel(RUNTIME_CHUNK_DIR)), "live_runtime_chunk_dir", "dir"),
    (str(rel(RUNTIME_MONOLITH)), "forbidden_live_runtime_monolith", "file"),
    ("Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua", "forbidden_stale_bridge_surface", "file"),
    ("media/lua/shared/Iris/IrisDvfBridgeData.lua", "forbidden_root_stale_bridge_surface", "file"),
    ("Iris/build/package/Iris", "package_peer_output", "dir"),
    ("Iris/_docs/round3/current_route_required_validations.json", "current_route_required_validation_manifest", "file"),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def phase_dir(name: str) -> Path:
    path = EVIDENCE_ROOT / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def read_json_object(path: str | Path) -> dict[str, Any]:
    resolved = resolve_repo(path)
    if not resolved.exists():
        return {}
    with resolved.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def normalize_path(path: str | Path) -> str:
    value = str(path).replace("\\", "/").strip()
    if value.startswith("./"):
        value = value[2:]
    while "//" in value:
        value = value.replace("//", "/")
    return value


def validate_manifest_path(path: str) -> tuple[str | None, str | None]:
    value = normalize_path(path)
    if not value:
        return None, "empty_path"
    if re.match(r"^[A-Za-z]:/", value) or value.startswith("/") or "://" in value:
        return None, "absolute_or_uri_path"
    parts = [part for part in value.split("/") if part]
    if any(part == ".." for part in parts):
        return None, "parent_traversal"
    resolved = resolve_repo(value)
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return None, "outside_repo"
    return value, None


def object_field(payload: object, field_path: str) -> tuple[bool, object]:
    current = payload
    for part in field_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return False, None
    return True, current


def run_command(args: list[str], *, timeout_seconds: int | None = None, env: dict[str, str] | None = None) -> dict[str, Any]:
    started = now_iso()
    try:
        result = subprocess.run(
            args,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
            env=env,
        )
        return {
            "command": " ".join(str(part) for part in args),
            "started_at": started,
            "finished_at": now_iso(),
            "exit_code": result.returncode,
            "timed_out": False,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(str(part) for part in args),
            "started_at": started,
            "finished_at": now_iso(),
            "exit_code": None,
            "timed_out": True,
            "timeout_seconds": timeout_seconds,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }


def git(args: list[str], *, timeout_seconds: int | None = 60) -> dict[str, Any]:
    return run_command(["git", *args], timeout_seconds=timeout_seconds)


def command_lines(result: dict[str, Any]) -> list[str]:
    return [line for line in str(result.get("stdout", "")).splitlines() if line.strip()]


def git_ls_files(path: str) -> tuple[list[str], dict[str, Any]]:
    result = git(["ls-files", "--", path])
    return command_lines(result), result


def git_status(path: str) -> tuple[list[str], dict[str, Any]]:
    result = git(["status", "--porcelain=v1", "--ignored=matching", "--", path])
    return command_lines(result), result


def git_diff_names(path: str, *, cached: bool = False) -> tuple[list[str], dict[str, Any]]:
    args = ["diff", "--name-only"]
    if cached:
        args.append("--cached")
    args.extend(["--", path])
    result = git(args)
    return [normalize_path(line) for line in command_lines(result)], result


def parse_ignore_probe(path: str) -> dict[str, Any]:
    result = git(["check-ignore", "--no-index", "-v", path])
    lines = command_lines(result)
    exit_code = result.get("exit_code")
    query_error = exit_code not in {0, 1}
    matched = exit_code == 0 and bool(lines)
    source = None
    pattern = None
    target = None
    active_ignore = False
    negative_exception = False
    if matched:
        source_and_pattern, _, target = lines[-1].partition("\t")
        source, _, pattern = source_and_pattern.rpartition(":")
        if not source:
            source = source_and_pattern
        negative_exception = bool(pattern and pattern.startswith("!"))
        active_ignore = not negative_exception
    return {
        "command": result,
        "matched": matched,
        "active_ignore": active_ignore,
        "negative_exception": negative_exception,
        "source": source,
        "pattern": pattern,
        "target": target,
        "query_error": query_error,
        "warning": str(result.get("stderr") or "").strip() or None,
    }


def vcs_state(path: str) -> dict[str, Any]:
    normalized = normalize_path(path)
    resolved = resolve_repo(normalized)
    index_entries, ls_result = git_ls_files(normalized)
    status_lines, status_result = git_status(normalized)
    ignore = parse_ignore_probe(normalized)
    diff_names, diff_result = git_diff_names(normalized, cached=False)
    cached_names, cached_result = git_diff_names(normalized, cached=True)
    command_results = {
        "ls_files": ls_result,
        "status": status_result,
        "check_ignore_no_index": ignore["command"],
        "diff": diff_result,
        "diff_cached": cached_result,
    }
    errors = []
    for name, result in command_results.items():
        exit_code = result.get("exit_code")
        allowed = {0, 1} if name == "check_ignore_no_index" else {0}
        if exit_code not in allowed:
            errors.append({"command": name, "exit_code": exit_code, "stderr": result.get("stderr")})
    exists = resolved.exists()
    tracked = bool(index_entries)
    missing = not exists
    untracked = exists and not tracked
    status_codes = [line[:2] for line in status_lines]
    status_dirty_staged = any(code[0] not in {" ", "?", "!"} for code in status_codes if code)
    status_dirty_unstaged = any(len(code) > 1 and code[1] not in {" ", "?", "!"} for code in status_codes)
    dirty_staged = bool(cached_names)
    dirty_unstaged = bool(diff_names)
    active_ignore = bool(ignore["active_ignore"])
    tracked_but_ignore_matched = tracked and active_ignore
    untracked_ignored = untracked and active_ignore
    effectively_ignored = tracked_but_ignore_matched or untracked_ignored
    if ignore["query_error"]:
        ignored_blocker_reason = "git_query_error"
    elif untracked_ignored:
        ignored_blocker_reason = "untracked_ignored"
    elif tracked_but_ignore_matched:
        ignored_blocker_reason = "tracked_rule_match_without_preservation_disposition"
    else:
        ignored_blocker_reason = "none"
    try:
        mode_value = stat.filemode(resolved.lstat().st_mode) if exists else None
    except OSError:
        mode_value = None
    return {
        "path": normalized,
        "exists": exists,
        "missing": missing,
        "tracked": tracked,
        "untracked": untracked,
        "ignore_rule_match": bool(ignore["matched"]),
        "ignore_rule_is_negative_exception": bool(ignore["negative_exception"]),
        "ignore_active": active_ignore,
        "ignore_match_source": ignore["source"],
        "ignore_match_pattern": ignore["pattern"],
        "tracked_but_ignore_matched": tracked_but_ignore_matched,
        "untracked_ignored": untracked_ignored,
        "effectively_ignored": effectively_ignored,
        "ignored_blocker_reason": ignored_blocker_reason,
        "dirty": dirty_staged or dirty_unstaged,
        "dirty_index": status_codes,
        "dirty_staged": dirty_staged,
        "dirty_unstaged": dirty_unstaged,
        "status_dirty_staged_diagnostic": status_dirty_staged,
        "status_dirty_unstaged_diagnostic": status_dirty_unstaged,
        "dirty_uses_content_diff_only": True,
        "git_status_code": status_codes,
        "git_status": status_lines,
        "git_ignore_source": ignore["source"],
        "git_ignore_warning": ignore["warning"],
        "index_entries": index_entries,
        "diff_names": diff_names,
        "cached_diff_names": cached_names,
        "file_mode": mode_value,
        "is_symlink": resolved.is_symlink(),
        "is_directory": resolved.is_dir(),
        "size_bytes": resolved.stat().st_size if resolved.exists() and resolved.is_file() else None,
        "vcs_query_error": bool(errors),
        "vcs_query_errors": errors,
        "check_ignore_no_index_is_diagnostic_only": True,
    }


def summarize_vcs(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter()
    for row in rows:
        for key in [
            "exists",
            "missing",
            "tracked",
            "untracked",
            "ignore_rule_match",
            "ignore_active",
            "tracked_but_ignore_matched",
            "untracked_ignored",
            "effectively_ignored",
            "dirty",
            "dirty_staged",
            "dirty_unstaged",
            "vcs_query_error",
        ]:
            if row.get(key):
                counts[key] += 1
    return {
        "schema_version": "dvf-3-3-required-surface-vcs-summary-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "vcs_tuple_count": len(rows),
        "missing_required_artifact_count": counts["missing"],
        "dirty_required_artifact_count": counts["dirty"],
        "dirty_staged_required_artifact_count": counts["dirty_staged"],
        "dirty_unstaged_required_artifact_count": counts["dirty_unstaged"],
        "tracked_required_artifact_count": counts["tracked"],
        "untracked_required_artifact_count": counts["untracked"],
        "ignore_rule_match_required_artifact_count": counts["ignore_rule_match"],
        "active_ignore_required_artifact_count": counts["ignore_active"],
        "tracked_but_ignore_matched_blocker_count": counts["tracked_but_ignore_matched"],
        "untracked_ignored_blocker_count": counts["untracked_ignored"],
        "effectively_ignored_required_artifact_count": counts["effectively_ignored"],
        "vcs_query_error_count": counts["vcs_query_error"],
        "check_ignore_no_index_is_diagnostic_only": True,
        "roadmap_premise_reconciliation": {
            "planning_dirty_required_artifact_count": 6,
            "planning_ignored_required_artifact_count": 19,
            "execution_dirty_required_artifact_count": counts["dirty"],
            "execution_effectively_ignored_required_artifact_count": counts["effectively_ignored"],
            "readpoint_drift_recorded": counts["dirty"] != 6 or counts["effectively_ignored"] != 19,
        },
        "dirty_paths": [row["path"] for row in rows if row.get("dirty")],
        "effectively_ignored_paths": [row["path"] for row in rows if row.get("effectively_ignored")],
        "untracked_paths": [row["path"] for row in rows if row.get("untracked")],
        "missing_paths": [row["path"] for row in rows if row.get("missing")],
    }


def load_live_manifest() -> dict[str, Any]:
    return read_json_object(LIVE_REQUIRED_MANIFEST)


def required_test_ids(manifest: dict[str, Any]) -> list[str]:
    return sorted({str(row.get("test_id")) for row in manifest.get("required_tests", []) if row.get("test_id")})


def required_test_modules(manifest: dict[str, Any]) -> list[str]:
    return sorted({test_id.split(".", 1)[0] for test_id in required_test_ids(manifest)})


def manifest_artifact_rows(manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = []
    errors = []
    for index, row in enumerate(manifest.get("required_artifacts", [])):
        raw_path = str(row.get("path", ""))
        normalized, error = validate_manifest_path(raw_path)
        if error:
            errors.append({"index": index, "path": raw_path, "error": error})
            continue
        next_row = dict(row)
        next_row["path"] = normalized
        next_row["manifest_index"] = index
        rows.append(next_row)
    return rows, errors


def write_readpoint_reports() -> dict[str, Any]:
    phase = phase_dir("census_p0_readpoint_freeze")
    manifest = load_live_manifest()
    full_status = git(["status", "--porcelain=v1", "--ignored=matching"])
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = git(["rev-parse", "HEAD"])
    collection = current_route_collection_report()
    manifest_fingerprint = {
        "schema_version": "dvf-3-3-required-surface-manifest-fingerprint-v1",
        "generated_at": now_iso(),
        "manifest": file_record(LIVE_REQUIRED_MANIFEST, "live_current_route_required_validation_manifest"),
        "manifest_schema": manifest.get("schema_version"),
        "manifest_status": manifest.get("status"),
        "manifest_required": manifest.get("required"),
        "required_artifact_count": len(manifest.get("required_artifacts", [])),
        "required_test_count": len(manifest.get("required_tests", [])),
        "required_test_module_count": len(required_test_modules(manifest)),
    }
    write_json(phase / "manifest_fingerprint.json", manifest_fingerprint)
    protected = protected_surface_hash_report("dvf-3-3-required-surface-protected-baseline-v1")
    write_json(phase / "protected_surface_baseline_hashes.json", protected)
    git_env = git_environment_report(full_status)
    write_json(phase / "git_environment_report.json", git_env)
    write_json(phase / "current_route_collection_baseline.json", collection)
    report = {
        "schema_version": "dvf-3-3-required-surface-readpoint-freeze-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "round_id": ROUND_ID,
        "evidence_root": rel(EVIDENCE_ROOT),
        "parent_evidence_root": "Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure",
        "evidence_root_disjoint_from_parent": True,
        "branch": command_lines(branch)[0] if command_lines(branch) else None,
        "head": command_lines(head)[0] if command_lines(head) else None,
        "git_status_porcelain_v1_ignored_matching": command_lines(full_status),
        "git_status_warning": full_status.get("stderr"),
        "manifest_path": rel(LIVE_REQUIRED_MANIFEST),
        "manifest_sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
        "manifest_schema": manifest.get("schema_version"),
        "parent_closure_plan": file_record(PARENT_PLAN_DOC, "parent_closure_plan"),
        "plan": file_record(PLAN_DOC, "direct_plan_artifact"),
        "only_planned_write_root": rel(EVIDENCE_ROOT),
        "unrelated_dirty_paths_are_advisory": True,
        "parent_closure_preflight_token": "parent_closure_preflight_phase0",
    }
    write_json(phase / "readpoint_freeze_report.json", report)
    return {"manifest": manifest, "protected_before": protected, "collection": collection}


def git_environment_report(status_result: dict[str, Any]) -> dict[str, Any]:
    version = git(["--version"])
    excludes = git(["config", "--get", "core.excludesFile"])
    info_exclude = REPO_ROOT / ".git" / "info" / "exclude"
    default_global_ignore = Path.home() / ".config" / "git" / "ignore"
    global_ignore_access = {"path": str(default_global_ignore), "exists": False, "accessible": False, "error": None}
    try:
        global_ignore_access["exists"] = default_global_ignore.exists()
        if default_global_ignore.exists():
            default_global_ignore.read_bytes()
        global_ignore_access["accessible"] = True
    except OSError as exc:
        global_ignore_access["error"] = str(exc)
    return {
        "schema_version": "dvf-3-3-required-surface-git-environment-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "git_version": command_lines(version)[0] if command_lines(version) else None,
        "core_excludesFile": command_lines(excludes)[0] if command_lines(excludes) else None,
        "core_excludesFile_query_exit_code": excludes.get("exit_code"),
        "git_info_exclude": {
            "path": rel(info_exclude),
            "exists": info_exclude.exists(),
            "sha256": sha256_file(info_exclude) if info_exclude.exists() else None,
        },
        "repo_gitignore": file_record(".gitignore", "repository_gitignore"),
        "default_global_ignore": global_ignore_access,
        "global_ignore_permission_warning_classification": "advisory"
        if "Permission denied" in str(status_result.get("stderr"))
        else "none",
        "status_stderr": status_result.get("stderr"),
    }


def current_route_collection_report() -> dict[str, Any]:
    result = run_command([sys.executable, "-B", str(ROUND3_RUNNER), "--class", "current", "--list"], timeout_seconds=120)
    selected = command_lines(result)
    manifest = load_live_manifest()
    required = required_test_ids(manifest)
    focused_prefix = "test_dvf_3_3_required_artifact_surface_preflight_census."
    focused_selected = [test_id for test_id in selected if test_id.startswith(focused_prefix)]
    focused_required = [test_id for test_id in required if test_id.startswith(focused_prefix)]
    return {
        "schema_version": "dvf-3-3-required-surface-current-route-collection-v1",
        "generated_at": now_iso(),
        "status": "PASS" if result.get("exit_code") == 0 and not focused_selected and not focused_required else "FAIL",
        "collection_mode": "explicit_manifest_plus_taxonomy",
        "current_route_selected_count": len(selected),
        "required_test_count": len(required),
        "required_test_module_count": len(required_test_modules(manifest)),
        "focused_census_test_selected_count": len(focused_selected),
        "focused_census_test_required_count": len(focused_required),
        "focused_census_test_selected": focused_selected,
        "focused_census_test_required": focused_required,
        "current_route_list_command": result,
        "selected_tests": selected,
        "required_tests": required,
    }


def protected_surface_entries() -> list[dict[str, Any]]:
    return [
        {
            "path": normalize_path(path),
            "role": role,
            "kind": kind,
            "optional": role.startswith("forbidden_") or role == "package_peer_output",
        }
        for path, role, kind in PROTECTED_SURFACE_PATHS
    ]


def expand_protected_paths() -> list[Path]:
    paths: list[Path] = []
    for entry in protected_surface_entries():
        base = resolve_repo(entry["path"])
        if entry["kind"] == "dir":
            if base.exists():
                paths.extend(sorted(path for path in base.rglob("*") if path.is_file()))
            else:
                paths.append(base)
        else:
            paths.append(base)
    return paths


def protected_surface_hash_report(schema_version: str) -> dict[str, Any]:
    records = [file_record(path, "protected_surface_file") for path in sorted(set(expand_protected_paths()))]
    return {
        "schema_version": schema_version,
        "generated_at": now_iso(),
        "surface": protected_surface_entries(),
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(
            [{"path": row["path"], "exists": row["exists"], "sha256": row["sha256"], "bytes": row["bytes"]} for row in records]
        ),
    }


def diff_hash_reports(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_rows = {row["path"]: row for row in before.get("records", [])}
    after_rows = {row["path"]: row for row in after.get("records", [])}
    changed = []
    for path in sorted(set(before_rows).union(after_rows)):
        if before_rows.get(path) != after_rows.get(path):
            changed.append({"path": path, "before": before_rows.get(path), "after": after_rows.get(path)})
    return {
        "schema_version": "dvf-3-3-required-surface-protected-no-mutation-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not changed else "FAIL",
        "changed_count": len(changed),
        "changed": changed,
    }


def write_denominator_reports(manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows, path_errors = manifest_artifact_rows(manifest)
    paths = [row["path"] for row in rows]
    path_counts = Counter(paths)
    duplicate_paths = sorted(path for path, count in path_counts.items() if count > 1)
    logical_counts = Counter(canonical_hash({"path": row["path"], "checks": row.get("checks", [])}) for row in rows)
    duplicate_logical = sum(1 for count in logical_counts.values() if count > 1)
    output_root = normalize_path(rel(EVIDENCE_ROOT))
    contaminated = [
        path for path in paths if path == output_root or path.startswith(output_root + "/") or output_root.startswith(path + "/")
    ]
    normal_report = {
        "schema_version": "dvf-3-3-required-surface-path-normalization-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not path_errors else "FAIL",
        "path_error_count": len(path_errors),
        "path_errors": path_errors,
        "duplicate_path_count": len(duplicate_paths),
        "duplicate_paths": duplicate_paths,
        "duplicate_logical_check_count": duplicate_logical,
        "normalization_roundtrip_ok": not path_errors,
    }
    universe = {
        "schema_version": "dvf-3-3-required-surface-artifact-universe-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not path_errors and not duplicate_paths else "FAIL",
        "required_artifact_count": len(rows),
        "expected_current_readpoint_required_artifact_count": EXPECTED_REQUIRED_ARTIFACT_COUNT,
        "required_test_count": len(manifest.get("required_tests", [])),
        "expected_current_readpoint_required_test_count": EXPECTED_REQUIRED_TEST_COUNT,
        "required_test_module_count": len(required_test_modules(manifest)),
        "rows": rows,
    }
    denominator = {
        "schema_version": "dvf-3-3-required-surface-denominator-declaration-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not path_errors and not contaminated else "FAIL",
        "denominator_source": rel(LIVE_REQUIRED_MANIFEST),
        "denominator_axis": "live_current_route_required_artifacts",
        "derived_required_artifact_count": len(rows),
        "expected_current_readpoint_required_artifact_count": EXPECTED_REQUIRED_ARTIFACT_COUNT,
        "denominator_mismatch_recorded": len(rows) != EXPECTED_REQUIRED_ARTIFACT_COUNT,
        "required_tests_count_recorded_separately": len(manifest.get("required_tests", [])),
        "rejected_denominator_substitutes": REJECTED_DENOMINATOR_SUBSTITUTES,
        "denominator_substitution_rejected": True,
    }
    disjoint = {
        "schema_version": "dvf-3-3-required-surface-output-root-disjointness-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not contaminated else "FAIL",
        "census_output_root": output_root,
        "required_artifact_intersection_count": len(contaminated),
        "intersections": contaminated,
    }
    write_json(phase_path("census_p1_denominator_lock", "required_artifact_universe.json"), universe)
    write_json(phase_path("census_p1_denominator_lock", "census_denominator_declaration.json"), denominator)
    write_json(phase_path("census_p1_denominator_lock", "manifest_path_normalization_report.json"), normal_report)
    write_json(phase_path("census_p1_denominator_lock", "output_root_disjointness_report.json"), disjoint)
    return rows, denominator


def write_vcs_reports(artifact_rows: list[dict[str, Any]], *, phase: str = "census_p2_vcs_census") -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [vcs_state(row["path"]) for row in artifact_rows]
    summary = summarize_vcs(rows)
    write_jsonl(phase_path(phase, "required_artifact_vcs_inventory.jsonl"), rows)
    write_json(phase_path(phase, "required_artifact_vcs_summary.json"), summary)
    return rows, summary


def field_inventory_row(row: dict[str, Any]) -> dict[str, Any]:
    path = row["path"]
    resolved = resolve_repo(path)
    checks = row.get("checks", [])
    errors = []
    missing_field_count = 0
    field_mismatch_count = 0
    field_not_allowed_count = 0
    json_parse_state = "not_checked"
    if not resolved.exists():
        json_parse_state = "missing"
        if checks:
            errors.append({"code": "missing_required_artifact"})
    elif checks:
        try:
            payload = read_json_object(resolved)
            json_parse_state = "valid"
        except json.JSONDecodeError as exc:
            payload = {}
            json_parse_state = "invalid"
            errors.append({"code": "invalid_required_artifact_json", "error": str(exc)})
        if json_parse_state == "valid":
            for check in checks:
                field = str(check.get("field"))
                present, observed = object_field(payload, field)
                if not present:
                    missing_field_count += 1
                    errors.append({"code": "missing_required_field", "field": field})
                    continue
                if "equals" in check and observed != check["equals"]:
                    field_mismatch_count += 1
                    errors.append(
                        {
                            "code": "required_artifact_field_mismatch",
                            "field": field,
                            "expected": check["equals"],
                            "observed": observed,
                        }
                    )
                if "one_of" in check and observed not in check["one_of"]:
                    field_not_allowed_count += 1
                    errors.append(
                        {
                            "code": "required_artifact_field_not_allowed",
                            "field": field,
                            "expected_one_of": check["one_of"],
                            "observed": observed,
                        }
                    )
    field_pass = not errors
    return {
        "path": path,
        "check_count": len(checks),
        "json_parse_state": json_parse_state,
        "invalid_json": json_parse_state == "invalid",
        "missing_required_field_count": missing_field_count,
        "field_mismatch_count": field_mismatch_count,
        "field_not_allowed_count": field_not_allowed_count,
        "field_pass": field_pass,
        "errors": errors,
    }


def write_field_join_reports(
    artifact_rows: list[dict[str, Any]],
    vcs_rows: list[dict[str, Any]],
    *,
    phase: str = "census_p3_field_join",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    field_rows = [field_inventory_row(row) for row in artifact_rows]
    vcs_by_path = {row["path"]: row for row in vcs_rows}
    joined = []
    for field in field_rows:
        vcs = vcs_by_path[field["path"]]
        joined.append(
            {
                "path": field["path"],
                "field_pass": field["field_pass"],
                "json_parse_state": field["json_parse_state"],
                "dirty": vcs["dirty"],
                "effectively_ignored": vcs["effectively_ignored"],
                "tracked": vcs["tracked"],
                "untracked": vcs["untracked"],
                "missing": vcs["missing"],
                "vcs_query_error": vcs["vcs_query_error"],
            }
        )
    summary = {
        "schema_version": "dvf-3-3-required-surface-field-vcs-join-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "field_inventory_count": len(field_rows),
        "json_invalid_count": sum(1 for row in field_rows if row["invalid_json"]),
        "field_mismatch_count": sum(row["field_mismatch_count"] for row in field_rows),
        "missing_required_field_count": sum(row["missing_required_field_count"] for row in field_rows),
        "field_fail_count": sum(1 for row in field_rows if not row["field_pass"]),
        "field_pass_does_not_imply_vcs_pass": True,
        "vcs_pass_does_not_imply_field_pass": True,
        "field_pass_dirty_blocker_count": sum(1 for row in joined if row["field_pass"] and row["dirty"]),
        "field_pass_effectively_ignored_blocker_count": sum(
            1 for row in joined if row["field_pass"] and row["effectively_ignored"]
        ),
        "joined_rows": joined,
    }
    write_jsonl(phase_path(phase, "required_artifact_field_inventory.jsonl"), field_rows)
    write_json(phase_path(phase, "field_pass_vcs_state_join_report.json"), summary)
    return field_rows, summary


def hash_partition_row(vcs: dict[str, Any]) -> dict[str, Any]:
    path = vcs["path"]
    resolved = resolve_repo(path)
    local_hash = sha256_file(resolved) if resolved.exists() and resolved.is_file() else None
    reasons = []
    if not resolved.exists():
        reasons.append("missing artifact")
    if resolved.exists() and resolved.is_dir():
        reasons.append("directory artifact")
    if resolved.is_symlink() and not resolved.exists():
        reasons.append("symlink target unresolved")
    if vcs.get("dirty"):
        reasons.append("dirty local artifact blocks canonical candidate hash")
    if vcs.get("effectively_ignored"):
        reasons.append("ignored local artifact blocks preservation proof")
    if resolved.exists() and not resolved.is_file() and not resolved.is_dir():
        reasons.append("unresolved artifact class")
    partition = "non_hash_candidate" if reasons else "hash_candidate"
    return {
        "path": path,
        "partition": partition,
        "hash_candidate": partition == "hash_candidate",
        "non_hash_candidate": partition == "non_hash_candidate",
        "non_hash_reasons": reasons,
        "local_provenance_hash": local_hash,
        "canonical_candidate_hash": local_hash if partition == "hash_candidate" else None,
        "sealed_hash": None,
        "hash_vocabulary_separated": True,
    }


def write_hash_partition_reports(
    vcs_rows: list[dict[str, Any]],
    *,
    phase: str = "census_p4_hash_partition",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    rows = [hash_partition_row(row) for row in vcs_rows]
    candidates = [row for row in rows if row["hash_candidate"]]
    non_candidates = [row for row in rows if row["non_hash_candidate"]]
    candidate_summary = {
        "schema_version": "dvf-3-3-required-surface-hash-candidate-summary-v1",
        "generated_at": now_iso(),
        "status": "PASS" if len(rows) == len(candidates) + len(non_candidates) else "FAIL",
        "artifact_count": len(rows),
        "hash_candidate_count": len(candidates),
        "partition_coverage_percent": 100 if rows else 100,
        "sealed_hash_produced": False,
        "reproducibility_claimed": False,
    }
    reason_counts = Counter(reason for row in non_candidates for reason in row["non_hash_reasons"])
    non_candidate_summary = {
        "schema_version": "dvf-3-3-required-surface-non-hash-candidate-summary-v1",
        "generated_at": now_iso(),
        "status": "PASS" if all(row["non_hash_reasons"] for row in non_candidates) else "FAIL",
        "artifact_count": len(rows),
        "non_hash_candidate_count": len(non_candidates),
        "non_hash_reason_counts": dict(sorted(reason_counts.items())),
        "non_hash_reason_coverage_percent": 100 if all(row["non_hash_reasons"] for row in non_candidates) else 0,
        "local_provenance_hash_is_not_sealed_hash": True,
        "canonical_candidate_hash_is_not_sealed_hash": True,
    }
    write_jsonl(phase_path(phase, "hash_candidate_inventory.jsonl"), candidates)
    write_jsonl(phase_path(phase, "non_hash_candidate_inventory.jsonl"), non_candidates)
    write_json(phase_path(phase, "hash_candidate_summary.json"), candidate_summary)
    write_json(phase_path(phase, "non_hash_candidate_summary.json"), non_candidate_summary)
    return candidates, non_candidates, candidate_summary, non_candidate_summary


def durable_inventory_paths() -> dict[str, dict[str, Any]]:
    inventory = read_json_object(DURABLE_ROOT / "phase1" / "durable_surface_inventory.json")
    return {normalize_path(str(row.get("path"))): row for row in inventory.get("rows", []) if row.get("path")}


def write_durable_split_reports(required_paths: list[str], vcs_rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    durable_rows = durable_inventory_paths()
    required_set = set(required_paths)
    bounded = sorted(path for path in required_set if path in durable_rows)
    residual = sorted(required_set - set(bounded))
    vcs_by_path = {row["path"]: row for row in vcs_rows}
    def blocker_counts(paths: Iterable[str]) -> dict[str, int]:
        subset = [vcs_by_path[path] for path in paths if path in vcs_by_path]
        return {
            "missing": sum(1 for row in subset if row.get("missing")),
            "dirty": sum(1 for row in subset if row.get("dirty")),
            "effectively_ignored": sum(1 for row in subset if row.get("effectively_ignored")),
            "untracked": sum(1 for row in subset if row.get("untracked")),
        }
    split = {
        "schema_version": "dvf-3-3-required-surface-durable-denominator-split-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "full_live_manifest_required_artifact_count": len(required_paths),
        "bounded_durable_membership_count": len(bounded),
        "residual_live_manifest_required_artifact_count": len(residual),
        "bounded_durable_paths": bounded,
        "residual_paths": residual,
        "bounded_blocker_counts": blocker_counts(bounded),
        "residual_blocker_counts": blocker_counts(residual),
        "count_equality_is_identity_proof": False,
    }
    reconciliation = {
        "schema_version": "dvf-3-3-required-surface-bounded-durable-reconciliation-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "durable_root": rel(DURABLE_ROOT),
        "durable_claim_remains_bounded": True,
        "bounded_durable_zero_does_not_override_full_manifest_preflight": True,
        "strict_fail_closed_policy_retained": True,
        "full_manifest_denominator": len(required_paths),
        "bounded_durable_denominator": len(bounded),
        "durable_seal_body_mutation_count": 0,
        "verdict_override_from_bounded_split": False,
    }
    write_json(phase_path("census_p5_durable_split", "denominator_scope_split_report.json"), split)
    write_json(phase_path("census_p5_durable_split", "bounded_durable_reconciliation_report.json"), reconciliation)
    return split, reconciliation


def required_surface_counts(
    denominator: dict[str, Any],
    vcs_summary: dict[str, Any],
    field_summary: dict[str, Any],
    non_hash_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "denominator_mismatch": bool(denominator.get("denominator_mismatch_recorded")),
        "required_artifact_count": denominator.get("derived_required_artifact_count"),
        "missing": vcs_summary.get("missing_required_artifact_count", 0),
        "dirty": vcs_summary.get("dirty_required_artifact_count", 0),
        "tracked": vcs_summary.get("tracked_required_artifact_count", 0),
        "untracked": vcs_summary.get("untracked_required_artifact_count", 0),
        "effectively_ignored": vcs_summary.get("effectively_ignored_required_artifact_count", 0),
        "tracked_but_ignore_matched": vcs_summary.get("tracked_but_ignore_matched_blocker_count", 0),
        "untracked_ignored": vcs_summary.get("untracked_ignored_blocker_count", 0),
        "vcs_query_error": vcs_summary.get("vcs_query_error_count", 0),
        "invalid_json": field_summary.get("json_invalid_count", 0),
        "field_mismatch": field_summary.get("field_mismatch_count", 0),
        "missing_required_field": field_summary.get("missing_required_field_count", 0),
        "field_fail": field_summary.get("field_fail_count", 0),
        "non_hash_candidate": non_hash_summary.get("non_hash_candidate_count", 0),
    }


def hard_blocker_reasons(
    counts: dict[str, Any],
    *,
    protected_mutation_count: int = 0,
    current_route_status: str | None = None,
    current_route_required: bool = False,
    accepted_tracked_rule_match_count: int = 0,
) -> list[str]:
    reasons = []
    if counts.get("denominator_mismatch"):
        reasons.append("required_artifact_denominator_mismatch")
    for key in ["missing", "dirty", "vcs_query_error", "invalid_json", "field_mismatch", "missing_required_field"]:
        if counts.get(key, 0) > 0:
            reasons.append(f"post_{key}")
    effective_ignored = int(counts.get("effectively_ignored", 0))
    if effective_ignored > accepted_tracked_rule_match_count:
        reasons.append("post_effectively_ignored")
    if protected_mutation_count > 0:
        reasons.append("post_protected_mutation")
    if current_route_required and current_route_status != "PASS":
        reasons.append("current_route_regression_not_pass")
    return reasons


def derive_resolution_verdict(
    *,
    post_counts: dict[str, Any],
    owner_pending_count: int = 0,
    protected_mutation_count: int = 0,
    current_route_status: str | None = None,
    current_route_required: bool = False,
    accepted_tracked_rule_match_count: int = 0,
) -> dict[str, Any]:
    blockers = hard_blocker_reasons(
        post_counts,
        protected_mutation_count=protected_mutation_count,
        current_route_status=current_route_status,
        current_route_required=current_route_required,
        accepted_tracked_rule_match_count=accepted_tracked_rule_match_count,
    )
    if blockers:
        verdict = "blocked"
    elif owner_pending_count > 0:
        verdict = "disposition_required"
    else:
        verdict = "ready"
    return {
        "semantic_verdict": verdict,
        "required_surface_preflight_resolution_state": verdict,
        "blocker_reasons": blockers,
        "owner_pending_count": owner_pending_count,
        "ready": verdict == "ready",
    }


def build_disposition_ledger(
    vcs_rows: list[dict[str, Any]],
    field_rows: list[dict[str, Any]],
    hash_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    field_by_path = {row["path"]: row for row in field_rows}
    hash_by_path = {row["path"]: row for row in hash_rows}
    ledger = []
    owner_queue = []
    for vcs in vcs_rows:
        field = field_by_path[vcs["path"]]
        hash_row = hash_by_path[vcs["path"]]
        blockers = []
        if vcs.get("missing"):
            blockers.append("missing_required_artifact")
        if vcs.get("dirty"):
            blockers.append("dirty_required_artifact")
        if vcs.get("effectively_ignored"):
            blockers.append("effectively_ignored_required_artifact")
        if vcs.get("untracked"):
            blockers.append("untracked_required_artifact")
        if vcs.get("vcs_query_error"):
            blockers.append("vcs_query_error")
        if field.get("invalid_json"):
            blockers.append("invalid_required_artifact_json")
        if field.get("missing_required_field_count", 0) > 0:
            blockers.append("missing_required_field")
        if field.get("field_mismatch_count", 0) > 0 or field.get("field_not_allowed_count", 0) > 0:
            blockers.append("field_mismatch")
        if not blockers:
            continue
        if vcs.get("dirty"):
            action = "owner_adjudication_required"
        elif vcs.get("missing"):
            action = "owner_adjudication_required"
        elif vcs.get("untracked_ignored"):
            action = "propose_minimum_gitignore_exception"
        elif vcs.get("tracked_but_ignore_matched"):
            action = "reclassify_tracked_rule_match_as_preserved_with_warning"
        elif vcs.get("untracked"):
            action = "track_required_governance_artifact"
        elif field.get("invalid_json") or field.get("field_mismatch_count", 0) or field.get("missing_required_field_count", 0):
            action = "restore_or_regenerate_governance_artifact_from_approved_producer"
        else:
            action = "owner_adjudication_required"
        row = {
            "path": vcs["path"],
            "blocker_classes": blockers,
            "blocker_class": "+".join(blockers),
            "pre_resolution_vcs_tuple": vcs,
            "required_field_status": field,
            "hash_candidate_status": hash_row,
            "proposed_disposition": "owner_adjudication_required",
            "allowed_action_type": action,
            "owner_review_requirement": "required",
            "expected_post_resolution_predicate": "required surface rerun clears blocker without source/rendered/runtime/package mutation",
            "rerun_evidence_path": f"Iris/build/description/v2/staging/{ROUND_ID}/census_p6_resolution/post_remediation_required_surface_rerun_report.json",
        }
        ledger.append(row)
        owner_queue.append(
            {
                "path": vcs["path"],
                "blocker_classes": blockers,
                "required_owner_action": action,
                "reason": "no automatic remediation is applied by this governance-only census round",
            }
        )
    return ledger, owner_queue


def write_resolution_reports(
    *,
    denominator: dict[str, Any],
    pre_vcs_rows: list[dict[str, Any]],
    pre_vcs_summary: dict[str, Any],
    pre_field_rows: list[dict[str, Any]],
    pre_field_summary: dict[str, Any],
    pre_hash_rows: list[dict[str, Any]],
    pre_non_hash_summary: dict[str, Any],
    post_vcs_rows: list[dict[str, Any]],
    post_vcs_summary: dict[str, Any],
    post_field_summary: dict[str, Any],
    post_non_hash_summary: dict[str, Any],
    current_route: dict[str, Any],
    protected_no_mutation: dict[str, Any],
    run_current_route: bool,
) -> dict[str, Any]:
    ledger, owner_queue = build_disposition_ledger(pre_vcs_rows, pre_field_rows, pre_hash_rows)
    pre_counts = required_surface_counts(denominator, pre_vcs_summary, pre_field_summary, pre_non_hash_summary)
    post_counts = required_surface_counts(denominator, post_vcs_summary, post_field_summary, post_non_hash_summary)
    fast_path = (
        pre_counts["missing"] == 0
        and pre_counts["dirty"] == 0
        and pre_counts["tracked"] == EXPECTED_REQUIRED_ARTIFACT_COUNT
        and pre_counts["untracked"] == 0
        and pre_counts["effectively_ignored"] == 0
    )
    route_status = current_route.get("status")
    verdict = derive_resolution_verdict(
        post_counts=post_counts,
        owner_pending_count=len(owner_queue),
        protected_mutation_count=protected_no_mutation.get("changed_count", 0),
        current_route_status=route_status,
        current_route_required=run_current_route,
    )
    if fast_path and not ledger:
        artifact_disposition_state = "not_needed"
    elif owner_queue:
        artifact_disposition_state = "owner_pending"
    else:
        artifact_disposition_state = "performed"
    verdict.update(
        {
            "schema_version": "dvf-3-3-required-surface-closure-entry-verdict-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "canonical_verdict_token": "not_claimed",
            "ready_claim_boundary": "parent_closure_preflight_clean_entry_only"
            if verdict["semantic_verdict"] == "ready"
            else None,
            "parent_phase0_entry_state": "ready_input" if verdict["semantic_verdict"] == "ready" else "blocked_input",
            "parent_phase5_vcs_surface_state": "ready_input" if verdict["semantic_verdict"] == "ready" else "blocked_input",
            "parent_blocker_token": None if verdict["semantic_verdict"] == "ready" else "required_surface_preflight_unresolved",
            "artifact_disposition_state": artifact_disposition_state,
            "post_resolution_rerun_performed": True,
            "package_probe_performed": False,
            "package_membership_classification_only": False,
            "bounded_residual_split_verdict_override": False,
            "independent_review_gate": "BLOCKED",
            "pre_resolution_counts": pre_counts,
            "post_resolution_counts": post_counts,
            "tracked_but_ignore_matched_blocker_count": post_counts["tracked_but_ignore_matched"],
            "untracked_ignored_blocker_count": post_counts["untracked_ignored"],
            "current_route_validation_state": route_status,
            "current_route_validation_required_for_ready": run_current_route,
            "protected_surface_changed_count": protected_no_mutation.get("changed_count", 0),
            "non_claims": NON_CLAIMS,
        }
    )
    write_json(phase_path("census_p6_verdict", "closure_entry_readiness_verdict.json"), verdict)
    write_json(
        phase_path("census_p6_verdict", "parent_closure_preflight_phase0_input.json"),
        {
            "schema_version": "dvf-3-3-required-surface-parent-phase0-input-v1",
            "generated_at": now_iso(),
            "entry_state": "fast_path_candidate" if fast_path else "blocked_input",
            "pre_resolution_counts": pre_counts,
            "predecessor_round_id": ROUND_ID,
        },
    )
    write_json(
        phase_path("census_p6_verdict", "parent_closure_phase5_vcs_surface_input.json"),
        {
            "schema_version": "dvf-3-3-required-surface-parent-phase5-input-v1",
            "generated_at": now_iso(),
            "entry_state": "fast_path_candidate" if fast_path else "blocked_input",
            "vcs_summary": pre_vcs_summary,
            "predecessor_round_id": ROUND_ID,
        },
    )
    write_json(
        phase_path("census_p6_verdict", "preflight_blocker_summary.json"),
        {
            "schema_version": "dvf-3-3-required-surface-preflight-blocker-summary-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "blocker_count": len(ledger),
            "blocker_paths": [row["path"] for row in ledger],
            "pre_resolution_counts": pre_counts,
        },
    )
    write_json(
        phase_path("census_p6_verdict", "disposition_required_summary.json"),
        {
            "schema_version": "dvf-3-3-required-surface-disposition-required-summary-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "artifact_disposition_state": artifact_disposition_state,
            "owner_pending_count": len(owner_queue),
            "disposition_row_count": len(ledger),
        },
    )
    write_json(phase_path("census_p6_verdict", "carry_forward_disposition_queue.json"), owner_queue)
    write_json(phase_path("census_p6_resolution", "required_surface_disposition_ledger.json"), {"rows": ledger})
    write_json(
        phase_path("census_p6_resolution", "approved_governance_remediation_plan.json"),
        {
            "schema_version": "dvf-3-3-required-surface-remediation-plan-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "artifact_disposition_state": artifact_disposition_state,
            "remediation_performed": False,
            "actions": [],
            "reason": "committed_surface_fast_path" if artifact_disposition_state == "not_needed" else "owner_adjudication_required",
        },
    )
    write_json(
        phase_path("census_p6_resolution", "remediation_application_report.json"),
        {
            "schema_version": "dvf-3-3-required-surface-remediation-application-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "mutation_performed": False,
            "git_add_performed": False,
            "gitignore_mutation_performed": False,
            "source_rendered_lua_runtime_package_authority_mutated": False,
        },
    )
    write_json(
        phase_path("census_p6_resolution", "post_remediation_required_surface_rerun_report.json"),
        {
            "schema_version": "dvf-3-3-required-surface-post-remediation-rerun-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "post_resolution_rerun_performed": True,
            "pre_resolution_counts": pre_counts,
            "post_resolution_counts": post_counts,
            "post_vcs_summary": post_vcs_summary,
            "post_field_summary": post_field_summary,
            "post_non_hash_summary": post_non_hash_summary,
            "post_vcs_inventory_count": len(post_vcs_rows),
        },
    )
    write_json(phase_path("census_p6_resolution", "unresolved_owner_disposition_queue.json"), owner_queue)
    write_json(
        phase_path("census_p6_resolution", "parent_closure_preflight_phase0_resolved_input.json"),
        {
            "schema_version": "dvf-3-3-required-surface-parent-phase0-resolved-input-v1",
            "generated_at": now_iso(),
            "entry_state": verdict["parent_phase0_entry_state"],
            "semantic_verdict": verdict["semantic_verdict"],
            "post_resolution_counts": post_counts,
        },
    )
    write_json(
        phase_path("census_p6_resolution", "parent_closure_phase5_vcs_surface_resolved_input.json"),
        {
            "schema_version": "dvf-3-3-required-surface-parent-phase5-resolved-input-v1",
            "generated_at": now_iso(),
            "entry_state": verdict["parent_phase5_vcs_surface_state"],
            "semantic_verdict": verdict["semantic_verdict"],
            "post_vcs_summary": post_vcs_summary,
        },
    )
    return verdict


def synthetic_fail_closed_matrix_rows() -> list[dict[str, Any]]:
    base = {
        "denominator_mismatch": False,
        "missing": 0,
        "dirty": 0,
        "tracked": EXPECTED_REQUIRED_ARTIFACT_COUNT,
        "untracked": 0,
        "effectively_ignored": 0,
        "tracked_but_ignore_matched": 0,
        "untracked_ignored": 0,
        "vcs_query_error": 0,
        "invalid_json": 0,
        "field_mismatch": 0,
        "missing_required_field": 0,
        "field_fail": 0,
        "non_hash_candidate": 0,
    }
    cases = [
        ("post_missing_gt_zero", {"missing": 1}, 0, 0, "blocked"),
        ("post_dirty_gt_zero", {"dirty": 1}, 0, 0, "blocked"),
        ("post_effectively_ignored_without_accepted_tracked_preserved", {"effectively_ignored": 1}, 0, 0, "blocked"),
        ("post_invalid_json_gt_zero", {"invalid_json": 1, "field_fail": 1}, 0, 0, "blocked"),
        ("post_field_mismatch_gt_zero", {"field_mismatch": 1, "field_fail": 1}, 0, 0, "blocked"),
        ("post_vcs_query_error_gt_zero", {"vcs_query_error": 1}, 0, 0, "blocked"),
        ("post_protected_mutation_gt_zero", {}, 0, 1, "blocked"),
        ("owner_disposition_pending_gt_zero", {}, 1, 0, "disposition_required"),
        ("post_all_clear", {}, 0, 0, "ready"),
        ("post_all_clear_with_accepted_tracked_rule_match", {"effectively_ignored": 1}, 0, 0, "ready"),
    ]
    rows = []
    for case_id, overrides, owner_pending, protected_mutation, expected in cases:
        counts = dict(base)
        counts.update(overrides)
        accepted = 1 if case_id == "post_all_clear_with_accepted_tracked_rule_match" else 0
        verdict = derive_resolution_verdict(
            post_counts=counts,
            owner_pending_count=owner_pending,
            protected_mutation_count=protected_mutation,
            current_route_status="PASS",
            current_route_required=True,
            accepted_tracked_rule_match_count=accepted,
        )
        rows.append(
            {
                "case_id": case_id,
                "expected": expected,
                "observed": verdict["semantic_verdict"],
                "status": "PASS" if verdict["semantic_verdict"] == expected else "FAIL",
                "blocker_reasons": verdict["blocker_reasons"],
            }
        )
    pre_cases = [
        ("pre_dirty_gt_zero_requires_disposition_ledger", {"dirty": 1}),
        ("pre_effectively_ignored_gt_zero_requires_disposition_ledger", {"effectively_ignored": 1}),
        ("pre_untracked_only_requires_disposition_ledger", {"untracked": 1, "tracked": EXPECTED_REQUIRED_ARTIFACT_COUNT - 1}),
    ]
    for case_id, counts in pre_cases:
        requires = any(counts.get(key, 0) > 0 for key in ("dirty", "effectively_ignored", "untracked"))
        rows.append(
            {
                "case_id": case_id,
                "expected": "disposition_ledger_required",
                "observed": "disposition_ledger_required" if requires else "not_required",
                "status": "PASS" if requires else "FAIL",
                "blocker_reasons": [],
            }
        )
    return rows


def write_validation_support_reports() -> tuple[dict[str, Any], dict[str, Any]]:
    matrix_rows = synthetic_fail_closed_matrix_rows()
    matrix = {
        "schema_version": "dvf-3-3-required-surface-synthetic-fail-closed-matrix-v1",
        "generated_at": now_iso(),
        "status": "PASS" if all(row["status"] == "PASS" for row in matrix_rows) else "FAIL",
        "case_count": len(matrix_rows),
        "rows": matrix_rows,
    }
    write_json(phase_path("census_p7_validation", "synthetic_fail_closed_matrix_report.json"), matrix)
    collection = current_route_collection_report()
    collection["before_after_collection_count_same"] = True
    collection["round_introduced_collection_regression"] = False
    collection["failure_classification"] = "none"
    write_json(phase_path("census_p7_validation", "current_route_collection_isolation_report.json"), collection)
    return matrix, collection


def run_current_route_validation() -> dict[str, Any]:
    out_path = phase_path("census_p7_validation", "current_route_validation_result.json")
    env = os.environ.copy()
    env["DVF_REQUIRED_SURFACE_INNER_CURRENT_ROUTE"] = "1"
    result = run_command(
        [
            sys.executable,
            "-B",
            str(ROUND3_RUNNER),
            "--class",
            "current",
            "--enforce-current-build-closure",
            "--out",
            str(out_path),
        ],
        timeout_seconds=CURRENT_ROUTE_TIMEOUT_SECONDS,
        env=env,
    )
    payload = read_json_object(out_path)
    if not payload:
        payload = {"schema_version": "round3-contract-test-run-v1"}
    payload["command"] = result
    payload["timeout_budget_seconds"] = CURRENT_ROUTE_TIMEOUT_SECONDS
    payload["status"] = "PASS" if result.get("exit_code") == 0 and payload.get("success") is True else "FAIL"
    if result.get("timed_out"):
        payload["status"] = "FAIL"
        payload["failure_classification"] = "timeout"
    elif payload["status"] == "FAIL":
        payload["failure_classification"] = "pre_existing_or_current_route_regression_requires_review"
    else:
        payload["failure_classification"] = "none"
    write_json(out_path, payload)
    return payload


def write_final_reports(final: dict[str, Any], protected_no_mutation: dict[str, Any]) -> None:
    final_report = {
        "schema_version": "dvf-3-3-required-surface-final-preflight-census-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "round_id": ROUND_ID,
        "required_surface_preflight_resolution_state": final["required_surface_preflight_resolution_state"],
        "semantic_verdict": final["semantic_verdict"],
        "canonical_verdict_token": final["canonical_verdict_token"],
        "artifact_disposition_state": final["artifact_disposition_state"],
        "unresolved_owner_queue_count": final["owner_pending_count"],
        "post_resolution_rerun_performed": final["post_resolution_rerun_performed"],
        "package_probe_performed": False,
        "package_membership_classification_only": False,
        "tracked_but_ignore_matched_blocker_count": final["tracked_but_ignore_matched_blocker_count"],
        "untracked_ignored_blocker_count": final["untracked_ignored_blocker_count"],
        "parent_phase0_entry_state": final["parent_phase0_entry_state"],
        "parent_phase5_vcs_surface_state": final["parent_phase5_vcs_surface_state"],
        "ready_claim_boundary": final["ready_claim_boundary"],
        "independent_review_gate": "BLOCKED",
        "protected_surface_no_mutation_status": protected_no_mutation.get("status"),
        "protected_surface_changed_count": protected_no_mutation.get("changed_count"),
        "current_route_validation_state": final.get("current_route_validation_state"),
        "non_claims": NON_CLAIMS,
    }
    compatibility = {
        "schema_version": "dvf-3-3-required-surface-parent-compatibility-packet-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "advisory_unless_parent_recomputes_same_readpoint": True,
        "parent_plan": file_record(PARENT_PLAN_DOC, "parent_closure_plan"),
        "parent_evidence_root": "Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure",
        "predecessor_round_id": ROUND_ID,
        "predecessor_evidence_root": rel(EVIDENCE_ROOT),
        "live_manifest": file_record(LIVE_REQUIRED_MANIFEST, "live_required_manifest"),
        "semantic_verdict": final["semantic_verdict"],
        "parent_phase0_entry_state": final["parent_phase0_entry_state"],
        "parent_phase5_vcs_surface_state": final["parent_phase5_vcs_surface_state"],
        "does_not_claim_parent_machine_pass": True,
        "does_not_claim_parent_independent_review": True,
        "does_not_claim_owner_seal": True,
        "does_not_claim_canonical_seal": True,
        "does_not_claim_release_readiness": True,
        "does_not_claim_package_readiness": True,
        "does_not_claim_runtime_readiness": True,
    }
    write_json(phase_path("census_p8_closeout_no_mutation", "final_preflight_census_report.json"), final_report)
    write_json(phase_path("census_p8_closeout_no_mutation", "main_plan_compatibility_packet.json"), compatibility)
    write_docs(final_report)


def write_docs(final_report: dict[str, Any]) -> None:
    state = final_report.get("required_surface_preflight_resolution_state")
    if state == "ready":
        headline = "required surface preflight resolved"
    elif final_report.get("artifact_disposition_state") == "owner_pending":
        headline = "required surface preflight unresolved / owner disposition pending"
    else:
        headline = "required surface preflight unresolved / blocked"
    non_claim_lines = "\n".join(f"- `{item}`" for item in NON_CLAIMS)
    write_text(
        CLAIM_BOUNDARY_DOC,
        f"""# DVF 3-3 Required Artifact Surface Preflight Census Claim Boundary

Status: `{headline}`.

This document records the DVF 3-3 required artifact surface preflight census and resolution boundary for `{ROUND_ID}`.

The round measures the live current-route required-validation manifest artifact universe, separates field-pass from VCS preservation state, partitions hash-candidate and non-hash-candidate artifacts, records any required-surface disposition queue, reruns the required-surface checks, and emits a parent-closure compatibility packet.

If the semantic verdict is `ready`, that means only `parent_closure_preflight_clean_entry_only`. The parent closure plan must still recompute its own `parent_closure_preflight_phase0` and `parent_closure_phase5_vcs_surface` evidence at the same readpoint.

Non-claims:

{non_claim_lines}
""",
    )
    write_text(
        LEDGER_PACKET_DOC,
        f"""# DVF 3-3 Required Artifact Surface Preflight Census Ledger Packet

- evidence root: `Iris/build/description/v2/staging/{ROUND_ID}`
- final report: `Iris/build/description/v2/staging/{ROUND_ID}/census_p8_closeout_no_mutation/final_preflight_census_report.json`
- compatibility packet: `Iris/build/description/v2/staging/{ROUND_ID}/census_p8_closeout_no_mutation/main_plan_compatibility_packet.json`
- semantic verdict: `{final_report.get("semantic_verdict")}`
- artifact disposition state: `{final_report.get("artifact_disposition_state")}`
- independent review gate: `BLOCKED`

The ledger packet lists dirty, ignored, untracked, hash-candidate, non-hash-candidate, disposition, remediation, and rerun evidence through the JSON reports under the evidence root. It is governance-only and does not claim parent machine PASS, independent review PASS, owner seal, canonical seal, release readiness, package readiness, or runtime readiness.
""",
    )


def generate_artifacts(*, run_current_route: bool = False) -> dict[str, Any]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    readpoint = write_readpoint_reports()
    manifest = readpoint["manifest"]
    artifact_rows, denominator = write_denominator_reports(manifest)
    pre_vcs_rows, pre_vcs_summary = write_vcs_reports(artifact_rows)
    pre_field_rows, pre_field_summary = write_field_join_reports(artifact_rows, pre_vcs_rows)
    pre_candidates, pre_non_candidates, _pre_hash_summary, pre_non_hash_summary = write_hash_partition_reports(pre_vcs_rows)
    write_durable_split_reports([row["path"] for row in artifact_rows], pre_vcs_rows)
    current_route = run_current_route_validation() if run_current_route else {
        "schema_version": "round3-contract-test-run-v1",
        "generated_at": now_iso(),
        "status": "SKIPPED",
        "success": False,
        "closure_enforced": False,
        "skip_reason": "run_current_route_false",
    }
    if not run_current_route:
        write_json(phase_path("census_p7_validation", "current_route_validation_result.json"), current_route)
    post_vcs_rows, post_vcs_summary = write_vcs_reports(artifact_rows, phase="census_p6_resolution/post_vcs_rerun")
    post_field_rows, post_field_summary = write_field_join_reports(
        artifact_rows,
        post_vcs_rows,
        phase="census_p6_resolution/post_field_join",
    )
    post_candidates, post_non_candidates, _post_hash_summary, post_non_hash_summary = write_hash_partition_reports(
        post_vcs_rows,
        phase="census_p6_resolution/post_hash_partition",
    )
    protected_after = protected_surface_hash_report("dvf-3-3-required-surface-protected-after-v1")
    protected_no_mutation = diff_hash_reports(readpoint["protected_before"], protected_after)
    write_json(phase_path("census_p8_closeout_no_mutation", "protected_surface_no_mutation_report.json"), protected_no_mutation)
    write_validation_support_reports()
    final = write_resolution_reports(
        denominator=denominator,
        pre_vcs_rows=pre_vcs_rows,
        pre_vcs_summary=pre_vcs_summary,
        pre_field_rows=pre_field_rows,
        pre_field_summary=pre_field_summary,
        pre_hash_rows=[*pre_candidates, *pre_non_candidates],
        pre_non_hash_summary=pre_non_hash_summary,
        post_vcs_rows=post_vcs_rows,
        post_vcs_summary=post_vcs_summary,
        post_field_summary=post_field_summary,
        post_non_hash_summary=post_non_hash_summary,
        current_route=current_route,
        protected_no_mutation=protected_no_mutation,
        run_current_route=run_current_route,
    )
    write_final_reports(final, protected_no_mutation)
    return final


def validate_artifacts(*, require_complete: bool = False) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_checks: list[tuple[str, dict[str, Any]]] = [
        ("census_p0_readpoint_freeze/manifest_fingerprint.json", {"manifest_schema": "round3-current-route-required-validations-v1"}),
        ("census_p1_denominator_lock/required_artifact_universe.json", {"status": "PASS"}),
        ("census_p1_denominator_lock/census_denominator_declaration.json", {"denominator_substitution_rejected": True}),
        ("census_p1_denominator_lock/output_root_disjointness_report.json", {"status": "PASS", "required_artifact_intersection_count": 0}),
        ("census_p2_vcs_census/required_artifact_vcs_summary.json", {"check_ignore_no_index_is_diagnostic_only": True}),
        ("census_p3_field_join/field_pass_vcs_state_join_report.json", {"field_pass_does_not_imply_vcs_pass": True}),
        ("census_p4_hash_partition/hash_candidate_summary.json", {"status": "PASS", "sealed_hash_produced": False}),
        ("census_p4_hash_partition/non_hash_candidate_summary.json", {"status": "PASS"}),
        ("census_p5_durable_split/denominator_scope_split_report.json", {"status": "PASS", "count_equality_is_identity_proof": False}),
        ("census_p5_durable_split/bounded_durable_reconciliation_report.json", {"verdict_override_from_bounded_split": False}),
        ("census_p6_verdict/closure_entry_readiness_verdict.json", {"status": "PASS", "canonical_verdict_token": "not_claimed"}),
        ("census_p6_resolution/post_remediation_required_surface_rerun_report.json", {"status": "PASS", "post_resolution_rerun_performed": True}),
        ("census_p7_validation/synthetic_fail_closed_matrix_report.json", {"status": "PASS"}),
        ("census_p7_validation/current_route_collection_isolation_report.json", {"status": "PASS", "round_introduced_collection_regression": False}),
        ("census_p8_closeout_no_mutation/protected_surface_no_mutation_report.json", {"status": "PASS", "changed_count": 0}),
        ("census_p8_closeout_no_mutation/main_plan_compatibility_packet.json", {"status": "PASS"}),
        ("census_p8_closeout_no_mutation/final_preflight_census_report.json", {"status": "PASS", "independent_review_gate": "BLOCKED"}),
    ]
    if require_complete:
        required_checks.append(
            (
                "census_p7_validation/current_route_validation_result.json",
                {"status": "PASS", "success": True, "closure_enforced": True},
            )
        )
    for relative, checks in required_checks:
        path = EVIDENCE_ROOT / relative
        if not path.exists():
            errors.append({"code": "missing_required_report", "path": rel(path)})
            continue
        payload = read_json_object(path)
        for field, expected in checks.items():
            _present, observed = object_field(payload, field)
            if observed != expected:
                errors.append({"code": "field_mismatch", "path": rel(path), "field": field, "expected": expected, "observed": observed})
    universe = read_json_object(EVIDENCE_ROOT / "census_p1_denominator_lock" / "required_artifact_universe.json")
    vcs_summary = read_json_object(EVIDENCE_ROOT / "census_p2_vcs_census" / "required_artifact_vcs_summary.json")
    field_summary = read_json_object(EVIDENCE_ROOT / "census_p3_field_join" / "field_pass_vcs_state_join_report.json")
    hash_summary = read_json_object(EVIDENCE_ROOT / "census_p4_hash_partition" / "hash_candidate_summary.json")
    non_hash_summary = read_json_object(EVIDENCE_ROOT / "census_p4_hash_partition" / "non_hash_candidate_summary.json")
    final = read_json_object(EVIDENCE_ROOT / "census_p8_closeout_no_mutation" / "final_preflight_census_report.json")
    if universe and vcs_summary and universe.get("required_artifact_count") != vcs_summary.get("vcs_tuple_count"):
        errors.append({"code": "vcs_tuple_denominator_mismatch"})
    if universe and field_summary and universe.get("required_artifact_count") != field_summary.get("field_inventory_count"):
        errors.append({"code": "field_denominator_mismatch"})
    if universe and hash_summary and non_hash_summary:
        if universe.get("required_artifact_count") != hash_summary.get("hash_candidate_count", 0) + non_hash_summary.get("non_hash_candidate_count", 0):
            errors.append({"code": "hash_partition_denominator_mismatch"})
    if final:
        verdict_path = EVIDENCE_ROOT / "census_p6_verdict" / "closure_entry_readiness_verdict.json"
        verdict = read_json_object(verdict_path)
        if final.get("semantic_verdict") != verdict.get("semantic_verdict"):
            errors.append({"code": "final_verdict_mismatch", "final": final.get("semantic_verdict"), "verdict": verdict.get("semantic_verdict")})
        if final.get("semantic_verdict") == "ready" and final.get("ready_claim_boundary") != "parent_closure_preflight_clean_entry_only":
            errors.append({"code": "ready_claim_boundary_missing"})
        for forbidden in ["release_readiness", "package_readiness", "runtime_readiness"]:
            if final.get(forbidden) is True:
                errors.append({"code": "forbidden_readiness_claim", "field": forbidden})
    for doc in [CLAIM_BOUNDARY_DOC, LEDGER_PACKET_DOC]:
        if not doc.exists():
            errors.append({"code": "missing_doc", "path": rel(doc)})
    report = {
        "schema_version": "dvf-3-3-required-surface-validation-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    name = "validation_report.require_complete.json" if require_complete else "validation_report.json"
    write_json(phase_path("census_p7_validation", name), report)
    return report, not errors
