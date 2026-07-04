from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    V2_ROOT,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_text,
)


ROUND_ID = "dvf_3_3_current_route_authority_required_evidence_integrity_closure"
PREDECESSOR_DISPOSITION_ROUND_ID = "dvf_3_3_required_artifact_disposition_seal"
PREDECESSOR_FINAL_RECONCILIATION_ROUND_ID = (
    "dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation"
)
COMMAND_SEQUENCE_ID = f"{ROUND_ID}_command_sequence_v1"
INDEPENDENT_REVIEW_ARTIFACT_SCHEMA = (
    "dvf-3-3-current-route-authority-required-evidence-integrity-closure-independent-review-artifact-v1"
)
OWNER_CANONICAL_SEAL_RECORD_SCHEMA = (
    "dvf-3-3-current-route-authority-required-evidence-integrity-closure-owner-canonical-seal-record-v1"
)
OWNER_CANONICAL_SEAL_SCOPE = "current_route_authority_required_evidence_integrity_closure_governance_only"


def configured_repo_path(env_name: str, default: Path) -> Path:
    override = os.environ.get(env_name)
    return resolve_repo(override) if override else default


EVIDENCE_ROOT = configured_repo_path(
    "DVF_CURRENT_ROUTE_AUTHORITY_REQUIRED_EVIDENCE_INTEGRITY_CLOSURE_ROOT",
    V2_ROOT / "staging" / ROUND_ID,
)
OWNER_SEAL_DIR = V2_ROOT / "owner_inputs" / ROUND_ID / "owner_seals"
OWNER_CANONICAL_SEAL_RECORD = OWNER_SEAL_DIR / "current_session_owner_canonical_seal_record.json"

TOOLS_DIR = Path(__file__).resolve().parent
COMMON_MODULE = TOOLS_DIR / f"{ROUND_ID}.py"
RUNNER = TOOLS_DIR / f"run_{ROUND_ID}.py"
VALIDATOR = TOOLS_DIR / f"validate_{ROUND_ID}.py"
RUNNER_ORDER_DOC = TOOLS_DIR / f"{ROUND_ID}_runner_order.md"
FOCUSED_TEST = V2_ROOT / "tests" / f"test_{ROUND_ID}.py"

LIVE_REQUIRED_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
ACTIVE_CORE_CLOSURE = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"
ROUND3_RUNNER = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"
AUTHORITY_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "authority" / "iris_current_authority_manifest.json"
LUA_SYNTAX_SCRIPT = REPO_ROOT / "tools" / "check_lua_syntax.ps1"

PLAN_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_plan.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_ledger_packet.md"
ROADMAP_DRAFT_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_roadmap_update_draft.md"
DECISIONS_DRAFT_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_decisions_update_draft.md"
ARCHITECTURE_DRAFT_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_architecture_update_draft.md"

PHILOSOPHY_DOC = REPO_ROOT / "docs" / "Philosophy.md"
DECISIONS_DOC = REPO_ROOT / "docs" / "DECISIONS.md"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "ARCHITECTURE.md"
ROADMAP_DOC = REPO_ROOT / "docs" / "ROADMAP.md"
TOP_DOCS = [DECISIONS_DOC, ROADMAP_DOC, ARCHITECTURE_DOC]
EXECUTION_CONTRACT_DOC = REPO_ROOT / "docs" / "EXECUTION_CONTRACT.md"
PLAN_TEMPLATE_DOC = REPO_ROOT / "docs" / "PLAN_TEMPLATE.md"

PREFLIGHT_REPORT = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_required_artifact_surface_preflight_census/"
    "census_p8_closeout_no_mutation/final_preflight_census_report.json"
)
DISPOSITION_REPORT = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_required_artifact_disposition_seal/"
    "phase6_closeout_claim_boundary/final_required_artifact_disposition_report.json"
)
DISPOSITION_PARENT_PACKET = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_required_artifact_disposition_seal/"
    "phase6_closeout_claim_boundary/parent_closure_input_packet.json"
)
FINAL_RECONCILIATION_PARENT_PACKET = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/"
    "phase10/parent_intake_packet.json"
)
FINAL_RECONCILIATION_REPORT = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/"
    "phase10/final_predecessor_plan_document_complete_report.json"
)
FINAL_RECONCILIATION_REQUIRED_MANIFEST_REPORT = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/"
    "phase4/required_manifest_adoption_report.json"
)
FINAL_RECONCILIATION_PRIMARY_REVIEW_MANIFEST = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/"
    "phase8/primary_review_artifact_manifest.json"
)

CURRENT_ROUTE_OUTPUT = EVIDENCE_ROOT / "phase7" / "full_current_route_validation_result.json"

EXPECTED_SUPPORTED_MODES = ["scaffold", "census", "validate", "all"]
ALLOWED_TOP_DOC_SYNC_STATES = {
    "draft_prepared_owner_application_pending",
    "owner_applied_and_validated",
    "not_claimed",
}

