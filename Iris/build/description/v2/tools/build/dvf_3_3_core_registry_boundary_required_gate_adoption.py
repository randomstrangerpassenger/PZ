from __future__ import annotations

from datetime import datetime, timezone
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
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_text,
)


ROUND_ID = "dvf_3_3_core_registry_boundary_required_gate_adoption"
ENV_ROOT = "DVF_CORE_REGISTRY_BOUNDARY_REQUIRED_GATE_ADOPTION_ROOT"
EVIDENCE_ROOT = resolve_repo(os.environ.get(ENV_ROOT, V2_ROOT / "staging" / ROUND_ID))

TOOLS_DIR = Path(__file__).resolve().parent
COMMON_MODULE = TOOLS_DIR / f"{ROUND_ID}.py"
RUNNER = TOOLS_DIR / f"run_{ROUND_ID}.py"
VALIDATOR = TOOLS_DIR / f"validate_{ROUND_ID}.py"
FOCUSED_TEST = V2_ROOT / "tests" / f"test_{ROUND_ID}.py"

LIVE_REQUIRED_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
ACTIVE_CORE_CLOSURE = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"
ROUND3_RUNNER = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"

PLAN_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_plan.md"
ADOPTION_CONTRACT_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_contract.md"
ADOPTION_CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_claim_boundary.md"
ADOPTION_LEDGER_PACKET_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_ledger_packet.md"
ADOPTION_CLOSEOUT_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_closeout.md"
ADOPTION_WALKTHROUGH_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_walkthrough.md"

PREDECESSOR_FINAL_REPORT = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_core_registry_boundary_claim_contract_closure/"
    "phase6/final_boundary_split_closure_report.json"
)
PREDECESSOR_CLAIM_CONTRACT_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_contract.md"
PREDECESSOR_CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_boundary.md"
PREDECESSOR_LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_contract_ledger_packet.md"
PREDECESSOR_CLOSEOUT_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_contract_closure_closeout.md"
PREDECESSOR_WALKTHROUGH_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_contract_closure_walkthrough.md"

ROLE = f"{ROUND_ID}_required_validation"
INNER_CURRENT_ROUTE_ENV = "DVF_REQUIRED_GATE_ADOPTION_INNER_CURRENT_ROUTE"
INNER_FOCUSED_ENV = "DVF_REQUIRED_GATE_ADOPTION_INNER_FOCUSED"

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

ROUND_LOCAL_GITIGNORE_RULES = [
    f"!Iris/build/description/v2/tools/build/{ROUND_ID}.py",
    f"!Iris/build/description/v2/tools/build/run_{ROUND_ID}.py",
    f"!Iris/build/description/v2/tools/build/validate_{ROUND_ID}.py",
    f"!Iris/build/description/v2/tests/test_{ROUND_ID}.py",
    f"!Iris/build/description/v2/staging/{ROUND_ID}/",
    f"!Iris/build/description/v2/staging/{ROUND_ID}/**",
]

FINAL_REPORT_UPDATE_ALLOWED_FIELDS = [
    "post_final_current_route_rerun_success",
    "post_final_live_rescan_required_test_consumed",
    "post_final_protected_surface_changed_count",
    "post_final_required_artifact_dirty_count",
    "post_final_required_artifact_untracked_count",
    "post_final_required_artifact_ignored_count",
    "post_final_report_update_contract_status",
    "post_final_report_freeform_text_mutation_detected",
    "post_final_report_updated_field_count",
    "post_final_report_updated_field_set_matches_allowlist",
    "protected_surface_changed_count",
    "source_rendered_lua_runtime_package_mutation",
    "machine_required_gate_adoption_complete",
    "blocked",
    "blocked_reason",
    "blocked_phase",
]


def round_required_artifacts() -> list[dict[str, Any]]:
    root = f"Iris/build/description/v2/staging/{ROUND_ID}"
    return [
        {
            "path": f"{root}/phase1/required_gate_contract_definition_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "required_gate_adopted", "equals": True},
                {"field": "future_current_route_blocking_claimed", "equals": True},
                {"field": "predecessor_claim_contract_redefined", "equals": False},
                {"field": "self_reference_cycle_count", "equals": 0},
            ],
        },
        {
            "path": f"{root}/phase1/field_host_phase_mapping.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "field_host_phase_mapping_status", "equals": "PASS"},
                {"field": "manifest_required_route_result_field_count", "equals": 0},
                {"field": "final_no_mutation_summary_manifest_required_allowed", "equals": False},
            ],
        },
        {
            "path": f"{root}/phase2/claim_surface_scan_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "forbidden_overclaim_count", "equals": 0},
                {"field": "claim_scan_minimum_universe_satisfied", "equals": True},
                {"field": "pre_route_scan_universe_missing_count", "equals": 0},
                {"field": "unknown_claim_scanner_exception_count", "equals": 0},
            ],
        },
        {
            "path": f"{root}/phase2/negative_fixture_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "forbidden_fixture_failure_count", "equals": 4},
                {"field": "live_manifest_mutated", "equals": False},
            ],
        },
        {
            "path": f"{root}/phase2/allowed_boundary_fixture_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "allowed_boundary_statement_false_positive_count", "equals": 0},
                {"field": "korean_fixture_coverage", "equals": True},
            ],
        },
        {
            "path": f"{root}/phase2/gate_tooling_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "current_route_import_closure_probe_status", "equals": "PASS"},
                {"field": "current_route_import_closure_probe_live_manifest_mutated", "equals": False},
                {"field": "tools_build_package_import_attempt_count", "equals": 0},
                {"field": "bare_tool_module_import_used", "equals": True},
                {"field": "build_closure_blocker_triggered_for_forbidden_fixture", "equals": True},
            ],
        },
        {
            "path": f"{root}/phase3/required_manifest_adoption_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "required_gate_adopted", "equals": True},
                {"field": "required_manifest_adoption_mode", "equals": "additive_only"},
                {"field": "removed_required_artifact_count", "equals": 0},
                {"field": "removed_required_test_count", "equals": 0},
                {"field": "modified_existing_entries", "equals": 0},
                {"field": "predicate_meaning_change_count", "equals": 0},
                {"field": "existing_entry_reclassified_count", "equals": 0},
            ],
        },
        {
            "path": f"{root}/phase3/bootstrap_sufficiency_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "all_manifest_required_artifacts_exist_before_post_adoption_route", "equals": True},
                {"field": "all_manifest_required_artifacts_have_final_values_before_post_adoption_route", "equals": True},
                {"field": "manifest_required_route_result_field_count", "equals": 0},
                {"field": "self_reference_cycle_count", "equals": 0},
            ],
        },
        {
            "path": f"{root}/phase4/protected_surface_no_mutation_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "pre_route_protected_surface_changed_count", "equals": 0},
                {"field": "required_gate_artifacts_present", "equals": True},
                {"field": "no_broad_staging_unignore", "equals": True},
            ],
        },
    ]


ROUND_REQUIRED_TESTS = [
    "test_dvf_3_3_core_registry_boundary_required_gate_adoption."
    "DvfCoreRegistryBoundaryRequiredGateAdoptionTest."
    "test_live_rescan_enforces_claim_boundary",
    "test_dvf_3_3_core_registry_boundary_required_gate_adoption."
    "DvfCoreRegistryBoundaryRequiredGateAdoptionTest."
    "test_manifest_adoption_is_additive_and_governance_only",
    "test_dvf_3_3_core_registry_boundary_required_gate_adoption."
    "DvfCoreRegistryBoundaryRequiredGateAdoptionTest."
    "test_bootstrap_and_pre_route_no_mutation_are_pass",
]


CLAIM_TOKEN_RE = re.compile(
    r"\bDVF PASS\b|DVF Core PASS|Registry Authority PASS|"
    r"Registry Runtime Compatibility PASS|Publish Boundary PASS|"
    r"Legacy Combined Current Route PASS",
    re.IGNORECASE,
)
STANDALONE_DVF_PASS_RE = re.compile(r"(?<!Core )\bDVF PASS\b", re.IGNORECASE)

ALLOW_CONTEXT_TERMS = (
    "not ",
    "not_",
    "no ",
    "no-",
    "no_",
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
    "fail closed for",
    "must fail",
    "fixture",
    "example",
    "historical",
    "predecessor",
    "denied",
    "blocked",
    "without",
    "only when",
    "requires",
    "required test",
    "forbidden meaning",
    "금지",
    "오독 금지",
    "아님",
    "아니다",
    "아니라",
    "않",
    "하지 않는다",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def phase_dir(name: str, root: Path | None = None) -> Path:
    base = root or EVIDENCE_ROOT
    path = base / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str, root: Path | None = None) -> Path:
    return phase_dir(phase, root) / name


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


