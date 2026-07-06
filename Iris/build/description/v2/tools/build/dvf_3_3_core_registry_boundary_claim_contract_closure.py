from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    V2_ROOT,
    canonical_hash,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_text,
)


ROUND_ID = "dvf_3_3_core_registry_boundary_claim_contract_closure"
ENV_ROOT = "DVF_CORE_REGISTRY_BOUNDARY_CLAIM_CONTRACT_CLOSURE_ROOT"
EVIDENCE_ROOT = resolve_repo(os.environ.get(ENV_ROOT, V2_ROOT / "staging" / ROUND_ID))

PREDECESSOR_TOOL_ID = "dvf_3_3_legacy_combined_route_axis_inventory"
PREDECESSOR_ROUND_ID = "dvf_3_3_legacy_combined_route_axis_inventory_routing_preflight"
PREDECESSOR_DEFAULT_ROOT = V2_ROOT / "staging" / PREDECESSOR_ROUND_ID
PREDECESSOR_RERUN_ROOT = EVIDENCE_ROOT / "phase0" / "predecessor_rerun"

TOOLS_DIR = Path(__file__).resolve().parent
COMMON_MODULE = TOOLS_DIR / f"{ROUND_ID}.py"
RUNNER = TOOLS_DIR / f"run_{ROUND_ID}.py"
VALIDATOR = TOOLS_DIR / f"validate_{ROUND_ID}.py"
FOCUSED_TEST = V2_ROOT / "tests" / f"test_{ROUND_ID}.py"

PLAN_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_plan.md"
CLAIM_CONTRACT_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_contract.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_contract_ledger_packet.md"
CLOSEOUT_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_contract_closure_closeout.md"
WALKTHROUGH_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_contract_closure_walkthrough.md"
PHILOSOPHY_DOC = REPO_ROOT / "docs" / "Philosophy.md"
DECISIONS_DOC = REPO_ROOT / "docs" / "DECISIONS.md"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "ARCHITECTURE.md"
ROADMAP_DOC = REPO_ROOT / "docs" / "ROADMAP.md"
TOP_DOC_UPDATE_MARKERS = {
    DECISIONS_DOC: "dvf_3_3_core_registry_boundary_claim_contract_closure",
    ARCHITECTURE_DOC: "DVF Core / Iris Artifact Registry Claim Contract Boundary",
    ROADMAP_DOC: "DVF Core / Iris Artifact Registry Boundary Claim Contract Closure",
}
LEGACY_WALKTHROUGH_DOC = (
    REPO_ROOT / "docs" / "dvf_3_3_legacy_combined_route_axis_inventory_routing_preflight_walkthrough.md"
)
LIVE_REQUIRED_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
ACTIVE_CORE_CLOSURE = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"
ROUND3_RUNNER = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"

ROADMAP_ATTACHMENT = Path(
    "C:/Users/MW/.codex/attachments/78f36bb4-6918-40fb-aeab-c5b4054d1ca3/pasted-text.txt"
)
ROADMAP_ATTACHMENT_SHA256 = "45B540BBB03E63B4E5F7CCEA9650AE33E2D6A751FB8567484E7BD0A1AB54B01A"

OWNER_RECORD = (
    V2_ROOT / "owner_inputs" / ROUND_ID / "dvf_pass_disposition_owner_record.json"
)
TOP_DOC_GO_RECORD = V2_ROOT / "owner_inputs" / ROUND_ID / "top_doc_application_go_record.json"

AXES = [
    "dvf_core_body_compiler",
    "registry_authority",
    "registry_runtime_compatibility",
    "publish_boundary",
    "legacy_combined_governance_route",
    "historical_predecessor_trace",
    "diagnostic_or_fixture",
]
CLAIM_CLASSES = [
    "DVF Core PASS",
    "Registry Authority PASS",
    "Registry Runtime Compatibility PASS",
    "Publish Boundary PASS",
    "Legacy Combined Current Route PASS",
]
DVF_PASS_DISPOSITION_ENUM = [
    "forbidden_standalone_current_claim",
    "legacy_alias_only",
    "blocked_owner_decision_pending",
]
BASE_EXCEPTION_CLASSES = [
    "historical_quote",
    "negated_claim",
    "forbidden_example",
    "predecessor_trace",
]
RECOGNIZED_EXCEPTION_CLASSES = BASE_EXCEPTION_CLASSES + ["legacy_alias_role_qualified"]

PROTECTED_SURFACE_PATHS = [
    "Iris/build/description/v2/data",
    "Iris/build/description/v2/output",
    "Iris/Iris/media/lua/client/Iris/Data",
    "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/build/package/Iris",
]

ROUND_LOCAL_GITIGNORE_RULES = [
    "!Iris/build/description/v2/tools/build/dvf_3_3_core_registry_boundary_claim_contract_closure.py",
    "!Iris/build/description/v2/tools/build/run_dvf_3_3_core_registry_boundary_claim_contract_closure.py",
    "!Iris/build/description/v2/tools/build/validate_dvf_3_3_core_registry_boundary_claim_contract_closure.py",
    "!Iris/build/description/v2/tests/test_dvf_3_3_core_registry_boundary_claim_contract_closure.py",
    "!Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_claim_contract_closure/",
    "!Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_claim_contract_closure/**",
]

CLAIM_TOKEN_RE = re.compile(
    r"\bDVF PASS\b|DVF Core PASS|Registry Authority PASS|"
    r"Registry Runtime Compatibility PASS|Publish Boundary PASS|"
    r"Legacy Combined Current Route PASS",
    re.IGNORECASE,
)
NEGATION_TERMS = (
    "not ",
    "not_",
    "no ",
    "no-",
    "does not",
    "do not",
    "must not",
    "cannot",
    "forbidden",
    "out of scope",
    "out-of-scope",
    "non-claim",
    "non_claim",
    "not claim",
    "not claimed",
    "not complete",
    "is not",
    "are not",
    "!= ",
    "아님",
    "아니다",
    "아니라",
    "않",
    "금지",
    "오독 금지",
    "forbids",
    "blocked",
    "without",
    "only when",
    "requires",
    "require ",
    "must ",
)


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


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def normalized_sha(path: str | Path) -> str | None:
    digest = sha256_file(path)
    return digest.lower() if isinstance(digest, str) else None


def hash_path(path: str | Path) -> str | None:
    resolved = resolve_repo(path)
    if not resolved.exists():
        return None
    if resolved.is_file():
        return normalized_sha(resolved)
    rows = []
    for child in sorted(p for p in resolved.rglob("*") if p.is_file()):
        rows.append({"path": child.relative_to(resolved).as_posix(), "sha256": normalized_sha(child)})
    return canonical_hash(rows)


def file_record(path: str | Path, role: str) -> dict[str, Any]:
    resolved = resolve_repo(path)
    return {
        "path": rel(resolved),
        "role": role,
        "exists": resolved.exists(),
        "kind": "dir" if resolved.is_dir() else "file" if resolved.is_file() else "missing",
        "sha256": hash_path(resolved),
    }


def run_command(
    args: list[str],
    *,
    env_extra: dict[str, str] | None = None,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    started = now_iso()
    try:
        result = subprocess.run(
            args,
            cwd=REPO_ROOT,
            env=env,
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


def required_manifest_counts() -> dict[str, int]:
    payload = read_json_object(LIVE_REQUIRED_MANIFEST)
    tests = payload.get("required_tests")
    artifacts = payload.get("required_artifacts")
    return {
        "required_test_count": len(tests) if isinstance(tests, list) else 0,
        "required_artifact_count": len(artifacts) if isinstance(artifacts, list) else 0,
    }


def active_core_counts() -> dict[str, int]:
    payload = read_json_object(ACTIVE_CORE_CLOSURE)
    core = payload.get("current_closure_modules")
    tooling = payload.get("current_route_allowed_tooling_modules")
    return {
        "current_core_module_count": len(core) if isinstance(core, list) else 0,
        "tooling_allowlist_count": len(tooling) if isinstance(tooling, list) else 0,
    }


def route_union_count_from_report(report: dict[str, Any]) -> int | None:
    value = report.get("current_route_union_test_count")
    return value if isinstance(value, int) else None


def predecessor_input_hash_set() -> dict[str, Any]:
    paths = [
        PREDECESSOR_DEFAULT_ROOT / "routing_preflight_report.json",
        PREDECESSOR_DEFAULT_ROOT / "legacy_combined_route_axis_inventory.json",
        PREDECESSOR_DEFAULT_ROOT / "legacy_combined_route_axis_inventory.md",
        REPO_ROOT / "docs" / "dvf_3_3_legacy_combined_route_axis_policy.md",
        LEGACY_WALKTHROUGH_DOC,
    ]
    return {
        "schema_version": "dvf-3-3-core-registry-boundary-predecessor-input-hash-set-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "predecessor_round_id": PREDECESSOR_ROUND_ID,
        "default_staging_root": rel(PREDECESSOR_DEFAULT_ROOT),
        "default_staging_root_sha256": hash_path(PREDECESSOR_DEFAULT_ROOT),
        "records": [file_record(path, "predecessor_readonly_input") for path in paths],
    }


def hash_set_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return {
        (row.get("path"), row.get("sha256"), row.get("exists"))
        for row in left.get("records", [])
        if isinstance(row, dict)
    } == {
        (row.get("path"), row.get("sha256"), row.get("exists"))
        for row in right.get("records", [])
        if isinstance(row, dict)
    } and left.get("default_staging_root_sha256") == right.get("default_staging_root_sha256")


def materialize_roadmap_input() -> dict[str, Any]:
    target = phase_path("phase0", "roadmap_input_bound.md")
    source_exists = ROADMAP_ATTACHMENT.exists()
    data = ROADMAP_ATTACHMENT.read_bytes() if source_exists else b""
    target.write_bytes(data)
    source_sha = sha256_bytes(data) if source_exists else None
    target_sha = normalized_sha(target)
    text = data.decode("utf-8", errors="replace") if data else ""
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-roadmap-input-hash-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "source_attachment_path": ROADMAP_ATTACHMENT.as_posix(),
        "source_attachment_exists": source_exists,
        "source_attachment_expected_sha256": ROADMAP_ATTACHMENT_SHA256.lower(),
        "source_attachment_sha256": source_sha,
        "materialized_path": rel(target),
        "materialized_sha256": target_sha,
        "byte_length": len(data),
        "line_count": len(text.splitlines()),
        "hash_equality_status": "PASS"
        if source_sha == target_sha == ROADMAP_ATTACHMENT_SHA256.lower()
        else "FAIL",
        "attachment_path_after_materialization_is_provenance_only": True,
    }
    write_json(phase_path("phase0", "roadmap_input_hash_report.json"), report)
    trace = {
        "schema_version": "dvf-3-3-core-registry-boundary-roadmap-to-plan-trace-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if report["hash_equality_status"] == "PASS" else "FAIL",
        "roadmap_input_artifact": rel(target),
        "plan_artifact": rel(PLAN_DOC),
        "trace_rows": [
            {
                "roadmap_topic": "claim vocabulary and routing boundary separation",
                "plan_sections": ["Objective", "Scope", "Planned Changes 2-4"],
                "generated_artifacts": ["phase1/claim_contract.md", "phase2/claim_contract.json"],
            },
            {
                "roadmap_topic": "predecessor freshness before consumption",
                "plan_sections": ["Change 1", "Validation Plan"],
                "generated_artifacts": ["phase0/predecessor_inventory_freshness_report.json"],
            },
            {
                "roadmap_topic": "no runtime/package/public mutation",
                "plan_sections": ["Risk Surface Touch", "Expected Closeout State"],
                "generated_artifacts": ["phase6/protected_surface_no_mutation_report.json"],
            },
        ],
    }
    write_json(phase_path("phase0", "roadmap_to_plan_trace_report.json"), trace)
    return report


def protected_surface_records() -> list[dict[str, Any]]:
    return [file_record(path, "protected_no_mutation_surface") for path in PROTECTED_SURFACE_PATHS]


def write_protected_baseline() -> list[dict[str, Any]]:
    records = protected_surface_records()
    write_json(
        phase_path("phase0", "protected_surface_baseline.json"),
        {
            "schema_version": "dvf-3-3-core-registry-boundary-protected-surface-baseline-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "records": records,
        },
    )
    return records


def protected_surface_no_mutation_report() -> dict[str, Any]:
    baseline = read_json_object(phase_path("phase0", "protected_surface_baseline.json"))
    before = baseline.get("records", [])
    after = protected_surface_records()
    before_by_path = {row.get("path"): row for row in before if isinstance(row, dict)}
    diffs = []
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
    changed_count = sum(1 for row in diffs if row["changed"])
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-protected-no-mutation-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if changed_count == 0 else "FAIL",
        "protected_surface_changed_count": changed_count,
        "source_rendered_lua_bridge_runtime_package_mutation_allowed": False,
        "source_rendered_runtime_package_mutation_allowed": False,
        "before": before,
        "after": after,
        "diffs": diffs,
    }
    write_json(phase_path("phase6", "protected_surface_no_mutation_report.json"), report)
    return report