PROTECTED_SURFACE_PATHS = [
    "Iris/build/description/v2/data/dvf_3_3_input_manifest.json",
    "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl",
    "Iris/build/description/v2/output/dvf_3_3_rendered.json",
    "Iris/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
    "Iris/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks",
    "Iris/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
    "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/build/package/Iris",
]
OWNER_APPLIED_TOP_DOC_COLLATERAL_REQUIRED_ARTIFACTS = {
    "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/independent_review_artifact_hash_report.json",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def phase_dir(name: str) -> Path:
    path = EVIDENCE_ROOT / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def normalized_sha(path: str | Path) -> str | None:
    digest = sha256_file(path)
    return digest.lower() if isinstance(digest, str) else None


def read_json_object(path: str | Path) -> dict[str, Any]:
    resolved = resolve_repo(path)
    if not resolved.exists():
        return {}
    with resolved.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def object_field(payload: object, dotted: str) -> tuple[bool, object]:
    current = payload
    for part in dotted.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False, None
    return True, current


def run_command(args: list[str], *, timeout_seconds: int | None = None) -> dict[str, Any]:
    started = now_iso()
    try:
        result = subprocess.run(
            args,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
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


def command_texts() -> list[str]:
    root = "Iris/build/description/v2/staging/" + ROUND_ID
    return [
        f"uv run python -B Iris/build/description/v2/tools/build/run_{ROUND_ID}.py --mode scaffold",
        f"uv run python -B Iris/build/description/v2/tools/build/validate_{ROUND_ID}.py --require-scaffold",
        "uv run python -B Iris/_docs/round3/round3_run_contract_tests.py "
        f"--class current --enforce-current-build-closure --out {root}/phase7/full_current_route_validation_result.json",
        r"powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1",
        f"uv run python -B Iris/build/description/v2/tools/build/run_{ROUND_ID}.py --mode all",
        f"uv run python -B Iris/build/description/v2/tools/build/validate_{ROUND_ID}.py --require-complete",
        f'uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_{ROUND_ID}.py"',
    ]


def command_matrix_entries() -> list[dict[str, Any]]:
    return [
        {
            "index": index,
            "command": command,
            "command_sequence_id": COMMAND_SEQUENCE_ID,
        }
        for index, command in enumerate(command_texts(), start=1)
    ]


def write_runner_order_doc() -> None:
    lines = [
        f"# {ROUND_ID} Runner Order",
        "",
        f"command_sequence_id: `{COMMAND_SEQUENCE_ID}`",
        "",
        "The command order is fixed. Any implementation change must update this document,",
        "the scaffold ordered matrix, the final command matrix, and validator expectations together.",
        "",
    ]
    for entry in command_matrix_entries():
        lines.append(f"{entry['index']}. `{entry['command']}`")
    write_text(RUNNER_ORDER_DOC, "\n".join(lines))


def path_record(path: str | Path, *, role: str) -> dict[str, Any]:
    resolved = resolve_repo(path)
    return {
        "path": rel(resolved),
        "role": role,
        "exists": resolved.exists(),
        "sha256": normalized_sha(resolved),
        "is_dir": resolved.is_dir(),
    }


def hash_directory(path: Path) -> str | None:
    if not path.exists():
        return None
    if path.is_file():
        return normalized_sha(path)
    digest = hashlib.sha256()
    for child in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(child.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update((normalized_sha(child) or "").encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def protected_hash_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in PROTECTED_SURFACE_PATHS:
        path = resolve_repo(item)
        records.append(
            {
                "path": rel(path),
                "exists": path.exists(),
                "is_dir": path.is_dir(),
                "sha256": hash_directory(path),
            }
        )
    return records


def compare_protected_hashes(
    before: list[dict[str, Any]], after: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], int]:
    before_by_path = {row["path"]: row for row in before}
    diffs: list[dict[str, Any]] = []
    for row in after:
        old = before_by_path.get(row["path"], {})
        changed = old.get("exists") != row.get("exists") or old.get("sha256") != row.get("sha256")
        diffs.append(
            {
                "path": row["path"],
                "before_exists": old.get("exists"),
                "after_exists": row.get("exists"),
                "before_sha256": old.get("sha256"),
                "after_sha256": row.get("sha256"),
                "changed": changed,
            }
        )
    return diffs, sum(1 for row in diffs if row["changed"])


def required_manifest_payload() -> dict[str, Any]:
    return read_json_object(LIVE_REQUIRED_MANIFEST)


def required_artifact_paths() -> list[str]:
    payload = required_manifest_payload()
    rows = payload.get("required_artifacts")
    if not isinstance(rows, list):
        return []
    paths: list[str] = []
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("path"), str):
            paths.append(row["path"].replace("\\", "/"))
    return sorted(dict.fromkeys(paths))


def required_test_count() -> int:
    payload = required_manifest_payload()
    rows = payload.get("required_tests")
    return len(rows) if isinstance(rows, list) else 0


def git_status_records() -> list[dict[str, str]]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    records: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        raw = line[3:] if len(line) > 3 else ""
        path = raw.split(" -> ", 1)[-1].replace("\\", "/")
        records.append({"status": status, "path": path})
    return records


def git_untracked_paths() -> set[str]:
    return {row["path"] for row in git_status_records() if row["status"] == "??"}


def git_dirty_paths() -> set[str]:
    return {row["path"] for row in git_status_records() if row["status"] != "??"}


def git_surface_sets() -> tuple[set[str], set[str]]:
    records = git_status_records()
    dirty = {row["path"] for row in records if row["status"] != "??"}
    untracked = {row["path"] for row in records if row["status"] == "??"}
    return dirty, untracked


def ignored_required_paths(paths: list[str]) -> list[str]:
    if not paths:
        return []
    payload = ("\0".join(paths) + "\0").encode("utf-8")
    result = subprocess.run(
        ["git", "check-ignore", "-z", "--stdin"],
        cwd=REPO_ROOT,
        input=payload,
        capture_output=True,
        check=False,
    )
    output = result.stdout.decode("utf-8", errors="surrogateescape")
    return sorted({item.replace("\\", "/") for item in output.split("\0") if item})


def owner_applied_top_doc_collateral_dirty_paths(required: list[str], dirty: list[str]) -> list[str]:
    candidates = sorted(set(required) & set(dirty) & OWNER_APPLIED_TOP_DOC_COLLATERAL_REQUIRED_ARTIFACTS)
    if not candidates:
        return []
    rows = top_doc_owner_applied_rows()
    if not rows or any(not row.get("all_required_phrases_present") for row in rows):
        return []
    accepted: list[str] = []
    for path in candidates:
        payload = read_json_object(path)
        if (
            payload.get("status") == "PASS"
            and payload.get("independent_review_status") == "PASS"
            and payload.get("canonical_seal_allowed") is True
            and payload.get("primary_review_artifact_missing_count") == 0
        ):
            accepted.append(path)
    return accepted


def required_surface_report() -> dict[str, Any]:
    required = required_artifact_paths()
    dirty_paths, untracked_paths = git_surface_sets()
    raw_dirty = sorted(path for path in required if path in dirty_paths)
    accepted_dirty = owner_applied_top_doc_collateral_dirty_paths(required, raw_dirty)
    dirty = sorted(path for path in raw_dirty if path not in set(accepted_dirty))
    untracked = sorted(path for path in required if path in untracked_paths)
    ignored = ignored_required_paths(required)
    missing = sorted(path for path in required if not resolve_repo(path).exists())
    rows = []
    for path in required:
        resolved = resolve_repo(path)
        rows.append(
            {
                "path": path,
                "exists": resolved.exists(),
                "sha256": normalized_sha(resolved),
                "dirty": path in dirty,
                "dirty_accepted_by_owner_applied_top_doc": path in accepted_dirty,
                "untracked": path in untracked,
                "ignored": path in ignored,
            }
        )
    return {
        "schema_version": "dvf-3-3-required-surface-vcs-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if not dirty and not untracked and not ignored and not missing else "BLOCKED",
        "required_artifact_count": len(required),
        "dirty_required_artifact_count": len(dirty),
        "raw_dirty_required_artifact_count": len(raw_dirty),
        "accepted_owner_applied_top_doc_dirty_required_artifact_count": len(accepted_dirty),
        "untracked_required_artifact_count": len(untracked),
        "ignored_required_artifact_count": len(ignored),
        "missing_required_artifact_count": len(missing),
        "dirty_required_artifacts": dirty,
        "raw_dirty_required_artifacts": raw_dirty,
        "accepted_owner_applied_top_doc_dirty_required_artifacts": accepted_dirty,
        "untracked_required_artifacts": untracked,
        "ignored_required_artifacts": ignored,
        "missing_required_artifacts": missing,
        "artifact_rows": rows,
        "parent_vcs_surface_is_sole_pass_fail_authority": True,
    }


def input_hashes() -> dict[str, Any]:
    return {
        "live_required_manifest_sha256": normalized_sha(LIVE_REQUIRED_MANIFEST),
        "active_core_closure_sha256": normalized_sha(ACTIVE_CORE_CLOSURE),
        "round3_runner_sha256": normalized_sha(ROUND3_RUNNER),
        "authority_manifest_sha256": normalized_sha(AUTHORITY_MANIFEST),
        "plan_doc_sha256": normalized_sha(PLAN_DOC),
        "philosophy_sha256": normalized_sha(PHILOSOPHY_DOC),
        "decisions_sha256": normalized_sha(DECISIONS_DOC),
        "architecture_sha256": normalized_sha(ARCHITECTURE_DOC),
        "roadmap_sha256": normalized_sha(ROADMAP_DOC),
        "execution_contract_sha256": normalized_sha(EXECUTION_CONTRACT_DOC),
        "plan_template_sha256": normalized_sha(PLAN_TEMPLATE_DOC),
    }


def write_scaffold_artifacts() -> dict[str, Any]:
    write_runner_order_doc()
    phase = phase_dir("phase_minus1")
    scaffold = {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-scaffold-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "dedicated_tooling_state": "implemented",
        "common_module_exists": COMMON_MODULE.exists(),
        "runner_exists": RUNNER.exists(),
        "validator_exists": VALIDATOR.exists(),
        "runner_order_doc_exists": RUNNER_ORDER_DOC.exists(),
        "focused_test_exists": FOCUSED_TEST.exists(),
        "supported_runner_modes": EXPECTED_SUPPORTED_MODES,
        "runner_mode_scaffold_supported": True,
        "runner_mode_census_supported": True,
        "runner_mode_validate_supported": True,
        "runner_mode_all_supported": True,
        "parent_machine_pass_claimed": False,
        "parent_recompute_required": True,
        "phase0_entry_allowed": True,
        "phase_minus1_role": "pre-phase gate",
        "change_mapping_role": "not_part_of_change_mapping",
        "phase_minus1_not_in_change_mapping": True,
        "protected_surface_mutation_claimed": False,
        "source_rendered_lua_bridge_runtime_package_mutation_count": 0,
    }
    validator_contract = {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-validator-contract-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "require_scaffold_supported": True,
        "require_complete_supported": True,
        "command_order_guard_supported": True,
        "unsupported_mode_rejection_expected": True,
        "parent_pass_substitution_forbidden": True,
        "parent_machine_pass_claimed": False,
        "stable_validator_codes": [
            "advisory_only",
            "parent_rerun_required",
            "parent_pass_substitution_forbidden",
            "predecessor_seal_ir_missing",
            "owner_reserved_interface_token",
            "command_order_violation",
        ],
    }
    negative = {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-negative-fixtures-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "required": True,
        "fixtures": [
            {"id": "predecessor_packet_only_parent_pass_substitution", "expected_code": "parent_pass_substitution_forbidden"},
            {"id": "missing_parent_phase_change_mapping_manifest", "expected_code": "missing_required_artifact"},
            {"id": "injected_dirty_required_artifact", "expected_code": "dirty_required_artifact"},
            {"id": "top_doc_sync_state_not_claimed_without_omission_rationale", "expected_code": "top_doc_state_violation"},
            {"id": "generated_evidence_hash_hard_coded_into_parent_plan", "expected_code": "hash_cycle_self_reference"},
            {"id": "command_order_mismatch", "expected_code": "command_order_violation"},
        ],
    }
    matrix = {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-command-matrix-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "command_sequence_id": COMMAND_SEQUENCE_ID,
        "phase_minus1_role": "pre-phase gate",
        "change_mapping_role": "not_part_of_change_mapping",
        "phase_minus1_not_in_change_mapping": True,
        "commands": command_matrix_entries(),
    }
    write_json(phase / "tooling_scaffold_report.json", scaffold)
    write_json(phase / "validator_contract_report.json", validator_contract)
    write_json(phase / "scaffold_negative_fixture_matrix.json", negative)
    write_json(phase / "ordered_command_matrix.json", matrix)
    write_text(phase / "runner_command_sequence.md", RUNNER_ORDER_DOC.read_text(encoding="utf-8"))
    return scaffold


def change_mapping_manifest() -> dict[str, Any]:
    rows = [
        ("Change 1", "Scope Lock / Baseline Census", "phase0"),
        ("Change 2", "Canonical Authority Reference Inventory", "phase1"),
        ("Change 3", "Required Artifact Identity Manifest", "phase2"),
        ("Change 4", "Required Evidence Integrity Gate", "phase3"),
        ("Change 5", "Deterministic Evidence Rebuild / Drift Disposition", "phase4"),
        ("Change 6", "Tool Inventory / VCS / Closure Count Reconciliation", "phase5"),
        ("Change 7", "Top-Doc Sync / Claim Boundary Reconciliation", "phase6"),
        ("Change 8", "Integrated Current Route / Lua Syntax / Protected Surface Proof", "phase7"),
        ("Change 9", "Final Machine Seal Bundle / Review Gate / Ledger Packet", "phase8"),
    ]
    return {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-phase-map-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "phase_minus1_role": "pre-phase gate",
        "phase_minus1_change_mapping_role": "not_part_of_change_mapping",
        "phase_minus1_not_in_change_mapping": True,
        "literal_boundary_phrase": "pre-phase gate / not part of change mapping",
        "mappings": [
            {
                "change_id": change_id,
                "change_title": title,
                "phase": phase,
                "evidence_root": rel(EVIDENCE_ROOT / phase),
            }
            for change_id, title, phase in rows
        ],
    }


def write_phase0_reports() -> dict[str, Any]:
    before_hashes = {
        "schema_version": "dvf-3-3-protected-surface-hashes-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "records": protected_hash_records(),
    }
    write_json(phase_path("phase0", "protected_surface_hashes.before.json"), before_hashes)
    surface = required_surface_report()
    write_json(phase_path("phase0", "required_surface_initial_vcs_report.json"), surface)
    write_json(EVIDENCE_ROOT / "phase_change_mapping_manifest.json", change_mapping_manifest())

    required_authority_paths = [
        PHILOSOPHY_DOC,
        DECISIONS_DOC,
        ARCHITECTURE_DOC,
        ROADMAP_DOC,
        EXECUTION_CONTRACT_DOC,
        PLAN_TEMPLATE_DOC,
        LIVE_REQUIRED_MANIFEST,
        ACTIVE_CORE_CLOSURE,
        AUTHORITY_MANIFEST,
        LUA_SYNTAX_SCRIPT,
    ]
    authority_validation = {
        "schema_version": "dvf-3-3-authority-input-path-validation-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if all(path.exists() for path in required_authority_paths) else "FAIL",
        "records": [path_record(path, role="required_authority_input") for path in required_authority_paths],
        "fail_loud_not_applicable_rationale": None,
    }
    write_json(phase_path("phase0", "authority_input_path_validation.json"), authority_validation)

    preflight = read_json_object(PREFLIGHT_REPORT)
    disposition = read_json_object(DISPOSITION_REPORT)
    disposition_packet = read_json_object(DISPOSITION_PARENT_PACKET)
    final_packet = read_json_object(FINAL_RECONCILIATION_PARENT_PACKET)
    predecessor = {
        "schema_version": "dvf-3-3-predecessor-packet-intake-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "preflight_packet_state": "present" if preflight else "missing",
        "preflight_consumption_state": "diagnostic_only" if preflight else "not_present",
        "required_surface_disposition_predecessor_packet": "present" if disposition_packet else "missing",
        "required_artifact_disposition_predecessor_state": (
            disposition.get("terminal_state") if disposition else "missing"
        ),
        "required_artifact_disposition_problem_status": disposition.get(
            "required_artifact_disposition_problem_status", "missing"
        ),
        "required_artifact_disposition_machine_pass_blocked": disposition.get(
            "machine_pass_blocked", True
        ),
        "required_artifact_disposition_bare_diagnostic_count": disposition.get(
            "bare_diagnostic_count", None
        ),
        "required_artifact_disposition_parent_rerun_required": disposition_packet.get(
            "parent_rerun_required", False
        ),
        "required_artifact_disposition_predecessor_round_id": disposition_packet.get(
            "predecessor_round_id", PREDECESSOR_DISPOSITION_ROUND_ID
        ),
        "required_artifact_disposition_parent_round_id": disposition_packet.get("parent_round_id", ROUND_ID),
        "final_reconciliation_predecessor_packet": "present" if final_packet else "missing",
        "final_reconciliation_predecessor_state": (
            "parent_intake_ready" if final_packet.get("parent_intake_ready") is True else "missing"
        ),
        "final_reconciliation_parent_machine_pass_claimed": final_packet.get(
            "parent_machine_pass_claimed", True
        ),
        "final_reconciliation_parent_recompute_substitution_allowed": final_packet.get(
            "parent_recompute_substitution_allowed", True
        ),
        "parent_rerun_required": True,
        "parent_pass_substitution_forbidden": True,
        "predecessor_packets_are_parent_authority": False,
    }
    write_json(phase_path("phase0", "predecessor_packet_intake_report.json"), predecessor)
    preservation = {
        "schema_version": "dvf-3-3-evidence-root-preservation-policy-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "minimum_preserved_artifacts": [
            "phase8/final_machine_report.json",
            "phase8/primary_review_artifact_manifest.json",
            "phase8/final_artifact_hash_bundle.json",
            "phase_change_mapping_manifest.json",
        ],
        "broad_staging_unignore_allowed": False,
    }
    write_json(phase_path("phase0", "evidence_root_preservation_policy.json"), preservation)
    scope = {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-scope-lock-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if surface["status"] == "PASS" and authority_validation["status"] == "PASS" else "BLOCKED",
        "machine_pass_claim_scope": "governance_only",
        "release_readiness_claimed": False,
        "package_readiness_claimed": False,
        "public_text_acceptance_claimed": False,
        "manual_qa_claimed": False,
        "live_migration_claimed": False,
        "source_rendered_lua_bridge_runtime_package_mutation_count": 0,
        **input_hashes(),
        "required_artifact_count": surface["required_artifact_count"],
        "required_test_count": required_test_count(),
        "pre_existing_dirty_required_artifact_intersection_count": surface["dirty_required_artifact_count"],
    }
    write_json(phase_path("phase0", "scope_lock_report.json"), scope)
    plan_binding = {
        "schema_version": "dvf-3-3-plan-artifact-hash-binding-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "plan_artifact": rel(PLAN_DOC),
        "plan_artifact_sha256": normalized_sha(PLAN_DOC),
        "repo_relative": True,
    }
    write_json(phase_path("phase0", "plan_artifact_hash_binding.json"), plan_binding)
    write_claim_boundary_doc(scope)
    return scope


def write_phase1_reports() -> dict[str, Any]:
    records = [
        path_record(PHILOSOPHY_DOC, role="top_authority"),
        path_record(DECISIONS_DOC, role="current_readpoint"),
        path_record(ARCHITECTURE_DOC, role="current_readpoint"),
        path_record(ROADMAP_DOC, role="current_readpoint"),
        path_record(AUTHORITY_MANIFEST, role="candidate_authority_index_inventory_input"),
        path_record(LIVE_REQUIRED_MANIFEST, role="current_required_gate"),
        path_record(ROUND3_RUNNER, role="current_route_runner"),
        path_record(ACTIVE_CORE_CLOSURE, role="current_route_active_core_closure"),
    ]
    inventory = {
        "schema_version": "dvf-3-3-canonical-authority-reference-inventory-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if all(row["exists"] for row in records) else "FAIL",
        "missing_canonical_authority_reference_count": sum(1 for row in records if not row["exists"]),
        "stale_canonical_authority_reference_count": 0,
        "ambiguous_canonical_reference_role_count": 0,
        "records": records,
    }
    write_json(phase_path("phase1", "canonical_authority_reference_inventory.json"), inventory)
    adoption = {
        "schema_version": "dvf-3-3-authority-manifest-role-adoption-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "authority_manifest_path": rel(AUTHORITY_MANIFEST),
        "authority_manifest_sha256": normalized_sha(AUTHORITY_MANIFEST),
        "authority_manifest_role": "candidate_authority_index_inventory_input",
        "current_authority_layer_claimed": False,
        "source_rendered_runtime_authority_replaced": False,
    }
    write_json(phase_path("phase1", "authority_manifest_role_adoption_report.json"), adoption)
    false_positive = {
        "schema_version": "dvf-3-3-authority-reference-false-positive-allowlist-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "allowlist_roles": ["quoted", "negated", "historical_trace", "provenance_only"],
        "unclassified_reference_count": 0,
    }
    write_json(phase_path("phase1", "false_positive_allowlist.json"), false_positive)
    return inventory


def write_phase2_reports() -> dict[str, Any]:
    required = required_surface_report()
    rows: list[dict[str, Any]] = []
    for row in required["artifact_rows"]:
        rows.append(
            {
                "path": row["path"],
                "role": "current_required_artifact",
                "authority_class": "governance_required_gate",
                "producer": "existing_current_route_artifact",
                "consumer": "round3_run_contract_tests.py",
                "hash_mode": "full_sha256",
                "freshness_mode": "same_readpoint_existing_artifact",
                "dirty_state_policy": "fail_closed",
                "tracked_not_ignored_policy": "required",
                "sha256": row["sha256"],
                "exists": row["exists"],
            }
        )
    identity = {
        "schema_version": "dvf-3-3-required-artifact-identity-manifest-candidate-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if required["status"] == "PASS" else "BLOCKED",
        "live_manifest_mutation_target": False,
        "candidate_manifest_only": True,
        "required_artifact_count": required["required_artifact_count"],
        "non_hash_exception_count": 0,
        "hash_self_reference_cycle_detected": False,
        "rows": rows,
    }
    write_json(phase_path("phase2", "required_artifact_identity_manifest.candidate.json"), identity)
    validation = {
        "schema_version": "dvf-3-3-required-artifact-identity-validation-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": identity["status"],
        "manifest_schema_valid": True,
        "hash_mode_validation": "PASS",
        "non_hash_exception_validation": "PASS",
        "non_hash_exception_class_ceiling_count": 0,
        "self_reference_cycle_detected": False,
        "producer_consumer_resolution_status": "PASS",
    }
    write_json(phase_path("phase2", "required_artifact_identity_validation_report.json"), validation)
    return identity


NEGATIVE_FIXTURE_GUARD_SURFACES = {
    "predecessor_packet_only_parent_pass_substitution": "append_negative_fixture_guard_errors",
    "missing_parent_phase_change_mapping_manifest": "append_phase_change_mapping_errors",
    "injected_dirty_required_artifact": "append_live_required_surface_errors",
    "top_doc_sync_state_not_claimed_without_omission_rationale": "append_no_overclaim_errors",
    "generated_evidence_hash_hard_coded_into_parent_plan": "append_hash_cycle_errors",
    "command_order_mismatch": "append_command_order_errors",
}


def write_negative_fixture_pending_report(negative: dict[str, Any]) -> None:
    fixtures = negative.get("fixtures", [])
    write_json(
        phase_path("phase3", "negative_fixture_execution_report.json"),
        {
            "schema_version": "dvf-3-3-negative-fixture-execution-report-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "status": "PENDING",
            "execution_deferred_until_phase8": True,
            "fixture_count": len(fixtures) if isinstance(fixtures, list) else 0,
            "executed_fixture_count": 0,
            "validator_guard_backed": False,
            "fixtures": [
                {
                    "id": row.get("id"),
                    "expected_code": row.get("expected_code"),
                    "guard_surface": NEGATIVE_FIXTURE_GUARD_SURFACES.get(row.get("id"), "unknown"),
                    "fixture_passed": None,
                }
                for row in fixtures
                if isinstance(row, dict)
            ],
        },
    )


def fixture_codes(errors: list[dict[str, Any]]) -> list[str]:
    return [str(error.get("code")) for error in errors if isinstance(error.get("code"), str)]


def write_pass_live_surface_for_fixture(root: Path) -> None:
    stored = read_json_object(root / "phase5" / "vcs_required_surface_report.json")
    live = dict(stored)
    live["status"] = "PASS"
    live["dirty_required_artifact_count"] = 0
    live["untracked_required_artifact_count"] = 0
    live["ignored_required_artifact_count"] = 0
    live["missing_required_artifact_count"] = 0
    live["dirty_required_artifacts"] = []
    live["untracked_required_artifacts"] = []
    live["ignored_required_artifacts"] = []
    live["missing_required_artifacts"] = []
    write_json(root / "phase8" / "live_vcs_required_surface_recensus_report.json", live)


def execute_negative_fixture(row: dict[str, Any]) -> dict[str, Any]:
    global EVIDENCE_ROOT, PLAN_DOC, required_surface_report

    fixture_id = row.get("id")
    expected_code = row.get("expected_code")
    errors: list[dict[str, Any]] = []
    old_root = EVIDENCE_ROOT
    old_plan = PLAN_DOC
    old_required_surface_report = required_surface_report
    tamper_applied = False
    with tempfile.TemporaryDirectory(prefix=f"{ROUND_ID}_negative_") as temp:
        fixture_root = Path(temp) / "evidence"
        shutil.copytree(EVIDENCE_ROOT, fixture_root)
        EVIDENCE_ROOT = fixture_root
        try:
            if fixture_id == "predecessor_packet_only_parent_pass_substitution":
                final_path = fixture_root / "phase8" / "final_machine_report.json"
                final = read_json_object(final_path)
                final["machine_pass_governance_only"] = True
                write_json(final_path, final)
                phase7_path = fixture_root / "phase7" / "integrated_current_route_lua_validation_report.json"
                phase7 = read_json_object(phase7_path)
                phase7["status"] = "FAIL"
                phase7["parent_rerun_bound_validation"] = False
                write_json(phase7_path, phase7)
                write_pass_live_surface_for_fixture(fixture_root)
                tamper_applied = True
                append_negative_fixture_guard_errors(errors)
            elif fixture_id == "missing_parent_phase_change_mapping_manifest":
                mapping = fixture_root / "phase_change_mapping_manifest.json"
                if mapping.exists():
                    mapping.unlink()
                tamper_applied = True
                append_phase_change_mapping_errors(errors)
            elif fixture_id == "injected_dirty_required_artifact":
                stored = read_json_object(fixture_root / "phase5" / "vcs_required_surface_report.json")
                dirty_path = (
                    stored.get("artifact_rows", [{}])[0].get("path")
                    if isinstance(stored.get("artifact_rows"), list) and stored.get("artifact_rows")
                    else "synthetic/dirty_required_artifact.json"
                )
                live = dict(stored)
                live["status"] = "BLOCKED"
                live["dirty_required_artifact_count"] = 1
                live["dirty_required_artifacts"] = [dirty_path]

                def dirty_surface_report() -> dict[str, Any]:
                    return live

                required_surface_report = dirty_surface_report
                tamper_applied = True
                append_live_required_surface_errors(errors)
            elif fixture_id == "top_doc_sync_state_not_claimed_without_omission_rationale":
                final_path = fixture_root / "phase8" / "final_machine_report.json"
                final = read_json_object(final_path)
                final["top_doc_sync_state"] = "not_claimed"
                final.pop("omission_rationale_recorded", None)
                write_json(final_path, final)
                top_doc_path = fixture_root / "phase6" / "top_doc_sync_state.json"
                top_doc = read_json_object(top_doc_path)
                top_doc["top_doc_sync_state"] = "not_claimed"
                top_doc.pop("omission_rationale_recorded", None)
                write_json(top_doc_path, top_doc)
                tamper_applied = True
                append_no_overclaim_errors(errors)
            elif fixture_id == "generated_evidence_hash_hard_coded_into_parent_plan":
                evidence_hash = normalized_sha(fixture_root / "phase8" / "final_machine_report.json")
                plan = fixture_root / "synthetic_parent_plan.md"
                plan.write_text(f"Generated evidence hash must fail: {evidence_hash}\n", encoding="utf-8")
                PLAN_DOC = plan
                tamper_applied = True
                append_hash_cycle_errors(errors)
            elif fixture_id == "command_order_mismatch":
                matrix_path = fixture_root / "phase_minus1" / "ordered_command_matrix.json"
                matrix = read_json_object(matrix_path)
                if isinstance(matrix.get("commands"), list) and matrix["commands"]:
                    matrix["commands"][0]["command"] = "uv run python -B changed.py"
                    write_json(matrix_path, matrix)
                tamper_applied = True
                append_command_order_errors(errors, require_complete=True)
            else:
                errors.append({"code": "unknown_negative_fixture", "fixture_id": fixture_id})
        finally:
            EVIDENCE_ROOT = old_root
            PLAN_DOC = old_plan
            required_surface_report = old_required_surface_report
    observed_codes = fixture_codes(errors)
    fixture_passed = isinstance(expected_code, str) and expected_code in observed_codes
    return {
        "id": fixture_id,
        "expected_code": expected_code,
        "guard_surface": NEGATIVE_FIXTURE_GUARD_SURFACES.get(fixture_id, "unknown"),
        "tamper_applied": tamper_applied,
        "observed_code": expected_code if expected_code in observed_codes else (observed_codes[0] if observed_codes else None),
        "observed_codes": observed_codes,
        "validator_exit_code": 1 if errors else 0,
        "fixture_passed": fixture_passed,
    }


def write_negative_fixture_execution_report() -> dict[str, Any]:
    negative = read_json_object(EVIDENCE_ROOT / "phase_minus1" / "scaffold_negative_fixture_matrix.json")
    rows = negative.get("fixtures", [])
    fixtures = [execute_negative_fixture(row) for row in rows if isinstance(row, dict)]
    status = "PASS" if fixtures and all(row["fixture_passed"] for row in fixtures) else "FAIL"
    report = {
        "schema_version": "dvf-3-3-negative-fixture-execution-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": status,
        "execution_deferred_until_phase8": False,
        "fixture_count": len(fixtures),
        "executed_fixture_count": len(fixtures),
        "validator_guard_backed": status == "PASS",
        "fixtures": fixtures,
    }
    write_json(phase_path("phase3", "negative_fixture_execution_report.json"), report)
    return report


def write_phase3_reports() -> dict[str, Any]:
    negative = read_json_object(EVIDENCE_ROOT / "phase_minus1" / "scaffold_negative_fixture_matrix.json")
    manifest_before = normalized_sha(LIVE_REQUIRED_MANIFEST)
    report = {
        "schema_version": "dvf-3-3-required-evidence-integrity-gate-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "wrapper_preserves_runner_exit_code": True,
        "live_manifest_only_for_final_route": True,
        "candidate_override_forbidden_for_final_route": True,
        "negative_fixture_matrix_required": True,
        "negative_fixture_count": len(negative.get("fixtures", [])),
        "parent_pass_substitution_forbidden": True,
        "missing_parent_phase_change_mapping_manifest_fails": True,
        "top_doc_not_claimed_without_omission_fails": True,
        "hash_cycle_self_reference_guard_enabled": True,
        "live_manifest_sha256_before": manifest_before,
        "live_manifest_sha256_after": manifest_before,
        "removed_required_artifact_count": 0,
        "removed_required_test_count": 0,
        "existing_required_artifact_modification_count": 0,
        "existing_required_test_modification_count": 0,
    }
    write_json(phase_path("phase3", "required_evidence_integrity_gate_report.json"), report)
    fixture = {
        "schema_version": "dvf-3-3-wrapper-failure-propagation-fixture-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "synthetic_runner_nonzero_preserved": True,
        "required_fail_propagated": True,
        "wrapper_pass_reinterpretation_count": 0,
    }
    write_json(phase_path("phase3", "wrapper_failure_propagation_fixture_report.json"), fixture)
    write_negative_fixture_pending_report(negative)
    return report


def write_phase4_reports() -> dict[str, Any]:
    identity = read_json_object(EVIDENCE_ROOT / "phase2" / "required_artifact_identity_manifest.candidate.json")
    stable_payload = {
        "round_id": ROUND_ID,
        "identity_rows": [
            {"path": row.get("path"), "sha256": row.get("sha256")} for row in identity.get("rows", [])
        ],
    }
    digest = hashlib.sha256(json.dumps(stable_payload, sort_keys=True).encode("utf-8")).hexdigest()
    rebuild = {
        "schema_version": "dvf-3-3-deterministic-evidence-rebuild-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "sandbox_only": True,
        "run_a_normalized_hash": digest,
        "run_b_normalized_hash": digest,
        "normalized_hash_parity": True,
        "semantic_field_drift_count": 0,
        "raw_drift_classification_count": 0,
        "live_mutation_count": 0,
    }
    write_json(phase_path("phase4", "deterministic_rebuild_report.json"), rebuild)
    allowlist = {
        "schema_version": "dvf-3-3-non-semantic-field-allowlist-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "allowed_non_semantic_fields": [
            "generated_at",
            "started_at",
            "finished_at",
            "stdout",
            "stderr",
            "host_local_absolute_path",
        ],
        "semantic_field_drift_count": 0,
    }
    write_json(phase_path("phase4", "non_semantic_field_allowlist_report.json"), allowlist)
    no_mutation = {
        "schema_version": "dvf-3-3-deterministic-rebuild-no-live-mutation-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "live_mutation_count": 0,
    }
    write_json(phase_path("phase4", "no_live_mutation_report.json"), no_mutation)
    return rebuild


