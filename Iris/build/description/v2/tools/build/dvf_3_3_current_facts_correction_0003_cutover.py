from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Sequence

import dvf_3_3_current_facts_correction_0002_cutover as cutover


CORRECTION_NUMBER = "0003"
CORRECTION_ID = "correction-0003"
ATTEMPT_ID = "attempt-0012"

INPUT_COMMIT = "cec8c43f5ba1c93d0c7a3436c74d73a1e24549fa"
INPUT_TREE = "1a3d7a5bafbbd9cadc9d0f31f19e2323fc217ae8"
REQUIRED_ANCESTOR = "80bd00cfedb22bb2ae9ab1d0860706b2cbbe5967"
PREIMAGE_FACTS_SHA256 = (
    "37db2595eff9b58f7b08e59221e950cb529453bd96733fb29171d458e46118f6"
)
PREIMAGE_MANIFEST_SHA256 = (
    "a105e3790896b30bc25e95839ceb0ee4c88357fed98ec9fa4258790bf0733a1f"
)
SUCCESSOR_FACTS_SHA256 = (
    "50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120"
)
SUCCESSOR_MANIFEST_SHA256 = (
    "da7f6676b899b628c444edca56241ad274f2c64fa1a3448a934abff2f059cbb5"
)
SUCCESSOR_RECEIPT_SHA256 = (
    "ad0b16c3bec487a4eba63ba51a24ba781f200551419b22d757eebd4e76cf57f8"
)
ROW_LINEAGE_SHA256 = (
    "6c257f1ce558068a1e5536be05c65dde33a477e7627cf15d98ad7d9563e62da8"
)
PREVIOUS_RECEIPT_SHA256 = (
    "475239fba798104371d2c9f4fb166c46ceab15bb462015493238a4aff4656f7f"
)
PREVIOUS_TERMINAL_SHA256 = (
    "b54cca40e1dcbf4d279d878a6fba42e244311b33691eb27054d0881ff4682a52"
)
PREVIOUS_REVIEW_SHA256 = (
    "1145413c6011b11485ad0e9b482fcb32208130c9f073dda33864ffaff15c27b5"
)
INITIAL_G3_RECEIPT_SHA256 = (
    "efcc387bb395b561ab67df0cab4e498fe0b429680fc6cc8f6dd96eb94ba49751"
)
REGISTRY_CONTRACT_PREIMAGE_SHA256 = (
    "c2655f766d8db30a31821471c8c871b723dadd9bb9803ff99a6765b2ec3dc361"
)
NATURALIZATION_CONTRACT_PREIMAGE_SHA256 = (
    "c2655f766d8db30a31821471c8c871b723dadd9bb9803ff99a6765b2ec3dc361"
)

SUCCESSOR_ROOT = (
    cutover.V2_ROOT
    / "staging"
    / "dvf_3_3_current_facts_correction_successor"
    / "successors"
    / CORRECTION_ID
)
SUCCESSOR_FACTS = SUCCESSOR_ROOT / "successor_facts.jsonl"
SUCCESSOR_MANIFEST = SUCCESSOR_ROOT / "successor_input_manifest.json"
SUCCESSOR_RECEIPT = SUCCESSOR_ROOT / "successor_receipt.json"
ROW_LINEAGE = SUCCESSOR_ROOT / "row_source_lineage.jsonl"
PATCH_LEDGER = SUCCESSOR_ROOT / "correction_patch_ledger.jsonl"
BLOCKER_PROJECTION = SUCCESSOR_ROOT / "blocker_44_projection.jsonl"
FULL_CENSUS = SUCCESSOR_ROOT / "full_cohort_census.jsonl"
NON_TARGET_REPORT = SUCCESSOR_ROOT / "non_target_byte_identity_report.json"
REGRESSION_REPORT = (
    SUCCESSOR_ROOT / "correction_0001_0002_regression_report.json"
)
COHORT_SUMMARY = SUCCESSOR_ROOT / "cohort_summary.json"
INTEGRITY_REPORT = SUCCESSOR_ROOT / "correction_integrity_report.json"
UNRESOLVED_ROWS = SUCCESSOR_ROOT / "unresolved_rows.jsonl"

PREVIOUS_ATTEMPT_ROOT = cutover.ATTEMPTS_ROOT / "attempt-0011"
PREVIOUS_RECEIPT = (
    PREVIOUS_ATTEMPT_ROOT
    / "closeout"
    / "registry_correction_adoption_receipt.json"
)
PREVIOUS_TERMINAL = (
    PREVIOUS_ATTEMPT_ROOT / "closeout" / "terminal_correction_hash_seal.json"
)
PREVIOUS_REVIEW = (
    PREVIOUS_ATTEMPT_ROOT / "reviews" / "codex_reviewer_closeout_review.json"
)

