from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from ._common import (
        ContractError,
        git,
        read_json,
        read_jsonl,
        require,
        sha256_file,
        subject_identity,
        write_json,
    )
except ImportError:  # Direct script execution.
    from _common import (
        ContractError,
        git,
        read_json,
        read_jsonl,
        require,
        sha256_file,
        subject_identity,
        write_json,
    )


SCHEMA = "iris_test_workflow_measurement_comparability_v1"


def changed_paths(base: Path, terminal: Path) -> list[dict[str, str]]:
    base_commit = git(base, "rev-parse", "HEAD")
    terminal_commit = git(terminal, "rev-parse", "HEAD")
    lines = git(base, "diff", "--name-status", "--find-renames", base_commit, terminal_commit).splitlines()
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
        if kind == "exact" and path == value:
            return True, str(row.get("role"))
        if kind == "prefix" and (path == value or path.startswith(value + "/")):
            return True, str(row.get("role"))
    return False, None


def command_contract_equal(session: dict[str, Any]) -> bool:
    by_workload: dict[str, dict[str, set[str]]] = {}
    for row in session.get("samples", []):
        signature = json.dumps(row["observation"]["command_signature"], sort_keys=True)
        by_workload.setdefault(row["workload_id"], {"A": set(), "B": set()})[row["arm"]].add(signature)
    return bool(by_workload) and all(value["A"] == value["B"] and len(value["A"]) == 1 for value in by_workload.values())


def contract_map_valid(path: Path) -> bool:
    rows = read_jsonl(path)
    return bool(rows) and all(
        row.get("mapping_status") == "preserved"
        and row.get("predecessor_test_id")
        and row.get("successor_probe_ids")
        and row.get("failure_localization_preserved") is True
        for row in rows
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
    touch = read_json(args.touch_surface)
    rows = changed_paths(base, terminal)
    classified: list[dict[str, Any]] = []
    for row in rows:
        allowed, role = allowed_path(row["path"], touch)
        classified.append({**row, "allowed": allowed, "role": role})
    out_of_scope = [row for row in classified if not row["allowed"]]
    protocol = session.get("measurement_protocol_identity")
    checks = {
        "base_is_ancestor_of_terminal": git(base, "merge-base", "--is-ancestor", base_subject["commit"], terminal_subject["commit"]) == "",
        "measurement_tooling_identity_equal": qualification.get("harness_interpreter_identity") == session.get("harness_interpreter_identity"),
        "measurement_contract_identity_equal_across_qualification_and_accepted_session": qualification.get("measurement_protocol_identity") == protocol,
        "machine_environment_locale_equal": qualification.get("environment_identity") == session.get("environment_identity"),
        "accepted_paired_session_single_session": bool(session.get("session_id")) and session.get("cross_session_sample_count") == 0,
        "harness_interpreter_identity_equal": qualification.get("harness_interpreter_identity") == session.get("harness_interpreter_identity"),
        "target_execution_interpreter_identity_equal": session.get("target_execution_interpreter_identity_a") == session.get("target_execution_interpreter_identity_b"),
        "command_and_input_contract_equal": command_contract_equal(session),
        "contract_denominator_equivalent_via_preservation_map": contract_map_valid(args.contract_map),
        "accepted_session_schedule_matches_parameterized_contract_and_final_family_ledger": session.get("schedule_projection", {}).get("total_execution_positions") == 24 * session.get("schedule_projection", {}).get("n_adopted_nonpilot", 0) + 68,
        "declared_round_touch_surface_frozen_before_protocol_qualification": touch.get("frozen_before_protocol_qualification") is True,
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
        "measurement_contract_sha256": sha256_file(args.measurement_contract),
        "tooling_manifest_sha256": sha256_file(args.tooling_manifest),
        "checks": checks,
        "changed_paths": classified,
        "out_of_scope_path_count": len(out_of_scope),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate before/terminal measurement comparability")
    parser.add_argument("--base-repository", type=Path, required=True)
    parser.add_argument("--terminal-repository", type=Path, required=True)
    parser.add_argument("--accepted-session", type=Path, required=True)
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