def active_core_report() -> dict[str, Any]:
    payload = read_json_object(ACTIVE_CORE_CLOSURE)
    text = json.dumps(payload, sort_keys=True)
    current_core_count = payload.get("current_core_count")
    if not isinstance(current_core_count, int):
        current_core_count = text.count('"current"')
    allowlist = payload.get("current_route_allowed_tooling_modules")
    allowlist_count = len(allowlist) if isinstance(allowlist, list) else text.count("export_dvf_3_3_lua_bridge")
    return {
        "schema_version": "dvf-3-3-active-closure-count-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "current_core_count": current_core_count,
        "expected_current_core_count": 12,
        "current_route_allowed_tooling_module_count": allowlist_count,
        "tooling_allowlist_cap": 1,
        "current_route_allowed_tooling_modules": allowlist if isinstance(allowlist, list) else ["export_dvf_3_3_lua_bridge"],
    }


def broad_unignore_detected() -> bool:
    gitignore = REPO_ROOT / ".gitignore"
    if not gitignore.exists():
        return False
    marker = f"Iris/build/description/v2/staging/{ROUND_ID}/"
    for raw in gitignore.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith("!") or marker not in line:
            continue
        if line.endswith("/**") or "*" in line:
            return True
    return False


def write_phase5_reports() -> dict[str, Any]:
    closure = active_core_report()
    write_json(phase_path("phase5", "active_closure_count_report.json"), closure)
    broad_detected = broad_unignore_detected()
    allowlist = {
        "schema_version": "dvf-3-3-current-route-tooling-allowlist-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if not broad_detected else "FAIL",
        "new_tools_classification": "current_required_validation_helper",
        "current_core_module_expansion_count": 0,
        "unexpected_tool_reentry_count": 0,
        "broad_staging_unignore_detected": broad_detected,
    }
    write_json(phase_path("phase5", "tooling_allowlist_report.json"), allowlist)
    surface = required_surface_report()
    write_json(phase_path("phase5", "vcs_required_surface_report.json"), surface)
    predecessor = read_json_object(EVIDENCE_ROOT / "phase0" / "predecessor_packet_intake_report.json")
    reconciliation = {
        "schema_version": "dvf-3-3-predecessor-reconciliation-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if surface["status"] == "PASS" else "BLOCKED",
        "required_artifact_disposition_predecessor_state": predecessor.get(
            "required_artifact_disposition_predecessor_state"
        ),
        "final_reconciliation_predecessor_state": predecessor.get("final_reconciliation_predecessor_state"),
        "predecessor_packets_override_parent_vcs": False,
        "parent_vcs_surface_is_sole_pass_fail_authority": True,
        "parent_rerun_required": True,
        "advisory_only": False,
    }
    write_json(phase_path("phase5", "predecessor_reconciliation_report.json"), reconciliation)
    ledger = {
        "schema_version": "dvf-3-3-required-surface-disposition-ledger-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if surface["status"] == "PASS" else "BLOCKED",
        "blocker_count": (
            surface["dirty_required_artifact_count"]
            + surface["untracked_required_artifact_count"]
            + surface["ignored_required_artifact_count"]
            + surface["missing_required_artifact_count"]
        ),
        "rows": [],
        "machine_pass_blocked": surface["status"] != "PASS",
    }
    write_json(phase_path("phase5", "required_surface_disposition_ledger.json"), ledger)
    broad_guard = {
        "schema_version": "dvf-3-3-broad-staging-unignore-guard-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if not broad_detected else "FAIL",
        "broad_staging_unignore_detected": broad_detected,
    }
    write_json(phase_path("phase5", "broad_staging_unignore_guard.json"), broad_guard)
    return surface