PROJECTION_ALLOWED_PATHS = {
    "authority_role",
    "current_facts_correction_successor_0003.current_authority_mutated",
    "current_facts_correction_successor_0003.registry_cutover_attempt_id",
    "current_facts_correction_successor_0003.registry_cutover_performed",
    "current_facts_correction_successor_0003.successor_receipt_path",
    "current_facts_correction_successor_0003.successor_receipt_sha256",
    "facts.path",
    "facts.role",
    "food_semantic_authority.registry_adoption_state",
    "food_semantic_authority.registry_cutover_attempt_id",
    "source_promotion.current_facts_correction_adoption_0003_binding",
    "status",
}


def configure_base() -> None:
    values = {
        "ATTEMPT_ID": ATTEMPT_ID,
        "CORRECTION_NUMBER": CORRECTION_NUMBER,
        "CORRECTION_ID": CORRECTION_ID,
        "INPUT_COMMIT": INPUT_COMMIT,
        "INPUT_TREE": INPUT_TREE,
        "REQUIRED_ANCESTOR": REQUIRED_ANCESTOR,
        "PREIMAGE_FACTS_SHA256": PREIMAGE_FACTS_SHA256,
        "PREIMAGE_MANIFEST_SHA256": PREIMAGE_MANIFEST_SHA256,
        "SUCCESSOR_FACTS_SHA256": SUCCESSOR_FACTS_SHA256,
        "SUCCESSOR_MANIFEST_SHA256": SUCCESSOR_MANIFEST_SHA256,
        "SUCCESSOR_RECEIPT_SHA256": SUCCESSOR_RECEIPT_SHA256,
        "PREVIOUS_RECEIPT_SHA256": PREVIOUS_RECEIPT_SHA256,
        "INITIAL_G3_RECEIPT_SHA256": INITIAL_G3_RECEIPT_SHA256,
        "REGISTRY_CONTRACT_PREIMAGE_SHA256": (
            REGISTRY_CONTRACT_PREIMAGE_SHA256
        ),
        "NATURALIZATION_CONTRACT_PREIMAGE_SHA256": (
            NATURALIZATION_CONTRACT_PREIMAGE_SHA256
        ),
        "SUCCESSOR_ROOT": SUCCESSOR_ROOT,
        "SUCCESSOR_FACTS": SUCCESSOR_FACTS,
        "SUCCESSOR_MANIFEST": SUCCESSOR_MANIFEST,
        "SUCCESSOR_RECEIPT": SUCCESSOR_RECEIPT,
        "PATCH_LEDGER": PATCH_LEDGER,
        "NON_TARGET_REPORT": NON_TARGET_REPORT,
        "REGRESSION_REPORT": REGRESSION_REPORT,
        "COHORT_SUMMARY": COHORT_SUMMARY,
        "UNRESOLVED_ROWS": UNRESOLVED_ROWS,
        "PREVIOUS_RECEIPT": PREVIOUS_RECEIPT,
        "PROJECTION_ALLOWED_PATHS": PROJECTION_ALLOWED_PATHS,
        "LOCK_PATH": cutover.ROUND_ROOT / "transaction.lock",
        "PROTECTED_PREFIXES": (
            "Iris/build/description/v2/staging/"
            "dvf_3_3_food_semantic_facts_authority/attempts/",
            "Iris/build/description/v2/staging/"
            "dvf_3_3_food_semantic_registry_operational_cutover/attempts/",
            "Iris/build/description/v2/staging/"
            "dvf_3_3_current_facts_correction_successor/successors/",
            "Iris/_docs/round3/"
            "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/",
            "Iris/_docs/round3/"
            "iris_publish_boundary_public_text_quality_acceptance_policy_closure/"
            "foundation/",
        ),
        "PROTECTED_EXCEPTIONS": {
            (
                "Iris/_docs/round3/"
                "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/"
                "food_semantic_registry_adoption_contract.json"
            ),
        },
    }
    for name, value in values.items():
        setattr(cutover, name, value)


def require_blob_working_identity(path: Path, expected: str, label: str) -> None:
    working = path.read_bytes()
    committed = cutover.git_blob_bytes(INPUT_COMMIT, path)
    cutover.require_equal(working, committed, f"{label}_git_blob_working_bytes")
    cutover.require_equal(cutover.sha256_bytes(working), expected, label)
    cutover.require_equal(
        cutover.git_text_attribute(path),
        "unset",
        f"{label}_text_attribute",
    )


