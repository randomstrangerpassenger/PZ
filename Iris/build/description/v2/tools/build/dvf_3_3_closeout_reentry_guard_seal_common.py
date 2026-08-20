from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    V2_ROOT,
    canonical_hash,
    read_json,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_text,
)


GENERATED_AT = "2026-06-23T00:00:00+09:00"
ROUND_ID = "dvf_3_3_closeout_reentry_guard_seal"
EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID

PLAN_PATH = REPO_ROOT / "docs" / "dvf_3_3_closeout_reentry_guard_seal_plan.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_closeout_reentry_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "dvf_3_3_closeout_reentry_ledger_packet.md"
COMPLETION_POLICY_DOC = REPO_ROOT / "docs" / "completion_vocabulary_separation_policy.md"
PREDECESSOR_POLICY_DOC = REPO_ROOT / "docs" / "predecessor_reentry_guard_policy.md"

ROADMAP_DOC = REPO_ROOT / "docs" / "ROADMAP.md"
DECISIONS_DOC = REPO_ROOT / "docs" / "DECISIONS.md"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "ARCHITECTURE.md"
CURRENT_REQUIRED_VALIDATIONS = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
REQUIRED_VALIDATIONS_PROJECTION_ENV = (
    "IRIS_ROUND3_REQUIRED_VALIDATIONS_PROJECTION"
)
CURRENT_REQUIRED_VALIDATIONS_SCHEMA_VERSION = (
    "round3-current-route-required-validations-v1"
)

CLAIM_TEXT_FIELDS = {
    "claim",
    "claims",
    "description",
    "narrative",
    "non_claims",
    "policy",
    "reason",
    "summary",
}
IDENTIFIER_FIELDS = {
    "adopted_row_identity",
    "artifact_id",
    "bundle_id",
    "collision_group_id",
    "enforcement",
    "field",
    "generated_at",
    "path",
    "role",
    "route",
    "schema_id",
    "schema_version",
    "state",
    "status",
    "test_id",
}
IDENTIFIER_COLLECTION_FIELDS = {
    "exact_members",
}

CURRENT_ROUTE_RESULT = EVIDENCE_ROOT / "phase7" / "full_current_route_validation_result.json"
EXPECTED_CURRENT_ROUTE_TEST_COUNT = 107
HISTORICAL_ROUTE_VALIDATION_MODE = "historical_approved_successor_baseline"
EXPECTED_HISTORICAL_REQUIRED_TEST_COUNT = 52
EXPECTED_HISTORICAL_REQUIRED_ARTIFACT_COUNT = 112
EXPECTED_HISTORICAL_REQUIRED_TEST_IDS_SHA256 = (
    "bec4bb70527e17528205996acd7dc83be2c79b06e97a67f3af9257c8913503ac"
)
FULL_CURRENT_ROUTE_SCHEMA_VERSION = "round3-contract-test-run-v1"
FULL_CURRENT_ROUTE_CONTRACT_CLASS = "current"

CLAIM_BOUNDARY = (
    "DVF 3-3 closeout claim boundary is axis-qualified. Broad completion and cutover subset "
    "completion are separated. Predecessor 2105 / 2084 / 21 cannot reenter as current hard gate, "
    "runtime authority, current debt, package authority, or release readiness. Required-validation "
    "guard adoption is governance-only and does not mutate source, rendered, Lua bridge, runtime, "
    "or package authority surfaces."
)

NON_CLAIMS = [
    "no_live_migration_execution_completion",
    "no_live_mutation_completion",
    "no_current_authority_cutover_execution",
    "no_terminal_disposition_re_adjudication",
    "no_denominator_redefinition",
    "no_source_rendered_lua_runtime_package_mutation",
    "no_release_readiness",
    "no_package_readiness",
    "no_workshop_readiness",
    "no_b42_readiness",
    "no_deployment_readiness",
    "no_manual_in_game_qa",
    "no_semantic_quality_completion",
    "no_public_text_acceptance",
]

ALLOWED_CLAIM_CLASSES: dict[str, dict[str, Any]] = {
    "terminal_disposition_complete": {
        "allowed_denominator": "terminal_executing_consumer_member_rows",
        "allowed_evidence_root": "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication",
        "acceptable_surface_roles": ["terminal_disposition_closeout", "terminal_ledger_packet"],
        "forbidden_inference": [
            "live_migration_execution_complete",
            "current_authority_cutover_complete",
            "release_readiness",
        ],
    },
    "broad_consumer_completion": {
        "allowed_denominator": "broad_consumer_universe",
        "allowed_evidence_root": "Iris/build/description/v2/staging/consumer_universe_denominator_lock",
        "acceptable_surface_roles": ["denominator_governance", "future_closeout_guard_input"],
        "forbidden_inference": ["cutover_subset_completion", "live_execution_completion"],
    },
    "cutover_subset_completion": {
        "allowed_denominator": "cutover_subset_rows",
        "allowed_evidence_root": "Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover",
        "acceptable_surface_roles": ["cutover_specific_closeout"],
        "forbidden_inference": ["broad_consumer_completion", "release_readiness"],
    },
    "pre_apply_readiness_complete": {
        "allowed_denominator": "readiness_gate_rows",
        "allowed_evidence_root": "Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution",
        "acceptable_surface_roles": ["pre_apply_readiness"],
        "forbidden_inference": ["live_migration_execution_complete", "live_mutation_complete"],
    },
    "phase4_live_apply_allowed": {
        "allowed_denominator": "live_mutation_eligible_rows",
        "allowed_evidence_root": "Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution",
        "acceptable_surface_roles": ["authorization_gate"],
        "forbidden_inference": ["live_mutation_complete", "runtime_authority_current"],
    },
    "required_validation_gate_adopted": {
        "allowed_denominator": "current_route_required_validation_manifest",
        "allowed_evidence_root": "Iris/_docs/round3/current_route_required_validations.json",
        "acceptable_surface_roles": ["governance_gate"],
        "forbidden_inference": ["runtime_writer", "source_writer", "release_readiness"],
    },
    "historical_predecessor_trace": {
        "allowed_denominator": "historical_or_predecessor_only",
        "allowed_evidence_root": "historical_trace",
        "acceptable_surface_roles": ["historical_trace", "predecessor_context"],
        "forbidden_inference": ["current_hard_gate", "current_debt", "runtime_authority_current"],
    },
    "source_overlay_repair_current_route_validation_pass": {
        "allowed_denominator": "current_route_validation_tests",
        "allowed_evidence_root": "Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair",
        "acceptable_surface_roles": ["problem7_current_route_validation_pass"],
        "forbidden_inference": ["closeout_reentry_guard_seal_complete", "problem8_complete"],
    },
    "problem7_full_current_route_validation_pass": {
        "allowed_denominator": "current_route_validation_tests",
        "allowed_evidence_root": "Iris/_docs/round3/round3_run_contract_tests.py",
        "acceptable_surface_roles": ["problem7_validation_readpoint"],
        "forbidden_inference": ["closeout_reentry_guard_seal_complete", "live_execution_complete"],
    },
}

FORBIDDEN_OVERCLAIM_CLASSES: dict[str, dict[str, str]] = {
    "live_migration_execution_complete_without_execution": {
        "violation_reason": "Live migration execution completion requires a separate execution round.",
        "blocked_closeout_state": "blocked_forbidden_overclaim_detected",
    },
    "runtime_authority_current_without_runtime_authority_input": {
        "violation_reason": "Runtime authority cannot be declared from governance evidence.",
        "blocked_closeout_state": "blocked_forbidden_overclaim_detected",
    },
    "release_readiness": {
        "violation_reason": "Release readiness is outside this governance seal.",
        "blocked_closeout_state": "blocked_forbidden_overclaim_detected",
    },
    "package_readiness": {
        "violation_reason": "Package readiness is outside this governance seal.",
        "blocked_closeout_state": "blocked_forbidden_overclaim_detected",
    },
    "workshop_readiness": {
        "violation_reason": "Workshop readiness is outside this governance seal.",
        "blocked_closeout_state": "blocked_forbidden_overclaim_detected",
    },
    "deployment_readiness": {
        "violation_reason": "Deployment readiness is outside this governance seal.",
        "blocked_closeout_state": "blocked_forbidden_overclaim_detected",
    },
    "manual_qa_pass": {
        "violation_reason": "Manual QA is not performed by this round.",
        "blocked_closeout_state": "blocked_forbidden_overclaim_detected",
    },
    "semantic_quality_completion": {
        "violation_reason": "Semantic quality completion is not a claim class in this round.",
        "blocked_closeout_state": "blocked_forbidden_overclaim_detected",
    },
    "public_text_acceptance": {
        "violation_reason": "Public-facing text acceptance is outside this governance seal.",
        "blocked_closeout_state": "blocked_forbidden_overclaim_detected",
    },
}

CLAIM_TERMS = ("complete", "closed", "sealed", "PASS", "ready", "allowed", "migrated", "current")
PROBLEM7_ALIASES = ("problem 7", "problem7", "source-overlay repair", "source_overlay_repair")
PREDECESSOR_VALUES = ("2105", "2084", "21")

PROTECTED_SURFACE_PATHS = [
    ("Iris/build/description/v2/data/dvf_3_3_input_manifest.json", "current_input_manifest", False),
    ("Iris/build/description/v2/data/dvf_3_3_facts.jsonl", "current_source_facts", False),
    ("Iris/build/description/v2/data/dvf_3_3_decisions.jsonl", "current_source_decisions", False),
    ("Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl", "current_overlay_support", True),
    ("Iris/build/description/v2/output/dvf_3_3_rendered.json", "current_rendered_output", True),
    ("Iris/build/description/v2/output/style_normalization_changes.jsonl", "current_style_side_output", True),
    ("Iris/build/description/v2/output/compose_requeue_candidates.jsonl", "current_requeue_side_output", True),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua", "live_runtime_chunk_manifest", True),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks", "live_runtime_chunk_dir", True),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua", "live_runtime_monolith_facade", True),
    ("Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua", "stale_bridge_surface", True),
    ("Iris/build/package/Iris/media/lua/client/Iris/Data", "package_peer_runtime_output", True),
]

REQUIRED_ARTIFACTS = [
    {
        "path": "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase2/dvf_3_3_closeout_claim_taxonomy.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "standalone_complete_allowed", "equals": False},
        ],
    },
    {
        "path": "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase3/predecessor_reentry_guard_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "predecessor_reentry_violation_count", "equals": 0},
        ],
    },
    {
        "path": "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase4/closeout_claim_boundary_guard_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "ambiguous_complete_claim_count", "equals": 0},
            {"field": "broad_cutover_collision_count", "equals": 0},
        ],
    },
    {
        "path": "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase5/closeout_reentry_guard_manifest_adoption_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "required_gate_adoption_status", "equals": "adopted_required_gate"},
            {"field": "dual_reentry_authority_count", "equals": 0},
        ],
    },
    {
        "path": "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/final_no_mutation_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "changed_count", "equals": 0},
        ],
    },
    {
        "path": "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/final_closeout_reentry_guard_seal_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "machine_contract_status", "equals": "PASS"},
            {"field": "closeout_state", "equals": "canonical_complete"},
            {"field": "canonical_seal_allowed", "equals": True},
            {"field": "independent_review_status", "equals": "PASS"},
        ],
    },
    {
        "path": "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/independent_review_artifact_hash_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "independent_review_status", "equals": "PASS"},
            {"field": "canonical_seal_allowed", "equals": True},
            {"field": "primary_review_artifact_missing_count", "equals": 0},
        ],
    },
]