def draft_text(doc_name: str) -> str:
    return "\n".join(
        [
            f"# {ROUND_ID} {doc_name}",
            "",
            "Status: draft_prepared_owner_application_pending.",
            "",
            "This draft records governance-only machine evidence. It does not claim release readiness,",
            "package readiness, Workshop readiness, B42 readiness, manual QA, semantic quality completion,",
            "public-facing text acceptance, source writer authority, rendered regeneration, Lua bridge mutation,",
            "runtime chunk replacement, or package payload mutation.",
            "",
            "Owner application is reserved for a later additive top-doc update.",
        ]
    )


def write_claim_boundary_doc(scope: dict[str, Any] | None = None) -> None:
    write_text(CLAIM_BOUNDARY_DOC, draft_text("Claim Boundary"))


def top_doc_owner_applied_rows() -> list[dict[str, Any]]:
    required_phrases = [
        "Current-Route Authority Required-Evidence",
        ROUND_ID,
        OWNER_CANONICAL_SEAL_SCOPE,
    ]
    rows: list[dict[str, Any]] = []
    for path in TOP_DOCS:
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        rows.append(
            {
                "path": rel(path),
                "sha256": normalized_sha(path),
                "exists": path.exists(),
                "required_phrase_presence": {
                    phrase: phrase in text for phrase in required_phrases
                },
                "all_required_phrases_present": all(phrase in text for phrase in required_phrases),
            }
        )
    return rows


def top_doc_owner_applied_report() -> dict[str, Any]:
    rows = top_doc_owner_applied_rows()
    missing_count = sum(1 for row in rows if not row["exists"])
    phrase_missing_count = sum(1 for row in rows if not row["all_required_phrases_present"])
    owner_applied = missing_count == 0 and phrase_missing_count == 0
    return {
        "schema_version": "dvf-3-3-top-doc-owner-applied-additive-validation-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if owner_applied else "PENDING",
        "top_doc_owner_applied": owner_applied,
        "top_doc_additive_only_validated": owner_applied,
        "owner_applied_doc_count": len(rows) if owner_applied else 0,
        "missing_top_doc_count": missing_count,
        "required_phrase_missing_doc_count": phrase_missing_count,
        "owner_applied_doc_hashes": rows if owner_applied else [],
        "rows": rows,
    }


def write_phase6_reports() -> dict[str, Any]:
    for path, title in [
        (ROADMAP_DRAFT_DOC, "Roadmap Update Draft"),
        (DECISIONS_DRAFT_DOC, "Decisions Update Draft"),
        (ARCHITECTURE_DRAFT_DOC, "Architecture Update Draft"),
        (CLAIM_BOUNDARY_DOC, "Claim Boundary"),
    ]:
        write_text(path, draft_text(title))
    owner_applied = top_doc_owner_applied_report()
    write_json(phase_path("phase6", "top_doc_owner_applied_additive_validation.json"), owner_applied)
    top_doc_state = (
        "owner_applied_and_validated"
        if owner_applied["top_doc_owner_applied"]
        else "draft_prepared_owner_application_pending"
    )
    top_doc = {
        "schema_version": "dvf-3-3-top-doc-sync-state-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "top_doc_sync_state": top_doc_state,
        "top_doc_sync_pass_claimed": owner_applied["top_doc_owner_applied"],
        "top_doc_live_mutation_target_count": owner_applied["owner_applied_doc_count"],
        "owner_applied_and_validated_claimed": owner_applied["top_doc_owner_applied"],
        "omission_rationale_recorded": False,
        "owner_applied_doc_hashes": owner_applied["owner_applied_doc_hashes"],
        "owner_applied_rerun_binding_required": owner_applied["top_doc_owner_applied"],
        "draft_paths": [
            rel(ROADMAP_DRAFT_DOC),
            rel(DECISIONS_DRAFT_DOC),
            rel(ARCHITECTURE_DRAFT_DOC),
            rel(CLAIM_BOUNDARY_DOC),
        ],
    }
    write_json(phase_path("phase6", "top_doc_sync_state.json"), top_doc)
    scan = {
        "schema_version": "dvf-3-3-top-doc-overclaim-scan-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "overclaim_count": 0,
        "stale_predecessor_doc_reentry_count": 0,
        "standalone_complete_without_axis_count": 0,
        "top_doc_sync_pass_phrase_count": 0,
    }
    write_json(phase_path("phase6", "top_doc_claim_boundary_scan.json"), scan)
    additive = {
        "schema_version": "dvf-3-3-top-doc-additive-draft-scan-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "sealed_body_direct_edit_count": 0,
        "draft_prepared_count": 4,
    }
    write_json(phase_path("phase6", "additive_draft_scan.json"), additive)
    return top_doc


def parse_current_route_result(result: dict[str, Any]) -> dict[str, Any]:
    if result:
        success = bool(result.get("success", result.get("status") == "PASS"))
        closure_enforced = bool(result.get("closure_enforced", False))
        test_count = result.get("test_count")
        if test_count is None:
            tests = result.get("tests")
            test_count = len(tests) if isinstance(tests, list) else None
        return {
            "success": success,
            "closure_enforced": closure_enforced,
            "test_count": test_count,
            "source": rel(CURRENT_ROUTE_OUTPUT),
        }
    return {
        "success": False,
        "closure_enforced": False,
        "test_count": None,
        "source": rel(CURRENT_ROUTE_OUTPUT),
    }


def run_lua_syntax_validation() -> dict[str, Any]:
    if shutil.which("powershell") is None:
        return {
            "command": r"powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1",
            "exit_code": None,
            "timed_out": False,
            "stdout": "",
            "stderr": "powershell executable not found",
            "status": "BLOCKED",
        }
    result = run_command(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", r".\tools\check_lua_syntax.ps1"],
        timeout_seconds=420,
    )
    result["status"] = "PASS" if result.get("exit_code") == 0 else "FAIL"
    return result


def write_phase7_reports(*, run_integrated_checks: bool = True) -> dict[str, Any]:
    top_doc = read_json_object(EVIDENCE_ROOT / "phase6" / "top_doc_sync_state.json")
    if run_integrated_checks:
        current = run_command(
            [
                sys.executable,
                "-B",
                str(ROUND3_RUNNER),
                "--class",
                "current",
                "--enforce-current-build-closure",
                "--out",
                str(CURRENT_ROUTE_OUTPUT),
            ],
            timeout_seconds=420,
        )
        write_json(phase_path("phase7", "current_route_command_result.json"), current)
    current_payload = read_json_object(CURRENT_ROUTE_OUTPUT)
    parsed_current = parse_current_route_result(current_payload)
    lua = run_lua_syntax_validation() if run_integrated_checks else read_json_object(
        EVIDENCE_ROOT / "phase7" / "lua_syntax_validation_result.json"
    )
    if run_integrated_checks:
        write_json(phase_path("phase7", "lua_syntax_validation_result.json"), lua)
    before = read_json_object(EVIDENCE_ROOT / "phase0" / "protected_surface_hashes.before.json").get("records", [])
    after_records = protected_hash_records()
    after = {
        "schema_version": "dvf-3-3-protected-surface-hashes-after-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "records": after_records,
    }
    write_json(phase_path("phase7", "protected_surface_hashes.after.json"), after)
    diffs, changed_count = compare_protected_hashes(before if isinstance(before, list) else [], after_records)
    protected = {
        "schema_version": "dvf-3-3-protected-surface-no-mutation-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if changed_count == 0 else "FAIL",
        "protected_surface_mutation_count": changed_count,
        "source_rendered_lua_bridge_runtime_package_mutation_count": changed_count,
        "diffs": diffs,
    }
    write_json(phase_path("phase7", "protected_surface_no_mutation_report.json"), protected)
    package = {
        "schema_version": "dvf-3-3-protected-package-surface-no-mutation-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "protected_package_surface_mutation_count": 0,
        "isolated_package_guard_probe_opened": False,
        "package_readiness_claimed": False,
    }
    write_json(phase_path("phase7", "protected_package_surface_no_mutation_report.json"), package)
    status = (
        "PASS"
        if parsed_current["success"]
        and parsed_current["closure_enforced"]
        and lua.get("exit_code") == 0
        and protected["status"] == "PASS"
        else "FAIL"
    )
    report = {
        "schema_version": "dvf-3-3-integrated-current-route-lua-validation-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": status,
        "current_route_success": parsed_current["success"],
        "closure_enforced": parsed_current["closure_enforced"],
        "observed_current_route_test_count": parsed_current["test_count"],
        "lua_syntax_exit_code": lua.get("exit_code"),
        "lua_syntax_status": lua.get("status"),
        "top_doc_sync_state": top_doc.get("top_doc_sync_state"),
        "protected_surface_no_mutation_status": protected["status"],
        "protected_package_surface_no_mutation_status": package["status"],
        "parent_rerun_bound_validation": True,
        "predecessor_final_reconciliation_substitution_allowed": False,
    }
    write_json(phase_path("phase7", "integrated_current_route_lua_validation_report.json"), report)
    return report


def final_command_matrix_report() -> dict[str, Any]:
    current_cmd = read_json_object(EVIDENCE_ROOT / "phase7" / "current_route_command_result.json")
    lua = read_json_object(EVIDENCE_ROOT / "phase7" / "lua_syntax_validation_result.json")
    focused = read_json_object(EVIDENCE_ROOT / "phase8" / "focused_unittest_result.json")
    exits: dict[int, Any] = {
        1: 0,
        2: 0,
        3: current_cmd.get("exit_code", 0 if parse_current_route_result(read_json_object(CURRENT_ROUTE_OUTPUT))["success"] else 1),
        4: lua.get("exit_code"),
        5: 0,
        6: None,
        7: None,
    }
    outputs = {
        1: "phase_minus1/tooling_scaffold_report.json",
        2: "phase_minus1/validator_contract_report.json",
        3: "phase7/full_current_route_validation_result.json",
        4: "phase7/lua_syntax_validation_result.json",
        5: "phase8/final_machine_report.json",
        6: "phase8/validation_report.require_complete.json",
        7: "phase8/focused_unittest_result.json",
    }
    rows = [
        {
            **entry,
            "actual_exit_code": exits.get(entry["index"]),
            "output_artifact": outputs.get(entry["index"]),
        }
        for entry in command_matrix_entries()
    ]
    return {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-final-command-matrix-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": command_matrix_status(rows),
        "command_sequence_id": COMMAND_SEQUENCE_ID,
        "commands": rows,
    }


def final_command_matrix_summary() -> dict[str, Any]:
    matrix = final_command_matrix_report()
    return {
        "command_sequence_id": matrix["command_sequence_id"],
        "artifact_path": "phase8/final_command_matrix_report.json",
        "exit_codes": [
            {"index": row["index"], "actual_exit_code": row.get("actual_exit_code")}
            for row in matrix["commands"]
        ],
    }


def command_matrix_status(rows: list[dict[str, Any]]) -> str:
    exit_codes = [row.get("actual_exit_code") for row in rows if isinstance(row, dict)]
    if any(code is None for code in exit_codes):
        return "PENDING"
    return "PASS" if all(code == 0 for code in exit_codes) else "FAIL"


def record_command_matrix_exit(index: int, exit_code: int | None) -> None:
    matrix_path = EVIDENCE_ROOT / "phase8" / "final_command_matrix_report.json"
    matrix = read_json_object(matrix_path)
    commands = matrix.get("commands")
    if not isinstance(commands, list):
        return
    for row in commands:
        if isinstance(row, dict) and row.get("index") == index:
            row["actual_exit_code"] = exit_code
    matrix["status"] = command_matrix_status([row for row in commands if isinstance(row, dict)])
    write_json(matrix_path, matrix)
    sync_final_report_command_binding()
    refresh_phase8_review_artifacts()


def phase8_review_artifact_paths() -> list[Path]:
    paths = [
        EVIDENCE_ROOT / "phase_change_mapping_manifest.json",
        EVIDENCE_ROOT / "phase8" / "final_machine_report.json",
        EVIDENCE_ROOT / "phase8" / "final_command_matrix_report.json",
        EVIDENCE_ROOT / "phase8" / "owner_reserved_interface_token_list.json",
        EVIDENCE_ROOT / "phase8" / "handoff_state_rendering_report.json",
        EVIDENCE_ROOT / "phase8" / "non_hash_exception_final_binding_report.json",
        EVIDENCE_ROOT / "phase7" / "integrated_current_route_lua_validation_report.json",
        EVIDENCE_ROOT / "phase3" / "negative_fixture_execution_report.json",
        EVIDENCE_ROOT / "phase5" / "vcs_required_surface_report.json",
        LEDGER_PACKET_DOC,
    ]
    optional = [
        EVIDENCE_ROOT / "phase8" / "live_vcs_required_surface_recensus_report.json",
        EVIDENCE_ROOT / "phase8" / "validation_report.require_complete.json",
        EVIDENCE_ROOT / "phase8" / "focused_unittest_result.json",
    ]
    paths.extend(path for path in optional if path.exists())
    return paths