def validate_inputs() -> dict[str, Any]:
    checks = (
        (cutover.CURRENT_FACTS, PREIMAGE_FACTS_SHA256, "current_facts_preimage"),
        (
            cutover.CURRENT_MANIFEST,
            PREIMAGE_MANIFEST_SHA256,
            "current_manifest_preimage",
        ),
        (SUCCESSOR_FACTS, SUCCESSOR_FACTS_SHA256, "successor_facts"),
        (
            SUCCESSOR_MANIFEST,
            SUCCESSOR_MANIFEST_SHA256,
            "successor_manifest",
        ),
        (
            SUCCESSOR_RECEIPT,
            SUCCESSOR_RECEIPT_SHA256,
            "successor_receipt",
        ),
        (ROW_LINEAGE, ROW_LINEAGE_SHA256, "row_level_lineage"),
    )
    for path, expected, label in checks:
        cutover.require_hash(path, expected, label)
        require_blob_working_identity(path, expected, label)
    cutover.require_hash(
        PREVIOUS_RECEIPT,
        PREVIOUS_RECEIPT_SHA256,
        "previous_correction_receipt",
    )
    cutover.require_hash(
        PREVIOUS_TERMINAL,
        PREVIOUS_TERMINAL_SHA256,
        "previous_terminal_seal",
    )
    cutover.require_hash(
        PREVIOUS_REVIEW,
        PREVIOUS_REVIEW_SHA256,
        "previous_codex_review",
    )
    cutover.require_hash(
        cutover.INITIAL_G3_RECEIPT,
        INITIAL_G3_RECEIPT_SHA256,
        "initial_g3_receipt",
    )
    cutover.require_hash(
        cutover.REGISTRY_CONTRACT,
        REGISTRY_CONTRACT_PREIMAGE_SHA256,
        "registry_contract_preimage",
    )
    cutover.require_hash(
        cutover.NATURALIZATION_CONTRACT,
        NATURALIZATION_CONTRACT_PREIMAGE_SHA256,
        "naturalization_contract_preimage",
    )

    receipt = cutover.read_json(SUCCESSOR_RECEIPT)
    expected_receipt = {
        "status": "PASS",
        "successor_id": CORRECTION_ID,
        "successor_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "row_source_lineage_sha256": ROW_LINEAGE_SHA256,
        "corrected_row_count": 44,
        "correction_field_count": 60,
        "unchanged_control_count": 105,
        "non_target_byte_identity_count": 2061,
        "non_target_byte_identity_denominator": 2061,
        "correction_0001_0002_regression_count": 0,
        "correction_0001_0002_regression_denominator": 251,
        "unresolved_row_count": 0,
        "layer4_evidence_consumed_count": 0,
    }
    for key, expected in expected_receipt.items():
        cutover.require_equal(receipt.get(key), expected, f"receipt_{key}")
    cutover.require_equal(
        cutover.count_jsonl(PATCH_LEDGER),
        60,
        "patch_ledger_line_count",
    )
    cutover.require_equal(
        cutover.count_jsonl(ROW_LINEAGE),
        44,
        "row_lineage_line_count",
    )
    cutover.require_equal(
        cutover.count_jsonl(BLOCKER_PROJECTION),
        44,
        "blocker_projection_line_count",
    )
    cutover.require_equal(
        cutover.count_jsonl(FULL_CENSUS),
        2105,
        "full_census_line_count",
    )
    cutover.require_equal(
        cutover.count_jsonl(UNRESOLVED_ROWS),
        0,
        "unresolved_line_count",
    )
    cutover.require_equal(
        cutover.count_jsonl(SUCCESSOR_FACTS),
        2105,
        "successor_row_count",
    )

    non_target = cutover.read_json(NON_TARGET_REPORT)
    for key, expected in {
        "status": "PASS",
        "non_target_byte_identical_count": 2061,
        "non_target_row_denominator": 2061,
        "non_target_byte_mismatch_count": 0,
        "row_order_preserved": True,
    }.items():
        cutover.require_equal(non_target.get(key), expected, f"non_target_{key}")
    regression = cutover.read_json(REGRESSION_REPORT)
    for key, expected in {
        "status": "PASS",
        "combined_unique_corrected_row_denominator": 251,
        "combined_regression_count": 0,
    }.items():
        cutover.require_equal(regression.get(key), expected, f"regression_{key}")
    cohort = cutover.read_json(COHORT_SUMMARY)
    for key, expected in {
        "status": "PASS",
        "corrected_row_count": 44,
        "correction_field_count": 60,
        "unchanged_control_count": 105,
        "unique_investigated_row_count": 149,
        "unresolved_row_count": 0,
        "layer4_evidence_consumed_count": 0,
    }.items():
        cutover.require_equal(cohort.get(key), expected, f"cohort_{key}")
    integrity = cutover.read_json(INTEGRITY_REPORT)
    cutover.require_equal(integrity.get("status"), "PASS", "integrity_status")
    cutover.require_equal(
        integrity.get("prior_correction_regression_count"),
        0,
        "integrity_prior_regression",
    )
    return {
        "status": "PASS",
        "current_preimages": {
            "facts": PREIMAGE_FACTS_SHA256,
            "manifest": PREIMAGE_MANIFEST_SHA256,
        },
        "successor": {
            "facts": SUCCESSOR_FACTS_SHA256,
            "manifest": SUCCESSOR_MANIFEST_SHA256,
            "receipt": SUCCESSOR_RECEIPT_SHA256,
            "row_level_lineage": ROW_LINEAGE_SHA256,
        },
        "corrected_row_count": 44,
        "correction_field_count": 60,
        "unchanged_control_count": 105,
        "non_target_byte_identity": "2061/2061",
        "previous_correction_regression": "0/251",
        "unresolved_row_count": 0,
        "git_blob_working_byte_identity": "PASS",
        "fresh_checkout_text_attributes": "PASS",
    }


