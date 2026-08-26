from __future__ import annotations

from pathlib import Path
from typing import Any

from .acceptance_assurance import metric_threshold_results, require_phase2_seal
from .acceptance_attempt_context import (
    compute_candidate_metric_snapshot, official_attempt_root, phase_root,
    require_artifacts,
)
from .acceptance_context import (
    DEFAULT_FOUNDATION_ROOT, FOUNDATION_CONTRACT_NAME, PHASE_ARTIFACTS,
)
from .acceptance_disposition import load_phase5_disposition
from .acceptance_infrastructure import (
    FoundationContractError, load_json_strict, sha256_bytes,
)
from .acceptance_policy import load_phase0_context
from .acceptance_rules import determine_qualified_disposition

def _validate_phase0(root: Path) -> dict[str, Any]:
    subject, validation = load_phase0_context(root)
    p0 = phase_root(root, 0)
    entries_bytes = (p0 / "canonical_entries_projection.jsonl").read_bytes()
    metric_bytes = (p0 / "canonical_metric_projection.jsonl").read_bytes()
    entries_digest = load_json_strict(p0 / "canonical_entries_digest.json")
    metric_digest = load_json_strict(
        p0 / "canonical_metric_projection_digest.json"
    )
    preflight = load_json_strict(p0 / "vcs_required_surface_preflight.json")
    protected = load_json_strict(p0 / "protected_surface_no_mutation_report.json")
    snapshot = compute_candidate_metric_snapshot(validation)
    if (
        entries_digest.get("sha256") != sha256_bytes(entries_bytes)
        or metric_digest.get("sha256") != sha256_bytes(metric_bytes)
        or metric_digest.get("normalized_projection_hash")
        != snapshot["metric_projection_hash"]
        or preflight.get("status") != "PASS"
        or protected.get("status") != "PASS"
        or protected.get("changed_count") != 0
    ):
        raise FoundationContractError("Phase 0 validation failed")
    return {
        "status": "PASS",
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "naturalization_handoff_hash": validation["handoff_raw_sha256"],
    }


def _validate_phase1(root: Path) -> dict[str, Any]:
    _validate_phase0(root)
    require_artifacts(root, 1)
    p1 = phase_root(root, 1)
    foundation = load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    metric = load_json_strict(p1 / "metric_registry.json")
    denominator = load_json_strict(p1 / "denominator_registry.json")
    report = load_json_strict(
        p1 / "metric_denominator_contract_validation_report.json"
    )
    if (
        metric.get("registrations")
        != foundation["metric_registry_candidate"]["registrations"]
        or denominator.get("registrations")
        != foundation["denominator_registry_candidate"]["registrations"]
        or report.get("status") != "PASS"
        or report.get("foundation_metric_projection_match") is not True
        or report.get("foundation_denominator_projection_match") is not True
    ):
        raise FoundationContractError("Phase 1 validation failed")
    return {
        "status": "PASS",
        "metric_count": report["metric_count"],
        "denominator_count": report["denominator_count"],
    }


def _validate_phase2(root: Path) -> dict[str, Any]:
    _validate_phase1(root)
    policy, seal = require_phase2_seal(root)
    p2 = phase_root(root, 2)
    ratification = load_json_strict(p2 / "policy_ratification_record.json")
    waiver = load_json_strict(p2 / "applicable_waiver_set.json")
    if (
        ratification.get("status") != "PASS"
        or ratification.get("metric_affirmation_missing_count") != 0
        or ratification.get("metric_affirmation_duplicate_count") != 0
        or ratification.get("metric_affirmation_mismatch_count") != 0
        or waiver.get("waivers") != []
        or policy.get("foundation_projection_byte_equivalent") is not True
    ):
        raise FoundationContractError("Phase 2 validation failed")
    return {
        "status": "PASS",
        "policy_raw_sha256": seal["policy_raw_sha256"],
        "policy_seal_hash": seal["seal_hash"],
    }


def _validate_phase3(root: Path) -> dict[str, Any]:
    _validate_phase2(root)
    require_artifacts(root, 3)
    p3 = phase_root(root, 3)
    reports = [
        load_json_strict(p3 / name)
        for name in PHASE_ARTIFACTS[3]
    ]
    if any(report.get("status") != "PASS" for report in reports):
        raise FoundationContractError("Phase 3 validation failed")
    return {"status": "PASS", "validator_report_count": len(reports)}


