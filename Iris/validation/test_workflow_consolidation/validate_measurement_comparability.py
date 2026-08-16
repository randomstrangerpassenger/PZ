from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from ._common import (
        committed_blob_identity,
        ContractError,
        git,
        read_json,
        read_jsonl,
        require,
        sha256_bytes,
        sha256_file,
        subject_identity,
        write_json,
    )
    from .measure_execution_cost import (
        build_qualification_schedule,
        build_schedule,
        canonical_input_hashes,
    )
except ImportError:  # Direct script execution.
    from _common import (
        committed_blob_identity,
        ContractError,
        git,
        read_json,
        read_jsonl,
        require,
        sha256_bytes,
        sha256_file,
        subject_identity,
        write_json,
    )
    from measure_execution_cost import (
        build_qualification_schedule,
        build_schedule,
        canonical_input_hashes,
    )


SCHEMA = "iris_test_workflow_measurement_comparability_v1"
COMMAND_SIGNATURE_FIELDS = {
    "executable",
    "ordered_argv",
    "cwd_role",
    "environment_contract",
    "path_normalization",
    "declared_input_identity",
    "canonical_input_hashes",
    "expected_output_contract",
}


def present_equal(left: object, right: object) -> bool:
    return isinstance(left, dict) and bool(left) and left == right


def touch_surface_frozen_for_base(touch: dict[str, Any], base_commit: str) -> bool:
    return (
        touch.get("frozen_before_protocol_qualification") is True
        and touch.get("base_subject_commit") == base_commit
    )


def touch_surface_identity_bound(
    qualification: dict[str, Any],
    session: dict[str, Any],
    current_identity: dict[str, str],
) -> bool:
    return (
        qualification.get("declared_round_touch_surface_identity") == current_identity
        and session.get("declared_round_touch_surface_identity") == current_identity
    )


def is_ancestor(repository: Path, base_commit: str, terminal_commit: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repository), "merge-base", "--is-ancestor", base_commit, terminal_commit],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode not in (0, 1):
        raise ContractError(result.stderr.decode("utf-8", errors="replace").strip() or "git ancestry check failed")
    return result.returncode == 0


def accepted_receipts_valid(session: dict[str, Any], qualification: dict[str, Any]) -> bool:
    return (
        session.get("status") == "PASS"
        and session.get("receipt_kind") == "terminal-acceptance"
        and session.get("accepted_before_after_sample") is True
        and qualification.get("status") == "PASS"
        and qualification.get("receipt_kind") == "baseline_protocol_qualification"
        and qualification.get("accepted_before_after_sample") is False
    )


def current_protocol_identity(path: Path) -> dict[str, str]:
    repo = Path(git(path.parent, "rev-parse", "--show-toplevel"))
    identity = committed_blob_identity(repo, path)
    return {
        "schema_version": "iris_test_workflow_measurement_contract_v1",
        "canonical_contract_path": identity["canonical_path"],
        "raw_sha256": identity["raw_sha256"],
        "git_blob_id": identity["git_blob_id"],
    }


def changed_paths(base: Path, terminal: Path) -> list[dict[str, str]]:
    base_commit = git(base, "rev-parse", "HEAD")
    terminal_commit = git(terminal, "rev-parse", "HEAD")
    lines = git(terminal, "diff", "--name-status", "--find-renames", base_commit, terminal_commit).splitlines()
    rows: list[dict[str, str]] = []
    for line in lines:
        fields = line.split("\t")
        status = fields[0]
        if status.startswith("R"):
            rows.append({"status": status, "path": fields[2].replace("\\", "/"), "source_path": fields[1].replace("\\", "/")})
        else:
            rows.append({"status": status, "path": fields[-1].replace("\\", "/")})
    return rows


def allowed_path(path: str, touch_surface: dict[str, Any]) -> tuple[bool, str | None]:
    for row in touch_surface.get("entries", []):
        value = str(row.get("path", "")).rstrip("/")
        kind = row.get("kind")
        matched = kind == "exact" and path == value
        matched = matched or (
            kind == "prefix" and (path == value or path.startswith(value + "/"))
        )
        if matched:
            return not bool(row.get("conditional_admission")), str(row.get("role"))
    return False, None


def conditional_admission_for(path: str, touch_surface: dict[str, Any]) -> str | None:
    for row in touch_surface.get("entries", []):
        value = str(row.get("path", "")).rstrip("/")
        kind = row.get("kind")
        if kind == "exact" and path == value or kind == "prefix" and (
            path == value or path.startswith(value + "/")
        ):
            value = row.get("conditional_admission")
            return str(value) if value else None
    return None