def build_current_manifest_projection(attempt_id: str) -> dict[str, Any]:
    source = cutover.read_json(SUCCESSOR_MANIFEST)
    projected = copy.deepcopy(source)
    projected["status"] = "current_authority"
    projected["authority_role"] = "successor_current_source_authority"
    projected["facts"]["path"] = cutover.CURRENT_FACTS_REL
    projected["facts"]["role"] = "current_source_authority"
    food = projected["food_semantic_authority"]
    food["registry_adoption_state"] = "current_correction_0003"
    food["registry_cutover_attempt_id"] = attempt_id
    binding = projected["current_facts_correction_successor_0003"]
    binding["registry_cutover_performed"] = True
    binding["current_authority_mutated"] = True
    binding["registry_cutover_attempt_id"] = attempt_id
    binding["successor_receipt_path"] = cutover.repo_relative(SUCCESSOR_RECEIPT)
    binding["successor_receipt_sha256"] = SUCCESSOR_RECEIPT_SHA256
    projected["source_promotion"][
        "current_facts_correction_adoption_0003_binding"
    ] = {
        "schema_version": "dvf-3-3-current-facts-correction-adoption-binding-v3",
        "append_only": True,
        "successor_id": CORRECTION_ID,
        "registry_cutover_attempt_id": attempt_id,
        "predecessor_current_facts_sha256": PREIMAGE_FACTS_SHA256,
        "predecessor_current_manifest_sha256": PREIMAGE_MANIFEST_SHA256,
        "successor_facts_path": cutover.repo_relative(SUCCESSOR_FACTS),
        "successor_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "sealed_successor_manifest_path": cutover.repo_relative(
            SUCCESSOR_MANIFEST
        ),
        "sealed_successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "successor_receipt_path": cutover.repo_relative(SUCCESSOR_RECEIPT),
        "successor_receipt_sha256": SUCCESSOR_RECEIPT_SHA256,
        "row_source_lineage_path": cutover.repo_relative(ROW_LINEAGE),
        "row_source_lineage_sha256": ROW_LINEAGE_SHA256,
        "previous_correction_receipt_path": cutover.repo_relative(
            PREVIOUS_RECEIPT
        ),
        "previous_correction_receipt_sha256": PREVIOUS_RECEIPT_SHA256,
        "previous_terminal_correction_seal_sha256": PREVIOUS_TERMINAL_SHA256,
        "corrected_row_count": 44,
        "correction_field_count": 60,
        "unchanged_control_count": 105,
        "non_target_byte_identity_count": 2061,
        "prior_correction_regression_count": 0,
        "post_adoption_predecessor_restore_allowed": False,
        "partial_current_allowed": False,
        "dual_current_allowed": False,
    }
    return projected


def validate_projection(
    projected: dict[str, Any],
    attempt_id: str,
) -> list[dict[str, Any]]:
    source = cutover.read_json(SUCCESSOR_MANIFEST)
    differences = cutover.deep_diff(source, projected)
    cutover.require_equal(
        {entry["path"] for entry in differences},
        PROJECTION_ALLOWED_PATHS,
        "projection_allowlist",
    )
    cutover.require_equal(
        projected,
        build_current_manifest_projection(attempt_id),
        "projection_exact",
    )
    cutover.require_equal(
        projected["facts"]["sha256"],
        SUCCESSOR_FACTS_SHA256,
        "projection_facts_sha256",
    )
    for key in (
        "current_facts_correction",
        "current_facts_correction_successor",
    ):
        cutover.require_equal(
            projected[key],
            source[key],
            f"immutable_predecessor_{key}",
        )
    for key in (
        "current_facts_correction_binding",
        "current_facts_correction_adoption_0002_binding",
        "current_facts_correction_successor_0002_binding",
    ):
        cutover.require_equal(
            projected["source_promotion"][key],
            source["source_promotion"][key],
            f"immutable_source_promotion_{key}",
        )
    return differences


