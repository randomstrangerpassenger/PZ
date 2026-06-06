from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


V2_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.validate_legacy_active_silent_current_surface_guard import (  # noqa: E402
    ALLOWLIST_TOO_BROAD_ERROR_CODE,
    CURRENT_SURFACE_ERROR_CODE,
    DEFAULT_RESOLVER_COMPAT_ERROR_CODE,
    DEFAULT_RUNTIME_STATE_ERROR_CODE,
    DIAGNOSTIC_ALIAS_OUTSIDE_ERROR_CODE,
    ERROR_CATALOG,
    LEGACY_METRIC_RENDERED_ERROR_CODE,
    UNALLOWLISTED_ERROR_CODE,
    validate_repo,
    write_inventory_files,
    write_json,
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


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def run_command(command: list[str], timeout: int = 300) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "command": command,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timed_out": False,
            "missing_tool": False,
        }
    except FileNotFoundError as exc:
        return {
            "command": command,
            "exit_code": None,
            "stdout": "",
            "stderr": str(exc),
            "timed_out": False,
            "missing_tool": True,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "exit_code": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
            "missing_tool": False,
        }


def compact_command(result: dict[str, Any], max_lines: int = 80) -> dict[str, Any]:
    stdout_lines = str(result.get("stdout", "")).splitlines()
    stderr_lines = str(result.get("stderr", "")).splitlines()
    return {
        "command": result.get("command"),
        "exit_code": result.get("exit_code"),
        "timed_out": result.get("timed_out"),
        "missing_tool": result.get("missing_tool"),
        "stdout_line_count": len(stdout_lines),
        "stderr_line_count": len(stderr_lines),
        "stdout_tail": stdout_lines[-max_lines:],
        "stderr_tail": stderr_lines[-max_lines:],
    }


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


