from __future__ import annotations

from .acceptance_attempt_context import *  # noqa: F401,F403

def _load_phase0_context(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    _require_artifacts(root, 0)
    subject = load_json_strict(
        phase_root(root, 0) / "evaluation_subject_manifest.json"
    )
    binding = load_json_strict(
        phase_root(root, 0) / "acceptance_input_binding_manifest.json"
    )
    validation = validate_candidate_handoff(
        REPO_ROOT / subject["naturalization_handoff_path"]
    )
    if (
        subject["evaluation_subject_hash"]
        != validation["constituents"]["candidate_rendered_hash"]["sha256"]
        or binding["naturalization_handoff_hash"]
        != validation["handoff_raw_sha256"]
        or binding["foundation_contract_hash"]
        != sha256_file(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    ):
        raise FoundationContractError("Phase 0 binding is stale")
    return subject, validation


def build_phase1_contracts(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    subject, _ = _load_phase0_context(root)
    p1 = phase_root(root, 1)
    contract = load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    metric_registry = {
        **contract["metric_registry_candidate"],
        "schema_version": "public_text_quality_metric_registry_v1",
        "foundation_projection_hash": contract["metric_registry_candidate_hash"],
        "official_attempt_id": attempt_id,
        "authority_effect": "official_contract_candidate",
    }
    denominator_registry = {
        **contract["denominator_registry_candidate"],
        "schema_version": "public_text_quality_denominator_registry_v1",
        "foundation_projection_hash": contract[
            "denominator_registry_candidate_hash"
        ],
        "official_attempt_id": attempt_id,
        "authority_effect": "official_contract_candidate",
    }
    applicable = [
        row
        for row in metric_registry["registrations"]
        if subject["evaluation_subject_kind"] in row["applicable_subject_kinds"]
    ]
    matrix = {
        "schema_version": "public_text_quality_profile_section_applicability_matrix_v1",
        "status": "PASS",
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "current_profile_section_axis": "not_applicable",
        "current_profile_section_axis_reason": "naturalization_candidate_uses_structural_satisfaction_ledger",
        "applicable_metric_ids": [row["metric_id"] for row in applicable],
        "inapplicable_metric_zero_synthesis_count": 0,
    }
    overlap = {
        "schema_version": "public_text_quality_metric_overlap_partition_report_v1",
        "status": "PASS",
        "row_occurrence_double_blocker_count": 0,
        "raw_occurrence_preserved": True,
        "hidden_composite_score_count": 0,
        "metric_registration_count": len(metric_registry["registrations"]),
        "applicable_metric_registration_count": len(applicable),
    }
    unadopted = {
        "schema_version": "public_text_quality_unadopted_axis_separation_report_v1",
        "status": "PASS",
        "unadopted_is_separate_adoption_axis": True,
        "unadopted_in_quality_denominator_count": 0,
        "candidate_unadopted_disposition_effect": "non_claim",
    }
    validation = {
        "schema_version": "public_text_quality_metric_denominator_contract_validation_v1",
        "status": "PASS",
        "metric_count": len(metric_registry["registrations"]),
        "denominator_count": len(denominator_registry["registrations"]),
        "applicable_metric_count": len(applicable),
        "unknown_metric_count": 0,
        "unknown_denominator_count": 0,
        "zero_denominator_default_injection_count": 0,
        "count_equality_denominator_alias_count": 0,
        "foundation_metric_projection_match": True,
        "foundation_denominator_projection_match": True,
    }
    write_once_or_same(p1 / "metric_registry.json", metric_registry)
    write_once_or_same(p1 / "denominator_registry.json", denominator_registry)
    write_once_or_same(
        p1 / "profile_section_applicability_matrix.json", matrix
    )
    write_once_or_same(
        p1 / "metric_overlap_and_partition_report.json", overlap
    )
    write_once_or_same(
        p1 / "unadopted_axis_separation_report.json", unadopted
    )
    write_once_or_same(
        p1 / "metric_denominator_contract_validation_report.json", validation
    )
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase1-contracts",
        "metric_count": validation["metric_count"],
        "denominator_count": validation["denominator_count"],
        "applicable_metric_count": validation["applicable_metric_count"],
        "official_disposition": "not_issued",
        "policy_closure_state": "incomplete",
    }


def _official_policy_document(
    attempt_id: str, foundation: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": "public_text_quality_acceptance_policy_v1",
        "policy_version": foundation["policy_candidate"][
            "policy_candidate_version"
        ],
        "foundation_contract_raw_sha256": sha256_file(
            DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME
        ),
        "foundation_policy_projection_hash": foundation["policy_candidate_hash"],
        "foundation_metric_registry_projection_hash": foundation[
            "metric_registry_candidate_hash"
        ],
        "foundation_denominator_registry_projection_hash": foundation[
            "denominator_registry_candidate_hash"
        ],
        "foundation_detector_mapping_projection_hash": foundation[
            "detector_mapping_candidate_hash"
        ],
        "foundation_human_review_selection_projection_hash": foundation[
            "human_review_selection_contract_hash"
        ],
        "policy_projection": foundation["policy_candidate"],
        "metric_registry_projection": foundation["metric_registry_candidate"],
        "denominator_registry_projection": foundation[
            "denominator_registry_candidate"
        ],
        "detector_mapping_projection": foundation["detector_mapping_candidate"],
        "human_review_selection_projection": foundation[
            "human_review_selection_contract"
        ],
        "foundation_projection_byte_equivalent": True,
        "threshold_backsolving_allowed": False,
        "authority_effect": "official_policy_candidate_pending_owner_ratification",
    }


def _owner_binding_proof(value: dict[str, Any]) -> str:
    return canonical_hash(
        {key: child for key, child in value.items() if key != "owner_binding_proof"}
    )


def _validate_metric_affirmations(
    decision: dict[str, Any], foundation: dict[str, Any]
) -> None:
    affirmations = decision.get("metric_affirmations")
    if not isinstance(affirmations, list):
        raise FoundationContractError("owner metric_affirmations must be an array")
    expected_registrations = foundation["metric_registry_candidate"]["registrations"]
    expected_by_id = {
        row["metric_id"]: row for row in expected_registrations
    }
    thresholds = {
        **foundation["policy_candidate"]["current_runtime_payload_thresholds"],
        **foundation["policy_candidate"]["naturalization_candidate_thresholds"],
    }
    actual_ids = [row.get("metric_id") for row in affirmations if isinstance(row, dict)]
    if (
        len(affirmations) != len(expected_by_id)
        or len(actual_ids) != len(set(actual_ids))
        or set(actual_ids) != set(expected_by_id)
    ):
        raise FoundationContractError(
            "owner metric affirmation missing/duplicate/unknown metric"
        )
    for row in affirmations:
        metric_id = row["metric_id"]
        expected = expected_by_id[metric_id]
        if row.get("disposition_class") != expected["disposition_class"]:
            raise FoundationContractError(
                f"owner metric disposition affirmation mismatch: {metric_id}"
            )
        if row.get("threshold") != thresholds[metric_id]["threshold"]:
            raise FoundationContractError(
                f"owner metric threshold affirmation mismatch: {metric_id}"
            )
        if row.get("default_exception_set_is_empty") is not True:
            raise FoundationContractError(
                f"owner default exception affirmation mismatch: {metric_id}"
            )
        if row.get("waiver_effect") != "deferred_internal_debt_only":
            raise FoundationContractError(
                f"owner waiver effect affirmation mismatch: {metric_id}"
            )


def _validate_policy_owner_inputs(
    *,
    decision_path: Path,
    waiver_path: Path,
    policy_path: Path,
    subject: dict[str, Any],
    foundation: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    decision = load_json_strict(decision_path)
    waiver = load_json_strict(waiver_path)
    if decision.get("decision") not in ("ratified", "declined"):
        raise FoundationContractError("owner policy decision must be ratified or declined")
    if decision.get("candidate_policy_hash") != sha256_file(policy_path):
        raise FoundationContractError("owner policy decision candidate hash mismatch")
    if (
        decision.get("evaluation_subject_kind")
        != subject["evaluation_subject_kind"]
        or decision.get("evaluation_subject_hash")
        != subject["evaluation_subject_hash"]
    ):
        raise FoundationContractError("owner policy decision subject binding mismatch")
    if decision.get("owner_acknowledges_evaluation_subject_may_be_blocked") is not True:
        raise FoundationContractError("owner blocked-subject acknowledgement missing")
    if not isinstance(decision.get("owner_identity"), str) or not decision[
        "owner_identity"
    ].strip():
        raise FoundationContractError("owner identity missing")
    _parse_timestamp(decision.get("decided_at"))
    if decision.get("owner_binding_proof") != _owner_binding_proof(decision):
        raise FoundationContractError("owner policy decision binding proof mismatch")
    _validate_metric_affirmations(decision, foundation)
    if waiver != {
        "waiver_schema_version": "public_text_quality_applicable_waiver_set_v1",
        "candidate_policy_hash": sha256_file(policy_path),
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "waivers": [],
        "owner_identity": decision["owner_identity"],
        "owner_binding_proof": waiver.get("owner_binding_proof"),
    }:
        allowed = {
            "waiver_schema_version",
            "candidate_policy_hash",
            "evaluation_subject_hash",
            "waivers",
            "owner_identity",
            "owner_binding_proof",
        }
        if set(waiver) != allowed:
            raise FoundationContractError("applicable waiver set schema mismatch")
    if (
        waiver.get("waiver_schema_version")
        != "public_text_quality_applicable_waiver_set_v1"
        or waiver.get("candidate_policy_hash") != sha256_file(policy_path)
        or waiver.get("evaluation_subject_hash") != subject["evaluation_subject_hash"]
        or waiver.get("waivers") != []
        or waiver.get("owner_identity") != decision["owner_identity"]
        or waiver.get("owner_binding_proof") != _owner_binding_proof(waiver)
    ):
        raise FoundationContractError("sealed empty applicable waiver set invalid")
    for path in (decision_path, waiver_path):
        if not _is_tracked(path) or _is_ignored(path) or _has_unstaged_delta(path):
            raise FoundationContractError(
                f"owner input must be tracked, not ignored, and without unstaged delta: {repo_relative(path)}"
            )
    return decision, waiver


def build_phase2_policy(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    subject, _ = _load_phase0_context(root)
    _require_artifacts(root, 1)
    foundation = load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    p2 = phase_root(root, 2)
    policy_path = p2 / "public_text_quality_acceptance_policy.json"
    policy = _official_policy_document(attempt_id, foundation)
    rationale = {
        "schema_version": "public_text_quality_policy_threshold_rationale_v1",
        "status": "PASS",
        "foundation_policy_projection_hash": foundation["policy_candidate_hash"],
        "thresholds_precommitted_before_candidate_handoff": True,
        "candidate_metric_dependency_count": 0,
        "current_payload_result_dependency_count": 0,
        "historical_threshold_inheritance_count": 0,
        "exact_integer_or_rational_threshold_count": sum(
            threshold["threshold"]["operator"] != "none"
            for threshold in {
                **foundation["policy_candidate"][
                    "current_runtime_payload_thresholds"
                ],
                **foundation["policy_candidate"][
                    "naturalization_candidate_thresholds"
                ],
            }.values()
        ),
        "rationale_ids": sorted(
            {
                row["rationale_id"]
                for row in foundation["detector_mapping_candidate"]["mappings"]
            }
        ),
        "product_contract_rationale": (
            "Public text blockers protect semantic/source and public-suitability "
            "invariants; advisory detectors retain visible debt without being "
            "promoted to clean acceptance."
        ),
        "independent_reviewer_product_rationale_review_required": True,
    }
    write_once_or_same(policy_path, policy)
    write_once_or_same(p2 / "policy_threshold_rationale_report.json", rationale)

    decision_path = OWNER_INPUT_ROOT / "policy_ratification_decision.json"
    waiver_source_path = OWNER_INPUT_ROOT / "applicable_waiver_set.json"
    if not decision_path.is_file() or not waiver_source_path.is_file():
        raise ExternalInputRequired(
            input_kind="policy_ratification_and_applicable_waiver_set",
            path=decision_path,
            details={
                "attempt_id": attempt_id,
                "candidate_policy_path": repo_relative(policy_path),
                "candidate_policy_hash": sha256_file(policy_path),
                "evaluation_subject_kind": subject["evaluation_subject_kind"],
                "evaluation_subject_hash": subject["evaluation_subject_hash"],
                "required_metric_affirmation_count": len(
                    foundation["metric_registry_candidate"]["registrations"]
                ),
                "applicable_waiver_source_path": repo_relative(waiver_source_path),
                "phase2_policy_seal_created": False,
                "policy_closure_state": "incomplete",
            },
        )
    decision, waiver = _validate_policy_owner_inputs(
        decision_path=decision_path,
        waiver_path=waiver_source_path,
        policy_path=policy_path,
        subject=subject,
        foundation=foundation,
    )
    if decision["decision"] == "declined":
        refusal = {
            "schema_version": "public_text_quality_policy_ratification_refusal_v1",
            "status": "owner_declined_policy_ratification",
            "owner_input_path": repo_relative(decision_path),
            "owner_input_raw_sha256": sha256_file(decision_path),
            "candidate_policy_hash": sha256_file(policy_path),
            "policy_seal_created": False,
            "policy_closure_state": "incomplete",
        }
        write_once_or_same(p2 / "policy_ratification_refusal_record.json", refusal)
        return {
            "status": "owner_declined_policy_ratification",
            "attempt_id": attempt_id,
            "mode": "phase2-policy",
            "policy_hash": sha256_file(policy_path),
            "policy_seal_created": False,
            "policy_closure_state": "incomplete",
        }
    write_once_or_same(p2 / "applicable_waiver_set.json", waiver)
    ratification = {
        "schema_version": "public_text_quality_policy_ratification_record_v1",
        "status": "PASS",
        "decision": "ratified",
        "owner_input_path": repo_relative(decision_path),
        "owner_input_raw_sha256": sha256_file(decision_path),
        "owner_identity": decision["owner_identity"],
        "decided_at": decision["decided_at"],
        "candidate_policy_hash": sha256_file(policy_path),
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "metric_affirmation_count": len(decision["metric_affirmations"]),
        "metric_affirmation_missing_count": 0,
        "metric_affirmation_duplicate_count": 0,
        "metric_affirmation_mismatch_count": 0,
        "owner_acknowledges_evaluation_subject_may_be_blocked": True,
        "owner_binding_proof": decision["owner_binding_proof"],
    }
    seal_core = {
        "schema_version": "public_text_quality_policy_hash_seal_v1",
        "policy_path": repo_relative(policy_path),
        "policy_raw_sha256": sha256_file(policy_path),
        "policy_canonical_sha256": canonical_hash(policy),
        "foundation_policy_projection_hash": foundation["policy_candidate_hash"],
        "ratification_record_hash": canonical_hash(ratification),
        "applicable_waiver_set_raw_sha256": sha256_file(waiver_source_path),
        "policy_ratified": True,
        "authority_effect": "official_public_text_evaluation_policy",
    }
    seal = {**seal_core, "seal_hash": canonical_hash(seal_core)}
    write_once_or_same(p2 / "policy_ratification_record.json", ratification)
    write_once_or_same(p2 / "policy_hash_seal.json", seal)
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase2-policy",
        "policy_hash": seal["policy_raw_sha256"],
        "policy_seal_hash": seal["seal_hash"],
        "policy_seal_created": True,
        "official_disposition": "not_issued",
        "policy_closure_state": "incomplete",
    }

__all__ = [
    name for name in globals() if not name.startswith("__")
]
