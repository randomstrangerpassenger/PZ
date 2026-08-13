from __future__ import annotations

from pathlib import Path

from Iris.validation.test_workflow_consolidation._common import sha256_bytes, sha256_file, write_json, write_jsonl
from Iris.validation.test_workflow_consolidation.validate_measurement_comparability import (
    accepted_schedule_valid,
    accepted_receipts_valid,
    allowed_path,
    classify_changed_rows,
    command_contract_equal,
    contract_map_valid,
    present_equal,
    target_execution_interpreter_identity_equal,
    touch_surface_identity_bound,
    touch_surface_frozen_for_base,
)


def test_identity_equality_requires_nonempty_mapping() -> None:
    assert present_equal(None, None) is False
    assert present_equal({}, {}) is False
    assert present_equal({"python": "3.13"}, {"python": "3.13"}) is True


def _receipt_with_command(executable: str = "python", input_id: str = "tree") -> dict[str, object]:
    signature = {
        "executable_identity": executable,
        "ordered_argv": ["-m", "pytest"],
        "cwd_contract": "target_repository",
        "environment_contract": {},
        "declared_input_identity": input_id,
    }
    return {
        "samples": [
            {
                "workload_id": "mandatory_pilot",
                "arm": arm,
                "observation": {"command_signature": signature},
            }
            for arm in ("A", "B")
        ]
    }


def test_command_and_input_contract_is_bound_to_qualification() -> None:
    qualification = _receipt_with_command()
    session = _receipt_with_command()
    assert command_contract_equal(session, qualification)
    qualification = _receipt_with_command(input_id="stale-tree")
    assert not command_contract_equal(session, qualification)


def test_target_interpreter_identity_is_bound_across_qualification_and_session() -> None:
    identity = {"executable": "python", "version": "3.13"}
    qualification = {
        "target_execution_interpreter_identity_a": identity,
        "target_execution_interpreter_identity_b": identity,
    }
    session = {
        "target_execution_interpreter_identity_a": identity,
        "target_execution_interpreter_identity_b": identity,
    }
    assert target_execution_interpreter_identity_equal(qualification, session)
    qualification["target_execution_interpreter_identity_b"] = {
        "executable": "python-other",
        "version": "3.13",
    }
    assert not target_execution_interpreter_identity_equal(qualification, session)


def test_touch_surface_identity_requires_qualification_and_session_binding() -> None:
    identity = {"canonical_path": "touch.json", "git_blob_id": "abc", "raw_sha256": "def"}
    qualification = {"declared_round_touch_surface_identity": identity}
    session = {"declared_round_touch_surface_identity": identity}
    assert touch_surface_identity_bound(qualification, session, identity) is True
    assert touch_surface_identity_bound(qualification, {}, identity) is False


def _schedule_contract() -> dict[str, object]:
    workload = {"workload_id": "mandatory_pilot", "command": ["python", "-c", "pass"]}
    configured = {
        "workload_id": "configured-current",
        "role": "configured_route_performance_observation",
        "command": ["python", "-c", "pass"],
    }
    return {
        "workloads": [workload, configured],
        "schedule": {"targeted_measured_blocks": 5, "configured_measured_blocks": 10},
        "statistics": {"bootstrap_seed": 1729},
    }


def test_schedule_validation_binds_hash_ledger_projection_and_samples(tmp_path: Path) -> None:
    from Iris.validation.test_workflow_consolidation.measure_execution_cost import build_schedule

    ledger = tmp_path / "ledger.jsonl"
    write_jsonl(ledger, [])
    schedule = build_schedule(_schedule_contract(), [], "terminal-acceptance")
    schedule["family_ledger_sha256"] = sha256_file(ledger)
    schedule_path = tmp_path / "schedule.json"
    write_json(schedule_path, schedule)
    projection = {
        "session_kind": schedule["session_kind"],
        "adopted_nonpilot_family_ids": [],
        "n_adopted_nonpilot": 0,
        "total_execution_positions": schedule["total_execution_positions"],
        "measured_block_count": schedule["measured_block_count"],
    }
    session = {
        "schedule_sha256": sha256_file(schedule_path),
        "schedule_projection": projection,
        "samples": schedule["positions"],
    }
    assert accepted_schedule_valid(session, schedule_path, ledger, _schedule_contract())
    session["schedule_projection"] = {**projection, "measured_block_count": 999}
    assert not accepted_schedule_valid(session, schedule_path, ledger, _schedule_contract())