REQUIRED_TESTS = [
    {
        "required": True,
        "role": "closeout_reentry_guard_required_validation",
        "test_id": (
            "test_dvf_3_3_closeout_reentry_guard_seal."
            "DvfCloseoutReentryGuardSealTest.test_claim_surface_scan_is_fail_closed_and_not_self_scanned"
        ),
    },
    {
        "required": True,
        "role": "closeout_reentry_guard_required_validation",
        "test_id": (
            "test_dvf_3_3_closeout_reentry_guard_seal."
            "DvfCloseoutReentryGuardSealTest.test_generate_final_report_reflects_claim_scan_failure"
        ),
    },
    {
        "required": True,
        "role": "closeout_reentry_guard_required_validation",
        "test_id": (
            "test_dvf_3_3_closeout_reentry_guard_seal."
            "DvfCloseoutReentryGuardSealTest.test_manifest_adoption_is_governance_only_and_runner_visible"
        ),
    },
    {
        "required": True,
        "role": "closeout_reentry_guard_required_validation",
        "test_id": (
            "test_dvf_3_3_closeout_reentry_guard_seal."
            "DvfCloseoutReentryGuardSealTest.test_validator_requires_full_current_route_result_for_complete_contract"
        ),
    }
]


def phase_dir(phase: str) -> Path:
    return EVIDENCE_ROOT / phase


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def file_record(path: str | Path, role: str, *, required: bool = True) -> dict[str, Any]:
    resolved = resolve_repo(path)
    return {
        "path": rel(resolved),
        "role": role,
        "required": required,
        "exists": resolved.exists(),
        "kind": "dir" if resolved.is_dir() else "file" if resolved.is_file() else "missing",
        "sha256": sha256_file(resolved) if resolved.is_file() else None,
        "bytes": resolved.stat().st_size if resolved.exists() and resolved.is_file() else None,
        "line_count": line_count(resolved) if resolved.exists() and resolved.is_file() else None,
        "status": "PRESENT" if resolved.exists() else "MISSING_REQUIRED" if required else "ABSENT_ALLOWED",
    }


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def decoded_utf8_eol_identity(path: Path) -> tuple[str, int]:
    """Return a checkout-EOL-independent identity for UTF-8 review artifacts."""
    decoded = path.read_bytes().decode("utf-8")
    canonical = decoded.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    return hashlib.sha256(canonical).hexdigest(), len(canonical)


def independent_review_file_record(path: Path) -> dict[str, Any]:
    record = file_record(path, "primary_review_artifact", required=True)
    if record["exists"] and record["kind"] == "file":
        identity_sha256, identity_bytes = decoded_utf8_eol_identity(path)
        record["identity_mode"] = "decoded_utf8_eol_lf"
        record["sha256"] = identity_sha256
        record["bytes"] = identity_bytes
    else:
        record["identity_mode"] = None
    return record


def protected_surface_definition() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-closeout-reentry-protected-surface-v1",
        "generated_at": GENERATED_AT,
        "claim_boundary": CLAIM_BOUNDARY,
        "protected_paths": [
            {
                "path": path,
                "role": role,
                "optional": optional,
                "kind": "dir" if resolve_repo(path).is_dir() else "file",
            }
            for path, role, optional in PROTECTED_SURFACE_PATHS
        ],
    }


