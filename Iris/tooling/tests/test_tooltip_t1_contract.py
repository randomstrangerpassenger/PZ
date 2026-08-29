from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from iris_tooling.domains.tooltip_t1.contract import (
    AUTHORITY_ROOT,
    CONTRACT_FILES,
    DECISION_CONTRACT,
    _validate_contract_values,
    canonical_bytes,
    load_json,
    ratify_open_decisions,
    sha256_bytes,
    sha256_file,
    validate_contracts,
    validate_execution_subject,
)
from iris_tooling.domains.tooltip_t1.models import (
    LocaleSurfaceReadiness,
    SemanticSlotState,
    Slot,
    T2Progression,
    TooltipContractError,
    build_handoff_row,
)


def _values(root: Path) -> dict[Path, dict]:
    return {path: load_json(root / path) for path in CONTRACT_FILES}


def _rebind_bundle(values: dict[Path, dict]) -> None:
    lines = "".join(
        f"{path.name}={sha256_bytes(canonical_bytes(values[path]))}\n"
        for path in CONTRACT_FILES
        if path != DECISION_CONTRACT
    )
    digest = sha256_bytes(lines.encode())
    for row in values[DECISION_CONTRACT]["decisions"]:
        row["contract_sha256"] = digest


def _evidence(subject_identity: str) -> dict:
    records = {
        decision_id: {
            "decision_id": decision_id,
            "subject_identity_sha256": subject_identity,
            "evidence_state": "present",
        }
        for decision_id in ("P-2", "P-4", "P-5", "P-6", "P-7", "P-8", "P-10")
    }
    return {
        "schema_version": "iris-tooltip-pre-ratification-decision-evidence-v1",
        "phase": "W1-A_read_only_complete",
        "subject_identity_sha256": subject_identity,
        "records": records,
    }


@pytest.mark.parametrize(
    "case",
    ["valid", "bad_sha", "dirty", "stale", "route_mismatch", "historical_reentry", "fixed_authority", "open_choice", "phase_order", "same_subject_ratification"],
)
def test_subject_decision_lifecycle(case: str) -> None:
    root = Path(__file__).resolve().parents[3]
    digest = sha256_file(root / DECISION_CONTRACT)
    if case == "valid":
        assert DECISION_CONTRACT.as_posix() in validate_contracts(root, digest)
    elif case == "bad_sha":
        with pytest.raises(TooltipContractError, match="SHA-256 mismatch"):
            validate_contracts(root, "0" * 64)
    elif case in {"dirty", "stale"}:
        subject = {"working_tree_clean": case != "dirty", "commit": "a" * 40, "tree": "b" * 40}
        with pytest.raises(TooltipContractError, match="clean checkout|stale commit"):
            validate_execution_subject(subject, expected_commit="c" * 40 if case == "stale" else None)
    elif case in {"route_mismatch", "historical_reentry", "fixed_authority", "open_choice"}:
        values = deepcopy(_values(root))
        if case == "route_mismatch":
            values[AUTHORITY_ROOT / "tooltip_t1_tool_disposition_contract.json"]["entries"][0]["disposition"] = "diagnostic"
        elif case == "historical_reentry":
            values[AUTHORITY_ROOT / "tooltip_t1_tool_disposition_contract.json"]["entries"][-1]["current_execution_allowed"] = True
        elif case == "fixed_authority":
            values[DECISION_CONTRACT]["decisions"][0]["authority_references"] = []
        else:
            values[DECISION_CONTRACT]["decisions"][1]["selected_choice"] = "invented_default"
        _rebind_bundle(values)
        with pytest.raises(TooltipContractError):
            _validate_contract_values(values)
    else:
        decision = load_json(root / DECISION_CONTRACT)
        subject_identity = "d" * 64
        evidence = _evidence(subject_identity)
        if case == "phase_order":
            evidence["phase"] = "G1_before_W1-A"
            with pytest.raises(TooltipContractError, match="phase"):
                ratify_open_decisions(decision, evidence, evidence_sha256=sha256_bytes(canonical_bytes(evidence)), subject_identity_sha256=subject_identity)
        else:
            adopted = ratify_open_decisions(decision, evidence, evidence_sha256=sha256_bytes(canonical_bytes(evidence)), subject_identity_sha256=subject_identity)
            assert {row["decision_id"] for row in adopted} == {"P-2", "P-4", "P-5", "P-6", "P-7", "P-8", "P-10"}