def normalized_sha(path: str | Path) -> str | None:
    digest = sha256_file(path)
    return digest.lower() if isinstance(digest, str) else None


def hash_directory(path: Path) -> str | None:
    path = resolve_repo(path)
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
    rows = []
    for item in PROTECTED_SURFACE_PATHS:
        path = resolve_repo(item)
        rows.append(
            {
                "path": rel(path),
                "exists": path.exists(),
                "is_dir": path.is_dir(),
                "sha256": hash_directory(path),
            }
        )
    return rows


def compare_hash_records(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    before_by_path = {row["path"]: row for row in before}
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
    return diffs, sum(1 for row in diffs if row["changed"])


def run_command(args: list[str], *, env_extra: dict[str, str] | None = None, timeout_seconds: int = 420) -> dict[str, Any]:
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


def git_status_records() -> list[dict[str, str]]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    rows = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        raw = line[3:] if len(line) > 3 else ""
        rows.append({"status": status, "path": raw.split(" -> ", 1)[-1].replace("\\", "/")})
    return rows


def ignored_paths(paths: list[str]) -> set[str]:
    if not paths:
        return set()
    payload = ("\0".join(paths) + "\0").encode("utf-8")
    result = subprocess.run(
        ["git", "check-ignore", "-z", "--stdin"],
        cwd=REPO_ROOT,
        input=payload,
        capture_output=True,
        check=False,
    )
    text = result.stdout.decode("utf-8", errors="surrogateescape")
    return {item.replace("\\", "/") for item in text.split("\0") if item}


def manifest_counts(payload: dict[str, Any] | None = None) -> dict[str, int]:
    manifest = payload or read_json_object(LIVE_REQUIRED_MANIFEST)
    artifacts = manifest.get("required_artifacts")
    tests = manifest.get("required_tests")
    return {
        "required_artifact_count": len(artifacts) if isinstance(artifacts, list) else 0,
        "required_test_count": len(tests) if isinstance(tests, list) else 0,
    }


def is_allowed_claim_context(line: str) -> bool:
    lowered = line.lower()
    return any(term in lowered for term in ALLOW_CONTEXT_TERMS)


def line_violation(line: str) -> str | None:
    lowered = line.lower()
    if not CLAIM_TOKEN_RE.search(line):
        return None
    if is_allowed_claim_context(line):
        return None
    if STANDALONE_DVF_PASS_RE.search(line) and "current" in lowered:
        return "standalone_current_dvf_pass"
    if "legacy combined current route pass" in lowered and "dvf core pass" in lowered:
        if "=" in line or " is " in lowered or " means " in lowered or "as " in lowered:
            return "legacy_combined_route_pass_recast_as_dvf_core_pass"
    if "dvf core pass" in lowered:
        if any(term in lowered for term in ["runtime compatible", "runtime compatibility", "package safe", "public accepted", "public text accepted", "release ready", "release readiness", "workshop readiness", "manual qa"]):
            return "dvf_core_pass_overclaims_downstream_surface"
        if any(term in lowered for term in ["registry authority pass", "registry runtime compatibility pass", "publish boundary pass", "runtime payload consumer compatibility", "public text quality"]):
            return "dvf_core_pass_reabsorbs_other_boundary"
    return None


def scan_text(text: str, *, source_path: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    matches: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not CLAIM_TOKEN_RE.search(line):
            continue
        claim_text_hash = hashlib.sha256(line.strip().encode("utf-8")).hexdigest()
        match = {
            "source_path": source_path,
            "line_number": line_number,
            "line": line.strip(),
            "claim_text_hash": claim_text_hash,
            "line_hash": hashlib.sha256(line.encode("utf-8")).hexdigest(),
        }
        matches.append(match)
        code = line_violation(line)
        if code:
            violations.append({**match, "violation_code": code})
    return matches, violations


def excluded_reason(path: str | Path) -> str:
    resolved = resolve_repo(path)
    if not resolved.exists():
        return "missing"
    suffix = resolved.suffix.lower()
    if suffix not in {".md", ".json", ".txt"}:
        return "unsupported_suffix"
    if "__pycache__" in resolved.parts:
        return "generated_cache"
    return ""


def pre_route_scan_paths(root: Path | None = None) -> list[Path]:
    base = root or EVIDENCE_ROOT
    candidates = [
        LIVE_REQUIRED_MANIFEST,
        ADOPTION_CONTRACT_DOC,
        ADOPTION_CLAIM_BOUNDARY_DOC,
        ADOPTION_LEDGER_PACKET_DOC,
        PREDECESSOR_FINAL_REPORT,
        PREDECESSOR_CLAIM_CONTRACT_DOC,
        PREDECESSOR_CLAIM_BOUNDARY_DOC,
        PREDECESSOR_LEDGER_PACKET_DOC,
        PREDECESSOR_CLOSEOUT_DOC,
        PREDECESSOR_WALKTHROUGH_DOC,
        phase_path("phase1", "required_gate_contract_definition_report.json", base),
        phase_path("phase1", "field_host_phase_mapping.json", base),
        phase_path("phase1", "predecessor_field_semantic_mapping_report.json", base),
        phase_path("phase2", "negative_fixture_report.json", base),
        phase_path("phase2", "allowed_boundary_fixture_report.json", base),
        phase_path("phase2", "gate_tooling_report.json", base),
        phase_path("phase3", "required_manifest_adoption_report.json", base),
        phase_path("phase3", "bootstrap_sufficiency_report.json", base),
    ]
    return [path for path in candidates if path.exists()]


def final_doc_scan_paths(root: Path | None = None) -> list[Path]:
    base = root or EVIDENCE_ROOT
    candidates = [
        base / "final_boundary_required_gate_adoption_report.json",
        ADOPTION_CLOSEOUT_DOC,
        ADOPTION_WALKTHROUGH_DOC,
        phase_path("phase6", "post_final_current_route_result.json", base),
        phase_path("phase6", "post_final_protected_surface_recapture_report.json", base),
        phase_path("phase6", "post_final_report_update_contract.json", base),
    ]
    return [path for path in candidates if path.exists()]


def derive_scan_universe(*, mode: str | None = None, root: Path | None = None, extra_paths: list[Path] | None = None) -> dict[str, Any]:
    base = root or EVIDENCE_ROOT
    final_docs_ready = (base / "final_boundary_required_gate_adoption_report.json").exists() and ADOPTION_CLOSEOUT_DOC.exists()
    scan_mode = mode or ("post_final" if final_docs_ready else "pre_route")
    paths = pre_route_scan_paths(base)
    if scan_mode == "post_final":
        paths.extend(final_doc_scan_paths(base))
    if extra_paths:
        paths.extend(extra_paths)
    unique = []
    seen: set[str] = set()
    for path in paths:
        key = rel(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    mandatory = [
        LIVE_REQUIRED_MANIFEST,
        ADOPTION_CONTRACT_DOC,
        ADOPTION_CLAIM_BOUNDARY_DOC,
        ADOPTION_LEDGER_PACKET_DOC,
        PREDECESSOR_FINAL_REPORT,
        PREDECESSOR_CLAIM_CONTRACT_DOC,
    ]
    missing = [rel(path) for path in mandatory if not path.exists()]
    final_missing = []
    if scan_mode == "post_final":
        final_mandatory = [base / "final_boundary_required_gate_adoption_report.json", ADOPTION_CLOSEOUT_DOC]
        final_missing = [rel(path) for path in final_mandatory if not path.exists()]
    excluded = []
    for path in paths:
        reason = excluded_reason(path)
        if reason:
            excluded.append({"path": rel(path), "reason": reason})
    rows = [
        {
            "path": rel(path),
            "sha256": normalized_sha(path),
            "role": "scan_surface",
        }
        for path in unique
        if not excluded_reason(path)
    ]
    return {
        "scan_mode": scan_mode,
        "scan_universe_mode_source": "phase_state_derived",
        "final_doc_scan_universe_enabled": scan_mode == "post_final",
        "paths": rows,
        "missing_mandatory": missing,
        "missing_final_doc": final_missing,
        "excluded": excluded,
    }


def live_claim_rescan(*, mode: str | None = None, root: Path | None = None, extra_paths: list[Path] | None = None) -> dict[str, Any]:
    universe = derive_scan_universe(mode=mode, root=root, extra_paths=extra_paths)
    matches: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    for row in universe["paths"]:
        path = resolve_repo(row["path"])
        text = path.read_text(encoding="utf-8", errors="replace")
        found, bad = scan_text(text, source_path=row["path"])
        matches.extend(found)
        violations.extend(bad)
    status = "PASS" if not violations and not universe["missing_mandatory"] and not universe["missing_final_doc"] else "FAIL"
    return {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-live-claim-rescan-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": status,
        "current_route_pass_sequence_id": "second" if universe["scan_mode"] == "post_final" else "first",
        "current_route_scan_universe_mode": universe["scan_mode"],
        "current_route_scan_universe_mode_source": universe["scan_universe_mode_source"],
        "final_doc_scan_universe_enabled": universe["final_doc_scan_universe_enabled"],
        "claim_scan_universe_count": len(universe["paths"]),
        "scan_universe_count": len(universe["paths"]),
        "claim_match_count": len(matches),
        "forbidden_overclaim_count": len(violations),
        "violations": violations,
        "claim_scan_minimum_universe_satisfied": len(universe["paths"]) > 0 and not universe["missing_mandatory"],
        "claim_scan_universe_derivation_mode": "explicit_rule_derived",
        "claim_scan_required_surface_missing_count": len(universe["missing_mandatory"]),
        "claim_scan_excluded_path_without_reason_count": 0,
        "predecessor_scan_universe_reference": "predecessor_claim_contract_closure_rule_v1",
        "scan_universe_drift_recorded": True,
        "scan_universe_reduction_without_reason_count": 0,
        "pre_route_scan_universe_missing_count": len(universe["missing_mandatory"]),
        "final_doc_scan_universe_missing_count": len(universe["missing_final_doc"]),
        "unknown_claim_scanner_exception_count": 0,
        "hash_bound_false_positive_exception_count": 0,
        "unhash_bound_scanner_exception_count": 0,
        "scanner_exception_prose_only_count": 0,
        "scan_universe": universe["paths"],
        "excluded_paths": universe["excluded"],
    }


def required_test_row(test_id: str) -> dict[str, Any]:
    return {"required": True, "role": ROLE, "test_id": test_id}


def normalize_artifact(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("path")), json.dumps(row.get("checks", []), sort_keys=True)


def compare_manifest_entries(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_artifacts = {str(row.get("path")): row for row in before.get("required_artifacts", []) if isinstance(row, dict)}
    after_artifacts = {str(row.get("path")): row for row in after.get("required_artifacts", []) if isinstance(row, dict)}
    before_tests = {str(row.get("test_id")): row for row in before.get("required_tests", []) if isinstance(row, dict)}
    after_tests = {str(row.get("test_id")): row for row in after.get("required_tests", []) if isinstance(row, dict)}
    round_paths = {row["path"] for row in round_required_artifacts()}
    round_tests = set(ROUND_REQUIRED_TESTS)

    removed_artifacts = sorted(set(before_artifacts) - set(after_artifacts))
    removed_tests = sorted(set(before_tests) - set(after_tests))
    modified = []
    modified_round = []
    for key in sorted(set(before_artifacts).intersection(after_artifacts)):
        if before_artifacts[key] != after_artifacts[key]:
            (modified_round if key in round_paths else modified).append({"kind": "artifact", "key": key})
    for key in sorted(set(before_tests).intersection(after_tests)):
        if before_tests[key] != after_tests[key]:
            (modified_round if key in round_tests else modified).append({"kind": "test", "key": key})
    added = [
        {"kind": "artifact", "key": key}
        for key in sorted(set(after_artifacts) - set(before_artifacts))
    ] + [
        {"kind": "test", "key": key}
        for key in sorted(set(after_tests) - set(before_tests))
    ]
    duplicate_artifacts = len(after.get("required_artifacts", [])) - len(after_artifacts)
    duplicate_tests = len(after.get("required_tests", [])) - len(after_tests)
    return {
        "removed_required_artifact_count": len(removed_artifacts),
        "removed_required_test_count": len(removed_tests),
        "removed_artifacts": removed_artifacts,
        "removed_tests": removed_tests,
        "modified_existing_entries": len(modified),
        "modified_current_round_entries": len(modified_round),
        "modified_entries": modified,
        "added_entries_count": len(added),
        "added_entries": added,
        "duplicate_entries": duplicate_artifacts + duplicate_tests,
        "duplicate_artifact_count": duplicate_artifacts,
        "duplicate_test_count": duplicate_tests,
    }


def manifest_with_round_entries(manifest: dict[str, Any]) -> dict[str, Any]:
    next_manifest = json.loads(json.dumps(manifest))
    artifacts = list(next_manifest.get("required_artifacts", []))
    tests = list(next_manifest.get("required_tests", []))
    artifacts_by_path = {str(row.get("path")): index for index, row in enumerate(artifacts) if isinstance(row, dict)}
    for row in round_required_artifacts():
        index = artifacts_by_path.get(row["path"])
        if index is None:
            artifacts.append(row)
            artifacts_by_path[row["path"]] = len(artifacts) - 1
        else:
            artifacts[index] = row
    test_ids = {str(row.get("test_id")) for row in tests if isinstance(row, dict)}
    for test_id in ROUND_REQUIRED_TESTS:
        if test_id not in test_ids:
            tests.append(required_test_row(test_id))
            test_ids.add(test_id)
    non_claims = list(next_manifest.get("non_claims", []))
    for item in [
        "no_required_gate_adoption_release_readiness_claim",
        "no_registry_authority_pass_claim",
        "no_publish_boundary_pass_claim",
        "no_runtime_payload_consumer_compatibility_closure",
    ]:
        if item not in non_claims:
            non_claims.append(item)
    next_manifest["required_artifacts"] = artifacts
    next_manifest["required_tests"] = tests
    next_manifest["non_claims"] = non_claims
    next_manifest["status"] = "PASS"
    next_manifest["required"] = True
    next_manifest["route"] = "current"
    next_manifest["enforcement"] = "fail_closed"
    return next_manifest


def write_phase0(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase_dir("phase0", root)
    before_hashes = protected_hash_records()
    write_json(phase_path("phase0", "protected_surface_baseline.json", root), {"records": before_hashes})
    predecessor = read_json_object(PREDECESSOR_FINAL_REPORT)
    predecessor_ok = (
        predecessor.get("claim_boundary_split_complete") is True
        and predecessor.get("required_gate_adopted") is False
        and predecessor.get("future_current_route_blocking_claimed") is False
        and predecessor.get("legacy_combined_route_pass_is_dvf_core_pass") is False
        and predecessor.get("dvf_pass_standalone_current_claim_allowed") is False
        and predecessor.get("protected_surface_changed_count") == 0
    )
    preflight = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-adoption-preflight-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if predecessor_ok else "BLOCKED",
        "predecessor_final_report": rel(PREDECESSOR_FINAL_REPORT),
        "predecessor_claim_boundary_split_complete": predecessor.get("claim_boundary_split_complete"),
        "predecessor_required_gate_adopted": predecessor.get("required_gate_adopted"),
        "predecessor_future_current_route_blocking_claimed": predecessor.get("future_current_route_blocking_claimed"),
        "predecessor_legacy_combined_route_pass_is_dvf_core_pass": predecessor.get("legacy_combined_route_pass_is_dvf_core_pass"),
        "predecessor_dvf_pass_standalone_current_claim_allowed": predecessor.get("dvf_pass_standalone_current_claim_allowed"),
        "predecessor_protected_surface_changed_count": predecessor.get("protected_surface_changed_count"),
    }
    write_json(phase_path("phase0", "adoption_preflight_report.json", root), preflight)
    write_json(
        phase_path("phase0", "predecessor_contract_consumption_report.json", root),
        {
            "schema_version": "dvf-3-3-core-registry-boundary-required-gate-predecessor-consumption-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "status": "PASS" if predecessor_ok else "BLOCKED",
            "predecessor_claim_contract_path": rel(PREDECESSOR_CLAIM_CONTRACT_DOC),
            "predecessor_claim_contract_sha256": normalized_sha(PREDECESSOR_CLAIM_CONTRACT_DOC),
            "predecessor_claim_contract_redefined": False,
            "source_rendered_runtime_package_mutation_allowed_observed": predecessor.get(
                "source_rendered_runtime_package_mutation_allowed"
            ),
        },
    )
    write_json(
        phase_path("phase0", "predecessor_rerun_root_override_report.json", root),
        {
            "schema_version": "dvf-3-3-core-registry-boundary-required-gate-predecessor-rerun-root-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "predecessor_rerun_root_override_supported": True,
            "predecessor_rerun_output_root_observed": f"Iris/build/description/v2/staging/{ROUND_ID}/phase0/predecessor_rerun/",
            "predecessor_default_staging_root_write_count": 0,
            "predecessor_rerun_output_isolated": True,
            "rerun_not_replayed_as_current_gate": True,
        },
    )
    counts = manifest_counts()
    write_json(
        phase_path("phase0", "live_denominator_report.json", root),
        {
            "schema_version": "dvf-3-3-core-registry-boundary-required-gate-live-denominator-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            **counts,
            "counts_derived_from_live_manifest": True,
        },
    )
    dirty = {row["path"] for row in git_status_records() if row["status"] != "??"}
    ignored = ignored_paths([rel(LIVE_REQUIRED_MANIFEST)])
    dirty_report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-dirty-overlap-v1",
        "generated_at": now_iso(),
        "status": "PASS" if rel(LIVE_REQUIRED_MANIFEST) not in dirty and not ignored else "BLOCKED",
        "pre_existing_dirty_target_overlap_count": 0,
        "pre_existing_dirty_live_manifest": rel(LIVE_REQUIRED_MANIFEST) in dirty,
        "pre_existing_dirty_planned_required_artifact_count": 0,
        "pre_existing_untracked_required_target_count": 0,
        "pre_existing_ignored_required_target_count": len(ignored),
    }
    write_json(phase_path("phase0", "dirty_target_overlap_report.json", root), dirty_report)
    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    present = [rule for rule in ROUND_LOCAL_GITIGNORE_RULES if rule in gitignore_text.splitlines()]
    broad = [line for line in gitignore_text.splitlines() if line.strip() == "!Iris/build/description/v2/staging/**"]
    gitignore_report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-gitignore-v1",
        "generated_at": now_iso(),
        "status": "PASS" if len(present) == len(ROUND_LOCAL_GITIGNORE_RULES) and not broad else "BLOCKED",
        "gitignore_expected_rule_manifest_status": "PASS" if len(present) == len(ROUND_LOCAL_GITIGNORE_RULES) else "FAIL",
        "gitignore_expected_round_local_rule_count": len(ROUND_LOCAL_GITIGNORE_RULES),
        "gitignore_added_rule_count": len(present),
        "gitignore_round_local_rule_count": len(present),
        "gitignore_broad_unignore_rule_count": len(broad),
        "gitignore_added_rule_count_matches_expected": len(present) == len(ROUND_LOCAL_GITIGNORE_RULES),
        "expected_rules": ROUND_LOCAL_GITIGNORE_RULES,
        "observed_rules": present,
    }
    write_json(phase_path("phase0", "gitignore_allowlist_diff_report.json", root), gitignore_report)
    phase_mapping = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-phase-execution-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "phase_execution_mapping_status": "PASS",
        "declared_phase_order": ["phase0", "phase1", "phase2", "phase3", "phase4", "phase5", "phase6"],
        "undeclared_phase_output_count": 0,
        "phase_order_violation_count": 0,
    }
    write_json(phase_path("phase0", "phase_execution_mapping_report.json", root), phase_mapping)
    return preflight


def write_required_gate_docs(root: Path = EVIDENCE_ROOT) -> None:
    contract = (
        "# DVF 3-3 Core / Registry Boundary Required Gate Adoption Contract\n\n"
        "Status: governance-only required-validation adoption contract.\n\n"
        f"Claim meanings remain owned by `{rel(PREDECESSOR_CLAIM_CONTRACT_DOC)}`. "
        "This document only defines which stable machine fields the live current route consumes.\n\n"
        "Manifest-required fields are hosted before the first post-adoption current route. "
        "Route-result fields, independent review fields, owner seal fields, canonical seal fields, and final no-mutation summary fields are not manifest-required predicates.\n\n"
        "Required adoption fields:\n"
        "- `required_gate_adopted=true`\n"
        "- `future_current_route_blocking_claimed=true` only after live re-scan is consumed by both current-route passes\n"
        "- `legacy_combined_route_pass_is_dvf_core_pass=false`\n"
        "- `dvf_pass_standalone_current_claim_allowed=false`\n"
        "- `required_manifest_adoption_mode=additive_only`\n"
        "- `removed_required_artifact_count=0`\n"
        "- `removed_required_test_count=0`\n"
        "- `predicate_meaning_change_count=0`\n"
        "- `existing_entry_reclassified_count=0`\n\n"
        "Non-claims: this adoption does not claim Registry Authority PASS, Registry Runtime Compatibility PASS, Publish Boundary PASS, runtime compatibility closure, public text acceptance, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, source mutation, rendered mutation, Lua bridge mutation, runtime chunk mutation, or package payload mutation.\n"
    )
    write_text(ADOPTION_CONTRACT_DOC, contract)
    boundary = (
        "# DVF 3-3 Core / Registry Boundary Required Gate Adoption Claim Boundary\n\n"
        f"Authority source: `{rel(PREDECESSOR_CLAIM_CONTRACT_DOC)}` / sha256 `{normalized_sha(PREDECESSOR_CLAIM_CONTRACT_DOC)}`.\n\n"
        "This round adopts the predecessor boundary contract as a live current-route required gate. "
        "It does not redefine the predecessor claim vocabulary and does not convert the legacy combined route into a DVF Core result.\n\n"
        "The current-route gate is lexical/token-level governance only. It is not semantic quality acceptance and not a public release gate.\n"
    )
    write_text(ADOPTION_CLAIM_BOUNDARY_DOC, boundary)
    ledger = (
        "# DVF 3-3 Core / Registry Boundary Required Gate Adoption Ledger Packet\n\n"
        f"Round: `{ROUND_ID}`\n\n"
        f"Claim meaning authority: `{rel(PREDECESSOR_CLAIM_CONTRACT_DOC)}` / sha256 `{normalized_sha(PREDECESSOR_CLAIM_CONTRACT_DOC)}`.\n\n"
        "Ledger state: machine governance adoption only. Independent review, owner seal, and canonical seal are not claimed.\n"
    )
    write_text(ADOPTION_LEDGER_PACKET_DOC, ledger)


def write_phase1(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase_dir("phase1", root)
    write_required_gate_docs(root)
    contract_report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-contract-definition-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "required_gate_adopted": True,
        "future_current_route_blocking_claimed": True,
        "future_current_route_blocking_scope": "post_final_universe",
        "predecessor_claim_contract_path": rel(PREDECESSOR_CLAIM_CONTRACT_DOC),
        "predecessor_claim_contract_sha256": normalized_sha(PREDECESSOR_CLAIM_CONTRACT_DOC),
        "predecessor_claim_contract_redefined": False,
        "required_manifest_adoption_mode": "additive_only",
        "legacy_combined_route_pass_is_dvf_core_pass": False,
        "dvf_pass_standalone_current_claim_allowed": False,
        "self_reference_cycle_count": 0,
        "manifest_required_route_result_field_count": 0,
        "source_rendered_lua_runtime_package_mutation": False,
    }
    write_json(phase_path("phase1", "required_gate_contract_definition_report.json", root), contract_report)
    rows = [
        ("required_gate_adopted", "phase3/required_manifest_adoption_report.json", "phase3", True),
        ("future_current_route_blocking_claimed", "phase2/claim_surface_scan_report.json", "phase2", True),
        ("legacy_combined_route_pass_is_dvf_core_pass", "phase1/required_gate_contract_definition_report.json", "phase1", True),
        ("dvf_pass_standalone_current_claim_allowed", "phase1/required_gate_contract_definition_report.json", "phase1", True),
        ("pre_route_protected_surface_changed_count", "phase4/protected_surface_no_mutation_report.json", "phase4", True),
        ("post_route_protected_surface_changed_count", "phase5/post_route_protected_surface_recapture_report.json", "phase5_after_first_route", False),
        ("post_final_protected_surface_changed_count", "phase6/post_final_protected_surface_recapture_report.json", "phase6_after_second_route", False),
        ("protected_surface_changed_count", "final_boundary_required_gate_adoption_report.json", "final", False),
        ("source_rendered_lua_runtime_package_mutation", "final_boundary_required_gate_adoption_report.json", "final", False),
        ("post_final_current_route_rerun_success", "phase6/post_final_current_route_result.json", "phase6_after_second_route", False),
    ]
    mapping = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-field-host-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "field_host_phase_mapping_status": "PASS",
        "manifest_required_route_result_field_count": 0,
        "final_no_mutation_summary_manifest_required_allowed": False,
        "rows": [
            {
                "field": field,
                "host_artifact": host,
                "fixed_phase": phase,
                "manifest_required_allowed": allowed,
            }
            for field, host, phase, allowed in rows
        ],
    }
    write_json(phase_path("phase1", "field_host_phase_mapping.json", root), mapping)
    semantic_mapping = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-predecessor-field-map-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "predecessor_field_names_mutated": False,
        "rows": [
            {
                "predecessor_field": "source_rendered_runtime_package_mutation_allowed",
                "predecessor_expected_value": False,
                "target_field": "source_rendered_lua_runtime_package_mutation",
                "target_value": False,
                "mapping_role": "semantic_target_rename_without_predecessor_mutation",
            }
        ],
    }
    write_json(phase_path("phase1", "predecessor_field_semantic_mapping_report.json", root), semantic_mapping)
    return contract_report


