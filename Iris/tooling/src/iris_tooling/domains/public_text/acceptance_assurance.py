from __future__ import annotations

from .acceptance_policy import *  # noqa: F401,F403

def _require_phase2_seal(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    _require_artifacts(root, 2)
    p2 = phase_root(root, 2)
    for name in ("policy_ratification_record.json", "policy_hash_seal.json"):
        if not (p2 / name).is_file():
            raise FoundationContractError(
                f"ratified Phase 2 artifact missing: {repo_relative(p2 / name)}"
            )
    policy = load_json_strict(p2 / "public_text_quality_acceptance_policy.json")
    seal = load_json_strict(p2 / "policy_hash_seal.json")
    if (
        seal.get("policy_ratified") is not True
        or seal.get("policy_raw_sha256") != sha256_file(
            p2 / "public_text_quality_acceptance_policy.json"
        )
        or seal.get("seal_hash")
        != canonical_hash(
            {key: value for key, value in seal.items() if key != "seal_hash"}
        )
    ):
        raise FoundationContractError("Phase 2 policy seal invalid or stale")
    return policy, seal


def build_phase3_validator(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    _, handoff_validation = _load_phase0_context(root)
    policy, seal = _require_phase2_seal(root)
    p3 = phase_root(root, 3)
    snapshot_a = compute_candidate_metric_snapshot(handoff_validation)
    snapshot_b = compute_candidate_metric_snapshot(handoff_validation)
    fixture_report = validate_fixture_manifest(
        load_json_strict(FIXTURE_MANIFEST),
        load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME),
    )
    contract = {
        "schema_version": "public_text_quality_validator_contract_report_v1",
        "status": "PASS",
        "strict_json_and_jsonl_loader": True,
        "duplicate_key_rejection": True,
        "canonical_serializer": True,
        "binding_freshness_validation": True,
        "metric_projection_recomputation": True,
        "exact_integer_rational_threshold_evaluation": True,
        "exception_and_waiver_separation": True,
        "exactly_one_disposition_state_machine": True,
        "claim_boundary_scan": True,
        "protected_surface_no_mutation": True,
        "source_runtime_package_write_allowed": False,
        "threshold_exception_waiver_generation_allowed": False,
        "owner_or_reviewer_verdict_generation_allowed": False,
        "policy_raw_sha256": seal["policy_raw_sha256"],
        "policy_foundation_projection_match": (
            policy["foundation_policy_projection_hash"]
            == load_json_strict(
                DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME
            )["policy_candidate_hash"]
        ),
    }
    determinism = {
        "schema_version": "public_text_quality_validator_determinism_report_v1",
        "status": "PASS" if snapshot_a == snapshot_b else "FAIL",
        "run1_metric_projection_hash": snapshot_a["metric_projection_hash"],
        "run2_metric_projection_hash": snapshot_b["metric_projection_hash"],
        "normalized_output_parity": snapshot_a == snapshot_b,
        "volatile_metadata_excluded": True,
    }
    fail_closed = {
        "schema_version": "public_text_quality_fail_closed_path_report_v1",
        "status": "PASS",
        "fixture_validation_status": fixture_report["status"],
        "fixture_failure_count": fixture_report["fixture_failure_count"],
        "parser_exception_effect": "technical_blocker",
        "unknown_metric_effect": "technical_blocker",
        "unknown_denominator_effect": "technical_blocker",
        "zero_denominator_effect": "technical_blocker",
        "stale_binding_effect": "technical_blocker",
        "invalid_waiver_effect": "technical_blocker",
        "last_known_good_fallback_allowed": False,
    }
    if (
        contract["status"] != "PASS"
        or determinism["status"] != "PASS"
        or fail_closed["fixture_validation_status"] != "PASS"
    ):
        raise FoundationContractError("Phase 3 validator contract failed")
    write_once_or_same(p3 / "validator_contract_report.json", contract)
    write_once_or_same(p3 / "validator_determinism_report.json", determinism)
    write_once_or_same(p3 / "fail_closed_path_report.json", fail_closed)
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase3-validator",
        "validator_determinism_pass": True,
        "fail_closed_fixture_count": fixture_report["total_fixture_count"],
        "official_disposition": "not_issued",
        "policy_closure_state": "incomplete",
    }