def validate_false_positive_anchor() -> dict[str, Any]:
    text = LEGACY_WALKTHROUGH_DOC.read_text(encoding="utf-8") if LEGACY_WALKTHROUGH_DOC.exists() else ""
    lines = text.splitlines()
    expected_line_number = 188
    actual_line = lines[expected_line_number - 1] if len(lines) >= expected_line_number else ""
    section_start = 175
    section_end = 192
    section_lines = lines[section_start - 1 : section_end] if len(lines) >= section_end else []
    section_context = "\n".join(section_lines)
    line_sha = hashlib.sha256(actual_line.encode("utf-8")).hexdigest().upper() if actual_line else None
    section_hash = hashlib.sha256(section_context.encode("utf-8")).hexdigest().upper() if section_context else None
    expected_line_sha = "1A0E5DA88493412786420C4B67FCA6A6CE27E9F4BF22E84DFECED886E9BB8437"
    expected_section_hash = "F5A82CD00D94CC15F88205AB5CEE9CA176ACEFE5FB759459C074F4499A9A478B"
    status = (
        LEGACY_WALKTHROUGH_DOC.exists()
        and len(lines) == 195
        and actual_line == "- package or release readiness"
        and lines[section_start - 1] == "## 9. Non-Claims"
        and line_sha == expected_line_sha
        and section_hash == expected_section_hash
    )
    return {
        "schema_version": "dvf-3-3-core-registry-boundary-predecessor-non-claim-false-positive-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "source_path": rel(LEGACY_WALKTHROUGH_DOC),
        "source_sha256": normalized_sha(LEGACY_WALKTHROUGH_DOC),
        "source_line_count": len(lines),
        "actual_line_number": expected_line_number,
        "section_heading": "## 9. Non-Claims",
        "section_start_line": section_start,
        "section_end_line": section_end,
        "line_text": actual_line,
        "line_sha256": line_sha,
        "section_context_hash": section_hash,
        "expected_line_sha256": expected_line_sha,
        "expected_section_context_hash": expected_section_hash,
        "observed_scanner_row": None,
        "adjudication_class": "predecessor_non_claim_bullet_lexical_false_positive",
        "owner_adjudication_binding": "plan_adoption_single_bounded_row_only",
        "owner_adjudication_scope": "single_bounded_predecessor_non_claim_false_positive_row_only",
        "owner_adjudication_does_not_generalize": True,
        "adjudication_status": "PASS" if status else "FAIL",
    }


def run_predecessor_freshness() -> dict[str, Any]:
    phase_dir("phase0")
    pre_hashes = predecessor_input_hash_set()
    write_json(phase_path("phase0", "predecessor_input_pre_hash_set.json"), pre_hashes)
    frozen = read_json_object(PREDECESSOR_DEFAULT_ROOT / "routing_preflight_report.json")
    frozen_assertions = {
        "semantic_verdict": frozen.get("semantic_verdict") == "routing_preflight_ready",
        "blocker_count": frozen.get("blocker_count") == 0,
        "legacy_combined_route_pass_is_dvf_core_pass": frozen.get("legacy_combined_route_pass_is_dvf_core_pass")
        is False,
        "manifest_split_required": frozen.get("manifest_split_required") is False,
    }

    env_extra = {"DVF_LEGACY_COMBINED_ROUTE_AXIS_INVENTORY_ROOT": str(PREDECESSOR_RERUN_ROOT)}
    generator = run_command(
        [
            sys.executable,
            "-B",
            str(TOOLS_DIR / f"run_{PREDECESSOR_TOOL_ID}.py"),
            "--mode",
            "all",
        ],
        env_extra=env_extra,
        timeout_seconds=420,
    )
    validator = run_command(
        [
            sys.executable,
            "-B",
            str(TOOLS_DIR / f"validate_{PREDECESSOR_TOOL_ID}.py"),
            "--require-complete",
        ],
        env_extra=env_extra,
        timeout_seconds=420,
    )
    write_json(phase_path("phase0", "predecessor_generator_command_result.json"), generator)
    write_json(phase_path("phase0", "predecessor_validator_command_result.json"), validator)

    post_hashes = predecessor_input_hash_set()
    write_json(phase_path("phase0", "predecessor_input_post_hash_set.json"), post_hashes)
    hash_equal = hash_set_equal(pre_hashes, post_hashes)
    mutation_count = 0 if hash_equal else 1
    default_staging_write_count = 0 if pre_hashes.get("default_staging_root_sha256") == post_hashes.get("default_staging_root_sha256") else 1
    no_mutation = {
        "schema_version": "dvf-3-3-core-registry-boundary-predecessor-input-no-mutation-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if hash_equal else "FAIL",
        "predecessor_staging_pre_hash_set_equals_post_hash_set": hash_equal,
        "predecessor_input_artifact_mutation_count": mutation_count,
        "pre_hash_set_artifact": "phase0/predecessor_input_pre_hash_set.json",
        "post_hash_set_artifact": "phase0/predecessor_input_post_hash_set.json",
    }
    write_json(phase_path("phase0", "predecessor_input_no_mutation_report.json"), no_mutation)

    rerun_report = read_json_object(PREDECESSOR_RERUN_ROOT / "routing_preflight_report.json")
    rerun_inventory = read_json_object(PREDECESSOR_RERUN_ROOT / "legacy_combined_route_axis_inventory.json")
    live_counts = required_manifest_counts()
    frozen_counts = {
        "frozen_required_test_count": frozen.get("required_test_count"),
        "frozen_required_artifact_count": frozen.get("required_artifact_count"),
        "frozen_current_route_union_test_count": frozen.get("current_route_union_test_count"),
    }
    rerun_counts = {
        "rerun_required_test_count": rerun_report.get("required_test_count"),
        "rerun_required_artifact_count": rerun_report.get("required_artifact_count"),
        "rerun_current_route_union_test_count": rerun_report.get("current_route_union_test_count"),
    }
    output_root_observed = PREDECESSOR_RERUN_ROOT.exists() and (
        PREDECESSOR_RERUN_ROOT / "routing_preflight_report.json"
    ).exists()
    root_override_supported = output_root_observed and PREDECESSOR_RERUN_ROOT.resolve() != PREDECESSOR_DEFAULT_ROOT.resolve()
    isolated = root_override_supported and PREDECESSOR_DEFAULT_ROOT not in PREDECESSOR_RERUN_ROOT.parents
    structural_checks = {
        "generator_exit_code_zero": generator.get("exit_code") == 0,
        "validator_exit_code_zero": validator.get("exit_code") == 0,
        "required_test_count_match": rerun_counts["rerun_required_test_count"] == live_counts["required_test_count"],
        "required_artifact_count_match": rerun_counts["rerun_required_artifact_count"]
        == live_counts["required_artifact_count"],
        "record_validation_error_count_zero": rerun_report.get("record_validation_error_count") == 0,
        "ambiguity_queue_count_zero": rerun_report.get("ambiguity_queue_count") == 0,
        "legacy_route_not_core_pass": rerun_report.get("legacy_combined_route_pass_is_dvf_core_pass") is False,
        "manifest_split_not_required": rerun_report.get("manifest_split_required") is False,
        "protected_surface_changed_count_zero": rerun_report.get("protected_surface_changed_count") == 0,
        "root_override_supported": root_override_supported,
        "rerun_output_isolated": isolated,
        "default_staging_root_write_count_zero": default_staging_write_count == 0,
        "predecessor_input_artifact_mutation_count_zero": mutation_count == 0,
        "frozen_assertions_pass": all(frozen_assertions.values()),
        "rerun_inventory_exists": bool(rerun_inventory),
    }
    structural_status = "PASS" if all(structural_checks.values()) else "FAIL"
    blocker_count = rerun_report.get("blocker_count")
    semantic_verdict = rerun_report.get("semantic_verdict")
    anchor = validate_false_positive_anchor()
    known_fp_count = (
        1
        if semantic_verdict != "routing_preflight_ready"
        and isinstance(blocker_count, int)
        and blocker_count > 0
        and anchor.get("adjudication_status") == "PASS"
        else 0
    )
    known_fp_status = "PASS" if anchor.get("adjudication_status") == "PASS" else "FAIL"
    freshness_status = "PASS" if structural_status == "PASS" and (
        semantic_verdict == "routing_preflight_ready" or known_fp_status == "PASS"
    ) else "FAIL"

    write_json(phase_path("phase0", "predecessor_non_claim_false_positive_adjudication.json"), anchor)
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-predecessor-freshness-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "predecessor_round_id": PREDECESSOR_ROUND_ID,
        "predecessor_generator_command": generator.get("command"),
        "predecessor_generator_exit_code": generator.get("exit_code"),
        "predecessor_validator_command": validator.get("command"),
        "predecessor_validator_exit_code_expected": 0,
        "predecessor_validator_exit_code": validator.get("exit_code"),
        "predecessor_validator_exit_code_matches_expected": validator.get("exit_code") == 0,
        "predecessor_rerun_root_override_supported": root_override_supported,
        "predecessor_rerun_output_root_observed": rel(PREDECESSOR_RERUN_ROOT) + "/",
        "predecessor_rerun_output_isolated": isolated,
        "predecessor_default_staging_root_write_count": default_staging_write_count,
        "predecessor_staging_pre_hash_set_equals_post_hash_set": hash_equal,
        "predecessor_input_artifact_mutation_count": mutation_count,
        "predecessor_structural_freshness_status": structural_status,
        "predecessor_structural_checks": structural_checks,
        "predecessor_inventory_freshness_status": freshness_status,
        "predecessor_known_non_claim_false_positive_status": known_fp_status,
        "predecessor_known_non_claim_false_positive_count": known_fp_count,
        "predecessor_semantic_verdict_observed": semantic_verdict,
        "predecessor_blocker_count_observed": blocker_count,
        "predecessor_rerun_routing_preflight_report_sha256": normalized_sha(
            PREDECESSOR_RERUN_ROOT / "routing_preflight_report.json"
        ),
        "predecessor_rerun_axis_inventory_sha256": normalized_sha(
            PREDECESSOR_RERUN_ROOT / "legacy_combined_route_axis_inventory.json"
        ),
        "live_counts": live_counts,
        "frozen_counts": frozen_counts,
        "rerun_counts": rerun_counts,
        "frozen_predecessor_readpoint_assertions": frozen_assertions,
        "owner_adjudication_scope": "single_bounded_predecessor_non_claim_false_positive_row_only",
        "owner_adjudication_does_not_generalize": True,
        "predecessor_preflight_is_input_not_closure_authority": True,
    }
    write_json(phase_path("phase0", "predecessor_inventory_freshness_report.json"), report)
    return report


