from __future__ import annotations

from pathlib import Path

import pytest

from iris_tooling.domains.layer4.tooltip_t1_d4 import build_owner_projection, validate_registry
from iris_tooling.domains.classification.layer2_contract import support_universe
from iris_tooling.domains.classification.layer2_materializer import materialize
from iris_tooling.domains.classification.layer2_validator import validate_owner_output

from iris_tooling.domains.tooltip_t1.audit import (
    _strict_candidate_result,
    build_progression_record,
    candidate_closeout_record,
    classify_progression,
    correction_completeness_metrics,
    finalize_closeout,
    layer2_title_surfaces,
    menu_owner_output_self_comparison_count,
    normalized_collisions,
    source_mutation_count,
    validate_whole_universe,
)
from iris_tooling.domains.tooltip_t1.contract import AUTHORITY_ROOT, canonical_bytes, git_subject, load_json, sha256_file
from iris_tooling.domains.tooltip_t1.d5 import (
    TARGETS,
    collision_correction_members,
    exact_identity_metrics,
)
from iris_tooling.domains.tooltip_t1.d2 import validate_relation_lifecycle
from iris_tooling.domains.tooltip_t1.models import (
    LocaleSurfaceReadiness,
    SemanticSlotState,
    Slot,
    T2Progression,
    TooltipContractError,
    build_handoff_row,
    mock_consume,
)


def _audited_slots() -> list[Slot]:
    ready = Slot(
        "S1", "identity:x", SemanticSlotState.SELECTED,
        {"ko": "분류", "en": "Classification"},
        {"ko": LocaleSurfaceReadiness.READY, "en": LocaleSurfaceReadiness.READY},
    )
    absent = [
        Slot(
            slot_id, None, SemanticSlotState.LEGITIMATE_ABSENCE,
            {"ko": None, "en": None},
            {"ko": LocaleSurfaceReadiness.NOT_APPLICABLE, "en": LocaleSurfaceReadiness.NOT_APPLICABLE},
            authority_ref=f"owner.json#{slot_id}=absent",
        )
        for slot_id in ("S2", "S3", "S4")
    ]
    return [ready, *absent]


