from __future__ import annotations

from pathlib import Path
from typing import Any

from .naturalization_context import (
    CORPUS_MANIFEST_PATH, EVALUATION_SUBJECT_KIND, FOUNDATION_CONTRACT,
    GOLD_APPROVAL_PATH, HUMAN_REVIEW_DECISION_PATH, POLICY_PATH,
    QUALITY_APPROVAL_PATH, SYNC_CONTRACT_ID,
)
from .naturalization_infrastructure import (
    canonical_hash, load_json, phase_root, repo_relative, require_files,
    sha256_file, write_once_or_same,
)
from .naturalization_projection import require_phase0
from .naturalization_transformation import implementation_hash

def constituent(
    identifier: str,
    *,
    path: Path | None = None,
    value: Any = None,
) -> dict[str, Any]:
    if path is not None:
        return {
            "id": identifier,
            "path": repo_relative(path),
            "sha256": sha256_file(path) if path.is_file() else None,
            "present": path.is_file(),
        }
    return {
        "id": identifier,
        "value": value,
        "sha256": canonical_hash(value),
        "present": value is not None,
    }


def build_phase8_handoff(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    p0 = phase_root(attempt_root, 0)
    p2 = phase_root(attempt_root, 2)
    p4 = phase_root(attempt_root, 4)
    p5 = phase_root(attempt_root, 5)
    p6 = phase_root(attempt_root, 6)
    p7 = phase_root(attempt_root, 7)
    root = phase_root(attempt_root, 8)
    root.mkdir(parents=True, exist_ok=True)
    required_prior = (
        p0 / "publish_foundation_binding_report.json",
        p0 / "body_plan_applicability_authority_binding.json",
        p2 / "source_proposition_manifest.json",
        p2 / "body_plan_requirement_inventory.jsonl",
        p2 / "body_plan_applicability_report.json",
        p4 / "candidate_rendered.json",
        p4 / "candidate_manifest.json",
        p4 / "protected_surface_after_snapshot.json",
        p5 / "semantic_preservation_report.json",
        p5 / "structural_satisfaction_ledger.jsonl",
        p5 / "body_plan_application_report.json",
        p6 / "raw_detector_report.json",
        p7 / "human_review_sample_manifest.json",
        p7 / "human_review_binding_report.json",
    )
    require_files(required_prior)
    foundation_binding = load_json(p0 / "publish_foundation_binding_report.json")
    applicability_binding = load_json(
        p0 / "body_plan_applicability_authority_binding.json"
    )
    applicability_report = load_json(p2 / "body_plan_applicability_report.json")
    candidate_manifest = load_json(p4 / "candidate_manifest.json")
    body_report = load_json(p5 / "body_plan_application_report.json")
    semantic_report = load_json(p5 / "semantic_preservation_report.json")
    raw_report = load_json(p6 / "raw_detector_report.json")
    review_binding = load_json(p7 / "human_review_binding_report.json")
    constituents = [
        constituent("naturalization_attempt_id", value=attempt_id),
        constituent(
            "foundation_contract_hash",
            path=FOUNDATION_CONTRACT,
        ),
        constituent("candidate_rendered_hash", path=p4 / "candidate_rendered.json"),
        constituent("candidate_manifest_hash", path=p4 / "candidate_manifest.json"),
        constituent(
            "source_proposition_manifest_hash",
            path=p2 / "source_proposition_manifest.json",
        ),
        constituent(
            "body_plan_requirement_digest",
            path=p2 / "body_plan_requirement_inventory.jsonl",
        ),
        constituent(
            "structural_satisfaction_ledger_hash",
            path=p5 / "structural_satisfaction_ledger.jsonl",
        ),
        constituent(
            "semantic_preservation_report_hash",
            path=p5 / "semantic_preservation_report.json",
        ),
        constituent("raw_detector_report_hash", path=p6 / "raw_detector_report.json"),
        constituent(
            "human_review_sample_manifest_hash",
            path=p7 / "human_review_sample_manifest.json",
        ),
        constituent(
            "human_review_decision_hash",
            path=HUMAN_REVIEW_DECISION_PATH,
        ),
        constituent(
            "compiler_implementation_hash",
            value=implementation_hash(),
        ),
        constituent("korean_prose_policy_hash", path=POLICY_PATH),
        constituent("corpus_manifest_hash", path=CORPUS_MANIFEST_PATH),
        constituent(
            "protected_surface_no_mutation_report_hash",
            path=p4 / "protected_surface_after_snapshot.json",
        ),
        constituent(
            "requested_evaluation_subject_kind",
            value=EVALUATION_SUBJECT_KIND,
        ),
    ]
    publish_input = {
        "schema_version": "dvf-3-3-publish-acceptance-input-v1",
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "requested_evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": sha256_file(p4 / "candidate_rendered.json"),
        "naturalization_attempt_id": attempt_id,
        "constituents": constituents,
        "candidate_runtime_parity_applicability": "not_applicable",
        "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
        "registry_runtime_pass_claim_allowed": False,
    }
    write_once_or_same(root / "publish_acceptance_input.json", publish_input)
    blockers: list[str] = []
    if any(not row["present"] for row in constituents):
        blockers.append("required_handoff_constituent_missing")
    if not semantic_report.get("semantic_preservation_pass"):
        blockers.append("semantic_preservation_not_pass")
    if body_report.get("unsatisfied_required_body_plan_role_count") != 0:
        blockers.append("unsatisfied_required_body_plan_role")
    if not raw_report.get("raw_detector_full_candidate_completeness_pass"):
        blockers.append("raw_detector_incomplete")
    if review_binding.get("status") != "PASS":
        blockers.append("human_review_not_pass")
    if (
        applicability_binding.get("owner_approval_match") is not True
        or applicability_report.get("status") != "PASS"
        or applicability_report.get("source_proposition_invention_count") != 0
    ):
        blockers.append("body_plan_applicability_authority_not_pass")
    if not QUALITY_APPROVAL_PATH.is_file() or not GOLD_APPROVAL_PATH.is_file():
        blockers.append("corpus_or_quality_owner_approval_missing")
    if candidate_manifest.get("candidate_content_hash_count") != 1:
        blockers.append("candidate_content_hash_count_invalid")
    readiness = {
        "schema_version": "dvf-3-3-publish-handoff-readiness-report-v1",
        "status": "PASS" if not blockers else "blocked_handoff_not_ready",
        "naturalization_attempt_id": attempt_id,
        "candidate_rendered_hash": sha256_file(p4 / "candidate_rendered.json"),
        "required_constituent_count": len(constituents),
        "present_constituent_count": sum(row["present"] for row in constituents),
        "blocker_reasons": blockers,
        "publish_acceptance_handoff_manifest_frozen": not blockers,
        "official_publish_attempt_created": False,
        "publish_disposition_created": False,
        "live_required_gate_adopted": False,
        "runtime_or_current_adoption_claimed": False,
    }
    write_once_or_same(root / "publish_handoff_readiness_report.json", readiness)
    if not blockers:
        handoff = {
            "schema_version": "naturalization_publish_handoff_required_schema_v1",
            "synchronization_contract_id": SYNC_CONTRACT_ID,
            "naturalization_attempt_id": attempt_id,
            "requested_evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
            "candidate_runtime_parity_applicability": "not_applicable",
            "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
            "constituents": constituents,
            "constituent_id_order": [row["id"] for row in constituents],
            "post_handoff_mutation_effect": "stale",
            "registry_runtime_pass_claim_allowed": False,
            "write_once": True,
        }
        handoff_path = root / "publish_acceptance_handoff_manifest.json"
        write_once_or_same(handoff_path, handoff)
        closeout = {
            "schema_version": "dvf-3-3-naturalization-phase8-closeout-v1",
            "status": "HANDOFF_COMPLETE",
            "naturalization_attempt_id": attempt_id,
            "candidate_rendered_sha256": sha256_file(
                p4 / "candidate_rendered.json"
            ),
            "publish_acceptance_handoff_manifest_path": repo_relative(
                handoff_path
            ),
            "publish_acceptance_handoff_manifest_sha256": sha256_file(
                handoff_path
            ),
            "human_review_denominator": review_binding.get(
                "required_review_denominator"
            ),
            "human_review_blocker_count": review_binding.get(
                "human_review_blocker_count_within_required_denominator"
            ),
            "official_publish_attempt_created": False,
            "official_publish_executed": False,
            "live_gate_mutated": False,
            "runtime_lua_or_package_mutated": False,
            "naturalization_terminal_closure_claimed": False,
            "next_stage": "official_publish_attempt_prohibited_until_separate_authorization",
            "write_once": True,
        }
        write_once_or_same(root / "phase8_closeout.json", closeout)
    return readiness

__all__ = ("build_phase8_handoff", "constituent")