def build_adoption_receipt(root: Path) -> dict[str, Any]:
    candidates = cutover.expected_candidates(root)
    cutover.require_equal(
        candidates["facts"],
        SUCCESSOR_FACTS_SHA256,
        "receipt_current_facts",
    )
    return {
        "schema_version": "dvf-3-3-registry-correction-adoption-receipt-v3",
        "status": "PASS",
        "attempt_id": root.name,
        "successor_id": CORRECTION_ID,
        "input_commit": INPUT_COMMIT,
        "input_tree": INPUT_TREE,
        "predecessor_current_facts_sha256": PREIMAGE_FACTS_SHA256,
        "predecessor_current_manifest_sha256": PREIMAGE_MANIFEST_SHA256,
        "successor_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "sealed_successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "successor_receipt_path": cutover.repo_relative(SUCCESSOR_RECEIPT),
        "successor_receipt_sha256": SUCCESSOR_RECEIPT_SHA256,
        "row_source_lineage_path": cutover.repo_relative(ROW_LINEAGE),
        "row_source_lineage_sha256": ROW_LINEAGE_SHA256,
        "current_facts_sha256": candidates["facts"],
        "current_manifest_sha256": candidates["manifest"],
        "previous_correction_receipt_path": cutover.repo_relative(
            PREVIOUS_RECEIPT
        ),
        "previous_correction_receipt_sha256": PREVIOUS_RECEIPT_SHA256,
        "previous_terminal_correction_seal_sha256": PREVIOUS_TERMINAL_SHA256,
        "previous_codex_review_sha256": PREVIOUS_REVIEW_SHA256,
        "corrected_row_count": 44,
        "correction_field_count": 60,
        "unchanged_control_count": 105,
        "non_target_byte_identity": "2061/2061",
        "previous_correction_regression": "0/251",
        "unresolved_row_count": 0,
        "candidate_first": True,
        "exclusive_lock": True,
        "facts_first": True,
        "manifest_last": True,
        "process_crash_recoverable": True,
        "rollback_snapshot_verified": True,
        "failure_injection_status": "PASS",
        "git_blob_working_byte_identity": "PASS",
        "fresh_checkout_text_attributes": "PASS",
        "power_loss_atomicity_claimed": False,
        "single_filesystem_primitive_atomicity_claimed": False,
        "partial_current_allowed": False,
        "dual_current_allowed": False,
        "post_adoption_predecessor_restore_allowed": False,
        "forbidden_scope_execution_count": 0,
        "generated_at": cutover.now_iso(),
    }


def build_contract_projection(
    root: Path,
    receipt_path: Path,
) -> dict[str, Any]:
    contract = cutover.read_json(cutover.REGISTRY_CONTRACT)
    cutover.require_equal(
        contract.get("schema_version"),
        "food-semantic-registry-adoption-contract-v4",
        "predecessor_contract_schema",
    )
    predecessor_bindings = copy.deepcopy(
        contract.get("current_correction_successors", [])
    )
    cutover.require_equal(
        [entry.get("successor_id") for entry in predecessor_bindings],
        ["correction-0002"],
        "predecessor_successor_chain",
    )
    candidates = cutover.expected_candidates(root)
    binding = {
        "schema_version": "food-semantic-registry-correction-successor-binding-v2",
        "append_only": True,
        "successor_id": CORRECTION_ID,
        "supersedes_successor_id": "correction-0002",
        "predecessor_binding_sha256": cutover.canonical_hash(
            predecessor_bindings[-1]
        ),
        "predecessor_current_facts_sha256": PREIMAGE_FACTS_SHA256,
        "predecessor_current_manifest_sha256": PREIMAGE_MANIFEST_SHA256,
        "sealed_successor_facts_path": cutover.repo_relative(SUCCESSOR_FACTS),
        "sealed_successor_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "sealed_successor_manifest_path": cutover.repo_relative(
            SUCCESSOR_MANIFEST
        ),
        "sealed_successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "successor_receipt_path": cutover.repo_relative(SUCCESSOR_RECEIPT),
        "successor_receipt_sha256": SUCCESSOR_RECEIPT_SHA256,
        "row_source_lineage_path": cutover.repo_relative(ROW_LINEAGE),
        "row_source_lineage_sha256": ROW_LINEAGE_SHA256,
        "registry_cutover_attempt_id": root.name,
        "current_facts_sha256": candidates["facts"],
        "current_manifest_sha256": candidates["manifest"],
        "registry_correction_adoption_receipt_path": cutover.repo_relative(
            receipt_path
        ),
        "registry_correction_adoption_receipt_sha256": cutover.sha256_file(
            receipt_path
        ),
        "previous_correction_receipt_sha256": PREVIOUS_RECEIPT_SHA256,
        "previous_terminal_correction_seal_sha256": PREVIOUS_TERMINAL_SHA256,
        "corrected_row_count": 44,
        "correction_field_count": 60,
        "unchanged_control_count": 105,
        "post_adoption_predecessor_restore_allowed": False,
    }
    projected = copy.deepcopy(contract)
    projected["schema_version"] = "food-semantic-registry-adoption-contract-v5"
    projected["contract_id"] = (
        "dvf3_3_food_semantic_facts_authority__naturalization_phase2_sync_v5"
    )
    projected["predecessor_contract_v4"] = {
        "schema_version": contract["schema_version"],
        "contract_id": contract["contract_id"],
        "authority_deployment_sha256": REGISTRY_CONTRACT_PREIMAGE_SHA256,
        "naturalization_deployment_sha256": (
            NATURALIZATION_CONTRACT_PREIMAGE_SHA256
        ),
        "selected_successor_id": "correction-0002",
        "selected_successor_binding_sha256": cutover.canonical_hash(
            predecessor_bindings[-1]
        ),
    }
    projected["current_correction_successors"] = [
        *predecessor_bindings,
        binding,
    ]
    projected["current_correction_selection"] = {
        "successor_id": CORRECTION_ID,
        "binding_path": "current_correction_successors[1]",
        "append_only_predecessor_path": "current_correction_successors[0]",
    }
    projected["registry_runtime_compatibility_successor"] = {
        "applies_when_current_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "current_source_alignment_state": "stale_requires_successor_rtc",
        "successor_rtc_closure_complete": False,
        "live_bridge_runtime_package_publication_allowed": False,
        "rtc_executed_by_this_cutover": False,
    }
    cutover.require_equal(
        projected["current_correction"],
        contract["current_correction"],
        "contract_initial_correction_immutable",
    )
    cutover.require_equal(
        projected["current_correction_successors"][0],
        contract["current_correction_successors"][0],
        "contract_correction_0002_immutable",
    )
    return projected