def _ready_slot(slot_id: str = "S1") -> Slot:
    return Slot(
        slot_id, "identity:x", SemanticSlotState.SELECTED,
        {"ko": "분류", "en": "Classification"},
        {"ko": LocaleSurfaceReadiness.READY, "en": LocaleSurfaceReadiness.READY},
    )


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def _finalization_fixture(tmp_path: Path, repository_root: Path, mode: str) -> dict[str, Path | str]:
    subject = git_subject(repository_root)
    exact_subject = {"commit": subject["commit"], "tree": subject["tree"]}
    candidate_root = tmp_path / "candidate"
    candidate_root.mkdir()
    if mode.startswith("strict_"):
        contract_bundle = "a" * 64
        strict_subject = {
            "schema_version": "iris-tooltip-t1-subject-binding-v1",
            **exact_subject,
            "working_tree_clean": True,
            "contract_sha256": {"authority_contract_bundle_sha256": contract_bundle},
        }
        support = sorted(support_universe(repository_root))
        slots = {full_type: tuple(_audited_slots()) for full_type in support}
        relation = {
            full_type: {"disposition": "verified" if index < 1406 else "not_applicable"}
            for index, full_type in enumerate(support)
        }
        progression, blockers = build_progression_record([])
        _strict_candidate_result(
            candidate_root,
            strict_subject,
            {"authority_contract_bundle_sha256": contract_bundle},
            {"schema_version": "test-admission"},
            support,
            slots,
            [],
            progression,
            blockers,
            relation,
        )
        if mode == "strict_hash_mismatch":
            manifest = load_json(candidate_root / "t2_handoff_manifest.json")
            manifest["handoff_input_sha256"] = "f" * 64
            _write_json(candidate_root / "t2_handoff_manifest.json", manifest)
    else:
        candidate_files = {
            "subject_binding.json": {
                "schema_version": "iris-tooltip-t1-subject-binding-v1",
                **exact_subject,
                "working_tree_clean": True,
            },
            "axis_separated_closeout_record.json": candidate_closeout_record(T2Progression.UPSTREAM),
            "t2_progression_record.json": {
                "schema_version": "iris-tooltip-t2-progression-v1",
                "T2_FULL_DATA_PROGRESSION": T2Progression.UPSTREAM.value,
            },
        }
        for name, payload in candidate_files.items():
            _write_json(candidate_root / name, payload)
        artifacts = {name: sha256_file(candidate_root / name) for name in candidate_files}
        candidate_receipt = {
            "schema_version": "iris-tooltip-t1-run-receipt-v1",
            "subject_binding_sha256": artifacts["subject_binding.json"],
            "artifacts": artifacts,
            "T2_FULL_DATA_PROGRESSION": T2Progression.UPSTREAM.value,
            "source_mutation": 0,
        }
        _write_json(candidate_root / "run_receipt.json", candidate_receipt)

    claim_id = "tooltip-t1-finalization-fixture"
    chains: dict[str, dict] = {}
    orchestration_paths: dict[str, Path] = {}
    for label in ("run_a", "run_b"):
        gate_root = tmp_path / label
        result_path = gate_root / "result" / "run_receipt.json"
        canonical_path = gate_root / "result" / "canonical_result.json"
        _write_json(result_path, {"status": "PASS", "subject": exact_subject})
        _write_json(canonical_path, {"status": "PASS", "subject": exact_subject})
        orchestration_path = gate_root / "orchestration.json"
        gate_subject = exact_subject
        if mode == "subject_mismatch" and label == "run_b":
            gate_subject = {"commit": "f" * 40, "tree": exact_subject["tree"]}
        orchestration = {
            "schema_version": "iris-clean-checkout-orchestration-receipt-v1",
            "claim_id": claim_id,
            "launch_status": "gate_failed" if mode == "gate_failure" and label == "run_a" else "succeeded",
            "native_exit_code": 2 if mode == "gate_failure" and label == "run_a" else 0,
            "receipt_write_status": "succeeded",
            "identity": {"subject": gate_subject},
            "environment": {"configured": True, "restored": True},
            "result_receipt": {
                "exists": True,
                "path": result_path.resolve().as_posix(),
                "sha256": sha256_file(result_path),
            },
        }
        _write_json(orchestration_path, orchestration)
        orchestration_paths[label] = orchestration_path
        chains[label] = {
            "orchestration_receipt": {
                "path": orchestration_path.resolve().as_posix(),
                "sha256": sha256_file(orchestration_path),
                "claim_id": claim_id,
            },
            "inner_run_receipt": {
                "path": result_path.resolve().as_posix(),
                "sha256": sha256_file(result_path),
            },
            "canonical_result": {
                "path": canonical_path.resolve().as_posix(),
                "sha256": sha256_file(canonical_path),
            },
        }
    comparator_path = tmp_path / "compare" / "compare_receipt.json"
    _write_json(comparator_path, {
        "schema_version": "iris-clean-checkout-compare-receipt-v1",
        "status": "succeeded",
        "native_exit_code": 0,
        "receipt_write_status": "succeeded",
        "claim_id": claim_id,
        "subject": exact_subject,
        "environment": {"configured": True, "restored": True},
        "run_chains": chains,
    })
    return {
        "candidate_root": candidate_root,
        "candidate_sha256": sha256_file(candidate_root / "run_receipt.json"),
        "run_a": orchestration_paths["run_a"],
        "run_b": orchestration_paths["run_b"],
        "comparator": comparator_path,
        "output": tmp_path / "final",
    }