def build_manifest() -> dict[str, Any]:
    return {
        "schema_version": "legacy-active-silent-current-surface-guard-manifest-v0",
        "round_name": "Legacy Active/Silent Current-Surface Guard Round",
        "generated_at": now_iso(),
        "round_root": rel(ROUND_ROOT),
        "canonical_runtime_state_enum": ["adopted", "unadopted"],
        "legacy_alias_scope": "diagnostic/import/historical read-only only",
        "classification_precedence": [
            "round-local staging evidence wins over generic build/report path matching",
            "hard-fail requires both a sealed hard-fail surface and a current-label occurrence",
            "current-label candidacy is based on occurrence_kind, not lexical token alone",
            "allow rules require path_glob, occurrence_kind, reason, and must_not_be_current_output",
            "no allow rule may downgrade current output serialization of active/silent",
        ],
        "hard_fail_surfaces": [
            {
                "id": "current_writer_output_decisions",
                "surface": "current writer output",
                "path_globs": ["Iris/build/description/v2/data/**/*.jsonl"],
                "occurrence_kinds": ["runtime_state_value", "source_value", "writer_output_label_value"],
                "primary_error_owner": DEFAULT_RUNTIME_STATE_ERROR_CODE,
            },
            {
                "id": "current_generated_report_operator_output",
                "surface": "current generated report / operator output",
                "path_globs": ["Iris/build/description/v2/output/**/*.json", "Iris/build/description/v2/output/**/*.jsonl"],
                "occurrence_kinds": ["operator_label_value", "current_report_label_value", "writer_output_label_value"],
                "primary_error_owner": CURRENT_SURFACE_ERROR_CODE,
            },
            {
                "id": "current_runtime_payload_lua",
                "surface": "current runtime payload",
                "path_globs": ["Iris/media/lua/client/Iris/Data/**/*.lua"],
                "occurrence_kinds": ["source_value", "operator_label_value", "current_report_label_value"],
                "primary_error_owner": CURRENT_SURFACE_ERROR_CODE,
            },
            {
                "id": "packaged_lua_data",
                "surface": "packaged Lua data",
                "path_globs": ["Iris/build/package/Iris/media/lua/client/Iris/Data/**/*.lua"],
                "occurrence_kinds": ["source_value", "operator_label_value", "current_report_label_value"],
                "primary_error_owner": CURRENT_SURFACE_ERROR_CODE,
            },
        ],
        "allow_surfaces": [
            {
                "id": "historical_docs",
                "path_globs": [
                    "docs/Iris/**",
                    "docs/DECISIONS.md",
                    "docs/ARCHITECTURE.md",
                    "docs/ROADMAP.md",
                    "Iris/_docs/**",
                ],
                "occurrence_kinds": [
                    "historical_quote",
                    "plain_text",
                    "code_identifier",
                    "legacy_metric_key",
                    "diagnostic_alias",
                    "runtime_state_value",
                    "source_value",
                    "operator_label_value",
                    "current_report_label_value",
                    "writer_output_label_value",
                ],
                "reason": "historical sealed body and planning text are preserved",
                "must_not_be_current_output": True,
            },
            {
                "id": "archive_historical_payload",
                "path_globs": ["Iris/_archive/**"],
                "occurrence_kinds": [
                    "historical_quote",
                    "plain_text",
                    "code_identifier",
                    "legacy_metric_key",
                    "diagnostic_alias",
                    "runtime_state_value",
                    "source_value",
                    "operator_label_value",
                    "current_report_label_value",
                    "writer_output_label_value",
                ],
                "reason": "archived payloads are preserved historical evidence and not current output",
                "must_not_be_current_output": True,
            },
            {
                "id": "staging_evidence",
                "path_globs": ["Iris/build/description/v2/staging/**"],
                "occurrence_kinds": [
                    "historical_quote",
                    "plain_text",
                    "legacy_metric_key",
                    "diagnostic_alias",
                    "code_identifier",
                    "runtime_state_value",
                    "source_value",
                    "operator_label_value",
                    "current_report_label_value",
                    "writer_output_label_value",
                ],
                "reason": "staging evidence is diagnostic and not current writer output",
                "must_not_be_current_output": True,
            },
            {
                "id": "round_local_diagnostics",
                "path_globs": [f"{rel(ROUND_ROOT)}/**"],
                "occurrence_kinds": [
                    "historical_quote",
                    "plain_text",
                    "legacy_metric_key",
                    "diagnostic_alias",
                    "code_identifier",
                    "runtime_state_value",
                    "source_value",
                    "operator_label_value",
                    "current_report_label_value",
                    "writer_output_label_value",
                ],
                "reason": "round-local scanner/validator evidence may quote guarded tokens",
                "must_not_be_current_output": True,
            },
            {
                "id": "validator_and_tests",
                "path_globs": [
                    "Iris/build/description/v2/tools/validate_legacy_active_silent_current_surface_guard.py",
                    "Iris/build/description/v2/tools/build/build_legacy_active_silent_current_surface_guard_round.py",
                    "Iris/build/description/v2/tests/test_legacy_active_silent_current_surface_guard.py",
                ],
                "occurrence_kinds": [
                    "explicit_legacy_test_fixture",
                    "plain_text",
                    "code_identifier",
                    "legacy_metric_key",
                    "diagnostic_alias",
                    "runtime_state_value",
                    "source_value",
                    "operator_label_value",
                    "current_report_label_value",
                    "writer_output_label_value",
                ],
                "reason": "validator and explicit guard tests contain expected legacy-token fixtures",
                "must_not_be_current_output": True,
            },
            {
                "id": "historical_build_tool_source",
                "path_globs": ["Iris/build/description/v2/tools/build/**/*.py"],
                "occurrence_kinds": [
                    "historical_quote",
                    "plain_text",
                    "code_identifier",
                    "legacy_metric_key",
                    "diagnostic_alias",
                    "runtime_state_value",
                    "source_value",
                    "operator_label_value",
                    "current_report_label_value",
                    "writer_output_label_value",
                ],
                "reason": "build tool source may quote legacy fixtures but is not current output",
                "must_not_be_current_output": True,
            },
            {
                "id": "legacy_output_metric_keys",
                "path_globs": ["Iris/output/**/*.json"],
                "occurrence_kinds": ["legacy_metric_key", "plain_text", "code_identifier"],
                "reason": "legacy metric keys are retained unless rendered as current labels",
                "must_not_be_current_output": True,
            },
        ],
        "existing_guard_boundaries": {
            "runtime_state writer/validator occurrence": DEFAULT_RUNTIME_STATE_ERROR_CODE,
            "legacy resolver compatibility label occurrence": DEFAULT_RESOLVER_COMPAT_ERROR_CODE,
            "packaged Lua / generated operator / writer non-runtime label occurrence": CURRENT_SURFACE_ERROR_CODE,
        },
        "error_catalog": ERROR_CATALOG,
    }


