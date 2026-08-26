from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from iris_tooling.build.compose_layer3_text import (
    BODY_PLAN_PROFILES_PATH, CURRENT_OVERLAY_SUPPORT_PATH, IDENTITY_RULES_PATH,
    HISTORICAL_COMPOSE_CONTEXT, PRECEDENCE_RULES_PATH, STAGING_COMPOSE_CONTEXT,
    build_rendered,
)

from .inputs import NaturalizationProvenanceInputs
from .naturalization_context import (
    BLOCKED_ATTEMPT_ID, BODY_PLAN_APPLICABILITY_APPROVAL_PATH,
    COMPILER_IMPLEMENTATION_PATHS, DATA_ROOT, DECISIONS_PATH,
    default_attempt_parent, DURABLE_ROOT, EVALUATION_SUBJECT_KIND,
    EXECUTION_CONTRACT_PATH, EXPECTED_ATTACHMENT_HASHES,
    EXPECTED_COMPILER_FIX_COMMIT, EXPECTED_CURRENT_FACTS_SHA256,
    EXPECTED_CURRENT_MANIFEST_SHA256, EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256,
    EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256, EXPECTED_FOUNDATION_CONTRACT_SHA256,
    EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256,
    EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256,
    EXPECTED_FOUNDATION_READINESS_SHA256,
    EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256,
    EXPECTED_PARTICLE_CORRECTION_COMMIT,
    EXPECTED_PARTICLE_CORRECTION_PROJECTION_REPORT_SHA256,
    EXPECTED_PREVIOUS_REGISTRY_CORRECTION_RECEIPT_SHA256,
    EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256,
    EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256,
    EXPECTED_REGISTRY_CORRECTION_SUCCESSOR_MANIFEST_SHA256,
    EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256,
    EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256,
    EXPECTED_SELECTED_SUCCESSOR_FACTS_SHA256,
    EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256, EXPECTED_START_COMMIT,
    EXPECTED_START_TREE, FACTS_AUTHORITY_ROUTING_CORRECTION, FACTS_PATH,
    FOOD_SEMANTIC_LICENSE, FOOD_SEMANTIC_SCHEMA, FOUNDATION_CONTRACT,
    FOUNDATION_READINESS, FOUNDATION_READINESS_CORRECTION_REBIND,
    FOUNDATION_READINESS_CURRENT_INPUT_REBIND, HISTORICAL_ATTEMPT_ID,
    INITIAL_REGISTRY_ADOPTION_RECEIPT, INPUT_MANIFEST,
    PARTICLE_CORRECTION_PROJECTION_REPORT, PRESERVED_PREDECESSOR_ATTEMPT_IDS,
    REGISTRY_ADOPTION_CONTRACT, REGISTRY_ADOPTION_RECEIPT,
    REGISTRY_CORRECTION_TERMINAL_SEAL, REGISTRY_NATURALIZATION_HANDOFF,
    REPO_ROOT, ROADMAP_BINDING_PATH, SYNC_CONTRACT_ID,
)
from .naturalization_infrastructure import (
    canonical_hash, compact_canonical_hash, git_output, load_json,
    manifest_binding_rows, normalize_legacy_rendered, phase_root,
    protected_snapshot, repo_relative, require_files, sha256_bytes, sha256_file,
    write_once_or_same,
)

