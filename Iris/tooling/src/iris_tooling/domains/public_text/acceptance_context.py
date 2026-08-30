from __future__ import annotations

from pathlib import Path
import re

from iris_tooling.build.naturalization_compiler_identity import compiler_source_paths

from iris_tooling.build.repository_context import (
    current_layer3_generation_root,
    require_external_workspace,
    require_repository_context,
)

V2_ROOT = require_repository_context().description_v2_root
REPO_ROOT = require_repository_context().repository_root
TOOLING_PACKAGE_SOURCE_DIR = (
    REPO_ROOT / "Iris" / "tooling" / "src" / "iris_tooling"
)
PUBLIC_TEXT_DOMAIN_DIR = TOOLING_PACKAGE_SOURCE_DIR / "domains" / "public_text"
TOOLS_DIR = TOOLING_PACKAGE_SOURCE_DIR / "build"

ROUND_ID = "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
STAGING_ROUND_ID = "iris_public_text_quality_policy_closure"
SYNC_CONTRACT_ID = "dvf3_3_korean_naturalization__publish_boundary_sync_v1"
GLOBAL_SYNC_CONTRACT_ID = "iris_aa49_four_plan_execution_sync_v1"
FOUR_PLAN_SYNC_PROJECTION_SHA256 = (
    "12c32873dc7e16e0d64e416bdb6693599e2790e9fc129606a90a72ca745a6eb0"
)
FOUNDATION_CONTRACT_VERSION = "2.0.0"
FOUNDATION_SCHEMA_VERSION = "public_text_quality_foundation_contract_v2"
READINESS_SCHEMA_VERSION = "public_text_quality_development_readiness_v2"
FIXTURE_SCHEMA_VERSION = "public_text_quality_acceptance_fixture_manifest_v1"

DEFAULT_FOUNDATION_ROOT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / ROUND_ID
    / "foundation"
)
FOUNDATION_CONTRACT_NAME = "public_text_quality_foundation_contract.json"
READINESS_REPORT_NAME = "public_text_quality_development_readiness_report.json"
PREDECESSOR_FOUNDATION = {
    "foundation_id": "ptqa-foundation-v1",
    "foundation_contract_version": "1.0.0",
    "foundation_contract_raw_sha256": (
        "3505b2edbe7b5826c70ee80a62c2eb6db25ff9d0b224f527936c1504fbf516ee"
    ),
    "source_commit": "33aad08676c96d5ae1ae7ff1c3fa509feff8bf08",
    "reuse_disposition": (
        "policy_schema_detector_fixture_runner_validator_reused_with_"
        "fresh_g0_g3_identity_binding"
    ),
}
FIXTURE_MANIFEST = (
    V2_ROOT
    / "tests"
    / "fixtures"
    / "public_text_quality_acceptance"
    / "foundation_fixtures.json"
)

CURRENT_GENERATION_ROOT = current_layer3_generation_root()


def default_attempts_root() -> Path:
    return (
        require_external_workspace("IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT")
        / STAGING_ROUND_ID
        / "attempts"
    )
OWNER_INPUT_ROOT = V2_ROOT / "owner_inputs" / ROUND_ID
REVIEWER_INPUT_ROOT = V2_ROOT / "reviewer_inputs" / ROUND_ID
LIVE_REQUIRED_VALIDATIONS = (
    REPO_ROOT / "Iris" / "validation" / "execution" / "required_validations.json"
)
NATURALIZATION_COMPILER_IMPLEMENTATION_FILES = compiler_source_paths(REPO_ROOT)

OFFICIAL_MODES = (
    "phase0-binding",
    "phase1-contracts",
    "phase2-policy",
    "phase3-validator",
    "phase4-adversarial",
    "phase5-disposition",
    "phase6-gate-candidate",
    "phase6-adopt-gate",
    "phase7-freeze",
    "phase7-finalize",
)

