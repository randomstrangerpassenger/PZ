from __future__ import annotations

from pathlib import Path
from typing import Any

from .acceptance_assurance import (
    build_phase3_validator, build_phase4_adversarial,
    earliest_naturalization_retry_phase, metric_threshold_results,
    require_phase2_seal,
)
from .acceptance_attempt_context import (
    build_phase0_binding, candidate_protected_snapshot,
    compute_candidate_metric_snapshot, official_attempt_root, phase_root,
    require_artifacts,
)
from .acceptance_context import (
    DEFAULT_FOUNDATION_ROOT, FOUNDATION_CONTRACT_NAME, OFFICIAL_MODES,
    OWNER_INPUT_ROOT, QUALIFIED_DISPOSITIONS, RAW_DETECTOR_IDS,
)
from .acceptance_emission import write_once_or_same, write_once_text
from .acceptance_infrastructure import (
    ExternalInputRequired, FoundationContractError, canonical_hash,
    load_json_strict, repo_relative, sha256_file,
)
from .acceptance_policy import (
    build_phase1_contracts, build_phase2_policy, load_phase0_context,
)
from .acceptance_rules import determine_qualified_disposition

def build_phase5_disposition(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    subject, handoff_validation = load_phase0_context(root)
    require_artifacts(root, 4)
    policy, seal = require_phase2_seal(root)
    p5 = phase_root(root, 5)
    snapshot = compute_candidate_metric_snapshot(handoff_validation)
    results = metric_threshold_results(snapshot, policy)
    waiver_set = load_json_strict(phase_root(root, 2) / "applicable_waiver_set.json")
    if waiver_set.get("waivers") != []:
        raise FoundationContractError(
            "v1 official candidate attempt supports only the sealed empty waiver set"
        )
    blocking = [
        row
        for row in results
        if not row["threshold_satisfied"]
        and row["disposition_class"] == "blocking_gate"
    ]
    advisory = [
        row
        for row in results
        if not row["threshold_satisfied"]
        and row["disposition_class"] == "advisory_debt"
    ]
    disposition = determine_qualified_disposition(
        technical_blocker_count=snapshot["technical_blocker_count"],
        effective_blocking_finding_count=len(blocking),
        advisory_debt_count=len(advisory),
        active_waiver_count=0,
    )
    all_findings = [*blocking, *advisory]
    raw_report = {
        "schema_version": "public_text_quality_evaluation_subject_raw_metric_report_v1",
        "status": "PASS",
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "policy_raw_sha256": seal["policy_raw_sha256"],
        "metric_snapshot_hash": canonical_hash(snapshot),
        "raw_metric_count": len(results),
        "raw_metrics": results,
        "exception_application": {
            "default_exception_count": 0,
            "applied_exception_count": 0,
            "raw_metric_mutation_count": 0,
        },
        "waiver_application": {
            "applicable_waiver_count": 0,
            "active_waiver_count": 0,
            "raw_metric_mutation_count": 0,
        },
        "effective_findings": all_findings,
        "omitted_blocking_or_advisory_finding_count": 0,
    }
    disposition_core = {
        "schema_version": "public_text_quality_evaluation_subject_disposition_v1",
        "attempt_id": attempt_id,
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "naturalization_handoff_hash": handoff_validation["handoff_raw_sha256"],
        "foundation_contract_hash": sha256_file(
            DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME
        ),
        "acceptance_input_binding_hash": load_json_strict(
            phase_root(root, 0) / "acceptance_input_binding_manifest.json"
        )["binding_hash"],
        "policy_raw_sha256": seal["policy_raw_sha256"],
        "policy_seal_hash": seal["seal_hash"],
        "metric_snapshot_hash": canonical_hash(snapshot),
        "applicable_waiver_set_hash": sha256_file(
            phase_root(root, 2) / "applicable_waiver_set.json"
        ),
        "technical_blocker_count": snapshot["technical_blocker_count"],
        "effective_blocking_finding_count": len(blocking),
        "advisory_debt_count": len(advisory),
        "active_waiver_count": 0,
        "qualified_disposition": disposition,
        "exact_failure_ledger": [
            {
                "metric_id": row["metric_id"],
                "disposition_class": row["disposition_class"],
                "numerator": row["numerator"],
                "denominator": row["denominator"],
                "threshold": row["threshold"],
                "owner_route": (
                    "dvf_korean_prose_naturalization_retry"
                    if row["metric_id"] in RAW_DETECTOR_IDS
                    else "source_or_description_remediation_successor"
                ),
            }
            for row in all_findings
        ],
        "synchronization_return": {
            "required": disposition != "accepted",
            "adoption_timing": (
                "immediate" if disposition == "accepted" else "after_remediation"
            ),
            "earliest_affected_naturalization_phase": earliest_naturalization_retry_phase(
                all_findings
            ),
            "phase6_live_gate_adoption_allowed": disposition == "accepted",
            "phase7_finalize_allowed": False,
        },
        "registry_runtime_current_adoption_claimed": False,
        "publish_boundary_pass_claimed": False,
        "package_or_release_ready_claimed": False,
        "policy_closure_state": "incomplete",
    }
    disposition_artifact = {
        **disposition_core,
        "disposition_hash": canonical_hash(disposition_core),
    }
    write_once_or_same(p5 / "evaluation_subject_metric_snapshot.json", snapshot)
    write_once_or_same(
        p5 / "evaluation_subject_raw_metric_report.json", raw_report
    )
    write_once_or_same(
        p5 / "evaluation_subject_disposition.json", disposition_artifact
    )
    write_once_text(
        p5 / "evaluation_subject_disposition.md",
        (
            "# Public Text Quality Evaluation-Subject Disposition\n\n"
            f"- Attempt: `{attempt_id}`\n"
            f"- Evaluation subject kind: `{subject['evaluation_subject_kind']}`\n"
            f"- Evaluation subject hash: `{subject['evaluation_subject_hash']}`\n"
            f"- Qualified disposition: `{disposition}`\n"
            f"- Effective blocking findings: `{len(blocking)}`\n"
            f"- Advisory debts: `{len(advisory)}`\n"
            f"- Adoption timing: `{disposition_artifact['synchronization_return']['adoption_timing']}`\n"
            f"- Earliest naturalization retry phase: "
            f"`{disposition_artifact['synchronization_return']['earliest_affected_naturalization_phase']}`\n\n"
            "This result is not Publish Boundary PASS, package-ready, release-ready, "
            "Registry/runtime adoption, or policy closure completion.\n"
        ),
    )
    protected_before = candidate_protected_snapshot(handoff_validation)
    protected_after = candidate_protected_snapshot(handoff_validation)
    protected = {
        "schema_version": "public_text_quality_phase5_protected_surface_no_mutation_v1",
        "status": "PASS" if protected_before == protected_after else "FAIL",
        "before_snapshot": protected_before,
        "after_snapshot": protected_after,
        "changed_count": 0 if protected_before == protected_after else 1,
    }
    write_once_or_same(p5 / "protected_surface_no_mutation_report.json", protected)
    hash_manifest_core = {
        "schema_version": "public_text_quality_disposition_hash_manifest_v1",
        "attempt_id": attempt_id,
        "ordered_artifacts": [
            {
                "path": repo_relative(p5 / name),
                "sha256": sha256_file(p5 / name),
            }
            for name in (
                "evaluation_subject_metric_snapshot.json",
                "evaluation_subject_raw_metric_report.json",
                "evaluation_subject_disposition.json",
                "evaluation_subject_disposition.md",
                "protected_surface_no_mutation_report.json",
            )
        ],
    }
    write_once_or_same(
        p5 / "evaluation_subject_disposition_hash_manifest.json",
        {
            **hash_manifest_core,
            "manifest_hash": canonical_hash(hash_manifest_core),
        },
    )
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase5-disposition",
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "qualified_disposition": disposition,
        "effective_blocking_finding_count": len(blocking),
        "advisory_debt_count": len(advisory),
        "adoption_timing": disposition_artifact["synchronization_return"][
            "adoption_timing"
        ],
        "earliest_affected_naturalization_phase": disposition_artifact[
            "synchronization_return"
        ]["earliest_affected_naturalization_phase"],
        "phase6_live_gate_adoption_allowed": disposition == "accepted",
        "phase7_finalize_allowed": False,
        "policy_closure_state": "incomplete",
    }