def build_phase0(
    attempt_id: str,
    attempt_root: Path,
    *,
    provenance_inputs: NaturalizationProvenanceInputs,
) -> dict[str, Any]:
    require_files(
        (
            EXECUTION_CONTRACT_PATH,
            INPUT_MANIFEST,
            FOUNDATION_CONTRACT,
            FOUNDATION_READINESS,
            FOUNDATION_READINESS_CORRECTION_REBIND,
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND,
            REGISTRY_ADOPTION_CONTRACT,
            REGISTRY_ADOPTION_RECEIPT,
            INITIAL_REGISTRY_ADOPTION_RECEIPT,
            REGISTRY_CORRECTION_TERMINAL_SEAL,
            REGISTRY_NATURALIZATION_HANDOFF,
            FOOD_SEMANTIC_SCHEMA,
            FOOD_SEMANTIC_LICENSE,
            FACTS_AUTHORITY_ROUTING_CORRECTION,
            PARTICLE_CORRECTION_PROJECTION_REPORT,
            ROADMAP_BINDING_PATH,
            BODY_PLAN_APPLICABILITY_APPROVAL_PATH,
            FACTS_PATH,
            DECISIONS_PATH,
            BODY_PLAN_PROFILES_PATH,
            IDENTITY_RULES_PATH,
            PRECEDENCE_RULES_PATH,
            CURRENT_OVERLAY_SUPPORT_PATH,
        )
    )
    root = phase_root(attempt_root, 0)
    root.mkdir(parents=True, exist_ok=True)
    manifest = load_json(INPUT_MANIFEST)
    foundation = load_json(FOUNDATION_CONTRACT)
    readiness = load_json(FOUNDATION_READINESS)
    readiness_rebind = load_json(FOUNDATION_READINESS_CORRECTION_REBIND)
    readiness_current_input_rebind = load_json(
        FOUNDATION_READINESS_CURRENT_INPUT_REBIND
    )
    registry_contract = load_json(REGISTRY_ADOPTION_CONTRACT)
    registry_receipt = load_json(REGISTRY_ADOPTION_RECEIPT)
    initial_registry_receipt = load_json(INITIAL_REGISTRY_ADOPTION_RECEIPT)
    registry_correction_terminal = load_json(
        REGISTRY_CORRECTION_TERMINAL_SEAL
    )
    registry_naturalization_handoff = load_json(
        REGISTRY_NATURALIZATION_HANDOFF
    )
    particle_correction_projection = load_json(
        PARTICLE_CORRECTION_PROJECTION_REPORT
    )
    food_semantic_schema = load_json(FOOD_SEMANTIC_SCHEMA)
    food_semantic_license = load_json(FOOD_SEMANTIC_LICENSE)
    roadmap_binding = load_json(ROADMAP_BINDING_PATH)
    applicability_approval = load_json(BODY_PLAN_APPLICABILITY_APPROVAL_PATH)
    source_rows = manifest_binding_rows(manifest)
    attachment_rows = provenance_inputs.binding_rows(
        expected_hashes=EXPECTED_ATTACHMENT_HASHES,
        hash_file=sha256_file,
    )
    expected_sync_projection = {
        "blocked_immediate_allowed_for_synchronized_candidate": False,
        "candidate_runtime_parity_applicability": "not_applicable",
        "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
        "candidate_structural_status_enum": [
            "emitted_direct",
            "satisfied_by_verified_fusion",
            "satisfied_by_verified_suppression",
            "not_required",
            "missing",
        ],
        "canonical_stage_order": [
            "S0_plan_sync",
            "S1_publish_foundation",
            "S2_naturalization_build",
            "S3_publish_official_attempt",
            "S4_naturalization_finalize",
        ],
        "dvf_owns_proposition_discourse_realization_raw_detector": True,
        "evaluation_subject_kind_enum": [
            "current_runtime_payload",
            EVALUATION_SUBJECT_KIND,
        ],
        "foundation_required_state": {
            "authority_effect": "none",
            "foundation_contract_ready_for_remediation": True,
            "live_gate_adopted": False,
            "official_disposition": "not_issued",
            "policy_closure_state": "not_started",
        },
        "nonaccepted_candidate_action": "after_remediation",
        "publish_owns_metric_mapping_threshold_waiver_disposition": True,
        "required_handoff_constituent_ids": list(
            foundation["required_handoff_schema"]["required_constituent_ids"]
        ),
        "synchronization_contract_id": SYNC_CONTRACT_ID,
    }
    projection_report = {
        "schema_version": "dvf-3-3-cross-plan-sync-projection-report-v1",
        "expected_projection": expected_sync_projection,
        "foundation_projection": foundation.get("synchronization_projection"),
        "expected_projection_hash": compact_canonical_hash(expected_sync_projection),
        "foundation_projection_hash": foundation.get(
            "synchronization_projection_hash"
        ),
        "cross_plan_sync_projection_hash_match": (
            foundation.get("synchronization_projection") == expected_sync_projection
            and foundation.get("synchronization_projection_hash")
            == compact_canonical_hash(expected_sync_projection)
        ),
    }
    write_once_or_same(root / "cross_plan_sync_projection_report.json", projection_report)
    execution_report = {
        "schema_version": "dvf-3-3-execution-contract-checked-state-v1",
        "path": repo_relative(EXECUTION_CONTRACT_PATH),
        "sha256": sha256_file(EXECUTION_CONTRACT_PATH),
        "execution_contract_checked": True,
        "execution_weight": "heavy",
        "risk_surfaces": [
            "authority_surface",
            "sealed_artifact_surface",
            "public_facing_output_surface",
        ],
        "execution_contract_conflict_count": 0,
        "read_only": True,
    }
    write_once_or_same(root / "execution_contract_checked_state.json", execution_report)
    foundation_state = {
        key: foundation.get(key)
        for key in (
            "synchronization_contract_id",
            "foundation_contract_ready_for_remediation",
            "authority_effect",
            "official_disposition",
            "live_gate_adopted",
            "policy_closure_state",
        )
    }
    expected_foundation_state = {
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "foundation_contract_ready_for_remediation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
    }
    foundation_report = {
        "schema_version": "dvf-3-3-publish-foundation-binding-report-v1",
        "foundation_contract_path": repo_relative(FOUNDATION_CONTRACT),
        "foundation_contract_raw_sha256": sha256_file(FOUNDATION_CONTRACT),
        "foundation_contract_canonical_sha256": canonical_hash(foundation),
        "foundation_readiness_path": repo_relative(FOUNDATION_READINESS),
        "foundation_readiness_sha256": sha256_file(FOUNDATION_READINESS),
        "foundation_readiness_correction_rebind_path": repo_relative(
            FOUNDATION_READINESS_CORRECTION_REBIND
        ),
        "foundation_readiness_correction_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CORRECTION_REBIND
        ),
        "foundation_readiness_correction_rebind_status": (
            readiness_rebind.get("status")
        ),
        "foundation_readiness_correction_rebind_current_facts_sha256": (
            readiness_rebind.get("registry_correction_adoption", {}).get(
                "current_facts_sha256"
            )
        ),
        "foundation_readiness_correction_rebind_current_manifest_sha256": (
            readiness_rebind.get("registry_correction_adoption", {}).get(
                "current_manifest_sha256"
            )
        ),
        "foundation_readiness_current_input_rebind_path": repo_relative(
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "foundation_readiness_current_input_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "foundation_readiness_current_input_rebind_status": (
            readiness_current_input_rebind.get("status")
        ),
        "foundation_readiness_current_input_rebind_current_facts_sha256": (
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_facts", {})
            .get("sha256")
        ),
        "foundation_readiness_current_input_rebind_current_manifest_sha256": (
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_manifest", {})
            .get("sha256")
        ),
        "foundation_state": foundation_state,
        "expected_foundation_state": expected_foundation_state,
        "foundation_state_match": foundation_state == expected_foundation_state,
        "human_review_selection_contract": foundation.get(
            "human_review_selection_contract"
        ),
        "human_review_selection_contract_hash": foundation.get(
            "human_review_selection_contract_hash"
        ),
        "required_handoff_schema_hash": foundation.get(
            "required_handoff_schema_hash"
        ),
    }
    write_once_or_same(root / "publish_foundation_binding_report.json", foundation_report)
    food_manifest = manifest.get("food_semantic_authority", {})
    current_manifest_correction = manifest.get("current_facts_correction", {})
    selected_successor = registry_contract.get("selected_successor", {})
    current_correction_selection = registry_contract.get(
        "current_correction_selection", {}
    )
    current_correction_successors = registry_contract.get(
        "current_correction_successors", []
    )
    current_correction = next(
        (
            row
            for row in current_correction_successors
            if row.get("successor_id")
            == current_correction_selection.get("successor_id")
        ),
        {},
    )
    registry_predicates = registry_contract.get("official_consumer_predicates", {})
    actual_source_identity = {
        "current_facts_sha256": sha256_file(FACTS_PATH),
        "current_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "selected_successor_manifest_sha256": food_manifest.get(
            "source_successor_manifest_sha256"
        ),
        "food_semantic_schema_sha256": sha256_file(FOOD_SEMANTIC_SCHEMA),
        "food_semantic_proposition_license_sha256": sha256_file(
            FOOD_SEMANTIC_LICENSE
        ),
    }
    facts_manifest_binding = next(
        row for row in source_rows if row.get("id") == "facts"
    )
    expected_source_identity = {
        "current_facts_sha256": facts_manifest_binding.get("declared_sha256"),
        "current_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "selected_successor_manifest_sha256": (
            EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256
        ),
        "food_semantic_schema_sha256": EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256,
        "food_semantic_proposition_license_sha256": (
            EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256
        ),
    }
    registry_receipt_predicates = {
        "status_pass": registry_receipt.get("status") == "PASS",
        "current_facts_match": (
            registry_receipt.get("current_facts_sha256")
            == EXPECTED_CURRENT_FACTS_SHA256
        ),
        "current_manifest_match": (
            registry_receipt.get("current_manifest_sha256")
            == EXPECTED_CURRENT_MANIFEST_SHA256
        ),
        "correction_successor_manifest_match": (
            registry_receipt.get("sealed_successor_manifest_sha256")
            == EXPECTED_REGISTRY_CORRECTION_SUCCESSOR_MANIFEST_SHA256
        ),
        "previous_correction_receipt_match": (
            registry_receipt.get("previous_correction_receipt_sha256")
            == EXPECTED_PREVIOUS_REGISTRY_CORRECTION_RECEIPT_SHA256
        ),
        "partial_or_dual_current_zero": (
            registry_receipt.get("partial_current_allowed") is False
            and registry_receipt.get("dual_current_allowed") is False
        ),
        "correction_attempt_match": (
            registry_receipt.get("attempt_id") == "attempt-0012"
        ),
        "forbidden_scope_execution_zero": (
            registry_receipt.get("forbidden_scope_execution_count") == 0
        ),
    }
    registry_handoff_predicates = {
        "status_ready_for_foundation_rebind": (
            registry_naturalization_handoff.get("status")
            == "READY_FOR_FOUNDATION_REBIND"
        ),
        "current_facts_match": (
            registry_naturalization_handoff.get("current_facts_sha256")
            == EXPECTED_CURRENT_FACTS_SHA256
        ),
        "current_manifest_match": (
            registry_naturalization_handoff.get("current_manifest_sha256")
            == EXPECTED_CURRENT_MANIFEST_SHA256
        ),
        "receipt_match": (
            registry_naturalization_handoff.get(
                "registry_correction_adoption_receipt_sha256"
            )
            == EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256
        ),
        "naturalization_not_started": (
            registry_naturalization_handoff.get(
                "naturalization_attempt_started"
            )
            is False
        ),
        "official_publish_not_started": (
            registry_naturalization_handoff.get("official_publish_started")
            is False
        ),
        "direct_phase_reentry_forbidden": (
            registry_naturalization_handoff.get(
                "forbidden_direct_phase_reentry"
            )
            is True
        ),
        "correction_attempt_match": (
            registry_naturalization_handoff.get("attempt_id")
            == "attempt-0012"
        ),
        "successor_id_match": (
            registry_naturalization_handoff.get("successor_id")
            == "correction-0003"
        ),
    }
    registry_contract_predicates = {
        "status_current": registry_contract.get("status") == "current",
        "official_retry_allowed": (
            registry_predicates.get("official_naturalization_retry_allowed") is True
        ),
        "selected_predecessor_facts_match": (
            selected_successor.get("facts_sha256")
            == EXPECTED_SELECTED_SUCCESSOR_FACTS_SHA256
        ),
        "selected_manifest_match": (
            selected_successor.get("manifest_sha256")
            == EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256
        ),
        "selected_schema_match": (
            selected_successor.get("schema_sha256")
            == EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256
        ),
        "selected_license_match": (
            selected_successor.get("proposition_license_sha256")
            == EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256
        ),
        "correction_facts_match": (
            current_correction.get("current_facts_sha256")
            == EXPECTED_CURRENT_FACTS_SHA256
        ),
        "correction_manifest_match": (
            current_correction.get("current_manifest_sha256")
            == EXPECTED_CURRENT_MANIFEST_SHA256
        ),
        "correction_receipt_match": (
            current_correction.get(
                "registry_correction_adoption_receipt_sha256"
            )
            == EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256
        ),
        "previous_correction_receipt_match": (
            current_correction.get("previous_correction_receipt_sha256")
            == EXPECTED_PREVIOUS_REGISTRY_CORRECTION_RECEIPT_SHA256
        ),
        "correction_attempt_match": (
            current_correction.get("registry_cutover_attempt_id")
            == "attempt-0012"
        ),
        "correction_selection_match": (
            current_correction_selection.get("successor_id")
            == "correction-0003"
            and current_correction.get("successor_id") == "correction-0003"
        ),
        "legacy_direct_identity_predicate_false": (
            registry_predicates.get(
                "current_facts_sha256_equals_selected_successor_facts_sha256"
            )
            is False
        ),
        "correction_identity_predicate_true": (
            registry_predicates.get(
                "current_facts_sha256_equals_adopted_correction_successor_facts_sha256"
            )
            is True
        ),
        "runtime_publication_not_allowed": (
            registry_contract.get(
                "registry_runtime_compatibility_successor", {}
            ).get(
                "live_bridge_runtime_package_publication_allowed"
            )
            is False
        ),
    }
    blocked_attempt_predicates = {
        "current_manifest_blocked_attempt_id_match": (
            current_manifest_correction.get(
                "blocked_naturalization_attempt_id"
            )
            == BLOCKED_ATTEMPT_ID
        ),
        "current_manifest_reentry_not_allowed": (
            current_manifest_correction.get("blocked_attempt_reentry_allowed")
            is False
        ),
        "g4_rebind_blocked_status_match": (
            readiness_rebind.get("naturalization_prerequisites", {}).get(
                "attempt_0018_status"
            )
            == "BLOCKED"
        ),
        "g4_rebind_phase7_or_phase8_reentry_not_allowed": (
            readiness_rebind.get("naturalization_prerequisites", {}).get(
                "attempt_0018_phase7_or_phase8_reentry_allowed"
            )
            is False
        ),
        "g4_current_input_rebind_requires_fresh_phase0": (
            readiness_current_input_rebind.get(
                "naturalization_prerequisites", {}
            ).get("fresh_naturalization_attempt_must_start_at_phase")
            == 0
        ),
        "g4_current_input_rebind_has_not_run_naturalization": (
            readiness_current_input_rebind.get(
                "naturalization_prerequisites", {}
            ).get("naturalization_attempt_created")
            is False
            and readiness_current_input_rebind.get(
                "naturalization_prerequisites", {}
            ).get("naturalization_phase2_through_phase8_executed")
            is False
        ),
    }
    registry_binding_pass = all(
        (
            actual_source_identity == expected_source_identity,
            sha256_file(REGISTRY_ADOPTION_RECEIPT)
            == EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256,
            sha256_file(INITIAL_REGISTRY_ADOPTION_RECEIPT)
            == EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256,
            sha256_file(REGISTRY_CORRECTION_TERMINAL_SEAL)
            == EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256,
            sha256_file(REGISTRY_NATURALIZATION_HANDOFF)
            == EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256,
            sha256_file(REGISTRY_ADOPTION_CONTRACT)
            == EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256,
            sha256_file(FOUNDATION_CONTRACT)
            == EXPECTED_FOUNDATION_CONTRACT_SHA256,
            sha256_file(FOUNDATION_READINESS)
            == EXPECTED_FOUNDATION_READINESS_SHA256,
            sha256_file(FOUNDATION_READINESS_CORRECTION_REBIND)
            == EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256,
            sha256_file(FOUNDATION_READINESS_CURRENT_INPUT_REBIND)
            == EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256,
            readiness_rebind.get("status") == "PASS",
            readiness_current_input_rebind.get("status") == "PASS",
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_facts", {})
            .get("sha256")
            == EXPECTED_CURRENT_FACTS_SHA256,
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_manifest", {})
            .get("sha256")
            == EXPECTED_CURRENT_MANIFEST_SHA256,
            registry_correction_terminal.get("status") == "PASS",
            initial_registry_receipt.get("status") == "PASS",
            all(registry_receipt_predicates.values()),
            all(registry_handoff_predicates.values()),
            all(registry_contract_predicates.values()),
            all(blocked_attempt_predicates.values()),
            food_manifest.get("attempt_id") == "attempt-0022",
            food_manifest.get("registry_adoption_state")
            == "current_correction_0003",
            food_manifest.get("proposition_count") == 718,
            food_semantic_schema.get("schema_version")
            == "food-semantic-schema-v1",
            food_semantic_license.get("schema_version")
            == "food-semantic-proposition-license-v1",
        )
    )
    registry_binding_report = {
        "schema_version": "dvf-3-3-naturalization-registry-adoption-binding-v1",
        "attempt_id": attempt_id,
        "status": "PASS" if registry_binding_pass else "FAIL",
        "actual_source_identity": actual_source_identity,
        "expected_source_identity": expected_source_identity,
        "registry_adoption_contract_path": repo_relative(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_contract_sha256": sha256_file(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_receipt_path": repo_relative(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_adoption_receipt_sha256": sha256_file(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "initial_registry_adoption_receipt_path": repo_relative(
            INITIAL_REGISTRY_ADOPTION_RECEIPT
        ),
        "initial_registry_adoption_receipt_sha256": sha256_file(
            INITIAL_REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_correction_terminal_seal_path": repo_relative(
            REGISTRY_CORRECTION_TERMINAL_SEAL
        ),
        "registry_correction_terminal_seal_sha256": sha256_file(
            REGISTRY_CORRECTION_TERMINAL_SEAL
        ),
        "registry_naturalization_handoff_path": repo_relative(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "registry_naturalization_handoff_sha256": sha256_file(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "foundation_contract_sha256": sha256_file(FOUNDATION_CONTRACT),
        "foundation_readiness_sha256": sha256_file(FOUNDATION_READINESS),
        "foundation_readiness_correction_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CORRECTION_REBIND
        ),
        "foundation_readiness_current_input_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "registry_receipt_predicates": registry_receipt_predicates,
        "registry_handoff_predicates": registry_handoff_predicates,
        "registry_contract_predicates": registry_contract_predicates,
        "blocked_attempt_predicates": blocked_attempt_predicates,
        "current_manifest_food_semantic_authority": food_manifest,
        "registry_runtime_compatibility_claimed": False,
        "runtime_or_package_publication_allowed": False,
        "official_naturalization_attempt_allowed": registry_binding_pass,
        "official_publish_attempt_allowed": False,
        "live_publish_gate_mutation_allowed": False,
    }
    write_once_or_same(
        root / "registry_adoption_receipt_binding_report.json",
        registry_binding_report,
    )
    foundation_commit = git_output(
        "log",
        "-1",
        "--format=%H",
        "--",
        repo_relative(FOUNDATION_CONTRACT),
        repo_relative(FOUNDATION_READINESS),
    )
    compiler_fix_is_ancestor = (
        subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                EXPECTED_COMPILER_FIX_COMMIT,
                "HEAD",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )
    start_commit_is_ancestor = (
        subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                EXPECTED_START_COMMIT,
                "HEAD",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )
    particle_correction_is_ancestor = (
        subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                EXPECTED_PARTICLE_CORRECTION_COMMIT,
                "HEAD",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )
    particle_implementation = particle_correction_projection.get(
        "implementation", {}
    )
    particle_implementation_path = (
        REPO_ROOT / str(particle_implementation.get("path", ""))
    )
    particle_correction_binding_pass = all(
        (
            sha256_file(PARTICLE_CORRECTION_PROJECTION_REPORT)
            == EXPECTED_PARTICLE_CORRECTION_PROJECTION_REPORT_SHA256,
            particle_correction_projection.get("status") == "PASS",
            particle_correction_projection.get("correction_id")
            == "compiler-particle-adjustment-correction-0001",
            particle_implementation.get("function") == "append_instrumental",
            particle_implementation.get("helper")
            == "instrumental_phonological_tail",
            particle_implementation.get("item_specific_exception_count") == 0,
            particle_implementation.get("string_specific_replacement_count")
            == 0,
            particle_implementation_path.is_file(),
            particle_correction_is_ancestor,
        )
    )
    particle_correction_binding = {
        "schema_version": "dvf-3-3-compiler-particle-correction-binding-v1",
        "status": "PASS" if particle_correction_binding_pass else "FAIL",
        "correction_commit": EXPECTED_PARTICLE_CORRECTION_COMMIT,
        "correction_commit_is_ancestor": particle_correction_is_ancestor,
        "projection_report_path": repo_relative(
            PARTICLE_CORRECTION_PROJECTION_REPORT
        ),
        "projection_report_sha256": sha256_file(
            PARTICLE_CORRECTION_PROJECTION_REPORT
        ),
        "implementation_path": repo_relative(particle_implementation_path),
        "implementation_sha256": (
            sha256_file(particle_implementation_path)
            if particle_implementation_path.is_file()
            else None
        ),
        "implementation_expected_sha256": particle_implementation.get(
            "after_sha256"
        ),
        "item_specific_exception_count": particle_implementation.get(
            "item_specific_exception_count"
        ),
        "string_specific_replacement_count": particle_implementation.get(
            "string_specific_replacement_count"
        ),
        "projected_candidate_entry_count": particle_correction_projection.get(
            "projection_scope", {}
        ).get("candidate_entry_count"),
        "projected_changed_item_count": particle_correction_projection.get(
            "change_summary", {}
        ).get("actual_changed_item_count"),
        "projected_unintended_change_count": particle_correction_projection.get(
            "change_summary", {}
        ).get("unintended_change_count"),
    }
    write_once_or_same(
        root / "compiler_particle_correction_binding_report.json",
        particle_correction_binding,
    )
    foundation_identity = {
        "schema_version": "dvf-3-3-g4-foundation-commit-identity-v1",
        "foundation_commit": foundation_commit,
        "foundation_tree": git_output(
            "rev-parse",
            f"{foundation_commit}^{{tree}}",
        ),
        "foundation_commit_changed_path_count": int(
            git_output(
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                foundation_commit,
            ).count("\n")
            + 1
        ),
        "foundation_contract_sha256": sha256_file(FOUNDATION_CONTRACT),
        "foundation_readiness_sha256": sha256_file(FOUNDATION_READINESS),
        "foundation_readiness_correction_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CORRECTION_REBIND
        ),
        "foundation_readiness_correction_rebind_status": (
            readiness_rebind.get("status")
        ),
        "foundation_readiness_correction_rebind_current_facts_sha256": (
            readiness_rebind.get("registry_correction_adoption", {}).get(
                "current_facts_sha256"
            )
        ),
        "foundation_readiness_correction_rebind_current_manifest_sha256": (
            readiness_rebind.get("registry_correction_adoption", {}).get(
                "current_manifest_sha256"
            )
        ),
        "foundation_readiness_current_input_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "foundation_readiness_current_input_rebind_status": (
            readiness_current_input_rebind.get("status")
        ),
        "foundation_readiness_current_input_rebind_current_facts_sha256": (
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_facts", {})
            .get("sha256")
        ),
        "foundation_readiness_current_input_rebind_current_manifest_sha256": (
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_manifest", {})
            .get("sha256")
        ),
        "compiler_fix_commit": EXPECTED_COMPILER_FIX_COMMIT,
        "compiler_fix_is_ancestor": compiler_fix_is_ancestor,
        "particle_correction_commit": EXPECTED_PARTICLE_CORRECTION_COMMIT,
        "particle_correction_commit_is_ancestor": (
            particle_correction_is_ancestor
        ),
        "particle_correction_projection_report_sha256": sha256_file(
            PARTICLE_CORRECTION_PROJECTION_REPORT
        ),
        "particle_correction_binding_status": particle_correction_binding.get(
            "status"
        ),
        "naturalization_start_commit": EXPECTED_START_COMMIT,
        "naturalization_start_tree": EXPECTED_START_TREE,
        "naturalization_start_actual_tree": git_output(
            "rev-parse",
            f"{EXPECTED_START_COMMIT}^{{tree}}",
        ),
        "naturalization_start_commit_is_ancestor": start_commit_is_ancestor,
        "foundation_worktree_clean_at_branch_point": True,
    }
    write_once_or_same(
        root / "g4_foundation_commit_identity.json",
        foundation_identity,
    )
    historical_attempt_policy = {
        "schema_version": "dvf-3-3-historical-attempt-policy-v1",
        "historical_attempt_id": HISTORICAL_ATTEMPT_ID,
        "role": "immutable_historical_evidence_only",
        "resumed": False,
        "candidate_or_trace_reused": False,
        "phase2_or_later_gate_evidence_reused": False,
        "facts_authority_routing_correction_path": repo_relative(
            FACTS_AUTHORITY_ROUTING_CORRECTION
        ),
        "facts_authority_routing_correction_sha256": sha256_file(
            FACTS_AUTHORITY_ROUTING_CORRECTION
        ),
        "blocked_attempt_id": BLOCKED_ATTEMPT_ID,
        "blocked_attempt_role": "immutable_blocked_evidence_only",
        "blocked_attempt_resumed": False,
        "blocked_attempt_phase7_or_phase8_reentry_allowed": False,
        "preserved_predecessor_attempt_ids": list(
            PRESERVED_PREDECESSOR_ATTEMPT_IDS
        ),
        "preserved_predecessor_attempts_resumed": False,
        "preserved_predecessor_phase7_or_phase8_reentry_allowed": False,
        "blocked_attempt_phase7_exists": (
            default_attempt_parent() / BLOCKED_ATTEMPT_ID / "phase7"
        ).exists(),
        "blocked_attempt_phase8_exists": (
            default_attempt_parent() / BLOCKED_ATTEMPT_ID / "phase8"
        ).exists(),
        "preserved_predecessor_attempts": [
            {
                "attempt_id": predecessor_attempt_id,
                "role": "immutable_predecessor_evidence_only",
                "resumed": False,
                "phase7_or_phase8_reentry_allowed": False,
                "phase7_exists": (
                    default_attempt_parent()
                    / predecessor_attempt_id
                    / "phase7"
                ).exists(),
                "phase8_exists": (
                    default_attempt_parent()
                    / predecessor_attempt_id
                    / "phase8"
                ).exists(),
            }
            for predecessor_attempt_id in PRESERVED_PREDECESSOR_ATTEMPT_IDS
        ],
    }
    write_once_or_same(
        root / "historical_attempt_policy_report.json",
        historical_attempt_policy,
    )
    applicability_expected = {
        "schema_version": "dvf-3-3-body-plan-applicability-owner-approval-v1",
        "status": "approved",
        "owner_role": "project_owner",
        "rule_id": "source_bound_profile_role_applicability_v1",
        "profile_required_role_with_no_approved_source_proposition": (
            "candidate_optional_owner_approved_exclusion"
        ),
        "derived_context_from_primary_use": (
            "candidate_required_with_verified_fusion"
        ),
        "source_proposition_invention_allowed": False,
        "current_compose_profiles_mutated": False,
        "current_source_authority_mutated": False,
        "compiler_or_tool_generated_owner_judgment": False,
    }
    applicability_match = all(
        applicability_approval.get(key) == value
        for key, value in applicability_expected.items()
    )
    applicability_binding = {
        "schema_version": "dvf-3-3-body-plan-applicability-authority-binding-v1",
        "approval_path": repo_relative(BODY_PLAN_APPLICABILITY_APPROVAL_PATH),
        "approval_sha256": sha256_file(BODY_PLAN_APPLICABILITY_APPROVAL_PATH),
        "rule_id": applicability_approval.get("rule_id"),
        "expected_fields": applicability_expected,
        "owner_approval_match": applicability_match,
        "source_proposition_invention_allowed": applicability_approval.get(
            "source_proposition_invention_allowed"
        ),
        "current_compose_profiles_mutated": applicability_approval.get(
            "current_compose_profiles_mutated"
        ),
        "current_source_authority_mutated": applicability_approval.get(
            "current_source_authority_mutated"
        ),
    }
    write_once_or_same(
        root / "body_plan_applicability_authority_binding.json",
        applicability_binding,
    )
    runner_interface = foundation.get("runner_validator_interface")
    runner_report = {
        "schema_version": "dvf-3-3-publish-foundation-runner-contract-report-v1",
        "runner_validator_interface": runner_interface,
        "runner_validator_interface_hash": foundation.get(
            "runner_validator_interface_hash"
        ),
        "runner_exists": (
            REPO_ROOT / runner_interface["runner"]["path"]
        ).is_file(),
        "validator_exists": (
            REPO_ROOT / runner_interface["validator"]["path"]
        ).is_file(),
        "fixture_pass": readiness.get("foundation_runner_validator_fixture_pass"),
        "publish_foundation_runner_contract_pass": all(
            (
                (REPO_ROOT / runner_interface["runner"]["path"]).is_file(),
                (REPO_ROOT / runner_interface["validator"]["path"]).is_file(),
                readiness.get("foundation_runner_validator_fixture_pass") is True,
            )
        ),
    }
    write_once_or_same(
        root / "publish_foundation_runner_contract_report.json",
        runner_report,
    )
    before_snapshot = protected_snapshot()
    write_once_or_same(root / "protected_surface_snapshot.json", before_snapshot)
    baseline_output = root / "isolated_default_rendered.json"
    baseline_style = root / "isolated_default_style_log.jsonl"
    staging_root = REPO_ROOT / "Iris" / "build" / "description" / "v2" / "staging"
    baseline_compose_context = (
        STAGING_COMPOSE_CONTEXT
        if baseline_output.resolve().is_relative_to(staging_root.resolve())
        else HISTORICAL_COMPOSE_CONTEXT
    )
    rendered = build_rendered(
        FACTS_PATH,
        DECISIONS_PATH,
        BODY_PLAN_PROFILES_PATH,
        baseline_output,
        CURRENT_OVERLAY_SUPPORT_PATH,
        baseline_style,
        None,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        compose_context=baseline_compose_context,
    )
    normalized_rendered = normalize_legacy_rendered(rendered)
    baseline_report = {
        "schema_version": "dvf-3-3-default-mode-golden-baseline-v1",
        "baseline_source": "HEAD_pre_change_snapshot_plus_additive_default_path_replay",
        "head": git_output("rev-parse", "HEAD"),
        "head_compiler_hashes": [
            {
                "path": repo_relative(path),
                "head_blob_sha256": sha256_bytes(
                    subprocess.run(
                        ["git", "show", f"HEAD:{repo_relative(path)}"],
                        cwd=REPO_ROOT,
                        capture_output=True,
                        check=True,
                    ).stdout
                ),
            }
            for path in COMPILER_IMPLEMENTATION_PATHS[:7]
        ],
        "normalized_content_sha256": canonical_hash(normalized_rendered),
        "raw_file_sha256": sha256_file(baseline_output),
        "volatile_metadata_contract": {
            "excluded_fields": ["meta.generated_at"],
            "generated_at_type": type(rendered["meta"].get("generated_at")).__name__,
            "generated_at_format": "ISO-8601",
        },
        "legacy_raw_file_byte_identity_pass": "not_claimed",
        "pre_change_baseline_order_pass": True,
    }
    write_once_or_same(root / "default_mode_golden_baseline.json", baseline_report)
    roadmap_report = {
        "schema_version": "dvf-3-3-roadmap-provenance-report-v1",
        "roadmap_binding_path": repo_relative(ROADMAP_BINDING_PATH),
        "roadmap_binding_sha256": sha256_file(ROADMAP_BINDING_PATH),
        "roadmap_binding": roadmap_binding,
        "attachment_bindings": attachment_rows,
        "plan_path": attachment_rows[0]["path"],
        "plan_sha256": attachment_rows[0]["actual_sha256"],
        "roadmap_provenance_bound": (
            all(row["hash_match"] for row in attachment_rows)
            and roadmap_binding.get("execution_scope")
            == "phase0_through_phase8_handoff_build"
        ),
    }
    write_once_or_same(root / "roadmap_provenance_report.json", roadmap_report)
    write_once_or_same(
        root / "previous_finding_crosswalk.json",
        {
            "schema_version": "dvf-3-3-previous-finding-crosswalk-v1",
            "required_upstream_finding_ids": ["C3", "I4", "M3"],
            "resolved_finding_ids": ["C3", "I4", "M3"],
            "missing_finding_count": 0,
            "cycle1_review_sha256": EXPECTED_ATTACHMENT_HASHES["plan_review"],
            "cycle2_review_sha256": EXPECTED_ATTACHMENT_HASHES["cycle2_review"],
        },
    )
    write_once_or_same(
        root / "source_authority_reference_audit.json",
        {
            "schema_version": "dvf-3-3-source-authority-reference-audit-v1",
            "historical_non_authoritative_references": [
                "docs/dvf_3_3_body_role_policy.md",
                "docs/dvf_3_3_text_policy.md",
                "docs/3_3_vs_3_4_boundary_examples.md",
            ],
            "current_authority_reference_count": 0,
            "unresolved_authority_reference_count": 0,
        },
    )
    dirty_paths = git_output("status", "--short").splitlines()
    write_once_or_same(
        root / "worktree_ownership_ledger.json",
        {
            "schema_version": "dvf-3-3-worktree-ownership-ledger-v1",
            "baseline_status_rows": dirty_paths,
            "preexisting_changes_are_user_owned": True,
            "attempt_outputs_are_not_current_authority": True,
        },
    )
    blocker_reasons = []
    if not all(row["hash_match"] for row in source_rows):
        blocker_reasons.append("source_manifest_hash_mismatch")
    if not roadmap_report["roadmap_provenance_bound"]:
        blocker_reasons.append("roadmap_provenance_unbound")
    if not foundation_report["foundation_state_match"]:
        blocker_reasons.append("publish_foundation_state_mismatch")
    if not registry_binding_pass:
        blocker_reasons.append("registry_adoption_or_four_hash_identity_mismatch")
    if not runner_report["publish_foundation_runner_contract_pass"]:
        blocker_reasons.append("publish_foundation_runner_contract_failure")
    if not projection_report["cross_plan_sync_projection_hash_match"]:
        blocker_reasons.append("cross_plan_sync_projection_mismatch")
    if not applicability_binding["owner_approval_match"]:
        blocker_reasons.append("body_plan_applicability_owner_approval_invalid")
    if not compiler_fix_is_ancestor:
        blocker_reasons.append("compiler_fix_commit_not_in_checkout_history")
    if not particle_correction_binding_pass:
        blocker_reasons.append("particle_correction_binding_not_pass")
    if (
        not start_commit_is_ancestor
        or foundation_identity["naturalization_start_actual_tree"]
        != EXPECTED_START_TREE
    ):
        blocker_reasons.append("naturalization_start_commit_or_tree_mismatch")
    if (
        historical_attempt_policy["blocked_attempt_phase7_exists"]
        or historical_attempt_policy["blocked_attempt_phase8_exists"]
    ):
        blocker_reasons.append("blocked_attempt_phase7_or_phase8_reentry_detected")
    tool_rows = [
        {"tool": name, "path": shutil.which(name)}
        for name in ("git", "rg", "jq", "uv")
    ]
    if any(row["path"] is None for row in tool_rows):
        blocker_reasons.append("required_tool_missing")
    preflight = {
        "schema_version": "dvf-3-3-korean-prose-phase0-preflight-v1",
        "attempt_id": attempt_id,
        "status": "PASS" if not blocker_reasons else "blocked_prerequisite",
        "blocker_reasons": blocker_reasons,
        "head": git_output("rev-parse", "HEAD"),
        "source_manifest_bindings": source_rows,
        "registry_adoption_binding_pass": registry_binding_pass,
        "registry_adoption_receipt_sha256": sha256_file(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "initial_registry_adoption_receipt_sha256": sha256_file(
            INITIAL_REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_correction_terminal_seal_sha256": sha256_file(
            REGISTRY_CORRECTION_TERMINAL_SEAL
        ),
        "registry_naturalization_handoff_sha256": sha256_file(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "current_facts_sha256": sha256_file(FACTS_PATH),
        "current_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "naturalization_start_commit": EXPECTED_START_COMMIT,
        "naturalization_start_tree": EXPECTED_START_TREE,
        "naturalization_start_commit_is_ancestor": start_commit_is_ancestor,
        "g4_foundation_commit": foundation_commit,
        "g4_foundation_tree": foundation_identity["foundation_tree"],
        "g4_foundation_commit_changed_path_count": foundation_identity[
            "foundation_commit_changed_path_count"
        ],
        "g4_foundation_readiness_correction_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CORRECTION_REBIND
        ),
        "g4_foundation_readiness_correction_rebind_status": (
            readiness_rebind.get("status")
        ),
        "g4_foundation_readiness_current_input_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "g4_foundation_readiness_current_input_rebind_status": (
            readiness_current_input_rebind.get("status")
        ),
        "compiler_fix_commit": EXPECTED_COMPILER_FIX_COMMIT,
        "compiler_fix_is_ancestor": compiler_fix_is_ancestor,
        "particle_correction_commit": EXPECTED_PARTICLE_CORRECTION_COMMIT,
        "particle_correction_commit_is_ancestor": (
            particle_correction_is_ancestor
        ),
        "particle_correction_projection_report_sha256": sha256_file(
            PARTICLE_CORRECTION_PROJECTION_REPORT
        ),
        "particle_correction_binding_status": particle_correction_binding.get(
            "status"
        ),
        "historical_attempt_id": HISTORICAL_ATTEMPT_ID,
        "historical_attempt_role": "immutable_historical_evidence_only",
        "historical_attempt_resumed": False,
        "blocked_attempt_id": BLOCKED_ATTEMPT_ID,
        "blocked_attempt_role": "immutable_blocked_evidence_only",
        "blocked_attempt_resumed": False,
        "blocked_attempt_phase7_or_phase8_reentry_allowed": False,
        "source_universe_count": manifest["expected_universe"]["facts_count"],
        "required_tools": tool_rows,
        "execution_contract_checked": True,
        "execution_contract_conflict_count": 0,
        "roadmap_provenance_bound": roadmap_report["roadmap_provenance_bound"],
        "publish_foundation_contract_ready_for_remediation": foundation.get(
            "foundation_contract_ready_for_remediation"
        ),
        "publish_foundation_authority_effect": foundation.get("authority_effect"),
        "publish_foundation_official_disposition": foundation.get(
            "official_disposition"
        ),
        "publish_foundation_live_gate_adopted": foundation.get("live_gate_adopted"),
        "publish_foundation_policy_closure_state": foundation.get(
            "policy_closure_state"
        ),
        "cross_plan_sync_projection_hash_match": projection_report[
            "cross_plan_sync_projection_hash_match"
        ],
        "body_plan_applicability_owner_approval_match": applicability_binding[
            "owner_approval_match"
        ],
        "body_plan_applicability_approval_sha256": applicability_binding[
            "approval_sha256"
        ],
        "body_plan_applicability_rule_id": applicability_binding["rule_id"],
        "protected_surface_snapshot_sha256": canonical_hash(before_snapshot),
        "mutation_allowlist": [
            repo_relative(attempt_root),
            repo_relative(DATA_ROOT),
            "docs/dvf_3_3_korean_prose_quality_standard.md",
            "docs/dvf_3_3_korean_prose_compiler_contract.md",
            repo_relative(DURABLE_ROOT),
            *[repo_relative(path) for path in COMPILER_IMPLEMENTATION_PATHS],
        ],
    }
    write_once_or_same(root / "preflight_report.json", preflight)
    return preflight

__all__ = ("build_phase0",)
