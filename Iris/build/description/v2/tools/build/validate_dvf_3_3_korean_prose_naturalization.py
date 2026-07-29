from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.build.run_dvf_3_3_korean_prose_naturalization import (
        EVALUATION_SUBJECT_KIND,
        EXPECTED_CURRENT_FACTS_SHA256,
        EXPECTED_CURRENT_MANIFEST_SHA256,
        EXPECTED_COMPILER_FIX_COMMIT,
        EXPECTED_FOUNDATION_CONTRACT_SHA256,
        EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256,
        EXPECTED_FOUNDATION_READINESS_SHA256,
        EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256,
        EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256,
        EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256,
        EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256,
        EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256,
        EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256,
        EXPECTED_SELECTED_SUCCESSOR_FACTS_SHA256,
        EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256,
        EXPECTED_START_COMMIT,
        EXPECTED_START_TREE,
        FOUNDATION_CONTRACT,
        FOUNDATION_READINESS_CURRENT_INPUT_REBIND,
        FOUNDATION_READINESS_CORRECTION_REBIND,
        NaturalizationError,
        REPO_ROOT,
        REGISTRY_ADOPTION_CONTRACT,
        REGISTRY_NATURALIZATION_HANDOFF,
        attempt_root_for,
        canonical_hash,
        implementation_hash,
        load_json,
        phase_root,
        sha256_file,
    )
else:
    from .run_dvf_3_3_korean_prose_naturalization import (
        EVALUATION_SUBJECT_KIND,
        EXPECTED_CURRENT_FACTS_SHA256,
        EXPECTED_CURRENT_MANIFEST_SHA256,
        EXPECTED_COMPILER_FIX_COMMIT,
        EXPECTED_FOUNDATION_CONTRACT_SHA256,
        EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256,
        EXPECTED_FOUNDATION_READINESS_SHA256,
        EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256,
        EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256,
        EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256,
        EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256,
        EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256,
        EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256,
        EXPECTED_SELECTED_SUCCESSOR_FACTS_SHA256,
        EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256,
        EXPECTED_START_COMMIT,
        EXPECTED_START_TREE,
        FOUNDATION_CONTRACT,
        FOUNDATION_READINESS_CURRENT_INPUT_REBIND,
        FOUNDATION_READINESS_CORRECTION_REBIND,
        NaturalizationError,
        REPO_ROOT,
        REGISTRY_ADOPTION_CONTRACT,
        REGISTRY_NATURALIZATION_HANDOFF,
        attempt_root_for,
        canonical_hash,
        implementation_hash,
        load_json,
        phase_root,
        sha256_file,
    )


def require_value(condition: bool, reason: str, errors: list[str]) -> None:
    if not condition:
        errors.append(reason)