def classify_changed_rows(
    rows: list[dict[str, str]], touch_surface: dict[str, Any]
) -> list[dict[str, Any]]:
    classified: list[dict[str, Any]] = []
    for row in rows:
        allowed, role = allowed_path(row["path"], touch_surface)
        source_allowed = True
        source_role = None
        if row.get("source_path"):
            source_allowed, source_role = allowed_path(
                row["source_path"], touch_surface
            )
        classified.append(
            {
                **row,
                "allowed": allowed and source_allowed,
                "role": role,
                "source_allowed": source_allowed,
                "source_role": source_role,
                "conditional_admission": conditional_admission_for(row["path"], touch_surface),
                "source_conditional_admission": conditional_admission_for(row["source_path"], touch_surface)
                if row.get("source_path")
                else None,
            }
        )
    return classified


def _signature_matches_workload(
    signature: object,
    workload: dict[str, Any],
    interpreter: dict[str, Any],
    live_input_hashes: dict[str, str],
) -> bool:
    return (
        isinstance(signature, dict)
        and set(signature) == COMMAND_SIGNATURE_FIELDS
        and signature.get("executable") == interpreter.get("executable")
        and signature.get("ordered_argv") == workload.get("command", [])[1:]
        and signature.get("cwd_role") == "target_repository_root"
        and signature.get("environment_contract")
        == workload.get("environment_contract")
        and signature.get("path_normalization")
        == "repository_and_result_roots_are_role_descriptors"
        and signature.get("declared_input_identity") == workload.get("input_identity")
        and signature.get("canonical_input_hashes") == live_input_hashes
        and signature.get("expected_output_contract")
        == workload.get("expected_output_contract")
    )


def _command_contracts_by_workload(
    receipt: dict[str, Any],
    workloads: dict[str, dict[str, Any]],
    repositories: dict[str, Path],
    interpreter: dict[str, Any],
) -> dict[str, dict[str, set[str]]] | None:
    by_workload: dict[str, dict[str, set[str]]] = {}
    live_hashes = {
        (arm, workload_id): canonical_input_hashes(repositories[arm], workload)
        for arm in ("A", "B")
        for workload_id, workload in workloads.items()
    }
    for row in receipt.get("samples", []):
        if not isinstance(row, dict):
            return None
        workload_id = row.get("workload_id")
        arm = row.get("arm")
        observation = row.get("observation")
        if (
            not isinstance(workload_id, str)
            or not workload_id
            or arm not in {"A", "B"}
            or workload_id not in workloads
            or not isinstance(observation, dict)
            or not _signature_matches_workload(
                observation.get("command_signature"),
                workloads[workload_id],
                interpreter,
                live_hashes[(arm, workload_id)],
            )
        ):
            return None
        signature = json.dumps(observation["command_signature"], sort_keys=True)
        by_workload.setdefault(workload_id, {"A": set(), "B": set()})[arm].add(signature)
    if not by_workload or not all(
        value["A"] == value["B"] and len(value["A"]) == 1
        for value in by_workload.values()
    ):
        return None
    return by_workload


def command_contract_equal(
    session: dict[str, Any],
    qualification: dict[str, Any],
    contract: dict[str, Any],
    accepted_schedule: dict[str, Any],
    base_repository: Path,
    terminal_repository: Path,
) -> bool:
    qualification_ids = contract.get("qualification_workload_ids")
    contract_workloads = {
        row["workload_id"]: row for row in contract.get("workloads", [])
    }
    qualification_workloads = {
        workload_id: contract_workloads[workload_id]
        for workload_id in qualification_ids
        if workload_id in contract_workloads
    } if isinstance(qualification_ids, list) else {}
    accepted_workloads = {
        row["workload_id"]: row for row in accepted_schedule.get("workloads", [])
        if isinstance(row, dict) and isinstance(row.get("workload_id"), str)
    }
    qualified = _command_contracts_by_workload(
        qualification,
        qualification_workloads,
        {"A": base_repository, "B": base_repository},
        qualification.get("target_execution_interpreter_identity_a", {}),
    )
    accepted = _command_contracts_by_workload(
        session,
        accepted_workloads,
        {"A": base_repository, "B": terminal_repository},
        session.get("target_execution_interpreter_identity_a", {}),
    )
    return (
        qualified is not None
        and accepted is not None
        and set(qualified) == set(qualification_workloads)
        and set(qualified) <= set(accepted)
        and all(
            qualified[workload_id]["A"]
            == qualified[workload_id]["B"]
            == accepted[workload_id]["A"]
            == accepted[workload_id]["B"]
            for workload_id in qualified
        )
    )


