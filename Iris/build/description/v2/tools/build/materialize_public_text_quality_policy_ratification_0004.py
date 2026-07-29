from __future__ import annotations

import json

import public_text_quality_acceptance as base
from public_text_quality_acceptance_official_0004 import ATTEMPT_ID, ATTEMPT_ROOT


OWNER_IDENTITY = "repository_owner_via_direct_codex_instruction"
DECIDED_AT = "2026-07-30T00:00:00Z"


def main() -> int:
    subject, _ = base._load_phase0_context(ATTEMPT_ROOT)
    base._require_artifacts(ATTEMPT_ROOT, 1)
    foundation = base.load_json_strict(
        base.DEFAULT_FOUNDATION_ROOT / base.FOUNDATION_CONTRACT_NAME
    )
    policy = base._official_policy_document(ATTEMPT_ID, foundation)
    policy_hash = base.sha256_bytes(base.pretty_json_bytes(policy))
    thresholds = {
        **foundation["policy_candidate"]["current_runtime_payload_thresholds"],
        **foundation["policy_candidate"]["naturalization_candidate_thresholds"],
    }
    affirmations = [
        {
            "metric_id": registration["metric_id"],
            "disposition_class": registration["disposition_class"],
            "threshold": thresholds[registration["metric_id"]]["threshold"],
            "default_exception_set_is_empty": True,
            "waiver_effect": "deferred_internal_debt_only",
        }
        for registration in foundation["metric_registry_candidate"]["registrations"]
    ]
    decision = {
        "schema_version": "public_text_quality_policy_ratification_decision_v1",
        "decision": "ratified",
        "candidate_policy_hash": policy_hash,
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "owner_acknowledges_evaluation_subject_may_be_blocked": True,
        "owner_identity": OWNER_IDENTITY,
        "decided_at": DECIDED_AT,
        "metric_affirmations": affirmations,
        "owner_instruction_basis": (
            "direct user instruction: keep the existing Foundation policy unchanged "
            "and create the hash-bound Phase 2 policy seal"
        ),
        "policy_change_authorized": False,
        "live_gate_adoption_authorized": False,
        "explicit_phase6_live_gate_approval_required": True,
    }
    decision["owner_binding_proof"] = base._owner_binding_proof(decision)
    waiver = {
        "waiver_schema_version": "public_text_quality_applicable_waiver_set_v1",
        "candidate_policy_hash": policy_hash,
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "waivers": [],
        "owner_identity": OWNER_IDENTITY,
    }
    waiver["owner_binding_proof"] = base._owner_binding_proof(waiver)
    base.write_once_or_same(
        base.OWNER_INPUT_ROOT / "policy_ratification_decision.json", decision
    )
    base.write_once_or_same(
        base.OWNER_INPUT_ROOT / "applicable_waiver_set.json", waiver
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "attempt_id": ATTEMPT_ID,
                "candidate_policy_hash": policy_hash,
                "metric_affirmation_count": len(affirmations),
                "waiver_count": 0,
                "policy_change_authorized": False,
                "live_gate_adoption_authorized": False,
                "explicit_phase6_live_gate_approval_required": True,
                "decision_path": base.repo_relative(
                    base.OWNER_INPUT_ROOT / "policy_ratification_decision.json"
                ),
                "waiver_path": base.repo_relative(
                    base.OWNER_INPUT_ROOT / "applicable_waiver_set.json"
                ),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