def test_comparability_rejects_failed_or_nonaccepted_receipts() -> None:
    qualification = {
        "status": "PASS",
        "receipt_kind": "baseline_protocol_qualification",
        "accepted_before_after_sample": False,
    }
    session = {
        "status": "FAIL",
        "receipt_kind": "terminal-acceptance",
        "accepted_before_after_sample": True,
    }
    assert accepted_receipts_valid(session, qualification) is False
    session["status"] = "PASS"
    assert accepted_receipts_valid(session, qualification) is True


def test_touch_surface_base_binding_is_explicit() -> None:
    surface = {"frozen_before_protocol_qualification": True, "base_subject_commit": "base-a"}
    assert touch_surface_frozen_for_base(surface, "base-a") is True
    assert touch_surface_frozen_for_base(surface, "base-b") is False


def test_touch_surface_is_fail_closed() -> None:
    surface = {
        "entries": [
            {"kind": "exact", "path": "docs/plan.md", "role": "plan_infrastructure"},
            {"kind": "prefix", "path": "Iris/validation/successor", "role": "application"},
        ]
    }
    assert allowed_path("docs/plan.md", surface) == (True, "plan_infrastructure")
    assert allowed_path("Iris/validation/successor/tool.py", surface) == (True, "application")
    assert allowed_path("Iris/media/lua/client/Iris/IrisMain.lua", surface) == (False, None)
    rename = classify_changed_rows(
        [
            {
                "status": "R100",
                "source_path": "Iris/media/lua/client/Iris/IrisMain.lua",
                "path": "Iris/validation/successor/IrisMain.lua",
            }
        ],
        surface,
    )
    assert rename[0]["allowed"] is False


def test_touch_surface_condition_is_not_unconditionally_admitted() -> None:
    surface = {
        "entries": [
            {
                "kind": "prefix",
                "path": "Iris/_docs/round3",
                "role": "authority_transaction",
                "conditional_admission": "identity migration only",
            }
        ]
    }
    assert allowed_path("Iris/_docs/round3/taxonomy.json", surface) == (
        False,
        "authority_transaction",
    )
    rows = classify_changed_rows(
        [{"status": "M", "path": "Iris/_docs/round3/taxonomy.json"}], surface
    )
    assert rows[0]["conditional_admission"] == "identity migration only"


def test_contract_map_requires_localization_and_successor_probe(tmp_path: Path) -> None:
    path = tmp_path / "mapping.jsonl"
    write_jsonl(
        path,
        [
            {
                "record_type": "manifest",
                "expected_predecessor_count": 1,
                "predecessor_id_sha256": sha256_bytes(b"old.test\n"),
            },
            {
                "record_type": "mapping",
                "predecessor_test_id": "old.test",
                "successor_probe_ids": ["probe"],
                "mapping_status": "preserved",
                "failure_localization_preserved": True,
            }
        ],
    )
    assert contract_map_valid(path)
    write_jsonl(
        path,
        [
            {
                "record_type": "manifest",
                "expected_predecessor_count": 1,
                "predecessor_id_sha256": sha256_bytes(b"old.test\n"),
            },
            {
                "record_type": "mapping",
                "predecessor_test_id": "old.test",
                "successor_probe_ids": [],
                "mapping_status": "preserved",
                "failure_localization_preserved": True,
            }
        ],
    )
    assert not contract_map_valid(path)


def test_contract_map_rejects_incomplete_denominator_manifest(tmp_path: Path) -> None:
    path = tmp_path / "mapping.jsonl"
    write_jsonl(
        path,
        [
            {
                "record_type": "manifest",
                "expected_predecessor_count": 2,
                "predecessor_id_sha256": sha256_bytes(b"old.test\nother.test\n"),
            },
            {
                "record_type": "mapping",
                "predecessor_test_id": "old.test",
                "successor_probe_ids": ["probe"],
                "mapping_status": "preserved",
                "failure_localization_preserved": True,
            },
        ],
    )
    assert not contract_map_valid(path)