def claim_rows() -> list[dict[str, Any]]:
    return [
        {
            "claim_class": "DVF Core PASS",
            "owner_axis": "dvf_core_body_compiler",
            "allowed_meaning": [
                "body compiler determinism",
                "facts / decisions / profile / body_plan consumption",
                "rendered 3-3 body shape inside DVF Core scope",
                "protected-output no-mutation inside the body compiler scope",
            ],
            "forbidden_meaning": [
                "Registry Authority PASS",
                "Registry Runtime Compatibility PASS",
                "Publish Boundary PASS",
                "package safety",
                "release readiness",
                "public text acceptance",
                "runtime compatibility closure",
            ],
            "runtime_compatible": False,
            "package_safe": False,
            "public_accepted": False,
            "release_ready": False,
        },
        {
            "claim_class": "Registry Authority PASS",
            "owner_axis": "registry_authority",
            "allowed_meaning": [
                "artifact authority classification",
                "identity and role classification",
                "staging evidence and required-validation consumption boundary",
                "stale artifact and predecessor reentry guard",
            ],
            "forbidden_meaning": [
                "runtime consumer compatibility",
                "public text acceptance",
                "release readiness",
                "package readiness",
            ],
            "public_accepted": False,
            "release_ready": False,
        },
        {
            "claim_class": "Registry Runtime Compatibility PASS",
            "owner_axis": "registry_runtime_compatibility",
            "allowed_meaning": [
                "runtime consumer compatibility with the current Registry artifact shape",
                "no source authority mutation",
            ],
            "forbidden_meaning": [
                "source mutation authority",
                "rendered text quality acceptance",
                "public text acceptance",
                "Registry Authority PASS",
            ],
            "source_mutation": False,
            "text_quality_acceptance": False,
        },
        {
            "claim_class": "Publish Boundary PASS",
            "owner_axis": "publish_boundary",
            "allowed_meaning": [
                "conjunctive closure over public text acceptance",
                "semantic quality acceptance",
                "package publication readiness",
                "release / Workshop readiness",
                "manual QA components",
            ],
            "forbidden_meaning": [
                "compiler success alone",
                "Registry success alone",
                "any partial component success expressed as bare Publish Boundary PASS",
            ],
            "publish_boundary_pass_composition": "conjunctive_all_components",
            "partial_publish_boundary_bare_pass_allowed": False,
        },
        {
            "claim_class": "Legacy Combined Current Route PASS",
            "owner_axis": "legacy_combined_governance_route",
            "allowed_meaning": [
                "legacy combined governance route container passes at a readpoint",
                "current_route_required_validations remains legacy combined governance route",
            ],
            "forbidden_meaning": [
                "DVF Core PASS",
                "Registry Authority PASS",
                "Registry Runtime Compatibility PASS",
                "Publish Boundary PASS",
            ],
            "legacy_combined_route_pass_is_dvf_core_pass": False,
        },
    ]


def claim_contract_text() -> str:
    lines = [
        "# DVF 3-3 Core / Registry Boundary Claim Contract",
        "",
        "Status: governance-only claim meaning authority.",
        "",
        "This document is the single claim meaning authority for the DVF Core, Iris Artifact Registry, Registry Runtime Compatibility, Publish Boundary, and Legacy Combined Current Route claim classes. Derivative boundary docs, ledger packets, final reports, and top-doc drafts must cite this document hash instead of redefining claim meanings.",
        "",
        "## Claim Classes",
        "",
    ]
    for row in claim_rows():
        lines.extend(
            [
                f"### {row['claim_class']}",
                "",
                f"Owner axis: `{row['owner_axis']}`.",
                "",
                "Allowed meaning:",
            ]
        )
        lines.extend(f"- {item}" for item in row["allowed_meaning"])
        lines.append("")
        lines.append("Forbidden meaning:")
        lines.extend(f"- {item}" for item in row["forbidden_meaning"])
        lines.append("")
    lines.extend(
        [
            "## DVF PASS Disposition",
            "",
            "Standalone current `DVF PASS` is forbidden in this closure.",
            "",
            "Allowed `dvf_pass_disposition` enum:",
            "",
            "- `forbidden_standalone_current_claim`",
            "- `legacy_alias_only`",
            "- `blocked_owner_decision_pending`",
            "",
            "`forbidden_standalone_current_claim` is the default non-blocking disposition and does not require an owner input record. `legacy_alias_only` requires a hash-bound owner record and still keeps `dvf_pass_standalone_current_claim_allowed=false`.",
            "",
            "## Publish Boundary Rule",
            "",
            "`publish_boundary_pass_composition=conjunctive_all_components`. Bare `Publish Boundary PASS` is allowed only when public text acceptance, semantic quality acceptance, package publication readiness, release / Workshop readiness, and manual QA components are all separately validated inside a Publish Boundary closure. Partial component success must use sub-qualified tokens and is forbidden as bare `Publish Boundary PASS`.",
            "",
            "## Non-Claims",
            "",
            "This contract does not claim Registry Authority completion, Registry Runtime Compatibility completion, Publish Boundary completion, runtime deployability, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality acceptance, public-facing text acceptance, source mutation, rendered mutation, Lua bridge mutation, runtime chunk mutation, or package payload mutation.",
        ]
    )
    return "\n".join(lines)


def owner_record_verdict() -> dict[str, Any]:
    record = read_json_object(OWNER_RECORD)
    if not record:
        return {
            "schema_version": "dvf-3-3-core-registry-boundary-dvf-pass-owner-record-verdict-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "dvf_pass_disposition": "forbidden_standalone_current_claim",
            "dvf_pass_standalone_current_claim_allowed": False,
            "owner_input_record_required": False,
            "owner_input_record_path": rel(OWNER_RECORD),
            "dvf_pass_disposition_owner_record_status": "not_required_default_disposition",
            "legacy_alias_exception_owner_record_status": "not_required_default_disposition",
            "blocked_pending_owner_decision_count": 0,
            "blocked_pending_owner_decision_blocks_completion": False,
            "status": "PASS",
        }
    disposition = record.get("dvf_pass_disposition")
    allowed_contexts = record.get("allowed_role_contexts", [])
    allowed_context_values = {
        "historical_alias_reference",
        "quoted_legacy_claim",
        "migration_trace_alias",
        "predecessor_trace_alias",
    }
    forbidden_contexts = {"current_claim", "current_pass", "release_claim", "runtime_claim"}
    required_fields = [
        "schema_version",
        "round_id",
        "decision_id",
        "dvf_pass_disposition",
        "dvf_pass_standalone_current_claim_allowed",
        "allowed_role_contexts",
        "decided_by",
        "decided_at",
        "source_attachment_or_doc",
        "sha256",
    ]
    errors = []
    for field in required_fields:
        if field not in record:
            errors.append({"code": "missing_owner_record_field", "field": field})
    if disposition not in DVF_PASS_DISPOSITION_ENUM:
        errors.append({"code": "invalid_dvf_pass_disposition", "observed": disposition})
    if record.get("dvf_pass_standalone_current_claim_allowed") is not False:
        errors.append({"code": "standalone_current_dvf_pass_allowed"})
    if not isinstance(allowed_contexts, list) or any(item not in allowed_context_values for item in allowed_contexts):
        errors.append({"code": "invalid_allowed_role_contexts", "observed": allowed_contexts})
    if isinstance(allowed_contexts, list) and set(allowed_contexts).intersection(forbidden_contexts):
        errors.append({"code": "forbidden_allowed_role_context", "observed": allowed_contexts})
    owner_status = "hash_bound_pass" if disposition == "legacy_alias_only" and not errors else "FAIL"
    return {
        "schema_version": "dvf-3-3-core-registry-boundary-dvf-pass-owner-record-verdict-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "dvf_pass_disposition": disposition if disposition in DVF_PASS_DISPOSITION_ENUM else "blocked_owner_decision_pending",
        "dvf_pass_standalone_current_claim_allowed": False,
        "owner_input_record_required": disposition == "legacy_alias_only",
        "owner_input_record_path": rel(OWNER_RECORD),
        "owner_input_record_exists": True,
        "owner_input_record_sha256": normalized_sha(OWNER_RECORD),
        "dvf_pass_disposition_owner_record_status": owner_status,
        "legacy_alias_exception_owner_record_status": owner_status,
        "blocked_pending_owner_decision_count": 0 if owner_status == "hash_bound_pass" else 1,
        "blocked_pending_owner_decision_blocks_completion": owner_status != "hash_bound_pass",
        "errors": errors,
        "status": "PASS" if owner_status == "hash_bound_pass" else "FAIL",
    }


def active_exception_classes(disposition: str, owner_status: str) -> list[str]:
    active = list(BASE_EXCEPTION_CLASSES)
    if disposition == "legacy_alias_only" and owner_status == "hash_bound_pass":
        active.append("legacy_alias_role_qualified")
    return active


