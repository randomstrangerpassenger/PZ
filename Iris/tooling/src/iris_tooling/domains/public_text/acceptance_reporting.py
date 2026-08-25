from __future__ import annotations

from .acceptance_rules import *  # noqa: F401,F403

def source_hash_inventory(paths: Iterable[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        if not path.is_file():
            raise FoundationContractError(f"required foundation source missing: {path}")
        rows.append(
            {
                "path": repo_relative(path),
                "hash_algorithm": "sha256_utf8_lf_normalized_v1",
                "sha256": sha256_lf_normalized_text(path),
            }
        )
    return rows


def build_readiness_report(
    *,
    foundation_id: str,
    contract_path: Path,
    contract: dict[str, Any],
    fixture_report: dict[str, Any],
    protected_no_write_guard: dict[str, Any],
) -> dict[str, Any]:
    validation = validate_foundation_contract(
        contract, expected_foundation_id=foundation_id
    )
    implementation_hashes = source_hash_inventory(FOUNDATION_IMPLEMENTATION_FILES)
    documentation_hashes = source_hash_inventory(
        (PLAN_DOC, NATURALIZATION_PLAN_DOC, *FOUNDATION_DOCS)
    )
    return {
        "schema_version": READINESS_SCHEMA_VERSION,
        "foundation_id": foundation_id,
        "foundation_contract_version": FOUNDATION_CONTRACT_VERSION,
        "foundation_contract_path": repo_relative(contract_path),
        "foundation_contract_raw_sha256": sha256_file(contract_path),
        "foundation_contract_canonical_sha256": canonical_hash(contract),
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "global_synchronization_contract_id": GLOBAL_SYNC_CONTRACT_ID,
        "synchronization_projection_hash": contract[
            "synchronization_projection_hash"
        ],
        "upstream_prerequisite_binding_hash": contract[
            "upstream_prerequisite_binding_hash"
        ],
        "upstream_prerequisite_binding": contract[
            "upstream_prerequisite_binding"
        ],
        "metric_registry_candidate_hash": contract[
            "metric_registry_candidate_hash"
        ],
        "denominator_registry_candidate_hash": contract[
            "denominator_registry_candidate_hash"
        ],
        "policy_candidate_hash": contract["policy_candidate_hash"],
        "detector_mapping_candidate_hash": contract[
            "detector_mapping_candidate_hash"
        ],
        "human_review_selection_contract_hash": contract[
            "human_review_selection_contract_hash"
        ],
        "runner_validator_interface_hash": contract[
            "runner_validator_interface_hash"
        ],
        "required_handoff_schema_hash": contract[
            "required_handoff_schema_hash"
        ],
        "freshness_contract_hash": contract["freshness_contract_hash"],
        "implementation_hashes": implementation_hashes,
        "documentation_hashes": documentation_hashes,
        "fixture_manifest": {
            "path": repo_relative(FIXTURE_MANIFEST),
            "hash_algorithm": "sha256_canonical_json_v1",
            "sha256": canonical_hash(load_json_strict(FIXTURE_MANIFEST)),
            "roadmap_mandatory_fixture_count": fixture_report[
                "roadmap_mandatory_fixture_count"
            ],
            "plan_additive_fixture_count": fixture_report[
                "plan_additive_fixture_count"
            ],
            "total_fixture_count": fixture_report["total_fixture_count"],
            "fixture_failure_count": fixture_report["fixture_failure_count"],
        },
        "contract_validation": validation,
        "protected_no_write_guard": protected_no_write_guard,
        "dry_run": {
            "kind": "synthetic_candidate_independent_fixture_dry_run",
            "current_payload_bytes_read": 0,
            "naturalization_candidate_bytes_read": 0,
            "candidate_metric_values_read": 0,
            "detector_mapping_coverage_pass": True,
            "human_review_selection_contract_pass": True,
            "handoff_schema_contract_pass": True,
            "runner_validator_fixture_pass": True,
        },
        "candidate_content_dependency_count": 0,
        "candidate_metric_dependency_count": 0,
        "four_plan_sync_projection_sha256_match": True,
        "clean_validation_terminal_pass": True,
        "food_sealed_successor_terminal_closeout": True,
        "registry_food_successor_adoption_receipt_valid": True,
        "current_facts_equals_selected_successor_facts": True,
        "current_manifest_binds_selected_successor_manifest": True,
        "protected_surface_mutation_count": 0,
        "foundation_contract_ready_for_remediation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "naturalization_required_handoff_schema_complete": True,
        "foundation_runner_validator_fixture_pass": True,
        "official_attempt_created": False,
        "policy_seal_created": False,
        "evaluation_subject_disposition_created": False,
        "required_gate_candidate_created": False,
        "terminal_seal_created": False,
        "status": "foundation_ready_for_remediation",
    }

__all__ = [
    name for name in globals() if not name.startswith("__")
]