def command_verify_adoption_commit(attempt_id: str) -> dict[str, Any]:
    root = cutover.attempt_root(attempt_id)
    cutover.require_clean_worktree()
    preflight = cutover.read_json(
        root / "preflight" / "current_preimage_report.json"
    )
    implementation_commit = preflight["entry_identity"]["implementation_commit"]
    head = cutover.git_output("rev-parse", "HEAD")
    ancestry = [
        line
        for line in cutover.git_output(
            "rev-list",
            "--ancestry-path",
            "--reverse",
            f"{implementation_commit}..{head}",
        ).splitlines()
        if line
    ]
    if not ancestry:
        raise cutover.CorrectionCutoverError("adoption_commit_not_found")
    adoption_commit = ancestry[0]
    cutover.require_equal(
        cutover.git_output("rev-parse", f"{adoption_commit}^"),
        implementation_commit,
        "adoption_parent",
    )
    changed = set(
        cutover.git_output(
            "diff",
            "--name-only",
            f"{implementation_commit}..{adoption_commit}",
        ).splitlines()
    )
    allowed = cutover.adoption_allowed_paths(root)
    unexpected = sorted(path for path in changed - allowed if path)
    if unexpected:
        raise cutover.CorrectionCutoverError(
            f"adoption_commit_unexpected_paths:{unexpected}"
        )
    required = {
        cutover.CURRENT_FACTS_REL,
        cutover.CURRENT_MANIFEST_REL,
        cutover.repo_relative(cutover.REGISTRY_CONTRACT),
        cutover.repo_relative(cutover.NATURALIZATION_CONTRACT),
        cutover.repo_relative(
            root / "closeout" / "registry_correction_adoption_receipt.json"
        ),
        cutover.repo_relative(root / "transaction" / "cutover_journal.json"),
        cutover.repo_relative(
            root / "transaction" / "rollback_current_facts.jsonl"
        ),
        cutover.repo_relative(
            root / "transaction" / "rollback_current_input_manifest.json"
        ),
    }
    cutover.require_equal(required - changed, set(), "adoption_required_paths")
    candidates = cutover.expected_candidates(root)
    cutover.require_equal(
        cutover.sha256_file(cutover.CURRENT_FACTS),
        SUCCESSOR_FACTS_SHA256,
        "current_facts",
    )
    cutover.require_equal(
        cutover.sha256_file(cutover.CURRENT_MANIFEST),
        candidates["manifest"],
        "current_manifest",
    )
    cutover.require_equal(
        cutover.read_json(cutover.CURRENT_MANIFEST)["facts"]["sha256"],
        SUCCESSOR_FACTS_SHA256,
        "current_manifest_facts_binding",
    )
    cutover.require_equal(
        cutover.read_json(root / "transaction" / "cutover_journal.json").get(
            "state"
        ),
        "committed",
        "journal_state",
    )
    contract_candidate = cutover.read_json(
        root / "candidate" / "registry_adoption_contract.json"
    )
    cutover.require_equal(
        cutover.read_json(cutover.REGISTRY_CONTRACT),
        contract_candidate,
        "registry_contract",
    )
    cutover.require_equal(
        cutover.read_json(cutover.NATURALIZATION_CONTRACT),
        contract_candidate,
        "naturalization_contract",
    )
    preservation = cutover.validate_protected_inventory(adoption_commit)
    byte_paths = [
        cutover.CURRENT_FACTS,
        cutover.CURRENT_MANIFEST,
        cutover.REGISTRY_CONTRACT,
        cutover.NATURALIZATION_CONTRACT,
        *sorted(path for path in root.rglob("*") if path.is_file()),
    ]
    for path in byte_paths:
        cutover.require_equal(
            cutover.git_blob_bytes(adoption_commit, path),
            path.read_bytes(),
            f"adoption_blob_working_{cutover.repo_relative(path)}",
        )
        cutover.require_equal(
            cutover.git_text_attribute(path),
            "unset",
            f"adoption_text_attribute_{cutover.repo_relative(path)}",
        )
    receipt_path = (
        root / "closeout" / "registry_correction_adoption_receipt.json"
    )
    receipt = cutover.read_json(receipt_path)
    cutover.require_equal(receipt.get("status"), "PASS", "adoption_receipt")
    adoption_tree = cutover.git_output(
        "rev-parse", f"{adoption_commit}^{{tree}}"
    )
    identity = {
        "schema_version": "dvf-3-3-current-correction-identity-report-v3",
        "status": "PASS",
        "attempt_id": attempt_id,
        "successor_id": CORRECTION_ID,
        "input_commit": INPUT_COMMIT,
        "input_tree": INPUT_TREE,
        "adoption_commit": adoption_commit,
        "adoption_tree": adoption_tree,
        "current_facts_path": cutover.CURRENT_FACTS_REL,
        "current_facts_sha256": candidates["facts"],
        "current_manifest_path": cutover.CURRENT_MANIFEST_REL,
        "current_manifest_sha256": candidates["manifest"],
        "current_manifest_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "successor_facts_byte_identity": True,
        "sealed_non_current_manifest_copied_unchanged": False,
        "current_adoption_projection_validation": "PASS",
        "single_current_identity": True,
        "partial_current_count": 0,
        "dual_current_count": 0,
        "committed_working_byte_identity_path_count": len(byte_paths),
        "cross_checkout_text_attribute_mismatch_count": 0,
        "post_adoption_predecessor_restore_allowed": False,
        "preservation": preservation,
        "generated_at": cutover.now_iso(),
    }
    identity_path = root / "closeout" / "current_correction_identity_report.json"
    cutover.write_once_json(identity_path, identity)
    handoff = {
        "schema_version": "dvf-3-3-naturalization-current-input-handoff-v3",
        "status": "READY_FOR_FOUNDATION_REBIND",
        "attempt_id": attempt_id,
        "successor_id": CORRECTION_ID,
        "registry_adoption_commit": adoption_commit,
        "registry_adoption_tree": adoption_tree,
        "current_facts_path": cutover.CURRENT_FACTS_REL,
        "current_facts_sha256": candidates["facts"],
        "current_manifest_path": cutover.CURRENT_MANIFEST_REL,
        "current_manifest_sha256": candidates["manifest"],
        "row_source_lineage_path": cutover.repo_relative(ROW_LINEAGE),
        "row_source_lineage_sha256": ROW_LINEAGE_SHA256,
        "registry_correction_adoption_receipt_path": cutover.repo_relative(
            receipt_path
        ),
        "registry_correction_adoption_receipt_sha256": cutover.sha256_file(
            receipt_path
        ),
        "required_next_stage": "G4_Foundation_current_input_rebind",
        "naturalization_attempt_started": False,
        "official_publish_started": False,
        "rtc_executed": False,
        "live_gate_mutated": False,
        "forbidden_direct_phase_reentry": True,
        "generated_at": cutover.now_iso(),
    }
    handoff_path = root / "handoff" / "naturalization_current_input_handoff.json"
    cutover.write_once_json(handoff_path, handoff)
    return {
        "status": "PASS",
        "adoption_commit": adoption_commit,
        "adoption_tree": adoption_tree,
        "current_facts_sha256": candidates["facts"],
        "current_manifest_sha256": candidates["manifest"],
        "identity_path": cutover.repo_relative(identity_path),
        "identity_sha256": cutover.sha256_file(identity_path),
        "handoff_path": cutover.repo_relative(handoff_path),
        "handoff_sha256": cutover.sha256_file(handoff_path),
        "review_required_before_terminal": True,
    }