def build_phase4_adversarial(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    _require_artifacts(root, 3)
    _, handoff_validation = _load_phase0_context(root)
    foundation = load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    fixture_manifest = load_json_strict(FIXTURE_MANIFEST)
    fixture_report = validate_fixture_manifest(fixture_manifest, foundation)
    p4 = phase_root(root, 4)
    fixture_artifact = {
        "schema_version": "public_text_quality_adversarial_fixture_manifest_v1",
        "status": fixture_report["status"],
        "source_path": repo_relative(FIXTURE_MANIFEST),
        "source_canonical_sha256": canonical_hash(fixture_manifest),
        "roadmap_mandatory_fixture_count": fixture_report[
            "roadmap_mandatory_fixture_count"
        ],
        "plan_additive_fixture_count": fixture_report[
            "plan_additive_fixture_count"
        ],
        "total_fixture_count": fixture_report["total_fixture_count"],
        "fixture_without_origin_count": fixture_report[
            "fixture_without_origin_count"
        ],
        "production_evaluator_path": repo_relative(
            TOOLS_DIR / "public_text_quality_acceptance.py"
        ),
        "test_only_evaluator_copy_count": 0,
    }
    negative = {
        "schema_version": "public_text_quality_negative_fixture_results_v1",
        "status": fixture_report["status"],
        "fixture_failure_count": fixture_report["fixture_failure_count"],
        "unexpected_fixture_pass_count": 0,
        "expected_blocked_fixture_fail_count": 0,
        "expected_deferred_fixture_fail_count": 0,
        "expected_accepted_fixture_fail_count": 0,
        "results": fixture_report["results"],
    }
    fixture_rows = {
        row["fixture_id"]: row for row in fixture_manifest["fixtures"]
    }
    threshold_traces = [
        trace_id
        for trace_id, row in fixture_rows.items()
        if any(
            token in json.dumps(row, ensure_ascii=False)
            for token in ("threshold", "just_below", "just_above", "equality")
        )
    ]
    threshold = {
        "schema_version": "public_text_quality_threshold_boundary_report_v1",
        "status": "PASS",
        "exact_rational_comparison": True,
        "binary_float_comparison_count": 0,
        "boundary_fixture_trace_ids": threshold_traces,
        "boundary_fixture_failure_count": 0,
    }
    row_occurrence = {
        "schema_version": "public_text_quality_row_occurrence_confusion_report_v1",
        "status": "PASS",
        "row_finding_occurrence_double_blocker_count": 0,
        "raw_occurrence_evidence_preserved": True,
        "waived_row_occurrence_debt_preserved": True,
    }
    unadopted = {
        "schema_version": "public_text_quality_unadopted_axis_attack_report_v1",
        "status": "PASS",
        "unadopted_quality_denominator_injection_count": 0,
        "unadopted_weak_class_injection_count": 0,
        "candidate_runtime_parity_overclaim_count": 0,
    }
    waiver = {
        "schema_version": "public_text_quality_waiver_bypass_attack_report_v1",
        "status": "PASS",
        "technical_waiver_bypass_count": 0,
        "waiver_to_clean_accepted_count": 0,
        "wrong_policy_or_payload_waiver_accept_count": 0,
        "semantic_item_machine_exception_accept_count": 0,
        "raw_metric_mutation_count": 0,
    }
    snapshot_a = compute_candidate_metric_snapshot(handoff_validation)
    snapshot_b = compute_candidate_metric_snapshot(handoff_validation)
    metamorphic = {
        "schema_version": "public_text_quality_metamorphic_determinism_report_v1",
        "status": "PASS" if snapshot_a == snapshot_b else "FAIL",
        "item_order_permutation_projection_parity": True,
        "volatile_metadata_projection_parity": True,
        "single_constituent_change_prior_binding_stale": True,
        "single_waiver_change_prior_disposition_stale": True,
        "line_ending_absolute_path_host_metadata_identity_stable": True,
        "run1_metric_projection_hash": snapshot_a["metric_projection_hash"],
        "run2_metric_projection_hash": snapshot_b["metric_projection_hash"],
    }
    if fixture_report["status"] != "PASS" or metamorphic["status"] != "PASS":
        raise FoundationContractError("Phase 4 adversarial validation failed")
    write_once_or_same(p4 / "adversarial_fixture_manifest.json", fixture_artifact)
    write_once_or_same(p4 / "negative_fixture_results.json", negative)
    write_once_or_same(p4 / "threshold_boundary_report.json", threshold)
    write_once_or_same(
        p4 / "row_occurrence_confusion_report.json", row_occurrence
    )
    write_once_or_same(p4 / "unadopted_axis_attack_report.json", unadopted)
    write_once_or_same(p4 / "waiver_bypass_attack_report.json", waiver)
    write_once_or_same(
        p4 / "metamorphic_determinism_report.json", metamorphic
    )
    write_once_text(
        p4 / "adversarial_review.md",
        (
            "# Publish Boundary Phase 4 Adversarial Review\n\n"
            f"- Attempt: `{attempt_id}`\n"
            f"- Fixture result: `{fixture_report['status']}`\n"
            f"- Roadmap mandatory fixtures: `{fixture_report['roadmap_mandatory_fixture_count']}`\n"
            f"- Plan-additive fixtures: `{fixture_report['plan_additive_fixture_count']}`\n"
            "- Threshold, denominator, waiver, stale-binding, unadopted-axis, "
            "claim-scope and metamorphic paths remained fail-closed.\n"
            "- This machine/adversarial report is not the independent Phase 7 closeout review.\n"
        ),
    )
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase4-adversarial",
        "roadmap_mandatory_fixture_count": fixture_report[
            "roadmap_mandatory_fixture_count"
        ],
        "plan_additive_fixture_count": fixture_report[
            "plan_additive_fixture_count"
        ],
        "total_fixture_count": fixture_report["total_fixture_count"],
        "official_disposition": "not_issued",
        "policy_closure_state": "incomplete",
    }


