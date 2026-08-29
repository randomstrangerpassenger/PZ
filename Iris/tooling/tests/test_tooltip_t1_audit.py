from __future__ import annotations

from pathlib import Path

import pytest

from iris_tooling.domains.layer4.tooltip_t1_d4 import build_owner_projection, validate_registry
from iris_tooling.domains.tooltip_t1.audit import (
    build_progression_record,
    candidate_closeout_record,
    classify_progression,
    correction_completeness_metrics,
    finalize_closeout,
    menu_owner_output_self_comparison_count,
    normalized_collisions,
    source_mutation_count,
    validate_whole_universe,
)
from iris_tooling.domains.tooltip_t1.contract import canonical_bytes, git_subject, sha256_file
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
        ("owner_output_self_comparison", None),
        ("candidate_pre_gate_axis", None),
        ("recipe_locale_projection", None),
        ("nonblocking_correction", None),
        ("gate_failure", None),
        ("gate_subject_mismatch", None),
        ("gate_same_subject_success", None),
    ],
)
def test_whole_universe_audit_progression(case: str, expected: T2Progression | None, tmp_path: Path) -> None:
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
    if case == "owner_output_self_comparison":
        assert menu_owner_output_self_comparison_count({
            "Base.A": {"fact_id": "fact:a", "menu_consumer_fact_identity_refs": ["fact:a"]},
            "Base.B": {"fact_id": "fact:b"},
        }) == 1
        assert menu_owner_output_self_comparison_count({"Base.A": {"fact_id": "fact:a"}}) == 0
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
    if case in {"gate_failure", "gate_subject_mismatch", "gate_same_subject_success"}:
        root = Path(__file__).resolve().parents[3]
        mode = {
            "gate_failure": "gate_failure",
            "gate_subject_mismatch": "subject_mismatch",
            "gate_same_subject_success": "success",
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
        if case != "gate_same_subject_success":
            with pytest.raises(TooltipContractError, match="did not exit 0|subject mismatch"):
                finalize_closeout(*arguments)
            assert not Path(fixture["output"]).exists()
        else:
            result = finalize_closeout(*arguments)
            assert result["contract_and_audit_axis"] == "complete"
            assert result["formal_closeout_state"] == "complete"
            assert Path(result["final_closeout_path"]).is_file()
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