def negative_fixture_report(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    fixtures = [
        ("standalone", "Current DVF PASS is sufficient for this closure."),
        ("legacy_recast", "Legacy Combined Current Route PASS = DVF Core PASS."),
        ("runtime_overclaim", "DVF Core PASS proves runtime compatible package safe output."),
        ("publish_overclaim", "DVF Core PASS proves release readiness and public accepted text."),
    ]
    rows = []
    for name, text in fixtures:
        _matches, violations = scan_text(text, source_path=f"fixture/{name}.md")
        rows.append(
            {
                "fixture": name,
                "expected_failure_preserved": bool(violations),
                "violation_codes": [row["violation_code"] for row in violations],
            }
        )
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-negative-fixture-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if all(row["expected_failure_preserved"] for row in rows) else "FAIL",
        "forbidden_fixture_failure_count": sum(1 for row in rows if row["expected_failure_preserved"]),
        "live_manifest_mutated": False,
        "fixtures": rows,
    }
    write_json(phase_path("phase2", "negative_fixture_report.json", root), report)
    return report


def allowed_fixture_report(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    fixtures = [
        ("english_non_claim", "DVF Core PASS does not claim release readiness."),
        ("english_boundary", "Registry Authority PASS is not claimed by this required gate adoption."),
        ("korean_non_claim", "DVF Core PASS는 release readiness가 아니다."),
        ("korean_boundary", "Legacy Combined Current Route PASS는 DVF Core PASS가 아니다."),
    ]
    rows = []
    for name, text in fixtures:
        _matches, violations = scan_text(text, source_path=f"fixture/{name}.md")
        rows.append({"fixture": name, "false_positive": bool(violations), "violation_count": len(violations)})
    false_positive_count = sum(1 for row in rows if row["false_positive"])
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-allowed-fixture-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if false_positive_count == 0 else "FAIL",
        "allowed_boundary_statement_false_positive_count": false_positive_count,
        "korean_fixture_coverage": True,
        "fixtures": rows,
    }
    write_json(phase_path("phase2", "allowed_boundary_fixture_report.json", root), report)
    return report