def command_finalize(attempt_id: str) -> dict[str, Any]:
    root = cutover.attempt_root(attempt_id)
    review_path = root / "reviews" / "codex_reviewer_closeout_review.json"
    review = cutover.read_json(review_path)
    cutover.require_equal(review.get("status"), "PASS", "review_status")
    cutover.require_equal(review.get("verdict"), "PASS", "review_verdict")
    cutover.require_equal(
        review.get("blocking_finding_count"),
        0,
        "review_blocker_count",
    )
    reviewer = review.get("reviewer_identity")
    if not isinstance(reviewer, str) or not reviewer.startswith(
        "Codex Reviewer /root/"
    ):
        raise cutover.CorrectionCutoverError("invalid_codex_reviewer_identity")
    reviewed_commit = cutover.git_output("rev-parse", "HEAD")
    reviewed_tree = cutover.git_output("rev-parse", "HEAD^{tree}")
    cutover.require_equal(
        review.get("checked_preterminal_commit"),
        reviewed_commit,
        "reviewed_preterminal_commit",
    )
    cutover.require_equal(
        review.get("checked_preterminal_tree"),
        reviewed_tree,
        "reviewed_preterminal_tree",
    )
    cutover.require_equal(
        cutover.sha256_file(cutover.CURRENT_FACTS),
        SUCCESSOR_FACTS_SHA256,
        "finalize_current_facts",
    )
    candidates = cutover.expected_candidates(root)
    cutover.require_equal(
        cutover.sha256_file(cutover.CURRENT_MANIFEST),
        candidates["manifest"],
        "finalize_current_manifest",
    )
    identity_path = root / "closeout" / "current_correction_identity_report.json"
    identity = cutover.read_json(identity_path)
    handoff_path = root / "handoff" / "naturalization_current_input_handoff.json"
    receipt_path = (
        root / "closeout" / "registry_correction_adoption_receipt.json"
    )
    terminal = {
        "schema_version": "dvf-3-3-terminal-correction-hash-seal-v3",
        "status": "PASS",
        "attempt_id": attempt_id,
        "successor_id": CORRECTION_ID,
        "input_commit": INPUT_COMMIT,
        "input_tree": INPUT_TREE,
        "adoption_commit": identity["adoption_commit"],
        "adoption_tree": identity["adoption_tree"],
        "reviewed_preterminal_commit": reviewed_commit,
        "reviewed_preterminal_tree": reviewed_tree,
        "current_facts_sha256": candidates["facts"],
        "current_manifest_sha256": candidates["manifest"],
        "successor_receipt_sha256": SUCCESSOR_RECEIPT_SHA256,
        "row_source_lineage_sha256": ROW_LINEAGE_SHA256,
        "previous_correction_receipt_sha256": PREVIOUS_RECEIPT_SHA256,
        "previous_terminal_correction_seal_sha256": PREVIOUS_TERMINAL_SHA256,
        "registry_correction_adoption_receipt_path": cutover.repo_relative(
            receipt_path
        ),
        "registry_correction_adoption_receipt_sha256": cutover.sha256_file(
            receipt_path
        ),
        "current_identity_report_path": cutover.repo_relative(identity_path),
        "current_identity_report_sha256": cutover.sha256_file(identity_path),
        "naturalization_current_input_handoff_path": cutover.repo_relative(
            handoff_path
        ),
        "naturalization_current_input_handoff_sha256": cutover.sha256_file(
            handoff_path
        ),
        "codex_reviewer_closeout_review_path": cutover.repo_relative(
            review_path
        ),
        "codex_reviewer_closeout_review_sha256": cutover.sha256_file(
            review_path
        ),
        "codex_reviewer_blocking_finding_count": 0,
        "transaction_journal_sha256": cutover.sha256_file(
            root / "transaction" / "cutover_journal.json"
        ),
        "rollback_snapshot_manifest_sha256": cutover.sha256_file(
            root / "transaction" / "rollback_snapshot_manifest.json"
        ),
        "failure_injection_report_sha256": cutover.sha256_file(
            root / "preflight" / "failure_injection_report.json"
        ),
        "registry_adoption_contract_sha256": cutover.sha256_file(
            cutover.REGISTRY_CONTRACT
        ),
        "atomicity_model": "process_crash_recoverable_two_file_transaction",
        "manifest_last": True,
        "rollback_verified": True,
        "failure_injection_status": "PASS",
        "git_blob_working_byte_identity": "PASS",
        "fresh_checkout_text_attributes": "PASS",
        "post_adoption_predecessor_restore_allowed": False,
        "forbidden_scope_execution_count": 0,
        "generated_at": cutover.now_iso(),
    }
    terminal_path = root / "closeout" / "terminal_correction_hash_seal.json"
    cutover.write_once_json(terminal_path, terminal)
    return {
        "status": "PASS",
        "terminal_path": cutover.repo_relative(terminal_path),
        "terminal_sha256": cutover.sha256_file(terminal_path),
        "review_path": cutover.repo_relative(review_path),
        "review_sha256": cutover.sha256_file(review_path),
        "current_facts_sha256": candidates["facts"],
        "current_manifest_sha256": candidates["manifest"],
    }


