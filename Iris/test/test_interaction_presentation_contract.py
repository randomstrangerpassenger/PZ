from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = (
    REPOSITORY_ROOT
    / "Iris"
    / "build"
    / "description"
    / "v2"
    / "tools"
    / "build"
    / "validate_interaction_presentation_contract.py"
)


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_interaction_presentation_contract", VALIDATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


@pytest.fixture(scope="session")
def diagnostic_thresholds() -> dict:
    # Gate 3 does not authorize presentation policy. These parameters exercise
    # schema diagnostics only and are explicitly non-authoritative in the report.
    return {"small_max": 8, "dense_min": 9}


@pytest.fixture(scope="session")
def report(diagnostic_thresholds: dict) -> dict:
    return validator.write_contract_artifacts(**diagnostic_thresholds)


def test_current_census_is_contract_clean_and_gate3_is_unblocked(report: dict) -> None:
    assert report["execution_status"] == "PASS"
    assert report["contract_errors"] == []
    assert report["gate3"]["status"] == "PASS"
    assert report["gate3"]["capability_only_count"] == 0
    assert report["gate3"]["recipe_only_count"] == 0
    assert report["closeout_state_ceiling"] == "gate3_pass_owner_approval_required"


def test_density_parameters_are_non_authoritative_until_owner_policy_seal(
    report: dict, diagnostic_thresholds: dict
) -> None:
    assert report["threshold_binding"]["small_max"] == diagnostic_thresholds["small_max"]
    assert report["threshold_binding"]["dense_min"] == diagnostic_thresholds["dense_min"]
    assert report["threshold_binding"]["proposal_not_sealed"] is True
    assert report["threshold_binding"]["validator_or_test_literal_is_authority"] is False
    assert report["threshold_binding"]["owner_policy_status"] == "unapproved"
    assert report["policy_authorization"] == {
        "status": "unapproved",
        "required_ratifications": [f"L4-RAT-{number:02d}" for number in range(1, 8)],
        "rat08": "not_applicable_no_recipe_only",
        "qg_only_publication_status": "owner_approval_required",
        "qg_only_count": 3,
        "existing_owner_seal_eligible": False,
    }
    assert report["density_and_schema"]["exact_small_boundary_fulltypes"]
    assert report["density_and_schema"]["exact_dense_boundary_fulltypes"]


def test_qg_schema_and_runtime_projection_are_exact(report: dict) -> None:
    schema = report["density_and_schema"]
    assert schema["duplicate_identity_count"] == 0
    assert schema["missing_identity_count"] == 0
    assert schema["unknown_surface_count"] == 0
    assert schema["surface_both_count"] == 0
    assert schema["source_surface_mismatch_count"] == 0
    runtime = report["runtime_projection_parity"]
    assert runtime["source_entry_count"] == runtime["runtime_chunk_entry_count"]
    assert runtime["source_entry_count"] == runtime["line_count_index_entry_count"]
    assert runtime["identity_order_mismatch_count"] == 0
    assert runtime["line_count_mismatch_count"] == 0


def test_capability_correction_removes_false_legacy_rows_and_preserves_qg_only(report: dict) -> None:
    crosswalk = report["capability_crosswalk"]
    assert crosswalk["legacy_tuple_count"] == 83
    assert crosswalk["qg_context_tuple_count"] == 86
    assert crosswalk["count_equality_is_not_identity_parity"] is False
    assert crosswalk["capability_only_count"] == 0
    assert {
        (entry["fulltype"], entry["use_case_id"])
        for entry in crosswalk["qg_only"]
    } == {
        ("Base.BallPeenHammer", "uc.action.construction"),
        ("Base.GardenSaw", "uc.action.wood_cutting"),
        ("Base.HammerStone", "uc.action.construction"),
    }
    assert crosswalk["unknown_capability_count"] == 0

    capabilities = json.loads(validator.CAPABILITIES_PATH.read_text(encoding="utf-8"))
    for fulltype in ("Base.UnusableMetal", "Base.UnusableWood", "Base.WeldingMask"):
        assert "can_scrap_moveables" not in capabilities.get(fulltype, [])


def test_recipe_crosswalk_taxonomy_is_exhaustive_disjoint_and_structured(report: dict) -> None:
    crosswalk = report["recipe_crosswalk"]
    assert crosswalk["category_union_matches_recipe_only"] is True
    assert crosswalk["category_pairwise_disjoint"] is True
    assert all(value == 0 for value in crosswalk["category_pairwise_intersection_counts"].values())
    assert crosswalk["planning_snapshot_drift"]["fresh_recipe_only_matches_planning"] is False
    assert crosswalk["recipe_only"] == []
    assert crosswalk["mapped_recipe_intersection_count"] == 794
    assert crosswalk["qg_recipe_only_count"] == 0
    assert crosswalk["runtime_stable_id_plumbing"]["common_prerequisite_not_taxonomy_bucket"] is True
    assert crosswalk["runtime_stable_id_plumbing"]["required"] is True


def test_rat08_is_not_applicable_and_no_old_seal_is_consumed(
    report: dict,
) -> None:
    assert report["rat08_dispositions"] == []
    assert report["rat08_status"] == "not_applicable_no_recipe_only"
    assert report["execution_subject"]["runtime_fact_correction_approval"] == {
        "status": "explicitly_approved",
        "source": "user_instruction_2026-08-21",
        "artifact": "Iris/media/lua/client/Iris/Data/IrisCapabilities.lua",
        "scope": "remove_three_false_can_scrap_moveables_facts",
        "not_adaptive_policy_approval": True,
    }
    assert report["gate3"]["owner_disposition_does_not_override_raw_gate"] is True
    assert report["gate3"]["status"] == "PASS"