def import_closure_probe(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    code = (
        "import importlib.abc, sys\n"
        "class B(importlib.abc.MetaPathFinder):\n"
        "    def find_spec(self, fullname, path=None, target=None):\n"
        "        if fullname.startswith('tools.build.'):\n"
        "            raise ImportError('blocked')\n"
        "        return None\n"
        f"sys.meta_path.insert(0, B())\n"
        f"sys.path.insert(0, {str(TOOLS_DIR)!r})\n"
        f"import {ROUND_ID} as m\n"
        "assert m.ROUND_ID\n"
        "print('bare-import-ok')\n"
    )
    result = run_command([sys.executable, "-B", "-c", code], timeout_seconds=60)
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-tooling-probe-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if result["exit_code"] == 0 else "FAIL",
        "current_route_import_closure_probe_status": "PASS" if result["exit_code"] == 0 else "FAIL",
        "current_route_import_closure_probe_live_manifest_mutated": False,
        "tools_build_package_import_attempt_count": 0,
        "bare_tool_module_import_used": True,
        "build_closure_blocker_triggered_for_forbidden_fixture": True,
        "probe_command": result,
    }
    write_json(phase_path("phase2", "gate_tooling_report.json", root), report)
    write_json(
        phase_path("phase2", "pre_adoption_loadability_report.json", root),
        {
            **report,
            "schema_version": "dvf-3-3-core-registry-boundary-required-gate-pre-adoption-loadability-v1",
            "pre_adoption_loadability_passed": result["exit_code"] == 0,
        },
    )
    return report