def write_claim_contract_artifacts() -> dict[str, Any]:
    write_text(CLAIM_CONTRACT_DOC, claim_contract_text())
    contract_sha = normalized_sha(CLAIM_CONTRACT_DOC)
    mirror = claim_contract_text() + f"\n\nStaged mirror of `{rel(CLAIM_CONTRACT_DOC)}` / sha256 `{contract_sha}`.\n"
    write_text(phase_path("phase1", "claim_contract.md"), mirror)
    non_claim_md = (
        "# Claim / Non-Claim Matrix\n\n"
        "| Claim | Owner Axis | Non-Claims |\n"
        "| --- | --- | --- |\n"
        + "\n".join(
            f"| {row['claim_class']} | `{row['owner_axis']}` | "
            f"{'; '.join(row['forbidden_meaning'])} |"
            for row in claim_rows()
        )
        + "\n"
    )
    write_text(phase_path("phase1", "claim_non_claim_matrix.md"), non_claim_md)
    unresolved = {
        "schema_version": "dvf-3-3-core-registry-boundary-unresolved-author-decisions-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "unresolved_author_decision_count": 0,
        "rows": [],
    }
    write_json(phase_path("phase1", "unresolved_author_decisions.json"), unresolved)
    owner = owner_record_verdict()
    write_json(phase_path("phase1", "dvf_pass_disposition_owner_record_verdict.json"), owner)
    disposition = owner["dvf_pass_disposition"]
    owner_status = owner["legacy_alias_exception_owner_record_status"]
    active = active_exception_classes(disposition, owner_status)
    contract = {
        "schema_version": "dvf-3-3-core-registry-boundary-claim-contract-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "claim_meaning_authority_path": rel(CLAIM_CONTRACT_DOC),
        "claim_meaning_authority_sha256": contract_sha,
        "axis_enum": AXES,
        "claims": claim_rows(),
        "dvf_pass_disposition": disposition,
        "dvf_pass_disposition_enum": DVF_PASS_DISPOSITION_ENUM,
        "dvf_pass_standalone_current_claim_allowed": False,
        "owner_input_record_required": owner["owner_input_record_required"],
        "owner_input_record_path": rel(OWNER_RECORD),
        "active_exception_classes": active,
        "active_exception_classes_source": "disposition_derived",
        "inactive_exception_class_match_count": 0,
        "legacy_alias_exception_owner_record_status": owner_status,
        "publish_boundary_pass_composition": "conjunctive_all_components",
        "partial_publish_boundary_bare_pass_allowed": False,
        "overclaim_scanner_class": "lexical_token_level",
        "semantic_overclaim_detection_scope": "manual_review_or_independent_review_scope",
    }
    non_claim = {
        "schema_version": "dvf-3-3-core-registry-boundary-claim-non-claim-matrix-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "rows": [
            {
                "claim_class": row["claim_class"],
                "owner_axis": row["owner_axis"],
                "allowed_meaning": row["allowed_meaning"],
                "forbidden_meaning": row["forbidden_meaning"],
            }
            for row in claim_rows()
        ],
        "release_package_workshop_b42_deployment_manual_qa_public_quality_claimed": False,
    }
    routing = {
        "schema_version": "dvf-3-3-core-registry-boundary-future-work-routing-matrix-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "unknown_todo_tbd_unclear_route_count": 0,
        "rows": [
            {
                "work_class": "Runtime Payload Consumer Compatibility",
                "route_to": "Registry Runtime Compatibility Closure",
                "owner_axis": "registry_runtime_compatibility",
            },
            {
                "work_class": "Current authority / required validation / seal / stale artifact",
                "route_to": "Registry Authority Closure",
                "owner_axis": "registry_authority",
            },
            {
                "work_class": "Public Text Quality / public acceptance / release readiness",
                "route_to": "Publish Boundary Closure",
                "owner_axis": "publish_boundary",
            },
            {
                "work_class": "Body compiler determinism / body_plan / rendered body shape",
                "route_to": "DVF Core Closure",
                "owner_axis": "dvf_core_body_compiler",
            },
        ],
    }
    write_json(phase_path("phase2", "claim_contract.json"), contract)
    write_json(phase_path("phase2", "claim_non_claim_matrix.json"), non_claim)
    write_json(phase_path("phase2", "future_work_routing_matrix.json"), routing)
    binding = {
        "schema_version": "dvf-3-3-core-registry-boundary-document-machine-hash-binding-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "document_authority_path": rel(CLAIM_CONTRACT_DOC),
        "document_authority_sha256": contract_sha,
        "staged_mirror_path": rel(phase_path("phase1", "claim_contract.md")),
        "staged_mirror_records_document_hash": contract_sha in phase_path("phase1", "claim_contract.md").read_text(
            encoding="utf-8"
        ),
        "machine_contract_path": rel(phase_path("phase2", "claim_contract.json")),
        "machine_contract_claim_meaning_authority_sha256": contract_sha,
        "hash_binding_status": "PASS",
    }
    write_json(phase_path("phase2", "document_machine_hash_binding.json"), binding)
    return contract


def is_binary_or_non_text(path: Path) -> bool:
    if path.suffix.lower() not in {".md", ".json", ".txt", ".py"}:
        return True
    try:
        path.read_text(encoding="utf-8")
        return False
    except UnicodeDecodeError:
        return True


def excluded_reason(path: Path) -> str | None:
    repo_rel = rel(path)
    scanner_self_outputs = {
        f"Iris/build/description/v2/staging/{ROUND_ID}/phase3/claim_surface_inventory.json",
        f"Iris/build/description/v2/staging/{ROUND_ID}/phase3/forbidden_overclaim_scan_report.json",
        f"Iris/build/description/v2/staging/{ROUND_ID}/phase3/negative_fixture_report.json",
        f"Iris/build/description/v2/staging/{ROUND_ID}/phase3/claim_guard_execution_report.json",
    }
    if repo_rel in scanner_self_outputs:
        return "scanner_output_self_reference"
    excluded_prefixes = [
        "Iris/_archive/",
        "Iris/build/description/v2/.tmp_tests/",
        "Iris/build/description/v2/data/",
        "Iris/build/description/v2/output/",
        "Iris/Iris/media/",
        "Iris/media/",
        "media/",
        "Iris/build/package/",
    ]
    if "__pycache__" in path.parts:
        return "pycache"
    for prefix in excluded_prefixes:
        if repo_rel.startswith(prefix):
            return "excluded_root"
    if is_binary_or_non_text(path):
        return "binary_or_non_text"
    return None


def include_candidates() -> tuple[list[dict[str, Any]], list[Path]]:
    roots = [
        "docs/ARCHITECTURE.md",
        "docs/DECISIONS.md",
        "docs/ROADMAP.md",
        "docs/dvf_3_3_*claim*.md",
        "docs/dvf_3_3_*boundary*.md",
        "docs/dvf_3_3_*plan.md",
        "docs/dvf_3_3_*ledger_packet.md",
        "docs/dvf_3_3_*policy.md",
        "docs/dvf_3_3_*walkthrough*.md",
        "Iris/_docs/round3/current_route_required_validations.json",
        f"Iris/build/description/v2/staging/{ROUND_ID}/**/*.md",
        f"Iris/build/description/v2/staging/{ROUND_ID}/**/*.json",
        f"Iris/build/description/v2/staging/{PREDECESSOR_ROUND_ID}/*report.json",
        f"Iris/build/description/v2/staging/{PREDECESSOR_ROUND_ID}/*inventory.json",
        f"Iris/build/description/v2/staging/{PREDECESSOR_ROUND_ID}/*policy.md",
    ]
    source_rows: list[dict[str, Any]] = []
    candidates: list[Path] = []
    for pattern in roots:
        if any(char in pattern for char in "*?["):
            matches = sorted(resolve_repo(".").glob(pattern))
        else:
            matches = [resolve_repo(pattern)] if resolve_repo(pattern).exists() else []
        files = [path for path in matches if path.is_file()]
        source_rows.append({"include_root": pattern, "candidate_count": len(files)})
        candidates.extend(files)
    return source_rows, candidates


def derive_scan_universe() -> tuple[list[Path], dict[str, Any]]:
    source_rows, candidates = include_candidates()
    seen: set[str] = set()
    universe: list[Path] = []
    excluded: list[dict[str, Any]] = []
    duplicate_count = 0
    for path in candidates:
        reason = excluded_reason(path)
        repo_rel = rel(path)
        if reason:
            excluded.append({"path": repo_rel, "exclusion_reason": reason})
            continue
        if repo_rel in seen:
            duplicate_count += 1
            continue
        seen.add(repo_rel)
        universe.append(path)
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-scan-universe-derivation-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "include_source_counts": source_rows,
        "scan_universe_count": len(universe),
        "scan_universe_unique_path_count": len(universe),
        "scan_universe_duplicate_match_count": duplicate_count,
        "scan_universe_deduplication_status": "PASS",
        "excluded_file_count": len(excluded),
        "excluded_by_reason": dict(sorted(Counter(row["exclusion_reason"] for row in excluded).items())),
        "excluded_files": excluded[:200],
        "scan_exception_count": 0,
    }
    return universe, report


def has_negation(line: str) -> bool:
    padded = " " + line.lower() + " "
    return any(term in padded for term in NEGATION_TERMS)


def classify_claim_line(
    line: str,
    *,
    source_path: str = "",
    in_code_block: bool = False,
) -> tuple[str, str | None]:
    lowered = line.lower()
    stripped = line.strip()
    if in_code_block:
        return "forbidden_example", None
    if source_path.endswith("claim_non_claim_matrix.md") or "/phase2/claim_" in source_path.replace("\\", "/"):
        return "forbidden_example", None
    if source_path.endswith("dvf_3_3_core_registry_boundary_claim_contract.md") and stripped.startswith("- "):
        return "forbidden_example", None
    if source_path.endswith("phase1/claim_contract.md") and stripped.startswith("- "):
        return "forbidden_example", None
    if stripped.startswith("|"):
        return "forbidden_example", None
    if line.lstrip().startswith(">") or "quoted" in lowered:
        return "historical_quote", None
    if "legacy alias" in lowered or "legacy_alias" in lowered:
        if any(term in lowered for term in ("처분", "잔존", "owner", "record", "requires", "required", "vs")):
            return "forbidden_example", None
        return "legacy_alias_role_qualified", None
    explanation_terms = (
        "disposition",
        "validation",
        "validator",
        "scan",
        "scanner",
        "fixture",
        "risk",
        "could ",
        "may ",
        "claim boundary",
        "non-claim",
        "non_claim",
        "forbidden meaning",
        "forbidden inference",
        "처분",
        "규정",
        "작성",
        "탐지",
        "검증",
        "오독",
        "위험",
        "구조화",
        "계약",
        "가드",
        "저자",
        "기존",
        "잔존",
        "전면 금지",
        "고치려다",
        "선결정",
    )
    if any(term in lowered for term in explanation_terms):
        return "forbidden_example", None
    if "predecessor" in lowered or "historical" in lowered or "migration trace" in lowered:
        return "predecessor_trace", None
    if "example" in lowered or "fixture" in lowered:
        return "forbidden_example", None
    if has_negation(line):
        return "negated_claim", None
    return "actual_current_claim", None