def test_keep_only_remove_battery_recipe_is_positive_qg_evidence(report: dict) -> None:
    decisions = json.loads(validator.RECIPE_DECISIONS_PATH.read_text(encoding="utf-8"))
    rule = decisions["rules"]["rp.recipe.remove_battery"]
    assert rule["decision"] == "PASS"
    assert rule["matched_fulltypes"] == []
    assert rule["matched_keep_fulltypes"] == [
        "Base.HandTorch",
        "Base.Rubberducky2",
        "Base.Torch",
    ]
    assert all(entry["decision"] != "NO" for entry in decisions["rules"].values())
    assert {
        (entry["legacy"]["fulltype"], entry["legacy"]["recipe_id"])
        for entry in report["recipe_crosswalk"]["mapped_recipe_intersection"]
        if entry["legacy"]["recipe_id"] == "remove_battery"
    } == {
        ("Base.HandTorch", "remove_battery"),
        ("Base.Rubberducky2", "remove_battery"),
        ("Base.Torch", "remove_battery"),
    }


def test_recipe_classifier_precedence_is_structural() -> None:
    missing_id = {
        "fulltype": "Base.Example",
        "recipe_id": "example",
        "producer_recipe_id_present": False,
    }
    assert validator.classify_recipe_only(
        missing_id, recipe_rows_by_fulltype={}, rules_by_recipe_id={}
    ) == ("identity_unavailable", "producer_recipe_id_missing")

    decided_no = {
        "fulltype": "Base.Example",
        "recipe_id": "example",
        "producer_recipe_id_present": True,
    }
    assert validator.classify_recipe_only(
        decided_no,
        recipe_rows_by_fulltype={},
        rules_by_recipe_id={
            "example": [
                (
                    "rp.recipe.example",
                    {
                        "recipe_id": "example",
                        "decision": "NO",
                        "matched_fulltypes": ["Base.Example"],
                    },
                )
            ]
        },
    ) == ("qg_decided_no", "decision_no:rp.recipe.example")

    assert validator.classify_recipe_only(
        {**decided_no, "recipe_id": "absent"},
        recipe_rows_by_fulltype={},
        rules_by_recipe_id={},
    ) == ("qg_absent", "no_rule")


def test_current_anchor_counts_follow_source_not_roadmap_literals(report: dict) -> None:
    counts = validator.parse_line_count_index()
    source = json.loads(validator.UPSTREAM_PATH.read_text(encoding="utf-8"))["fulltypes"]
    for fulltype in ("Base.223BulletsMold", "Base.Tongs"):
        assert counts[fulltype] == len(validator.positive_rows(source[fulltype]))


def test_source_correction_scope_report_does_not_hide_unrelated_changes(
    report: dict,
) -> None:
    manifest = json.loads(validator.NO_MUTATION_PATH.read_text(encoding="utf-8"))
    assert manifest["contract_report_payload_sha256"] == report["report_payload_sha256"]
    assert manifest["policy_dependent_current_mutation_count"] == 0
    assert manifest["protected_changed_paths"] == []
    assert manifest["assertion"] == "PASS"
    assert manifest["unrelated_or_permitted_changes_are_not_hidden"] is True


def test_gate3_source_migration_path_stops_before_adaptive_implementation(report: dict) -> None:
    selection = json.loads(validator.PATH_SELECTION_PATH.read_text(encoding="utf-8"))
    assert selection["gate3_status"] == "PASS"
    assert selection["selected_execution_path"] == "gate3_source_migration_unblocked"
    assert selection["owner_policy_seal_status"] == "unapproved_new_seal_required"
    assert selection["rat08_binding_status"] == "not_applicable_no_recipe_only"
    assert selection["change2_and_later_policy_dependent_current_implementation"] == "blocked_pending_owner_policy_seal"
    assert selection["required_validation"] == ["V1", "V4"]
    assert selection["mixed_qg_legacy_recipe_projection"] == "forbidden"
    assert set(selection["not_applicable"]) == {"V2", "V3", "V5", "V6", "V7"}


def test_off_live_stable_id_candidate_is_not_an_installation(report: dict) -> None:
    candidate = json.loads(validator.STABLE_ID_CANDIDATE_PATH.read_text(encoding="utf-8"))
    assert candidate["contract_report_payload_sha256"] == report["report_payload_sha256"]
    assert candidate["status"] == "isolated_off_live_candidate_only"
    assert candidate["current_installation"] is False
    assert candidate["unmapped_recipe_only"] == []


def test_report_replay_is_deterministic(report: dict, diagnostic_thresholds: dict) -> None:
    replay, selection, no_mutation, candidate = validator.build_contract_report(**diagnostic_thresholds)
    assert validator.canonical_json_bytes(replay) == validator.canonical_json_bytes(report)
    assert selection["contract_report_payload_sha256"] == report["report_payload_sha256"]
    assert no_mutation["contract_report_payload_sha256"] == report["report_payload_sha256"]
    assert candidate["contract_report_payload_sha256"] == report["report_payload_sha256"]