def configure_commands() -> None:
    cutover.validate_inputs = validate_inputs
    cutover.build_current_manifest_projection = build_current_manifest_projection
    cutover.validate_projection = validate_projection
    cutover.build_adoption_receipt = build_adoption_receipt
    cutover.build_contract_projection = build_contract_projection


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DVF 3-3 correction successor 0003 Registry cutover"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in (
        "prepare",
        "failure-injection-check",
        "apply",
        "verify-adoption-commit",
        "finalize",
        "verify-closeout",
    ):
        child = subparsers.add_parser(command)
        child.add_argument("--attempt-id", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    configure_base()
    configure_commands()
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            result = cutover.command_prepare(args.attempt_id)
        elif args.command == "failure-injection-check":
            result = cutover.command_failure_injection_check(args.attempt_id)
        elif args.command == "apply":
            result = cutover.command_apply(args.attempt_id)
        elif args.command == "verify-adoption-commit":
            result = command_verify_adoption_commit(args.attempt_id)
        elif args.command == "finalize":
            result = command_finalize(args.attempt_id)
        else:
            result = cutover.command_verify_closeout(args.attempt_id)
    except (
        cutover.CorrectionCutoverError,
        cutover.transaction_core.CutoverError,
    ) as exc:
        print(
            json.dumps(
                {
                    "schema_version": (
                        "dvf-3-3-current-facts-correction-0003-cutover-error-v1"
                    ),
                    "status": "BLOCKED",
                    "failure": str(exc),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
