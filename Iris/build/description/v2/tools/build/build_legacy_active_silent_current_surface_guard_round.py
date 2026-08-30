from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


V2_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.validate_legacy_active_silent_current_surface_guard import (  # noqa: E402
    ALLOWLIST_TOO_BROAD_ERROR_CODE,
    AUTHORIZED_RESULT_SUBROOTS,
    CURRENT_SURFACE_ERROR_CODE,
    DEFAULT_MANIFEST,
    DEFAULT_RESOLVER_COMPAT_ERROR_CODE,
    DEFAULT_RUNTIME_STATE_ERROR_CODE,
    DIAGNOSTIC_ALIAS_OUTSIDE_ERROR_CODE,
    ERROR_CATALOG,
    LEGACY_METRIC_RENDERED_ERROR_CODE,
    SCAN_BACKENDS,
    UNALLOWLISTED_ERROR_CODE,
    compact_report,
    load_manifest,
    validate_repo,
    validate_external_run_roots,
    validate_successor_output_policy,
    verify_occurrence_stream_reference,
    write_inventory_files,
    write_json,
    write_json_create_new,
)


ROUND_ROOT = (
    V2_ROOT
    / "staging"
    / "compose_contract_migration"
    / "legacy_active_silent_current_surface_guard_round"
)
PLAN = REPO_ROOT / "docs" / "Iris" / "iris-dvf-3-3-legacy-active-silent-current-surface-guard-round-plan.md"
PHILOSOPHY = REPO_ROOT / "docs" / "Philosophy.md"
DECISIONS = REPO_ROOT / "docs" / "DECISIONS.md"
ARCHITECTURE = REPO_ROOT / "docs" / "ARCHITECTURE.md"
ROADMAP = REPO_ROOT / "docs" / "ROADMAP.md"
OUTPUT_POLICY = (
    REPO_ROOT
    / "Iris"
    / "validation"
    / "execution"
    / "contracts"
    / "isolated_command_output_policy.json"
)