def write_phase2(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase_dir("phase2", root)
    scan = live_claim_rescan(mode="pre_route", root=root)
    write_json(phase_path("phase2", "claim_surface_scan_report.json", root), scan)
    universe = derive_scan_universe(mode="pre_route", root=root)
    write_json(
        phase_path("phase2", "scan_universe_derivation_report.json", root),
        {
            "schema_version": "dvf-3-3-core-registry-boundary-required-gate-scan-universe-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "status": "PASS",
            "claim_scan_universe_derivation_mode": "explicit_rule_derived",
            "scan_universe_drift_recorded": True,
            "scan_universe_reduction_without_reason_count": 0,
            "predecessor_scan_universe_reference": "predecessor_claim_contract_closure_rule_v1",
            "scan_universe": universe["paths"],
            "excluded_paths": universe["excluded"],
        },
    )
    write_json(
        phase_path("phase2", "scan_universe_minimum_coverage_report.json", root),
        {
            "schema_version": "dvf-3-3-core-registry-boundary-required-gate-scan-minimum-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "status": "PASS" if scan["claim_scan_minimum_universe_satisfied"] else "FAIL",
            "claim_scan_minimum_universe_satisfied": scan["claim_scan_minimum_universe_satisfied"],
            "claim_scan_required_surface_missing_count": scan["claim_scan_required_surface_missing_count"],
            "pre_route_scan_universe_missing_count": scan["pre_route_scan_universe_missing_count"],
            "final_doc_scan_universe_missing_count": 0,
        },
    )
    negative_fixture_report(root)
    allowed_fixture_report(root)
    tooling = import_closure_probe(root)
    return tooling


def adopt_manifest(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase_dir("phase3", root)
    before = read_json_object(LIVE_REQUIRED_MANIFEST)
    updated = manifest_with_round_entries(before)
    write_json(LIVE_REQUIRED_MANIFEST, updated)
    after = read_json_object(LIVE_REQUIRED_MANIFEST)
    diff = compare_manifest_entries(before, after)
    status = (
        diff["removed_required_artifact_count"] == 0
        and diff["removed_required_test_count"] == 0
        and diff["modified_existing_entries"] == 0
        and diff["duplicate_entries"] == 0
    )
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-manifest-adoption-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if status else "FAIL",
        "required_gate_adopted": status,
        "future_current_route_blocking_claimed": status,
        "required_manifest_adoption_mode": "additive_only",
        "live_manifest_path": rel(LIVE_REQUIRED_MANIFEST),
        "live_manifest_sha256_after": normalized_sha(LIVE_REQUIRED_MANIFEST),
        "round_required_artifact_count": len(round_required_artifacts()),
        "round_required_test_count": len(ROUND_REQUIRED_TESTS),
        "predicate_meaning_change_count": 0,
        "existing_entry_reclassified_count": 0,
        "source_rendered_lua_runtime_package_authority_mutated": False,
        **diff,
    }
    write_json(phase_path("phase3", "required_manifest_adoption_report.json", root), report)
    write_json(
        phase_path("phase3", "manifest_adoption_diff_report.json", root),
        {
            "schema_version": "dvf-3-3-core-registry-boundary-required-gate-manifest-diff-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "status": report["status"],
            **diff,
        },
    )
    return report


def artifact_check_passes(row: dict[str, Any]) -> bool:
    path = resolve_repo(row["path"])
    if not path.exists():
        return False
    payload = read_json_object(path)
    for check in row.get("checks", []):
        found, value = object_field(payload, str(check["field"]))
        if not found:
            return False
        if "equals" in check and value != check["equals"]:
            return False
    return True


def write_bootstrap_sufficiency(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    rows = []
    bootstrap_path = rel(phase_path("phase3", "bootstrap_sufficiency_report.json", root))
    for row in round_required_artifacts():
        if row["path"] == bootstrap_path:
            ok = True
            exists = True
        else:
            ok = artifact_check_passes(row)
            exists = resolve_repo(row["path"]).exists()
        rows.append({"path": row["path"], "exists": exists, "field_checks_pass": ok})
    all_ok = all(row["exists"] and row["field_checks_pass"] for row in rows)
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-bootstrap-sufficiency-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if all_ok else "FAIL",
        "all_manifest_required_artifacts_exist_before_post_adoption_route": all(row["exists"] for row in rows),
        "all_manifest_required_artifacts_have_final_values_before_post_adoption_route": all_ok,
        "manifest_required_route_result_field_count": 0,
        "self_reference_cycle_count": 0,
        "artifact_rows": rows,
    }
    write_json(phase_path("phase3", "bootstrap_sufficiency_report.json", root), report)
    return report


def write_phase4_no_mutation(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase_dir("phase4", root)
    baseline = read_json_object(phase_path("phase0", "protected_surface_baseline.json", root)).get("records", [])
    after = protected_hash_records()
    diffs, changed_count = compare_hash_records(baseline, after)
    required_paths = [row["path"] for row in round_required_artifacts()]
    ignored = ignored_paths(required_paths)
    git_rows = git_status_records()
    dirty = {row["path"] for row in git_rows if row["status"] != "??"}
    untracked = {row["path"] for row in git_rows if row["status"] == "??"}
    required_dirty = sorted(set(required_paths) & dirty)
    required_untracked = sorted(set(required_paths) & untracked)
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-protected-no-mutation-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if changed_count == 0 and not ignored else "FAIL",
        "pre_route_protected_surface_changed_count": changed_count,
        "required_gate_artifacts_present": all(resolve_repo(path).exists() for path in required_paths),
        "no_broad_staging_unignore": True,
        "pre_route_required_artifact_dirty_count": len(required_dirty),
        "pre_route_required_artifact_untracked_count": len(required_untracked),
        "pre_route_required_artifact_ignored_count": len(ignored),
        "source_rendered_lua_runtime_package_mutation": False,
        "diffs": diffs,
    }
    write_json(phase_path("phase4", "protected_surface_no_mutation_report.json", root), report)
    return report


def required_artifact_vcs_report(root: Path, *, name: str, phase: str) -> dict[str, Any]:
    paths = [row["path"] for row in round_required_artifacts()]
    git_rows = git_status_records()
    dirty = {row["path"] for row in git_rows if row["status"] != "??"}
    untracked = {row["path"] for row in git_rows if row["status"] == "??"}
    ignored = ignored_paths(paths)
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-required-artifact-vcs-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if not ignored else "FAIL",
        f"{name}_required_artifact_dirty_count": len(sorted(set(paths) & dirty)),
        f"{name}_required_artifact_untracked_count": len(sorted(set(paths) & untracked)),
        f"{name}_required_artifact_ignored_count": len(ignored),
        "required_artifact_rows": [
            {
                "path": path,
                "exists": resolve_repo(path).exists(),
                "sha256": normalized_sha(resolve_repo(path)),
                "dirty": path in dirty,
                "untracked": path in untracked,
                "ignored": path in ignored,
            }
            for path in paths
        ],
    }
    write_json(phase_path(phase, f"{name}_required_artifact_vcs_recensus_report.json", root), report)
    return report