def _validate_phase4(root: Path) -> dict[str, Any]:
    _validate_phase3(root)
    require_artifacts(root, 4)
    p4 = phase_root(root, 4)
    json_reports = [
        load_json_strict(p4 / name)
        for name in PHASE_ARTIFACTS[4]
        if name.endswith(".json")
    ]
    if any(report.get("status") != "PASS" for report in json_reports):
        raise FoundationContractError("Phase 4 validation failed")
    return {
        "status": "PASS",
        "adversarial_report_count": len(json_reports),
        "roadmap_mandatory_fixture_count": json_reports[0][
            "roadmap_mandatory_fixture_count"
        ],
    }


def _validate_phase5(root: Path) -> dict[str, Any]:
    _validate_phase4(root)
    disposition = load_phase5_disposition(root)
    p5 = phase_root(root, 5)
    snapshot = load_json_strict(
        p5 / "evaluation_subject_metric_snapshot.json"
    )
    raw = load_json_strict(p5 / "evaluation_subject_raw_metric_report.json")
    policy, _ = require_phase2_seal(root)
    recomputed = compute_candidate_metric_snapshot(
        load_phase0_context(root)[1]
    )
    results = metric_threshold_results(recomputed, policy)
    blocking_count = sum(
        not row["threshold_satisfied"]
        and row["disposition_class"] == "blocking_gate"
        for row in results
    )
    advisory_count = sum(
        not row["threshold_satisfied"]
        and row["disposition_class"] == "advisory_debt"
        for row in results
    )
    expected = determine_qualified_disposition(
        technical_blocker_count=recomputed["technical_blocker_count"],
        effective_blocking_finding_count=blocking_count,
        advisory_debt_count=advisory_count,
        active_waiver_count=0,
    )
    if (
        snapshot != recomputed
        or raw.get("omitted_blocking_or_advisory_finding_count") != 0
        or disposition["qualified_disposition"] != expected
        or disposition["effective_blocking_finding_count"] != blocking_count
        or disposition["advisory_debt_count"] != advisory_count
        or load_json_strict(
            p5 / "protected_surface_no_mutation_report.json"
        ).get("status")
        != "PASS"
    ):
        raise FoundationContractError("Phase 5 disposition validation failed")
    return {
        "status": "PASS",
        "qualified_disposition": expected,
        "effective_blocking_finding_count": blocking_count,
        "advisory_debt_count": advisory_count,
        "adoption_timing": disposition["synchronization_return"][
            "adoption_timing"
        ],
        "earliest_affected_naturalization_phase": disposition[
            "synchronization_return"
        ]["earliest_affected_naturalization_phase"],
        "phase6_live_gate_adoption_allowed": expected == "accepted",
        "phase7_finalize_allowed": False,
        "policy_closure_state": "incomplete",
    }


def validate_official_attempt(
    *,
    attempt_id: str,
    requirement: str,
    attempt_root: Path | None = None,
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    validators = {
        "phase0": _validate_phase0,
        "phase1": _validate_phase1,
        "phase2": _validate_phase2,
        "phase3": _validate_phase3,
        "phase4": _validate_phase4,
        "phase5": _validate_phase5,
    }
    if requirement in validators:
        result = validators[requirement](root)
        return {
            "schema_version": "public_text_quality_official_validation_result_v1",
            "status": "PASS",
            "attempt_id": attempt_id,
            "requirement": requirement,
            "no_write": True,
            **{key: value for key, value in result.items() if key != "status"},
        }
    if requirement in (
        "gate-candidate",
        "phase6",
        "independent-review",
        "owner-seal",
        "terminal-seal",
    ):
        disposition = _validate_phase5(root)
        if disposition["qualified_disposition"] != "accepted":
            raise FoundationContractError(
                f"{requirement} is forbidden for non-accepted synchronized candidate"
            )
        raise FoundationContractError(
            f"{requirement} artifacts are not complete"
        )
    if requirement == "required-gate":
        disposition = _validate_phase5(root)
        return {
            "schema_version": "public_text_quality_required_gate_result_v1",
            "status": (
                "PASS"
                if disposition["qualified_disposition"] == "accepted"
                else "QUALIFIED_DEBT"
                if disposition["qualified_disposition"]
                == "deferred_internal_debt"
                else "BLOCKED"
            ),
            "attempt_id": attempt_id,
            "qualified_disposition": disposition["qualified_disposition"],
            "policy_closure_state": "incomplete",
            "publish_boundary_pass_claimed": False,
            "package_or_release_ready_claimed": False,
        }
    raise FoundationContractError(f"unknown official validation requirement: {requirement}")

__all__ = ("validate_official_attempt",)