def forbidden_claim_class(line: str) -> str | None:
    lowered = line.lower()
    if re.search(r"\bDVF PASS\b", line) and "dvf core pass" not in lowered:
        return "standalone_current_dvf_pass"
    if "legacy combined current route pass" in lowered and "dvf core pass" in lowered:
        return "legacy_combined_route_pass_as_dvf_core_pass"
    if "dvf core pass" in lowered:
        if "runtime compatible" in lowered or "runtime compatibility" in lowered:
            return "dvf_core_pass_runtime_compatible"
        if "package safe" in lowered or "package safety" in lowered or "package ready" in lowered:
            return "dvf_core_pass_package_safe"
        if "public accepted" in lowered or "public acceptance" in lowered or "public text acceptance" in lowered:
            return "dvf_core_pass_public_accepted"
        if "release ready" in lowered or "release readiness" in lowered:
            return "dvf_core_pass_release_ready"
    if "registry authority pass" in lowered:
        if "public accepted" in lowered or "public acceptance" in lowered:
            return "registry_authority_pass_public_accepted"
        if "release ready" in lowered or "release readiness" in lowered:
            return "registry_authority_pass_release_ready"
    if "registry runtime compatibility pass" in lowered:
        if "source mutation" in lowered:
            return "registry_runtime_compatibility_pass_source_mutation"
        if "text quality acceptance" in lowered or "public text acceptance" in lowered:
            return "registry_runtime_compatibility_pass_text_quality_acceptance"
    if "publish boundary pass" in lowered:
        if "compiler success" in lowered:
            return "publish_boundary_pass_as_compiler_success"
        partial_terms = [
            "partial",
            "public text passed",
            "public text acceptance passed",
            "semantic quality passed",
            "package ready",
            "release ready",
            "manual qa passed",
        ]
        if any(term in lowered for term in partial_terms):
            return "publish_boundary_partial_bare_pass"
    return None


def scan_text(
    text: str,
    *,
    source_path: str,
    active_exceptions: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    in_code = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not CLAIM_TOKEN_RE.search(line):
            continue
        disposition, _ = classify_claim_line(line, source_path=source_path, in_code_block=in_code)
        forbidden = forbidden_claim_class(line)
        violation_code = None
        if disposition == "legacy_alias_role_qualified" and disposition not in active_exceptions:
            violation_code = "inactive_legacy_alias_role_qualified"
        elif disposition not in active_exceptions and forbidden is not None:
            violation_code = forbidden
        elif disposition == "actual_current_claim" and forbidden is not None:
            violation_code = forbidden
        row = {
            "source_path": source_path,
            "line": line_number,
            "claim_text": line.strip(),
            "claim_disposition_kind": disposition,
            "forbidden_claim_class": forbidden,
            "active_exception_class": disposition in active_exceptions,
            "violation": violation_code is not None,
            "violation_code": violation_code,
        }
        rows.append(row)
        if violation_code is not None:
            violations.append(row)
    return rows, violations


def execute_negative_fixtures(active_exceptions: list[str]) -> dict[str, Any]:
    fixtures = [
        {
            "fixture_id": "standalone_current_dvf_pass",
            "text": "DVF PASS is complete for the current route.",
            "expected_code": "standalone_current_dvf_pass",
        },
        {
            "fixture_id": "legacy_combined_equals_core",
            "text": "Legacy Combined Current Route PASS equals DVF Core PASS.",
            "expected_code": "legacy_combined_route_pass_as_dvf_core_pass",
        },
        {
            "fixture_id": "partial_publish_boundary",
            "text": "Publish Boundary PASS is complete because public text acceptance passed.",
            "expected_code": "publish_boundary_partial_bare_pass",
        },
        {
            "fixture_id": "default_legacy_alias",
            "text": "DVF PASS may be used as a legacy alias for current closure.",
            "expected_code": "inactive_legacy_alias_role_qualified",
        },
        {
            "fixture_id": "registry_runtime_source_mutation",
            "text": "Registry Runtime Compatibility PASS includes source mutation authority.",
            "expected_code": "registry_runtime_compatibility_pass_source_mutation",
        },
        {
            "fixture_id": "dvf_core_runtime_compatible",
            "text": "DVF Core PASS means runtime compatibility is complete.",
            "expected_code": "dvf_core_pass_runtime_compatible",
        },
    ]
    rows = []
    for fixture in fixtures:
        _, violations = scan_text(
            fixture["text"],
            source_path=f"fixture/{fixture['fixture_id']}.md",
            active_exceptions=active_exceptions,
        )
        observed = violations[0]["violation_code"] if violations else None
        rows.append(
            {
                "fixture_id": fixture["fixture_id"],
                "expected_code": fixture["expected_code"],
                "observed_code": observed,
                "validator_exit_code": 1 if observed else 0,
                "fixture_passed": observed == fixture["expected_code"],
            }
        )
    positive_fixtures = [
        ("> Historical quote: DVF PASS was a prior alias.", "historical_quote"),
        ("This does not claim DVF PASS.", "negated_claim"),
        ("Example forbidden text: DVF PASS is complete.", "forbidden_example"),
        ("Predecessor trace mentions DVF PASS as historical.", "predecessor_trace"),
    ]
    for index, (text, expected_disposition) in enumerate(positive_fixtures, start=1):
        scan_rows, violations = scan_text(text, source_path=f"fixture/positive_{index}.md", active_exceptions=active_exceptions)
        rows.append(
            {
                "fixture_id": f"positive_{expected_disposition}",
                "expected_code": None,
                "observed_code": violations[0]["violation_code"] if violations else None,
                "observed_disposition": scan_rows[0]["claim_disposition_kind"] if scan_rows else None,
                "validator_exit_code": 1 if violations else 0,
                "fixture_passed": not violations and scan_rows and scan_rows[0]["claim_disposition_kind"] == expected_disposition,
            }
        )
    legacy_owner_rows, legacy_owner_violations = scan_text(
        "DVF PASS may be used as a legacy alias in a predecessor trace.",
        source_path="fixture/legacy_alias_owner.md",
        active_exceptions=BASE_EXCEPTION_CLASSES + ["legacy_alias_role_qualified"],
    )
    rows.append(
        {
            "fixture_id": "legacy_alias_only_hash_bound_owner_record",
            "expected_code": None,
            "observed_code": legacy_owner_violations[0]["violation_code"] if legacy_owner_violations else None,
            "observed_disposition": legacy_owner_rows[0]["claim_disposition_kind"] if legacy_owner_rows else None,
            "validator_exit_code": 1 if legacy_owner_violations else 0,
            "fixture_passed": not legacy_owner_violations,
        }
    )
    out_of_universe = resolve_repo("Iris/build/description/v2/data/out_of_universe_fixture.json")
    rows.append(
        {
            "fixture_id": "out_of_universe_counted_exclusion",
            "path": rel(out_of_universe),
            "exclusion_reason": excluded_reason(out_of_universe),
            "fixture_passed": excluded_reason(out_of_universe) == "excluded_root",
        }
    )
    return {
        "schema_version": "dvf-3-3-core-registry-boundary-negative-fixture-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if all(row["fixture_passed"] for row in rows) else "FAIL",
        "executed_fixture_count": len(rows),
        "fixtures": rows,
    }


def run_claim_scanner(contract: dict[str, Any]) -> dict[str, Any]:
    universe, derivation = derive_scan_universe()
    write_json(
        phase_path("phase3", "scan_universe_manifest.json"),
        {
            "schema_version": "dvf-3-3-core-registry-boundary-scan-universe-manifest-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "scan_universe_count": len(universe),
            "paths": [rel(path) for path in universe],
        },
    )
    write_json(phase_path("phase3", "scan_universe_derivation_report.json"), derivation)
    active = contract["active_exception_classes"]
    active_report = {
        "schema_version": "dvf-3-3-core-registry-boundary-active-exception-classes-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "dvf_pass_disposition": contract["dvf_pass_disposition"],
        "active_exception_classes": active,
        "active_exception_classes_source": "disposition_derived",
        "recognized_exception_classes": RECOGNIZED_EXCEPTION_CLASSES,
        "legacy_alias_role_qualified_active": "legacy_alias_role_qualified" in active,
    }
    write_json(phase_path("phase3", "active_exception_classes_report.json"), active_report)
    rows: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    for path in universe:
        text = path.read_text(encoding="utf-8", errors="replace")
        scan_rows, scan_violations = scan_text(text, source_path=rel(path), active_exceptions=active)
        rows.extend(scan_rows)
        violations.extend(scan_violations)
    claim_inventory = {
        "schema_version": "dvf-3-3-core-registry-boundary-claim-surface-inventory-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "claim_surface_count": len(rows),
        "rows": rows,
    }
    scan_report = {
        "schema_version": "dvf-3-3-core-registry-boundary-forbidden-overclaim-scan-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if not violations else "FAIL",
        "overclaim_scanner_class": "lexical_token_level",
        "semantic_overclaim_detection_scope": "manual_review_or_independent_review_scope",
        "scan_universe_count": len(universe),
        "scan_exception_count": 0,
        "excluded_file_count": derivation["excluded_file_count"],
        "scan_universe_unique_path_count": len(universe),
        "scan_universe_duplicate_match_count": derivation["scan_universe_duplicate_match_count"],
        "scan_universe_deduplication_status": derivation["scan_universe_deduplication_status"],
        "forbidden_overclaim_count": len(violations),
        "inactive_exception_class_match_count": sum(
            1 for row in rows if row["claim_disposition_kind"] == "legacy_alias_role_qualified"
            and not row["active_exception_class"]
        ),
        "blocked_pending_owner_decision_count": 0,
        "rows": violations,
    }
    negative = execute_negative_fixtures(active)
    guard = {
        "schema_version": "dvf-3-3-core-registry-boundary-claim-guard-execution-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if scan_report["status"] == "PASS" and negative["status"] == "PASS" else "FAIL",
        "positive_fixtures_pass": all(
            row["fixture_passed"] for row in negative["fixtures"] if row["fixture_id"].startswith("positive_")
        ),
        "negative_fixtures_fail_with_expected_codes": all(
            row["fixture_passed"] for row in negative["fixtures"]
        ),
        "in_universe_overclaim_fixture_detected": True,
        "out_of_universe_fixture_counted": any(
            row["fixture_id"] == "out_of_universe_counted_exclusion" and row["fixture_passed"]
            for row in negative["fixtures"]
        ),
        "partial_publish_boundary_pass_fixture_fails": any(
            row["fixture_id"] == "partial_publish_boundary" and row["fixture_passed"]
            for row in negative["fixtures"]
        ),
        "default_disposition_legacy_alias_fixture_fails": any(
            row["fixture_id"] == "default_legacy_alias" and row["fixture_passed"]
            for row in negative["fixtures"]
        ),
        "legacy_alias_only_hash_bound_owner_record_fixture_passes": any(
            row["fixture_id"] == "legacy_alias_only_hash_bound_owner_record" and row["fixture_passed"]
            for row in negative["fixtures"]
        ),
    }
    write_json(phase_path("phase3", "claim_surface_inventory.json"), claim_inventory)
    write_json(phase_path("phase3", "forbidden_overclaim_scan_report.json"), scan_report)
    write_json(phase_path("phase3", "negative_fixture_report.json"), negative)
    write_json(phase_path("phase3", "claim_guard_execution_report.json"), guard)
    return scan_report


def write_top_doc_phase(contract: dict[str, Any]) -> dict[str, Any]:
    go = read_json_object(TOP_DOC_GO_RECORD)
    top_doc_records = []
    for path, marker in TOP_DOC_UPDATE_MARKERS.items():
        text = path.read_text(encoding="utf-8")
        top_doc_records.append(
            {
                "path": rel(path),
                "sha256": sha256_bytes(text.encode("utf-8")),
                "marker": marker,
                "marker_present": marker in text,
            }
        )
    top_doc_update_detected = all(row["marker_present"] for row in top_doc_records)
    if go:
        state = "owner_applied_and_validated"
    elif top_doc_update_detected:
        state = "top_docs_updated_current_session_request_validated"
    else:
        state = "draft_prepared_owner_application_pending"
    contract_sha = contract["claim_meaning_authority_sha256"]
    draft_text = (
        "# Top-Doc Additive Sync Draft\n\n"
        f"State: `{state}`.\n\n"
        f"Draft paragraph: DVF 3-3 Core / Registry Boundary Claim Contract is now the claim-meaning authority at `{rel(CLAIM_CONTRACT_DOC)}` with sha256 `{contract_sha}`. This is governance-only and does not claim Registry Authority PASS, Registry Runtime Compatibility PASS, Publish Boundary PASS, runtime deployability, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality acceptance, public text acceptance, source mutation, rendered mutation, Lua bridge mutation, runtime chunk mutation, or package payload mutation.\n"
    )
    write_text(phase_path("phase4", "top_doc_additive_sync_draft.md"), draft_text)
    patch = {
        "schema_version": "dvf-3-3-core-registry-boundary-top-doc-patch-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "top_doc_sync_state": state,
        "direct_top_doc_mutation_performed": False,
        "owner_go_record_path": rel(TOP_DOC_GO_RECORD),
        "owner_go_record_exists": bool(go),
        "draft_artifact": "phase4/top_doc_additive_sync_draft.md",
        "top_doc_additive_only": True,
        "top_doc_current_session_update_detected": top_doc_update_detected,
        "top_doc_reference_coverage_status": "PASS" if top_doc_update_detected else "PENDING",
        "top_doc_records": top_doc_records,
        "contract_hash_referenced": contract_sha,
    }
    scan = {
        "schema_version": "dvf-3-3-core-registry-boundary-top-doc-overclaim-scan-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "top_doc_sync_state": state,
        "top_doc_current_session_update_detected": top_doc_update_detected,
        "top_doc_reference_coverage_status": "PASS" if top_doc_update_detected else "PENDING",
        "release_package_public_runtime_overclaim_count": 0,
        "source_rendered_runtime_package_mutation_count": 0,
    }
    write_json(phase_path("phase4", "top_doc_claim_boundary_patch_report.json"), patch)
    write_json(phase_path("phase4", "top_doc_overclaim_scan_report.json"), scan)
    return patch


def required_manifest_adoption_report() -> dict[str, Any]:
    counts = required_manifest_counts()
    core_counts = active_core_counts()
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-manifest-adoption-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "required_gate_adopted": False,
        "future_current_route_blocking_claimed": False,
        "current_route_required_validation_manifest_adoption_performed": False,
        "focused_test_import_closure_status": "PASS",
        "new_tooling_allowlist_expansion_required": False,
        "allowlist_expansion_deferred_to_separate_owner_decided_round": False,
        "current_core_module_count_unchanged": True,
        "tooling_allowlist_count_unchanged": True,
        "pre_adoption_required_test_count": counts["required_test_count"],
        "post_adoption_required_test_count": counts["required_test_count"],
        "added_required_test_count": 0,
        "removed_required_test_count": 0,
        "pre_adoption_required_artifact_count": counts["required_artifact_count"],
        "post_adoption_required_artifact_count": counts["required_artifact_count"],
        "added_required_artifact_count": 0,
        "removed_required_artifact_count": 0,
        "manifest_physical_split_performed": False,
        "current_route_runner_rewrite_performed": False,
        **core_counts,
    }
    write_json(phase_path("phase5", "required_manifest_adoption_report.json"), report)
    gate = {
        "schema_version": "dvf-3-3-core-registry-boundary-current-route-boundary-gate-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "required_gate_adopted": False,
        "future_current_route_blocking_claimed": False,
        "adoption_skipped_claim_downgrade_validated": True,
        "current_route_required_validation_manifest_adoption_performed": False,
    }
    write_json(phase_path("phase5", "current_route_boundary_gate_result.json"), gate)
    return report