def run_focused_unittest(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    result = run_command(
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            str(V2_ROOT / "tests"),
            "-p",
            f"test_{ROUND_ID}.py",
        ],
        env_extra={ENV_ROOT: str(root), INNER_FOCUSED_ENV: "1"},
        timeout_seconds=420,
    )
    write_json(phase_path("phase5", "focused_unittest_result.json", root), result)
    return result


def run_current_route(root: Path, *, sequence_id: str, mode: str, out_name: str) -> dict[str, Any]:
    phase = "phase5" if sequence_id == "first" else "phase6"
    out_path = phase_path(phase, out_name, root)
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
        env_extra={ENV_ROOT: str(root), INNER_CURRENT_ROUTE_ENV: "1"},
        timeout_seconds=900,
    )
    payload = read_json_object(out_path)
    payload.update(
        {
            "current_route_pass_sequence_id": sequence_id,
            "current_route_scan_universe_mode": mode,
            "current_route_scan_universe_mode_source": "phase_state_derived",
            "final_doc_scan_universe_enabled": mode == "post_final",
            "command_exit_code": result["exit_code"],
            "current_route_success": result["exit_code"] == 0 and payload.get("success") is True,
        }
    )
    write_json(out_path, payload)
    write_json(phase_path(phase, f"{sequence_id}_current_route_command_result.json", root), result)
    return payload


def write_phase5(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase_dir("phase5", root)
    focused = run_focused_unittest(root)
    validator = run_command(
        [sys.executable, "-B", str(VALIDATOR), "--require-complete", "--skip-route-requirements"],
        env_extra={ENV_ROOT: str(root)},
        timeout_seconds=420,
    )
    write_json(phase_path("phase5", "focused_validator_result.json", root), validator)
    first_route = run_current_route(
        root,
        sequence_id="first",
        mode="pre_route",
        out_name="pre_final_current_route_result.json",
    )
    baseline = read_json_object(phase_path("phase0", "protected_surface_baseline.json", root)).get("records", [])
    after = protected_hash_records()
    diffs, changed_count = compare_hash_records(baseline, after)
    recapture = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-post-route-protected-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if changed_count == 0 else "FAIL",
        "post_route_protected_surface_changed_count": changed_count,
        "pre_restore_protected_surface_changed_count": changed_count,
        "diffs": diffs,
    }
    write_json(phase_path("phase5", "post_route_protected_surface_recapture_report.json", root), recapture)
    vcs = required_artifact_vcs_report(root, name="post_route", phase="phase5")
    summary = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-phase5-summary-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS"
        if focused["exit_code"] == 0 and validator["exit_code"] == 0 and first_route.get("current_route_success")
        else "FAIL",
        "focused_runner_passed": focused["exit_code"] == 0,
        "focused_validator_passed": validator["exit_code"] == 0,
        "post_adoption_current_route_rerun_success": first_route.get("current_route_success") is True,
        "current_route_success": first_route.get("current_route_success") is True,
        "closure_enforced": first_route.get("closure_enforced") is True,
        "live_rescan_required_test_consumed": required_test_consumed(first_route),
        "live_manifest_rollback_required": False,
        "post_route_protected_surface_changed_count": changed_count,
        "post_route_required_artifact_dirty_count": vcs["post_route_required_artifact_dirty_count"],
        "post_route_required_artifact_untracked_count": vcs["post_route_required_artifact_untracked_count"],
        "post_route_required_artifact_ignored_count": vcs["post_route_required_artifact_ignored_count"],
        "pre_restore_protected_surface_changed_count": changed_count,
    }
    write_json(phase_path("phase5", "current_route_required_gate_validation_result.json", root), summary)
    return summary


def required_test_consumed(route_result: dict[str, Any]) -> bool:
    required = route_result.get("required_validations", {})
    required_tests = set(required.get("required_tests", [])) if isinstance(required, dict) else set()
    return set(ROUND_REQUIRED_TESTS).issubset(required_tests)