def qualification_schedule_valid(
    qualification: dict[str, Any], contract: dict[str, Any]
) -> bool:
    expected = build_qualification_schedule(contract)
    expected_projection = [
        {
            "workload_id": row["workload_id"],
            "phase": row["phase"],
            "block": row["block"],
            "position": row["position"],
            "arm": row["arm"],
        }
        for row in expected["positions"]
    ]
    received_projection = [
        {
            "workload_id": row.get("workload_id"),
            "phase": row.get("phase"),
            "block": row.get("block"),
            "position": row.get("position"),
            "arm": row.get("arm"),
        }
        for row in qualification.get("samples", [])
        if isinstance(row, dict)
    ]
    expected_ids = [row["workload_id"] for row in expected["workloads"]]
    summaries = qualification.get("workload_summaries")
    return (
        len(received_projection) == len(qualification.get("samples", []))
        and received_projection == expected_projection
        and isinstance(summaries, list)
        and sorted(row.get("workload_id") for row in summaries if isinstance(row, dict))
        == sorted(expected_ids)
        and len(summaries) == len(expected_ids)
    )


def target_execution_interpreter_identity_equal(
    qualification: dict[str, Any], session: dict[str, Any]
) -> bool:
    identities = [
        qualification.get("target_execution_interpreter_identity_a"),
        qualification.get("target_execution_interpreter_identity_b"),
        session.get("target_execution_interpreter_identity_a"),
        session.get("target_execution_interpreter_identity_b"),
    ]
    return all(isinstance(value, dict) and bool(value) for value in identities) and all(
        value == identities[0] for value in identities[1:]
    )


def accepted_schedule_valid(
    session: dict[str, Any],
    schedule_path: Path,
    family_ledger_path: Path,
    contract: dict[str, Any],
) -> bool:
    schedule = read_json(schedule_path)
    family_rows = read_jsonl(family_ledger_path)
    expected = build_schedule(contract, family_rows, "terminal-acceptance")
    compared_keys = (
        "session_kind",
        "adopted_nonpilot_family_ids",
        "n_adopted_nonpilot",
        "workloads",
        "positions",
        "measured_block_count",
        "total_execution_positions",
        "statistics",
    )
    projection = {
        "session_kind": schedule.get("session_kind"),
        "adopted_nonpilot_family_ids": schedule.get("adopted_nonpilot_family_ids", []),
        "n_adopted_nonpilot": schedule.get("n_adopted_nonpilot", 0),
        "total_execution_positions": schedule.get("total_execution_positions"),
        "measured_block_count": schedule.get("measured_block_count"),
    }
    sample_projection = [
        {
            "workload_id": row.get("workload_id"),
            "phase": row.get("phase"),
            "block": row.get("block"),
            "position": row.get("position"),
            "arm": row.get("arm"),
        }
        for row in session.get("samples", [])
    ]
    position_projection = [
        {
            "workload_id": row.get("workload_id"),
            "phase": row.get("phase"),
            "block": row.get("block"),
            "position": row.get("position"),
            "arm": row.get("arm"),
        }
        for row in schedule.get("positions", [])
    ]
    return (
        session.get("schedule_sha256") == sha256_file(schedule_path)
        and schedule.get("family_ledger_sha256") == sha256_file(family_ledger_path)
        and all(schedule.get(key) == expected.get(key) for key in compared_keys)
        and session.get("schedule_projection") == projection
        and sample_projection == position_projection
    )


def contract_map_valid(path: Path) -> bool:
    rows = read_jsonl(path)
    if not rows or rows[0].get("record_type") != "manifest":
        return False
    manifest = rows[0]
    mappings = rows[1:]
    predecessor_ids = sorted(str(row.get("predecessor_test_id", "")) for row in mappings)
    encoded = ("\n".join(predecessor_ids) + "\n").encode("utf-8")
    complete = (
        manifest.get("expected_predecessor_count") == len(mappings)
        and manifest.get("predecessor_id_sha256") == sha256_bytes(encoded)
        and len(predecessor_ids) == len(set(predecessor_ids))
        and all(predecessor_ids)
    )
    return complete and all(
        row.get("mapping_status") == "preserved"
        and row.get("predecessor_test_id")
        and row.get("successor_probe_ids")
        and row.get("failure_localization_preserved") is True
        for row in mappings
    )