def validate_facts_authority_routing_contract(
    request: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    require_value(
        request.get("schema_version")
        == "dvf-3-3-facts-authority-enrichment-request-v1",
        "facts_authority_schema_invalid",
        errors,
    )
    require_value(
        request.get("status")
        in {
            "blocked_facts_authority_information_insufficient",
            "not_required",
        },
        "facts_authority_status_invalid",
        errors,
    )
    require_value(
        request.get("owner") == "dvf_3_3_facts_authority",
        "facts_authority_owner_invalid",
        errors,
    )
    require_value(
        request.get("authority_domain") == "layer3_3_facts",
        "facts_authority_domain_invalid",
        errors,
    )
    require_value(
        request.get("routing_target")
        == "dvf_3_3_facts_authority_enrichment_plan",
        "facts_authority_routing_target_invalid",
        errors,
    )
    require_value(
        request.get("facts_authority_plan_path")
        == "docs/dvf_3_3_facts_authority_enrichment_plan.md",
        "facts_authority_plan_path_invalid",
        errors,
    )
    require_value(
        request.get("layer4_qg_role")
        == "separate_interaction_quality_gate",
        "layer4_qg_role_invalid",
        errors,
    )
    require_value(
        request.get("layer4_qg_routing_allowed") is False,
        "layer3_source_deficiency_auto_routed_to_layer4_qg",
        errors,
    )
    require_value(
        request.get("layer4_qg_source_authority_allowed") is False,
        "layer4_qg_promoted_to_layer3_facts_authority",
        errors,
    )
    require_value(
        request.get("cross_layer_promotion_requires_separate_approved_plan")
        is True,
        "cross_layer_promotion_plan_requirement_missing",
        errors,
    )
    return errors


def validate_phase0(root: Path, errors: list[str]) -> dict[str, Any]:
    report = load_json(phase_root(root, 0) / "preflight_report.json")
    registry_binding = load_json(
        phase_root(root, 0)
        / "registry_adoption_receipt_binding_report.json"
    )
    foundation_identity = load_json(
        phase_root(root, 0) / "g4_foundation_commit_identity.json"
    )
    historical_policy = load_json(
        phase_root(root, 0) / "historical_attempt_policy_report.json"
    )
    registry_contract = load_json(REGISTRY_ADOPTION_CONTRACT)
    readiness_rebind = load_json(FOUNDATION_READINESS_CORRECTION_REBIND)
    readiness_current_input_rebind = load_json(
        FOUNDATION_READINESS_CURRENT_INPUT_REBIND
    )
    applicability = load_json(
        phase_root(root, 0) / "body_plan_applicability_authority_binding.json"
    )
    require_value(report.get("status") == "PASS", "phase0_status_not_pass", errors)
    require_value(
        report.get("execution_contract_checked") is True,
        "execution_contract_not_checked",
        errors,
    )
    require_value(
        report.get("execution_contract_conflict_count") == 0,
        "execution_contract_conflict",
        errors,
    )
    require_value(
        report.get("publish_foundation_contract_ready_for_remediation") is True,
        "publish_foundation_not_ready",
        errors,
    )
    require_value(
        report.get("publish_foundation_authority_effect") == "none",
        "foundation_authority_effect_invalid",
        errors,
    )
    require_value(
        report.get("publish_foundation_official_disposition") == "not_issued",
        "foundation_official_disposition_invalid",
        errors,
    )
    require_value(
        report.get("publish_foundation_live_gate_adopted") is False,
        "foundation_live_gate_state_invalid",
        errors,
    )
    require_value(
        report.get("publish_foundation_policy_closure_state") == "not_started",
        "foundation_policy_closure_state_invalid",
        errors,
    )
    require_value(
        applicability.get("owner_approval_match") is True,
        "body_plan_applicability_owner_approval_invalid",
        errors,
    )
    require_value(
        report.get("body_plan_applicability_approval_sha256")
        == applicability.get("approval_sha256"),
        "body_plan_applicability_approval_hash_mismatch",
        errors,
    )
    require_value(
        report.get("registry_adoption_binding_pass") is True
        and registry_binding.get("status") == "PASS",
        "registry_adoption_binding_not_pass",
        errors,
    )
    registry_actual = registry_binding.get("actual_source_identity", {})
    selected_successor = registry_contract.get("selected_successor", {})
    registry_contract_predicates = registry_binding.get(
        "registry_contract_predicates", {}
    )
    blocked_attempt_predicates = registry_binding.get(
        "blocked_attempt_predicates", {}
    )
    require_value(
        registry_binding.get("registry_adoption_contract_sha256")
        == EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256
        and sha256_file(REGISTRY_ADOPTION_CONTRACT)
        == EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256,
        "registry_adoption_contract_identity_mismatch",
        errors,
    )
    require_value(
        registry_actual.get("current_facts_sha256")
        == EXPECTED_CURRENT_FACTS_SHA256
        and registry_actual.get("current_manifest_sha256")
        == EXPECTED_CURRENT_MANIFEST_SHA256
        and registry_actual.get("selected_successor_manifest_sha256")
        == EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256
        and selected_successor.get("facts_sha256")
        == EXPECTED_SELECTED_SUCCESSOR_FACTS_SHA256
        and selected_successor.get("manifest_sha256")
        == EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256
        and registry_contract_predicates.get(
            "selected_predecessor_facts_match"
        )
        is True
        and registry_contract_predicates.get("selected_manifest_match")
        is True
        and registry_contract_predicates.get("correction_facts_match")
        is True
        and registry_contract_predicates.get("correction_manifest_match")
        is True,
        "registry_selected_predecessor_or_correction_binding_mismatch",
        errors,
    )
    require_value(
        registry_binding.get("official_publish_attempt_allowed") is False
        and registry_binding.get("live_publish_gate_mutation_allowed")
        is False
        and registry_binding.get("runtime_or_package_publication_allowed")
        is False,
        "registry_publish_boundary_expanded",
        errors,
    )
    require_value(
        blocked_attempt_predicates.get(
            "current_manifest_blocked_attempt_id_match"
        )
        is True
        and blocked_attempt_predicates.get(
            "current_manifest_reentry_not_allowed"
        )
        is True
        and blocked_attempt_predicates.get(
            "g4_rebind_blocked_status_match"
        )
        is True
        and blocked_attempt_predicates.get(
            "g4_rebind_phase7_or_phase8_reentry_not_allowed"
        )
        is True
        and blocked_attempt_predicates.get(
            "g4_current_input_rebind_requires_fresh_phase0"
        )
        is True
        and blocked_attempt_predicates.get(
            "g4_current_input_rebind_has_not_run_naturalization"
        )
        is True
        and readiness_rebind.get("naturalization_prerequisites", {}).get(
            "attempt_0018_status"
        )
        == "BLOCKED"
        and readiness_rebind.get("naturalization_prerequisites", {}).get(
            "attempt_0018_phase7_or_phase8_reentry_allowed"
        )
        is False,
        "attempt_0018_rebind_boundary_invalid",
        errors,
    )
    require_value(
        report.get("current_facts_sha256") == EXPECTED_CURRENT_FACTS_SHA256
        and report.get("current_manifest_sha256")
        == EXPECTED_CURRENT_MANIFEST_SHA256
        and report.get("registry_adoption_receipt_sha256")
        == EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256
        and report.get("initial_registry_adoption_receipt_sha256")
        == EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256
        and report.get("registry_correction_terminal_seal_sha256")
        == EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256
        and report.get("registry_naturalization_handoff_sha256")
        == EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256
        and sha256_file(REGISTRY_NATURALIZATION_HANDOFF)
        == EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256,
        "g3_current_source_identity_mismatch",
        errors,
    )
    require_value(
        foundation_identity.get("foundation_contract_sha256")
        == EXPECTED_FOUNDATION_CONTRACT_SHA256
        and foundation_identity.get("foundation_readiness_sha256")
        == EXPECTED_FOUNDATION_READINESS_SHA256
        and foundation_identity.get(
            "foundation_readiness_correction_rebind_sha256"
        )
        == EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256
        and foundation_identity.get(
            "foundation_readiness_current_input_rebind_sha256"
        )
        == EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256
        and sha256_file(FOUNDATION_READINESS_CURRENT_INPUT_REBIND)
        == EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256
        and foundation_identity.get(
            "foundation_readiness_current_input_rebind_current_facts_sha256"
        )
        == EXPECTED_CURRENT_FACTS_SHA256
        and foundation_identity.get(
            "foundation_readiness_current_input_rebind_current_manifest_sha256"
        )
        == EXPECTED_CURRENT_MANIFEST_SHA256
        and readiness_current_input_rebind.get("status") == "PASS"
        and foundation_identity.get("compiler_fix_commit")
        == EXPECTED_COMPILER_FIX_COMMIT
        and foundation_identity.get("compiler_fix_is_ancestor") is True
        and foundation_identity.get("naturalization_start_commit")
        == EXPECTED_START_COMMIT
        and foundation_identity.get("naturalization_start_tree")
        == EXPECTED_START_TREE
        and foundation_identity.get("naturalization_start_actual_tree")
        == EXPECTED_START_TREE
        and foundation_identity.get(
            "naturalization_start_commit_is_ancestor"
        )
        is True
        and foundation_identity.get("foundation_commit_changed_path_count")
        == 19,
        "g4_foundation_identity_mismatch",
        errors,
    )
    require_value(
        historical_policy.get("historical_attempt_id")
        == "attempt-0014-remediation"
        and historical_policy.get("role")
        == "immutable_historical_evidence_only"
        and historical_policy.get("resumed") is False
        and historical_policy.get("candidate_or_trace_reused") is False,
        "attempt_0014_reuse_boundary_invalid",
        errors,
    )
    require_value(
        historical_policy.get("blocked_attempt_id")
        == "attempt-0018-g3-reseal-a"
        and historical_policy.get("blocked_attempt_role")
        == "immutable_blocked_evidence_only"
        and historical_policy.get("blocked_attempt_resumed") is False
        and historical_policy.get(
            "blocked_attempt_phase7_or_phase8_reentry_allowed"
        )
        is False
        and historical_policy.get("blocked_attempt_phase7_exists") is False
        and historical_policy.get("blocked_attempt_phase8_exists") is False,
        "attempt_0018_blocked_boundary_invalid",
        errors,
    )
    return report


def validate_phase1(root: Path, errors: list[str]) -> dict[str, Any]:
    result = load_json(phase_root(root, 1) / "phase1_result.json")
    census = load_json(phase_root(root, 1) / "current_prose_census.json")
    require_value(result.get("status") == "PASS", "phase1_status_not_pass", errors)
    require_value(
        census.get("current_surface_snapshot_is_semantic_authority") is False,
        "current_surface_promoted_to_semantic_authority",
        errors,
    )
    require_value(
        all(row.get("exists") for row in result.get("corpus_bindings", [])),
        "corpus_artifact_missing",
        errors,
    )
    require_value(
        result.get("corpus_validation_pass") is True,
        "corpus_validation_failure",
        errors,
    )
    return result


def validate_phase2(root: Path, errors: list[str]) -> dict[str, Any]:
    result = load_json(phase_root(root, 2) / "phase2_result.json")
    manifest = load_json(phase_root(root, 2) / "source_proposition_manifest.json")
    applicability = load_json(
        phase_root(root, 2) / "body_plan_applicability_report.json"
    )
    coverage = load_json(
        phase_root(root, 2) / "source_to_proposition_coverage_report.json"
    )
    reseal = load_json(
        phase_root(root, 2) / "source_authority_reseal_report.json"
    )
    phase0_registry_binding = load_json(
        phase_root(root, 0)
        / "registry_adoption_receipt_binding_report.json"
    )
    registry_contract = load_json(REGISTRY_ADOPTION_CONTRACT)
    require_value(result.get("status") == "PASS", "phase2_status_not_pass", errors)
    require_value(
        manifest.get("candidate_dependency_count") == 0,
        "source_inventory_candidate_dependency",
        errors,
    )
    require_value(
        manifest.get("candidate_trace_dependency_count") == 0,
        "source_inventory_trace_dependency",
        errors,
    )
    require_value(
        manifest.get("profile_body_plan_generated_semantic_proposition_count") == 0,
        "body_plan_generated_semantic_content",
        errors,
    )
    require_value(
        coverage.get("source_to_proposition_coverage_pass") is True,
        "source_to_proposition_coverage_failure",
        errors,
    )
    require_value(
        applicability.get("status") == "PASS"
        and applicability.get("policy_contract_match") is True,
        "body_plan_applicability_not_pass",
        errors,
    )
    require_value(
        applicability.get("source_proposition_invention_count") == 0
        and applicability.get("current_compose_profile_mutation_count") == 0
        and applicability.get("current_source_authority_mutation_count") == 0,
        "body_plan_applicability_authority_expansion",
        errors,
    )
    require_value(
        manifest.get("body_plan_applicability_approval_sha256")
        == applicability.get("approval_sha256"),
        "body_plan_applicability_phase2_hash_mismatch",
        errors,
    )
    require_value(
        result.get("source_authority_reseal_pass") is True
        and reseal.get("status") == "PASS",
        "phase2_source_authority_reseal_not_pass",
        errors,
    )
    require_value(
        reseal.get("current_facts_sha256") == EXPECTED_CURRENT_FACTS_SHA256
        and reseal.get("current_manifest_sha256")
        == EXPECTED_CURRENT_MANIFEST_SHA256
        and reseal.get("registry_adoption_receipt_sha256")
        == EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256
        and reseal.get("registry_adoption_contract_sha256")
        == EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256
        and reseal.get("initial_registry_adoption_receipt_sha256")
        == EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256
        and reseal.get("registry_correction_terminal_seal_sha256")
        == EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256
        and reseal.get("registry_naturalization_handoff_sha256")
        == EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256
        and reseal.get("g4_foundation_contract_sha256")
        == EXPECTED_FOUNDATION_CONTRACT_SHA256
        and reseal.get("g4_foundation_readiness_sha256")
        == EXPECTED_FOUNDATION_READINESS_SHA256
        and reseal.get(
            "g4_foundation_readiness_correction_rebind_sha256"
        )
        == EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256
        and reseal.get(
            "g4_foundation_readiness_current_input_rebind_sha256"
        )
        == EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256
        and reseal.get("naturalization_start_commit")
        == EXPECTED_START_COMMIT
        and reseal.get("naturalization_start_tree") == EXPECTED_START_TREE
        and reseal.get("compiler_fix_commit") == EXPECTED_COMPILER_FIX_COMMIT
        and reseal.get("compiler_fix_is_ancestor") is True,
        "phase2_g3_g4_identity_mismatch",
        errors,
    )
    phase2_four_hash = reseal.get("actual_four_hash_identity", {})
    selected_successor = registry_contract.get("selected_successor", {})
    require_value(
        phase2_four_hash.get("current_facts_sha256")
        == EXPECTED_CURRENT_FACTS_SHA256
        and phase2_four_hash.get("selected_successor_manifest_sha256")
        == EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256
        and selected_successor.get("facts_sha256")
        == EXPECTED_SELECTED_SUCCESSOR_FACTS_SHA256
        and selected_successor.get("manifest_sha256")
        == EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256
        and phase0_registry_binding.get(
            "registry_contract_predicates", {}
        ).get("selected_predecessor_facts_match")
        is True
        and reseal.get("live_gate_mutation_allowed") is False
        and reseal.get("official_publish_attempt_allowed") is False
        and reseal.get("runtime_or_package_compatibility_claimed") is False,
        "phase2_selected_successor_or_publish_boundary_mismatch",
        errors,
    )
    require_value(
        manifest.get("food_semantic_proposition_count") == 718
        and result.get("food_semantic_proposition_count") == 718
        and reseal.get("food_semantic_proposition_count") == 718
        and reseal.get("invalid_food_semantic_assertion_count") == 0,
        "phase2_food_semantic_inventory_invalid",
        errors,
    )
    require_value(
        manifest.get("attempt_0014_reused_as_current_evidence") is False
        and reseal.get("attempt_0014_reused_as_current_evidence") is False
        and manifest.get("attempt_0018_reused_or_resumed") is False
        and reseal.get("attempt_0018_reused_or_resumed") is False,
        "phase2_attempt_0014_evidence_reused",
        errors,
    )
    return result


def validate_phase3(root: Path, errors: list[str]) -> dict[str, Any]:
    result = load_json(phase_root(root, 3) / "phase3_result.json")
    regression = load_json(
        phase_root(root, 3) / "default_mode_regression_report.json"
    )
    negative = load_json(
        phase_root(root, 3) / "write_boundary_negative_test_report.json"
    )
    cause = load_json(
        phase_root(root, 3) / "repeated_skeleton_cause_analysis.json"
    )
    projection = load_json(
        phase_root(root, 3) / "semantic_lead_rule_projection_report.json"
    )
    facts_authority = load_json(
        phase_root(root, 3) / "facts_authority_enrichment_request.json"
    )
    require_value(result.get("status") == "PASS", "phase3_status_not_pass", errors)
    require_value(
        regression.get("legacy_normalized_content_hash_identity_pass") is True,
        "legacy_normalized_content_drift",
        errors,
    )
    require_value(
        negative.get("write_boundary_negative_test_pass") is True,
        "candidate_write_boundary_failure",
        errors,
    )
    require_value(
        result.get("semantic_condition_facts_authority_gate_pass") is True
        and cause.get("oversized_identical_approved_semantic_condition_count") == 0
        and facts_authority.get("status") == "not_required",
        "phase3_facts_authority_information_gate_not_pass",
        errors,
    )
    errors.extend(validate_facts_authority_routing_contract(facts_authority))
    require_value(
        result.get("compiler_rule_projection_pass") is True
        and projection.get("compiler_rule_projection_pass") is True
        and projection.get("unexplained_compiler_blocked_item_count") == 0,
        "phase3_semantic_rule_projection_not_pass",
        errors,
    )
    return result


def validate_phase4(
    root: Path,
    compare_root: Path | None,
    errors: list[str],
) -> dict[str, Any]:
    result = load_json(phase_root(root, 4) / "phase4_result.json")
    manifest = load_json(phase_root(root, 4) / "candidate_manifest.json")
    full = load_json(
        phase_root(root, 4) / "full_universe_generation_report.json"
    )
    require_value(result.get("status") == "PASS", "phase4_status_not_pass", errors)
    require_value(
        full.get("candidate_full_universe_generation_pass") is True,
        "candidate_full_universe_generation_failure",
        errors,
    )
    require_value(
        manifest.get("candidate_content_hash_count") == 1,
        "candidate_content_hash_count_invalid",
        errors,
    )
    require_value(
        manifest.get("candidate_volatile_metadata_field_count") == 0,
        "candidate_volatile_metadata_present",
        errors,
    )
    if compare_root is None:
        errors.append("phase4_compare_attempt_required")
    else:
        compare_manifest = load_json(
            phase_root(compare_root, 4) / "candidate_manifest.json"
        )
        require_value(
            manifest.get("candidate_rendered_hash")
            == compare_manifest.get("candidate_rendered_hash"),
            "candidate_two_run_content_hash_mismatch",
            errors,
        )
        require_value(
            manifest.get("candidate_proposition_trace_hash")
            == compare_manifest.get("candidate_proposition_trace_hash"),
            "candidate_two_run_trace_hash_mismatch",
            errors,
        )
    return result


def validate_phase5(root: Path, errors: list[str]) -> dict[str, Any]:
    result = load_json(phase_root(root, 5) / "phase5_semantic_result.json")
    adversarial = load_json(
        phase_root(root, 5) / "adversarial_validation_report.json"
    )
    require_value(
        result.get("semantic_preservation_pass") is True,
        "semantic_preservation_failure",
        errors,
    )
    require_value(
        result.get("unsatisfied_required_body_plan_role_count") == 0,
        "unsatisfied_required_body_plan_role",
        errors,
    )
    require_value(
        result.get("rendered_shape_contract_pass") is True,
        "rendered_shape_contract_failure",
        errors,
    )
    require_value(
        adversarial.get("adversarial_validation_pass") is True,
        "adversarial_validation_failure",
        errors,
    )
    return result


def validate_phase6(root: Path, errors: list[str]) -> dict[str, Any]:
    result = load_json(phase_root(root, 6) / "phase6_result.json")
    raw = load_json(phase_root(root, 6) / "raw_detector_report.json")
    residual = load_json(
        phase_root(root, 6) / "compiler_invalid_residual_report.json"
    )
    require_value(
        raw.get("raw_detector_full_candidate_completeness_pass") is True,
        "raw_detector_completeness_failure",
        errors,
    )
    require_value(
        raw.get("disposition_created") is False,
        "raw_detector_created_disposition",
        errors,
    )
    require_value(
        residual.get("compiler_invalid_pattern_count") == 0,
        "compiler_invalid_pattern_present",
        errors,
    )
    require_value(
        residual.get("item_specific_patch_count") == 0
        and residual.get("item_specific_override_count") == 0
        and residual.get("item_specific_branch_count") == 0,
        "item_specific_exception_present",
        errors,
    )
    return result


def validate_phase7(root: Path, errors: list[str]) -> dict[str, Any]:
    manifest = load_json(
        phase_root(root, 7) / "human_review_sample_manifest.json"
    )
    binding = load_json(phase_root(root, 7) / "human_review_binding_report.json")
    eligibility = load_json(
        phase_root(root, 7) / "human_review_eligibility_report.json"
    )
    require_value(binding.get("status") == "PASS", "human_review_not_pass", errors)
    require_value(
        binding.get("candidate_rendered_hash")
        == manifest.get("candidate_rendered_hash"),
        "human_review_candidate_hash_mismatch",
        errors,
    )
    require_value(
        binding.get("human_review_blocker_count_within_required_denominator") == 0,
        "human_review_blocker_present",
        errors,
    )
    require_value(
        binding.get("human_review_decision_mode")
        == "exact_full_candidate_external_review",
        "human_review_decision_mode_invalid",
        errors,
    )
    require_value(
        manifest.get("selection_scope")
        == "full_candidate_review_owner_directive"
        and manifest.get("selected_required_denominator")
        == manifest.get("full_candidate_denominator")
        == manifest.get("eligible_review_denominator"),
        "human_review_not_full_candidate",
        errors,
    )
    require_value(
        binding.get("expanded_review_row_count")
        == manifest.get("selected_required_denominator"),
        "human_review_expansion_denominator_mismatch",
        errors,
    )
    require_value(
        binding.get("corpus_wide_human_only_blocker_zero_claimed") is True,
        "full_candidate_human_review_claim_missing",
        errors,
    )
    require_value(
        eligibility.get("reviewer_identity_present") is True
        and eligibility.get("reviewer_is_not_compiler") is True
        and eligibility.get("full_candidate_review") is True,
        "external_full_candidate_reviewer_ineligible",
        errors,
    )
    return binding


def validate_phase8(root: Path, errors: list[str]) -> dict[str, Any]:
    readiness = load_json(
        phase_root(root, 8) / "publish_handoff_readiness_report.json"
    )
    manifest_path = (
        phase_root(root, 8) / "publish_acceptance_handoff_manifest.json"
    )
    closeout_path = phase_root(root, 8) / "phase8_closeout.json"
    require_value(readiness.get("status") == "PASS", "handoff_not_ready", errors)
    require_value(manifest_path.is_file(), "handoff_manifest_missing", errors)
    require_value(closeout_path.is_file(), "phase8_closeout_missing", errors)
    if manifest_path.is_file():
        manifest = load_json(manifest_path)
        publish_input = load_json(
            phase_root(root, 8) / "publish_acceptance_input.json"
        )
        foundation = load_json(FOUNDATION_CONTRACT)
        constituents = manifest.get("constituents", [])
        required_ids = foundation["required_handoff_schema"][
            "required_constituent_ids"
        ]
        require_value(
            manifest.get("requested_evaluation_subject_kind")
            == EVALUATION_SUBJECT_KIND,
            "handoff_subject_kind_mismatch",
            errors,
        )
        require_value(
            all(row.get("present") for row in constituents),
            "handoff_constituent_missing",
            errors,
        )
        require_value(
            manifest.get("constituent_id_order") == required_ids
            and [row.get("id") for row in constituents] == required_ids,
            "handoff_constituent_schema_mismatch",
            errors,
        )
        require_value(
            publish_input.get("constituents") == constituents,
            "handoff_publish_input_constituent_mismatch",
            errors,
        )
        for row in constituents:
            identifier = row.get("id")
            if "path" in row:
                path = REPO_ROOT / str(row["path"])
                require_value(
                    path.is_file() and sha256_file(path) == row.get("sha256"),
                    f"handoff_constituent_stale:{identifier}",
                    errors,
                )
            else:
                require_value(
                    canonical_hash(row.get("value")) == row.get("sha256"),
                    f"handoff_value_constituent_stale:{identifier}",
                    errors,
                )
            if identifier == "compiler_implementation_hash":
                require_value(
                    row.get("value") == implementation_hash(),
                    "handoff_compiler_implementation_stale",
                    errors,
                )
        require_value(
            manifest.get("registry_runtime_pass_claim_allowed") is False,
            "handoff_registry_claim_expansion",
            errors,
        )
        require_value(
            manifest.get("write_once") is True
            and manifest.get("post_handoff_mutation_effect") == "stale",
            "handoff_immutability_contract_invalid",
            errors,
        )
        require_value(
            readiness.get("official_publish_attempt_created") is False
            and readiness.get("publish_disposition_created") is False
            and readiness.get("live_required_gate_adopted") is False
            and readiness.get("runtime_or_current_adoption_claimed") is False,
            "handoff_scope_boundary_expanded",
            errors,
        )
        if closeout_path.is_file():
            closeout = load_json(closeout_path)
            require_value(
                closeout.get("status") == "HANDOFF_COMPLETE"
                and closeout.get(
                    "publish_acceptance_handoff_manifest_sha256"
                )
                == sha256_file(manifest_path)
                and closeout.get("official_publish_attempt_created") is False
                and closeout.get("official_publish_executed") is False
                and closeout.get("live_gate_mutated") is False
                and closeout.get("runtime_lua_or_package_mutated") is False
                and closeout.get("naturalization_terminal_closure_claimed")
                is False
                and closeout.get("write_once") is True,
                "phase8_closeout_boundary_invalid",
                errors,
            )
    return readiness


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only validator for DVF 3-3 Korean prose naturalization "
            "evidence through Phase 8 handoff-build."
        )
    )
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--attempt-root", type=Path, default=None)
    parser.add_argument("--compare-attempt")
    parser.add_argument("--compare-attempt-root", type=Path, default=None)
    parser.add_argument("--require-phase0", action="store_true")
    parser.add_argument("--require-execution-contract", action="store_true")
    parser.add_argument("--require-publish-foundation-contract", action="store_true")
    parser.add_argument("--require-phase1", action="store_true")
    parser.add_argument("--require-source-proposition-inventory", action="store_true")
    parser.add_argument("--require-body-plan-contract", action="store_true")
    parser.add_argument("--require-phase3", action="store_true")
    parser.add_argument("--require-phase4", action="store_true")
    parser.add_argument("--require-phase5", action="store_true")
    parser.add_argument("--require-raw-detector-completeness", action="store_true")
    parser.add_argument("--require-human-review", action="store_true")
    parser.add_argument("--require-publish-handoff-ready", action="store_true")
    parser.add_argument("--no-write", action="store_true", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    selected = any(
        (
            args.require_phase0,
            args.require_execution_contract,
            args.require_publish_foundation_contract,
            args.require_phase1,
            args.require_source_proposition_inventory,
            args.require_body_plan_contract,
            args.require_phase3,
            args.require_phase4,
            args.require_phase5,
            args.require_raw_detector_completeness,
            args.require_human_review,
            args.require_publish_handoff_ready,
        )
    )
    if not selected:
        print(
            json.dumps(
                {"status": "FAIL", "error": "at least one --require-* is required"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    try:
        root = attempt_root_for(args.attempt_id, args.attempt_root)
        compare_root = None
        if args.compare_attempt is not None:
            compare_root = attempt_root_for(
                args.compare_attempt,
                args.compare_attempt_root,
            )
        errors: list[str] = []
        checked: list[str] = []
        if (
            args.require_phase0
            or args.require_execution_contract
            or args.require_publish_foundation_contract
        ):
            validate_phase0(root, errors)
            checked.append("phase0")
        if args.require_phase1:
            validate_phase1(root, errors)
            checked.append("phase1")
        if args.require_source_proposition_inventory or args.require_body_plan_contract:
            validate_phase2(root, errors)
            checked.append("phase2")
        if args.require_phase3:
            validate_phase3(root, errors)
            checked.append("phase3")
        if args.require_phase4:
            validate_phase4(root, compare_root, errors)
            checked.append("phase4")
        if args.require_phase5:
            validate_phase5(root, errors)
            checked.append("phase5")
        if args.require_raw_detector_completeness:
            validate_phase6(root, errors)
            checked.append("phase6")
        if args.require_human_review:
            validate_phase7(root, errors)
            checked.append("phase7")
        if args.require_publish_handoff_ready:
            validate_phase8(root, errors)
            checked.append("phase8_handoff")
        result = {
            "schema_version": "dvf-3-3-korean-prose-validation-result-v1",
            "status": "PASS" if not errors else "FAIL",
            "attempt_id": args.attempt_id,
            "checked": checked,
            "error_count": len(errors),
            "errors": errors,
            "no_write": True,
        }
    except (NaturalizationError, KeyError, TypeError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "FAIL", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