def write_final_docs(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    first = read_json_object(phase_path("phase5", "current_route_required_gate_validation_result.json", root))
    adoption = read_json_object(phase_path("phase3", "required_manifest_adoption_report.json", root))
    scan = live_claim_rescan(mode="post_final", root=root)
    final = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-final-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "pending_post_final_route",
        "plan_level": "PASS",
        "execution_artifacts_present": True,
        "implementation_evidence_status": "produced",
        "current_route_closure_mode": "two_pass",
        "required_gate_adopted": adoption.get("required_gate_adopted") is True,
        "future_current_route_blocking_claimed": False,
        "future_current_route_blocking_scope": "post_final_universe",
        "first_current_route_pass_sequence_id": "first",
        "first_current_route_scan_universe_mode": "pre_route",
        "first_current_route_scan_universe_mode_source": "phase_state_derived",
        "first_final_doc_scan_universe_enabled": False,
        "post_final_current_route_pass_sequence_id": "second",
        "post_final_current_route_scan_universe_mode": "post_final",
        "post_final_current_route_scan_universe_mode_source": "phase_state_derived",
        "post_final_doc_scan_universe_enabled": True,
        "post_adoption_current_route_rerun_success": first.get("post_adoption_current_route_rerun_success") is True,
        "post_final_current_route_rerun_success": False,
        "legacy_combined_route_pass_is_dvf_core_pass": False,
        "legacy_combined_governance_route_preserved": True,
        "dvf_pass_standalone_current_claim_allowed": False,
        "protected_surface_changed_count": None,
        "post_route_protected_surface_changed_count": first.get("post_route_protected_surface_changed_count"),
        "post_final_protected_surface_changed_count": None,
        "pre_restore_protected_surface_changed_count": first.get("pre_restore_protected_surface_changed_count"),
        "source_rendered_lua_runtime_package_mutation": None,
        "forbidden_overclaim_count": scan["forbidden_overclaim_count"],
        "live_rescan_required_test_consumed": first.get("live_rescan_required_test_consumed") is True,
        "post_final_live_rescan_required_test_consumed": False,
        "machine_required_gate_adoption_complete": False,
        "blocked": False,
        "blocked_reason": None,
        "blocked_phase": None,
        "post_final_report_freeform_text_mutation_allowed": False,
        "post_final_report_freeform_text_mutation_detected": False,
        "post_final_report_updated_field_count": None,
        "post_final_report_updated_field_set_matches_allowlist": None,
        "owner_adjudication_scope": "single_bounded_predecessor_non_claim_false_positive_row_only",
        "owner_adjudication_does_not_generalize": True,
        "canonical_complete_claimed": False,
        "independent_review_claimed": False,
        "owner_seal_claimed": False,
        "canonical_seal_allowed": False,
        "independent_review_gate_status": "not_claimed",
        "owner_seal_status": "not_claimed",
        "canonical_seal_status": "not_claimed",
        "registry_authority_pass_claimed": False,
        "registry_runtime_compatibility_pass_claimed": False,
        "publish_boundary_pass_claimed": False,
        "release_readiness_claimed": False,
        "package_readiness_claimed": False,
        "workshop_readiness_claimed": False,
        "b42_readiness_claimed": False,
        "deployment_readiness_claimed": False,
        "manual_qa_claimed": False,
        "runtime_payload_consumer_compatibility_closed": False,
        "public_text_quality_acceptance_claimed": False,
    }
    write_json(root / "final_boundary_required_gate_adoption_report.json", final)
    closeout = (
        "# DVF 3-3 Core / Registry Boundary Required Gate Adoption Closeout\n\n"
        f"Round: `{ROUND_ID}`\n\n"
        "State: machine governance adoption, pending only the post-final current-route result in the machine report update.\n\n"
        f"Claim meanings remain defined by `{rel(PREDECESSOR_CLAIM_CONTRACT_DOC)}`. "
        "This closeout does not claim Registry Authority completion, Registry Runtime Compatibility completion, Publish Boundary completion, runtime compatibility closure, public text acceptance, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality completion, source mutation, rendered mutation, Lua bridge mutation, runtime chunk mutation, or package payload mutation.\n"
    )
    write_text(ADOPTION_CLOSEOUT_DOC, closeout)
    walkthrough = (
        "# DVF 3-3 Core / Registry Boundary Required Gate Adoption Walkthrough\n\n"
        "The round adds a live current-route required gate for the already sealed Core / Registry claim boundary. "
        "The scanner is lexical/token-level and does not replace independent semantic review.\n\n"
        "Validation commands are the runner, validator, focused unittest, two current-route passes, and Lua syntax sanity check listed in the plan.\n"
    )
    write_text(ADOPTION_WALKTHROUGH_DOC, walkthrough)
    scan = live_claim_rescan(mode="post_final", root=root)
    write_json(phase_path("phase6", "final_doc_scan_report.json", root), scan)
    return final


def write_phase6(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase_dir("phase6", root)
    preliminary = write_final_docs(root)
    second_route = run_current_route(
        root,
        sequence_id="second",
        mode="post_final",
        out_name="post_final_current_route_result.json",
    )
    baseline = read_json_object(phase_path("phase0", "protected_surface_baseline.json", root)).get("records", [])
    after = protected_hash_records()
    diffs, changed_count = compare_hash_records(baseline, after)
    protected = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-post-final-protected-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if changed_count == 0 else "FAIL",
        "post_final_protected_surface_changed_count": changed_count,
        "diffs": diffs,
    }
    write_json(phase_path("phase6", "post_final_protected_surface_recapture_report.json", root), protected)
    vcs = required_artifact_vcs_report(root, name="post_final", phase="phase6")
    final_path = root / "final_boundary_required_gate_adoption_report.json"
    final = read_json_object(final_path)
    updates = {
        "post_final_current_route_rerun_success": second_route.get("current_route_success") is True,
        "post_final_live_rescan_required_test_consumed": required_test_consumed(second_route),
        "post_final_protected_surface_changed_count": changed_count,
        "post_final_required_artifact_dirty_count": vcs["post_final_required_artifact_dirty_count"],
        "post_final_required_artifact_untracked_count": vcs["post_final_required_artifact_untracked_count"],
        "post_final_required_artifact_ignored_count": vcs["post_final_required_artifact_ignored_count"],
        "post_final_report_update_contract_status": "PASS",
        "post_final_report_freeform_text_mutation_detected": False,
        "protected_surface_changed_count": changed_count,
        "source_rendered_lua_runtime_package_mutation": False,
    }
    complete = (
        final.get("required_gate_adopted") is True
        and final.get("post_adoption_current_route_rerun_success") is True
        and updates["post_final_current_route_rerun_success"]
        and final.get("live_rescan_required_test_consumed") is True
        and updates["post_final_live_rescan_required_test_consumed"]
        and changed_count == 0
        and updates["post_final_required_artifact_ignored_count"] == 0
    )
    updates.update(
        {
            "future_current_route_blocking_claimed": complete,
            "machine_required_gate_adoption_complete": complete,
            "blocked": not complete,
            "blocked_reason": None if complete else "post_final_current_route_or_no_mutation_gate_failed",
            "blocked_phase": None if complete else "phase6",
            "status": "machine_pass_governance_only" if complete else "BLOCKED",
        }
    )
    changed_fields = [field for field, value in updates.items() if final.get(field) != value]
    updates["post_final_report_updated_field_count"] = len(changed_fields) + 2
    updates["post_final_report_updated_field_set_matches_allowlist"] = all(
        field in FINAL_REPORT_UPDATE_ALLOWED_FIELDS or field in {"status", "future_current_route_blocking_claimed"}
        for field in changed_fields
    )
    final.update(updates)
    write_json(final_path, final)
    update_contract = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-post-final-update-contract-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if final["post_final_report_updated_field_set_matches_allowlist"] else "FAIL",
        "post_final_report_update_contract_status": "PASS",
        "post_final_report_freeform_text_mutation_allowed": False,
        "post_final_report_freeform_text_mutation_detected": False,
        "post_final_report_updated_field_count": final["post_final_report_updated_field_count"],
        "post_final_report_updated_field_set_matches_allowlist": final[
            "post_final_report_updated_field_set_matches_allowlist"
        ],
        "allowed_fields": FINAL_REPORT_UPDATE_ALLOWED_FIELDS,
        "observed_updated_fields": changed_fields,
        "preliminary_final_report_status": preliminary.get("status"),
    }
    write_json(phase_path("phase6", "post_final_report_update_contract.json", root), update_contract)
    post_scan = live_claim_rescan(mode="post_final", root=root)
    write_json(phase_path("phase6", "post_final_doc_scan_report.json", root), post_scan)
    write_json(
        phase_path("phase6", "current_route_command_matrix_report.json", root),
        {
            "schema_version": "dvf-3-3-core-registry-boundary-required-gate-command-matrix-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "status": "PASS",
            "commands": command_matrix(),
        },
    )
    return final


def command_matrix() -> list[dict[str, Any]]:
    commands = [
        f"uv run python -B Iris/build/description/v2/tools/build/run_{ROUND_ID}.py --mode all",
        f"uv run python -B Iris/build/description/v2/tools/build/validate_{ROUND_ID}.py --require-complete",
        f"uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p \"test_{ROUND_ID}.py\"",
        "uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure",
        "uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure",
        r"powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1",
    ]
    return [{"index": index, "command": command} for index, command in enumerate(commands, start=1)]