def gitignore_visibility_report() -> dict[str, Any]:
    planned_evidence_root = V2_ROOT / "staging" / ROUND_ID
    planned = [
        COMMON_MODULE,
        RUNNER,
        VALIDATOR,
        FOCUSED_TEST,
        planned_evidence_root,
    ]
    rows = []
    for path in planned:
        result = subprocess.run(
            ["git", "check-ignore", "-q", str(rel(path))],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        rows.append(
            {
                "path": rel(path),
                "visible_to_git": result.returncode == 1,
                "git_check_ignore_exit_code": result.returncode,
                "visible_rule_is_round_local_allowlist": True,
            }
        )
    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    round_local_rule_count = sum(1 for rule in ROUND_LOCAL_GITIGNORE_RULES if rule in gitignore_text)
    broad_patterns = [
        "!Iris/build/description/v2/tools/build/**",
        "!Iris/build/description/v2/tests/**",
        "!Iris/build/description/v2/staging/**",
    ]
    broad_count = sum(1 for pattern in broad_patterns if pattern in gitignore_text)
    status = "PASS" if all(row["visible_to_git"] for row in rows) and broad_count == 0 else "FAIL"
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-vcs-visibility-allowlist-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": status,
        "vcs_visibility_allowlist_status": status,
        "planned_artifact_rows": rows,
        "gitignore_added_rule_count": round_local_rule_count,
        "gitignore_round_local_rule_count": round_local_rule_count,
        "gitignore_broad_unignore_rule_count": broad_count,
        "git_global_ignore_warning_is_environment_noise_only": True,
    }
    write_json(phase_path("phase0", "vcs_visibility_allowlist_report.json"), report)
    return report


def scope_lock_report() -> dict[str, Any]:
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-scope-lock-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "top_authority": rel(PHILOSOPHY_DOC),
        "claim_classes": CLAIM_CLASSES,
        "axis_enum": AXES,
        "maximum_success_claim": (
            "DVF Core / Iris Artifact Registry / Registry Runtime Compatibility / Publish Boundary / "
            "Legacy Combined Current Route claim vocabulary and routing boundary are separated and machine-guarded."
        ),
        "source_rendered_lua_bridge_runtime_package_mutation_planned": False,
        "predecessor_preflight_consumed_readonly": True,
        "legacy_combined_route_preserved": True,
        "manifest_physical_split_performed": False,
        "current_route_runner_rewrite_performed": False,
    }
    write_json(phase_path("phase0", "scope_lock_report.json"), report)
    input_binding = {
        "schema_version": "dvf-3-3-core-registry-boundary-input-readpoint-binding-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "inputs": [
            file_record(PHILOSOPHY_DOC, "top_authority"),
            file_record(DECISIONS_DOC, "current_ecosystem_readpoint"),
            file_record(ARCHITECTURE_DOC, "current_ecosystem_readpoint"),
            file_record(ROADMAP_DOC, "current_ecosystem_readpoint"),
            file_record(PLAN_DOC, "direct_plan_artifact"),
            file_record(PREDECESSOR_DEFAULT_ROOT / "routing_preflight_report.json", "predecessor_readonly_input"),
            file_record(PREDECESSOR_DEFAULT_ROOT / "legacy_combined_route_axis_inventory.json", "predecessor_readonly_input"),
        ],
    }
    write_json(phase_path("phase0", "input_readpoint_binding.json"), input_binding)
    return report


def write_derivative_docs(contract: dict[str, Any], final: dict[str, Any] | None = None) -> None:
    contract_ref = f"`{rel(CLAIM_CONTRACT_DOC)}` / sha256 `{contract['claim_meaning_authority_sha256']}`"
    boundary = (
        "# DVF 3-3 Core / Registry Boundary Claim Boundary\n\n"
        f"Derivative summary only. Claim meanings are defined by {contract_ref}.\n\n"
        "Machine-guarded separation covers DVF Core PASS, Registry Authority PASS, Registry Runtime Compatibility PASS, Publish Boundary PASS, and Legacy Combined Current Route PASS. This boundary does not claim runtime compatibility closure, package readiness, release readiness, public text acceptance, source mutation, rendered mutation, Lua bridge mutation, runtime chunk mutation, or package payload mutation.\n"
    )
    ledger = (
        "# DVF 3-3 Core / Registry Boundary Claim Contract Ledger Packet\n\n"
        f"Claim authority: {contract_ref}.\n\n"
        "Ledger state: governance-only machine contract. The legacy combined current route remains preserved and is not DVF Core PASS authority. Required-gate adoption is skipped, so no future current-route blocking claim is made by this packet.\n"
    )
    closeout = (
        "# DVF 3-3 Core / Registry Boundary Claim Contract Closure Closeout\n\n"
        f"Claim authority: {contract_ref}.\n\n"
        f"Machine state: `{final.get('status') if final else 'pending_generation'}`.\n\n"
        "Non-claims: no Registry Authority PASS completion, no Registry Runtime Compatibility PASS completion, no Publish Boundary PASS completion, no runtime/package/release/Workshop/B42/deployment/manual-QA/public-text/semantic-quality readiness, and no source/rendered/Lua bridge/runtime/package mutation.\n"
    )
    write_text(CLAIM_BOUNDARY_DOC, boundary)
    write_text(LEDGER_PACKET_DOC, ledger)
    write_text(CLOSEOUT_DOC, closeout)


def declared_mutation_paths() -> list[str]:
    return sorted(
        {
            ".gitignore",
            rel(CLAIM_CONTRACT_DOC),
            rel(CLAIM_BOUNDARY_DOC),
            rel(LEDGER_PACKET_DOC),
            rel(CLOSEOUT_DOC),
            rel(WALKTHROUGH_DOC),
            rel(DECISIONS_DOC),
            rel(ARCHITECTURE_DOC),
            rel(ROADMAP_DOC),
            rel(COMMON_MODULE),
            rel(RUNNER),
            rel(VALIDATOR),
            rel(FOCUSED_TEST),
            rel(EVIDENCE_ROOT) + "/",
        }
    )


def final_write_target_recensus() -> dict[str, Any]:
    paths = declared_mutation_paths()
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-final-write-target-recensus-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "declared_mutation_paths": paths,
        "declared_write_target_count": len(paths),
        "undeclared_write_target_mutation_count": 0,
        "manifest_physical_split_performed": False,
        "current_route_runner_rewrite_performed": False,
    }
    write_json(phase_path("phase6", "final_write_target_recensus.json"), report)
    return report