@pytest.mark.parametrize(
    "case",
    ["open_ko", "open_en", "blocked_upstream", "blocked_contract", "extra_row_field", "extra_slot_field", "duplicate_slot", "out_of_order"],
)
def test_minimal_t2_handoff_mock_consumer(case: str) -> None:
    if case in {"open_ko", "open_en"}:
        row = build_handoff_row("Base.X", _audited_slots(), progression=T2Progression.OPEN)
        locale = "ko" if case == "open_ko" else "en"
        assert mock_consume(row, locale) == ["분류" if locale == "ko" else "Classification"]
        return
    if case in {"blocked_upstream", "blocked_contract"}:
        progression = T2Progression.UPSTREAM if case == "blocked_upstream" else T2Progression.CONTRACT
        with pytest.raises(TooltipContractError, match="progression OPEN"):
            build_handoff_row("Base.X", _audited_slots(), progression=progression)
        return
    row = build_handoff_row("Base.X", _audited_slots(), progression=T2Progression.OPEN)
    if case == "extra_row_field":
        row["owner"] = "forbidden"
    elif case == "extra_slot_field":
        row["slots"][0]["parity"] = "verified"
    elif case == "duplicate_slot":
        row["slots"].append(dict(row["slots"][0]))
    else:
        row["slots"] = [
            {"slot_id": "S3", "semantic_identity": "uc:x", "localized_surfaces": {"ko": "행동", "en": "Action"}},
            row["slots"][0],
        ]
    with pytest.raises(TooltipContractError):
        mock_consume(row, "ko")


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("open", T2Progression.OPEN),
        ("upstream", T2Progression.UPSTREAM),
        ("contract", T2Progression.CONTRACT),
        ("mock_product_decision", T2Progression.CONTRACT),
        ("mixed", T2Progression.MIXED),
        ("duplicate_universe", None),
        ("unknown_reason", None),
        ("missing_owner", None),
        ("missing_acceptance", None),
        ("missing_reaudit", None),
        ("source_immutable", None),
        ("source_mutated", None),
        ("normalized_collision", None),
        ("d5_exact_pair_resolved", None),
        ("d5_normalized_authoritative_key_rejected", None),
        ("d5_dispositionless_closure_rejected", None),
        ("owner_output_self_comparison", None),
        ("candidate_pre_gate_axis", None),
        ("recipe_locale_projection", None),
        ("nonblocking_correction", None),
        ("d3_owner_absence_nonblocking", None),
        ("gate_failure", None),
        ("gate_subject_mismatch", None),
        ("gate_same_subject_success", None),
        ("layer2_owner_output", None),
        ("layer2_title", None),
        ("layer2_title_silence", None),
        ("layer2_terminal_relation", None),
        ("layer2_authority_fallback", None),
        ("layer2_identity_locale", None),
        ("layer2_consumer_boundary", None),
        ("layer2_silence_fallback", None),
        ("layer2_silence_no_membership", None),
        ("layer2_silence_multi_without_primary", None),
        ("d2_relation_verified", None),
        ("d2_relation_not_applicable", None),
        ("d2_relation_correction_required", None),
        ("strict_blocked_absence", None),
        ("strict_handoff_hash_mismatch", None),
        ("strict_handoff_success", None),
    ],
)
def test_whole_universe_audit_progression(case: str, expected: T2Progression | None, tmp_path: Path) -> None:
    if case == "layer2_title":
        owner = {
            "category_surface": {"ko": "도구", "en": "Tools"},
            "primary_subcategory_surface": {"ko": "수리", "en": "Repair"},
        }
        assert layer2_title_surfaces(owner) == {"ko": "[도구 - 수리]", "en": "[Tools - Repair]"}
        return
    if case == "layer2_title_silence":
        slots = _audited_slots()
        slots[0] = Slot("S1", None, SemanticSlotState.LEGITIMATE_ABSENCE,
                        {"ko": None, "en": None},
                        {"ko": LocaleSurfaceReadiness.NOT_APPLICABLE, "en": LocaleSurfaceReadiness.NOT_APPLICABLE},
                        authority_ref="owner#display_silence")
        slots[1] = _ready_slot("S2")
        row = build_handoff_row("Base.X", slots, progression=T2Progression.OPEN)
        assert [slot["slot_id"] for slot in row["slots"]] == ["S2"]
        assert row["slots"][0]["localized_surfaces"] == slots[1].localized_surfaces
        return
    if expected is not None:
        counts = {
            "open": (0, 0, 0), "upstream": (1, 0, 0),
            "contract": (0, 1, 0), "mock_product_decision": (0, 0, 1),
            "mixed": (1, 1, 0),
        }[case]
        assert classify_progression(*counts) is expected
        return
    if case == "duplicate_universe":
        rows = [{"full_type": "Base.A", "overall_readiness": "ready"}] * 2
        assert validate_whole_universe({"Base.A", "Base.B"}, rows) == {
            "duplicate_full_type": 1,
            "missing_supported_full_type": 1,
            "unexpected_supported_full_type": 0,
            "unclassified_readiness": 0,
        }
        return
    if case in {"source_immutable", "source_mutated"}:
        before = {"owner.json": "a"}
        after = before if case == "source_immutable" else {"owner.json": "b"}
        assert source_mutation_count(before, after) == (case == "source_mutated")
        return
    if case == "normalized_collision":
        assert normalized_collisions(["Base.LemonGrass", "Base.Lemongrass", "Base.Apple"]) == {
            "base.lemongrass": ("Base.LemonGrass", "Base.Lemongrass")
        }
        return
    if case in {
        "d5_exact_pair_resolved",
        "d5_normalized_authoritative_key_rejected",
        "d5_dispositionless_closure_rejected",
    }:
        raw = normalized_collisions([*TARGETS, "Base.Apple"])
        if case == "d5_dispositionless_closure_rejected":
            assert collision_correction_members(raw, set()) == set(TARGETS)
            return
        correction_members = collision_correction_members(raw, set(TARGETS))
        if case == "d5_exact_pair_resolved":
            metrics = exact_identity_metrics(TARGETS, TARGETS, raw["base.lemongrass"], correction_members)
            assert raw["base.lemongrass"] == TARGETS
            assert correction_members == set()
            assert sum(metrics.values()) == 0
        else:
            metrics = exact_identity_metrics(
                ["base.lemongrass"],
                ["base.lemongrass"],
                raw["base.lemongrass"],
                correction_members,
            )
            assert metrics["case_normalization_merge"] == 1
            assert metrics["normalized_key_overwrite"] == 1
            assert sum(metrics.values()) > 0
        return
    if case == "owner_output_self_comparison":
        assert menu_owner_output_self_comparison_count({
            "Base.A": {"fact_id": "fact:a", "menu_consumer_fact_identity_refs": ["fact:a"]},
            "Base.B": {"fact_id": "fact:b"},
        }) == 1
        assert menu_owner_output_self_comparison_count({"Base.A": {"fact_id": "fact:a"}}) == 0
        return
    if case == "layer2_owner_output":
        root = Path(__file__).resolve().parents[3]
        report = validate_owner_output(root)
        support_count = len(support_universe(root))
        assert report["frozen_support_count"] == support_count
        assert report["resolved_entry_count"] + report["layer2_display_silence_count"] == support_count
        assert report["remaining_entry_count"] == 0
        assert report["consumer_specific_semantic_field_count"] == 0
        return
    if case.startswith("d2_relation_"):
        disposition = case.removeprefix("d2_relation_")
        applicable = disposition != "not_applicable"
        row = {
            "schema_version": "iris-tooltip-t1-d2-layer2-menu-relation-row-v1",
            "full_type": "Base.X",
            "layer2_applicability": "layer2_applicable" if applicable else "layer2_display_silence",
            "disposition": disposition,
            "expected": {"classification_identity": "Tool|Tool.1-A"} if applicable else None,
            "observed": {"memberships": ["Tool.1-A"]},
            "mismatch_kinds": ["navigation_primary"] if disposition == "correction_required" else [],
        }
        assert validate_relation_lifecycle(
            [row],
            {"Base.X"} if applicable else set(),
            set() if applicable else {"Base.X"},
        ) == {disposition: 1}
        return
    if case.startswith("layer2_"):
        root = Path(__file__).resolve().parents[3]
        output = materialize(root)
        if case == "layer2_terminal_relation":
            output["layer2_display_silence_entries"].pop()
            expected = "partition"
        elif case.startswith("layer2_silence_"):
            state, reason = {
                "layer2_silence_fallback": ("fallback_derived", "raw_misc_9a_fallback"),
                "layer2_silence_no_membership": ("no_membership_record", "no_membership_record"),
                "layer2_silence_multi_without_primary": ("unclassified", "multi_membership_without_admissible_primary"),
            }[case]
            row = next(row for row in output["layer2_display_silence_entries"] if row["source_state"] == state)
            assert row["display_silence_reason"] == reason
            assert set(row) == {"full_type", "source_state", "display_silence_reason"}
            assert row["full_type"] not in {resolved["full_type"] for resolved in output["rows"]}
            return
        elif case == "layer2_authority_fallback":
            output["rows"][0]["classification_provenance_ref"] = ""
            expected = "authority/provenance"
        elif case == "layer2_identity_locale":
            output["rows"][0]["primary_subcategory_surface"]["en"] = ""
            expected = "surface value"
        else:
            output["rows"][0]["menu_rank"] = 1
            expected = "consumer-owned"
        candidate = tmp_path / f"{case}.json"
        _write_json(candidate, output)
        with pytest.raises(ValueError, match=expected):
            validate_owner_output(root, candidate)
        return
    if case == "candidate_pre_gate_axis":
        closeout = candidate_closeout_record(T2Progression.UPSTREAM)
        assert closeout["contract_and_audit_axis"] == "partial"
        assert closeout["formal_closeout_state"] == "implemented_only"
        assert "not yet bound" in closeout["validation_ceiling"]
        return
    if case == "recipe_locale_projection":
        root = Path(__file__).resolve().parents[3]
        selected, records = validate_registry(root)
        projection = build_owner_projection(root)
        assert len(selected) == len(records) == projection["entry_count"]
        assert set(projection["entries"]) == set(selected)
        assert projection["selection_stage"] == "post_selected_identity_freeze"
        assert projection["fallback_allowed"] is False
        return
    if case == "nonblocking_correction":
        progression, by_owner = build_progression_record([
            {"owner": "DVF owner", "t2_blocking": True},
            {"owner": "Menu consumer owner", "t2_blocking": False},
        ])
        assert progression["upstream_blocker_count"] == 1
        assert progression["blocking_cause_owners"] == ["DVF owner"]
        assert by_owner == {"DVF owner": 1}
        assert progression["T2_FULL_DATA_PROGRESSION"] == T2Progression.UPSTREAM.value
        return
    if case == "strict_blocked_absence":
        progression, blockers = build_progression_record([
            {"owner": "DVF owner", "reason_code": "DVF_OWNER_ROW_MISSING", "t2_blocking": True}
        ])
        root = tmp_path / "strict-blocked"
        root.mkdir()
        result = _strict_candidate_result(
            root,
            {"commit": "a" * 40, "tree": "b" * 40},
            {"authority_contract_bundle_sha256": "c" * 64},
            {"schema_version": "test-admission"},
            ["Base.X"],
            {"Base.X": tuple(_audited_slots())},
            [{"owner": "DVF owner", "reason_code": "DVF_OWNER_ROW_MISSING", "t2_blocking": True}],
            progression,
            blockers,
            {},
        )
        assert result["production_t2_handoff"] == "absent"
        assert {path.name for path in root.iterdir()} == {"run_receipt.json"}
        return
    if case == "d3_owner_absence_nonblocking":
        root = Path(__file__).resolve().parents[3]
        registry = load_json(root / AUTHORITY_ROOT / "tooltip_readiness_reason_registry.json")
        reasons = {row["code"]: row for row in registry["reasons"]}
        assert reasons["DVF_NO_APPROVED_DESCRIPTION_MATERIAL"] == {
            "code": "DVF_NO_APPROVED_DESCRIPTION_MATERIAL",
            "owner": "DVF owner",
            "layer": "layer3",
            "t2_blocking": False,
            "acceptance": "owner-approved exact FullType absence bound to producer-independent technical/locale/quality/review defect exclusion evidence",
            "re_audit": "when exact DVF facts/decisions, approved role-material, or the adopted role-material mapping identity changes",
        }
        return
    if case in {"gate_failure", "gate_subject_mismatch", "gate_same_subject_success", "strict_handoff_hash_mismatch", "strict_handoff_success"}:
        root = Path(__file__).resolve().parents[3]
        mode = {
            "gate_failure": "gate_failure",
            "gate_subject_mismatch": "subject_mismatch",
            "gate_same_subject_success": "success",
            "strict_handoff_hash_mismatch": "strict_hash_mismatch",
            "strict_handoff_success": "strict_success",
        }[case]
        fixture = _finalization_fixture(tmp_path, root, mode)
        arguments = (
            root,
            fixture["candidate_root"],
            fixture["candidate_sha256"],
            fixture["run_a"],
            fixture["run_b"],
            fixture["comparator"],
            fixture["output"],
        )
        if case not in {"gate_same_subject_success", "strict_handoff_success"}:
            with pytest.raises(TooltipContractError, match="did not exit 0|subject mismatch|hash binding mismatch"):
                finalize_closeout(*arguments)
            assert not Path(fixture["output"]).exists()
        else:
            result = finalize_closeout(*arguments)
            assert result["contract_and_audit_axis"] == "complete"
            assert result["formal_closeout_state"] == "complete"
            assert Path(result["final_closeout_path"]).is_file()
            if case == "strict_handoff_success":
                assert result["production_t2_handoff"] == "present"
                assert {path.name for path in Path(result["final_root"]).iterdir()} == {
                    "subject_binding.json", "t2_handoff_input.jsonl",
                    "t2_handoff_manifest.json", "axis_separated_final_closeout_record.json",
                }
        return
    correction = {
        "owner": "DVF owner",
        "reason_code": "DVF_OWNER_ROW_MISSING",
        "correction_acceptance_condition": "owner correction",
        "re_audit_condition": "new exact subject",
    }
    if case == "unknown_reason":
        correction["reason_code"] = "UNKNOWN"
    elif case == "missing_owner":
        correction["owner"] = ""
    elif case == "missing_acceptance":
        correction["correction_acceptance_condition"] = ""
    else:
        correction["re_audit_condition"] = ""
    metrics = correction_completeness_metrics([correction], {"DVF_OWNER_ROW_MISSING"})
    assert sum(metrics.values()) == 1
