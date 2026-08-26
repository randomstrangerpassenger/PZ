from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from .acceptance_context import (
    CANDIDATE_STRUCTURAL_STATUSES,
    CURRENT_GENERATION_ROOT,
    CURRENT_FACTS,
    CURRENT_INPUT_MANIFEST,
    default_attempts_root,
    DISPOSITION_CLASSES,
    EVALUATION_SUBJECT_KINDS,
    FOUNDATION_CONTRACT_VERSION,
    FOUNDATION_SCHEMA_VERSION,
    FOUR_PLAN_SYNC_PROJECTION_SHA256,
    G0_G1_RELEASE_BINDING,
    G2_SEALED_SUCCESSOR_CLOSEOUT,
    G2_SEALED_SUCCESSOR_RECEIPT,
    G2_SELECTED_SUCCESSOR_BINDING,
    G2_TERMINAL_HASH_SEAL,
    G3_CURRENT_IDENTITY_REPORT,
    G3_REGISTRY_ADOPTION_RECEIPT,
    G3_TERMINAL_HASH_SEAL,
    GLOBAL_SYNC_CONTRACT_ID,
    GLOBAL_SYNC_MANIFEST,
    GLOBAL_SYNC_MANIFEST_GIT_BLOB_ID,
    GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256,
    LIVE_REQUIRED_VALIDATIONS,
    OWNER_INPUT_ROOT,
    PREDECESSOR_FOUNDATION,
    QUALIFIED_DISPOSITIONS,
    RAW_DETECTOR_IDS,
    REPO_ROOT,
    REQUIRED_HANDOFF_CONSTITUENT_IDS,
    REVIEWER_INPUT_ROOT,
    SYNC_CONTRACT_ID,
    V2_ROOT,
)
from .acceptance_infrastructure import (
    FoundationContractError,
    artifact_record,
    canonical_hash,
    commit_blob_record,
    head_blob_record,
    head_filtered_blob_record,
    is_ignored,
    is_tracked,
    load_json_strict,
    repo_relative,
    require_exact_keys,
    require_true_predicates,
    run_git,
    sha256_bytes,
    sha256_file,
)

def _g0_sync_manifest_record() -> dict[str, Any]:
    path = GLOBAL_SYNC_MANIFEST
    if not path.is_file() or not is_tracked(path) or is_ignored(path):
        raise FoundationContractError(
            "G0 synchronization manifest must be present, tracked, and not ignored"
        )
    record = head_filtered_blob_record(path)
    if (
        record["git_blob_id"] != GLOBAL_SYNC_MANIFEST_GIT_BLOB_ID
        or record["git_filtered_working_identity"] is not True
        or record["git_blob_sha256"]
        != GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256
        or record["working_sha256_lf_normalized"]
        != GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256
    ):
        raise FoundationContractError(
            "G0 synchronization manifest filtered/normalized identity mismatch"
        )
    return {
        **record,
        "hash_algorithm": "sha256_lf_normalized_text_v1",
        "sha256": GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256,
        "tracked": True,
        "ignored_by_current_rules": False,
        "sealed_expected_git_blob_id": GLOBAL_SYNC_MANIFEST_GIT_BLOB_ID,
        "sealed_expected_lf_normalized_sha256": (
            GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256
        ),
        "sealed_expected_identity_match": True,
    }