@pytest.mark.parametrize(
    "case",
    ["absence_compaction", "absence_without_proof", "defect_not_compacted", "locale_split", "raw_inference_forbidden", "body_rewrite_forbidden", "layer2_workstream_candidate"],
)
def test_slot_layer2_layer3_input_contract(case: str) -> None:
    root = Path(__file__).resolve().parents[3]
    ready = Slot(
        "S1", "classification:x", SemanticSlotState.SELECTED,
        {"ko": "분류", "en": "Classification"},
        {"ko": LocaleSurfaceReadiness.READY, "en": LocaleSurfaceReadiness.READY},
    )
    if case == "absence_without_proof":
        with pytest.raises(TooltipContractError, match="positive owner proof"):
            Slot("S2", None, SemanticSlotState.LEGITIMATE_ABSENCE, {"ko": None, "en": None}, {"ko": LocaleSurfaceReadiness.NOT_APPLICABLE, "en": LocaleSurfaceReadiness.NOT_APPLICABLE})
        return
    absent = Slot(
        "S2", None, SemanticSlotState.LEGITIMATE_ABSENCE,
        {"ko": None, "en": None},
        {"ko": LocaleSurfaceReadiness.NOT_APPLICABLE, "en": LocaleSurfaceReadiness.NOT_APPLICABLE},
        authority_ref="owner.json#rows/Base.X/core_source_fact_ids=[]",
    )
    if case == "absence_compaction":
        absent_s3 = Slot("S3", None, SemanticSlotState.LEGITIMATE_ABSENCE, {"ko": None, "en": None}, {"ko": LocaleSurfaceReadiness.NOT_APPLICABLE, "en": LocaleSurfaceReadiness.NOT_APPLICABLE}, authority_ref="owner.json#S3=absent")
        absent_s4 = Slot("S4", None, SemanticSlotState.LEGITIMATE_ABSENCE, {"ko": None, "en": None}, {"ko": LocaleSurfaceReadiness.NOT_APPLICABLE, "en": LocaleSurfaceReadiness.NOT_APPLICABLE}, authority_ref="owner.json#S4=absent")
        row = build_handoff_row("Base.X", [absent_s4, absent, ready, absent_s3], progression=T2Progression.OPEN)
        assert [slot["slot_id"] for slot in row["slots"]] == ["S1"]
    elif case == "defect_not_compacted":
        defect = Slot("S2", None, SemanticSlotState.CORRECTION_REQUIRED, {"ko": None, "en": None}, {"ko": LocaleSurfaceReadiness.CORRECTION_REQUIRED, "en": LocaleSurfaceReadiness.CORRECTION_REQUIRED}, t2_blocking=True)
        absent_s3 = Slot("S3", None, SemanticSlotState.LEGITIMATE_ABSENCE, {"ko": None, "en": None}, {"ko": LocaleSurfaceReadiness.NOT_APPLICABLE, "en": LocaleSurfaceReadiness.NOT_APPLICABLE}, authority_ref="owner.json#S3=absent")
        absent_s4 = Slot("S4", None, SemanticSlotState.LEGITIMATE_ABSENCE, {"ko": None, "en": None}, {"ko": LocaleSurfaceReadiness.NOT_APPLICABLE, "en": LocaleSurfaceReadiness.NOT_APPLICABLE}, authority_ref="owner.json#S4=absent")
        with pytest.raises(TooltipContractError, match="T2-blocking"):
            build_handoff_row("Base.X", [ready, defect, absent_s3, absent_s4], progression=T2Progression.OPEN)
    elif case == "locale_split":
        slot = Slot("S2", "fact:x", SemanticSlotState.SELECTED, {"ko": "사실", "en": None}, {"ko": LocaleSurfaceReadiness.READY, "en": LocaleSurfaceReadiness.CORRECTION_REQUIRED}, t2_blocking=True)
        assert slot.displayable("ko") and not slot.displayable("en")
    elif case == "raw_inference_forbidden":
        contract = load_json(root / AUTHORITY_ROOT / "layer2_tooltip_input_contract.json")
        assert contract["raw_tag_resolution_allowed"] is False and contract["runtime_resolver_reimplementation_allowed"] is False
    elif case == "layer2_workstream_candidate":
        contract = load_json(root / AUTHORITY_ROOT / "layer2_tooltip_input_contract.json")
        candidate = contract["workstream_candidate_route"]
        assert contract["current_route"] == "no_admissible_authority_relation"
        assert candidate["path"] == "Iris/build/classification/data/classification_layer2_owner_output.json"
        assert candidate["current_ecosystem_adoption"] == "pending_T1_D6"
    else:
        contract = load_json(root / AUTHORITY_ROOT / "layer3_tooltip_input_contract.json")
        assert all(contract[key] is False for key in ("body_truncation_allowed", "body_summarization_allowed", "body_rewrite_allowed", "multiple_core_fact_synthesis_allowed"))