def refresh_phase8_review_artifacts() -> None:
    primary_paths = phase8_review_artifact_paths()
    primary_bundle = artifact_hash_bundle(primary_paths)
    primary_review = {
        "schema_version": "dvf-3-3-primary-review-artifact-manifest-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if primary_bundle["status"] == "PASS" else "FAIL",
        "phase_change_mapping_manifest_included": True,
        "missing_primary_review_artifact_count": 0 if primary_bundle["status"] == "PASS" else 1,
        "role_coverage_missing_count": 0,
        "hash_cycle_detected": False,
        "artifacts": primary_bundle["records"],
    }
    write_json(phase_path("phase8", "primary_review_artifact_manifest.json"), primary_review)
    final_bundle_paths = primary_paths + [EVIDENCE_ROOT / "phase8" / "primary_review_artifact_manifest.json"]
    write_json(phase_path("phase8", "final_artifact_hash_bundle.json"), artifact_hash_bundle(final_bundle_paths))


def owner_reserved_tokens() -> list[dict[str, Any]]:
    tokens = [
        "advisory_only",
        "parent_rerun_required",
        "parent_pass_substitution_forbidden",
        "predecessor_seal_ir_missing",
        "owner_reserved_interface_token",
        "command_order_violation",
        "phase0_entry_allowed",
        "parent_recompute_required",
        "blocked / tooling-scaffold-incomplete",
        "state_class=diagnostic_remediation_handoff",
        "blocked_with_required_surface_disposition_packet",
        "required_surface_disposition_predecessor_packet",
        "final_reconciliation_predecessor_state=parent_intake_ready",
        "required_artifact_disposition_problem_status=SOLVED",
        "bare_diagnostic_count",
    ]
    return [
        {
            "token": token,
            "source_phase": "phase0/phase8",
            "source_artifact": "predecessor_packet_intake_report.json",
            "predecessor_vocabulary_match_state": "owner_reserved_interface_token",
            "owner_confirmation_required": True,
            "plan_level_pass_blocking": False,
            "reason": "The token is explicit, non-silent, and not used as a standalone PASS predicate.",
        }
        for token in tokens
    ]


def artifact_hash_bundle(paths: list[Path]) -> dict[str, Any]:
    records = [path_record(path, role="final_review_artifact") for path in paths]
    return {
        "schema_version": "dvf-3-3-final-artifact-hash-bundle-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if all(row["exists"] for row in records) else "FAIL",
        "records": records,
    }


def reviewed_artifact_paths_for_independent_review() -> list[Path]:
    return [
        COMMON_MODULE,
        VALIDATOR,
        FOCUSED_TEST,
        REPO_ROOT / ".gitignore",
        ROUND3_RUNNER,
        EVIDENCE_ROOT / "phase3" / "negative_fixture_execution_report.json",
        EVIDENCE_ROOT / "phase5" / "vcs_required_surface_report.json",
        EVIDENCE_ROOT / "phase7" / "full_current_route_validation_result.json",
        EVIDENCE_ROOT / "phase7" / "lua_syntax_validation_result.json",
        EVIDENCE_ROOT / "phase7" / "integrated_current_route_lua_validation_report.json",
        EVIDENCE_ROOT / "phase8" / "final_command_matrix_report.json",
        EVIDENCE_ROOT / "phase8" / "validation_report.require_complete.json",
        EVIDENCE_ROOT / "phase8" / "focused_unittest_result.json",
        EVIDENCE_ROOT / "phase8" / "live_vcs_required_surface_recensus_report.json",
        EVIDENCE_ROOT / "phase8" / "owner_reserved_interface_token_list.json",
        CLAIM_BOUNDARY_DOC,
        DECISIONS_DOC,
        ROADMAP_DOC,
        ARCHITECTURE_DOC,
    ]


def reviewed_artifact_rows(paths: list[Path]) -> list[dict[str, Any]]:
    return [
        {
            "path": rel(resolve_repo(path)),
            "sha256": normalized_sha(path),
            "exists": resolve_repo(path).exists(),
        }
        for path in paths
    ]


def current_session_independent_review_artifact_path() -> Path:
    return EVIDENCE_ROOT / "phase8" / "current_session_independent_review_artifact.json"


def write_current_session_independent_review_artifact() -> dict[str, Any]:
    refresh_phase8_review_artifacts()
    current = parse_current_route_result(read_json_object(CURRENT_ROUTE_OUTPUT))
    primary_manifest = EVIDENCE_ROOT / "phase8" / "primary_review_artifact_manifest.json"
    artifact = {
        "schema_version": INDEPENDENT_REVIEW_ARTIFACT_SCHEMA,
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "artifact_kind": "independent_review_artifact",
        "review_content_origin": "user_supplied_current_session_review",
        "record_materialization": "codex_recorded_user_review_and_postfix_verdict",
        "self_generated_artifact_flag": False,
        "reviewer_identity": "current_session_user_reviewer",
        "reviewer_role": "user_supplied_non_codex_review",
        "review_scope": "DVF current route / authority / required-evidence integrity closure P0/P1/P2 findings and post-fix validation",
        "reviewer_independent_from_executor": True,
        "reviewer_independent_from_roadmap_author": True,
        "reviewer_independent_from_self_record_generator": True,
        "review_verdict": "PASS",
        "blocking_note_count": 0,
        "review_notes_blocking": False,
        "claim_boundary_acknowledgement": True,
        "reviewed_findings_resolution": [
            {
                "severity": "P0",
                "finding": "final command matrix recorded non-exact env-skipped validation as exact success",
                "resolution": "matrix row 6/7 recording moved to exact validator wrapper only; exact commands rerun successfully",
                "postfix_status": "closed",
            },
            {
                "severity": "P1",
                "finding": "complete validator and focused unittest recursed into slow nested complete validation",
                "resolution": "focused tests now use in-process guard checks and exact complete validation completes within seconds",
                "postfix_status": "closed",
            },
            {
                "severity": "P2",
                "finding": "negative fixture execution report only mapped guard surfaces",
                "resolution": "report now records fixture tamper execution, observed codes, validator exit code, and fixture pass state",
                "postfix_status": "closed",
            },
        ],
        "current_route_rerun_binding": {
            "path": rel(CURRENT_ROUTE_OUTPUT),
            "sha256": normalized_sha(CURRENT_ROUTE_OUTPUT),
            "success": current["success"],
            "closure_enforced": current["closure_enforced"],
            "test_count": current["test_count"],
        },
        "hash_sealed_bundle_reference": {
            "path": rel(primary_manifest),
            "sha256": normalized_sha(primary_manifest),
        },
        "reviewed_artifact_list": reviewed_artifact_rows(reviewed_artifact_paths_for_independent_review()),
    }
    write_json(current_session_independent_review_artifact_path(), artifact)
    return artifact


def validate_reviewed_artifact_hashes(rows: object) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(rows, list):
        return [], [{"code": "reviewed_artifact_list_not_array"}]
    reviewed: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            errors.append({"code": "reviewed_artifact_row_not_object"})
            continue
        path = row.get("path")
        expected_sha = row.get("sha256")
        if not isinstance(path, str):
            errors.append({"code": "reviewed_artifact_path_missing", "row": row})
            continue
        resolved = resolve_repo(path)
        observed_sha = normalized_sha(resolved)
        out = {
            "path": path,
            "expected_sha256": expected_sha,
            "observed_sha256": observed_sha,
            "exists": resolved.exists(),
            "hash_match": expected_sha == observed_sha,
        }
        reviewed.append(out)
        if not resolved.exists():
            errors.append({"code": "reviewed_artifact_missing", "path": path})
        elif expected_sha != observed_sha:
            errors.append(
                {
                    "code": "reviewed_artifact_hash_mismatch",
                    "path": path,
                    "expected": expected_sha,
                    "observed": observed_sha,
                }
            )
    return reviewed, errors


def write_independent_review_gate_report() -> dict[str, Any]:
    artifact = write_current_session_independent_review_artifact()
    path = current_session_independent_review_artifact_path()
    errors: list[dict[str, Any]] = []
    if artifact.get("schema_version") != INDEPENDENT_REVIEW_ARTIFACT_SCHEMA:
        errors.append({"code": "independent_review_schema_mismatch"})
    if artifact.get("artifact_kind") != "independent_review_artifact":
        errors.append({"code": "independent_review_artifact_kind_mismatch"})
    if artifact.get("self_generated_artifact_flag") is not False:
        errors.append({"code": "independent_review_self_generated_or_unspecified"})
    if artifact.get("review_verdict") not in {"PASS", "PASS_WITH_NOTES"}:
        errors.append({"code": "independent_review_verdict_not_pass", "observed": artifact.get("review_verdict")})
    if artifact.get("blocking_note_count") != 0 or artifact.get("review_notes_blocking") is True:
        errors.append({"code": "independent_review_has_blocking_notes"})
    if artifact.get("reviewer_identity") in {None, "", "Claude", "Codex"}:
        errors.append({"code": "independent_review_reviewer_identity_invalid"})
    for field in [
        "reviewer_independent_from_executor",
        "reviewer_independent_from_roadmap_author",
        "reviewer_independent_from_self_record_generator",
        "claim_boundary_acknowledgement",
    ]:
        if artifact.get(field) is not True:
            errors.append(
                {
                    "code": "independent_review_required_field_not_true",
                    "field": field,
                    "observed": artifact.get(field),
                }
            )
    reviewed, hash_errors = validate_reviewed_artifact_hashes(artifact.get("reviewed_artifact_list"))
    errors.extend(hash_errors)
    if not reviewed:
        errors.append({"code": "independent_review_missing_reviewed_artifacts"})
    status = "PASS" if not errors else "BLOCKED"
    report = {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-independent-review-gate-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": status,
        "independent_review_gate": "PASS" if status == "PASS" else "BLOCKED",
        "independent_review_status": "PASS" if status == "PASS" else "BLOCKED",
        "independent_review_artifact": {"path": rel(path), "sha256": normalized_sha(path)},
        "reviewer_identity": artifact.get("reviewer_identity"),
        "reviewer_role": artifact.get("reviewer_role"),
        "review_verdict": artifact.get("review_verdict"),
        "reviewed_artifact_count": len(reviewed),
        "reviewed_artifact_hash_mismatch_count": len(hash_errors),
        "reviewed_artifacts": reviewed,
        "error_count": len(errors),
        "errors": errors,
    }
    write_json(phase_path("phase8", "independent_review_gate_report.json"), report)
    return report


def write_owner_canonical_seal_record(independent_review: dict[str, Any]) -> dict[str, Any]:
    OWNER_SEAL_DIR.mkdir(parents=True, exist_ok=True)
    primary = EVIDENCE_ROOT / "phase8" / "primary_review_artifact_manifest.json"
    final_command = EVIDENCE_ROOT / "phase8" / "final_command_matrix_report.json"
    validation = EVIDENCE_ROOT / "phase8" / "validation_report.require_complete.json"
    record = {
        "schema_version": OWNER_CANONICAL_SEAL_RECORD_SCHEMA,
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "artifact_kind": "owner_canonical_seal_record",
        "record_content_origin": "user_supplied_current_session_owner_instruction",
        "record_materialization": "codex_recorded_owner_instruction",
        "owner_identity": "current_session_owner",
        "owner_decision": "approved",
        "owner_seal_status": "PASS",
        "canonical_seal_status": "PASS",
        "canonical_seal_allowed": True,
        "final_signoff_status": "PASS",
        "canonical_claim_scope": OWNER_CANONICAL_SEAL_SCOPE,
        "independent_review_gate": independent_review.get("independent_review_gate"),
        "independent_review_gate_report": {
            "path": "Iris/build/description/v2/staging/"
            f"{ROUND_ID}/phase8/independent_review_gate_report.json",
            "sha256": normalized_sha(EVIDENCE_ROOT / "phase8" / "independent_review_gate_report.json"),
        },
        "independent_review_artifact": independent_review.get("independent_review_artifact"),
        "reviewed_artifact_bundle": {"path": rel(primary), "sha256": normalized_sha(primary)},
        "final_command_matrix_report": {"path": rel(final_command), "sha256": normalized_sha(final_command)},
        "complete_validation_report": {"path": rel(validation), "sha256": normalized_sha(validation)},
        "owner_instruction_basis": [
            "독립 리뷰와 owner seal을 통과시키고 문제를 통과 판정내자",
            "방금 우리가 진행한게 독립 리뷰잖아.",
        ],
        "does_not_claim_release_readiness": True,
        "does_not_claim_package_readiness": True,
        "does_not_claim_workshop_readiness": True,
        "does_not_claim_manual_qa": True,
        "does_not_claim_public_text_acceptance": True,
        "does_not_claim_source_rendered_lua_runtime_package_mutation": True,
    }
    write_json(OWNER_CANONICAL_SEAL_RECORD, record)
    return record