PHASE_ARTIFACTS = {
    0: (
        "evaluation_subject_manifest.json",
        "cross_plan_handoff_binding_report.json",
        "current_input_constituent_manifest.json",
        "canonical_entries_projection.jsonl",
        "canonical_entries_digest.json",
        "canonical_metric_projection.jsonl",
        "canonical_metric_projection_digest.json",
        "acceptance_input_binding_manifest.json",
        "protected_surface_no_mutation_report.json",
        "vcs_required_surface_preflight.json",
    ),
    1: (
        "metric_registry.json",
        "denominator_registry.json",
        "profile_section_applicability_matrix.json",
        "metric_overlap_and_partition_report.json",
        "unadopted_axis_separation_report.json",
        "metric_denominator_contract_validation_report.json",
    ),
    2: (
        "public_text_quality_acceptance_policy.json",
        "applicable_waiver_set.json",
        "policy_threshold_rationale_report.json",
    ),
    3: (
        "validator_contract_report.json",
        "validator_determinism_report.json",
        "fail_closed_path_report.json",
    ),
    4: (
        "adversarial_fixture_manifest.json",
        "negative_fixture_results.json",
        "threshold_boundary_report.json",
        "row_occurrence_confusion_report.json",
        "unadopted_axis_attack_report.json",
        "waiver_bypass_attack_report.json",
        "metamorphic_determinism_report.json",
        "adversarial_review.md",
    ),
    5: (
        "evaluation_subject_metric_snapshot.json",
        "evaluation_subject_raw_metric_report.json",
        "evaluation_subject_disposition.json",
        "evaluation_subject_disposition.md",
        "evaluation_subject_disposition_hash_manifest.json",
        "protected_surface_no_mutation_report.json",
    ),
}

ATTEMPT_ID_PATTERN = re.compile(r"^attempt-[0-9]{4,}-[a-z0-9][a-z0-9-]*$")
GIT_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")

PLAN_DOC = (
    REPO_ROOT
    / "docs"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md"
)
NATURALIZATION_PLAN_DOC = (
    REPO_ROOT
    / "docs"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md"
)

GLOBAL_SYNC_MANIFEST = (
    REPO_ROOT / "docs" / "iris_aa49_four_plan_execution_sync_manifest.json"
)
G2_ATTEMPT_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_facts_authority"
    / "attempts"
    / "attempt-0022"
)
G0_G1_RELEASE_BINDING = (
    G2_ATTEMPT_ROOT
    / "phase0_plan_and_decisions"
    / "g0_g1_release_binding.json"
)
G2_SELECTED_SUCCESSOR_BINDING = (
    G2_ATTEMPT_ROOT
    / "phase11_successor"
    / "selected_successor_input_binding.json"
)
G2_SEALED_SUCCESSOR_RECEIPT = (
    G2_ATTEMPT_ROOT / "phase11_successor" / "sealed_successor_receipt.json"
)
G2_SEALED_SUCCESSOR_CLOSEOUT = (
    G2_ATTEMPT_ROOT / "phase13_closeout" / "sealed_successor_closeout.json"
)
G2_TERMINAL_HASH_SEAL = (
    G2_ATTEMPT_ROOT / "phase13_closeout" / "terminal_hash_seal.json"
)
G3_ATTEMPT_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_registry_operational_cutover"
    / "attempts"
    / "attempt-0009"
)
G3_REGISTRY_ADOPTION_RECEIPT = (
    G3_ATTEMPT_ROOT / "closeout" / "registry_adoption_receipt.json"
)
G3_CURRENT_IDENTITY_REPORT = (
    G3_ATTEMPT_ROOT / "closeout" / "current_identity_report.json"
)
G3_TERMINAL_HASH_SEAL = (
    G3_ATTEMPT_ROOT / "closeout" / "terminal_hash_seal.json"
)
CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
CURRENT_INPUT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"