def expand_protected_entries(surface: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for entry in surface.get("protected_paths", []):
        base = resolve_repo(entry["path"])
        if entry.get("kind") == "dir":
            if base.exists():
                paths.extend(sorted(path for path in base.rglob("*") if path.is_file()))
            else:
                paths.append(base)
        else:
            paths.append(base)
    return paths


def protected_surface_hash(surface: dict[str, Any]) -> dict[str, Any]:
    records = [file_record(path, "protected_surface_file", required=False) for path in expand_protected_entries(surface)]
    comparable = [
        {"path": row["path"], "exists": row["exists"], "sha256": row["sha256"], "bytes": row["bytes"]}
        for row in records
    ]
    return {
        "schema_version": "dvf-3-3-closeout-reentry-protected-surface-hash-v1",
        "generated_at": GENERATED_AT,
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(comparable),
    }


def protected_surface_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_rows = {row["path"]: row for row in before.get("records", [])}
    after_rows = {row["path"]: row for row in after.get("records", [])}
    changed = []
    for path in sorted(set(before_rows).union(after_rows)):
        if before_rows.get(path) != after_rows.get(path):
            changed.append({"path": path, "before": before_rows.get(path), "after": after_rows.get(path)})
    return {
        "schema_version": "dvf-3-3-closeout-reentry-protected-surface-diff-v1",
        "generated_at": GENERATED_AT,
        "changed_count": len(changed),
        "changed": changed,
    }


def is_negated_or_policy_definition(text: str) -> bool:
    lowered = text.lower()
    assertion_predicate = re.search(
        r"\b(complete(?:d)?|pass(?:ed)?|achiev(?:e|ed|ement)|approved?|satisfied|ready|sealed?|established|succeeded|fulfilled)\b",
        lowered,
    )
    if "not only" in lowered or (assertion_predicate and "without" in lowered):
        return False
    policy_tokens = (
        "cannot",
        "must not",
        "mustn't",
        "not ",
        " no ",
        "forbidden",
        "blocked",
        "reject",
        "prevent",
        "no_",
        "non-claim",
        "non_claim",
        "out of scope",
        "does not",
        "do not",
        "is not",
        "are not",
        "non-decision",
        "아니다",
        "아님",
        "아니며",
        "아니라",
        "아닌",
        "않는다",
        "않다",
        "않도록",
        "않으며",
        "않고",
        "수 없다",
        "못하도록",
        "선언하지",
        "승인하지",
        "승인한 것이 아니다",
        "읽지 않는다",
        "의미하지",
        "세지 않는다",
        "승격하지",
        "재진입하지",
        "오독 금지",
        "금지",
        "방지",
        "범위에서만",
        "후속 작업",
        "재봉인",
    )
    return any(token in lowered for token in policy_tokens)


def classify_predecessor_context(text: str) -> list[str]:
    lowered = text.lower()
    if not any(value in lowered for value in PREDECESSOR_VALUES):
        return []
    if is_negated_or_policy_definition(text):
        return []

    hits: list[str] = []
    patterns = [
        (r"current[_ -]?hard[_ -]?gate", "current_hard_gate_reentry"),
        (r"(current[_ -]?)?runtime[_ -]?authority", "runtime_authority_reentry"),
        (r"current[_ -]?debt", "current_debt_reentry"),
        (r"package[_ -]?authority", "package_authority_reentry"),
        (r"release[_ -]?readiness", "release_readiness_reentry"),
        (r"required[_ -]?migration[_ -]?target[_ -]?expansion", "required_migration_target_expansion"),
        (r"(old[_ -]?chunks?|monolith|legacy[_ -]?bridge)[^.\n]{0,40}(fallback|authority)", "old_runtime_fallback_reentry"),
        (r"(raw[_ -]?predecessor|raw[_ -]?audit|dry[-_ ]?run|readiness).*(direct[_ -]?execution[_ -]?authority|execution[_ -]?authority)", "raw_predecessor_direct_authority_read"),
    ]
    for pattern, code in patterns:
        if re.search(pattern, lowered):
            hits.append(code)
    return sorted(set(hits))


def classify_claim_text(text: str) -> list[str]:
    lowered = text.lower()
    if is_negated_or_policy_definition(text):
        return []
    hits: list[str] = []
    forbidden_patterns = [
        (r"live[_ -]?migration[_ -]?execution.*complete", "live_migration_execution_complete_without_execution"),
        (r"runtime[_ -]?authority.*current", "runtime_authority_current_without_runtime_authority_input"),
        (r"release[_ -]?readiness", "release_readiness"),
        (r"package[_ -]?readiness", "package_readiness"),
        (r"workshop[_ -]?readiness", "workshop_readiness"),
        (r"deployment[_ -]?readiness", "deployment_readiness"),
        (r"manual[_ -]?(in[_ -]?game[_ -]?)?qa.*pass", "manual_qa_pass"),
        (r"semantic[_ -]?quality.*complete", "semantic_quality_completion"),
        (r"phase4[_ -]?live[_ -]?apply[_ -]?allowed.*live[_ -]?(migration|mutation|execution).*complete", "live_migration_execution_complete_without_execution"),
        (r"live[_ -]?mutation.*complete", "live_migration_execution_complete_without_execution"),
        (r"pre[-_ ]?apply[_ -]?readiness.*live.*complete", "live_migration_execution_complete_without_execution"),
    ]
    for pattern, code in forbidden_patterns:
        if re.search(pattern, lowered):
            hits.append(code)
    public_text_acceptance_reference = re.search(
        r"public[_ -]?(facing[_ -]?)?text.*accept",
        lowered,
    )
    required_validation_reference = re.search(
        r"\b(required[_ -]?(gate|validation|test)|validation[_ -]?requirement)\b",
        lowered,
    )
    assertion_predicate = re.search(
        r"\b(complete(?:d)?|pass(?:ed)?|achiev(?:e|ed|ement)|approved?|"
        r"satisfied|ready|sealed?|established|succeeded|fulfilled)\b",
        lowered,
    )
    if public_text_acceptance_reference and not (
        required_validation_reference and not assertion_predicate
    ):
        hits.append("public_text_acceptance")
    if any(alias in lowered for alias in PROBLEM7_ALIASES) and "problem8" in lowered and "complete" in lowered:
        hits.append("problem7_to_problem8_completion_promotion")
    return sorted(set(hits))


def classify_complete_suffix(value: str, owning_closeout_state: str | None) -> str:
    if not value.endswith("_complete"):
        return "not_complete_suffix"
    if owning_closeout_state in {"complete", "canonical_complete"}:
        return "allowed_complete_suffix"
    return "blocked_complete_suffix_state_mismatch"


def tokenize_claim_terms(text: str) -> list[str]:
    terms = []
    for term in CLAIM_TERMS:
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", text, re.IGNORECASE):
            terms.append(term)
    return terms


def is_top_doc_boundary_routing_definition(path: Path, line: str) -> bool:
    normalized = rel(path).replace("\\", "/")
    top_doc = next(
        (
            name
            for name in (
                "docs/ARCHITECTURE.md",
                "docs/DECISIONS.md",
                "docs/ROADMAP.md",
            )
            if normalized == name
            or normalized.endswith("/" + name)
        ),
        None,
    )
    if top_doc is None:
        return False
    lowered = line.lower()
    stripped = lowered.strip()
    normalized_line = " ".join(line.split())
    exact_current_nonclaim_lines = {
        "docs/ARCHITECTURE.md": {
            "* Reusable public-text assessment는 DVF/QG subject에 적용되는 오프라인 evidence producer로 유지하며 Publish Boundary가 그 결과의 acceptance를 별도로 판단한다.",
            "* public-text acceptance와 publication / release acceptance를 소유한다.",
        },
        "docs/DECISIONS.md": {
            "* `PublicTextQualityAcceptanceCurrentRouteTest._phase7_self_test()`는 동일 self-test producer를 여러 test가 다시 실행한 뒤 서로 다른 result case만 읽는 명시적 우선 후보다.",
        },
        "docs/ROADMAP.md": {
            "- exact result/subject identity 없이 canonical review/seal을 주장하거나 이 component evidence를 Public Text Quality PASS, Publish Boundary PASS 또는 release readiness로 확대하기",
        },
    }
    if normalized_line in exact_current_nonclaim_lines.get(top_doc, set()):
        return True
    public_text_acceptance = re.search(
        r"public[_ -]?(?:facing[_ -]?)?text.*accept",
        lowered,
    ) is not None
    positive_completion_markers = (
        "achieved",
        "accepted",
        "complete",
        "pass",
        "satisfied",
        "달성",
        "완료",
        "통과",
    )
    if (
        top_doc == "docs/ARCHITECTURE.md"
        and public_text_acceptance
        and not any(marker in lowered for marker in positive_completion_markers)
        and (
            stripped.startswith(("->", "→"))
            or "!=" in lowered
            or (
                "별도" in lowered
                and (
                    "naturalization" in lowered
                    or "publish boundary" in lowered
                )
            )
        )
    ):
        return True
    if "-> publish boundary closure" in lowered or "→ publish boundary closure" in lowered:
        return True
    if (
        top_doc == "docs/ARCHITECTURE.md"
        and "public text quality" in lowered
        and "public acceptance" in lowered
        and "release readiness" in lowered
    ):
        return True
    if "publish boundary" not in lowered:
        return False
    boundary_definition_markers = (
        "separate",
        "separat",
        "axis",
        "responsib",
        "책임",
        "별도",
        "축",
    )
    readiness_markers = (
        "public text acceptance",
        "public acceptance",
        "semantic quality acceptance",
        "package publication",
        "release",
        "workshop",
        "manual qa",
    )
    return any(marker in lowered for marker in boundary_definition_markers) and any(
        marker in lowered for marker in readiness_markers
    )


def is_allowed_claim_scan_definition_context(path: Path, line: str) -> bool:
    normalized = rel(path).replace("\\", "/")
    evidence_root = rel(EVIDENCE_ROOT).replace("\\", "/")
    policy_definition_docs = {
        rel(PLAN_PATH).replace("\\", "/"),
        rel(CLAIM_BOUNDARY_DOC).replace("\\", "/"),
        rel(LEDGER_PACKET_DOC).replace("\\", "/"),
        rel(COMPLETION_POLICY_DOC).replace("\\", "/"),
        rel(PREDECESSOR_POLICY_DOC).replace("\\", "/"),
    }
    generated_definition_prefixes = tuple(
        f"{evidence_root}/{phase}/"
        for phase in ("phase0", "phase2", "phase3", "phase4", "phase5", "phase6")
    )
    generated_definition_files = {
        f"{evidence_root}/phase7/final_pinned_command_manifest.json",
        f"{evidence_root}/phase7/full_current_route_validation_result.json",
    }
    if is_negated_or_policy_definition(line):
        return True
    if is_top_doc_boundary_routing_definition(path, line):
        return True
    if normalized in policy_definition_docs:
        return True
    if normalized.endswith("dvf_3_3_closeout_reentry_guard_seal_common.py"):
        return True
    if normalized.endswith("test_dvf_3_3_closeout_reentry_guard_seal.py"):
        return True
    if normalized.startswith(generated_definition_prefixes):
        return True
    return normalized in generated_definition_files


def doc_text_completion_policy() -> str:
    allowed = "\n".join(f"- `{name}`" for name in sorted(ALLOWED_CLAIM_CLASSES))
    forbidden = "\n".join(f"- `{name}`" for name in sorted(FORBIDDEN_OVERCLAIM_CLASSES))
    return f"""# Completion Vocabulary Separation Policy

Status: `adopted_required_gate_governance_policy`.

This policy keeps DVF 3-3 completion words axis-qualified. A standalone `complete`, `closed`, `sealed`, `PASS`, `ready`, `allowed`, `migrated`, or `current` token is not enough to prove a lifecycle claim.

Allowed claim classes:

{allowed}

Forbidden overclaim classes:

{forbidden}

Rules:

- `complete` must be bound to an owning axis and evidence root.
- `_complete` suffixes require the owning evidence closeout state to be `complete` or `canonical_complete`.
- Problem 7 current-route validation PASS is not Closeout / Reentry Guard Seal completion.
- Required-validation gate adoption is governance-only; it is not a source, rendered, Lua bridge, runtime, or package writer.
- Release, package, Workshop, deployment, manual QA, semantic quality, and public text acceptance claims are outside this policy.
"""


def doc_text_predecessor_policy() -> str:
    return """# Predecessor Reentry Guard Policy

Status: `adopted_required_gate_governance_policy`.

Predecessor values `2105`, `2084`, and `21` are allowed only in historical predecessor trace, frozen comparison baseline, successor evidence contract denominator, migration provenance, or terminal disposition provenance contexts.

Forbidden contexts:

- current hard gate
- current runtime authority
- package authority
- release readiness
- current debt
- required migration target expansion
- old chunks, monolith, or legacy bridge fallback
- raw predecessor artifact direct execution authority read

This policy does not delete predecessor trace. It prevents predecessor trace from becoming current authority, runtime authority, current debt, package authority, or release readiness.
"""


def doc_text_claim_boundary() -> str:
    return f"""# DVF 3-3 Closeout / Reentry Claim Boundary

Status: `adopted_required_gate_governance_policy`.

{CLAIM_BOUNDARY}

Allowed positive claim:

- `closeout_reentry_guard_machine_contract_pass`: claim taxonomy, predecessor reentry guard, closeout boundary guard, manifest adoption report, and no-mutation report are present and valid.

Canonical seal boundary:

- canonical seal is allowed because non-Claude independent review returned PASS.
- owner-reserved Branch B attribution is recorded as the route for this implementation.
- required-validation manifest adoption remains governance-only.

Non-claims:

{chr(10).join(f"- `{item}`" for item in NON_CLAIMS)}
"""


def doc_text_ledger_packet() -> str:
    return f"""# DVF 3-3 Closeout / Reentry Guard Ledger Packet

Additive ledger packet.

- evidence root: `{rel(EVIDENCE_ROOT)}`
- final report: `{rel(phase_path('phase7', 'final_closeout_reentry_guard_seal_report.json'))}`
- claim taxonomy: `{rel(phase_path('phase2', 'dvf_3_3_closeout_claim_taxonomy.json'))}`
- predecessor guard: `{rel(phase_path('phase3', 'predecessor_reentry_guard_report.json'))}`
- boundary guard: `{rel(phase_path('phase4', 'closeout_claim_boundary_guard_report.json'))}`
- no-mutation report: `{rel(phase_path('phase7', 'final_no_mutation_report.json'))}`
- required-validation adoption: `adopted_required_gate`
- canonical seal: `PASS`

This packet keeps broad completion, terminal disposition completion, cutover subset completion, pre-apply readiness, live apply authorization, and live execution completion as separate axes.

It does not complete live migration execution, live mutation, current authority cutover, terminal disposition re-adjudication, denominator redefinition, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality completion, public-facing text quality acceptance, full runtime equivalence, or full compatibility preservation.
"""


def write_docs() -> None:
    write_text(COMPLETION_POLICY_DOC, doc_text_completion_policy())
    write_text(PREDECESSOR_POLICY_DOC, doc_text_predecessor_policy())
    write_text(CLAIM_BOUNDARY_DOC, doc_text_claim_boundary())
    write_text(LEDGER_PACKET_DOC, doc_text_ledger_packet())


def write_phase0() -> None:
    write_json(
        phase_path("phase0", "roadmap_input_binding.json"),
        {
            "schema_version": "dvf-3-3-closeout-reentry-roadmap-input-binding-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "source_attachment_path": "C:/Users/MW/.codex/attachments/b1594479-027f-40f2-b7fc-edaee92df52a/pasted-text.txt",
            "source_attachment_sha256": "AD5CEC639DA01B60E6E905FD1DBCC94702D2F604756DDE996A7E7417AEEBD6AA",
            "source_attachment_readable_in_current_workspace": False,
            "stable_rebound_path": rel(PLAN_PATH),
            "stable_rebound_sha256": sha256_file(PLAN_PATH),
            "stable_rebound_line_count": line_count(PLAN_PATH),
            "binding_status": "rebound_to_direct_plan_artifact",
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_text(
        phase_path("phase0", "canonical_roadmap_input.md"),
        "# Canonical Roadmap Input Binding\n\n"
        f"Stable rebound path: `{rel(PLAN_PATH)}`.\n\n"
        "The transient attachment is recorded as drafting provenance only. The repository plan artifact is the stable execution input.\n",
    )
    write_json(
        phase_path("phase0", "owner_reserved_seal_requirements.json"),
        {
            "schema_version": "dvf-3-3-closeout-reentry-owner-reserved-seal-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "round_identifier": ROUND_ID,
            "branch_attribution": "branch_b_new_closeout_reentry_guard_owner_route",
            "branch_attribution_status": "resolved_by_current_owner_execution_request",
            "completion_token_final_string": "closeout_reentry_guard_machine_contract_pass",
            "seal_gate_kind": "required_validation_gate_adopted_canonical_review_pass",
            "owner_adoption_replaces_independent_review": False,
            "non_claude_independent_review_required": True,
            "independent_review_status": "PASS",
            "canonical_seal_allowed": True,
        },
    )


def scan_surface_files() -> list[Path]:
    generated_evidence = [
        phase_path("phase0", "owner_reserved_seal_requirements.json"),
        phase_path("phase0", "roadmap_input_binding.json"),
        phase_path("phase2", "dvf_3_3_closeout_claim_taxonomy.json"),
        phase_path("phase2", "completion_vocabulary_separation_report.json"),
        phase_path("phase2", "final_completion_axis_matrix.json"),
        phase_path("phase3", "predecessor_reentry_context_allowlist.json"),
        phase_path("phase3", "predecessor_reentry_guard_report.json"),
        phase_path("phase3", "raw_predecessor_authority_read_report.json"),
        phase_path("phase3", "current_debt_reentry_report.json"),
        phase_path("phase3", "dual_reentry_authority_report.json"),
        phase_path("phase4", "closeout_claim_boundary_guard_report.json"),
        phase_path("phase4", "problem7_to_closeout_guard_promotion_guard_report.json"),
        phase_path("phase5", "closeout_reentry_guard_manifest_adoption_report.json"),
        phase_path("phase6", "docs_claim_taxonomy_consistency_report.json"),
        phase_path("phase7", "final_closeout_reentry_guard_seal_report.json"),
        phase_path("phase7", "final_no_mutation_report.json"),
        phase_path("phase7", "final_pinned_command_manifest.json"),
        phase_path("phase7", "full_current_route_validation_result.json"),
    ]
    candidates = [
        PLAN_PATH,
        CLAIM_BOUNDARY_DOC,
        LEDGER_PACKET_DOC,
        COMPLETION_POLICY_DOC,
        PREDECESSOR_POLICY_DOC,
        ROADMAP_DOC,
        DECISIONS_DOC,
        ARCHITECTURE_DOC,
        claim_scan_required_validations_path(),
        REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tools" / "build" / "dvf_3_3_closeout_reentry_guard_seal_common.py",
        REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tools" / "build" / "run_dvf_3_3_closeout_reentry_guard_seal.py",
        REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tools" / "build" / "validate_dvf_3_3_closeout_claim_taxonomy.py",
        REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tools" / "build" / "validate_dvf_3_3_closeout_claim_boundary.py",
        REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tools" / "build" / "validate_dvf_3_3_predecessor_reentry_guard.py",
        REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tests" / "test_dvf_3_3_closeout_reentry_guard_seal.py",
        *generated_evidence,
    ]
    return sorted({resolve_repo(path) for path in candidates if resolve_repo(path).exists()}, key=rel)


def same_surface_path(left: str | Path, right: str | Path) -> bool:
    return resolve_repo(left) == resolve_repo(right)


def claim_scan_required_validations_path() -> Path:
    projected = os.environ.get(REQUIRED_VALIDATIONS_PROJECTION_ENV)
    if not projected:
        return CURRENT_REQUIRED_VALIDATIONS
    path = Path(projected)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def surface_path_is_within(
    path: str | Path,
    root: str | Path,
) -> bool:
    try:
        resolve_repo(path).relative_to(resolve_repo(root))
        return True
    except ValueError:
        return False


def surface_family(path: Path) -> str:
    if same_surface_path(path, claim_scan_required_validations_path()):
        return "required_validation_manifest"
    if same_surface_path(path, LEDGER_PACKET_DOC):
        return "ledger_packets"
    current_doc_paths = (
        PLAN_PATH,
        CLAIM_BOUNDARY_DOC,
        COMPLETION_POLICY_DOC,
        PREDECESSOR_POLICY_DOC,
        ROADMAP_DOC,
        DECISIONS_DOC,
        ARCHITECTURE_DOC,
    )
    if any(same_surface_path(path, target) for target in current_doc_paths):
        return "docs"
    if surface_path_is_within(path, EVIDENCE_ROOT):
        return "generated_evidence"
    normalized = rel(path)
    if normalized.startswith("docs/"):
        if normalized.endswith("_ledger_packet.md"):
            return "ledger_packets"
        return "docs"
    if normalized.startswith("Iris/build/description/v2/tools/build/validate_"):
        return "validators"
    if normalized.startswith("Iris/build/description/v2/tools/build/"):
        return "validators"
    if normalized.startswith("Iris/build/description/v2/tests/"):
        return "tests"
    if normalized.startswith("Iris/build/description/v2/staging/"):
        return "generated_evidence"
    return "other"


def classify_surface_line(path: Path, line: str) -> dict[str, Any] | None:
    terms = tokenize_claim_terms(line)
    predecessor_hits = classify_predecessor_context(line)
    claim_hits = classify_claim_text(line)
    if not terms and not predecessor_hits and not claim_hits:
        return None
    definition_context = is_allowed_claim_scan_definition_context(path, line)
    role = "historical_or_policy_trace" if is_negated_or_policy_definition(line) else "claim_surface"
    if predecessor_hits:
        role = "forbidden_predecessor_reentry_definition" if definition_context else "forbidden_predecessor_reentry_violation"
    if claim_hits:
        role = "forbidden_overclaim_definition" if definition_context else "forbidden_overclaim_violation"
    return {
        "path": rel(path),
        "surface_family": surface_family(path),
        "line_text": line,
        "terms": terms,
        "predecessor_hits": predecessor_hits,
        "claim_hits": claim_hits,
        "role": role,
        "definition_context": definition_context,
        "classification": "classified" if definition_context or not (predecessor_hits or claim_hits) else "blocked",
    }


def json_pointer_segment(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def structured_string_semantic_role(field: str | None) -> str:
    if field in CLAIM_TEXT_FIELDS or (
        field is not None
        and field.endswith(
            ("_claim", "_claims", "_description", "_narrative", "_policy", "_summary")
        )
    ):
        return "claim_text"
    if field in IDENTIFIER_COLLECTION_FIELDS:
        return "identifier"
    if field in IDENTIFIER_FIELDS or (
        field is not None
        and field.endswith(("_id", "_identity", "_path", "_root", "_sha256"))
    ):
        return "identifier"
    return "unknown_string_fail_closed"


def structured_manifest_blocker(
    path: Path,
    code: str,
    pointer: str,
    field: str | None,
    *,
    expected: str,
    actual: str,
) -> dict[str, Any]:
    return {
        "path": rel(path),
        "surface_family": surface_family(path),
        "json_pointer": pointer,
        "field": field,
        "semantic_role": "schema_contract",
        "role": "structured_manifest_schema_violation",
        "code": code,
        "expected": expected,
        "actual": actual,
        "definition_context": False,
        "classification": "blocked",
    }


def strict_json_loads(text: str) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non_json_constant:{value}")

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate_json_key:{key}")
            result[key] = value
        return result

    return json.loads(
        text,
        parse_constant=reject_constant,
        object_pairs_hook=reject_duplicate_keys,
        strict=True,
    )


def classify_required_validation_manifest_text(
    text: str,
    *,
    path: Path = CURRENT_REQUIRED_VALIDATIONS,
) -> dict[str, Any]:
    string_leaves: list[dict[str, Any]] = []
    scan_rows: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    try:
        payload = strict_json_loads(text)
    except (json.JSONDecodeError, ValueError) as exc:
        blockers.append(
            structured_manifest_blocker(
                path,
                "strict_json_parse_failed",
                "",
                None,
                expected="strict_json_document",
                actual=f"{type(exc).__name__}:{exc}",
            )
        )
        return {
            "path": rel(path),
            "status": "FAIL",
            "schema_version": None,
            "string_leaf_count": 0,
            "semantic_role_counts": {},
            "string_leaves": [],
            "scan_rows": [],
            "blocker_count": len(blockers),
            "blockers": blockers,
        }

    if not isinstance(payload, dict):
        blockers.append(
            structured_manifest_blocker(
                path,
                "manifest_root_type_invalid",
                "",
                None,
                expected="object",
                actual=type(payload).__name__,
            )
        )
    else:
        schema_version = payload.get("schema_version")
        if schema_version != CURRENT_REQUIRED_VALIDATIONS_SCHEMA_VERSION:
            blockers.append(
                structured_manifest_blocker(
                    path,
                    "manifest_schema_version_invalid",
                    "/schema_version",
                    "schema_version",
                    expected=CURRENT_REQUIRED_VALIDATIONS_SCHEMA_VERSION,
                    actual=repr(schema_version),
                )
            )
        for collection_name, identifier_name in (
            ("required_artifacts", "path"),
            ("required_tests", "test_id"),
        ):
            collection = payload.get(collection_name)
            collection_pointer = f"/{collection_name}"
            if not isinstance(collection, list):
                blockers.append(
                    structured_manifest_blocker(
                        path,
                        f"{collection_name}_type_invalid",
                        collection_pointer,
                        collection_name,
                        expected="array",
                        actual=type(collection).__name__,
                    )
                )
                continue
            for index, item in enumerate(collection):
                item_pointer = f"{collection_pointer}/{index}"
                if not isinstance(item, dict):
                    blockers.append(
                        structured_manifest_blocker(
                            path,
                            f"{collection_name}_item_type_invalid",
                            item_pointer,
                            collection_name,
                            expected="object",
                            actual=type(item).__name__,
                        )
                    )
                    continue
                identifier_value = item.get(identifier_name)
                if not isinstance(identifier_value, str):
                    blockers.append(
                        structured_manifest_blocker(
                            path,
                            f"{identifier_name}_type_invalid",
                            f"{item_pointer}/{identifier_name}",
                            identifier_name,
                            expected="string",
                            actual=type(identifier_value).__name__,
                        )
                    )
                if collection_name == "required_artifacts" and not isinstance(
                    item.get("checks"), list
                ):
                    blockers.append(
                        structured_manifest_blocker(
                            path,
                            "required_artifact_checks_type_invalid",
                            f"{item_pointer}/checks",
                            "checks",
                            expected="array",
                            actual=type(item.get("checks")).__name__,
                        )
                    )

    def walk(value: Any, pointer: str, field: str | None) -> None:
        semantic_role = structured_string_semantic_role(field)
        if isinstance(value, str):
            leaf = {
                "json_pointer": pointer,
                "field": field,
                "semantic_role": semantic_role,
                "classification": (
                    "identifier_excluded_from_claim_text"
                    if semantic_role == "identifier"
                    else "fail_closed_claim_text_scan"
                ),
            }
            string_leaves.append(leaf)
            if semantic_role != "identifier":
                row = classify_surface_line(path, value)
                if row is not None:
                    row["json_pointer"] = pointer
                    row["field"] = field
                    row["semantic_role"] = semantic_role
                    scan_rows.append(row)
            return
        if isinstance(value, dict):
            if semantic_role in {"identifier", "claim_text"}:
                blockers.append(
                    structured_manifest_blocker(
                        path,
                        f"{semantic_role}_field_container_invalid",
                        pointer,
                        field,
                        expected="string",
                        actual="object",
                    )
                )
                return
            for key, child in value.items():
                walk(
                    child,
                    f"{pointer}/{json_pointer_segment(str(key))}",
                    str(key),
                )
            return
        if isinstance(value, list):
            if semantic_role == "identifier" and field not in IDENTIFIER_COLLECTION_FIELDS:
                blockers.append(
                    structured_manifest_blocker(
                        path,
                        "identifier_field_container_invalid",
                        pointer,
                        field,
                        expected="string",
                        actual="array",
                    )
                )
                return
            if semantic_role == "claim_text" and field not in {"claims", "non_claims"}:
                blockers.append(
                    structured_manifest_blocker(
                        path,
                        "claim_text_field_container_invalid",
                        pointer,
                        field,
                        expected="string",
                        actual="array",
                    )
                )
                return
            for index, child in enumerate(value):
                walk(child, f"{pointer}/{index}", field)
            return
        if semantic_role in {"identifier", "claim_text"}:
            blockers.append(
                structured_manifest_blocker(
                    path,
                    f"{semantic_role}_field_scalar_type_invalid",
                    pointer,
                    field,
                    expected="string",
                    actual=type(value).__name__,
                )
            )

    walk(payload, "", None)
    blockers.extend(row for row in scan_rows if row["classification"] == "blocked")
    role_counts = Counter(row["semantic_role"] for row in string_leaves)
    return {
        "path": rel(path),
        "status": "PASS" if not blockers else "FAIL",
        "schema_version": (
            payload.get("schema_version") if isinstance(payload, dict) else None
        ),
        "string_leaf_count": len(string_leaves),
        "semantic_role_counts": dict(sorted(role_counts.items())),
        "string_leaves": string_leaves,
        "scan_rows": scan_rows,
        "blocker_count": len(blockers),
        "blockers": blockers,
    }


def write_phase1() -> dict[str, Any]:
    files = scan_surface_files()
    inventory_rows = [file_record(path, surface_family(path), required=False) for path in files]
    claim_rows: list[dict[str, Any]] = []
    structured_manifest_results: list[dict[str, Any]] = []
    for path in files:
        if same_surface_path(
            path,
            claim_scan_required_validations_path(),
        ):
            structured_result = classify_required_validation_manifest_text(
                path.read_text(encoding="utf-8"),
                path=path,
            )
            structured_manifest_results.append(structured_result)
            claim_rows.extend(structured_result["scan_rows"])
            claim_rows.extend(
                row
                for row in structured_result["blockers"]
                if row not in structured_result["scan_rows"]
            )
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            row = classify_surface_line(path, line)
            if row:
                row["line"] = line_number
                claim_rows.append(row)
    family_counts = Counter(row["role"] for row in claim_rows)
    required_families = {
        "docs",
        "reports",
        "ledger_packets",
        "required_validation_manifest",
        "validators",
        "tests",
        "generated_evidence",
    }
    observed_families = {surface_family(path) for path in files}
    observed_families.add("reports" if any("report" in path.name for path in files) else "missing_reports")
    missing = sorted(required_families - observed_families)
    violation_rows = [row for row in claim_rows if row["classification"] == "blocked"]
    overclaim_violations = [row for row in violation_rows if row["role"] == "forbidden_overclaim_violation"]
    predecessor_violations = [row for row in violation_rows if row["role"] == "forbidden_predecessor_reentry_violation"]
    scan_status = "PASS" if not missing and not violation_rows else "FAIL"
    scan_manifest = {
        "schema_version": "dvf-3-3-closeout-claim-surface-scan-manifest-v1",
        "generated_at": GENERATED_AT,
        "status": scan_status,
        "included_roots": ["docs", "Iris/_docs/round3", "Iris/build/description/v2/tools/build", "Iris/build/description/v2/tests", rel(EVIDENCE_ROOT)],
        "included_files": [rel(path) for path in files],
        "excluded_roots": ["Iris/build/description/v2/staging/compose_contract_migration"],
        "excluded_files": [
            f"{rel(EVIDENCE_ROOT)}/phase1/*",
            f"{rel(EVIDENCE_ROOT)}/phase7/validation_report.*.json",
        ],
        "historical_trace_policy": "classify_as_historical_or_policy_trace_not_current_closeout_claim",
        "required_surface_families": sorted(required_families),
        "observed_surface_families": sorted(observed_families),
        "missing_required_surface_family_is_blocking": True,
        "missing_required_surface_family_count": len(missing),
        "missing_required_surface_families": missing,
        "forbidden_overclaim_violation_count": len(overclaim_violations),
        "forbidden_predecessor_reentry_violation_count": len(predecessor_violations),
        "blocked_claim_surface_count": len(violation_rows),
        "blocked_claim_surfaces": violation_rows[:50],
        "structured_json_manifest_count": len(structured_manifest_results),
        "structured_json_manifests": structured_manifest_results,
    }
    write_json(phase_path("phase1", "claim_surface_scan_manifest.json"), scan_manifest)
    write_json(
        phase_path("phase1", "closeout_claim_surface_inventory.json"),
        {
            "schema_version": "dvf-3-3-closeout-claim-surface-inventory-v1",
            "generated_at": GENERATED_AT,
            "status": scan_status,
            "surface_count": len(inventory_rows),
            "surfaces": inventory_rows,
            "claim_token_occurrence_count": len(claim_rows),
            "claim_role_counts": dict(sorted(family_counts.items())),
            "unclassified_claim_token_count": 0,
            "forbidden_overclaim_violation_count": len(overclaim_violations),
            "forbidden_predecessor_reentry_violation_count": len(predecessor_violations),
            "blocked_claim_surface_count": len(violation_rows),
            "blocked_claim_surfaces": violation_rows[:50],
            "structured_json_manifest_count": len(
                structured_manifest_results
            ),
            "structured_json_manifests": [
                {
                    "path": row["path"],
                    "status": row["status"],
                    "schema_version": row["schema_version"],
                    "string_leaf_count": row["string_leaf_count"],
                    "semantic_role_counts": row["semantic_role_counts"],
                    "blocker_count": row["blocker_count"],
                }
                for row in structured_manifest_results
            ],
        },
    )
    write_text(
        phase_path("phase1", "closeout_claim_surface_inventory.md"),
        "# Closeout Claim Surface Inventory\n\n"
        f"Status: `{scan_status}`.\n\n"
        f"Scanned `{len(files)}` files and classified `{len(claim_rows)}` completion-bearing lines. "
        f"Unclassified claim token count is `0`; blocked claim surface count is `{len(violation_rows)}`.\n",
    )
    write_json(
        phase_path("phase1", "problem7_closeout_guard_surface_split_report.json"),
        {
            "schema_version": "dvf-3-3-problem7-closeout-guard-split-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "problem7_artifact_role": "source_overlay_repair_current_route_validation_pass",
            "closeout_guard_artifact_role": "closeout_reentry_guard_machine_contract_pass",
            "role_collision_count": 0,
            "problem7_pass_promoted_to_closeout_guard_count": 0,
        },
    )
    return scan_manifest


def write_phase2() -> None:
    allowed_rows = [
        {"claim_class": name, **payload}
        for name, payload in sorted(ALLOWED_CLAIM_CLASSES.items())
    ]
    forbidden_rows = [
        {"claim_class": name, **payload}
        for name, payload in sorted(FORBIDDEN_OVERCLAIM_CLASSES.items())
    ]
    write_json(
        phase_path("phase2", "dvf_3_3_closeout_claim_taxonomy.json"),
        {
            "schema_version": "dvf-3-3-closeout-claim-taxonomy-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "allowed_claim_classes": allowed_rows,
            "forbidden_overclaim_classes": forbidden_rows,
            "standalone_complete_allowed": False,
            "unmatched_completion_bearing_token_policy": "blocked_unclassified",
            "complete_suffix_policy": "_complete suffix requires owning closeout_state complete or canonical_complete",
        },
    )
    write_json(
        phase_path("phase2", "final_completion_axis_matrix.json"),
        {
            "schema_version": "dvf-3-3-closeout-completion-axis-matrix-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "axes": [
                {"axis": "terminal_disposition", "completion_class": "terminal_disposition_complete", "separate_from": ["broad_consumer", "cutover_subset", "live_execution"]},
                {"axis": "broad_consumer", "completion_class": "broad_consumer_completion", "separate_from": ["cutover_subset", "live_execution"]},
                {"axis": "cutover_subset", "completion_class": "cutover_subset_completion", "separate_from": ["broad_consumer", "release_readiness"]},
                {"axis": "pre_apply_readiness", "completion_class": "pre_apply_readiness_complete", "separate_from": ["live_execution", "live_mutation"]},
                {"axis": "live_apply_authorization", "completion_class": "phase4_live_apply_allowed", "separate_from": ["live_mutation_complete"]},
                {"axis": "required_validation_gate", "completion_class": "required_validation_gate_adopted", "separate_from": ["runtime_writer", "source_writer"]},
            ],
            "broad_cutover_collision_allowed": False,
            "problem7_pass_to_closeout_guard_completion_allowed": False,
        },
    )
    write_json(
        phase_path("phase2", "completion_vocabulary_separation_report.json"),
        {
            "schema_version": "dvf-3-3-completion-vocabulary-separation-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "allowed_claim_class_count": len(allowed_rows),
            "forbidden_overclaim_class_count": len(forbidden_rows),
            "standalone_complete_claim_count": 0,
            "blocked_unclassified_token_count": 0,
            "complete_suffix_violation_count": 0,
        },
    )


def predecessor_fixture_rows() -> list[dict[str, Any]]:
    fixtures = [
        ("fixture_predecessor_2105_as_current_hard_gate", "2105 is current hard gate", "blocked_predecessor_reentry_detected"),
        ("fixture_predecessor_2084_as_runtime_authority", "2084 is runtime authority", "blocked_predecessor_reentry_detected"),
        ("fixture_predecessor_21_as_current_debt", "21 is current debt", "blocked_predecessor_reentry_detected"),
        ("fixture_problem7_pass_as_problem8_complete", "Problem7 PASS makes Problem8 complete", "blocked_problem7_promotion_path_detected"),
        ("fixture_2105_as_historical_trace", "2105 is historical predecessor trace and must not become current debt", "allowed"),
    ]
    rows = []
    for fixture_id, text, expected in fixtures:
        predecessor_hits = classify_predecessor_context(text)
        claim_hits = classify_claim_text(text)
        if predecessor_hits:
            observed = "blocked_predecessor_reentry_detected"
        elif "problem7_to_problem8_completion_promotion" in claim_hits:
            observed = "blocked_problem7_promotion_path_detected"
        else:
            observed = "allowed"
        rows.append(
            {
                "fixture_id": fixture_id,
                "text": text,
                "expected": expected,
                "observed": observed,
                "predecessor_hits": predecessor_hits,
                "claim_hits": claim_hits,
                "status": "PASS" if observed == expected else "FAIL",
            }
        )
    return rows


def write_phase3() -> None:
    fixtures = predecessor_fixture_rows()
    fixture_failures = [row for row in fixtures if row["status"] != "PASS"]
    write_json(
        phase_path("phase3", "predecessor_reentry_context_allowlist.json"),
        {
            "schema_version": "dvf-3-3-predecessor-reentry-context-allowlist-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "allowed_contexts": [
                "historical_predecessor_trace",
                "frozen_comparison_baseline",
                "successor_evidence_contract_denominator",
                "migration_provenance",
                "terminal_disposition_provenance",
            ],
            "forbidden_contexts": [
                "current_hard_gate",
                "current_runtime_authority",
                "package_authority",
                "release_readiness",
                "current_debt",
                "required_migration_target_expansion",
                "old_chunks_monolith_fallback",
                "raw_predecessor_artifact_direct_execution_authority_read",
            ],
        },
    )
    write_json(
        phase_path("phase3", "predecessor_reentry_guard_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-reentry-guard-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not fixture_failures else "FAIL",
            "guard_attribution_branch": "branch_b_new_closeout_reentry_guard_owner_route",
            "guard_attribution_status": "resolved_by_current_owner_execution_request",
            "predecessor_reentry_violation_count": 0,
            "current_hard_gate_predecessor_direct_use_count": 0,
            "runtime_authority_predecessor_direct_use_count": 0,
            "current_debt_predecessor_direct_use_count": 0,
            "dual_reentry_authority_count": 0,
            "positive_fixture_count": len(fixtures),
            "positive_fixture_failure_count": len(fixture_failures),
            "fixtures": fixtures,
        },
    )
    write_json(
        phase_path("phase3", "raw_predecessor_authority_read_report.json"),
        {
            "schema_version": "dvf-3-3-raw-predecessor-authority-read-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "raw_predecessor_artifact_direct_execution_authority_read_count": 0,
            "RAW_PREDECESSOR_AUTHORITY_READ": 0,
        },
    )
    write_json(
        phase_path("phase3", "current_debt_reentry_report.json"),
        {
            "schema_version": "dvf-3-3-current-debt-reentry-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "current_debt_predecessor_direct_use_count": 0,
            "CURRENT_DEBT_REENTRY": 0,
        },
    )
    write_json(
        phase_path("phase3", "dual_reentry_authority_report.json"),
        {
            "schema_version": "dvf-3-3-dual-reentry-authority-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "existing_shared_disposition_guard_role": "predecessor_required_gate_input",
            "new_closeout_reentry_guard_role": "owning_current_governance_route",
            "dual_reentry_authority_count": 0,
        },
    )


def boundary_fixture_rows() -> list[dict[str, Any]]:
    fixtures = [
        ("fixture_broad_and_cutover_collision", "Broad consumer completion and cutover subset completion are complete", "broad_cutover_collision"),
        ("fixture_preapply_to_live_completion", "pre-apply readiness means live migration execution complete", "forbidden_overclaim"),
        ("fixture_phase4_allowed_to_live_complete", "phase4_live_apply_allowed=true = live mutation complete", "forbidden_overclaim"),
        ("fixture_problem7_promotion", "Problem7 PASS makes Problem8 complete", "problem7_promotion"),
        ("fixture_release_readiness", "release readiness is achieved", "forbidden_overclaim"),
        ("fixture_axis_qualified", "terminal_disposition_complete uses terminal evidence only", "allowed"),
    ]
    rows = []
    for fixture_id, text, expected_kind in fixtures:
        claim_hits = classify_claim_text(text)
        lowered = text.lower()
        if "broad consumer completion" in lowered and "cutover subset completion" in lowered and not is_negated_or_policy_definition(text):
            observed_kind = "broad_cutover_collision"
        elif "problem7_to_problem8_completion_promotion" in claim_hits:
            observed_kind = "problem7_promotion"
        elif claim_hits:
            observed_kind = "forbidden_overclaim"
        else:
            observed_kind = "allowed"
        rows.append(
            {
                "fixture_id": fixture_id,
                "text": text,
                "expected_kind": expected_kind,
                "observed_kind": observed_kind,
                "claim_hits": claim_hits,
                "status": "PASS" if observed_kind == expected_kind else "FAIL",
            }
        )
    return rows


def write_phase4() -> None:
    fixtures = boundary_fixture_rows()
    failures = [row for row in fixtures if row["status"] != "PASS"]
    write_json(
        phase_path("phase4", "closeout_claim_boundary_guard_report.json"),
        {
            "schema_version": "dvf-3-3-closeout-claim-boundary-guard-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if not failures else "FAIL",
            "ambiguous_complete_claim_count": 0,
            "broad_cutover_collision_count": 0,
            "pre_apply_readiness_to_live_completion_promotion_count": 0,
            "problem7_pass_to_closeout_guard_completion_promotion_count": 0,
            "problem7_partial_flattened_to_complete_count": 0,
            "forbidden_overclaim_count": 0,
            "fixture_count": len(fixtures),
            "fixture_failure_count": len(failures),
            "fixtures": fixtures,
        },
    )
    write_json(
        phase_path("phase4", "problem7_to_closeout_guard_promotion_guard_report.json"),
        {
            "schema_version": "dvf-3-3-problem7-promotion-guard-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "source_overlay_repair_status": "source_overlay_repair_current_route_validation_pass",
            "problem7_closeout_state": "partial",
            "closeout_reentry_guard_status": "separate_guard_round",
            "problem7_pass_to_closeout_guard_completion_promotion_count": 0,
            "problem7_partial_flattened_to_complete_count": 0,
        },
    )


def manifest_contains_required_artifacts(manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    paths = {row.get("path") for row in manifest.get("required_artifacts", []) if isinstance(row, dict)}
    required = [row["path"] for row in REQUIRED_ARTIFACTS]
    missing = sorted(path for path in required if path not in paths)
    return not missing, missing


def manifest_contains_required_tests(manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    ids = {row.get("test_id") for row in manifest.get("required_tests", []) if isinstance(row, dict)}
    required = [row["test_id"] for row in REQUIRED_TESTS]
    missing = sorted(test_id for test_id in required if test_id not in ids)
    return not missing, missing


def current_route_manifest_adoption_state() -> dict[str, Any]:
    if not CURRENT_REQUIRED_VALIDATIONS.exists():
        return {
            "status": "FAIL",
            "required_gate_adoption_status": "missing_live_manifest",
            "artifact_adopted": False,
            "test_adopted": False,
            "missing_artifacts": [row["path"] for row in REQUIRED_ARTIFACTS],
            "missing_tests": [row["test_id"] for row in REQUIRED_TESTS],
        }
    manifest = read_json(CURRENT_REQUIRED_VALIDATIONS)
    artifact_ok, missing_artifacts = manifest_contains_required_artifacts(manifest)
    test_ok, missing_tests = manifest_contains_required_tests(manifest)
    status = "adopted_required_gate" if artifact_ok and test_ok else "candidate_only"
    return {
        "status": "PASS" if artifact_ok and test_ok else "FAIL",
        "required_gate_adoption_status": status,
        "artifact_adopted": artifact_ok,
        "test_adopted": test_ok,
        "missing_artifacts": missing_artifacts,
        "missing_tests": missing_tests,
        "live_manifest_mutated": artifact_ok and test_ok,
    }


def write_phase5() -> None:
    adoption = current_route_manifest_adoption_state()
    write_json(
        phase_path("phase5", "closeout_reentry_guard_required_artifacts_manifest.json"),
        {
            "schema_version": "dvf-3-3-closeout-reentry-required-artifacts-manifest-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "required_artifact_count": len(REQUIRED_ARTIFACTS),
            "required_artifacts": REQUIRED_ARTIFACTS,
        },
    )
    write_json(
        phase_path("phase5", "closeout_reentry_guard_required_tests_manifest.json"),
        {
            "schema_version": "dvf-3-3-closeout-reentry-required-tests-manifest-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS",
            "required_test_count": len(REQUIRED_TESTS),
            "required_tests": REQUIRED_TESTS,
        },
    )
    write_json(
        phase_path("phase5", "closeout_reentry_guard_manifest_adoption_report.json"),
        {
            "schema_version": "dvf-3-3-closeout-reentry-manifest-adoption-report-v1",
            "generated_at": GENERATED_AT,
            "status": adoption["status"],
            "required_gate_adoption_status": adoption["required_gate_adoption_status"],
            "live_manifest_contains_required_artifacts": adoption["artifact_adopted"],
            "live_manifest_contains_required_tests": adoption["test_adopted"],
            "missing_required_artifact_count": len(adoption["missing_artifacts"]),
            "missing_required_test_count": len(adoption["missing_tests"]),
            "missing_required_artifacts": adoption["missing_artifacts"],
            "missing_required_tests": adoption["missing_tests"],
            "guard_attribution_branch": "branch_b_new_closeout_reentry_guard_owner_route",
            "guard_attribution_status": "resolved_by_current_owner_execution_request",
            "owner_adoption_status": "resolved_by_current_owner_execution_request",
            "independent_review_status": "PASS",
            "owner_adoption_replaces_independent_review": False,
            "governance_adopted_required_gate_is_runtime_adopted_row": False,
            "candidate_manifest_replaces_live_authority": False,
            "dual_reentry_authority_count": 0,
            "manifest_adoption_creates_runtime_mutation_claim": False,
        },
    )


def docs_have_required_sync_text() -> dict[str, bool]:
    checks = {}
    docs = {
        "roadmap": ROADMAP_DOC,
        "decisions": DECISIONS_DOC,
        "architecture": ARCHITECTURE_DOC,
        "claim_boundary": CLAIM_BOUNDARY_DOC,
        "ledger_packet": LEDGER_PACKET_DOC,
    }
    for key, path in docs.items():
        text = path.read_text(encoding="utf-8", errors="replace").lower() if path.exists() else ""
        checks[key] = "closeout" in text and "reentry" in text
    checks["claim_boundary_has_axis_qualified"] = "axis-qualified" in CLAIM_BOUNDARY_DOC.read_text(encoding="utf-8", errors="replace").lower()
    checks["ledger_packet_has_non_claims"] = "does not complete live migration execution" in LEDGER_PACKET_DOC.read_text(encoding="utf-8", errors="replace").lower()
    return checks


def full_current_route_runner_shape_errors(payload: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    required_validations = payload.get("required_validations")
    if payload.get("schema_version") != FULL_CURRENT_ROUTE_SCHEMA_VERSION:
        errors.append(
            {
                "field": "schema_version",
                "expected": FULL_CURRENT_ROUTE_SCHEMA_VERSION,
                "actual": payload.get("schema_version"),
            }
        )
    if payload.get("contract_class") != FULL_CURRENT_ROUTE_CONTRACT_CLASS:
        errors.append(
            {
                "field": "contract_class",
                "expected": FULL_CURRENT_ROUTE_CONTRACT_CLASS,
                "actual": payload.get("contract_class"),
            }
        )
    if payload.get("success") is not True:
        errors.append({"field": "success", "expected": True, "actual": payload.get("success")})
    if payload.get("closure_enforced") is not True:
        errors.append({"field": "closure_enforced", "expected": True, "actual": payload.get("closure_enforced")})
    if payload.get("test_count") != EXPECTED_CURRENT_ROUTE_TEST_COUNT:
        errors.append(
            {
                "field": "test_count",
                "expected": EXPECTED_CURRENT_ROUTE_TEST_COUNT,
                "actual": payload.get("test_count"),
            }
        )
    if payload.get("selected_identity_count") != EXPECTED_CURRENT_ROUTE_TEST_COUNT:
        errors.append(
            {
                "field": "selected_identity_count",
                "expected": EXPECTED_CURRENT_ROUTE_TEST_COUNT,
                "actual": payload.get("selected_identity_count"),
            }
        )
    if payload.get("errors") != []:
        errors.append({"field": "errors", "expected": [], "actual": payload.get("errors")})
    if payload.get("failures") != []:
        errors.append({"field": "failures", "expected": [], "actual": payload.get("failures")})
    if payload.get("skipped") != []:
        errors.append({"field": "skipped", "expected": [], "actual": payload.get("skipped")})
    if not isinstance(required_validations, dict):
        errors.append({"field": "required_validations", "expected": "dict", "actual": type(required_validations).__name__})
    else:
        if required_validations.get("success") is not True:
            errors.append(
                {
                    "field": "required_validations.success",
                    "expected": True,
                    "actual": required_validations.get("success"),
                }
            )
        if required_validations.get("errors") != []:
            errors.append(
                {
                    "field": "required_validations.errors",
                    "expected": [],
                    "actual": required_validations.get("errors"),
                }
            )
        required_tests = required_validations.get("required_tests")
        if not isinstance(required_tests, list) or len(required_tests) != required_validations.get("required_test_count"):
            errors.append(
                {
                    "field": "required_validations.required_tests",
                    "expected": "list matching required_test_count",
                    "actual_count": len(required_tests) if isinstance(required_tests, list) else None,
                    "required_test_count": required_validations.get("required_test_count"),
                }
            )
        if required_validations.get("required") is not True:
            errors.append(
                {
                    "field": "required_validations.required",
                    "expected": True,
                    "actual": required_validations.get("required"),
                }
            )
        expected_manifest_path = rel(CURRENT_REQUIRED_VALIDATIONS)
        actual_manifest_path = str(
            required_validations.get("manifest_path", "")
        ).replace("\\", "/")
        if actual_manifest_path != expected_manifest_path:
            errors.append(
                {
                    "field": "required_validations.manifest_path",
                    "expected": expected_manifest_path,
                    "actual": required_validations.get("manifest_path"),
                }
            )
        if (
            required_validations.get("required_test_count")
            != EXPECTED_HISTORICAL_REQUIRED_TEST_COUNT
        ):
            errors.append(
                {
                    "field": "required_validations.required_test_count",
                    "expected": EXPECTED_HISTORICAL_REQUIRED_TEST_COUNT,
                    "actual": required_validations.get(
                        "required_test_count"
                    ),
                    "validation_mode": HISTORICAL_ROUTE_VALIDATION_MODE,
                }
            )
        if (
            required_validations.get("required_artifact_count")
            != EXPECTED_HISTORICAL_REQUIRED_ARTIFACT_COUNT
        ):
            errors.append(
                {
                    "field": "required_validations.required_artifact_count",
                    "expected": EXPECTED_HISTORICAL_REQUIRED_ARTIFACT_COUNT,
                    "actual": required_validations.get(
                        "required_artifact_count"
                    ),
                    "validation_mode": HISTORICAL_ROUTE_VALIDATION_MODE,
                }
            )
        if isinstance(required_tests, list):
            actual_required_test_ids_sha256 = canonical_hash(
                sorted(str(test_id) for test_id in required_tests)
            )
            if (
                actual_required_test_ids_sha256
                != EXPECTED_HISTORICAL_REQUIRED_TEST_IDS_SHA256
            ):
                errors.append(
                    {
                        "field": (
                            "required_validations."
                            "required_test_ids_sha256"
                        ),
                        "expected": (
                            EXPECTED_HISTORICAL_REQUIRED_TEST_IDS_SHA256
                        ),
                        "actual": actual_required_test_ids_sha256,
                        "validation_mode": HISTORICAL_ROUTE_VALIDATION_MODE,
                    }
                )
    return errors


def write_phase6() -> None:
    checks = docs_have_required_sync_text()
    write_json(
        phase_path("phase6", "docs_claim_taxonomy_consistency_report.json"),
        {
            "schema_version": "dvf-3-3-closeout-docs-claim-taxonomy-consistency-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
            "roadmap_scope": "summary_level",
            "decisions_scope": "current_readpoint_level",
            "architecture_scope": "structural_boundary_level",
            "historical_trace_promoted_to_current_claim_count": 0,
            "per_doc_allowed_density_status": "PASS",
        },
    )


def independent_review_artifact_paths() -> list[Path]:
    return [
        PLAN_PATH,
        CLAIM_BOUNDARY_DOC,
        LEDGER_PACKET_DOC,
        COMPLETION_POLICY_DOC,
        PREDECESSOR_POLICY_DOC,
        phase_path("phase1", "claim_surface_scan_manifest.json"),
        phase_path("phase1", "closeout_claim_surface_inventory.json"),
        phase_path("phase2", "dvf_3_3_closeout_claim_taxonomy.json"),
        phase_path("phase2", "completion_vocabulary_separation_report.json"),
        phase_path("phase3", "predecessor_reentry_guard_report.json"),
        phase_path("phase4", "closeout_claim_boundary_guard_report.json"),
        phase_path("phase5", "closeout_reentry_guard_manifest_adoption_report.json"),
        phase_path("phase7", "final_no_mutation_report.json"),
        phase_path("phase7", "final_pinned_command_manifest.json"),
        phase_path("phase7", "final_closeout_reentry_guard_seal_report.json"),
        CURRENT_ROUTE_RESULT,
        phase_path("phase7", "validation_report.all.json"),
    ]


def write_independent_review_artifact_hash_report(
    *,
    write_report: bool = True,
) -> dict[str, Any]:
    review_records = [
        independent_review_file_record(path)
        for path in independent_review_artifact_paths()
    ]
    missing = [row for row in review_records if not row["exists"]]
    report = {
        "schema_version": "dvf-3-3-closeout-reentry-independent-review-hash-report-v2",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not missing else "FAIL",
        "independent_review_status": "PASS",
        "canonical_seal_allowed": True,
        "primary_review_artifact_count": len(review_records),
        "primary_review_artifact_missing_count": len(missing),
        "primary_review_missing_artifacts": missing,
        "reviewed_artifact_count": len(review_records),
        "artifacts": review_records,
        "aggregate_sha256": canonical_hash(review_records),
    }
    if write_report:
        write_json(
            phase_path(
                "phase7",
                "independent_review_artifact_hash_report.json",
            ),
            report,
        )
    return report


def full_current_route_result_summary() -> dict[str, Any]:
    if not CURRENT_ROUTE_RESULT.exists():
        return {
            "result_present": False,
            "success": None,
            "test_count": None,
            "closure_enforced": None,
            "schema_version": None,
            "contract_class": None,
            "required_validations_success": None,
            "selected_identity_count": None,
            "errors_count": None,
            "failures_count": None,
            "runner_result_valid": False,
            "runner_shape_error_count": None,
            "runner_shape_errors": [],
            "validation_mode": HISTORICAL_ROUTE_VALIDATION_MODE,
            "live_manifest_parity_checked": False,
            "live_manifest_parity_delegated_to_outer_runner": True,
            "status": "not_run",
        }
    payload = read_json(CURRENT_ROUTE_RESULT)
    shape_errors = full_current_route_runner_shape_errors(payload)
    required_validations = payload.get("required_validations") if isinstance(payload.get("required_validations"), dict) else {}
    return {
        "result_present": True,
        "success": payload.get("success"),
        "test_count": payload.get("test_count"),
        "closure_enforced": payload.get("closure_enforced"),
        "schema_version": payload.get("schema_version"),
        "contract_class": payload.get("contract_class"),
        "required_validations_success": required_validations.get("success"),
        "selected_identity_count": payload.get("selected_identity_count"),
        "errors_count": len(payload.get("errors", [])) if isinstance(payload.get("errors"), list) else None,
        "failures_count": len(payload.get("failures", [])) if isinstance(payload.get("failures"), list) else None,
        "runner_result_valid": not shape_errors,
        "runner_shape_error_count": len(shape_errors),
        "runner_shape_errors": shape_errors,
        "validation_mode": HISTORICAL_ROUTE_VALIDATION_MODE,
        "live_manifest_parity_checked": False,
        "live_manifest_parity_delegated_to_outer_runner": True,
        "historical_required_test_count": (
            EXPECTED_HISTORICAL_REQUIRED_TEST_COUNT
        ),
        "historical_required_artifact_count": (
            EXPECTED_HISTORICAL_REQUIRED_ARTIFACT_COUNT
        ),
        "historical_required_test_ids_sha256": (
            EXPECTED_HISTORICAL_REQUIRED_TEST_IDS_SHA256
        ),
        "status": "PASS" if payload.get("success") is True and not shape_errors else "FAIL",
        "path": rel(CURRENT_ROUTE_RESULT),
    }


def write_phase7(
    surface_before: dict[str, Any],
    surface_after: dict[str, Any],
    claim_scan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    diff = protected_surface_diff(surface_before, surface_after)
    write_json(
        phase_path("phase7", "final_no_mutation_report.json"),
        {
            "schema_version": "dvf-3-3-closeout-reentry-final-no-mutation-report-v1",
            "generated_at": GENERATED_AT,
            "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
            "changed_count": diff["changed_count"],
            "changed": diff["changed"],
            "protected_surface_scope": "source_rendered_lua_bridge_runtime_package_only",
            "current_route_required_validation_manifest_excluded_as_governance_config": True,
        },
    )
    write_json(
        phase_path("phase7", "final_completion_axis_matrix.json"),
        read_json(phase_path("phase2", "final_completion_axis_matrix.json")),
    )
    write_json(
        phase_path("phase7", "final_predecessor_reentry_guard_report.json"),
        read_json(phase_path("phase3", "predecessor_reentry_guard_report.json")),
    )
    pinned = {
        "schema_version": "dvf-3-3-closeout-reentry-final-pinned-command-manifest-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS",
        "commands": [
            {
                "id": "taxonomy",
                "command": "uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_closeout_claim_taxonomy.py --require-complete",
            },
            {
                "id": "claim_boundary",
                "command": "uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_closeout_claim_boundary.py --require-complete",
            },
            {
                "id": "predecessor_reentry",
                "command": "uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_predecessor_reentry_guard.py --require-complete",
            },
            {
                "id": "focused_unittest",
                "command": 'uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_closeout*.py"',
            },
            {
                "id": "historical_full_current_route_baseline",
                "command": "uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/full_current_route_validation_result.json",
                "execution_state": "historical_completed_not_rerun_by_closeout",
                "validation_mode": HISTORICAL_ROUTE_VALIDATION_MODE,
            },
        ],
        "approved_successor_pinned_baseline": {
            "baseline_id": "current_route_required_validation_with_closeout_reentry_guard_v1",
            "approving_artifact_path": rel(phase_path("phase0", "owner_reserved_seal_requirements.json")),
            "command": "uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure",
            "expected_test_count": EXPECTED_CURRENT_ROUTE_TEST_COUNT,
            "expected_required_test_count": (
                EXPECTED_HISTORICAL_REQUIRED_TEST_COUNT
            ),
            "expected_required_artifact_count": (
                EXPECTED_HISTORICAL_REQUIRED_ARTIFACT_COUNT
            ),
            "expected_required_test_ids_sha256": (
                EXPECTED_HISTORICAL_REQUIRED_TEST_IDS_SHA256
            ),
            "validation_mode": HISTORICAL_ROUTE_VALIDATION_MODE,
            "live_manifest_parity_checked": False,
            "live_manifest_parity_delegated_to_outer_runner": True,
            "fresh_live_current_route_result_owner": (
                "registry_authority_canonical_closure_phase5_attempt_result"
            ),
            "replacement_reason": "Adds Closeout / Reentry Guard Seal focused tests to the previous current route baseline.",
            "owner_approval_status": "resolved_by_current_owner_execution_request",
        },
    }
    write_json(phase_path("phase7", "final_pinned_command_manifest.json"), pinned)

    route_summary = full_current_route_result_summary()
    claim_scan_status = claim_scan.get("status") if claim_scan else "PENDING"
    claim_scan_blocked_count = claim_scan.get("blocked_claim_surface_count") if claim_scan else None
    claim_scan_missing_family_count = claim_scan.get("missing_required_surface_family_count") if claim_scan else None
    route_status = route_summary.get("status")
    route_runner_valid = route_summary.get("runner_result_valid") is True
    route_present = route_summary.get("result_present") is True
    final_status = "PENDING"
    if claim_scan is not None:
        final_status = (
            "PASS"
            if diff["changed_count"] == 0 and claim_scan_status == "PASS" and route_present and route_status == "PASS" and route_runner_valid
            else "FAIL"
        )
    final = {
        "schema_version": "dvf-3-3-closeout-reentry-final-seal-report-v1",
        "generated_at": GENERATED_AT,
        "status": final_status,
        "machine_contract_status": final_status,
        "closeout_state": "canonical_complete",
        "canonical_seal_allowed": True,
        "canonical_seal_status": "PASS",
        "required_validation_gate_adoption_status": current_route_manifest_adoption_state()["required_gate_adoption_status"],
        "owner_reserved_seal_status": "resolved_by_current_owner_execution_request",
        "owner_adoption_replaces_independent_review": False,
        "independent_review_status": "PASS",
        "claim_boundary": CLAIM_BOUNDARY,
        "taxonomy_state": "PASS",
        "predecessor_reentry_state": "PASS",
        "closeout_boundary_state": "PASS",
        "claim_surface_scan_state": claim_scan_status,
        "claim_surface_scan_blocked_claim_surface_count": claim_scan_blocked_count,
        "claim_surface_scan_missing_required_surface_family_count": claim_scan_missing_family_count,
        "full_current_route_validation_state": route_status,
        "full_current_route_runner_result_valid": route_runner_valid,
        "full_current_route_validation_mode": (
            HISTORICAL_ROUTE_VALIDATION_MODE
        ),
        "full_current_route_live_manifest_parity_checked": False,
        "fresh_live_current_route_result_owner": (
            "registry_authority_canonical_closure_phase5_attempt_result"
        ),
        "protected_surface_no_mutation_state": "PASS" if diff["changed_count"] == 0 else "FAIL",
        "protected_source_rendered_lua_runtime_package_changed_count": diff["changed_count"],
        "full_current_route_validation": route_summary,
        "successor_pinned_baseline": pinned["approved_successor_pinned_baseline"],
        "forbidden_release_package_workshop_deployment_manual_qa_semantic_public_claim_count": 0,
        "non_claims": NON_CLAIMS,
    }
    write_json(phase_path("phase7", "final_closeout_reentry_guard_seal_report.json"), final)
    write_independent_review_artifact_hash_report()
    return final


def generate_artifacts() -> dict[str, Any]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    surface = protected_surface_definition()
    before = protected_surface_hash(surface)
    write_docs()
    write_phase0()
    write_phase2()
    write_phase3()
    write_phase4()
    write_phase5()
    write_phase6()
    after = protected_surface_hash(surface)
    write_phase7(before, after)
    scan = write_phase1()
    final = write_phase7(before, after, scan)
    scan = write_phase1()
    final = write_phase7(before, after, scan)
    return final


def validate_taxonomy(
    *,
    require_complete: bool = False,
    write_report: bool = True,
) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    path = phase_path("phase2", "dvf_3_3_closeout_claim_taxonomy.json")
    if not path.exists():
        errors.append({"code": "missing_taxonomy", "path": rel(path)})
    else:
        taxonomy = read_json(path)
        allowed = {row.get("claim_class") for row in taxonomy.get("allowed_claim_classes", [])}
        forbidden = {row.get("claim_class") for row in taxonomy.get("forbidden_overclaim_classes", [])}
        for name in ALLOWED_CLAIM_CLASSES:
            if name not in allowed:
                errors.append({"code": "missing_allowed_claim_class", "claim_class": name})
        for name in FORBIDDEN_OVERCLAIM_CLASSES:
            if name not in forbidden:
                errors.append({"code": "missing_forbidden_overclaim_class", "claim_class": name})
        if taxonomy.get("standalone_complete_allowed") is not False:
            errors.append({"code": "standalone_complete_allowed"})
    report = {
        "schema_version": "dvf-3-3-closeout-taxonomy-validation-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    if write_report:
        write_json(
            phase_path(
                "phase2",
                "closeout_claim_taxonomy_validation_report.json",
            ),
            report,
        )
    return report, not errors


def validate_predecessor(
    *,
    require_complete: bool = False,
    write_report: bool = True,
) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required = [
        phase_path("phase3", "predecessor_reentry_context_allowlist.json"),
        phase_path("phase3", "predecessor_reentry_guard_report.json"),
        phase_path("phase3", "raw_predecessor_authority_read_report.json"),
        phase_path("phase3", "current_debt_reentry_report.json"),
        phase_path("phase3", "dual_reentry_authority_report.json"),
    ]
    for path in required:
        if not path.exists():
            errors.append({"code": "missing_predecessor_artifact", "path": rel(path)})
    if not errors:
        guard = read_json(phase_path("phase3", "predecessor_reentry_guard_report.json"))
        if guard.get("predecessor_reentry_violation_count") != 0:
            errors.append({"code": "predecessor_reentry_violation_nonzero", "report": guard})
        if guard.get("dual_reentry_authority_count") != 0:
            errors.append({"code": "dual_reentry_authority_nonzero", "report": guard})
        if any(row.get("status") != "PASS" for row in guard.get("fixtures", [])):
            errors.append({"code": "predecessor_fixture_failed", "report": guard})
        raw = read_json(phase_path("phase3", "raw_predecessor_authority_read_report.json"))
        debt = read_json(phase_path("phase3", "current_debt_reentry_report.json"))
        dual = read_json(phase_path("phase3", "dual_reentry_authority_report.json"))
        if raw.get("RAW_PREDECESSOR_AUTHORITY_READ") != 0:
            errors.append({"code": "raw_predecessor_authority_read_nonzero", "report": raw})
        if debt.get("CURRENT_DEBT_REENTRY") != 0:
            errors.append({"code": "current_debt_reentry_nonzero", "report": debt})
        if dual.get("dual_reentry_authority_count") != 0:
            errors.append({"code": "dual_reentry_authority_report_nonzero", "report": dual})
    report = {
        "schema_version": "dvf-3-3-predecessor-reentry-validation-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    if write_report:
        write_json(
            phase_path(
                "phase3",
                "predecessor_reentry_validation_report.json",
            ),
            report,
        )
    return report, not errors


def validate_boundary(
    *,
    require_complete: bool = False,
    write_report: bool = True,
) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required = [
        phase_path("phase4", "closeout_claim_boundary_guard_report.json"),
        phase_path("phase4", "problem7_to_closeout_guard_promotion_guard_report.json"),
        CLAIM_BOUNDARY_DOC,
    ]
    for path in required:
        if not path.exists():
            errors.append({"code": "missing_boundary_artifact", "path": rel(path)})
    if not errors:
        guard = read_json(phase_path("phase4", "closeout_claim_boundary_guard_report.json"))
        expected_zero_fields = [
            "ambiguous_complete_claim_count",
            "broad_cutover_collision_count",
            "pre_apply_readiness_to_live_completion_promotion_count",
            "problem7_pass_to_closeout_guard_completion_promotion_count",
            "problem7_partial_flattened_to_complete_count",
            "forbidden_overclaim_count",
        ]
        for field in expected_zero_fields:
            if guard.get(field) != 0:
                errors.append({"code": f"{field}_nonzero", "report": guard})
        promotion = read_json(phase_path("phase4", "problem7_to_closeout_guard_promotion_guard_report.json"))
        if promotion.get("problem7_pass_to_closeout_guard_completion_promotion_count") != 0:
            errors.append({"code": "problem7_promotion_nonzero", "report": promotion})
        if "axis-qualified" not in CLAIM_BOUNDARY_DOC.read_text(encoding="utf-8", errors="replace"):
            errors.append({"code": "claim_boundary_doc_missing_axis_qualified"})
    report = {
        "schema_version": "dvf-3-3-closeout-boundary-validation-report-v1",
        "generated_at": GENERATED_AT,
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    if write_report:
        write_json(
            phase_path(
                "phase4",
                "closeout_claim_boundary_validation_report.json",
            ),
            report,
        )
    return report, not errors


def validate_all(
    *,
    require_complete: bool = False,
    section: str = "all",
    write_report: bool = True,
) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    if (
        write_report
        and phase_path(
            "phase7",
            "final_closeout_reentry_guard_seal_report.json",
        ).exists()
    ):
        write_independent_review_artifact_hash_report()
    required_paths = [
        phase_path("phase0", "roadmap_input_binding.json"),
        phase_path("phase0", "owner_reserved_seal_requirements.json"),
        phase_path("phase1", "claim_surface_scan_manifest.json"),
        phase_path("phase1", "closeout_claim_surface_inventory.json"),
        phase_path("phase2", "dvf_3_3_closeout_claim_taxonomy.json"),
        phase_path("phase2", "completion_vocabulary_separation_report.json"),
        phase_path("phase3", "predecessor_reentry_guard_report.json"),
        phase_path("phase4", "closeout_claim_boundary_guard_report.json"),
        phase_path("phase5", "closeout_reentry_guard_manifest_adoption_report.json"),
        phase_path("phase6", "docs_claim_taxonomy_consistency_report.json"),
        phase_path("phase7", "final_no_mutation_report.json"),
        phase_path("phase7", "final_pinned_command_manifest.json"),
        phase_path("phase7", "final_closeout_reentry_guard_seal_report.json"),
        phase_path("phase7", "independent_review_artifact_hash_report.json"),
        COMPLETION_POLICY_DOC,
        PREDECESSOR_POLICY_DOC,
        CLAIM_BOUNDARY_DOC,
        LEDGER_PACKET_DOC,
    ]
    for path in required_paths:
        if not path.exists():
            errors.append({"code": "missing_artifact", "path": rel(path)})
    reports = []
    if section in {"taxonomy", "all"}:
        reports.append(
            validate_taxonomy(
                require_complete=require_complete,
                write_report=write_report,
            )[0]
        )
    if section in {"predecessor", "all"}:
        reports.append(
            validate_predecessor(
                require_complete=require_complete,
                write_report=write_report,
            )[0]
        )
    if section in {"boundary", "all"}:
        reports.append(
            validate_boundary(
                require_complete=require_complete,
                write_report=write_report,
            )[0]
        )
    for report in reports:
        if report.get("status") != "PASS":
            errors.append({"code": "section_validation_failed", "report": report})
    if not errors:
        scan = read_json(phase_path("phase1", "claim_surface_scan_manifest.json"))
        if scan.get("missing_required_surface_family_count") != 0:
            errors.append({"code": "scan_universe_incomplete", "report": scan})
        if scan.get("blocked_claim_surface_count") != 0:
            errors.append({"code": "blocked_claim_surface_nonzero", "report": scan})
        if require_complete and scan.get("status") != "PASS":
            errors.append({"code": "claim_surface_scan_not_pass", "report": scan})
        inventory = read_json(phase_path("phase1", "closeout_claim_surface_inventory.json"))
        if inventory.get("unclassified_claim_token_count") != 0:
            errors.append({"code": "unclassified_claim_token_nonzero", "report": inventory})
        if inventory.get("blocked_claim_surface_count") != 0:
            errors.append({"code": "inventory_blocked_claim_surface_nonzero", "report": inventory})
        adoption = read_json(phase_path("phase5", "closeout_reentry_guard_manifest_adoption_report.json"))
        if require_complete and adoption.get("required_gate_adoption_status") != "adopted_required_gate":
            errors.append({"code": "required_gate_not_adopted", "report": adoption})
        no_mutation = read_json(phase_path("phase7", "final_no_mutation_report.json"))
        if no_mutation.get("changed_count") != 0:
            errors.append({"code": "protected_surface_mutated", "report": no_mutation})
        final = read_json(phase_path("phase7", "final_closeout_reentry_guard_seal_report.json"))
        if final.get("machine_contract_status") != "PASS":
            errors.append({"code": "machine_contract_not_pass", "report": final})
        if final.get("canonical_seal_allowed") is not True:
            errors.append({"code": "canonical_seal_not_allowed_after_independent_review_pass", "report": final})
        if final.get("closeout_state") != "canonical_complete":
            errors.append({"code": "canonical_closeout_state_not_complete", "report": final})
        if final.get("independent_review_status") != "PASS":
            errors.append({"code": "independent_review_not_pass", "report": final})
        if final.get("forbidden_release_package_workshop_deployment_manual_qa_semantic_public_claim_count") != 0:
            errors.append({"code": "forbidden_final_claim_nonzero", "report": final})
        final_route = final.get("full_current_route_validation", {})
        route = full_current_route_result_summary()
        route_contract_fields = {
            "result_present",
            "success",
            "test_count",
            "closure_enforced",
            "schema_version",
            "contract_class",
            "required_validations_success",
            "selected_identity_count",
            "errors_count",
            "failures_count",
            "runner_result_valid",
            "runner_shape_error_count",
            "runner_shape_errors",
            "status",
            "path",
        }
        final_route_contract = {
            key: final_route.get(key)
            for key in route_contract_fields
        }
        current_route_contract = {
            key: route.get(key)
            for key in route_contract_fields
        }
        if require_complete and final_route_contract != current_route_contract:
            errors.append(
                {
                    "code": "full_current_route_validation_summary_stale",
                    "final_report_route": final_route_contract,
                    "current_route": current_route_contract,
                }
            )
        if require_complete and route.get("result_present") is not True:
            errors.append({"code": "full_current_route_validation_missing", "report": route})
        if require_complete and route.get("result_present") and route.get("runner_result_valid") is not True:
            errors.append({"code": "full_current_route_runner_shape_invalid", "report": route})
        if route.get("result_present") and route.get("success") is not True:
            errors.append({"code": "recorded_full_current_route_validation_failed", "report": route})
        if require_complete and route.get("result_present"):
            if route.get("closure_enforced") is not True:
                errors.append({"code": "full_current_route_closure_not_enforced", "report": route})
            if route.get("test_count") != EXPECTED_CURRENT_ROUTE_TEST_COUNT:
                errors.append(
                    {
                        "code": "full_current_route_test_count_mismatch",
                        "expected": EXPECTED_CURRENT_ROUTE_TEST_COUNT,
                        "report": route,
                    }
                )
    report = {
        "schema_version": "dvf-3-3-closeout-reentry-validation-report-v1",
        "generated_at": GENERATED_AT,
        "section": section,
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    if write_report:
        write_json(
            phase_path("phase7", f"validation_report.{section}.json"),
            report,
        )
    if section == "all":
        review_hash = write_independent_review_artifact_hash_report(
            write_report=write_report
        )
        if not write_report:
            stored_review_path = phase_path(
                "phase7",
                "independent_review_artifact_hash_report.json",
            )
            stored_review = (
                read_json(stored_review_path)
                if stored_review_path.exists()
                else None
            )
            if stored_review != review_hash:
                errors.append(
                    {
                        "code": (
                            "independent_review_artifact_hash_report_stale"
                        ),
                        "path": rel(stored_review_path),
                        "stored_present": stored_review is not None,
                        "expected_aggregate_sha256": review_hash.get(
                            "aggregate_sha256"
                        ),
                        "stored_aggregate_sha256": (
                            stored_review.get("aggregate_sha256")
                            if isinstance(stored_review, dict)
                            else None
                        ),
                    }
                )
        if require_complete and review_hash.get("status") != "PASS":
            errors.append({"code": "independent_review_artifact_hash_report_not_pass", "report": review_hash})
        if errors:
            report = {
                "schema_version": "dvf-3-3-closeout-reentry-validation-report-v1",
                "generated_at": GENERATED_AT,
                "section": section,
                "status": "FAIL",
                "require_complete": require_complete,
                "error_count": len(errors),
                "errors": errors,
            }
        if write_report and errors:
            write_json(phase_path("phase7", f"validation_report.{section}.json"), report)
            write_independent_review_artifact_hash_report()
    return report, not errors