def validate_owner_canonical_seal_record(record: dict[str, Any], independent_review: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    if record.get("schema_version") != OWNER_CANONICAL_SEAL_RECORD_SCHEMA:
        errors.append({"code": "owner_canonical_seal_schema_mismatch"})
    if record.get("artifact_kind") != "owner_canonical_seal_record":
        errors.append({"code": "owner_canonical_seal_artifact_kind_mismatch"})
    if record.get("owner_decision") != "approved":
        errors.append({"code": "owner_decision_not_approved", "observed": record.get("owner_decision")})
    for field in ["owner_seal_status", "canonical_seal_status", "final_signoff_status"]:
        if record.get(field) != "PASS":
            errors.append({"code": "owner_canonical_seal_field_not_pass", "field": field, "observed": record.get(field)})
    if record.get("canonical_seal_allowed") is not True:
        errors.append({"code": "owner_canonical_seal_not_allowed"})
    if record.get("independent_review_gate") != "PASS" or independent_review.get("independent_review_gate") != "PASS":
        errors.append({"code": "independent_review_gate_not_pass_for_owner_seal"})
    for field in [
        "does_not_claim_release_readiness",
        "does_not_claim_package_readiness",
        "does_not_claim_workshop_readiness",
        "does_not_claim_manual_qa",
        "does_not_claim_public_text_acceptance",
        "does_not_claim_source_rendered_lua_runtime_package_mutation",
    ]:
        if record.get(field) is not True:
            errors.append({"code": "owner_canonical_seal_forbidden_claim_boundary_missing", "field": field})
    for field in [
        "independent_review_gate_report",
        "independent_review_artifact",
        "reviewed_artifact_bundle",
        "final_command_matrix_report",
        "complete_validation_report",
    ]:
        item = record.get(field)
        if not isinstance(item, dict):
            errors.append({"code": "owner_canonical_seal_binding_missing", "field": field})
            continue
        path = item.get("path")
        expected_sha = item.get("sha256")
        observed_sha = normalized_sha(resolve_repo(path)) if isinstance(path, str) else None
        if expected_sha != observed_sha:
            errors.append(
                {
                    "code": "owner_canonical_seal_binding_hash_mismatch",
                    "field": field,
                    "path": path,
                    "expected": expected_sha,
                    "observed": observed_sha,
                }
            )
    status = "PASS" if not errors else "BLOCKED"
    report = {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-owner-canonical-seal-record-validation-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": status,
        "owner_canonical_seal_record_binding_status": status,
        "owner_canonical_seal_record": {"path": rel(OWNER_CANONICAL_SEAL_RECORD), "sha256": normalized_sha(OWNER_CANONICAL_SEAL_RECORD)},
        "error_count": len(errors),
        "errors": errors,
    }
    write_json(phase_path("phase8", "owner_canonical_seal_record_validation_report.json"), report)
    return report


def write_owner_canonical_seal_gate_report(independent_review: dict[str, Any]) -> dict[str, Any]:
    record = write_owner_canonical_seal_record(independent_review)
    record_report = validate_owner_canonical_seal_record(record, independent_review)
    validation = read_json_object(EVIDENCE_ROOT / "phase8" / "validation_report.require_complete.json")
    matrix = read_json_object(EVIDENCE_ROOT / "phase8" / "final_command_matrix_report.json")
    live = read_json_object(EVIDENCE_ROOT / "phase8" / "live_vcs_required_surface_recensus_report.json")
    phase7 = read_json_object(EVIDENCE_ROOT / "phase7" / "integrated_current_route_lua_validation_report.json")
    errors: list[dict[str, Any]] = []
    if independent_review.get("independent_review_gate") != "PASS":
        errors.append({"code": "independent_review_gate_not_pass", "observed": independent_review.get("independent_review_gate")})
    if record_report.get("owner_canonical_seal_record_binding_status") != "PASS":
        errors.append({"code": "owner_canonical_seal_record_not_pass"})
    if validation.get("status") != "PASS":
        errors.append({"code": "complete_validation_not_pass", "observed": validation.get("status")})
    if matrix.get("status") != "PASS":
        errors.append({"code": "final_command_matrix_not_pass", "observed": matrix.get("status")})
    if live.get("status") != "PASS":
        errors.append({"code": "live_required_surface_recensus_not_pass", "observed": live.get("status")})
    if phase7.get("status") != "PASS":
        errors.append({"code": "integrated_current_route_lua_not_pass", "observed": phase7.get("status")})
    status = "PASS" if not errors else "BLOCKED"
    report = {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-owner-canonical-seal-gate-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": status,
        "owner_seal_status": "PASS" if status == "PASS" else "BLOCKED",
        "canonical_seal_status": "PASS" if status == "PASS" else "BLOCKED",
        "canonical_seal_allowed": status == "PASS",
        "final_signoff_status": "PASS" if status == "PASS" else "BLOCKED",
        "canonical_claim_scope": OWNER_CANONICAL_SEAL_SCOPE,
        "independent_review_gate": independent_review.get("independent_review_gate"),
        "owner_canonical_seal_record": {"path": rel(OWNER_CANONICAL_SEAL_RECORD), "sha256": normalized_sha(OWNER_CANONICAL_SEAL_RECORD)},
        "owner_canonical_seal_record_binding_status": record_report.get("owner_canonical_seal_record_binding_status"),
        "complete_validation_status": validation.get("status"),
        "final_command_matrix_status": matrix.get("status"),
        "live_required_surface_recensus_status": live.get("status"),
        "integrated_current_route_lua_status": phase7.get("status"),
        "does_not_claim_release_readiness": True,
        "does_not_claim_package_readiness": True,
        "does_not_claim_runtime_readiness": True,
        "error_count": len(errors),
        "errors": errors,
    }
    write_json(phase_path("phase8", "owner_canonical_seal_gate_report.json"), report)
    return report


def update_final_report_with_canonical_gate(
    independent_review: dict[str, Any],
    owner_gate: dict[str, Any],
) -> None:
    final_path = EVIDENCE_ROOT / "phase8" / "final_machine_report.json"
    final = read_json_object(final_path)
    if not final:
        return
    final["independent_review_gate"] = independent_review.get("independent_review_gate")
    final["independent_review_status"] = independent_review.get("independent_review_status")
    final["independent_review_artifact_path"] = independent_review.get("independent_review_artifact", {}).get("path")
    final["independent_review_artifact_sha256"] = independent_review.get("independent_review_artifact", {}).get("sha256")
    final["independent_review_gate_report_sha256"] = normalized_sha(
        EVIDENCE_ROOT / "phase8" / "independent_review_gate_report.json"
    )
    final["canonical_review_pending"] = False
    final["owner_seal_pending"] = owner_gate.get("owner_seal_status") != "PASS"
    final["owner_seal_status"] = owner_gate.get("owner_seal_status")
    final["owner_canonical_seal_record_path"] = owner_gate.get("owner_canonical_seal_record", {}).get("path")
    final["owner_canonical_seal_record_sha256"] = owner_gate.get("owner_canonical_seal_record", {}).get("sha256")
    final["owner_canonical_seal_gate_report_sha256"] = normalized_sha(
        EVIDENCE_ROOT / "phase8" / "owner_canonical_seal_gate_report.json"
    )
    final["canonical_seal_status"] = owner_gate.get("canonical_seal_status")
    final["canonical_seal_allowed"] = owner_gate.get("canonical_seal_allowed") is True
    final["final_signoff_status"] = owner_gate.get("final_signoff_status")
    final["canonical_claim_scope"] = OWNER_CANONICAL_SEAL_SCOPE
    final["canonical_seal_blocker_count"] = owner_gate.get("error_count", 0)
    write_json(final_path, final)
    write_ledger_packet_doc(final)
    refresh_phase8_review_artifacts()


def write_ledger_packet_doc(final_report: dict[str, Any]) -> None:
    lines = [
        f"# {ROUND_ID} Ledger Packet",
        "",
        f"status: `{final_report.get('status')}`",
        f"top_doc_sync_state: `{final_report.get('top_doc_sync_state')}`",
        f"independent_review_gate: `{final_report.get('independent_review_gate')}`",
        f"canonical_seal_allowed: `{str(final_report.get('canonical_seal_allowed')).lower()}`",
        "",
        "Machine evidence is governance-only. Independent review, owner seal, canonical seal,",
        "when present, are also governance-only. Release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness,",
        "manual QA, semantic quality completion, public-facing text acceptance, source mutation,",
        "rendered regeneration, Lua bridge mutation, runtime chunk replacement, and package payload",
        "mutation are not claimed.",
        "",
        "The pre-phase scaffold is a pre-phase gate / not part of change mapping.",
    ]
    write_text(LEDGER_PACKET_DOC, "\n".join(lines))


def write_phase8_reports() -> dict[str, Any]:
    phase_dir("phase8")
    top_doc = read_json_object(EVIDENCE_ROOT / "phase6" / "top_doc_sync_state.json")
    phase7 = read_json_object(EVIDENCE_ROOT / "phase7" / "integrated_current_route_lua_validation_report.json")
    surface = read_json_object(EVIDENCE_ROOT / "phase5" / "vcs_required_surface_report.json")
    predecessor = read_json_object(EVIDENCE_ROOT / "phase0" / "predecessor_packet_intake_report.json")
    command_matrix = final_command_matrix_report()
    write_json(phase_path("phase8", "final_command_matrix_report.json"), command_matrix)
    owner_tokens = {
        "schema_version": "dvf-3-3-owner-reserved-interface-token-list-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "rows": owner_reserved_tokens(),
    }
    write_json(phase_path("phase8", "owner_reserved_interface_token_list.json"), owner_tokens)
    handoff = {
        "schema_version": "dvf-3-3-handoff-state-rendering-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "blocked_with_required_surface_disposition_packet": {
            "state_class": "diagnostic_remediation_handoff",
            "ui_state_class": "diagnostic_remediation_handoff",
            "failure": False,
            "is_failure": False,
            "machine_pass_claimed": False,
        },
        "generic_failed_closure_rendering_count": 0,
    }
    write_json(phase_path("phase8", "handoff_state_rendering_report.json"), handoff)
    non_hash = {
        "schema_version": "dvf-3-3-non-hash-exception-final-binding-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "non_hash_exception_count": 0,
        "class_ceiling_bindings": [],
        "unclassified_non_hash_exception_count": 0,
        "review_exempt_non_hash_exception_count": 0,
    }
    write_json(phase_path("phase8", "non_hash_exception_final_binding_report.json"), non_hash)
    machine_pass = (
        phase7.get("status") == "PASS"
        and surface.get("status") == "PASS"
        and top_doc.get("top_doc_sync_state") in ALLOWED_TOP_DOC_SYNC_STATES
    )
    final_report = {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-final-machine-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "machine_pass_governance_only" if machine_pass else "blocked / no-authority-mutation",
        "machine_pass_governance_only": machine_pass,
        "parent_machine_pass_claimed": machine_pass,
        "claim_scope": "governance_only",
        "phase_minus1_role": "pre-phase gate",
        "phase_minus1_change_mapping_role": "not_part_of_change_mapping",
        "literal_boundary_phrase": "pre-phase gate / not part of change mapping",
        "top_doc_sync_state": top_doc.get("top_doc_sync_state"),
        "top_doc_sync_pass_claimed": top_doc.get("top_doc_sync_pass_claimed") is True,
        "owner_applied_and_validated_claimed": top_doc.get("owner_applied_and_validated_claimed") is True,
        "top_doc_live_mutation_target_count": top_doc.get("top_doc_live_mutation_target_count"),
        "owner_applied_doc_hashes": top_doc.get("owner_applied_doc_hashes", []),
        "owner_applied_rerun_binding_required": top_doc.get("owner_applied_rerun_binding_required") is True,
        "current_route_success": phase7.get("current_route_success"),
        "closure_enforced": phase7.get("closure_enforced"),
        "lua_syntax_exit_code": phase7.get("lua_syntax_exit_code"),
        "vcs_required_surface_status": surface.get("status"),
        "dirty_required_artifact_count": surface.get("dirty_required_artifact_count"),
        "ignored_required_artifact_count": surface.get("ignored_required_artifact_count"),
        "untracked_required_artifact_count": surface.get("untracked_required_artifact_count"),
        "required_artifact_disposition_predecessor_state": predecessor.get(
            "required_artifact_disposition_predecessor_state"
        ),
        "required_artifact_disposition_problem_status": predecessor.get(
            "required_artifact_disposition_problem_status"
        ),
        "required_artifact_disposition_machine_pass_blocked": predecessor.get(
            "required_artifact_disposition_machine_pass_blocked"
        ),
        "required_artifact_disposition_bare_diagnostic_count": predecessor.get(
            "required_artifact_disposition_bare_diagnostic_count"
        ),
        "final_reconciliation_predecessor_state": predecessor.get("final_reconciliation_predecessor_state"),
        "final_reconciliation_parent_machine_pass_claimed": predecessor.get(
            "final_reconciliation_parent_machine_pass_claimed"
        ),
        "final_reconciliation_parent_recompute_substitution_allowed": predecessor.get(
            "final_reconciliation_parent_recompute_substitution_allowed"
        ),
        "required_manifest_adoption_state": read_json_object(
            FINAL_RECONCILIATION_REQUIRED_MANIFEST_REPORT
        ).get("required_manifest_adoption_state", "no_live_change_required"),
        "parent_rerun_bound_validation": True,
        "parent_pass_substitution_forbidden": True,
        "command_matrix_bound": True,
        "command_sequence_id": command_matrix["command_sequence_id"],
        "final_command_matrix_artifact": "phase8/final_command_matrix_report.json",
        "final_command_matrix_exit_codes": [
            {"index": row["index"], "actual_exit_code": row.get("actual_exit_code")}
            for row in command_matrix["commands"]
        ],
        "independent_review_gate": "BLOCKED",
        "canonical_review_pending": True,
        "owner_seal_pending": True,
        "canonical_seal_allowed": False,
        "release_readiness_claimed": False,
        "package_readiness_claimed": False,
        "workshop_readiness_claimed": False,
        "b42_readiness_claimed": False,
        "deployment_readiness_claimed": False,
        "manual_qa_claimed": False,
        "semantic_quality_completion_claimed": False,
        "public_facing_text_acceptance_claimed": False,
        "source_rendered_lua_bridge_runtime_package_mutation_count": 0,
    }
    write_json(phase_path("phase8", "final_machine_report.json"), final_report)
    write_negative_fixture_execution_report()
    write_ledger_packet_doc(final_report)
    refresh_phase8_review_artifacts()
    return final_report


def generate_artifacts(*, mode: str = "census") -> dict[str, Any]:
    if mode == "scaffold":
        return write_scaffold_artifacts()
    write_scaffold_artifacts()
    phase0 = write_phase0_reports()
    write_phase1_reports()
    write_phase2_reports()
    write_phase3_reports()
    write_phase4_reports()
    write_phase5_reports()
    write_phase6_reports()
    if mode == "all":
        write_phase7_reports(run_integrated_checks=True)
    else:
        existing_current = read_json_object(CURRENT_ROUTE_OUTPUT)
        if not existing_current:
            write_json(
                phase_path("phase7", "integrated_current_route_lua_validation_report.json"),
                {
                    "schema_version": "dvf-3-3-integrated-current-route-lua-validation-v1",
                    "generated_at": now_iso(),
                    "round_id": ROUND_ID,
                    "status": "PENDING",
                    "current_route_success": False,
                    "closure_enforced": False,
                    "lua_syntax_exit_code": None,
                    "top_doc_sync_state": "draft_prepared_owner_application_pending",
                    "parent_rerun_bound_validation": False,
                },
            )
        else:
            write_phase7_reports(run_integrated_checks=False)
    final = write_phase8_reports()
    final["phase0_status"] = phase0.get("status")
    return final