SEALED_PREREQUISITE_RAW_SHA256 = {
    G0_G1_RELEASE_BINDING: (
        "35bf9c5d4cd5b3dfd9ecaf397a67866d75b58b2ddf4eae2c456e66704503a9e2"
    ),
    G2_SELECTED_SUCCESSOR_BINDING: (
        "bbea40be6c9b174fbc1e25de217646e13584dde1e9fcb18fa424ccd8bf3f2f42"
    ),
    G2_SEALED_SUCCESSOR_RECEIPT: (
        "a4a1960c332246cf9f9c33d15d04568859a251c7d6988fab4d878ec235a3b4b5"
    ),
    G2_SEALED_SUCCESSOR_CLOSEOUT: (
        "fe77dc23a9b6c1296c8c54361bd1291fbb5fa09bd6a662ad02336c145f4507f7"
    ),
    G2_TERMINAL_HASH_SEAL: (
        "9a9a37731e8d76399f6b960a0e9beb21bcdd65d8ae39e511337527c5306d0c19"
    ),
    G3_REGISTRY_ADOPTION_RECEIPT: (
        "efcc387bb395b561ab67df0cab4e498fe0b429680fc6cc8f6dd96eb94ba49751"
    ),
    G3_CURRENT_IDENTITY_REPORT: (
        "71dadc9901b713d6927e66719f758f925c50735fc6bc887e8f6a6ba8e086dca8"
    ),
    G3_TERMINAL_HASH_SEAL: (
        "1f494ed0661627a82c3fcfd8465f2313fe0768cac82af09457e9ffc9e91b7ae1"
    ),
}
GLOBAL_SYNC_MANIFEST_GIT_BLOB_ID = "70035140563ed6cd7ad70b60a6fb36101ed50519"
GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256 = (
    "1f43bc3144f59f17774adac76f313ee67312c1818af120510de0c2591a9c426d"
)

FOUNDATION_DOCS = (
    REPO_ROOT / "docs" / "public_text_quality_metric_contract.md",
    REPO_ROOT / "docs" / "public_text_quality_denominator_contract.md",
    REPO_ROOT / "docs" / "public_text_quality_acceptance_policy.md",
    REPO_ROOT / "docs" / "public_text_quality_acceptance_claim_boundary.md",
    REPO_ROOT / "docs" / "public_text_quality_exception_policy.md",
    REPO_ROOT / "docs" / "public_text_quality_waiver_policy.md",
    REPO_ROOT / "docs" / "public_text_quality_freshness_policy.md",
)

FOUNDATION_IMPLEMENTATION_FILES = (
    TOOLS_DIR / "naturalization_compiler_identity.py",
    TOOLS_DIR / "public_text_quality_acceptance.py",
    TOOLS_DIR / "run_public_text_quality_acceptance.py",
    TOOLS_DIR / "validate_public_text_quality_acceptance.py",
    PUBLIC_TEXT_DOMAIN_DIR / "inputs.py",
    PUBLIC_TEXT_DOMAIN_DIR / "evaluate.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_context.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_infrastructure.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_contracts.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_rules.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_reporting.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_emission.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_foundation_application.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_attempt_context.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_policy.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_assurance.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_disposition.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_validation.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_cli.py",
    PUBLIC_TEXT_DOMAIN_DIR / "acceptance_validation_cli.py",
)

EVALUATION_SUBJECT_KINDS = (
    "current_runtime_payload",
    "dvf_3_3_korean_naturalization_candidate",
)
DISPOSITION_CLASSES = ("blocking_gate", "advisory_debt", "non_claim")
QUALIFIED_DISPOSITIONS = ("accepted", "blocked", "deferred_internal_debt")
CANDIDATE_STRUCTURAL_STATUSES = (
    "emitted_direct",
    "satisfied_by_verified_fusion",
    "satisfied_by_verified_suppression",
    "not_required",
    "missing",
)
SATISFIED_REQUIRED_STRUCTURAL_STATUSES = (
    "emitted_direct",
    "satisfied_by_verified_fusion",
    "satisfied_by_verified_suppression",
)

REQUIRED_HANDOFF_CONSTITUENT_IDS = (
    "naturalization_attempt_id",
    "foundation_contract_hash",
    "candidate_rendered_hash",
    "candidate_manifest_hash",
    "source_proposition_manifest_hash",
    "body_plan_requirement_digest",
    "structural_satisfaction_ledger_hash",
    "semantic_preservation_report_hash",
    "raw_detector_report_hash",
    "human_review_sample_manifest_hash",
    "human_review_decision_hash",
    "compiler_implementation_hash",
    "korean_prose_policy_hash",
    "corpus_manifest_hash",
    "protected_surface_no_mutation_report_hash",
    "requested_evaluation_subject_kind",
)
TEXT_HANDOFF_CONSTITUENT_IDS = frozenset(
    {
        "foundation_contract_hash",
        "candidate_rendered_hash",
        "candidate_manifest_hash",
        "source_proposition_manifest_hash",
        "body_plan_requirement_digest",
        "structural_satisfaction_ledger_hash",
        "semantic_preservation_report_hash",
        "raw_detector_report_hash",
        "human_review_sample_manifest_hash",
        "human_review_decision_hash",
        "korean_prose_policy_hash",
        "corpus_manifest_hash",
        "protected_surface_no_mutation_report_hash",
    }
)
TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID = (
    "git_head_blob_raw_sha256_with_filtered_or_lf_canonical_working_v1"
)
PROTECTED_SNAPSHOT_IDENTITY_ALGORITHM_ID = (
    "git_head_blob_raw_sha256_with_filtered_or_lf_canonical_working_text_"
    "and_raw_binary_v1"
)