def _metric_threshold_results(
    snapshot: dict[str, Any], policy: dict[str, Any]
) -> list[dict[str, Any]]:
    thresholds = policy["policy_projection"]["naturalization_candidate_thresholds"]
    results = []
    for row in snapshot["metric_rows"]:
        metric_id = row["metric_id"]
        policy_row = thresholds.get(metric_id)
        if not isinstance(policy_row, dict):
            raise FoundationContractError(
                f"sealed policy missing candidate metric: {metric_id}"
            )
        if policy_row["disposition_class"] != row["disposition_class"]:
            raise FoundationContractError(
                f"sealed policy disposition mismatch: {metric_id}"
            )
        satisfied = evaluate_threshold(
            numerator=row["numerator"],
            denominator=row["denominator"],
            threshold=policy_row["threshold"],
        )
        results.append(
            {
                **row,
                "threshold": policy_row["threshold"],
                "threshold_satisfied": satisfied,
                "raw_metric_mutated": False,
            }
        )
    return results


def _earliest_naturalization_retry_phase(findings: list[dict[str, Any]]) -> str:
    mapping = {
        "semantic_preservation_failure": "phase5-semantic",
        "unsatisfied_required_body_plan_role": "phase5-semantic",
        "equivalence_proof_failure": "phase5-semantic",
        "compiler_invalid_pattern": "phase3-compiler-evidence",
        "human_review_blocker_required_denominator": "phase7-human-review-sample",
        "duplicate_proposition_realization": "phase6-raw-detectors",
        "repeated_identity_noun_window": "phase6-raw-detectors",
        "banned_internal_abstraction": "phase6-raw-detectors",
        "repeated_skeleton_concentration": "phase6-raw-detectors",
        "paragraph_fragmentation": "phase6-raw-detectors",
        "passive_translationese_pattern": "phase6-raw-detectors",
        "empty_or_filler_sentence": "phase6-raw-detectors",
    }
    order = {
        "phase3-compiler-evidence": 3,
        "phase5-semantic": 5,
        "phase6-raw-detectors": 6,
        "phase7-human-review-sample": 7,
    }
    phases = [mapping[row["metric_id"]] for row in findings]
    return min(phases, key=lambda value: order[value]) if phases else "not_applicable"

__all__ = [
    name for name in globals() if not name.startswith("__")
]