def validate(args: argparse.Namespace) -> dict[str, Any]:
    base = args.base_repository.resolve()
    terminal = args.terminal_repository.resolve()
    base_subject = subject_identity(base)
    terminal_subject = subject_identity(terminal)
    session = read_json(args.accepted_session)
    qualification = read_json(args.protocol_qualification_receipt)
    contract = read_json(args.measurement_contract)
    tooling = read_json(args.tooling_manifest)
    accepted_schedule = read_json(args.accepted_schedule)
    touch = read_json(args.touch_surface)
    tool_repo = Path(git(args.tooling_manifest.parent, "rev-parse", "--show-toplevel"))
    touch_identity = committed_blob_identity(tool_repo, args.touch_surface)
    rows = changed_paths(base, terminal)
    classified = classify_changed_rows(rows, touch)
    out_of_scope = [row for row in classified if not row["allowed"]]
    protocol = session.get("measurement_protocol_identity")
    supplied_protocol = current_protocol_identity(args.measurement_contract)
    manifest_identity = committed_blob_identity(tool_repo, args.tooling_manifest)
    expected_tool_subject = subject_identity(tool_repo)
    received_tooling_identity = session.get("measurement_tooling_identity", {})
    current_tooling_identity_matches = (
        received_tooling_identity.get("manifest_raw_sha256")
        == manifest_identity["raw_sha256"]
        and received_tooling_identity.get("tool_subject") == expected_tool_subject
    )
    checks = {
        "base_is_ancestor_of_terminal": is_ancestor(terminal, base_subject["commit"], terminal_subject["commit"]),
        "accepted_and_qualification_receipts_valid": accepted_receipts_valid(session, qualification),
        "protocol_qualification_schedule_matches_frozen_contract": qualification_schedule_valid(
            qualification, contract
        ),
        "protocol_qualification_subject_matches_base": qualification.get("target_subject_a") == base_subject and qualification.get("target_subject_b") == base_subject,
        "measurement_tooling_identity_equal": qualification.get("measurement_tooling_identity") == received_tooling_identity and bool(received_tooling_identity) and current_tooling_identity_matches,
        "measurement_contract_identity_equal_across_qualification_and_accepted_session": qualification.get("measurement_protocol_identity") == protocol and protocol == supplied_protocol,
        "machine_environment_locale_equal": present_equal(qualification.get("environment_identity"), session.get("environment_identity")),
        "accepted_paired_session_single_session": bool(session.get("session_id")) and session.get("cross_session_sample_count") == 0,
        "harness_interpreter_identity_equal": present_equal(qualification.get("harness_interpreter_identity"), session.get("harness_interpreter_identity")),
        "target_execution_interpreter_identity_equal": target_execution_interpreter_identity_equal(
            qualification, session
        ),
        "command_and_input_contract_equal": command_contract_equal(
            session,
            qualification,
            contract,
            accepted_schedule,
            base,
            terminal,
        ),
        "contract_denominator_equivalent_via_preservation_map": contract_map_valid(args.contract_map),
        "accepted_session_schedule_matches_parameterized_contract_and_final_family_ledger": accepted_schedule_valid(session, args.accepted_schedule, args.family_ledger, contract),
        "declared_round_touch_surface_frozen_before_protocol_qualification": touch_surface_frozen_for_base(touch, base_subject["commit"]),
        "declared_round_touch_surface_identity_bound": touch_surface_identity_bound(
            qualification, session, touch_identity
        ),
        "S_base_to_S_terminal_changed_paths_subset_of_declared_touch_surface": not out_of_scope,
        "out_of_scope_path_count_zero": not out_of_scope,
        "accepted_subjects_match": session.get("target_subject_a") == base_subject and session.get("target_subject_b") == terminal_subject,
        "measurement_contract_schema_match": contract.get("schema_version") == "iris_test_workflow_measurement_contract_v1",
        "tooling_manifest_schema_match": tooling.get("schema_version") == "iris_test_workflow_measurement_tooling_manifest_v1",
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    return {
        "schema_version": SCHEMA,
        "status": status,
        "comparability_verdict": status,
        "base_subject": base_subject,
        "terminal_subject": terminal_subject,
        "accepted_session_id": session.get("session_id"),
        "measurement_protocol_identity": protocol,
        "measurement_contract_sha256": supplied_protocol["raw_sha256"],
        "tooling_manifest_sha256": manifest_identity["raw_sha256"],
        "checks": checks,
        "changed_paths": classified,
        "out_of_scope_path_count": len(out_of_scope),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate before/terminal measurement comparability")
    parser.add_argument("--base-repository", type=Path, required=True)
    parser.add_argument("--terminal-repository", type=Path, required=True)
    parser.add_argument("--accepted-session", type=Path, required=True)
    parser.add_argument("--accepted-schedule", type=Path, required=True)
    parser.add_argument("--family-ledger", type=Path, required=True)
    parser.add_argument("--protocol-qualification-receipt", type=Path, required=True)
    parser.add_argument("--measurement-contract", type=Path, required=True)
    parser.add_argument("--tooling-manifest", type=Path, required=True)
    parser.add_argument("--touch-surface", type=Path, required=True)
    parser.add_argument("--contract-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args)
    write_json(args.output, report)
    require(report["status"] == "PASS", "measurement subjects are not comparable")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