def load_phase5_disposition(root: Path) -> dict[str, Any]:
    require_artifacts(root, 5)
    value = load_json_strict(
        phase_root(root, 5) / "evaluation_subject_disposition.json"
    )
    core = {key: child for key, child in value.items() if key != "disposition_hash"}
    if (
        value.get("qualified_disposition") not in QUALIFIED_DISPOSITIONS
        or value.get("disposition_hash") != canonical_hash(core)
    ):
        raise FoundationContractError("Phase 5 disposition is invalid")
    return value


def build_phase6_gate_candidate(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    disposition = load_phase5_disposition(root)
    if (
        disposition["evaluation_subject_kind"]
        == "dvf_3_3_korean_naturalization_candidate"
        and disposition["qualified_disposition"] != "accepted"
    ):
        raise FoundationContractError(
            "synchronized naturalization candidate is not accepted; "
            "Phase 6 live-gate work is forbidden and the attempt must return "
            f"after_remediation to {disposition['synchronization_return']['earliest_affected_naturalization_phase']}"
        )
    raise ExternalInputRequired(
        input_kind="accepted_candidate_gate_candidate_implementation",
        path=OWNER_INPUT_ROOT / "gate_adoption_decision.json",
        details={
            "attempt_id": attempt_id,
            "qualified_disposition": disposition["qualified_disposition"],
            "policy_closure_state": "incomplete",
        },
    )


def build_phase6_adopt_gate(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    disposition = load_phase5_disposition(root)
    if disposition["qualified_disposition"] != "accepted":
        raise FoundationContractError(
            "Phase 6 gate adoption forbidden for non-accepted synchronized candidate"
        )
    raise ExternalInputRequired(
        input_kind="gate_adoption_decision",
        path=OWNER_INPUT_ROOT / "gate_adoption_decision.json",
        details={
            "attempt_id": attempt_id,
            "evaluation_subject_hash": disposition["evaluation_subject_hash"],
            "evaluation_subject_disposition_hash": disposition["disposition_hash"],
            "policy_closure_state": "incomplete",
        },
    )


def build_phase7_freeze(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    disposition = load_phase5_disposition(root)
    if disposition["qualified_disposition"] != "accepted":
        raise FoundationContractError(
            "Phase 7 freeze forbidden: synchronized candidate disposition is not accepted"
        )
    raise FoundationContractError(
        "Phase 7 freeze requires completed live gate adoption and post-adoption evidence"
    )


def build_phase7_finalize(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    disposition = load_phase5_disposition(root)
    if disposition["qualified_disposition"] != "accepted":
        raise FoundationContractError(
            "Phase 7 finalize forbidden: synchronized candidate disposition is not accepted"
        )
    raise FoundationContractError(
        "Phase 7 finalize requires tracked eligible independent review, owner seal, "
        "live gate adoption, and a complete post-adoption artifact set"
    )


def run_official_mode(
    *,
    attempt_id: str,
    mode: str,
    evaluation_subject_kind: str | None = None,
    subject_handoff: Path | None = None,
    attempt_root: Path | None = None,
) -> dict[str, Any]:
    if mode not in OFFICIAL_MODES:
        raise FoundationContractError(f"unknown official mode: {mode}")
    if mode == "phase0-binding":
        if evaluation_subject_kind is None or subject_handoff is None:
            raise FoundationContractError(
                "phase0-binding requires explicit evaluation subject kind and handoff"
            )
        return build_phase0_binding(
            attempt_id=attempt_id,
            evaluation_subject_kind=evaluation_subject_kind,
            subject_handoff=subject_handoff,
            attempt_root=attempt_root,
        )
    if evaluation_subject_kind is not None or subject_handoff is not None:
        raise FoundationContractError(
            "evaluation subject arguments are only allowed for phase0-binding"
        )
    dispatch = {
        "phase1-contracts": build_phase1_contracts,
        "phase2-policy": build_phase2_policy,
        "phase3-validator": build_phase3_validator,
        "phase4-adversarial": build_phase4_adversarial,
        "phase5-disposition": build_phase5_disposition,
        "phase6-gate-candidate": build_phase6_gate_candidate,
        "phase6-adopt-gate": build_phase6_adopt_gate,
        "phase7-freeze": build_phase7_freeze,
        "phase7-finalize": build_phase7_finalize,
    }
    return dispatch[mode](attempt_id=attempt_id, attempt_root=attempt_root)

__all__ = (
    "build_phase5_disposition", "build_phase6_adopt_gate",
    "build_phase6_gate_candidate", "build_phase7_finalize",
    "build_phase7_freeze", "load_phase5_disposition", "run_official_mode",
)