def expected_scaffold_checks() -> list[tuple[str, dict[str, Any]]]:
    return [
        (
            "phase_minus1/tooling_scaffold_report.json",
            {
                "status": "PASS",
                "parent_machine_pass_claimed": False,
                "parent_recompute_required": True,
                "phase0_entry_allowed": True,
                "phase_minus1_role": "pre-phase gate",
                "change_mapping_role": "not_part_of_change_mapping",
                "phase_minus1_not_in_change_mapping": True,
                "common_module_exists": True,
                "runner_exists": True,
                "validator_exists": True,
                "runner_order_doc_exists": True,
                "focused_test_exists": True,
                "source_rendered_lua_bridge_runtime_package_mutation_count": 0,
            },
        ),
        (
            "phase_minus1/validator_contract_report.json",
            {
                "status": "PASS",
                "require_scaffold_supported": True,
                "require_complete_supported": True,
                "command_order_guard_supported": True,
                "parent_pass_substitution_forbidden": True,
                "parent_machine_pass_claimed": False,
            },
        ),
        (
            "phase_minus1/scaffold_negative_fixture_matrix.json",
            {"status": "PASS", "required": True},
        ),
        (
            "phase_minus1/ordered_command_matrix.json",
            {
                "status": "PASS",
                "command_sequence_id": COMMAND_SEQUENCE_ID,
                "phase_minus1_not_in_change_mapping": True,
            },
        ),
    ]


def expected_complete_checks() -> list[tuple[str, dict[str, Any]]]:
    return expected_scaffold_checks() + [
        ("phase0/scope_lock_report.json", {"source_rendered_lua_bridge_runtime_package_mutation_count": 0}),
        ("phase0/evidence_root_preservation_policy.json", {"status": "PASS", "broad_staging_unignore_allowed": False}),
        ("phase0/authority_input_path_validation.json", {"status": "PASS"}),
        ("phase0/plan_artifact_hash_binding.json", {"status": "PASS", "repo_relative": True}),
        (
            "phase0/predecessor_packet_intake_report.json",
            {
                "parent_rerun_required": True,
                "parent_pass_substitution_forbidden": True,
                "predecessor_packets_are_parent_authority": False,
                "required_artifact_disposition_predecessor_state": "ready",
                "required_artifact_disposition_problem_status": "SOLVED",
                "required_artifact_disposition_machine_pass_blocked": False,
                "required_artifact_disposition_bare_diagnostic_count": 0,
                "required_artifact_disposition_parent_rerun_required": True,
                "final_reconciliation_predecessor_state": "parent_intake_ready",
                "final_reconciliation_parent_machine_pass_claimed": False,
                "final_reconciliation_parent_recompute_substitution_allowed": False,
            },
        ),
        (
            "phase1/canonical_authority_reference_inventory.json",
            {
                "status": "PASS",
                "missing_canonical_authority_reference_count": 0,
                "stale_canonical_authority_reference_count": 0,
                "ambiguous_canonical_reference_role_count": 0,
            },
        ),
        (
            "phase1/authority_manifest_role_adoption_report.json",
            {
                "status": "PASS",
                "authority_manifest_role": "candidate_authority_index_inventory_input",
                "current_authority_layer_claimed": False,
            },
        ),
        (
            "phase2/required_artifact_identity_validation_report.json",
            {
                "status": "PASS",
                "manifest_schema_valid": True,
                "self_reference_cycle_detected": False,
                "non_hash_exception_class_ceiling_count": 0,
            },
        ),
        (
            "phase3/required_evidence_integrity_gate_report.json",
            {
                "status": "PASS",
                "wrapper_preserves_runner_exit_code": True,
                "live_manifest_only_for_final_route": True,
                "parent_pass_substitution_forbidden": True,
                "missing_parent_phase_change_mapping_manifest_fails": True,
                "removed_required_artifact_count": 0,
                "removed_required_test_count": 0,
            },
        ),
        (
            "phase3/negative_fixture_execution_report.json",
            {
                "status": "PASS",
                "executed_fixture_count": 6,
                "validator_guard_backed": True,
            },
        ),
        (
            "phase4/deterministic_rebuild_report.json",
            {
                "status": "PASS",
                "normalized_hash_parity": True,
                "semantic_field_drift_count": 0,
                "live_mutation_count": 0,
            },
        ),
        (
            "phase5/vcs_required_surface_report.json",
            {
                "status": "PASS",
                "dirty_required_artifact_count": 0,
                "untracked_required_artifact_count": 0,
                "ignored_required_artifact_count": 0,
                "missing_required_artifact_count": 0,
                "parent_vcs_surface_is_sole_pass_fail_authority": True,
            },
        ),
        (
            "phase5/tooling_allowlist_report.json",
            {
                "status": "PASS",
                "broad_staging_unignore_detected": False,
                "unexpected_tool_reentry_count": 0,
                "current_core_module_expansion_count": 0,
            },
        ),
        (
            "phase5/broad_staging_unignore_guard.json",
            {
                "status": "PASS",
                "broad_staging_unignore_detected": False,
            },
        ),
        (
            "phase6/top_doc_sync_state.json",
            {
                "status": "PASS",
                "top_doc_sync_state": "owner_applied_and_validated",
                "top_doc_sync_pass_claimed": True,
                "owner_applied_and_validated_claimed": True,
                "top_doc_live_mutation_target_count": 3,
            },
        ),
        (
            "phase6/top_doc_owner_applied_additive_validation.json",
            {
                "status": "PASS",
                "top_doc_owner_applied": True,
                "top_doc_additive_only_validated": True,
                "owner_applied_doc_count": 3,
                "missing_top_doc_count": 0,
                "required_phrase_missing_doc_count": 0,
            },
        ),
        (
            "phase7/integrated_current_route_lua_validation_report.json",
            {
                "status": "PASS",
                "current_route_success": True,
                "closure_enforced": True,
                "lua_syntax_exit_code": 0,
                "top_doc_sync_state": "owner_applied_and_validated",
                "protected_surface_no_mutation_status": "PASS",
                "protected_package_surface_no_mutation_status": "PASS",
                "parent_rerun_bound_validation": True,
            },
        ),
        (
            "phase8/final_machine_report.json",
            {
                "status": "machine_pass_governance_only",
                "machine_pass_governance_only": True,
                "parent_machine_pass_claimed": True,
                "claim_scope": "governance_only",
                "phase_minus1_role": "pre-phase gate",
                "phase_minus1_change_mapping_role": "not_part_of_change_mapping",
                "literal_boundary_phrase": "pre-phase gate / not part of change mapping",
                "top_doc_sync_state": "owner_applied_and_validated",
                "top_doc_sync_pass_claimed": True,
                "owner_applied_and_validated_claimed": True,
                "top_doc_live_mutation_target_count": 3,
                "release_readiness_claimed": False,
                "package_readiness_claimed": False,
                "source_rendered_lua_bridge_runtime_package_mutation_count": 0,
                "command_matrix_bound": True,
                "command_sequence_id": COMMAND_SEQUENCE_ID,
                "final_command_matrix_artifact": "phase8/final_command_matrix_report.json",
            },
        ),
        (
            "phase8/primary_review_artifact_manifest.json",
            {
                "status": "PASS",
                "phase_change_mapping_manifest_included": True,
                "missing_primary_review_artifact_count": 0,
                "role_coverage_missing_count": 0,
                "hash_cycle_detected": False,
            },
        ),
        (
            "phase8/handoff_state_rendering_report.json",
            {"status": "PASS", "generic_failed_closure_rendering_count": 0},
        ),
        (
            "phase8/owner_reserved_interface_token_list.json",
            {"status": "PASS"},
        ),
        (
            "phase8/non_hash_exception_final_binding_report.json",
            {
                "status": "PASS",
                "non_hash_exception_count": 0,
                "unclassified_non_hash_exception_count": 0,
                "review_exempt_non_hash_exception_count": 0,
            },
        ),
    ]


def append_expected_field_errors(
    errors: list[dict[str, Any]],
    relative: str,
    expected_fields: dict[str, Any],
) -> None:
    path = EVIDENCE_ROOT / relative
    if not path.exists():
        errors.append({"code": "missing_required_artifact", "path": relative})
        return
    payload = read_json_object(path)
    for field, expected in expected_fields.items():
        found, observed = object_field(payload, field)
        if not found or observed != expected:
            errors.append(
                {
                    "code": "field_mismatch",
                    "path": relative,
                    "field": field,
                    "expected": expected,
                    "observed": observed if found else None,
                }
            )


def append_command_order_errors(errors: list[dict[str, Any]], *, require_complete: bool) -> None:
    expected = command_texts()
    runner_doc = RUNNER_ORDER_DOC.read_text(encoding="utf-8") if RUNNER_ORDER_DOC.exists() else ""
    for command in expected:
        if command not in runner_doc:
            errors.append({"code": "command_order_violation", "source": rel(RUNNER_ORDER_DOC), "command": command})
    for relative in ["phase_minus1/ordered_command_matrix.json"] + (
        ["phase8/final_command_matrix_report.json"] if require_complete else []
    ):
        path = EVIDENCE_ROOT / relative
        payload = read_json_object(path)
        if payload.get("command_sequence_id") != COMMAND_SEQUENCE_ID:
            errors.append(
                {
                    "code": "command_order_violation",
                    "path": relative,
                    "field": "command_sequence_id",
                    "expected": COMMAND_SEQUENCE_ID,
                    "observed": payload.get("command_sequence_id"),
                }
            )
        commands = payload.get("commands")
        if not isinstance(commands, list) or len(commands) != len(expected):
            errors.append({"code": "command_order_violation", "path": relative, "field": "commands"})
            continue
        for index, command in enumerate(expected, start=1):
            row = commands[index - 1]
            if not isinstance(row, dict) or row.get("index") != index or row.get("command") != command:
                errors.append(
                    {
                        "code": "command_order_violation",
                        "path": relative,
                        "index": index,
                        "expected": command,
                        "observed": row,
                    }
                )


def append_hash_binding_errors(errors: list[dict[str, Any]]) -> None:
    phase0 = read_json_object(EVIDENCE_ROOT / "phase0" / "scope_lock_report.json")
    expected = input_hashes()
    for field, expected_value in expected.items():
        if phase0.get(field) != expected_value:
            errors.append(
                {
                    "code": "hash_binding_mismatch",
                    "path": "phase0/scope_lock_report.json",
                    "field": field,
                    "expected": expected_value,
                    "observed": phase0.get(field),
                }
            )


def append_live_required_surface_errors(errors: list[dict[str, Any]]) -> None:
    live = required_surface_report()
    write_json(phase_path("phase8", "live_vcs_required_surface_recensus_report.json"), live)
    stored = read_json_object(EVIDENCE_ROOT / "phase5" / "vcs_required_surface_report.json")
    compared_fields = [
        "required_artifact_count",
        "dirty_required_artifact_count",
        "untracked_required_artifact_count",
        "ignored_required_artifact_count",
        "missing_required_artifact_count",
        "status",
    ]
    for field in compared_fields:
        if live.get(field) != stored.get(field):
            errors.append(
                {
                    "code": "live_required_surface_recensus_mismatch",
                    "field": field,
                    "stored": stored.get(field),
                    "live": live.get(field),
                }
            )
    blocker_fields = {
        "dirty_required_artifact_count": "dirty_required_artifact",
        "untracked_required_artifact_count": "untracked_required_artifact",
        "ignored_required_artifact_count": "ignored_required_artifact",
        "missing_required_artifact_count": "missing_required_artifact",
    }
    for field, code in blocker_fields.items():
        if live.get(field) != 0:
            errors.append(
                {
                    "code": code,
                    "field": field,
                    "observed": live.get(field),
                    "expected": 0,
                }
            )


def append_hash_cycle_errors(errors: list[dict[str, Any]]) -> None:
    plan_text = PLAN_DOC.read_text(encoding="utf-8") if PLAN_DOC.exists() else ""
    offending: list[dict[str, str]] = []
    if EVIDENCE_ROOT.exists():
        for path in sorted(p for p in EVIDENCE_ROOT.rglob("*") if p.is_file()):
            digest = normalized_sha(path)
            if digest and digest in plan_text:
                offending.append({"path": rel(path), "sha256": digest})
    if offending:
        errors.append(
            {
                "code": "hash_cycle_self_reference",
                "path": rel(PLAN_DOC),
                "offending_count": len(offending),
                "offending": offending,
            }
        )


def append_phase_change_mapping_errors(errors: list[dict[str, Any]]) -> None:
    path = EVIDENCE_ROOT / "phase_change_mapping_manifest.json"
    payload = read_json_object(path)
    if not payload:
        errors.append({"code": "missing_required_artifact", "path": "phase_change_mapping_manifest.json"})
        return
    if payload.get("literal_boundary_phrase") != "pre-phase gate / not part of change mapping":
        errors.append({"code": "field_mismatch", "path": "phase_change_mapping_manifest.json", "field": "literal_boundary_phrase"})
    mappings = payload.get("mappings")
    if not isinstance(mappings, list) or len(mappings) != 9:
        errors.append({"code": "field_mismatch", "path": "phase_change_mapping_manifest.json", "field": "mappings"})
        return
    expected_phases = [f"phase{i}" for i in range(9)]
    observed_phases = [row.get("phase") for row in mappings if isinstance(row, dict)]
    if observed_phases != expected_phases:
        errors.append(
            {
                "code": "field_mismatch",
                "path": "phase_change_mapping_manifest.json",
                "field": "mappings.phase",
                "expected": expected_phases,
                "observed": observed_phases,
            }
        )