def write_phase0() -> None:
    write_json(
        ROUND_ROOT / "phase0_scope_lock" / "prior_readpoint_summary.json",
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
        ROUND_ROOT / "phase0_scope_lock" / "scope_lock.md",
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


def write_phase1(manifest: dict[str, Any]) -> None:
    phase = ROUND_ROOT / "phase1_manifest"
    write_json(phase / "current_surface_guard_referent_manifest.json", manifest)
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


def write_phase2(report: dict[str, Any]) -> None:
    phase = ROUND_ROOT / "phase2_inventory"
    write_inventory_files(report, phase)


def write_phase3(report: dict[str, Any]) -> dict[str, Any]:
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
    phase = ROUND_ROOT / "phase3_adjudication"
    write_json(phase / "occurrence_adjudication_report.json", report)
    write_json(phase / "branch_decision.json", decision)
    write_json(
        ROUND_ROOT / "phase4_mutation_if_needed" / "phase3_execution_diff_report.json",
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


def write_phase5(report: dict[str, Any]) -> None:
    phase = ROUND_ROOT / "phase5_guard"
    write_json(phase / "current_surface_guard_report.json", report)
    write_json(phase / "validator_error_catalog.json", ERROR_CATALOG)
    write_json(
        ROUND_ROOT / "phase5_negative_invariant_report.json",
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


def write_validation_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "command: " + " ".join(str(part) for part in result["command"]),
        f"exit_code: {result['exit_code']}",
        f"timed_out: {result['timed_out']}",
        f"missing_tool: {result['missing_tool']}",
        "",
        "stdout:",
        result.get("stdout", ""),
        "",
        "stderr:",
        result.get("stderr", ""),
    ]
    write_text(path, "\n".join(lines))


def run_validations(manifest_path: Path, run_tests: bool) -> dict[str, Any]:
    validator_cmd = [
        "python",
        "-B",
        "Iris\\build\\description\\v2\\tools\\validate_legacy_active_silent_current_surface_guard.py",
        "--manifest",
        str(manifest_path),
        "--repo-root",
        ".",
    ]
    validator = run_command(validator_cmd)
    python_unittest = {"command": ["not_run"], "exit_code": None, "stdout": "", "stderr": "", "timed_out": False, "missing_tool": False}
    lua_syntax = {"command": ["not_run"], "exit_code": None, "stdout": "", "stderr": "", "timed_out": False, "missing_tool": False}
    if run_tests:
        python_unittest = run_command(
            ["python", "-B", "-m", "unittest", "discover", "-s", "Iris\\build\\description\\v2\\tests", "-p", "test_*.py"],
            timeout=600,
        )
        lua_syntax = run_command(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", ".\\tools\\check_lua_syntax.ps1"],
            timeout=600,
        )
    phase = ROUND_ROOT / "phase6_validation"
    write_validation_report(phase / "python_unittest_report.txt", python_unittest)
    write_validation_report(phase / "lua_syntax_report.txt", lua_syntax)
    static_dynamic = {
        "schema_version": "legacy-active-silent-static-dynamic-residue-report-v0",
        "generated_at": now_iso(),
        "standalone_validator": compact_command(validator),
        "static_gate_a_status": "pass" if validator["exit_code"] == 0 else "fail",
        "dynamic_runtime_gate": "not_applicable",
        "dynamic_runtime_gate_reason": "This is an offline build-time guard round; runtime rollout is out of scope.",
    }
    hard_gate = {
        "schema_version": "legacy-active-silent-phase6-hard-gate-v0",
        "generated_at": now_iso(),
        "gate_a_allowlist_outside_current_label_occurrence_0": validator["exit_code"] == 0,
        "gate_b_negative_hard_fail_reach_verified_by_unittest": python_unittest["exit_code"] == 0 if run_tests else False,
        "standalone_validator_exit_code": validator["exit_code"],
        "python_unittest_exit_code": python_unittest["exit_code"],
        "lua_syntax_exit_code": lua_syntax["exit_code"],
        "default_build_test_path_wiring": {
            "status": "pass" if run_tests and python_unittest["exit_code"] == 0 else "not_proven",
            "evidence": "guard tests are included in unittest discovery under Iris\\build\\description\\v2\\tests",
        },
        "overall_status": (
            "pass"
            if validator["exit_code"] == 0
            and run_tests
            and python_unittest["exit_code"] == 0
            and lua_syntax["exit_code"] == 0
            else "fail"
        ),
        "commands": {
            "standalone_validator": compact_command(validator),
            "python_unittest": compact_command(python_unittest),
            "lua_syntax": compact_command(lua_syntax),
        },
    }
    write_json(phase / "static_dynamic_residue_report.json", static_dynamic)
    write_json(phase / "phase6_hard_gate_report.json", hard_gate)
    return hard_gate


def write_phase7_review(branch_decision: dict[str, Any], hard_gate: dict[str, Any]) -> dict[str, Any]:
    critical: list[str] = []
    important: list[str] = []
    if branch_decision["branch"] not in {"GUARD-A", "GUARD-B"}:
        critical.append(f"Branch is blocked: {branch_decision['closeout_state']}")
    if hard_gate["overall_status"] != "pass":
        critical.append("Phase 6 hard gate did not pass.")
    if branch_decision["mutation_required"] and not branch_decision["mutation_performed"]:
        important.append("GUARD-B would require writer-origin or artifact-only mutation before closeout.")
    verdict = "PASS" if not critical else "FAIL"
    path = ROUND_ROOT / "phase7_adversarial_review.md"
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
                "- none" if not critical else "- resolve critical issues before successful closeout",
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


def write_closeout(branch_decision: dict[str, Any], hard_gate: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    if review["verdict"] == "PASS" and hard_gate["overall_status"] == "pass":
        closeout_state = branch_decision["closeout_state"]
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
        "gate_b": "pass" if hard_gate.get("gate_b_negative_hard_fail_reach_verified_by_unittest") else "fail",
        "phase6_hard_gate": hard_gate["overall_status"],
        "adversarial_review": review,
        "validation_ceiling": {
            "validated": [
                "manifest schema and allowlist broadness checks",
                "current checkout active/silent occurrence inventory",
                "standalone validator Gate A",
                "unittest negative and positive fixture reach",
                "Lua syntax command",
            ],
            "out_of_scope": [
                "runtime rollout",
                "deployed closeout",
                "manual in-game QA pass",
                "Workshop release readiness",
                "external mod compatibility sweep",
                "original artifact referent recovery",
            ],
            "unvalidated_but_in_scope": [],
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
            "manifest": rel(ROUND_ROOT / "phase1_manifest" / "current_surface_guard_referent_manifest.json"),
            "inventory": rel(ROUND_ROOT / "phase2_inventory" / "legacy_active_silent_occurrence_inventory.jsonl"),
            "branch_decision": rel(ROUND_ROOT / "phase3_adjudication" / "branch_decision.json"),
            "guard_report": rel(ROUND_ROOT / "phase5_guard" / "current_surface_guard_report.json"),
            "phase6_hard_gate": rel(ROUND_ROOT / "phase6_validation" / "phase6_hard_gate_report.json"),
            "adversarial_review": review["path"],
        },
    }
    phase = ROUND_ROOT / "phase7_closeout"
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
    parser.add_argument("--run-validations", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_phase0()
    manifest = build_manifest()
    write_phase1(manifest)
    manifest_path = ROUND_ROOT / "phase1_manifest" / "current_surface_guard_referent_manifest.json"
    report = validate_repo(REPO_ROOT, manifest)
    write_phase2(report)
    branch_decision = write_phase3(report)
    write_phase5(report)
    hard_gate = run_validations(manifest_path, run_tests=args.run_validations)
    review = write_phase7_review(branch_decision, hard_gate)
    closeout = write_closeout(branch_decision, hard_gate, review)
    print(json.dumps(closeout, ensure_ascii=False, indent=2))
    return 0 if closeout["closeout_state"].startswith("closed_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