VOLATILE_CANONICAL_FIELDS = frozenset(
    {"generated_at", "host", "absolute_path", "mtime"}
)

RAW_DETECTOR_IDS = (
    "duplicate_proposition_realization",
    "repeated_identity_noun_window",
    "banned_internal_abstraction",
    "repeated_skeleton_concentration",
    "paragraph_fragmentation",
    "passive_translationese_pattern",
    "empty_or_filler_sentence",
)

__all__ = (
    "ATTEMPT_ID_PATTERN", "CANDIDATE_STRUCTURAL_STATUSES", "CURRENT_FACTS",
    "CURRENT_INPUT_MANIFEST", "default_attempts_root", "DEFAULT_FOUNDATION_ROOT",
    "DISPOSITION_CLASSES", "EVALUATION_SUBJECT_KINDS", "FIXTURE_MANIFEST",
    "FIXTURE_SCHEMA_VERSION", "FOUNDATION_CONTRACT_NAME",
    "FOUNDATION_CONTRACT_VERSION", "FOUNDATION_DOCS",
    "FOUNDATION_IMPLEMENTATION_FILES", "FOUNDATION_SCHEMA_VERSION",
    "FOUR_PLAN_SYNC_PROJECTION_SHA256", "G0_G1_RELEASE_BINDING",
    "G2_ATTEMPT_ROOT", "G2_SEALED_SUCCESSOR_CLOSEOUT",
    "G2_SEALED_SUCCESSOR_RECEIPT", "G2_SELECTED_SUCCESSOR_BINDING",
    "G2_TERMINAL_HASH_SEAL", "G3_ATTEMPT_ROOT", "G3_CURRENT_IDENTITY_REPORT",
    "G3_REGISTRY_ADOPTION_RECEIPT", "G3_TERMINAL_HASH_SEAL", "GIT_COMMIT_PATTERN",
    "GLOBAL_SYNC_CONTRACT_ID", "GLOBAL_SYNC_MANIFEST",
    "GLOBAL_SYNC_MANIFEST_GIT_BLOB_ID", "GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256",
    "LIVE_REQUIRED_VALIDATIONS", "NATURALIZATION_COMPILER_IMPLEMENTATION_FILES",
    "NATURALIZATION_PLAN_DOC", "OFFICIAL_MODES", "OWNER_INPUT_ROOT",
    "PHASE_ARTIFACTS", "PLAN_DOC", "PREDECESSOR_FOUNDATION",
    "PROTECTED_SNAPSHOT_IDENTITY_ALGORITHM_ID", "PUBLIC_TEXT_DOMAIN_DIR",
    "QUALIFIED_DISPOSITIONS", "RAW_DETECTOR_IDS", "READINESS_REPORT_NAME",
    "READINESS_SCHEMA_VERSION", "REPO_ROOT", "REQUIRED_HANDOFF_CONSTITUENT_IDS",
    "REVIEWER_INPUT_ROOT", "ROUND_ID", "SATISFIED_REQUIRED_STRUCTURAL_STATUSES",
    "SEALED_PREREQUISITE_RAW_SHA256", "STAGING_ROUND_ID", "SYNC_CONTRACT_ID",
    "TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID", "TEXT_HANDOFF_CONSTITUENT_IDS",
    "TOOLING_PACKAGE_SOURCE_DIR", "TOOLS_DIR", "V2_ROOT",
    "VOLATILE_CANONICAL_FIELDS",
)