def _predecessor_foundation_binding() -> dict[str, Any]:
    relative = (
        "Iris/_docs/round3/"
        "iris_publish_boundary_public_text_quality_acceptance_policy_closure/"
        "foundation/public_text_quality_foundation_contract.json"
    )
    revision = PREDECESSOR_FOUNDATION["source_commit"]
    blob_id = run_git("rev-parse", f"{revision}:{relative}").stdout.strip()
    result = subprocess.run(
        ["git", "cat-file", "blob", blob_id],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationContractError(
            "cannot read predecessor Foundation v1 contract blob"
        )
    actual_sha256 = sha256_bytes(result.stdout)
    if actual_sha256 != PREDECESSOR_FOUNDATION["foundation_contract_raw_sha256"]:
        raise FoundationContractError(
            "predecessor Foundation v1 contract hash mismatch"
        )
    return {
        **PREDECESSOR_FOUNDATION,
        "path": relative,
        "git_blob_id": blob_id,
        "git_object_raw_sha256_match": True,
    }


def _require_ancestor(commit: str, *, label: str) -> None:
    if not isinstance(commit, str) or not commit:
        raise FoundationContractError(f"{label} commit is missing")
    result = run_git("merge-base", "--is-ancestor", commit, "HEAD", check=False)
    if result.returncode != 0:
        raise FoundationContractError(f"{label} commit is not an ancestor of HEAD")


def _materialized_plan_blob_record(row: dict[str, Any]) -> dict[str, Any]:
    require_exact_keys(
        row,
        required=("path", "sha256", "git_blob_id", "projection_occurrence_count"),
        label="G0 materialized plan row",
    )
    result = subprocess.run(
        ["git", "cat-file", "blob", row["git_blob_id"]],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationContractError(
            f"cannot read G0 materialized plan blob: {row['path']}"
        )
    actual_sha256 = sha256_bytes(result.stdout)
    if actual_sha256 != row["sha256"]:
        raise FoundationContractError(
            f"G0 materialized plan blob hash mismatch: {row['path']}"
        )
    return {
        **row,
        "git_object_raw_sha256": actual_sha256,
        "git_object_raw_sha256_match": True,
    }


def _validate_g0_binding() -> dict[str, Any]:
    artifact = _g0_sync_manifest_record()
    manifest = load_json_strict(GLOBAL_SYNC_MANIFEST)
    expected_plan_paths = [
        "docs/iris_clean_checkout_full_repository_validation_reproducibility_authority_closure_plan.md",
        "docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md",
        "docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md",
        "docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md",
    ]
    plan_rows = manifest.get("plans")
    projection = manifest.get("projection")
    if (
        manifest.get("schema_version")
        != "iris_aa49_four_plan_execution_sync_manifest_v1"
        or manifest.get("contract_id") != GLOBAL_SYNC_CONTRACT_ID
        or manifest.get("materialization_state") != "tracked_plan_set_ready"
        or manifest.get("baseline_commit")
        != "aa49e8f9fce19955a374b45d0744b1418a45ac9e"
        or manifest.get("owner_directive")
        != "synchronization_only_no_additional_plan_level_review"
        or manifest.get("four_plan_sync_projection_sha256")
        != FOUR_PLAN_SYNC_PROJECTION_SHA256
        or not isinstance(projection, dict)
        or canonical_hash(projection) != FOUR_PLAN_SYNC_PROJECTION_SHA256
        or manifest.get("plan_count") != 4
        or not isinstance(plan_rows, list)
        or [row.get("path") for row in plan_rows] != expected_plan_paths
        or any(row.get("projection_occurrence_count") != 1 for row in plan_rows)
        or manifest.get("implementation_or_attempt_output_imported_count") != 0
        or manifest.get("self_referential_commit_fields") != 0
    ):
        raise FoundationContractError("G0 synchronized plan-set binding is invalid")
    materialized_plan_blobs = [
        _materialized_plan_blob_record(row) for row in plan_rows
    ]
    current_successor_plan_blobs = []
    for relative in expected_plan_paths:
        path = REPO_ROOT / relative
        if not is_tracked(path) or is_ignored(path):
            raise FoundationContractError(
                f"current successor plan is not tracked and visible: {relative}"
            )
        head_blob = head_filtered_blob_record(path)
        if head_blob["git_filtered_working_identity"] is not True:
            raise FoundationContractError(
                f"current successor plan differs from its filtered HEAD Git blob: {relative}"
            )
        current_successor_plan_blobs.append(head_blob)
    return {
        "global_stage": "G0_plan_set_materialization_and_owner_sync",
        "status": "PASS",
        "artifact": artifact,
        "contract_id": GLOBAL_SYNC_CONTRACT_ID,
        "four_plan_sync_projection_sha256": FOUR_PLAN_SYNC_PROJECTION_SHA256,
        "four_plan_set_tracked_blob_count": 4,
        "materialized_plan_blobs": materialized_plan_blobs,
        "materialized_plan_blob_hash_match_count": 4,
        "current_successor_plan_blobs": current_successor_plan_blobs,
        "current_successor_plan_git_filtered_identity_count": 4,
        "current_top_doc_successor_changes_allowed": True,
        "current_top_doc_blob_equality_required": False,
    }


def _validate_g1_binding() -> dict[str, Any]:
    artifact = artifact_record(G0_G1_RELEASE_BINDING)
    binding = load_json_strict(G0_G1_RELEASE_BINDING)
    require_true_predicates(
        binding.get("receipt_predicates"), label="G1 release receipt predicates"
    )
    require_true_predicates(
        binding.get("closeout_binding", {}).get("predicates"),
        label="G1 closeout binding predicates",
    )
    require_true_predicates(
        binding.get("manifest", {}).get("predicates"),
        label="G0 manifest binding predicates",
    )
    if (
        binding.get("schema_version") != "food-semantic-g0-g1-release-binding-v1"
        or binding.get("status") != "PASS"
        or binding.get("four_plan_set_tracked_blob_count") != 4
        or binding.get("authority_claim_emitted_count") != 0
        or binding.get("owner_approval_consumed_count") != 0
        or binding.get("owner_decision_consumed_count") != 0
        or binding.get("manifest", {}).get("projection_sha256")
        != FOUR_PLAN_SYNC_PROJECTION_SHA256
    ):
        raise FoundationContractError("G1 downstream-unblock binding is invalid")
    source_receipt = binding.get("source_receipt", {})
    closeout = binding.get("closeout_binding", {})
    return {
        "global_stage": "G1_clean_checkout_full_repository_validation",
        "status": "PASS",
        "artifact": artifact,
        "clean_validation_terminal_pass": True,
        "downstream_unblock_target": "G2_food_semantic_facts_authority",
        "source_receipt_path": source_receipt.get("path"),
        "source_receipt_sha256": source_receipt.get("sha256"),
        "terminal_closeout_path": closeout.get("path"),
        "terminal_closeout_sha256": closeout.get("sha256"),
        "validated_subject_commit": closeout.get("containing_commit"),
    }


def _validate_g2_binding() -> dict[str, Any]:
    selected_artifact = artifact_record(G2_SELECTED_SUCCESSOR_BINDING)
    receipt_artifact = artifact_record(G2_SEALED_SUCCESSOR_RECEIPT)
    closeout_artifact = artifact_record(G2_SEALED_SUCCESSOR_CLOSEOUT)
    terminal_artifact = artifact_record(G2_TERMINAL_HASH_SEAL)
    selected = load_json_strict(G2_SELECTED_SUCCESSOR_BINDING)
    receipt = load_json_strict(G2_SEALED_SUCCESSOR_RECEIPT)
    closeout = load_json_strict(G2_SEALED_SUCCESSOR_CLOSEOUT)
    terminal = load_json_strict(G2_TERMINAL_HASH_SEAL)
    final_verification = terminal.get("final_artifact_manifest_verification", {})
    implementation_verification = terminal.get(
        "implementation_bundle_artifact_verification", {}
    )
    if (
        selected.get("schema_version")
        != "food-semantic-selected-successor-input-binding-v1"
        or receipt.get("schema_version")
        != "food-semantic-sealed-successor-receipt-v1"
        or receipt.get("non_current") is not True
        or receipt.get("current_facts_manifest_mutation_count") != 0
        or receipt.get("selected_binding_sha256") != selected_artifact["raw_sha256"]
        or closeout.get("schema_version")
        != "food-semantic-sealed-successor-closeout-v1"
        or closeout.get("status") != "PASS"
        or closeout.get("food_semantic_facts_authority_closeout")
        != "sealed_successor_handoff_complete"
        or closeout.get("selected_branch") != "B+G2"
        or closeout.get("canonical_complete") is not False
        or closeout.get("current_authority_reconstruction_complete") is not False
        or closeout.get("sealed_successor_receipt_sha256")
        != receipt_artifact["raw_sha256"]
        or terminal.get("schema_version")
        != "food-semantic-terminal-hash-seal-v1"
        or terminal.get("status") != "PASS"
        or terminal.get("sealed_successor_closeout_sha256")
        != closeout_artifact["raw_sha256"]
        or final_verification.get("status") != "PASS"
        or final_verification.get("artifact_mismatch_count") != 0
        or implementation_verification.get("status") != "PASS"
        or implementation_verification.get("artifact_mismatch_count") != 0
        or selected.get("successor_facts_sha256")
        != receipt.get("successor_facts_sha256")
        or selected.get("successor_input_manifest_sha256")
        != receipt.get("successor_manifest_sha256")
    ):
        raise FoundationContractError("G2 sealed successor binding is invalid")
    return {
        "global_stage": "G2_food_semantic_facts_authority",
        "status": "PASS",
        "attempt_id": "attempt-0022",
        "sealed_successor_terminal_closeout": True,
        "selected_successor_facts_sha256": receipt["successor_facts_sha256"],
        "selected_successor_manifest_sha256": receipt[
            "successor_manifest_sha256"
        ],
        "selected_successor_binding": selected_artifact,
        "sealed_successor_receipt": receipt_artifact,
        "sealed_successor_closeout": closeout_artifact,
        "terminal_hash_seal": terminal_artifact,
    }


def _validate_g3_and_current_identity(g2: dict[str, Any]) -> dict[str, Any]:
    receipt_artifact = artifact_record(G3_REGISTRY_ADOPTION_RECEIPT)
    identity_artifact = artifact_record(G3_CURRENT_IDENTITY_REPORT)
    terminal_artifact = artifact_record(G3_TERMINAL_HASH_SEAL)
    facts_artifact = artifact_record(CURRENT_FACTS)
    manifest_artifact = artifact_record(CURRENT_INPUT_MANIFEST)
    receipt = load_json_strict(G3_REGISTRY_ADOPTION_RECEIPT)
    identity = load_json_strict(G3_CURRENT_IDENTITY_REPORT)
    terminal = load_json_strict(G3_TERMINAL_HASH_SEAL)
    manifest = load_json_strict(CURRENT_INPUT_MANIFEST)
    _require_ancestor(identity.get("adoption_commit"), label="G3 adoption")
    actual_adoption_tree = run_git(
        "rev-parse", f"{identity['adoption_commit']}^{{tree}}"
    ).stdout.strip()

    adoption_commit = identity["adoption_commit"]
    adoption_facts_blob = commit_blob_record(CURRENT_FACTS, adoption_commit)
    adoption_manifest_blob = commit_blob_record(CURRENT_INPUT_MANIFEST, adoption_commit)
    current_facts_blob = head_blob_record(CURRENT_FACTS)
    current_manifest_blob = head_blob_record(CURRENT_INPUT_MANIFEST)
    adoption_facts_sha256 = adoption_facts_blob["git_blob_sha256"]
    adoption_manifest_sha256 = adoption_manifest_blob["git_blob_sha256"]
    initial_successor_facts_sha256 = g2["selected_successor_facts_sha256"]
    initial_successor_manifest_sha256 = g2["selected_successor_manifest_sha256"]
    current_facts_sha256 = facts_artifact["raw_sha256"]
    current_manifest_sha256 = manifest_artifact["raw_sha256"]
    food_authority = manifest.get("food_semantic_authority", {})
    source_binding = (
        manifest.get("source_promotion", {})
        .get("food_semantic_successor_binding", {})
    )
    terminal_artifacts = terminal.get("artifacts", {})
    correction_binding = manifest.get("current_facts_correction_successor_0003", {})
    correction_adoption = (
        manifest.get("source_promotion", {})
        .get("current_facts_correction_adoption_0003_binding", {})
    )
    if (
        receipt.get("schema_version")
        != "food-semantic-registry-adoption-receipt-v1"
        or receipt.get("status") != "PASS"
        or receipt.get("attempt_id") != "attempt-0009"
        or receipt.get("food_semantic_registry_adoption")
        != "current_adoption_complete"
        or receipt.get("current_identity_ambiguity_count") != 0
        or receipt.get("partial_or_dual_current_count") != 0
        or receipt.get("rendered_lua_runtime_package_mutation_count") != 0
        or receipt.get("selected_successor_facts_sha256")
        != initial_successor_facts_sha256
        or receipt.get("selected_successor_manifest_sha256")
        != initial_successor_manifest_sha256
        or receipt.get("current_facts_sha256") != adoption_facts_sha256
        or receipt.get("candidate_current_facts_sha256") != adoption_facts_sha256
        or receipt.get("current_manifest_sha256") != adoption_manifest_sha256
        or receipt.get("candidate_current_manifest_sha256")
        != adoption_manifest_sha256
        or receipt.get("projected_current_manifest_sha256")
        != adoption_manifest_sha256
        or receipt.get("current_manifest_adopted_successor_manifest_sha256")
        != initial_successor_manifest_sha256
        or identity.get("schema_version")
        != "food-semantic-current-identity-report-v1"
        or identity.get("status") != "PASS"
        or identity.get("attempt_id") != "attempt-0009"
        or identity.get("adoption_tree") != actual_adoption_tree
        or identity.get("canonical_adoption_readpoint") is not True
        or identity.get("current_identity_ambiguity_count") != 0
        or identity.get("partial_or_dual_current_count") != 0
        or identity.get("facts", {}).get("working_sha256") != adoption_facts_sha256
        or identity.get("facts", {}).get("git_blob_sha256")
        != adoption_facts_sha256
        or identity.get("manifest", {}).get("working_sha256")
        != adoption_manifest_sha256
        or identity.get("manifest", {}).get("git_blob_sha256")
        != adoption_manifest_sha256
        or identity.get("facts", {}).get("git_blob_id")
        != adoption_facts_blob["git_blob_id"]
        or identity.get("manifest", {}).get("git_blob_id")
        != adoption_manifest_blob["git_blob_id"]
        or current_facts_blob["git_blob_working_byte_identity"] is not True
        or current_manifest_blob["git_blob_working_byte_identity"] is not True
        or terminal.get("schema_version")
        != "food-semantic-registry-adoption-terminal-hash-seal-v1"
        or terminal.get("status") != "PASS"
        or terminal.get("terminal_hash_seal") != "PASS"
        or terminal.get("food_semantic_registry_adoption")
        != "current_adoption_complete"
        or terminal.get("current_facts_sha256") != adoption_facts_sha256
        or terminal.get("current_manifest_sha256") != adoption_manifest_sha256
        or terminal.get("selected_successor_facts_sha256")
        != initial_successor_facts_sha256
        or terminal.get("selected_successor_manifest_sha256")
        != initial_successor_manifest_sha256
        or terminal_artifacts.get("registry_adoption_receipt_sha256")
        != receipt_artifact["raw_sha256"]
        or terminal_artifacts.get("current_identity_report_sha256")
        != identity_artifact["raw_sha256"]
        or manifest.get("facts", {}).get("sha256") != current_facts_sha256
        or food_authority.get("attempt_id") != "attempt-0022"
        or food_authority.get("registry_cutover_attempt_id") != "attempt-0012"
        or food_authority.get("authority_bearing") is not True
        or food_authority.get("non_current") is not False
        or food_authority.get("registry_adoption_state") != "current_correction_0003"
        or food_authority.get("source_successor_manifest_sha256")
        != initial_successor_manifest_sha256
        or source_binding.get("successor_facts_sha256")
        != initial_successor_facts_sha256
        or source_binding.get("successor_manifest_sha256")
        != initial_successor_manifest_sha256
        or correction_binding.get("successor_id") != "correction-0003"
        or correction_binding.get("registry_cutover_attempt_id") != "attempt-0012"
        or correction_binding.get("current_authority_mutated") is not True
        or correction_binding.get("successor_facts_sha256") != current_facts_sha256
        or correction_adoption.get("successor_id") != "correction-0003"
        or correction_adoption.get("registry_cutover_attempt_id") != "attempt-0012"
        or correction_adoption.get("successor_facts_sha256") != current_facts_sha256
    ):
        raise FoundationContractError(
            "G3 adoption receipt and current facts/manifest identity binding is invalid"
        )
    return {
        "global_stage": "G3_registry_food_successor_operational_cutover",
        "status": "PASS",
        "attempt_id": "attempt-0009",
        "registry_food_successor_adoption_receipt_valid": True,
        "food_semantic_registry_adoption": "current_adoption_complete",
        "adoption_commit": identity["adoption_commit"],
        "adoption_tree": actual_adoption_tree,
        "adoption_tree_matches_commit": True,
        "initial_g3_selected_successor_facts_sha256": initial_successor_facts_sha256,
        "initial_g3_selected_successor_manifest_sha256": initial_successor_manifest_sha256,
        "selected_successor_facts_sha256": current_facts_sha256,
        "selected_successor_manifest_sha256": current_manifest_sha256,
        "initial_g3_adoption_facts": adoption_facts_blob,
        "initial_g3_adoption_manifest": adoption_manifest_blob,
        "current_facts": {
            **facts_artifact,
            **current_facts_blob,
        },
        "current_input_manifest": {
            **manifest_artifact,
            **current_manifest_blob,
            "adopted_successor_manifest_sha256": current_manifest_sha256,
        },
        "registry_adoption_receipt": receipt_artifact,
        "current_identity_report": identity_artifact,
        "terminal_hash_seal": terminal_artifact,
        "current_identity_ambiguity_count": 0,
        "partial_or_dual_current_count": 0,
        "rendered_lua_runtime_package_mutation_count": 0,
        "registry_runtime_compatibility_current_source_alignment": (
            "stale_requires_successor_rtc"
        ),
        "successor_registry_runtime_compatibility_closure": False,
        "runtime_package_publication_claim_effect": "none_fail_closed_out_of_scope",
    }


def build_upstream_prerequisite_binding() -> dict[str, Any]:
    g0 = _validate_g0_binding()
    g1 = _validate_g1_binding()
    g2 = _validate_g2_binding()
    g3 = _validate_g3_and_current_identity(g2)
    return {
        "schema_version": "public_text_quality_foundation_upstream_binding_v1",
        "global_stage_order": [
            "G0_plan_set_materialization_and_owner_sync",
            "G1_clean_checkout_full_repository_validation",
            "G2_food_semantic_facts_authority",
            "G3_registry_food_successor_operational_cutover",
            "G4_publish_boundary_foundation",
        ],
        "g0": g0,
        "g1": g1,
        "g2": g2,
        "g3": g3,
        "four_plan_sync_projection_sha256_match": True,
        "clean_validation_terminal_pass": True,
        "food_sealed_successor_terminal_closeout": True,
        "registry_food_successor_adoption_receipt_valid": True,
        "current_facts_equals_selected_successor_facts": True,
        "current_manifest_binds_selected_successor_manifest": True,
        "upstream_prerequisite_status": "PASS",
    }


def _protected_foundation_surface_paths() -> list[Path]:
    fixed = [
        CURRENT_FACTS,
        CURRENT_INPUT_MANIFEST,
        LIVE_REQUIRED_VALIDATIONS,
        V2_ROOT / "data" / "dvf_3_3_decisions.jsonl",
        V2_ROOT / "data" / "dvf_3_3_overlay_support.jsonl",
        V2_ROOT / "data" / "compose_profiles_v2.json",
        V2_ROOT / "data" / "compose_profile_identity_hint_rules.json",
        V2_ROOT / "data" / "compose_profile_conflict_precedence_rules.json",
        CURRENT_GENERATION_ROOT / "dvf_3_3_rendered.json",
    ]
    recursive_roots = [
        REPO_ROOT / "Iris" / "media" / "lua",
        REPO_ROOT / "Iris" / "Contents" / "mods" / "Iris",
        default_attempts_root(),
        OWNER_INPUT_ROOT,
        REVIEWER_INPUT_ROOT,
    ]
    paths = set(fixed)
    for root in recursive_roots:
        if root.is_dir():
            paths.update(path for path in root.rglob("*") if path.is_file())
    return sorted(paths, key=repo_relative)


def protected_foundation_surface_snapshot() -> dict[str, Any]:
    rows = []
    for path in _protected_foundation_surface_paths():
        present = path.is_file()
        rows.append(
            {
                "path": repo_relative(path),
                "present": present,
                "raw_sha256": sha256_file(path) if present else None,
                "byte_count": path.stat().st_size if present else None,
            }
        )
    return {
        "schema_version": "public_text_quality_foundation_no_write_snapshot_v1",
        "surface_count": len(rows),
        "surface_hash": canonical_hash(rows),
        "surfaces": rows,
    }


def build_no_write_guard(
    before: dict[str, Any], after: dict[str, Any]
) -> dict[str, Any]:
    changed_paths = sorted(
        {
            row["path"]
            for row in before["surfaces"] + after["surfaces"]
            if next(
                (
                    candidate
                    for candidate in before["surfaces"]
                    if candidate["path"] == row["path"]
                ),
                None,
            )
            != next(
                (
                    candidate
                    for candidate in after["surfaces"]
                    if candidate["path"] == row["path"]
                ),
                None,
            )
        }
    )
    if changed_paths:
        raise FoundationContractError(
            f"foundation protected no-write guard detected mutations: {changed_paths}"
        )
    return {
        "schema_version": "public_text_quality_foundation_no_write_guard_v1",
        "status": "PASS",
        "before_snapshot_hash": canonical_hash(before),
        "after_snapshot_hash": canonical_hash(after),
        "protected_surface_mutation_count": 0,
        "changed_paths": [],
        "source_rendered_lua_runtime_package_authority_effect": "none",
    }


def denominator_registry_candidate() -> dict[str, Any]:
    current = ("current_runtime_payload",)
    candidate = ("dvf_3_3_korean_naturalization_candidate",)
    rows = [
        ("current_item_universe_v1", "item", current),
        ("quality_evaluable_adopted_item_v1", "item", current),
        ("unadopted_item_v1", "item", current),
        ("required_section_opportunity_v1", "section_opportunity", current),
        (
            "required_identity_core_opportunity_v1",
            "section_opportunity",
            current,
        ),
        (
            "required_context_support_opportunity_v1",
            "section_opportunity",
            current,
        ),
        (
            "required_limitation_tail_opportunity_v1",
            "section_opportunity",
            current,
        ),
        ("required_use_core_opportunity_v1", "section_opportunity", current),
        (
            "profile_adopted_item_v1:<profile_id>",
            "item",
            current,
        ),
        ("naturalization_candidate_item_v1", "item", candidate),
        (
            "naturalization_source_proposition_v1",
            "source_proposition",
            candidate,
        ),
        (
            "naturalization_required_body_plan_role_v1",
            "required_body_plan_role",
            candidate,
        ),
        (
            "naturalization_fusion_suppression_transformation_v1",
            "fusion_suppression_transformation",
            candidate,
        ),
        (
            "naturalization_raw_detector_opportunity_v1:<detector_id>",
            "detector_opportunity",
            candidate,
        ),
        (
            "naturalization_human_review_required_v1",
            "required_human_review_row",
            candidate,
        ),
    ]
    return {
        "schema_version": "public_text_quality_denominator_registry_candidate_v1",
        "zero_denominator_effect": "technical_blocker",
        "count_equality_does_not_alias_denominator_ids": True,
        "registrations": [
            {
                "denominator_id": denominator_id,
                "unit": unit,
                "applicable_subject_kinds": list(subjects),
                "unknown_or_missing_effect": "technical_blocker",
            }
            for denominator_id, unit, subjects in rows
        ],
    }


def detector_mapping_candidate() -> dict[str, Any]:
    return {
        "schema_version": "public_text_quality_detector_mapping_candidate_v1",
        "unknown_or_unmapped_detector_effect": "technical_blocker",
        "mappings": [
            {
                "detector_id": "duplicate_proposition_realization",
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "semantic_duplication_zero_tolerance_v1",
            },
            {
                "detector_id": "repeated_identity_noun_window",
                "disposition_class": "advisory_debt",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "identity_repetition_debt_free_target_v1",
            },
            {
                "detector_id": "banned_internal_abstraction",
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "internal_abstraction_zero_tolerance_v1",
            },
            {
                "detector_id": "repeated_skeleton_concentration",
                "disposition_class": "advisory_debt",
                "threshold": {
                    "operator": "le",
                    "value": {"numerator": 1, "denominator": 20},
                },
                "rationale_id": "corpus_skeleton_concentration_cap_v1",
            },
            {
                "detector_id": "paragraph_fragmentation",
                "disposition_class": "advisory_debt",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "fragmentation_debt_free_target_v1",
            },
            {
                "detector_id": "passive_translationese_pattern",
                "disposition_class": "advisory_debt",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "translationese_debt_free_target_v1",
            },
            {
                "detector_id": "empty_or_filler_sentence",
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "empty_filler_zero_tolerance_v1",
            },
        ],
    }


def metric_registry_candidate() -> dict[str, Any]:
    current = ["current_runtime_payload"]
    candidate = ["dvf_3_3_korean_naturalization_candidate"]
    rows: list[dict[str, Any]] = [
        {
            "metric_id": "coverage_quality_weak",
            "unit": "ratio",
            "denominator_id": "quality_evaluable_adopted_item_v1",
            "disposition_class": "blocking_gate",
            "annotation": "acceptance_blocker",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "coverage_quality_adequate",
            "unit": "ratio",
            "denominator_id": "quality_evaluable_adopted_item_v1",
            "disposition_class": "non_claim",
            "annotation": "quality_distribution",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "coverage_quality_strong",
            "unit": "ratio",
            "denominator_id": "quality_evaluable_adopted_item_v1",
            "disposition_class": "non_claim",
            "annotation": "quality_distribution",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "missing_any_required_section_row",
            "unit": "ratio",
            "denominator_id": "quality_evaluable_adopted_item_v1",
            "disposition_class": "blocking_gate",
            "annotation": "acceptance_blocker",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "missing_required_section_occurrence",
            "unit": "ratio",
            "denominator_id": "required_section_opportunity_v1",
            "disposition_class": "advisory_debt",
            "annotation": "missing_occurrence_debt",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "missing_context_support",
            "unit": "ratio",
            "denominator_id": "required_context_support_opportunity_v1",
            "disposition_class": "non_claim",
            "annotation": "diagnostic_breakdown",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "missing_limitation_tail",
            "unit": "ratio",
            "denominator_id": "required_limitation_tail_opportunity_v1",
            "disposition_class": "non_claim",
            "annotation": "diagnostic_breakdown",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "missing_use_core",
            "unit": "ratio",
            "denominator_id": "required_use_core_opportunity_v1",
            "disposition_class": "non_claim",
            "annotation": "diagnostic_breakdown",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "unadopted",
            "unit": "count_ratio",
            "denominator_id": "current_item_universe_v1",
            "disposition_class": "non_claim",
            "annotation": "separate_adoption_axis",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "semantic_preservation_failure",
            "unit": "count",
            "denominator_id": "naturalization_source_proposition_v1",
            "disposition_class": "blocking_gate",
            "annotation": "source_provenance_blocker",
            "applicable_subject_kinds": candidate,
        },
        {
            "metric_id": "unsatisfied_required_body_plan_role",
            "unit": "count",
            "denominator_id": "naturalization_required_body_plan_role_v1",
            "disposition_class": "blocking_gate",
            "annotation": "structural_satisfaction_blocker",
            "applicable_subject_kinds": candidate,
        },
        {
            "metric_id": "equivalence_proof_failure",
            "unit": "count",
            "denominator_id": (
                "naturalization_fusion_suppression_transformation_v1"
            ),
            "disposition_class": "blocking_gate",
            "annotation": "technical_semantic_blocker",
            "applicable_subject_kinds": candidate,
        },
        {
            "metric_id": "compiler_invalid_pattern",
            "unit": "count",
            "denominator_id": "naturalization_candidate_item_v1",
            "disposition_class": "blocking_gate",
            "annotation": "compiler_contract_blocker",
            "applicable_subject_kinds": candidate,
        },
    ]
    detector_by_id = {
        row["detector_id"]: row for row in detector_mapping_candidate()["mappings"]
    }
    for detector_id in RAW_DETECTOR_IDS:
        mapping = detector_by_id[detector_id]
        rows.append(
            {
                "metric_id": detector_id,
                "unit": (
                    "rational_metric"
                    if detector_id == "repeated_skeleton_concentration"
                    else "count_ratio"
                ),
                "denominator_id": (
                    f"naturalization_raw_detector_opportunity_v1:{detector_id}"
                ),
                "disposition_class": mapping["disposition_class"],
                "annotation": "raw_korean_prose_detector",
                "applicable_subject_kinds": candidate,
            }
        )
    rows.append(
        {
            "metric_id": "human_review_blocker_required_denominator",
            "unit": "count",
            "denominator_id": "naturalization_human_review_required_v1",
            "disposition_class": "blocking_gate",
            "annotation": "denominator_qualified_human_only_finding",
            "applicable_subject_kinds": candidate,
        }
    )
    return {
        "schema_version": "public_text_quality_metric_registry_candidate_v1",
        "disposition_class_enum": list(DISPOSITION_CLASSES),
        "raw_metric_immutable": True,
        "registrations": rows,
    }


def human_review_selection_contract() -> dict[str, Any]:
    return {
        "schema_version": "public_text_quality_human_review_selection_v1",
        "algorithm_id": "deterministic_stratified_sha256_rank_v1",
        "selection_identity": (
            "sha256(candidate_rendered_hash + NUL + stratum_id + NUL + item_id)"
        ),
        "base_sample": {
            "ratio": {"numerator": 1, "denominator": 20},
            "minimum_rows": 128,
            "maximum_rows": 256,
            "cap_at_candidate_item_count": True,
        },
        "required_strata": [
            {
                "stratum_source": "resolved_profile",
                "minimum_rows_per_nonempty_stratum": 8,
            },
            {
                "stratum_source": "structural_fusion_or_suppression",
                "minimum_rows_per_nonempty_stratum": 16,
            },
            {
                "stratum_source": "raw_detector_id",
                "minimum_rows_per_nonempty_stratum": 8,
            },
        ],
        "selection_union_deduplicated_by": "exact_item_id",
        "required_denominator_id": "naturalization_human_review_required_v1",
        "human_only_claim_scope": "selected_required_denominator_only",
        "corpus_wide_human_only_zero_claim_requires_full_corpus_review": True,
        "missing_or_unbound_review_effect": "technical_blocker",
    }


def required_handoff_schema() -> dict[str, Any]:
    return {
        "schema_version": "naturalization_publish_handoff_required_schema_v1",
        "requested_evaluation_subject_kind": (
            "dvf_3_3_korean_naturalization_candidate"
        ),
        "required_constituent_ids": list(REQUIRED_HANDOFF_CONSTITUENT_IDS),
        "hash_fields_require_lowercase_sha256_hex": True,
        "exact_path_hash_binding_required": True,
        "post_handoff_mutation_effect": "stale",
        "candidate_runtime_parity_applicability": "not_applicable",
        "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
        "registry_runtime_pass_claim_allowed": False,
    }


def freshness_contract() -> dict[str, Any]:
    return {
        "schema_version": "public_text_quality_freshness_contract_v1",
        "stale_on_change": [
            "foundation_contract_bytes_or_hash",
            "policy_bytes_or_hash",
            "evaluation_subject_binding",
            "metric_calculator_or_schema",
            "subject_applicable_source_runtime_or_candidate_handoff_constituent",
            "applicable_waiver_set",
            "human_review_selection_or_decision_binding",
        ],
        "foundation_change_requires_new_version": True,
        "naturalization_earliest_affected_phase_rerun_required": True,
        "same_version_threshold_or_mapping_mutation_allowed": False,
        "last_known_good_disposition_fallback_allowed": False,
        "technical_or_freshness_waiver_allowed": False,
    }


def runner_validator_interface_contract() -> dict[str, Any]:
    return {
        "schema_version": "public_text_quality_runner_validator_interface_v1",
        "runner": {
            "path": (
                "Iris/tooling/src/iris_tooling/build/"
                "run_public_text_quality_acceptance.py"
            ),
            "required_arguments": {
                "--foundation-id": "nonempty_identifier",
                "--mode": "foundation-build",
            },
            "optional_arguments": {
                "--foundation-root": "explicit_output_root_for_fixture_or_diagnostic"
            },
            "foundation_root_policy": {
                "repository_local_default": (
                    "exact_tracked_g4_foundation_root_only"
                ),
                "external_fixture_or_diagnostic_root": "allowed_when_explicit",
                "other_repository_local_root": "forbidden",
            },
            "forbidden_arguments": ["--attempt-id"],
            "implicit_default_mode_allowed": False,
        },
        "validator": {
            "path": (
                "Iris/tooling/src/iris_tooling/build/"
                "validate_public_text_quality_acceptance.py"
            ),
            "required_arguments": {
                "--foundation-id": "exact_runner_foundation_id",
                "--require-foundation-ready": True,
                "--no-write": True,
            },
            "optional_arguments": {
                "--foundation-root": "explicit_input_root_for_fixture_or_diagnostic"
            },
            "foundation_root_policy": {
                "repository_local_default": (
                    "exact_tracked_g4_foundation_root_only"
                ),
                "external_fixture_or_diagnostic_root": "allowed_when_explicit",
                "other_repository_local_root": "forbidden",
            },
            "forbidden_arguments": ["--attempt-id"],
        },
        "exit_codes": {
            "0": "validated_foundation_ready",
            "2": "interface_or_contract_failure",
            "3": "write_once_conflict",
        },
        "official_phase_modes_implemented": False,
        "foundation_can_issue_official_disposition": False,
    }


def policy_candidate() -> dict[str, Any]:
    detector_mapping = detector_mapping_candidate()
    detector_thresholds = {
        row["detector_id"]: {
            "disposition_class": row["disposition_class"],
            "threshold": row["threshold"],
            "rationale_id": row["rationale_id"],
        }
        for row in detector_mapping["mappings"]
    }
    return {
        "schema_version": "public_text_quality_acceptance_policy_candidate_v1",
        "policy_candidate_version": "1.0.0",
        "authority_state": "development_foundation_candidate",
        "authority_effect": "none",
        "official_policy_ratified": False,
        "raw_metrics_immutable": True,
        "default_exceptions": [],
        "current_runtime_payload_thresholds": {
            "coverage_quality_weak": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "coverage_quality_adequate": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
            "coverage_quality_strong": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
            "missing_any_required_section_row": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "missing_required_section_occurrence": {
                "disposition_class": "advisory_debt",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "missing_context_support": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
            "missing_limitation_tail": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
            "missing_use_core": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
            "unadopted": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
        },
        "naturalization_candidate_thresholds": {
            "semantic_preservation_failure": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "unsatisfied_required_body_plan_role": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "equivalence_proof_failure": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "compiler_invalid_pattern": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            **detector_thresholds,
            "human_review_blocker_required_denominator": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
        },
        "waiver_contract": {
            "default_set": [],
            "allowed_waived_disposition": "deferred_internal_debt",
            "technical_or_freshness_scope_allowed": False,
            "raw_metric_mutation_allowed": False,
            "waiver_can_create_clean_accepted": False,
            "expiry_or_reevaluation_condition_required": True,
        },
        "item_disposition_mapping": {
            "technical_blocker": "blocked",
            "blocking_gate_unsatisfied": "blocked",
            "advisory_debt_unsatisfied": "deferred_internal_debt",
            "active_waiver": "deferred_internal_debt",
            "no_applicable_finding": "accepted",
            "non_claim_metric": "no_item_disposition_effect",
        },
        "aggregate_disposition_enum": list(QUALIFIED_DISPOSITIONS),
        "final_disposition_algorithm": [
            {
                "when": "technical_blocker_count > 0",
                "result": "blocked",
            },
            {
                "when": "effective_blocking_finding_count > 0",
                "result": "blocked",
            },
            {
                "when": "advisory_debt_count > 0 or active_waiver_count > 0",
                "result": "deferred_internal_debt",
            },
            {"when": "otherwise", "result": "accepted"},
        ],
        "threshold_rationale_constraints": {
            "candidate_metric_dependency_allowed": False,
            "current_payload_result_dependency_allowed": False,
            "historical_threshold_inheritance_allowed": False,
            "exact_integer_or_rational_comparison_required": True,
        },
    }


def synchronization_projection() -> dict[str, Any]:
    return {
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "canonical_stage_order": [
            "S0_plan_sync",
            "S1_publish_foundation",
            "S2_naturalization_build",
            "S3_publish_official_attempt",
            "S4_naturalization_finalize",
        ],
        "foundation_required_state": {
            "foundation_contract_ready_for_remediation": True,
            "authority_effect": "none",
            "official_disposition": "not_issued",
            "live_gate_adopted": False,
            "policy_closure_state": "not_started",
        },
        "evaluation_subject_kind_enum": list(EVALUATION_SUBJECT_KINDS),
        "candidate_structural_status_enum": list(CANDIDATE_STRUCTURAL_STATUSES),
        "required_handoff_constituent_ids": list(REQUIRED_HANDOFF_CONSTITUENT_IDS),
        "nonaccepted_candidate_action": "after_remediation",
        "blocked_immediate_allowed_for_synchronized_candidate": False,
        "candidate_runtime_parity_applicability": "not_applicable",
        "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
        "publish_owns_metric_mapping_threshold_waiver_disposition": True,
        "dvf_owns_proposition_discourse_realization_raw_detector": True,
    }


def build_foundation_contract(foundation_id: str) -> dict[str, Any]:
    if not foundation_id or foundation_id.strip() != foundation_id:
        raise FoundationContractError("foundation_id must be nonempty and trimmed")
    candidates = {
        "upstream_prerequisite_binding": build_upstream_prerequisite_binding(),
        "metric_registry_candidate": metric_registry_candidate(),
        "denominator_registry_candidate": denominator_registry_candidate(),
        "policy_candidate": policy_candidate(),
        "detector_mapping_candidate": detector_mapping_candidate(),
        "human_review_selection_contract": human_review_selection_contract(),
        "runner_validator_interface": runner_validator_interface_contract(),
        "required_handoff_schema": required_handoff_schema(),
        "freshness_contract": freshness_contract(),
        "synchronization_projection": synchronization_projection(),
    }
    hashes = {f"{name}_hash": canonical_hash(value) for name, value in candidates.items()}
    return {
        "schema_version": FOUNDATION_SCHEMA_VERSION,
        "foundation_id": foundation_id,
        "foundation_contract_version": FOUNDATION_CONTRACT_VERSION,
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "global_synchronization_contract_id": GLOBAL_SYNC_CONTRACT_ID,
        "roadmap_input_sha256_planning_observation": (
            "4b28e1fd3302877de81d85b14b6a7facd79b5b97a09e6db5aa5bcf8e2d4b07b9"
        ),
        "roadmap_provenance_effect": "planning_observation_only",
        "owner_instruction_scope": "implement_fresh_g4_foundation_successor_only",
        "owner_instruction_is_policy_ratification": False,
        "owner_instruction_is_gate_adoption": False,
        "owner_instruction_is_terminal_seal": False,
        "predecessor_foundation": _predecessor_foundation_binding(),
        "successor_reason": (
            "bind_fresh_g4_readiness_to_g3_adoption_and_current_facts_manifest_identity"
        ),
        **hashes,
        **candidates,
        "candidate_content_dependency_count": 0,
        "candidate_metric_dependency_count": 0,
        "foundation_contract_ready_for_remediation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "naturalization_required_handoff_schema_complete": True,
        "official_attempt_created": False,
        "policy_seal_created": False,
        "terminal_seal_created": False,
    }

__all__ = (
    "build_foundation_contract", "build_no_write_guard",
    "build_upstream_prerequisite_binding", "denominator_registry_candidate",
    "detector_mapping_candidate", "freshness_contract",
    "human_review_selection_contract", "metric_registry_candidate",
    "policy_candidate", "protected_foundation_surface_snapshot",
    "required_handoff_schema", "runner_validator_interface_contract",
    "synchronization_projection",
)