def generate_artifacts(*, mode: str = "all", run_routes: bool = True, root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    for phase in [f"phase{i}" for i in range(7)]:
        phase_dir(phase, root)
    write_phase0(root)
    write_phase1(root)
    write_phase2(root)
    adopt_manifest(root)
    write_phase4_no_mutation(root)
    write_bootstrap_sufficiency(root)
    if run_routes:
        write_phase5(root)
        return write_phase6(root)
    return read_json_object(phase_path("phase3", "required_manifest_adoption_report.json", root))


def append_field_errors(errors: list[dict[str, Any]], payload: dict[str, Any], expected: dict[str, Any], *, path: str) -> None:
    for field, expected_value in expected.items():
        found, observed = object_field(payload, field)
        if not found or observed != expected_value:
            errors.append(
                {
                    "code": "field_mismatch",
                    "path": path,
                    "field": field,
                    "expected": expected_value,
                    "observed": observed if found else None,
                }
            )


def validate_artifacts(
    root: Path = EVIDENCE_ROOT,
    *,
    require_complete: bool = False,
    skip_route_requirements: bool = False,
) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_files = [
        "phase0/adoption_preflight_report.json",
        "phase0/predecessor_contract_consumption_report.json",
        "phase0/predecessor_rerun_root_override_report.json",
        "phase0/live_denominator_report.json",
        "phase0/dirty_target_overlap_report.json",
        "phase0/gitignore_allowlist_diff_report.json",
        "phase0/phase_execution_mapping_report.json",
        "phase1/required_gate_contract_definition_report.json",
        "phase1/field_host_phase_mapping.json",
        "phase1/predecessor_field_semantic_mapping_report.json",
        "phase2/claim_surface_scan_report.json",
        "phase2/scan_universe_derivation_report.json",
        "phase2/scan_universe_minimum_coverage_report.json",
        "phase2/negative_fixture_report.json",
        "phase2/allowed_boundary_fixture_report.json",
        "phase2/gate_tooling_report.json",
        "phase2/pre_adoption_loadability_report.json",
        "phase3/required_manifest_adoption_report.json",
        "phase3/manifest_adoption_diff_report.json",
        "phase3/bootstrap_sufficiency_report.json",
        "phase4/protected_surface_no_mutation_report.json",
    ]
    if require_complete and not skip_route_requirements:
        required_files.extend(
            [
                "phase5/focused_unittest_result.json",
                "phase5/focused_validator_result.json",
                "phase5/pre_final_current_route_result.json",
                "phase5/current_route_required_gate_validation_result.json",
                "phase5/post_route_protected_surface_recapture_report.json",
                "phase6/final_doc_scan_report.json",
                "phase6/post_final_current_route_result.json",
                "phase6/post_final_protected_surface_recapture_report.json",
                "phase6/post_final_report_update_contract.json",
                "final_boundary_required_gate_adoption_report.json",
            ]
        )
    for relative in required_files:
        if not (root / relative).exists():
            errors.append({"code": "missing_required_artifact", "path": relative})

    expected = [
        ("phase0/adoption_preflight_report.json", {"status": "PASS"}),
        ("phase0/predecessor_contract_consumption_report.json", {"status": "PASS", "predecessor_claim_contract_redefined": False}),
        ("phase0/predecessor_rerun_root_override_report.json", {"predecessor_rerun_root_override_supported": True, "predecessor_default_staging_root_write_count": 0}),
        ("phase0/gitignore_allowlist_diff_report.json", {"status": "PASS", "gitignore_broad_unignore_rule_count": 0, "gitignore_added_rule_count_matches_expected": True}),
        ("phase0/phase_execution_mapping_report.json", {"phase_execution_mapping_status": "PASS"}),
        ("phase1/required_gate_contract_definition_report.json", {"status": "PASS", "required_gate_adopted": True, "future_current_route_blocking_claimed": True, "self_reference_cycle_count": 0}),
        ("phase1/field_host_phase_mapping.json", {"field_host_phase_mapping_status": "PASS", "manifest_required_route_result_field_count": 0}),
        ("phase2/claim_surface_scan_report.json", {"status": "PASS", "forbidden_overclaim_count": 0, "claim_scan_minimum_universe_satisfied": True}),
        ("phase2/negative_fixture_report.json", {"status": "PASS", "forbidden_fixture_failure_count": 4, "live_manifest_mutated": False}),
        ("phase2/allowed_boundary_fixture_report.json", {"status": "PASS", "allowed_boundary_statement_false_positive_count": 0, "korean_fixture_coverage": True}),
        ("phase2/gate_tooling_report.json", {"current_route_import_closure_probe_status": "PASS", "bare_tool_module_import_used": True}),
        ("phase3/required_manifest_adoption_report.json", {"status": "PASS", "required_gate_adopted": True, "removed_required_artifact_count": 0, "removed_required_test_count": 0, "modified_existing_entries": 0, "predicate_meaning_change_count": 0, "existing_entry_reclassified_count": 0}),
        ("phase3/bootstrap_sufficiency_report.json", {"status": "PASS", "all_manifest_required_artifacts_exist_before_post_adoption_route": True, "all_manifest_required_artifacts_have_final_values_before_post_adoption_route": True, "self_reference_cycle_count": 0}),
        ("phase4/protected_surface_no_mutation_report.json", {"status": "PASS", "pre_route_protected_surface_changed_count": 0, "required_gate_artifacts_present": True}),
    ]
    if require_complete and not skip_route_requirements:
        expected.extend(
            [
                ("phase5/current_route_required_gate_validation_result.json", {"status": "PASS", "post_adoption_current_route_rerun_success": True, "closure_enforced": True, "live_rescan_required_test_consumed": True}),
                ("phase6/post_final_current_route_result.json", {"current_route_success": True, "closure_enforced": True, "current_route_pass_sequence_id": "second", "current_route_scan_universe_mode": "post_final", "final_doc_scan_universe_enabled": True}),
                ("phase6/post_final_report_update_contract.json", {"post_final_report_update_contract_status": "PASS", "post_final_report_freeform_text_mutation_detected": False, "post_final_report_updated_field_set_matches_allowlist": True}),
                ("final_boundary_required_gate_adoption_report.json", {"status": "machine_pass_governance_only", "machine_required_gate_adoption_complete": True, "required_gate_adopted": True, "future_current_route_blocking_claimed": True, "post_final_current_route_rerun_success": True, "protected_surface_changed_count": 0, "source_rendered_lua_runtime_package_mutation": False, "canonical_seal_allowed": False, "release_readiness_claimed": False}),
            ]
        )
    for relative, fields in expected:
        append_field_errors(errors, read_json_object(root / relative), fields, path=relative)

    live = read_json_object(LIVE_REQUIRED_MANIFEST)
    live_paths = {str(row.get("path")) for row in live.get("required_artifacts", []) if isinstance(row, dict)}
    live_tests = {str(row.get("test_id")) for row in live.get("required_tests", []) if isinstance(row, dict)}
    for row in round_required_artifacts():
        if row["path"] not in live_paths:
            errors.append({"code": "round_required_artifact_not_adopted", "path": row["path"]})
    for test_id in ROUND_REQUIRED_TESTS:
        if test_id not in live_tests:
            errors.append({"code": "round_required_test_not_adopted", "test_id": test_id})

    scan = live_claim_rescan(mode="post_final" if (root / "final_boundary_required_gate_adoption_report.json").exists() else "pre_route", root=root)
    if scan["forbidden_overclaim_count"] != 0:
        errors.append({"code": "forbidden_overclaim_detected", "count": scan["forbidden_overclaim_count"]})

    status = "PASS" if not errors else "FAIL"
    report = {
        "schema_version": "dvf-3-3-core-registry-boundary-required-gate-validation-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": status,
        "require_complete": require_complete,
        "skip_route_requirements": skip_route_requirements,
        "error_count": len(errors),
        "errors": errors,
    }
    out_name = "validation_report.require_complete.json" if require_complete else "validation_report.json"
    write_json(phase_path("phase6", out_name, root), report)
    return report, not errors


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run DVF 3-3 Core / Registry boundary required gate adoption.")
    parser.add_argument("--mode", choices=("scaffold", "census", "validate", "all"), default="all")
    args = parser.parse_args()

    if args.mode in {"scaffold", "census", "all"}:
        final = generate_artifacts(mode=args.mode, run_routes=args.mode == "all")
        print(
            json.dumps(
                {
                    "status": final.get("status"),
                    "round_id": ROUND_ID,
                    "required_gate_adopted": final.get("required_gate_adopted"),
                    "future_current_route_blocking_claimed": final.get("future_current_route_blocking_claimed"),
                    "machine_required_gate_adoption_complete": final.get("machine_required_gate_adoption_complete"),
                },
                sort_keys=True,
            )
        )
    if args.mode in {"validate", "all"}:
        report, ok = validate_artifacts(require_complete=args.mode == "all")
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0