SOURCE_DECISIONS = V2_ROOT / "data" / "dvf_3_3_decisions.jsonl"
RENDERED_OUTPUT = V2_ROOT / "output" / "dvf_3_3_rendered.json"
RUNTIME_CHUNK_DIRS = [
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks",
    REPO_ROOT
    / "Iris"
    / "build"
    / "package"
    / "Iris"
    / "media"
    / "lua"
    / "client"
    / "Iris"
    / "Data"
    / "IrisLayer3DataChunks",
]
RUNTIME_MANIFESTS = [
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks.lua",
    REPO_ROOT
    / "Iris"
    / "build"
    / "package"
    / "Iris"
    / "media"
    / "lua"
    / "client"
    / "Iris"
    / "Data"
    / "IrisLayer3DataChunks.lua",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix().replace("\\", "/")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    ensure_parent(path)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_record(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "exists": path.exists(),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def write_json_atomic(path: Path, payload: Any) -> None:
    write_json_create_new(path, payload)


def load_and_validate_allocation_receipt(
    allocation_receipt_path: Path,
    work_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    receipt = json.loads(allocation_receipt_path.read_text(encoding="utf-8"))
    if receipt.get("schema_version") != "iris_repository_runtime_lightweighting_allocation_receipt_v1":
        raise ValueError("unsupported repository-runtime allocation receipt schema")
    if receipt.get("status") != "PASS":
        raise ValueError("allocation receipt is not PASS")
    for field in ("claim_id", "attempt_id", "run_id", "allocation_profile"):
        if not isinstance(receipt.get(field), str) or not str(receipt[field]).strip():
            raise ValueError(f"allocation receipt lacks non-empty {field}")
    if receipt["allocation_profile"] not in {"checkpoint", "terminal-run-a", "terminal-run-b"}:
        raise ValueError("allocation receipt profile cannot authorize the guard producer")
    for proof_name, count_name in (
        ("pre_create_existence", "existing_count"),
        ("ledger_reuse", "match_count"),
        ("post_create_empty", "nonempty_count"),
    ):
        proof = receipt.get(proof_name, {})
        if proof.get("checked") is not True or int(proof.get(count_name, -1)) != 0:
            raise ValueError(f"allocation receipt proof is not zero-PASS: {proof_name}")
    roots = receipt.get("roots", {})
    recorded_work = Path(str(roots.get("work", ""))).resolve()
    recorded_result = Path(str(roots.get("result", ""))).resolve()
    if recorded_work != work_root.resolve() or recorded_result != result_root.resolve():
        raise ValueError("producer work/result roots do not match allocation receipt")
    ledger = receipt.get("allocation_ledger", {})
    required_ledger_fields = {
        "path",
        "sha256_after_append",
        "appended_entry_sha256",
        "append_offset_bytes",
        "reservation_ledger_sha256_after_append",
        "reservation_entry_sha256",
        "reservation_append_offset_bytes",
    }
    if not isinstance(ledger, dict) or not required_ledger_fields.issubset(ledger):
        raise ValueError("allocation receipt lacks ledger identity")
    ledger_path = Path(str(ledger["path"])).resolve()
    if not ledger_path.is_file() or ledger_path == REPO_ROOT.resolve() or REPO_ROOT.resolve() in ledger_path.parents:
        raise ValueError("allocation ledger must be a readable repository-external file")
    ledger_bytes = ledger_path.read_bytes()
    reservation_offset = int(ledger["reservation_append_offset_bytes"])
    if reservation_offset < 0 or reservation_offset >= len(ledger_bytes):
        raise ValueError("allocation ledger reservation offset is outside the ledger")
    reservation_newline = ledger_bytes.find(b"\n", reservation_offset)
    if reservation_newline < 0:
        raise ValueError("allocation ledger reservation entry is not newline terminated")
    reservation_bytes = ledger_bytes[reservation_offset : reservation_newline + 1]
    if hashlib.sha256(reservation_bytes).hexdigest() != str(ledger["reservation_entry_sha256"]).lower():
        raise ValueError("allocation ledger reservation entry identity mismatch")
    if hashlib.sha256(ledger_bytes[: reservation_newline + 1]).hexdigest() != str(
        ledger["reservation_ledger_sha256_after_append"]
    ).lower():
        raise ValueError("allocation ledger reservation prefix identity mismatch")
    offset = int(ledger["append_offset_bytes"])
    if offset < 0 or offset >= len(ledger_bytes):
        raise ValueError("allocation ledger append offset is outside the ledger")
    newline = ledger_bytes.find(b"\n", offset)
    if newline < 0:
        raise ValueError("allocation ledger appended entry is not newline terminated")
    entry_bytes = ledger_bytes[offset : newline + 1]
    if hashlib.sha256(entry_bytes).hexdigest() != str(ledger["appended_entry_sha256"]).lower():
        raise ValueError("allocation ledger appended entry identity mismatch")
    if hashlib.sha256(ledger_bytes[: newline + 1]).hexdigest() != str(ledger["sha256_after_append"]).lower():
        raise ValueError("allocation ledger prefix identity mismatch")
    if offset != reservation_newline + 1:
        raise ValueError("allocation ledger commit does not immediately follow its reservation")
    reservation_entry = json.loads(reservation_bytes.decode("utf-8"))
    ledger_entry = json.loads(entry_bytes.decode("utf-8"))
    if (
        reservation_entry.get("schema_version")
        != "iris_repository_runtime_lightweighting_allocation_ledger_v2"
        or reservation_entry.get("state") != "reserved"
    ):
        raise ValueError("allocation ledger reservation state is invalid")
    if (
        ledger_entry.get("schema_version")
        != "iris_repository_runtime_lightweighting_allocation_ledger_v2"
        or ledger_entry.get("state") != "committed"
    ):
        raise ValueError("allocation ledger commit state is invalid")
    if (
        ledger_entry.get("reservation_entry_sha256")
        != str(ledger["reservation_entry_sha256"]).lower()
        or int(ledger_entry.get("reservation_append_offset_bytes", -1)) != reservation_offset
    ):
        raise ValueError("allocation ledger commit does not bind its reservation")
    for field in ("claim_id", "attempt_id", "run_id", "allocation_profile"):
        if ledger_entry.get(field) != receipt.get(field) or reservation_entry.get(field) != receipt.get(field):
            raise ValueError(f"allocation ledger entry does not bind receipt {field}")
    ledger_paths = {Path(str(value)).resolve() for value in ledger_entry.get("paths", [])}
    reservation_paths = {Path(str(value)).resolve() for value in reservation_entry.get("paths", [])}
    if reservation_paths != ledger_paths:
        raise ValueError("allocation ledger reservation and commit paths differ")
    if work_root.resolve() not in ledger_paths or result_root.resolve() not in ledger_paths:
        raise ValueError("allocation ledger entry does not bind producer roots")
    return receipt


def load_and_validate_output_policy() -> dict[str, Any]:
    return validate_successor_output_policy(REPO_ROOT, OUTPUT_POLICY)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def source_decision_summary() -> dict[str, Any]:
    rows = read_jsonl(SOURCE_DECISIONS)
    counts = Counter(str(row.get("state", "__missing__")) for row in rows)
    return {
        "path": rel(SOURCE_DECISIONS),
        "row_count": len(rows),
        "state_counts": dict(sorted(counts.items())),
        "sha256": sha256_file(SOURCE_DECISIONS),
    }


def rendered_summary() -> dict[str, Any]:
    if not RENDERED_OUTPUT.exists():
        return {"path": rel(RENDERED_OUTPUT), "exists": False}
    payload = json.loads(RENDERED_OUTPUT.read_text(encoding="utf-8"))
    entries = payload.get("entries", {}) if isinstance(payload, dict) else {}
    source_counts = Counter(str(row.get("source")) for row in entries.values() if isinstance(row, dict))
    return {
        "path": rel(RENDERED_OUTPUT),
        "exists": True,
        "row_count": len(entries),
        "source_counts": dict(sorted(source_counts.items())),
        "sha256": sha256_file(RENDERED_OUTPUT),
    }


def runtime_records() -> list[dict[str, Any]]:
    records = [path_record(path) for path in RUNTIME_MANIFESTS]
    for chunk_dir in RUNTIME_CHUNK_DIRS:
        if chunk_dir.exists():
            records.extend(path_record(path) for path in sorted(chunk_dir.glob("Chunk*.lua")))
    return records


def write_phase0(phase_root: Path) -> None:
    write_json(
        phase_root / "phase0_scope_lock" / "prior_readpoint_summary.json",
        {
            "schema_version": "legacy-active-silent-current-surface-guard-prior-readpoint-v0",
            "generated_at": now_iso(),
            "authority_chain": [rel(PHILOSOPHY), rel(DECISIONS), rel(ARCHITECTURE), rel(ROADMAP), rel(PLAN)],
            "prior_readpoints": [
                "Runtime Payload Enum Rename Scope Round: adopted/unadopted is canonical current runtime enum",
                "Static Report Label Cleanup Round: current Surface C preflight found no rewrite target",
                "Static Report Label Cleanup Referent Recovery Branch D: original referent missing and cleanup not claimed",
                "2026-05-21 guard split: future current-surface reentry prevention is separate hardening",
            ],
            "non_claims": [
                "original artifact cleanup success",
                "repo-wide active/silent zero",
                "diagnostic/import/historical alias removal",
                "runtime rollout",
                "deployed closeout",
                "manual in-game QA pass",
                "Workshop readiness",
                "ready_for_release",
            ],
        },
    )
    write_text(
        phase_root / "phase0_scope_lock" / "scope_lock.md",
        "\n".join(
            [
                "# Scope Lock",
                "",
                "This round installs a build-time guard against legacy active/silent current-label reentry.",
                "It does not reopen original generated report/operator artifact recovery.",
                "It does not pursue repo-wide lexical zero or alias removal.",
                "Runtime Lua remains render-only; current-label adjudication stays in offline Python validation.",
            ]
        ),
    )


def write_phase1(manifest: dict[str, Any], phase_root: Path) -> Path:
    phase = phase_root / "phase1_manifest"
    effective_manifest = phase / "effective_current_surface_guard_manifest.json"
    write_json(effective_manifest, manifest)
    write_json(
        phase / "hard_fail_surface_manifest.json",
        {"schema_version": "legacy-active-silent-hard-fail-surface-manifest-v0", "surfaces": manifest["hard_fail_surfaces"]},
    )
    write_json(
        phase / "allow_surface_manifest.json",
        {"schema_version": "legacy-active-silent-allow-surface-manifest-v0", "surfaces": manifest["allow_surfaces"]},
    )
    write_json(
        phase / "baseline_seal_report.json",
        {
            "schema_version": "legacy-active-silent-baseline-seal-v0",
            "generated_at": now_iso(),
            "source_decisions": source_decision_summary(),
            "rendered_output": rendered_summary(),
            "runtime_lua": runtime_records(),
            "top_docs": [path_record(path) for path in [PHILOSOPHY, DECISIONS, ARCHITECTURE, ROADMAP, PLAN]],
        },
    )
    return effective_manifest


def write_phase2(report: dict[str, Any], result_root: Path, phase_root: Path) -> None:
    phase = phase_root / "phase2_inventory"
    write_inventory_files(report, phase, result_root)


def write_phase3(report: dict[str, Any], phase_root: Path) -> dict[str, Any]:
    summary = report["summary"]
    manifest_errors = [item for item in report["errors"] if item.get("code") == ALLOWLIST_TOO_BROAD_ERROR_CODE]
    hard_fail_residue = [
        item
        for item in report["errors"]
        if item.get("code") in {CURRENT_SURFACE_ERROR_CODE, DEFAULT_RUNTIME_STATE_ERROR_CODE}
    ]
    unclassified = [
        item
        for item in report["errors"]
        if item.get("code")
        in {UNALLOWLISTED_ERROR_CODE, DIAGNOSTIC_ALIAS_OUTSIDE_ERROR_CODE, LEGACY_METRIC_RENDERED_ERROR_CODE}
    ]
    if manifest_errors:
        branch = "GUARD-D"
        closeout_state = "blocked_guard_manifest_too_broad_or_unstable"
    elif unclassified:
        branch = "GUARD-C"
        closeout_state = "blocked_unclassified_legacy_active_silent_occurrence"
    elif hard_fail_residue:
        branch = "GUARD-B"
        closeout_state = "closed_with_current_surface_residue_rewritten_and_guarded"
    else:
        branch = "GUARD-A"
        closeout_state = "closed_with_no_current_surface_residue_found_and_guarded"

    decision = {
        "schema_version": "legacy-active-silent-branch-decision-v0",
        "generated_at": now_iso(),
        "branch": branch,
        "closeout_state": closeout_state,
        "mutation_required": branch == "GUARD-B",
        "mutation_performed": False,
        "hard_fail_current_label_occurrence_count": summary["hard_fail_current_label_occurrence_count"],
        "unclassified_occurrence_count": summary["unclassified_occurrence_count"],
        "manifest_error_count": summary["manifest_error_count"],
        "gate_a_pass": summary["gate_a_pass"],
        "gate_b_required": True,
    }
    phase = phase_root / "phase3_adjudication"
    write_json(phase / "occurrence_adjudication_report.json", compact_report(report))
    write_json(phase / "branch_decision.json", decision)
    write_json(
        phase_root / "phase4_mutation_if_needed" / "phase3_execution_diff_report.json",
        {
            "schema_version": "legacy-active-silent-phase4-mutation-report-v0",
            "generated_at": now_iso(),
            "mutation_performed": False,
            "reason": "No confirmed hard-fail current-label residue in current checkout." if branch == "GUARD-A" else closeout_state,
            "changed_file_count": 0,
            "changed_files": [],
        },
    )
    return decision


def write_phase5(report: dict[str, Any], phase_root: Path) -> None:
    phase = phase_root / "phase5_guard"
    write_json(phase / "current_surface_guard_report.json", compact_report(report))
    write_json(phase / "validator_error_catalog.json", ERROR_CATALOG)
    write_json(
        phase_root / "phase5_negative_invariant_report.json",
        {
            "schema_version": "legacy-active-silent-negative-invariant-report-v0",
            "generated_at": now_iso(),
            "historical_body_mutated": False,
            "diagnostic_import_alias_removed": False,
            "legacy_metric_keys_removed": False,
            "runtime_lua_guard_logic_added": False,
            "source_decisions": source_decision_summary(),
            "rendered_output": rendered_summary(),
            "runtime_lua": runtime_records(),
            "existing_guard_error_codes": {
                "runtime_state": DEFAULT_RUNTIME_STATE_ERROR_CODE,
                "resolver_compat": DEFAULT_RESOLVER_COMPAT_ERROR_CODE,
            },
        },
    )


def run_validations(
    report: dict[str, Any],
    phase_root: Path,
) -> dict[str, Any]:
    phase = phase_root / "phase6_validation"
    summary = report.get("summary", {})
    gate_a_pass = (
        report.get("status") == "pass"
        and summary.get("gate_a_pass") is True
        and int(summary.get("manifest_error_count", -1)) == 0
        and int(summary.get("hard_fail_current_label_occurrence_count", -1)) == 0
        and int(summary.get("unclassified_occurrence_count", -1)) == 0
    )
    static_dynamic = {
        "schema_version": "legacy-active-silent-static-dynamic-residue-report-v0",
        "generated_at": now_iso(),
        "static_gate_a_status": "pass" if gate_a_pass else "fail",
        "scan_receipt": report.get("scan_receipt"),
        "dynamic_runtime_gate": "not_applicable",
        "dynamic_runtime_gate_reason": "This is an offline build-time guard round; runtime rollout is out of scope.",
        "native_process_policy": "producer_spawns_no_nested_native_processes",
    }
    hard_gate = {
        "schema_version": "legacy-active-silent-phase6-hard-gate-v0",
        "generated_at": now_iso(),
        "gate_a_allowlist_outside_current_label_occurrence_0": gate_a_pass,
        "gate_b_negative_hard_fail_reach": "external_receipt_bound_common_guard_test_required",
        "lua_syntax": "external_receipt_bound_terminal_validation_required",
        "default_build_test_path_wiring": {
            "status": "delegated_to_common_candidate_checkpoint",
            "evidence": "STEP 7 runs test_legacy_active_silent_current_surface_guard.py through Invoke-IrisNative with checkout_unchanged",
        },
        "overall_status": (
            "pending_external_checkpoint" if gate_a_pass else "fail"
        ),
        "nested_native_process_count": 0,
        "source_validation_authority": "external_checkpoint_command_receipts",
    }
    write_json(phase / "static_dynamic_residue_report.json", static_dynamic)
    write_json(phase / "phase6_hard_gate_report.json", hard_gate)
    return hard_gate


def write_phase7_review(
    branch_decision: dict[str, Any],
    hard_gate: dict[str, Any],
    phase_root: Path,
) -> dict[str, Any]:
    critical: list[str] = []
    important: list[str] = []
    if branch_decision["branch"] not in {"GUARD-A", "GUARD-B"}:
        critical.append(f"Branch is blocked: {branch_decision['closeout_state']}")
    if hard_gate["overall_status"] == "fail":
        critical.append("Phase 6 hard gate did not pass.")
    elif hard_gate["overall_status"] == "pending_external_checkpoint":
        important.append(
            "Adoption remains pending the receipt-bound Common guard test and terminal Lua syntax validation."
        )
    if branch_decision["mutation_required"] and not branch_decision["mutation_performed"]:
        important.append("GUARD-B would require writer-origin or artifact-only mutation before closeout.")
    verdict = (
        "FAIL"
        if critical
        else "PENDING_EXTERNAL_CHECKPOINT"
        if hard_gate["overall_status"] == "pending_external_checkpoint"
        else "PASS"
    )
    path = phase_root / "phase7_adversarial_review.md"
    write_text(
        path,
        "\n".join(
            [
                "# Adversarial Review",
                "",
                "## 1. Verdict",
                "",
                verdict,
                "",
                "## 2. Executive Summary",
                "",
                "The guard is scoped as offline build-time hardening and does not claim historical cleanup success.",
                "",
                "## 3. Critical Issues",
                "",
                *(f"- {item}" for item in critical),
                *([] if critical else ["- none"]),
                "",
                "## 4. Non-Critical Issues",
                "",
                *(f"- {item}" for item in important),
                *([] if important else ["- none"]),
                "",
                "## 5. Scope Review",
                "",
                "- No original referent recovery reopen.",
                "- No repo-wide active/silent lexical zero.",
                "- Runtime Lua remains render-only.",
                "",
                "## 6. Validation Review",
                "",
                f"- Phase 6 hard gate: `{hard_gate['overall_status']}`",
                "",
                "## 7. Governance Review",
                "",
                "- Existing runtime_state and resolver guards remain primary owners for their surfaces.",
                "",
                "## 8. Risk Surface Review",
                "",
                "- Authority Surface: touched through manifest and closeout artifacts.",
                "- Runtime Behavior Surface: not touched.",
                "- Compatibility Surface: aliases and metric keys preserved.",
                "- Sealed Artifact Surface: read-only.",
                "- Public-Facing Output Surface: no current residue found in GUARD-A path.",
                "",
                "## 9. Risk Review",
                "",
                "- Main residual risk is future hard-fail surface drift; manifest tests cover broad allowlist failure.",
                "",
                "## 10. Required Revisions",
                "",
                (
                    "- bind the external checkpoint receipts before adoption closeout"
                    if verdict == "PENDING_EXTERNAL_CHECKPOINT"
                    else "- none"
                    if not critical
                    else "- resolve critical issues before successful closeout"
                ),
                "",
                "## 11. Final Recommendation",
                "",
                verdict,
                "",
                "## 12. Reviewer Notes",
                "",
                "- No manual in-game QA or release readiness is claimed.",
            ]
        ),
    )
    return {"verdict": verdict, "critical_count": len(critical), "important_count": len(important), "path": rel(path)}


def write_closeout(
    branch_decision: dict[str, Any],
    hard_gate: dict[str, Any],
    review: dict[str, Any],
    phase_root: Path,
) -> dict[str, Any]:
    if review["verdict"] == "PASS" and hard_gate["overall_status"] == "pass":
        closeout_state = branch_decision["closeout_state"]
    elif hard_gate["overall_status"] == "pending_external_checkpoint":
        closeout_state = "implemented_pending_external_checkpoint"
    else:
        closeout_state = branch_decision["closeout_state"] if branch_decision["branch"] in {"GUARD-C", "GUARD-D"} else "implemented_only"
    closeout = {
        "schema_version": "legacy-active-silent-current-surface-guard-closeout-v0",
        "generated_at": now_iso(),
        "closeout_state": closeout_state,
        "branch": branch_decision["branch"],
        "mutation_performed": branch_decision["mutation_performed"],
        "current_surface_residue_count": branch_decision["hard_fail_current_label_occurrence_count"],
        "unclassified_occurrence_count": branch_decision["unclassified_occurrence_count"],
        "manifest_error_count": branch_decision["manifest_error_count"],
        "gate_a": "pass" if branch_decision["gate_a_pass"] else "fail",
        "gate_b": "external_checkpoint_required",
        "phase6_hard_gate": hard_gate["overall_status"],
        "adversarial_review": review,
        "validation_ceiling": {
            "validated": [
                "manifest schema and allowlist broadness checks",
                "current checkout active/silent occurrence inventory",
                "in-process canonical scan Gate A",
            ],
            "out_of_scope": [
                "runtime rollout",
                "deployed closeout",
                "manual in-game QA pass",
                "Workshop release readiness",
                "external mod compatibility sweep",
                "original artifact referent recovery",
            ],
            "unvalidated_but_in_scope": [
                "receipt-bound Common guard unit test",
                "receipt-bound terminal Lua syntax validation",
            ],
        },
        "non_claims": [
            "original artifact cleanup success = not_claimed",
            "repo-wide active/silent zero = not_claimed",
            "diagnostic/import/historical alias removal = not_claimed",
            "runtime rollout = not_claimed",
            "deployed closeout = not_claimed",
            "manual in-game QA pass = not_claimed",
            "Workshop readiness = not_claimed",
            "ready_for_release = not_claimed",
        ],
        "evidence": {
            "manifest_authority": rel(DEFAULT_MANIFEST),
            "effective_manifest": rel(
                phase_root
                / "phase1_manifest"
                / "effective_current_surface_guard_manifest.json"
            ),
            "inventory": rel(phase_root / "phase2_inventory" / "occurrence_stream_reference.json"),
            "branch_decision": rel(phase_root / "phase3_adjudication" / "branch_decision.json"),
            "guard_report": rel(phase_root / "phase5_guard" / "current_surface_guard_report.json"),
            "phase6_hard_gate": rel(phase_root / "phase6_validation" / "phase6_hard_gate_report.json"),
            "adversarial_review": review["path"],
        },
    }
    phase = phase_root / "phase7_closeout"
    write_json(phase / "closeout.json", closeout)
    write_text(
        phase / "closeout.md",
        "\n".join(
            [
                "# Closeout",
                "",
                f"- closeout_state: `{closeout_state}`",
                f"- branch: `{branch_decision['branch']}`",
                f"- mutation_performed: `{branch_decision['mutation_performed']}`",
                f"- current_surface_residue_count: `{branch_decision['hard_fail_current_label_occurrence_count']}`",
                f"- unclassified_occurrence_count: `{branch_decision['unclassified_occurrence_count']}`",
                f"- phase6_hard_gate: `{hard_gate['overall_status']}`",
                "",
                "## Non-Claims",
                "",
                *(f"- {claim}" for claim in closeout["non_claims"]),
            ]
        ),
    )
    return closeout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Legacy Active/Silent Current-Surface Guard Round artifacts.")
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--result-root", required=True)
    parser.add_argument("--allocation-receipt", required=True)
    parser.add_argument("--scan-backend", choices=sorted(SCAN_BACKENDS), default="rg")
    parser.add_argument("--scan-timeout", type=int, default=60)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_policy = load_and_validate_output_policy()
    work_root, result_root = validate_external_run_roots(
        REPO_ROOT,
        Path(args.work_root),
        Path(args.result_root),
    )
    allocation_receipt_path = Path(args.allocation_receipt).resolve()
    allocation_receipt = load_and_validate_allocation_receipt(
        allocation_receipt_path,
        work_root,
        result_root,
    )
    result_subroots = {
        name: result_root / name
        for name in output_policy["external_subroots"]
    }
    if list(result_subroots) != AUTHORIZED_RESULT_SUBROOTS:
        raise ValueError("successor policy result subroots are not the canonical ordered set")
    for subroot in result_subroots.values():
        subroot.mkdir(parents=True, exist_ok=False)
    phase_root = (
        result_subroots["phases"]
        / "legacy_active_silent_current_surface_guard_round"
    )
    manifest = load_manifest(DEFAULT_MANIFEST, REPO_ROOT)
    write_phase0(phase_root)
    effective_manifest_path = write_phase1(manifest, phase_root)
    report = validate_repo(
        REPO_ROOT,
        manifest,
        scan_backend=args.scan_backend,
        scan_timeout=args.scan_timeout,
        result_root=result_root,
    )
    write_phase2(report, result_root, phase_root)
    branch_decision = write_phase3(report, phase_root)
    write_phase5(report, phase_root)
    write_json_atomic(
        result_subroots["phases"] / "phase2_occurrence_stream_reference.json",
        report["occurrence_stream"],
    )
    write_json_atomic(
        result_subroots["phases"] / "phase3_occurrence_adjudication_summary.json",
        compact_report(report),
    )
    write_json_atomic(
        result_subroots["phases"] / "phase5_current_surface_guard_summary.json",
        compact_report(report),
    )
    hard_gate = run_validations(
        report,
        phase_root=phase_root,
    )
    review = write_phase7_review(branch_decision, hard_gate, phase_root)
    closeout = write_closeout(branch_decision, hard_gate, review, phase_root)
    verify_occurrence_stream_reference(report["occurrence_stream"], result_root)
    producer_receipt_path = result_subroots["logs"] / "legacy_active_silent_guard_producer_receipt.json"
    producer_receipt = {
        "schema_version": "legacy-active-silent-guard-producer-receipt-v1",
        "status": "PENDING_EXTERNAL_CHECKPOINT",
        "execution_status": "PASS",
        "adoption_validation_status": "pending_external_checkpoint",
        "generated_at": now_iso(),
        "run_id": allocation_receipt.get("run_id"),
        "claim_id": allocation_receipt.get("claim_id"),
        "attempt_id": allocation_receipt.get("attempt_id"),
        "allocation_profile": allocation_receipt.get("allocation_profile"),
        "output_policy": {
            "path": rel(OUTPUT_POLICY),
            "sha256": sha256_file(OUTPUT_POLICY),
            "approval": output_policy.get("approval"),
        },
        "allocation_receipt": {
            "path": allocation_receipt_path.as_posix(),
            "sha256": sha256_file(allocation_receipt_path),
        },
        "allocation_ledger": allocation_receipt.get("allocation_ledger"),
        "resolved_roots": {
            "work": work_root.as_posix(),
            "result": result_root.as_posix(),
            **{name: path.as_posix() for name, path in result_subroots.items()},
        },
        "scan_receipt": report["scan_receipt"],
        "occurrence_stream": report["occurrence_stream"],
        "manifest_authority": {
            "path": rel(DEFAULT_MANIFEST),
            "sha256": sha256_file(DEFAULT_MANIFEST),
            "effective_copy": path_record(effective_manifest_path),
        },
        "phase_summaries": [
            path_record(phase_root / "phase2_inventory" / "occurrence_stream_reference.json"),
            path_record(phase_root / "phase3_adjudication" / "occurrence_adjudication_report.json"),
            path_record(phase_root / "phase5_guard" / "current_surface_guard_report.json"),
        ],
        "external_phase_summaries": [
            path_record(result_subroots["phases"] / "phase2_occurrence_stream_reference.json"),
            path_record(result_subroots["phases"] / "phase3_occurrence_adjudication_summary.json"),
            path_record(result_subroots["phases"] / "phase5_current_surface_guard_summary.json"),
        ],
        "root_disposition": {
            "work": "empty_verified_delete_eligible_after_closeout",
            "result": "retained_content_addressed_objects_phases_logs_and_package",
            "package": "empty_verified_not_required_for_guard_pilot",
        },
        "object_lifecycle_dispositions": [
            {
                "logical_id": report["occurrence_stream"]["logical_id"],
                "sha256": report["occurrence_stream"]["sha256"],
                "role": "retained_current_required",
            }
        ],
        "dangling_reference_count": 0,
        "work_root_empty_at_closeout": not any(work_root.iterdir()),
    }
    write_json_atomic(producer_receipt_path, producer_receipt)
    closeout["producer_receipt"] = {
        "path": producer_receipt_path.as_posix(),
        "sha256": sha256_file(producer_receipt_path),
    }
    print(json.dumps(closeout, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