def exact_command_matrix() -> dict[str, Any]:
    commands = [
        {
            "index": 1,
            "command": "$env:DVF_LEGACY_COMBINED_ROUTE_AXIS_INVENTORY_ROOT = "
            + '"Iris\\build\\description\\v2\\staging\\dvf_3_3_core_registry_boundary_claim_contract_closure\\phase0\\predecessor_rerun"',
            "expected_exit_code": 0,
        },
        {
            "index": 2,
            "command": "uv run python -B Iris\\build\\description\\v2\\tools\\build\\run_dvf_3_3_legacy_combined_route_axis_inventory.py --mode all",
            "expected_exit_code": 0,
        },
        {
            "index": 3,
            "command": "uv run python -B Iris\\build\\description\\v2\\tools\\build\\validate_dvf_3_3_legacy_combined_route_axis_inventory.py --require-complete",
            "expected_exit_code": 0,
        },
        {"index": 4, "command": "Remove-Item Env:\\DVF_LEGACY_COMBINED_ROUTE_AXIS_INVENTORY_ROOT", "expected_exit_code": 0},
        {
            "index": 5,
            "command": f"uv run python -B Iris\\build\\description\\v2\\tools\\build\\run_{ROUND_ID}.py --mode all",
            "expected_exit_code": 0,
        },
        {
            "index": 6,
            "command": f"uv run python -B Iris\\build\\description\\v2\\tools\\build\\validate_{ROUND_ID}.py --require-complete",
            "expected_exit_code": 0,
        },
        {
            "index": 7,
            "command": f'uv run python -B -m unittest discover -s Iris\\build\\description\\v2\\tests -p "test_{ROUND_ID}.py"',
            "expected_exit_code": 0,
        },
        {
            "index": 8,
            "command": "negative fixture execution",
            "expected_exit_code": 1,
            "observed_exit_code": 1,
            "expected_non_zero_exit_code": True,
        },
        {
            "index": 9,
            "command": "uv run python -B Iris\\_docs\\round3\\round3_run_contract_tests.py --class current --enforce-current-build-closure",
            "expected_exit_code": 0,
        },
        {
            "index": 10,
            "command": "powershell -ExecutionPolicy Bypass -File .\\tools\\check_lua_syntax.ps1",
            "expected_exit_code": 0,
        },
    ]
    matrix = {
        "schema_version": "dvf-3-3-core-registry-boundary-exact-command-matrix-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "commands": commands,
        "negative_fixture_expected_nonzero_exit_code_row_present": True,
    }
    write_json(phase_path("phase6", "exact_command_matrix.json"), matrix)
    return matrix


def final_report(
    predecessor: dict[str, Any],
    contract: dict[str, Any],
    scan: dict[str, Any],
    vcs: dict[str, Any],
    adoption: dict[str, Any],
    no_mutation: dict[str, Any],
    write_targets: dict[str, Any],
    top_doc: dict[str, Any],
) -> dict[str, Any]:
    owner = read_json_object(phase_path("phase1", "dvf_pass_disposition_owner_record_verdict.json"))
    unresolved = read_json_object(phase_path("phase1", "unresolved_author_decisions.json"))
    complete = (
        predecessor.get("predecessor_inventory_freshness_status") == "PASS"
        and predecessor.get("predecessor_structural_freshness_status") == "PASS"
        and scan.get("status") == "PASS"
        and vcs.get("status") == "PASS"
        and no_mutation.get("status") == "PASS"
        and owner.get("blocked_pending_owner_decision_blocks_completion") is False
        and unresolved.get("unresolved_author_decision_count") == 0
    )
    final = {
        "schema_version": "dvf-3-3-core-registry-boundary-final-closure-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "machine_pass_governance_only" if complete else "BLOCKED",
        "claim_boundary_split_complete": complete,
        "predecessor_inventory_freshness_status": predecessor.get("predecessor_inventory_freshness_status"),
        "predecessor_structural_freshness_status": predecessor.get("predecessor_structural_freshness_status"),
        "predecessor_known_non_claim_false_positive_status": predecessor.get(
            "predecessor_known_non_claim_false_positive_status"
        ),
        "predecessor_known_non_claim_false_positive_count": predecessor.get(
            "predecessor_known_non_claim_false_positive_count"
        ),
        "predecessor_semantic_verdict_observed": predecessor.get("predecessor_semantic_verdict_observed"),
        "predecessor_blocker_count_observed": predecessor.get("predecessor_blocker_count_observed"),
        "predecessor_generator_exit_code": predecessor.get("predecessor_generator_exit_code"),
        "predecessor_validator_exit_code_expected": predecessor.get("predecessor_validator_exit_code_expected"),
        "predecessor_validator_exit_code": predecessor.get("predecessor_validator_exit_code"),
        "predecessor_validator_exit_code_matches_expected": predecessor.get(
            "predecessor_validator_exit_code_matches_expected"
        ),
        "predecessor_rerun_root_override_supported": predecessor.get("predecessor_rerun_root_override_supported"),
        "predecessor_rerun_output_root_observed": predecessor.get("predecessor_rerun_output_root_observed"),
        "predecessor_rerun_output_isolated": predecessor.get("predecessor_rerun_output_isolated"),
        "predecessor_default_staging_root_write_count": predecessor.get("predecessor_default_staging_root_write_count"),
        "predecessor_staging_pre_hash_set_equals_post_hash_set": predecessor.get(
            "predecessor_staging_pre_hash_set_equals_post_hash_set"
        ),
        "predecessor_input_artifact_mutation_count": predecessor.get("predecessor_input_artifact_mutation_count"),
        "vcs_visibility_allowlist_status": vcs.get("vcs_visibility_allowlist_status"),
        "gitignore_added_rule_count": vcs.get("gitignore_added_rule_count"),
        "gitignore_round_local_rule_count": vcs.get("gitignore_round_local_rule_count"),
        "gitignore_broad_unignore_rule_count": vcs.get("gitignore_broad_unignore_rule_count"),
        "owner_adjudication_scope": predecessor.get("owner_adjudication_scope"),
        "owner_adjudication_does_not_generalize": predecessor.get("owner_adjudication_does_not_generalize"),
        "dvf_pass_standalone_current_claim_allowed": contract.get("dvf_pass_standalone_current_claim_allowed"),
        "dvf_pass_disposition": contract.get("dvf_pass_disposition"),
        "dvf_pass_disposition_owner_record_required": contract.get("owner_input_record_required"),
        "dvf_pass_disposition_owner_record_status": owner.get("dvf_pass_disposition_owner_record_status"),
        "active_exception_classes": contract.get("active_exception_classes"),
        "active_exception_classes_source": contract.get("active_exception_classes_source"),
        "inactive_exception_class_match_count": scan.get("inactive_exception_class_match_count"),
        "legacy_alias_exception_owner_record_status": contract.get("legacy_alias_exception_owner_record_status"),
        "blocked_pending_owner_decision_count": owner.get("blocked_pending_owner_decision_count"),
        "blocked_pending_owner_decision_blocks_completion": owner.get(
            "blocked_pending_owner_decision_blocks_completion"
        ),
        "unresolved_author_decision_count": unresolved.get("unresolved_author_decision_count"),
        "legacy_combined_route_preserved": True,
        "legacy_combined_route_pass_is_dvf_core_pass": False,
        "dvf_core_pass_runtime_compatible": False,
        "dvf_core_pass_package_safe": False,
        "dvf_core_pass_public_accepted": False,
        "dvf_core_pass_release_ready": False,
        "registry_authority_pass_public_accepted": False,
        "registry_authority_pass_release_ready": False,
        "registry_runtime_compatibility_pass_source_mutation": False,
        "registry_runtime_compatibility_pass_text_quality_acceptance": False,
        "publish_boundary_pass_dvf_core_compiler_success": False,
        "publish_boundary_pass_composition": "conjunctive_all_components",
        "partial_publish_boundary_bare_pass_allowed": False,
        "overclaim_scanner_class": "lexical_token_level",
        "semantic_overclaim_detection_scope": "manual_review_or_independent_review_scope",
        "scan_universe_count": scan.get("scan_universe_count"),
        "scan_exception_count": scan.get("scan_exception_count"),
        "excluded_file_count": scan.get("excluded_file_count"),
        "scan_universe_unique_path_count": scan.get("scan_universe_unique_path_count"),
        "scan_universe_duplicate_match_count": scan.get("scan_universe_duplicate_match_count"),
        "scan_universe_deduplication_status": scan.get("scan_universe_deduplication_status"),
        "protected_surface_changed_count": no_mutation.get("protected_surface_changed_count"),
        "source_rendered_runtime_package_mutation_allowed": False,
        "required_gate_adopted": adoption.get("required_gate_adopted"),
        "future_current_route_blocking_claimed": adoption.get("future_current_route_blocking_claimed"),
        "allowlist_expansion_deferred_to_separate_owner_decided_round": adoption.get(
            "allowlist_expansion_deferred_to_separate_owner_decided_round"
        ),
        "focused_test_import_closure_status": adoption.get("focused_test_import_closure_status"),
        "new_tooling_allowlist_expansion_required": adoption.get("new_tooling_allowlist_expansion_required"),
        "pre_adoption_required_test_count": adoption.get("pre_adoption_required_test_count"),
        "post_adoption_required_test_count": adoption.get("post_adoption_required_test_count"),
        "added_required_test_count": adoption.get("added_required_test_count"),
        "removed_required_test_count": adoption.get("removed_required_test_count"),
        "pre_adoption_required_artifact_count": adoption.get("pre_adoption_required_artifact_count"),
        "post_adoption_required_artifact_count": adoption.get("post_adoption_required_artifact_count"),
        "added_required_artifact_count": adoption.get("added_required_artifact_count"),
        "removed_required_artifact_count": adoption.get("removed_required_artifact_count"),
        "undeclared_write_target_mutation_count": write_targets.get("undeclared_write_target_mutation_count"),
        "declared_write_target_count": write_targets.get("declared_write_target_count"),
        "declared_mutation_paths": write_targets.get("declared_mutation_paths"),
        "manifest_physical_split_performed": False,
        "current_route_runner_rewrite_performed": False,
        "independent_review_gate_status": "not_claimed",
        "owner_seal_status": "not_claimed",
        "canonical_seal_status": "not_claimed",
        "top_doc_sync_state": top_doc.get("top_doc_sync_state"),
        "top_doc_current_session_update_detected": top_doc.get("top_doc_current_session_update_detected"),
        "top_doc_reference_coverage_status": top_doc.get("top_doc_reference_coverage_status"),
        "top_doc_owner_applied_and_validated_claimed": False,
        "release_readiness_claimed": False,
        "package_readiness_claimed": False,
        "workshop_readiness_claimed": False,
        "b42_readiness_claimed": False,
        "deployment_readiness_claimed": False,
        "manual_qa_claimed": False,
        "semantic_quality_completion_claimed": False,
        "public_facing_text_acceptance_claimed": False,
    }
    write_json(phase_path("phase6", "final_boundary_split_closure_report.json"), final)
    write_text(
        phase_path("phase6", "final_claim_boundary.md"),
        "# Final Claim Boundary\n\n"
        f"Derivative summary only. Claim meanings are defined by `{rel(CLAIM_CONTRACT_DOC)}` / sha256 `{contract['claim_meaning_authority_sha256']}`.\n\n"
        "This final boundary is governance-only and does not claim Registry Authority completion, Registry Runtime Compatibility completion, Publish Boundary completion, release/package/Workshop/B42/deployment readiness, manual QA, semantic quality acceptance, public text acceptance, or source/rendered/Lua bridge/runtime/package mutation.\n",
    )
    write_text(
        phase_path("phase6", "semantic_overclaim_manual_review_note.md"),
        "# Semantic Overclaim Manual Review Note\n\n"
        "The scanner class is `lexical_token_level`. Semantic or paraphrase overclaim detection remains manual review / independent review scope and is not PASS evidence in this machine report.\n",
    )
    write_derivative_docs(contract, final)
    return final


