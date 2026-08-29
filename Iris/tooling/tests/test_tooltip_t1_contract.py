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
    validate_layer3_owner_output,
)
from iris_tooling.domains.tooltip_t1.models import (
    LocaleSurfaceReadiness,
    SemanticSlotState,
    Slot,
    T2Progression,
    TooltipContractError,
    build_handoff_row,
)
from iris_tooling.domains.tooltip_t1.d5 import (
    DISPOSITION_RECORD,
    TARGETS,
    build_target_snapshot,
    evaluate_disposition_snapshot,
    validate_disposition_authority,
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
        for decision_id in ("P-2", "P-4", "P-5", "P-6", "P-7", "P-8")
    }
    return {
        "schema_version": "iris-tooltip-pre-ratification-decision-evidence-v1",
        "phase": "W1-A_read_only_complete",
        "subject_identity_sha256": subject_identity,
        "records": records,
    }


@pytest.mark.parametrize(
    "case",
    [
        "valid", "bad_sha", "dirty", "stale", "route_mismatch", "recipe_locale_route", "historical_reentry",
        "fixed_authority", "open_choice", "phase_order", "same_subject_ratification",
        "d5_issuance_applicability", "d5_target_scope", "d5_approval_relation", "d5_mechanism_rebind",
    ],
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
    elif case in {"route_mismatch", "recipe_locale_route", "historical_reentry", "fixed_authority", "open_choice"}:
        values = deepcopy(_values(root))
        if case == "route_mismatch":
            values[AUTHORITY_ROOT / "tooltip_t1_tool_disposition_contract.json"]["entries"][0]["disposition"] = "diagnostic"
        elif case == "recipe_locale_route":
            values[AUTHORITY_ROOT / "layer4_recipe_locale_input_contract.json"]["lookup_stage"] = "before_selection"
        elif case == "historical_reentry":
            values[AUTHORITY_ROOT / "tooltip_t1_tool_disposition_contract.json"]["entries"][-1]["current_execution_allowed"] = True
        elif case == "fixed_authority":
            values[DECISION_CONTRACT]["decisions"][0]["authority_references"] = []
        else:
            values[DECISION_CONTRACT]["decisions"][1]["selected_choice"] = "invented_default"
        _rebind_bundle(values)
        with pytest.raises(TooltipContractError):
            _validate_contract_values(values)
    elif case.startswith("d5_"):
        disposition = load_json(root / DISPOSITION_RECORD)
        snapshot = build_target_snapshot(root)
        validate_disposition_authority(disposition)
        if case == "d5_issuance_applicability":
            report = evaluate_disposition_snapshot(disposition, snapshot)
            assert report["applicable"] is True
            assert report["commit_tree_equality_used"] is False
            unrelated_change = deepcopy(snapshot)
            unrelated_change["unrelated_full_type_layer_change"] = "not fingerprinted"
            assert evaluate_disposition_snapshot(disposition, unrelated_change)["applicable"] is True
            changed_target = deepcopy(snapshot)
            changed_target["targets"][TARGETS[0]]["layer2"]["row_sha256"] = "0" * 64
            assert evaluate_disposition_snapshot(disposition, changed_target)["applicable"] is False
            wrong_issuance = deepcopy(disposition)
            wrong_issuance["issuance_subject"]["commit"] = "0" * 40
            with pytest.raises(TooltipContractError, match="issuance subject"):
                validate_disposition_authority(wrong_issuance)
        elif case == "d5_target_scope":
            third_member = deepcopy(snapshot)
            third_member["normalized_collision_members"].append("Base.LEMONGRASS")
            assert evaluate_disposition_snapshot(disposition, third_member)["applicable"] is False
            incomplete = deepcopy(disposition)
            incomplete["records"] = incomplete["records"][:1]
            with pytest.raises(TooltipContractError, match="exactly two"):
                validate_disposition_authority(incomplete)
            case_mutated = deepcopy(disposition)
            case_mutated["records"][1]["exact_full_type"] = "Base.LEMONGRASS"
            with pytest.raises(TooltipContractError, match="case-mutated"):
                validate_disposition_authority(case_mutated)
        elif case == "d5_approval_relation":
            invalid_approval = deepcopy(disposition)
            invalid_approval["pre_mutation_owner_approval"]["approval_sha256"] = "0" * 64
            with pytest.raises(TooltipContractError, match="approval hash"):
                validate_disposition_authority(invalid_approval)
            conflict = deepcopy(disposition)
            conflict["records"][0]["identity_relation"]["counterpart_exact_full_type"] = TARGETS[0]
            with pytest.raises(TooltipContractError, match="relation conflict"):
                validate_disposition_authority(conflict)
            branch_b_overlay = deepcopy(disposition)
            branch_b_overlay["records"][0]["support_disposition"] = "exclude_after_upstream_authority_withdrawal"
            with pytest.raises(TooltipContractError, match="support disposition"):
                validate_disposition_authority(branch_b_overlay)
        else:
            blocking_axis = deepcopy(disposition)
            blocking_axis["collision_terminal_mechanism"]["id"] = "resolved_observation_blocking_axis_transition_v1"
            with pytest.raises(TooltipContractError, match="unsupported"):
                validate_disposition_authority(blocking_axis)
            nonempty_correction = deepcopy(disposition)
            nonempty_correction["collision_terminal_mechanism"]["expected_correction_row_exact_set"] = list(TARGETS)
            with pytest.raises(TooltipContractError, match="eliminate"):
                validate_disposition_authority(nonempty_correction)
            unselected = deepcopy(disposition)
            del unselected["collision_terminal_mechanism"]["id"]
            with pytest.raises(TooltipContractError, match="missing or unsupported"):
                validate_disposition_authority(unselected)
            values = deepcopy(_values(root))
            values[DECISION_CONTRACT]["d5_contract_rebind"]["post_implementation_owner_approval"]["approval_sha256"] = "0" * 64
            with pytest.raises(TooltipContractError, match="rebind approval hash"):
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
            assert {row["decision_id"] for row in adopted} == {"P-2", "P-4", "P-5", "P-6", "P-7", "P-8"}


@pytest.mark.parametrize(
    "case",
    ["absence_compaction", "absence_without_proof", "defect_not_compacted", "locale_split", "raw_inference_forbidden", "body_rewrite_forbidden", "explicit_owner_absence", "invalid_owner_absence", "layer2_workstream_candidate", "layer2_display_silence_compaction"],
)
def test_slot_layer2_layer3_input_contract(case: str) -> None:
    root = Path(__file__).resolve().parents[3]
    ready = Slot(
        "S1", "classification:x", SemanticSlotState.SELECTED,
        {"ko": "분류", "en": "Classification"},
        {"ko": LocaleSurfaceReadiness.READY, "en": LocaleSurfaceReadiness.READY},
    )
    if case in {"explicit_owner_absence", "invalid_owner_absence"}:
        absence_row = {
            "exact_full_type": "Base.X",
            "disposition": "approved_legitimate_absence",
            "absence_reason_code": "DVF_NO_APPROVED_DESCRIPTION_MATERIAL",
            "owner": "DVF owner",
            "acceptance_evidence": {"artifact": "d3_independent_defect_exclusion_verdict.json", "sha256": "a" * 64},
            "applicable_scope": "Base.X",
            "reaudit_condition": "exact owner material changes",
            "authority_decision_ref": "user_prompt_owner_gate_preapproval_2026-08-29",
        }
        if case == "invalid_owner_absence":
            absence_row["acceptance_evidence"] = {"artifact": "producer-self-report.json", "sha256": "a" * 64}
        fact_entries: dict = {}
        absence_entries = {"Base.X": absence_row}
        payload = {
            "schema_version": "iris-tooltip-t1-layer3-owner-input-v2",
            "generation_id": "dvf33-test",
            "entries": fact_entries,
            "fact_entries": fact_entries,
            "absence_entries": absence_entries,
            "manifest": {
                "fact_entry_count": 0,
                "absence_entry_count": 1,
                "total_owner_row_count": 1,
                "fact_entries_sha256": sha256_bytes(canonical_bytes(fact_entries)),
                "absence_entries_sha256": sha256_bytes(canonical_bytes(absence_entries)),
            },
        }
        if case == "invalid_owner_absence":
            with pytest.raises(TooltipContractError, match="independent evidence"):
                validate_layer3_owner_output(payload, expected_generation_id="dvf33-test")
        else:
            facts, absences = validate_layer3_owner_output(payload, expected_generation_id="dvf33-test")
            assert not facts and set(absences) == {"Base.X"}
        return
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
    elif case == "layer2_display_silence_compaction":
        silent_s1 = Slot("S1", None, SemanticSlotState.LEGITIMATE_ABSENCE, {"ko": None, "en": None}, {"ko": LocaleSurfaceReadiness.NOT_APPLICABLE, "en": LocaleSurfaceReadiness.NOT_APPLICABLE}, reason_codes=("no_membership_record",), authority_ref="classification_layer2_resolution_contract.json#successor_amendment")
        ready_s2 = Slot("S2", "fact:x", SemanticSlotState.SELECTED, {"ko": "사실", "en": "Fact"}, {"ko": LocaleSurfaceReadiness.READY, "en": LocaleSurfaceReadiness.READY})
        absent_s3 = Slot("S3", None, SemanticSlotState.LEGITIMATE_ABSENCE, {"ko": None, "en": None}, {"ko": LocaleSurfaceReadiness.NOT_APPLICABLE, "en": LocaleSurfaceReadiness.NOT_APPLICABLE}, authority_ref="owner.json#S3=absent")
        absent_s4 = Slot("S4", None, SemanticSlotState.LEGITIMATE_ABSENCE, {"ko": None, "en": None}, {"ko": LocaleSurfaceReadiness.NOT_APPLICABLE, "en": LocaleSurfaceReadiness.NOT_APPLICABLE}, authority_ref="owner.json#S4=absent")
        row = build_handoff_row("Base.X", [silent_s1, ready_s2, absent_s3, absent_s4], progression=T2Progression.OPEN)
        assert [slot["slot_id"] for slot in row["slots"]] == ["S2"]
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
        d2_candidate = contract["workstream_d2_relation_candidate_route"]
        assert d2_candidate["artifact"] == "layer2_menu_consumer_relation.jsonl"
        assert d2_candidate["producer"] == "iris_tooling.domains.tooltip_t1.d2"
        assert d2_candidate["dispositions"] == ["verified", "not_applicable", "correction_required"]
        assert d2_candidate["current_ecosystem_adoption"] == "pending_T1_D6"
        amendment = contract["successor_owner_amendment"]
        assert amendment["layer2_is_required_for_every_support_fulltype"] is False
        assert amendment["d2_owns_menu_relation_and_applicable_na_parity"] is True
    else:
        contract = load_json(root / AUTHORITY_ROOT / "layer3_tooltip_input_contract.json")
        assert all(contract[key] is False for key in ("body_truncation_allowed", "body_summarization_allowed", "body_rewrite_allowed", "multiple_core_fact_synthesis_allowed"))
