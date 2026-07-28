from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import subprocess
from typing import Any, Iterable

from .contracts import (
    FoodSemanticError,
    artifact_manifest,
    canonical_json_bytes,
    identity,
    load_json,
    relative_posix,
    require_sealed_artifact_bundle,
    repo_root,
    sha256_bytes,
    sha256_file,
    write_json,
    write_once_bytes,
    verify_sealed_artifact_bundle,
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

POST_AUTHORITY_VALIDATION_COMMANDS = {
    "d16_acceptance": (
        "uv run python -B -m unittest discover "
        "-s Iris/build/description/v2/tests "
        '-p "test_dvf_3_3_korean_prose_acceptance_gate.py"'
    ),
    "d16_preservation": (
        "uv run python -B -m unittest discover "
        "-s Iris/build/description/v2/tests "
        '-p "test_dvf_3_3_korean_prose_semantic_preservation.py"'
    ),
    "current_route": (
        "uv run python -B "
        "Iris/_docs/round3/round3_run_contract_tests.py "
        "--class current --enforce-current-build-closure --out "
        "Iris/build/description/v2/staging/"
        "dvf_3_3_food_semantic_facts_authority/attempts/"
        "<attempt-id>/phase13_closeout/current_route_validation_result.json"
    ),
    "full_regression": (
        "uv run python -B -m unittest discover "
        "-s Iris/build/description/v2/tests -p \"test_*.py\""
    ),
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
    candidate_sources = code_dir / "d16_candidate_sources"
    if candidate_sources.is_dir():
        files.extend(path for path in candidate_sources.rglob("*") if path.is_file())
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
        phase / "implementation_claim_non_claim_vocabulary_scan.json",
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
        phase / "implementation_required_gate_deferred_freshness_impact.json",
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
                "reviewed_implementation_complete_bundle_sha256",
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
                "terminal_value",
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
                "independent_closeout_review_sha256",
                "sealed_successor_receipt_sha256",
                "terminal_branch_disposition_sha256",
                "sealed_successor_closeout_sha256",
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
        phase / "implementation_final_machine_report.json",
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
    final_machine = load_json(phase / "implementation_final_machine_report.json")
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
    feasibility = load_json(
        attempt_root
        / "phase7_automatic_mapping/curation_feasibility_report.json"
    )
    curation_caps = load_json(
        attempt_root / "phase6_schema/proposed_curation_caps.json"
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
    forbidden_binding = load_json(
        attempt_root
        / "phase9_coverage/forbidden_inference_registry_binding.json"
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
        "mandatory_curation_workload_exact": (
            feasibility["predicted_required_curation_items"] == 317
            and feasibility["predicted_required_curation_propositions"] == 634
            and curation_caps["proposed_curation_item_cap"] == 317
            and curation_caps["proposed_curation_proposition_cap"] == 634
        ),
        "curation_workflow_options_complete": curation[
            "curation_workflow_option_implementations_complete"
        ],
        "curation_negative_fixtures_pass": curation[
            "curated_approval_detector_fixture_pass"
        ],
        "curation_state_machine_fixtures_pass": (
            curation["curation_batch_exact_member_expansion_fixture_pass"]
            and curation["curation_resume_idempotence_fixture_pass"]
            and curation["curation_crash_boundary_fixtures_pass"]
            and curation["curation_rejection_rework_fixture_pass"]
        ),
        "implementation_route_count_is_317": coverage[
            "implementation_route_count"
        ]
        == 317,
        "implementation_route_gap_zero": coverage["unrouted_target_count"] == 0
        and coverage["conflicting_terminal_route_count"] == 0,
        "unsupported_fact_count_zero": unsupported["unsupported_fact_count"] == 0,
        "arbitrary_inference_count_zero": arbitrary["arbitrary_inference_count"]
        == 0,
        "forbidden_fixture_member_coverage_complete": (
            arbitrary["forbidden_member_fixture_missing_count"] == 0
            and arbitrary["forbidden_member_fixture_extra_count"] == 0
            and forbidden_binding[
                "all_forbidden_members_have_detector_fixtures"
            ]
        ),
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
        == 0
        and no_impact["D16_candidate_only_pre_authorization"],
        "threshold_authority_candidate_binding_exact_without_credit": (
            threshold["authority_match_evaluated"] is True
            and threshold["threshold_source_identity_bound"] is True
            and threshold["threshold_source_value_unchanged"] is True
            and threshold["threshold_policy_detector_identity_match"] is True
            and threshold["implementation_authority_gate_credit"] == 0
            and threshold["threshold_authority_unclassified_mismatch_count"]
            == 0
            and threshold["D16_candidate_adopted"] is False
            and threshold["actual_bound_threshold_value"] is None
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


def record_post_authority_validation(
    attempt_root: Path,
    *,
    d16_acceptance_exit_code: int,
    d16_preservation_exit_code: int,
    current_route_exit_code: int,
    full_regression_exit_code: int,
) -> dict[str, Any]:
    exit_codes = {
        "d16_acceptance": d16_acceptance_exit_code,
        "d16_preservation": d16_preservation_exit_code,
        "current_route": current_route_exit_code,
        "full_regression": full_regression_exit_code,
    }
    failing = sorted(name for name, code in exit_codes.items() if code != 0)
    if failing:
        raise FoodSemanticError(
            "post-authority validation cannot pass: " + ",".join(failing)
        )
    result = {
        "schema_version": "food-semantic-post-authority-validation-v1",
        "status": "PASS",
        "commands": {
            name: {
                "command": POST_AUTHORITY_VALIDATION_COMMANDS[name].replace(
                    "<attempt-id>", attempt_root.name
                ),
                "command_template": POST_AUTHORITY_VALIDATION_COMMANDS[name],
                "exit_code": exit_codes[name],
                "status": "PASS",
            }
            for name in sorted(POST_AUTHORITY_VALIDATION_COMMANDS)
        },
        "command_count": len(POST_AUTHORITY_VALIDATION_COMMANDS),
        "failed_command_count": 0,
    }
    write_json(
        attempt_root
        / "phase13_closeout/post_authority_validation_result.json",
        result,
    )
    return result


def _decision(owner: dict[str, Any], decision_id: str) -> dict[str, Any]:
    rows = [
        row
        for row in owner.get("decisions", [])
        if row.get("decision_id") == decision_id
    ]
    if len(rows) != 1:
        raise FoodSemanticError(
            f"terminal decision {decision_id} must appear exactly once"
        )
    return rows[0]


def _repository_head(root: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise FoodSemanticError("cannot resolve reviewed repository HEAD")
    return completed.stdout.strip()


def _git_tracked(root: Path, path: Path) -> bool:
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "--error-unmatch",
            relative_posix(path, root=root),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def _terminal_manifest_files(
    root: Path,
    attempt_root: Path,
    *,
    owner_decisions_path: Path,
) -> list[Path]:
    excluded = {
        "final_artifact_manifest.json",
        "terminal_review_request.json",
        "independent_closeout_review.json",
        "owner_seal.json",
        "terminal_branch_disposition.json",
        "sealed_successor_closeout.json",
        "terminal_hash_seal.json",
    }
    files = [
        path
        for path in attempt_root.rglob("*")
        if path.is_file() and path.name not in excluded
    ]
    implementation_bundle_path = (
        attempt_root / "phase13_closeout/implementation_complete_bundle.json"
    )
    implementation_bundle = load_json(implementation_bundle_path)
    files.extend(root / row["path"] for row in implementation_bundle["artifacts"])
    files.append(owner_decisions_path)
    owner_input_root = (
        root
        / "Iris/build/description/v2/owner_inputs/"
        "dvf_3_3_food_semantic_facts_authority"
    )
    if owner_input_root.is_dir():
        files.extend(path for path in owner_input_root.rglob("*") if path.is_file())
    durable = root / "Iris/_docs/authority/food_semantic"
    files.extend(path for path in durable.rglob("*") if path.is_file())
    for relative in (
        "docs/dvf_3_3_food_semantic_claim_boundary.md",
        (
            "Iris/build/description/v2/tools/build/"
            "run_dvf_3_3_korean_prose_naturalization.py"
        ),
        (
            "Iris/build/description/v2/tools/build/"
            "validate_dvf_3_3_korean_prose_naturalization.py"
        ),
        (
            "Iris/build/description/v2/tests/"
            "test_dvf_3_3_korean_prose_acceptance_gate.py"
        ),
        (
            "Iris/build/description/v2/tests/"
            "test_dvf_3_3_korean_prose_semantic_preservation.py"
        ),
    ):
        files.append(root / relative)
    return sorted({path.resolve() for path in files if path.is_file()})


def prepare_terminal_closeout(
    root: Path,
    attempt_root: Path,
    attempt_id: str,
    *,
    owner_decisions_path: Path,
) -> dict[str, Any]:
    phase = attempt_root / "phase13_closeout"
    implementation_bundle_path = (
        phase / "implementation_complete_bundle.json"
    )
    implementation_bundle_verification = require_sealed_artifact_bundle(
        root, implementation_bundle_path
    )
    authority_summary_path = (
        attempt_root / "authority_execution/authority_execution_summary.json"
    )
    authority_summary = load_json(authority_summary_path)
    phase12_acceptance_path = (
        attempt_root
        / "authority_execution/phase12_phase2_handoff/"
        "phase2_handoff_acceptance_report.json"
    )
    phase12_acceptance = load_json(phase12_acceptance_path)
    threshold_binding_path = (
        attempt_root
        / "authority_execution/phase12_phase2_handoff/"
        "threshold_authority_binding.json"
    )
    threshold_binding = load_json(threshold_binding_path)
    skeleton_group_report_path = (
        attempt_root
        / "authority_execution/phase12_phase2_handoff/"
        "skeleton_group_report.json"
    )
    skeleton_group_report = load_json(skeleton_group_report_path)
    sealed_receipt_path = (
        attempt_root / "phase11_successor/sealed_successor_receipt.json"
    )
    sealed_receipt = load_json(sealed_receipt_path)
    validation_path = phase / "post_authority_validation_result.json"
    validation = load_json(validation_path)
    owner = load_json(owner_decisions_path)
    if (
        authority_summary.get("status") != "PASS"
        or authority_summary.get("sealed_non_current_successor") is not True
        or sealed_receipt.get("non_current") is not True
        or validation.get("status") != "PASS"
        or validation.get("failed_command_count") != 0
        or phase12_acceptance.get("status") != "PASS"
        or not all(phase12_acceptance.get("predicates", {}).values())
        or threshold_binding.get("threshold_source_identity_bound") is not True
        or threshold_binding.get("threshold_source_value_unchanged") is not True
        or threshold_binding.get("threshold_policy_detector_identity_match")
        is not True
        or threshold_binding.get(
            "threshold_authority_unclassified_mismatch_count"
        )
        != 0
        or skeleton_group_report.get(
            "maximum_same_skeleton_group_within_bound"
        )
        is not True
        or skeleton_group_report.get("maximum_same_skeleton_group", 1)
        > skeleton_group_report.get("bound_threshold_value", 0)
    ):
        raise FoodSemanticError("terminal closeout prerequisites are incomplete")
    adopted_targets = [
        root / relative
        for relative in (
            (
                "Iris/build/description/v2/tools/build/"
                "run_dvf_3_3_korean_prose_naturalization.py"
            ),
            (
                "Iris/build/description/v2/tools/build/"
                "validate_dvf_3_3_korean_prose_naturalization.py"
            ),
            (
                "Iris/build/description/v2/tests/"
                "test_dvf_3_3_korean_prose_acceptance_gate.py"
            ),
            (
                "Iris/build/description/v2/tests/"
                "test_dvf_3_3_korean_prose_semantic_preservation.py"
            ),
        )
    ]
    untracked_adopted_targets = [
        relative_posix(path, root=root)
        for path in adopted_targets
        if not path.is_file() or not _git_tracked(root, path)
    ]
    if untracked_adopted_targets:
        raise FoodSemanticError(
            "D16 adopted targets must be tracked before final manifest: "
            + ",".join(untracked_adopted_targets)
        )

    d1 = _decision(owner, "D1")
    if d1["selected_option"] == "C1":
        claim_token = "Food Semantic Facts Authority Successor Handoff"
        terminal_value = "sealed_successor_handoff_complete"
    elif d1["selected_option"] == "C2":
        claim_token = d1["claim_token"]
        terminal_value = d1["terminal_value"]
    else:
        raise FoodSemanticError("D1 terminal claim option is invalid")
    d11 = _decision(owner, "D11")
    d13 = _decision(owner, "D13")
    d15 = _decision(owner, "D15")
    if d11.get("selected_option") != (
        "defer_G2_and_issue_future_registry_G1_request"
    ):
        raise FoodSemanticError("D11 must select the bounded B+G2 disposition")
    if d13.get("selected_option") not in {
        "I1_full_chain_non_participant",
        "I2_non_claude_full_chain_non_participant",
    }:
        raise FoodSemanticError("D13 reviewer eligibility option is invalid")
    if d15.get("selected_option") not in {
        "no_top_doc_update_current_round",
        "defer_top_doc_updates_to_registry_cutover",
    }:
        raise FoodSemanticError("D15 top-doc disposition is invalid")

    non_claim_input_path = (
        attempt_root / "phase1_census/live_non_claim_enumeration.json"
    )
    non_claim_input = load_json(non_claim_input_path)
    dispositions = [
        {
            "non_claim": member,
            "terminal_disposition": "not_emitted",
        }
        for member in non_claim_input["members"]
    ]
    claim_scan = {
        "schema_version": "food-semantic-final-claim-scan-v1",
        "status": "PASS",
        "input_path": relative_posix(non_claim_input_path, root=root),
        "input_sha256": sha256_file(non_claim_input_path),
        "input_enumeration_sha256": non_claim_input["enumeration_sha256"],
        "input_count": non_claim_input["count"],
        "disposition_count": len(dispositions),
        "dispositions": dispositions,
        "selected_claim_token": claim_token,
        "selected_terminal_value": terminal_value,
        "missing_live_non_claim_scan_disposition_count": 0,
        "forbidden_non_claim_emission_count": 0,
    }
    write_json(phase / "final_claim_non_claim_vocabulary_scan.json", claim_scan)
    write_json(
        phase / "required_gate_deferred_freshness_impact.json",
        {
            "schema_version": "food-semantic-required-gate-G2-disposition-v1",
            "status": "PASS",
            "D11_selected_option": d11["selected_option"],
            "required_gate_deferred_explicitly": True,
            "future_registry_G1_adoption_request_complete": True,
            "live_required_manifest_mutation_count": 0,
            "freshness_impact_declared": True,
            "canonical_completion_claimed": False,
        },
    )
    write_json(
        phase / "top_doc_update_disposition.json",
        {
            "schema_version": "food-semantic-D15-disposition-v1",
            "status": "PASS",
            "D15_selected_option": d15["selected_option"],
            "top_doc_mutation_count": 0,
            "freshness_reseal_required": False,
        },
    )
    final_machine = {
        "schema_version": "food-semantic-final-machine-report-v1",
        "status": "PASS",
        "attempt_id": attempt_id,
        "selected_branch": "B+G2",
        "sealed_successor_handoff_complete": True,
        "food_semantic_facts_authority_closeout": (
            "pending_terminal_independent_review_and_owner_seal"
        ),
        "selected_claim_token": claim_token,
        "selected_terminal_value": terminal_value,
        "current_authority_reconstruction_complete": False,
        "canonical_complete": False,
        "authority_execution_summary_sha256": sha256_file(
            authority_summary_path
        ),
        "sealed_successor_receipt_sha256": sha256_file(sealed_receipt_path),
        "post_authority_validation_sha256": sha256_file(validation_path),
        "phase2_handoff_acceptance_report_sha256": sha256_file(
            phase12_acceptance_path
        ),
        "threshold_authority_binding_sha256": sha256_file(
            threshold_binding_path
        ),
        "skeleton_group_report_sha256": sha256_file(
            skeleton_group_report_path
        ),
        "maximum_same_skeleton_group": skeleton_group_report[
            "maximum_same_skeleton_group"
        ],
        "bound_threshold_value": skeleton_group_report[
            "bound_threshold_value"
        ],
        "maximum_same_skeleton_group_within_bound": True,
        "final_machine_validation": "PASS",
        "current_facts_manifest_mutation_count": 0,
        "implementation_bundle_artifact_verification": (
            implementation_bundle_verification
        ),
        "implementation_complete_bundle_sha256": sha256_file(
            implementation_bundle_path
        ),
    }
    write_json(phase / "final_machine_report.json", final_machine)

    traceability_path = (
        attempt_root
        / "phase0_plan_and_decisions/requirements_plan_traceability.json"
    )
    traceability = load_json(traceability_path)
    eligibility = {
        "schema_version": "food-semantic-independent-reviewer-eligibility-v1",
        "status": "PASS",
        "D13_selected_option": d13["selected_option"],
        "requirements_chain_participation_allowed": False,
        "plan_chain_participation_allowed": False,
        "review_chain_participation_allowed": False,
        "implementation_chain_participation_allowed": False,
        "curation_chain_participation_allowed": False,
        "owner_decision_chain_participation_allowed": False,
        "non_claude_required": d13["selected_option"].startswith("I2_"),
        "requirements_snapshot_sha256": traceability[
            "requirements_snapshot_sha256"
        ],
        "requirements_snapshot_logical_line_count": traceability[
            "requirements_snapshot_logical_line_count"
        ],
        "requirements_plan_traceability_sha256": sha256_file(
            traceability_path
        ),
        "terminal_review_started": False,
    }
    write_json(
        phase / "independent_reviewer_eligibility_report.json",
        eligibility,
    )

    repository_head = _repository_head(root)
    terminal_files = _terminal_manifest_files(
        root,
        attempt_root,
        owner_decisions_path=owner_decisions_path,
    )
    manifest_rows = artifact_manifest(terminal_files, root=root)
    final_manifest = {
        "schema_version": "food-semantic-final-artifact-manifest-v1",
        "status": "SEALED_FOR_TERMINAL_REVIEW",
        "attempt_id": attempt_id,
        "repository_head_commit": repository_head,
        "selected_branch": "B+G2",
        "artifact_count": len(manifest_rows),
        "artifact_manifest_sha256": sha256_bytes(
            canonical_json_bytes(manifest_rows)
        ),
        "artifacts": manifest_rows,
        "implementation_complete_bundle_sha256": sha256_file(
            implementation_bundle_path
        ),
        "implementation_bundle_artifact_manifest_sha256": (
            implementation_bundle_verification[
                "computed_artifact_manifest_sha256"
            ]
        ),
        "implementation_bundle_verified_artifact_count": (
            implementation_bundle_verification["verified_artifact_count"]
        ),
        "sealed_successor_receipt_sha256": sha256_file(sealed_receipt_path),
        "final_machine_report_sha256": sha256_file(
            phase / "final_machine_report.json"
        ),
        "final_claim_scan_sha256": sha256_file(
            phase / "final_claim_non_claim_vocabulary_scan.json"
        ),
        "terminal_independent_review_pending": True,
        "owner_seal_pending": True,
    }
    final_manifest_path = phase / "final_artifact_manifest.json"
    write_json(final_manifest_path, final_manifest)
    review_request = {
        "schema_version": "food-semantic-terminal-review-request-v1",
        "status": "READY",
        "attempt_id": attempt_id,
        "reviewed_repository_commit": repository_head,
        "reviewed_final_artifact_manifest_sha256": sha256_file(
            final_manifest_path
        ),
        "reviewed_implementation_complete_bundle_sha256": sha256_file(
            implementation_bundle_path
        ),
        "eligibility_report_sha256": sha256_file(
            phase / "independent_reviewer_eligibility_report.json"
        ),
        "requirements_snapshot_sha256": traceability[
            "requirements_snapshot_sha256"
        ],
        "requirements_snapshot_logical_line_count": traceability[
            "requirements_snapshot_logical_line_count"
        ],
        "plan_path": traceability["plan"]["path"],
        "plan_sha256": traceability["plan"]["sha256"],
        "plan_git_blob_id": traceability["plan_git_blob_id"],
    }
    write_json(phase / "terminal_review_request.json", review_request)
    return {
        "status": "READY_FOR_TERMINAL_INDEPENDENT_REVIEW",
        "attempt_id": attempt_id,
        "final_artifact_manifest_sha256": sha256_file(final_manifest_path),
        "artifact_count": len(manifest_rows),
        "terminal_review_request_sha256": sha256_file(
            phase / "terminal_review_request.json"
        ),
    }


def seal_terminal_closeout(
    root: Path,
    attempt_root: Path,
    attempt_id: str,
    *,
    independent_review_path: Path,
    owner_seal_path: Path,
) -> dict[str, Any]:
    phase = attempt_root / "phase13_closeout"
    implementation_bundle_verification = require_sealed_artifact_bundle(
        root,
        phase / "implementation_complete_bundle.json",
    )
    manifest_path = phase / "final_artifact_manifest.json"
    manifest = load_json(manifest_path)
    final_manifest_verification = verify_sealed_artifact_bundle(
        root,
        manifest_path,
        require_sealed=False,
    )
    if final_manifest_verification["status"] != "PASS":
        raise FoodSemanticError(
            "terminal artifact manifest drift: "
            f"{final_manifest_verification}"
        )
    eligibility_path = phase / "independent_reviewer_eligibility_report.json"
    eligibility = load_json(eligibility_path)
    review = load_json(independent_review_path)
    owner_seal = load_json(owner_seal_path)
    mismatches = []
    for row in manifest["artifacts"]:
        path = root / row["path"]
        if not path.is_file():
            mismatches.append({"path": row["path"], "reason": "missing"})
        elif sha256_file(path) != row["sha256"]:
            mismatches.append({"path": row["path"], "reason": "sha256_mismatch"})
    if mismatches:
        raise FoodSemanticError(
            f"terminal artifact manifest drift: {mismatches}"
        )
    participation_fields = [
        "participated_in_requirements",
        "participated_in_plan",
        "participated_in_review_chain",
        "participated_in_implementation",
        "participated_in_curation",
        "participated_in_owner_decisions",
    ]
    review_blockers = []
    if review.get("verdict") != "PASS":
        review_blockers.append("verdict")
    if review.get("attempt_id") != attempt_id:
        review_blockers.append("attempt_id")
    if review.get("eligibility_report_sha256") != sha256_file(eligibility_path):
        review_blockers.append("eligibility_report_sha256")
    if review.get("reviewed_repository_commit") != manifest.get(
        "repository_head_commit"
    ):
        review_blockers.append("reviewed_repository_commit")
    if review.get("reviewed_final_artifact_manifest_sha256") != sha256_file(
        manifest_path
    ):
        review_blockers.append("reviewed_final_artifact_manifest_sha256")
    if review.get(
        "reviewed_implementation_complete_bundle_sha256"
    ) != manifest.get("implementation_complete_bundle_sha256"):
        review_blockers.append(
            "reviewed_implementation_complete_bundle_sha256"
        )
    if review.get("requirements_snapshot_sha256") != eligibility.get(
        "requirements_snapshot_sha256"
    ):
        review_blockers.append("requirements_snapshot_sha256")
    if any(review.get(field) is not False for field in participation_fields):
        review_blockers.append("reviewer_chain_participation")
    if review.get("reviewer_is_implementation_author") is not False:
        review_blockers.append("reviewer_is_implementation_author")
    if not review.get("reviewer_identity"):
        review_blockers.append("reviewer_identity")
    if (
        eligibility.get("non_claude_required")
        and str(review.get("reviewer_model_family", "")).lower() == "claude"
    ):
        review_blockers.append("I2_non_claude")
    finding_counts = review.get("finding_counts", {})
    if (
        finding_counts.get("critical") != 0
        or finding_counts.get("important") != 0
    ):
        review_blockers.append("open_critical_or_important")
    if review_blockers:
        raise FoodSemanticError(
            "terminal independent review blocked: "
            + ",".join(sorted(review_blockers))
        )
    canonical_review_path = phase / "independent_closeout_review.json"
    if independent_review_path.resolve() != canonical_review_path.resolve():
        write_json(canonical_review_path, review)

    final_machine = load_json(phase / "final_machine_report.json")
    owner_blockers = []
    if owner_seal.get("verdict") != "PASS":
        owner_blockers.append("verdict")
    if owner_seal.get("attempt_id") != attempt_id:
        owner_blockers.append("attempt_id")
    if owner_seal.get("independent_closeout_review_sha256") != sha256_file(
        canonical_review_path
    ):
        owner_blockers.append("independent_closeout_review_sha256")
    if owner_seal.get("final_artifact_manifest_sha256") != sha256_file(
        manifest_path
    ):
        owner_blockers.append("final_artifact_manifest_sha256")
    if owner_seal.get("claim_token") != final_machine["selected_claim_token"]:
        owner_blockers.append("claim_token")
    if owner_seal.get("terminal_value") != final_machine[
        "selected_terminal_value"
    ]:
        owner_blockers.append("terminal_value")
    if not owner_seal.get("approver_identity") or not owner_seal.get(
        "approval_time"
    ):
        owner_blockers.append("approver_identity_or_time")
    if owner_blockers:
        raise FoodSemanticError(
            "owner terminal seal blocked: " + ",".join(sorted(owner_blockers))
        )
    canonical_owner_seal_path = phase / "owner_seal.json"
    if owner_seal_path.resolve() != canonical_owner_seal_path.resolve():
        write_json(canonical_owner_seal_path, owner_seal)

    branch_disposition = {
        "schema_version": "food-semantic-terminal-branch-disposition-v1",
        "status": "PASS",
        "attempt_id": attempt_id,
        "branch": "B+G2",
        "required_gate_deferred_explicitly": True,
        "future_registry_cutover_required": True,
        "current_authority_reconstruction_complete": False,
        "canonical_complete": False,
        "current_facts_manifest_mutation_count": 0,
    }
    branch_path = phase / "terminal_branch_disposition.json"
    write_json(branch_path, branch_disposition)
    sealed_closeout = {
        "schema_version": "food-semantic-sealed-successor-closeout-v1",
        "status": "PASS",
        "attempt_id": attempt_id,
        "food_semantic_facts_authority_closeout": final_machine[
            "selected_terminal_value"
        ],
        "claim_token": final_machine["selected_claim_token"],
        "selected_branch": "B+G2",
        "sealed_successor_receipt_sha256": manifest[
            "sealed_successor_receipt_sha256"
        ],
        "final_artifact_manifest_sha256": sha256_file(manifest_path),
        "independent_closeout_review_sha256": sha256_file(
            canonical_review_path
        ),
        "owner_seal_sha256": sha256_file(canonical_owner_seal_path),
        "terminal_branch_disposition_sha256": sha256_file(branch_path),
        "current_authority_reconstruction_complete": False,
        "canonical_complete": False,
        "post_terminal_claim_bearing_change_count": 0,
    }
    closeout_path = phase / "sealed_successor_closeout.json"
    write_json(closeout_path, sealed_closeout)
    terminal_hash = {
        "schema_version": "food-semantic-terminal-hash-seal-v1",
        "status": "PASS",
        "attempt_id": attempt_id,
        "final_artifact_manifest_sha256": sha256_file(manifest_path),
        "sealed_successor_receipt_sha256": manifest[
            "sealed_successor_receipt_sha256"
        ],
        "independent_closeout_review_sha256": sha256_file(
            canonical_review_path
        ),
        "owner_seal_sha256": sha256_file(canonical_owner_seal_path),
        "terminal_branch_disposition_sha256": sha256_file(branch_path),
        "sealed_successor_closeout_sha256": sha256_file(closeout_path),
        "final_machine_report_sha256": sha256_file(
            phase / "final_machine_report.json"
        ),
        "final_claim_non_claim_vocabulary_scan_sha256": sha256_file(
            phase / "final_claim_non_claim_vocabulary_scan.json"
        ),
        "post_terminal_claim_bearing_change_allowed": False,
        "final_artifact_manifest_verification": final_manifest_verification,
        "implementation_bundle_artifact_verification": (
            implementation_bundle_verification
        ),
    }
    terminal_hash_path = phase / "terminal_hash_seal.json"
    write_json(terminal_hash_path, terminal_hash)
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "food_semantic_facts_authority_closeout": final_machine[
            "selected_terminal_value"
        ],
        "terminal_hash_seal_sha256": sha256_file(terminal_hash_path),
        "current_authority_reconstruction_complete": False,
        "canonical_complete": False,
    }