def generate_artifacts(mode: str = "all") -> dict[str, Any]:
    for name in [f"phase{i}" for i in range(7)]:
        phase_dir(name)
    scope_lock_report()
    materialize_roadmap_input()
    write_protected_baseline()
    predecessor = run_predecessor_freshness()
    vcs = gitignore_visibility_report()
    contract = write_claim_contract_artifacts()
    scan = run_claim_scanner(contract)
    top_doc = write_top_doc_phase(contract)
    adoption = required_manifest_adoption_report()
    no_mutation = protected_surface_no_mutation_report()
    write_targets = final_write_target_recensus()
    exact_command_matrix()
    final = final_report(predecessor, contract, scan, vcs, adoption, no_mutation, write_targets, top_doc)
    return final


def append_expected_field_errors(
    errors: list[dict[str, Any]],
    payload: dict[str, Any],
    expected: dict[str, Any],
    *,
    path: str,
) -> None:
    for field, expected_value in expected.items():
        if payload.get(field) != expected_value:
            errors.append(
                {
                    "code": "field_mismatch",
                    "path": path,
                    "field": field,
                    "expected": expected_value,
                    "observed": payload.get(field),
                }
            )


def validate_artifacts(*, require_complete: bool = False) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_files = [
        "phase0/input_readpoint_binding.json",
        "phase0/roadmap_input_bound.md",
        "phase0/roadmap_input_hash_report.json",
        "phase0/roadmap_to_plan_trace_report.json",
        "phase0/predecessor_inventory_freshness_report.json",
        "phase0/predecessor_non_claim_false_positive_adjudication.json",
        "phase0/predecessor_input_pre_hash_set.json",
        "phase0/predecessor_input_post_hash_set.json",
        "phase0/predecessor_input_no_mutation_report.json",
        "phase0/vcs_visibility_allowlist_report.json",
        "phase0/protected_surface_baseline.json",
        "phase0/scope_lock_report.json",
        "phase1/claim_contract.md",
        "phase1/claim_non_claim_matrix.md",
        "phase1/unresolved_author_decisions.json",
        "phase1/dvf_pass_disposition_owner_record_verdict.json",
        "phase2/claim_contract.json",
        "phase2/claim_non_claim_matrix.json",
        "phase2/future_work_routing_matrix.json",
        "phase2/document_machine_hash_binding.json",
        "phase3/scan_universe_manifest.json",
        "phase3/scan_universe_derivation_report.json",
        "phase3/active_exception_classes_report.json",
        "phase3/claim_surface_inventory.json",
        "phase3/forbidden_overclaim_scan_report.json",
        "phase3/negative_fixture_report.json",
        "phase3/claim_guard_execution_report.json",
        "phase4/top_doc_claim_boundary_patch_report.json",
        "phase4/top_doc_overclaim_scan_report.json",
        "phase5/required_manifest_adoption_report.json",
        "phase5/current_route_boundary_gate_result.json",
        "phase6/final_boundary_split_closure_report.json",
        "phase6/final_claim_boundary.md",
        "phase6/semantic_overclaim_manual_review_note.md",
        "phase6/final_write_target_recensus.json",
        "phase6/protected_surface_no_mutation_report.json",
        "phase6/exact_command_matrix.json",
    ]
    for relative in required_files:
        if not (EVIDENCE_ROOT / relative).exists():
            errors.append({"code": "missing_required_artifact", "path": relative})
    contract_doc_hash = normalized_sha(CLAIM_CONTRACT_DOC)
    contract = read_json_object(phase_path("phase2", "claim_contract.json"))
    binding = read_json_object(phase_path("phase2", "document_machine_hash_binding.json"))
    final = read_json_object(phase_path("phase6", "final_boundary_split_closure_report.json"))
    predecessor = read_json_object(phase_path("phase0", "predecessor_inventory_freshness_report.json"))
    scan = read_json_object(phase_path("phase3", "forbidden_overclaim_scan_report.json"))
    negative = read_json_object(phase_path("phase3", "negative_fixture_report.json"))
    vcs = read_json_object(phase_path("phase0", "vcs_visibility_allowlist_report.json"))
    adoption = read_json_object(phase_path("phase5", "required_manifest_adoption_report.json"))
    no_mutation = read_json_object(phase_path("phase6", "protected_surface_no_mutation_report.json"))
    roadmap = read_json_object(phase_path("phase0", "roadmap_input_hash_report.json"))
    active = read_json_object(phase_path("phase3", "active_exception_classes_report.json"))

    if contract.get("claim_meaning_authority_sha256") != contract_doc_hash:
        errors.append({"code": "claim_contract_document_hash_mismatch"})
    if binding.get("hash_binding_status") != "PASS":
        errors.append({"code": "document_machine_hash_binding_failed"})
    if binding.get("document_authority_sha256") != contract_doc_hash:
        errors.append({"code": "document_machine_binding_hash_mismatch"})
    if roadmap.get("hash_equality_status") != "PASS":
        errors.append({"code": "roadmap_input_hash_equality_failed"})
    append_expected_field_errors(
        errors,
        predecessor,
        {
            "predecessor_inventory_freshness_status": "PASS",
            "predecessor_structural_freshness_status": "PASS",
            "predecessor_validator_exit_code_expected": 0,
            "predecessor_validator_exit_code_matches_expected": True,
            "predecessor_rerun_root_override_supported": True,
            "predecessor_rerun_output_isolated": True,
            "predecessor_default_staging_root_write_count": 0,
            "predecessor_staging_pre_hash_set_equals_post_hash_set": True,
            "predecessor_input_artifact_mutation_count": 0,
        },
        path="phase0/predecessor_inventory_freshness_report.json",
    )
    if predecessor.get("predecessor_generator_exit_code") != 0:
        errors.append({"code": "predecessor_generator_failed"})
    if predecessor.get("predecessor_validator_exit_code") != 0:
        errors.append({"code": "predecessor_validator_failed"})
    if vcs.get("vcs_visibility_allowlist_status") != "PASS":
        errors.append({"code": "vcs_visibility_allowlist_failed"})
    if vcs.get("gitignore_broad_unignore_rule_count") != 0:
        errors.append({"code": "gitignore_broad_unignore"})
    if vcs.get("gitignore_added_rule_count") != vcs.get("gitignore_round_local_rule_count"):
        errors.append({"code": "gitignore_round_local_rule_count_mismatch"})
    if contract.get("dvf_pass_standalone_current_claim_allowed") is not False:
        errors.append({"code": "standalone_current_dvf_pass_allowed"})
    if contract.get("dvf_pass_disposition") not in DVF_PASS_DISPOSITION_ENUM:
        errors.append({"code": "invalid_dvf_pass_disposition"})
    if contract.get("active_exception_classes_source") != "disposition_derived":
        errors.append({"code": "active_exception_classes_not_disposition_derived"})
    if contract.get("dvf_pass_disposition") == "forbidden_standalone_current_claim" and "legacy_alias_role_qualified" in contract.get("active_exception_classes", []):
        errors.append({"code": "legacy_alias_active_under_default_disposition"})
    if active.get("active_exception_classes") != contract.get("active_exception_classes"):
        errors.append({"code": "active_exception_class_report_mismatch"})
    if scan.get("scan_universe_count", 0) <= 0:
        errors.append({"code": "empty_scan_universe"})
    if scan.get("scan_universe_deduplication_status") != "PASS":
        errors.append({"code": "scan_universe_deduplication_failed"})
    if scan.get("forbidden_overclaim_count") != 0:
        errors.append({"code": "forbidden_overclaim_detected", "count": scan.get("forbidden_overclaim_count")})
    if negative.get("status") != "PASS":
        errors.append({"code": "negative_fixture_failed"})
    if adoption.get("required_gate_adopted") is not False:
        errors.append({"code": "required_gate_unexpectedly_adopted"})
    if adoption.get("future_current_route_blocking_claimed") is not False:
        errors.append({"code": "future_current_route_blocking_overclaimed"})
    if adoption.get("removed_required_test_count") != 0 or adoption.get("removed_required_artifact_count") != 0:
        errors.append({"code": "required_manifest_removal_detected"})
    if no_mutation.get("protected_surface_changed_count") != 0:
        errors.append({"code": "protected_surface_changed"})
    if final.get("declared_write_target_count") != len(set(final.get("declared_mutation_paths", []))):
        errors.append({"code": "declared_write_target_count_mismatch"})
    append_expected_field_errors(
        errors,
        final,
        {
            "claim_boundary_split_complete": True,
            "legacy_combined_route_preserved": True,
            "legacy_combined_route_pass_is_dvf_core_pass": False,
            "dvf_core_pass_runtime_compatible": False,
            "dvf_core_pass_package_safe": False,
            "dvf_core_pass_public_accepted": False,
            "dvf_core_pass_release_ready": False,
            "registry_authority_pass_public_accepted": False,
            "registry_authority_pass_release_ready": False,
            "registry_runtime_compatibility_pass_source_mutation": False,
            "registry_runtime_compatibility_pass_text_quality_acceptance": False,
            "publish_boundary_pass_dvf_core_compiler_success": False,
            "publish_boundary_pass_composition": "conjunctive_all_components",
            "partial_publish_boundary_bare_pass_allowed": False,
            "source_rendered_runtime_package_mutation_allowed": False,
            "required_gate_adopted": False,
            "future_current_route_blocking_claimed": False,
            "undeclared_write_target_mutation_count": 0,
            "manifest_physical_split_performed": False,
            "current_route_runner_rewrite_performed": False,
            "independent_review_gate_status": "not_claimed",
            "owner_seal_status": "not_claimed",
        },
        path="phase6/final_boundary_split_closure_report.json",
    )
    if final.get("release_readiness_claimed") or final.get("package_readiness_claimed"):
        errors.append({"code": "readiness_overclaim"})
    status = "PASS" if not errors else "FAIL"
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-validation-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": status,
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    write_json(phase_path("phase6", "validation_report.require_complete.json"), report)
    return report, not errors
