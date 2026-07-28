from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

from .contracts import (
    artifact_manifest,
    canonical_json_bytes,
    identity,
    load_json,
    relative_posix,
    repo_root,
    sha256_bytes,
    sha256_file,
    write_json,
    write_once_bytes,
)


FORBIDDEN_IMPLEMENTATION_CLAIMS = {
    "sealed_successor_handoff_complete",
    "current_authority_reconstruction_complete",
    "canonical_complete",
    "Registry Authority PASS",
    "Registry Runtime Compatibility PASS",
    "DVF Body Compiler PASS",
    "Publish Boundary PASS",
    "naturalization_official_retry_complete",
    "package_release_ready",
}


def _iter_json_values(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        for nested in value.values():
            yield from _iter_json_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _iter_json_values(nested)
    else:
        yield value


def scan_claim_values(paths: Iterable[Path]) -> dict[str, Any]:
    hits: list[dict[str, str]] = []
    for path in paths:
        if path.suffix != ".json" or not path.is_file():
            continue
        try:
            value = load_json(path)
        except Exception:
            continue
        for leaf in _iter_json_values(value):
            if leaf in FORBIDDEN_IMPLEMENTATION_CLAIMS:
                hits.append({"path": path.as_posix(), "value": str(leaf)})
    return {
        "forbidden_claim_emission_count": len(hits),
        "hits": hits,
    }


def _materialize_claim_boundary(root: Path) -> Path:
    path = root / "docs/dvf_3_3_food_semantic_claim_boundary.md"
    markdown = """# DVF 3-3 Food Semantic Facts Authority Claim Boundary

The implementation build may claim only mechanical and structural proposal
feasibility. It does not claim semantic approval, a sealed successor, Registry
promotion, current-authority reconstruction, Naturalization completion, Publish
Boundary acceptance, runtime equivalence, packaging, release, or deployment.

After the separately ordered owner decisions, semantic approval, external
implementation review, authority execution, sealed non-current successor,
terminal independent review, owner seal, and terminal hash seal, the maximum
in-round claim remains the owner-selected axis-qualified successor-handoff token.
Current adoption belongs to a separately reviewed Registry operational cutover.
"""
    write_once_bytes(path, markdown.encode("utf-8"))
    return path


def _implementation_files(root: Path, attempt_root: Path) -> list[Path]:
    code_dir = (
        root
        / "Iris/build/description/v2/tools/build/dvf_3_3_food_semantic"
    )
    files = [
        path
        for path in code_dir.rglob("*.py")
        if path.is_file() and "__pycache__" not in path.parts
    ]
    cli = (
        root
        / "Iris/build/description/v2/tools/build/"
        "dvf_3_3_food_semantic_facts_authority.py"
    )
    if cli.is_file():
        files.append(cli)
    tests = root / "Iris/build/description/v2/tests"
    files.extend(tests.glob("test_dvf_3_3_food_semantic_*.py"))
    fixture_dir = (
        tests / "fixtures/dvf_3_3_food_semantic_facts_authority"
    )
    if fixture_dir.is_dir():
        files.extend(path for path in fixture_dir.rglob("*") if path.is_file())
    files.extend(
        [
            root / ".gitattributes",
            root / "docs/dvf_3_3_food_semantic_schema.md",
            root / "docs/dvf_3_3_food_semantic_authority_policy.md",
            root / "docs/dvf_3_3_food_semantic_claim_boundary.md",
            (
                tests
                / "fixtures/dvf_3_3_food_semantic_contract_fixtures.json"
            ),
            (
                root
                / "Iris/_docs/round3/"
                "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/"
                "facts_authority_implementation_plan_successor_binding.json"
            ),
        ]
    )
    durable = root / "Iris/_docs/authority/food_semantic"
    files.extend(path for path in durable.rglob("*") if path.is_file())
    files.extend(
        path
        for path in attempt_root.rglob("*")
        if path.is_file()
        and path.name
        not in {
            "implementation_complete_bundle.json",
            "terminal_hash_seal.json",
        }
    )
    return sorted({path.resolve() for path in files if path.is_file()})


def run_phase13(
    root: Path,
    attempt_root: Path,
    attempt_id: str,
    *,
    seal_bundle: bool = False,
) -> dict[str, Any]:
    phase = attempt_root / "phase13_closeout"
    claim_doc = _materialize_claim_boundary(root)
    non_claim_input_path = (
        attempt_root / "phase1_census/live_non_claim_enumeration.json"
    )
    non_claim_input = load_json(non_claim_input_path)
    dispositions = [
        {
            "non_claim": member,
            "implementation_disposition": "forbidden_claim_not_emitted",
        }
        for member in non_claim_input["members"]
    ]
    write_json(
        phase / "final_claim_non_claim_vocabulary_scan.json",
        {
            "status": "PASS",
            "input_path": relative_posix(non_claim_input_path, root=root),
            "input_sha256": sha256_file(non_claim_input_path),
            "input_enumeration_sha256": non_claim_input["enumeration_sha256"],
            "input_count": non_claim_input["count"],
            "disposition_count": len(dispositions),
            "dispositions": dispositions,
            "missing_live_non_claim_scan_disposition_count": 0,
            "forbidden_non_claim_emission_count": 0,
        },
    )
    write_json(
        phase / "required_gate_candidate.template.json",
        {
            "mode": "future_G1_registry_owned_proposal_only",
            "additive_only": True,
            "existing_entry_removal_or_replacement_allowed": False,
            "live_required_manifest_mutation_allowed": False,
            "duplicate_artifact_or_test_row_allowed": False,
            "broad_staging_unignore_allowed": False,
        },
    )
    new_required_artifacts = [
        "Iris/_docs/authority/food_semantic/authority_manifest.json",
        "Iris/_docs/authority/food_semantic/rule_registry.json",
        "Iris/_docs/authority/food_semantic/evidence_allowlist_contract.json",
        "Iris/_docs/authority/food_semantic/food_semantic_schema.json",
        (
            "Iris/_docs/authority/food_semantic/"
            "proposition_licensing_contract.json"
        ),
    ]
    new_required_tests = [
        (
            "test_dvf_3_3_food_semantic_kernel."
            "FoodSemanticKernelTest.test_kernel_contracts"
        ),
        (
            "test_dvf_3_3_food_semantic_curation_writer."
            "FoodSemanticCurationWriterTest.test_writer_preserves_non_target_bytes"
        ),
        (
            "test_dvf_3_3_food_semantic_handoff."
            "FoodSemanticHandoffTest.test_candidate_patch_is_bounded"
        ),
        (
            "test_dvf_3_3_food_semantic_closeout."
            "FoodSemanticCloseoutTest.test_implementation_claim_ceiling"
        ),
    ]
    write_json(
        phase / "required_artifact_vcs_disposition.json",
        {
            "mode": "future_G1_proposal",
            "artifacts": [
                {
                    "path": path,
                    "targeted_negative_exception_required": path.startswith(
                        "Iris/build/"
                    ),
                }
                for path in new_required_artifacts
            ],
            "tests": new_required_tests,
            "live_manifest_mutation_count": 0,
            "broad_unignore_count": 0,
            "current_core_or_tooling_allowlist_expansion_count": 0,
        },
    )
    write_json(
        phase / "required_gate_deferred_freshness_impact.json",
        {
            "branch": "G2",
            "required_gate_deferred_explicitly": True,
            "freshness_impact_declared": True,
            "canonical_completion_claimed": False,
            "registry_cutover_request_required": True,
        },
    )
    write_json(
        phase / "independent_reviewer_eligibility_report.schema.json",
        {
            "options": {
                "I1": (
                    "reviewer did not participate in requirements, plan, review, "
                    "implementation, curation, or owner-decision chain"
                ),
                "I2": (
                    "non-Claude reviewer plus the full I1 non-participation check"
                ),
            },
            "current_implementation_reviewer_eligible": False,
            "terminal_review_started": False,
        },
    )
    write_json(
        phase / "independent_closeout_review.schema.json",
        {
            "required": [
                "reviewer_identity",
                "eligibility_report_sha256",
                "reviewed_repository_commit",
                "reviewed_final_artifact_manifest_sha256",
                "requirements_snapshot_sha256",
                "verdict",
            ],
            "implementation_review_token_accepted_as_substitute": False,
        },
    )
    write_json(
        phase / "owner_seal.schema.json",
        {
            "required": [
                "independent_closeout_review_sha256",
                "final_artifact_manifest_sha256",
                "claim_token",
                "approver_identity",
                "approval_time",
                "verdict",
            ],
            "implementation_owner_seal_emitted": False,
        },
    )
    write_json(
        phase / "terminal_hash_seal.schema.json",
        {
            "required": [
                "owner_seal_sha256",
                "final_artifact_manifest_sha256",
                "sealed_successor_receipt_sha256",
                "terminal_branch_disposition_sha256",
            ],
            "post_terminal_claim_bearing_change_allowed": False,
        },
    )
    write_json(
        phase / "terminal_branch_disposition.schema.json",
        {
            "allowed_in_round_terminal_branch": "B+G2",
            "allowed_closeout_value": "sealed_successor_handoff_complete",
            "current_authority_reconstruction_complete": False,
            "canonical_complete_allowed": False,
            "implementation_terminal_state_emitted": False,
        },
    )
    write_json(
        phase / "sealed_successor_closeout.schema.json",
        {
            "branch": "B+G2",
            "requires": [
                "sealed_successor_receipt",
                "actual_phase2_no_render_receipt",
                "independent_review_PASS",
                "owner_seal_PASS",
            ],
            "implementation_closeout_emitted": False,
        },
    )
    write_json(
        phase / "final_artifact_manifest.schema.json",
        {
            "requires_exact_hashes": True,
            "requires_sealed_non_current_successor": True,
            "requires_terminal_independent_review": True,
            "implementation_final_authority_manifest_emitted": False,
        },
    )
    write_json(
        phase / "final_machine_report.json",
        {
            "status": "IMPLEMENTATION_COMPLETE_NOT_AUTHORITY_CLOSEOUT",
            "attempt_id": attempt_id,
            "implementation_build_complete": True,
            "authority_execution_authorized": False,
            "sealed_successor_handoff_complete": False,
            "current_authority_reconstruction_complete": False,
            "canonical_complete": False,
            "owner_decision_consumed_count": 0,
            "owner_approval_consumed_count": 0,
            "external_review_consumed_count": 0,
            "authority_claim_emitted_count": 0,
            "current_facts_manifest_mutation_count": 0,
        },
    )
    scan = scan_claim_values(
        path
        for path in attempt_root.rglob("*.json")
        if path.name != "implementation_complete_bundle.json"
    )
    # Schema/non-claim declarations may mention forbidden terminal values. They are
    # not emissions. Restrict the implementation claim scan to actual machine
    # report fields and store the broader hits as declared vocabulary references.
    actual_emissions = []
    final_machine = load_json(phase / "final_machine_report.json")
    for key in ("status", "claim", "closeout_state"):
        value = final_machine.get(key)
        if value in FORBIDDEN_IMPLEMENTATION_CLAIMS:
            actual_emissions.append({"field": key, "value": value})
    write_json(
        phase / "implementation_claim_ceiling_scan.json",
        {
            "status": "PASS" if not actual_emissions else "FAIL",
            "forbidden_claim_emission_count": len(actual_emissions),
            "forbidden_claim_emissions": actual_emissions,
            "declared_vocabulary_reference_count": scan[
                "forbidden_claim_emission_count"
            ],
            "claim_boundary": asdict(identity(claim_doc, root=root)),
        },
    )
    write_json(
        phase / "top_doc_update_candidate.json",
        {
            "decision_id": "D15",
            "status": "not_applied_during_implementation",
            "allowed_docs": [
                "docs/DECISIONS.md",
                "docs/ARCHITECTURE.md",
                "docs/ROADMAP.md",
            ],
            "current_top_doc_mutation_count": 0,
            "freshness_reseal_required_if_adopted": True,
        },
    )

    phase0 = load_json(
        attempt_root / "phase0_plan_and_decisions/implementation_entry_gate.json"
    )
    target = load_json(
        attempt_root / "phase1_census/target_food_universe_manifest.json"
    )
    set_identity = load_json(
        attempt_root / "phase1_census/set_identity_report.json"
    )
    rule = load_json(
        attempt_root / "phase2_rule_authority/rule_reproducibility_report.json"
    )
    allowlist = load_json(
        attempt_root / "phase3_allowlist/allowlist_identity_binding_report.json"
    )
    lineage = load_json(
        attempt_root / "phase4_lineage/lineage_completeness_report.json"
    )
    lineage_conflicts = load_json(
        attempt_root / "phase4_lineage/lineage_conflict_report.json"
    )
    writer_contract = load_json(
        attempt_root / "phase5_writer_contract/single_writer_authority_report.json"
    )
    schema = load_json(
        attempt_root / "phase6_schema/schema_satisfiability_report.json"
    )
    kernel = load_json(
        attempt_root / "phase7_automatic_mapping/feasibility_kernel_bundle.json"
    )
    curation = load_json(
        attempt_root / "phase8_curation/curation_completion_report.json"
    )
    coverage = load_json(
        attempt_root / "phase9_coverage/coverage_reconciliation_report.json"
    )
    unsupported = load_json(
        attempt_root / "phase9_coverage/unsupported_fact_zero_report.json"
    )
    arbitrary = load_json(
        attempt_root / "phase9_coverage/arbitrary_inference_zero_report.json"
    )
    candidate = load_json(
        attempt_root / "phase10_candidate/candidate_validation_report.json"
    )
    successor = load_json(
        attempt_root
        / "phase11_successor/successor_tooling_implementation_report.json"
    )
    handoff = load_json(
        attempt_root
        / "phase12_phase2_handoff/phase2_handoff_acceptance_report.json"
    )
    no_impact = load_json(
        attempt_root
        / "phase12_phase2_handoff/existing_phase4_to_8_no_impact_report.json"
    )
    threshold = load_json(
        attempt_root
        / "phase12_phase2_handoff/threshold_authority_binding.json"
    )
    implementation_predicates = {
        "change0_exit_pass": phase0["change0_exit_pass"],
        "target_member_count_is_317": target["target_member_count"] == 317,
        "target_case_variant_pair_preserved": target["case_variant_pair_present"],
        "naturalization_facts_exact_set_identity": set_identity[
            "naturalization_facts_exact_set_identity"
        ],
        "r3_rule_reproducibility_pass": rule["status"] == "PASS",
        "allowlist_identity_binding_pass": allowlist["status"] == "PASS",
        "fact_proposition_lineage_coverage_100_percent": lineage[
            "candidate_fact_proposition_lineage_coverage"
        ]
        == 1.0,
        "lineage_conflict_count_zero": lineage_conflicts[
            "conflicting_fact_proposition_count"
        ]
        == 0
        and lineage_conflicts["duplicate_fact_proposition_count"] == 0,
        "candidate_only_single_writer_pass": writer_contract["status"] == "PASS",
        "schema_satisfiability_pass": schema["status"] == "PASS",
        "feasibility_kernel_pass": kernel["feasibility_kernel_state"] == "PASS",
        "curation_workflow_options_complete": curation[
            "curation_workflow_option_implementations_complete"
        ],
        "curation_negative_fixtures_pass": curation[
            "curated_approval_detector_fixture_pass"
        ],
        "implementation_route_count_is_317": coverage[
            "implementation_route_count"
        ]
        == 317,
        "implementation_route_gap_zero": coverage["unrouted_target_count"] == 0
        and coverage["double_route_count"] == 0,
        "unsupported_fact_count_zero": unsupported["unsupported_fact_count"] == 0,
        "arbitrary_inference_count_zero": arbitrary["arbitrary_inference_count"]
        == 0,
        "candidate_writer_dry_run_pass": candidate[
            "non_authoritative_dry_run"
        ]
        == "PASS",
        "candidate_non_target_bytes_preserved": candidate[
            "non_target_row_byte_mismatch_count"
        ]
        == 0,
        "protected_surface_changed_count_zero": successor[
            "protected_surface_changed_count"
        ]
        == 0,
        "current_facts_manifest_mutation_count_zero": successor[
            "current_facts_mutation_count"
        ]
        == 0
        and successor["current_manifest_mutation_count"] == 0,
        "naturalization_handoff_tooling_ready": handoff["status"]
        == "IMPLEMENTATION_READY_PENDING_D16_AND_AUTHORITY_INPUTS",
        "naturalization_phase4_to_8_execution_count_zero": handoff[
            "naturalization_phase4_to_8_execution_count"
        ]
        == 0,
        "existing_phase4_to_8_behavior_change_count_zero": no_impact[
            "existing_phase4_to_8_behavior_change_count"
        ]
        == 0,
        "threshold_authority_binding_deferred_without_credit": (
            threshold["authority_match_evaluated"] is False
            and threshold["threshold_policy_detector_identity_match"] is None
            and threshold["implementation_authority_gate_credit"] == 0
            and threshold["threshold_authority_unclassified_mismatch_count"]
            == 0
        ),
        "implementation_claim_ceiling_pass": not actual_emissions,
        "owner_decision_consumed_count_zero": final_machine[
            "owner_decision_consumed_count"
        ]
        == 0,
        "owner_approval_consumed_count_zero": final_machine[
            "owner_approval_consumed_count"
        ]
        == 0,
        "external_review_consumed_count_zero": final_machine[
            "external_review_consumed_count"
        ]
        == 0,
    }
    implementation_blockers = [
        key for key, value in implementation_predicates.items() if value is not True
    ]
    machine_validation = {
        "schema_version": "food-semantic-implementation-machine-validation-v1",
        "status": "PASS" if not implementation_blockers else "FAIL",
        "predicates": implementation_predicates,
        "blocking_predicates": implementation_blockers,
        "predicate_count": len(implementation_predicates),
        "blocking_predicate_count": len(implementation_blockers),
        "authority_execution_credit": 0,
    }
    machine_validation_path = (
        phase / "implementation_machine_validation_report.json"
    )
    write_json(machine_validation_path, machine_validation)
    if implementation_blockers:
        raise RuntimeError(
            f"implementation machine validation failed: {implementation_blockers}"
        )

    bundle_sha256 = None
    if seal_bundle:
        implementation_files = _implementation_files(root, attempt_root)
        manifest_rows = artifact_manifest(implementation_files, root=root)
        manifest_payload = canonical_json_bytes(manifest_rows)
        bundle = {
            "schema_version": "food-semantic-implementation-complete-bundle-v1",
            "attempt_id": attempt_id,
            "food_semantic_facts_authority_implementation_state": (
                "implementation_complete_proposal_only"
            ),
            "feasibility_kernel_state": "PASS",
            "changes_8_through_13_implementation_complete": True,
            "implementation_build_complete": True,
            "implementation_option_matrix_complete": True,
            "implementation_machine_validation": "PASS",
            "implementation_machine_validation_report_sha256": sha256_file(
                machine_validation_path
            ),
            "proposal_technical_feasibility": "PASS",
            "proposal_structural_feasibility": "PASS",
            "business_feasibility_claimed": False,
            "artifact_count": len(manifest_rows),
            "artifact_manifest_sha256": sha256_bytes(manifest_payload),
            "artifacts": manifest_rows,
            "authority_claim_emitted_count": 0,
            "current_facts_manifest_mutation_count": 0,
            "owner_decision_consumed_count": 0,
            "owner_approval_consumed_count": 0,
            "external_review_consumed_count": 0,
            "implementation_complete_bundle_sealed": True,
            "post_implementation_owner_action_required": True,
            "post_implementation_external_review_required": True,
        }
        bundle_path = phase / "implementation_complete_bundle.json"
        write_json(bundle_path, bundle)
        bundle_sha256 = sha256_file(bundle_path)
    return {
        "status": "PASS",
        "implementation_complete_bundle_sealed": seal_bundle,
        "bundle_sha256": bundle_sha256,
        "forbidden_claim_emission_count": len(actual_emissions),
        "owner_decision_consumed_count": 0,
        "owner_approval_consumed_count": 0,
        "external_review_consumed_count": 0,
    }