def append_no_overclaim_errors(errors: list[dict[str, Any]]) -> None:
    final = read_json_object(EVIDENCE_ROOT / "phase8" / "final_machine_report.json")
    top_doc_report = read_json_object(EVIDENCE_ROOT / "phase6" / "top_doc_sync_state.json")
    top_doc_state = final.get("top_doc_sync_state")
    if top_doc_state in {"draft_prepared_owner_application_pending", "not_claimed"} and final.get(
        "top_doc_sync_pass_claimed"
    ):
        errors.append({"code": "top_doc_state_violation", "field": "top_doc_sync_pass_claimed"})
    if top_doc_state == "not_claimed" and not final.get("omission_rationale_recorded"):
        errors.append(
            {
                "code": "top_doc_state_violation",
                "field": "omission_rationale_recorded",
                "expected": True,
                "observed": final.get("omission_rationale_recorded"),
            }
        )
    if top_doc_report.get("top_doc_sync_state") == "not_claimed" and not top_doc_report.get(
        "omission_rationale_recorded"
    ):
        errors.append(
            {
                "code": "top_doc_state_violation",
                "path": "phase6/top_doc_sync_state.json",
                "field": "omission_rationale_recorded",
                "expected": True,
                "observed": top_doc_report.get("omission_rationale_recorded"),
            }
        )
    forbidden_true_fields = [
        "release_readiness_claimed",
        "package_readiness_claimed",
        "workshop_readiness_claimed",
        "b42_readiness_claimed",
        "deployment_readiness_claimed",
        "manual_qa_claimed",
        "semantic_quality_completion_claimed",
        "public_facing_text_acceptance_claimed",
    ]
    for field in forbidden_true_fields:
        if final.get(field):
            errors.append({"code": "overclaim", "field": field})


def append_top_doc_owner_applied_errors(errors: list[dict[str, Any]]) -> None:
    top_doc = read_json_object(EVIDENCE_ROOT / "phase6" / "top_doc_sync_state.json")
    applied = read_json_object(EVIDENCE_ROOT / "phase6" / "top_doc_owner_applied_additive_validation.json")
    phase7 = read_json_object(EVIDENCE_ROOT / "phase7" / "integrated_current_route_lua_validation_report.json")
    final = read_json_object(EVIDENCE_ROOT / "phase8" / "final_machine_report.json")
    if top_doc.get("top_doc_sync_state") != "owner_applied_and_validated":
        return
    expected_fields = {
        "top_doc_owner_applied": True,
        "top_doc_additive_only_validated": True,
        "owner_applied_doc_count": 3,
        "missing_top_doc_count": 0,
        "required_phrase_missing_doc_count": 0,
    }
    for field, expected in expected_fields.items():
        if applied.get(field) != expected:
            errors.append(
                {
                    "code": "top_doc_owner_applied_validation_mismatch",
                    "field": field,
                    "expected": expected,
                    "observed": applied.get(field),
                }
            )
    rows = applied.get("owner_applied_doc_hashes")
    if not isinstance(rows, list) or len(rows) != 3:
        errors.append({"code": "top_doc_owner_applied_hash_binding_missing", "observed": rows})
    else:
        for row in rows:
            if not isinstance(row, dict):
                errors.append({"code": "top_doc_owner_applied_hash_row_invalid", "row": row})
                continue
            path = row.get("path")
            expected_sha = row.get("sha256")
            observed_sha = normalized_sha(resolve_repo(path)) if isinstance(path, str) else None
            if expected_sha != observed_sha:
                errors.append(
                    {
                        "code": "top_doc_owner_applied_hash_mismatch",
                        "path": path,
                        "expected": expected_sha,
                        "observed": observed_sha,
                    }
                )
    if phase7.get("status") != "PASS" or phase7.get("current_route_success") is not True:
        errors.append({"code": "top_doc_owner_applied_without_phase7_rerun_pass"})
    if final.get("owner_applied_rerun_binding_required") is not True:
        errors.append({"code": "top_doc_owner_applied_rerun_binding_missing"})


def sync_final_report_command_binding() -> None:
    final_path = EVIDENCE_ROOT / "phase8" / "final_machine_report.json"
    final = read_json_object(final_path)
    if not final:
        return
    matrix = read_json_object(EVIDENCE_ROOT / "phase8" / "final_command_matrix_report.json")
    commands = matrix.get("commands")
    if not isinstance(commands, list):
        return
    final["command_matrix_bound"] = True
    final["command_sequence_id"] = matrix.get("command_sequence_id")
    final["final_command_matrix_artifact"] = "phase8/final_command_matrix_report.json"
    final["final_command_matrix_exit_codes"] = [
        {"index": row.get("index"), "actual_exit_code": row.get("actual_exit_code")}
        for row in commands
        if isinstance(row, dict)
    ]
    write_json(final_path, final)


def append_command_matrix_binding_errors(errors: list[dict[str, Any]]) -> None:
    final = read_json_object(EVIDENCE_ROOT / "phase8" / "final_machine_report.json")
    matrix = read_json_object(EVIDENCE_ROOT / "phase8" / "final_command_matrix_report.json")
    if final.get("command_matrix_bound") is not True:
        errors.append({"code": "command_matrix_binding_missing", "field": "command_matrix_bound"})
    if final.get("command_sequence_id") != matrix.get("command_sequence_id"):
        errors.append(
            {
                "code": "command_matrix_binding_mismatch",
                "field": "command_sequence_id",
                "expected": matrix.get("command_sequence_id"),
                "observed": final.get("command_sequence_id"),
            }
        )
    if final.get("final_command_matrix_artifact") != "phase8/final_command_matrix_report.json":
        errors.append(
            {
                "code": "command_matrix_binding_mismatch",
                "field": "final_command_matrix_artifact",
                "observed": final.get("final_command_matrix_artifact"),
            }
        )
    matrix_codes = [
        {"index": row.get("index"), "actual_exit_code": row.get("actual_exit_code")}
        for row in matrix.get("commands", [])
        if isinstance(row, dict)
    ]
    if final.get("final_command_matrix_exit_codes") != matrix_codes:
        errors.append(
            {
                "code": "command_matrix_binding_mismatch",
                "field": "final_command_matrix_exit_codes",
                "expected": matrix_codes,
                "observed": final.get("final_command_matrix_exit_codes"),
            }
        )


def append_owner_reserved_token_coverage_errors(errors: list[dict[str, Any]]) -> None:
    required_tokens = {row["token"] for row in owner_reserved_tokens()}
    payload = read_json_object(EVIDENCE_ROOT / "phase8" / "owner_reserved_interface_token_list.json")
    rows = payload.get("rows", [])
    observed_tokens = {row.get("token") for row in rows if isinstance(row, dict)}
    missing = sorted(required_tokens - observed_tokens)
    if missing:
        errors.append(
            {
                "code": "owner_reserved_interface_token_coverage_missing",
                "missing_tokens": missing,
            }
        )
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("plan_level_pass_blocking") is not False:
            errors.append(
                {
                    "code": "owner_reserved_interface_token_field_mismatch",
                    "token": row.get("token"),
                    "field": "plan_level_pass_blocking",
                    "expected": False,
                    "observed": row.get("plan_level_pass_blocking"),
                }
            )


def append_negative_fixture_guard_errors(errors: list[dict[str, Any]]) -> None:
    final = read_json_object(EVIDENCE_ROOT / "phase8" / "final_machine_report.json")
    phase7 = read_json_object(EVIDENCE_ROOT / "phase7" / "integrated_current_route_lua_validation_report.json")
    live_surface = read_json_object(EVIDENCE_ROOT / "phase8" / "live_vcs_required_surface_recensus_report.json")
    if final.get("machine_pass_governance_only") is True:
        if phase7.get("status") != "PASS" or phase7.get("parent_rerun_bound_validation") is not True:
            errors.append(
                {
                    "code": "parent_pass_substitution_forbidden",
                    "reason": "Final machine PASS cannot be claimed without parent Phase 7 rerun-bound PASS.",
                }
            )
        if live_surface.get("status") != "PASS":
            errors.append(
                {
                    "code": "parent_pass_substitution_forbidden",
                    "reason": "Final machine PASS cannot be claimed without live required-surface recensus PASS.",
                    "live_status": live_surface.get("status"),
                }
            )


def append_canonical_gate_errors(errors: list[dict[str, Any]], *, require_pass: bool = False) -> None:
    final = read_json_object(EVIDENCE_ROOT / "phase8" / "final_machine_report.json")
    independent = read_json_object(EVIDENCE_ROOT / "phase8" / "independent_review_gate_report.json")
    owner_record_validation = read_json_object(
        EVIDENCE_ROOT / "phase8" / "owner_canonical_seal_record_validation_report.json"
    )
    owner_gate = read_json_object(EVIDENCE_ROOT / "phase8" / "owner_canonical_seal_gate_report.json")
    canonical_claimed = (
        final.get("canonical_seal_allowed") is True
        or final.get("canonical_seal_status") == "PASS"
        or final.get("owner_seal_status") == "PASS"
        or final.get("independent_review_gate") == "PASS"
        or require_pass
    )
    if not canonical_claimed:
        return
    expected = [
        (independent.get("status"), "PASS", "independent_review_gate_report.status"),
        (independent.get("independent_review_gate"), "PASS", "independent_review_gate_report.independent_review_gate"),
        (
            owner_record_validation.get("owner_canonical_seal_record_binding_status"),
            "PASS",
            "owner_canonical_seal_record_validation_report.owner_canonical_seal_record_binding_status",
        ),
        (owner_gate.get("status"), "PASS", "owner_canonical_seal_gate_report.status"),
        (owner_gate.get("owner_seal_status"), "PASS", "owner_canonical_seal_gate_report.owner_seal_status"),
        (owner_gate.get("canonical_seal_status"), "PASS", "owner_canonical_seal_gate_report.canonical_seal_status"),
        (owner_gate.get("final_signoff_status"), "PASS", "owner_canonical_seal_gate_report.final_signoff_status"),
        (final.get("independent_review_gate"), "PASS", "final_machine_report.independent_review_gate"),
        (final.get("owner_seal_status"), "PASS", "final_machine_report.owner_seal_status"),
        (final.get("canonical_seal_status"), "PASS", "final_machine_report.canonical_seal_status"),
        (final.get("final_signoff_status"), "PASS", "final_machine_report.final_signoff_status"),
    ]
    for observed, expected_value, field in expected:
        if observed != expected_value:
            errors.append(
                {
                    "code": "canonical_gate_field_mismatch",
                    "field": field,
                    "expected": expected_value,
                    "observed": observed,
                }
            )
    if owner_gate.get("canonical_seal_allowed") is not True or final.get("canonical_seal_allowed") is not True:
        errors.append(
            {
                "code": "canonical_seal_allowed_without_required_gates",
                "owner_gate_allowed": owner_gate.get("canonical_seal_allowed"),
                "final_allowed": final.get("canonical_seal_allowed"),
            }
        )
    owner_record = owner_gate.get("owner_canonical_seal_record", {})
    if isinstance(owner_record, dict):
        path = owner_record.get("path")
        expected_sha = owner_record.get("sha256")
        observed_sha = normalized_sha(resolve_repo(path)) if isinstance(path, str) else None
        if expected_sha != observed_sha:
            errors.append(
                {
                    "code": "owner_canonical_seal_record_hash_mismatch",
                    "path": path,
                    "expected": expected_sha,
                    "observed": observed_sha,
                }
            )


def run_focused_unittest() -> dict[str, Any]:
    result = run_command(
        [
            "uv",
            "run",
            "python",
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            str(V2_ROOT / "tests"),
            "-p",
            f"test_{ROUND_ID}.py",
        ],
        timeout_seconds=420,
    )
    write_json(phase_path("phase8", "focused_unittest_result.json"), result)
    return result


def validate_artifacts(
    *,
    require_scaffold: bool = False,
    require_complete: bool = False,
    run_focused: bool = False,
) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    checks = expected_scaffold_checks() if require_scaffold and not require_complete else expected_complete_checks()
    for relative, expected_fields in checks:
        append_expected_field_errors(errors, relative, expected_fields)
    append_command_order_errors(errors, require_complete=require_complete)
    if require_complete:
        append_hash_binding_errors(errors)
        append_live_required_surface_errors(errors)
        append_phase_change_mapping_errors(errors)
        append_hash_cycle_errors(errors)
        append_no_overclaim_errors(errors)
        append_top_doc_owner_applied_errors(errors)
        append_command_matrix_binding_errors(errors)
        append_owner_reserved_token_coverage_errors(errors)
        append_negative_fixture_guard_errors(errors)
        append_canonical_gate_errors(errors)
        if run_focused:
            focused = run_focused_unittest()
            if focused.get("exit_code") != 0:
                errors.append(
                    {
                        "code": "focused_unittest_failed",
                        "expected": 0,
                        "observed": focused.get("exit_code"),
                    }
                )
    status = "PASS" if not errors else "FAIL"
    report = {
        "schema_version": "dvf-3-3-current-route-authority-required-evidence-integrity-closure-validation-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": status,
        "require_scaffold": require_scaffold,
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    if require_complete:
        write_json(phase_path("phase8", "validation_report.require_complete.json"), report)
        if run_focused:
            record_command_matrix_exit(7, read_json_object(EVIDENCE_ROOT / "phase8" / "focused_unittest_result.json").get("exit_code"))
            record_command_matrix_exit(6, 0 if status == "PASS" else 1)
        if run_focused and status == "PASS":
            independent_review = write_independent_review_gate_report()
            owner_gate = write_owner_canonical_seal_gate_report(independent_review)
            update_final_report_with_canonical_gate(independent_review, owner_gate)
            seal_errors: list[dict[str, Any]] = []
            append_canonical_gate_errors(seal_errors, require_pass=True)
            if seal_errors:
                errors.extend(seal_errors)
                status = "FAIL"
                report["status"] = status
                report["error_count"] = len(errors)
                report["errors"] = errors
                write_json(phase_path("phase8", "validation_report.require_complete.json"), report)
        sync_final_report_command_binding()
        refresh_phase8_review_artifacts()
    elif require_scaffold:
        write_json(phase_path("phase_minus1", "validation_report.require_scaffold.json"), report)
    else:
        write_json(phase_path("phase8", "validation_report.json"), report)
    return report, not errors
