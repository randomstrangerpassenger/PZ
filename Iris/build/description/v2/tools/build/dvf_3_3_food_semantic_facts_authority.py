from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Callable

V2_ROOT = Path(__file__).resolve().parents[2]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.candidate_writer import (
    run_phase10,
    run_phase11,
)
from tools.build.dvf_3_3_food_semantic.census_rules import (
    run_phase0,
    run_phase1,
    run_phase2,
)
from tools.build.dvf_3_3_food_semantic.closeout import run_phase13
from tools.build.dvf_3_3_food_semantic.contracts import (
    ATTEMPT_ROOT_FRAGMENT,
    FoodSemanticError,
    assert_attempt_output_root,
    load_json,
    repo_root,
    sha256_file,
    write_json,
)
from tools.build.dvf_3_3_food_semantic.curation_workflow import (
    run_phase8,
    run_phase9,
)
from tools.build.dvf_3_3_food_semantic.lineage_allowlist import (
    run_phase3,
    run_phase4,
    run_phase5,
)
from tools.build.dvf_3_3_food_semantic.naturalization_handoff import run_phase12
from tools.build.dvf_3_3_food_semantic.schema_feasibility import (
    run_phase6,
    run_phase7,
)


ATTEMPT_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
FOCUSED_VALIDATION_COMMAND = (
    'uv run python -B -m unittest discover '
    '-s Iris/build/description/v2/tests '
    '-p "test_dvf_3_3_food_semantic_*.py"'
)


def resolve_attempt_root(root: Path, attempt_id: str) -> Path:
    if not ATTEMPT_ID_PATTERN.fullmatch(attempt_id):
        raise FoodSemanticError(f"invalid attempt id: {attempt_id!r}")
    attempt_root = root / ATTEMPT_ROOT_FRAGMENT / attempt_id
    assert_attempt_output_root(attempt_root, root=root)
    return attempt_root


def _run_phases(
    phase_functions: list[tuple[str, Callable[[], dict[str, Any]]]],
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for phase_name, function in phase_functions:
        result = function()
        if result.get("status") in {"FAIL", "BLOCKED"}:
            raise FoodSemanticError(f"{phase_name} did not pass: {result}")
        results[phase_name] = result
    return results


def run_kernel(root: Path, attempt_root: Path, attempt_id: str) -> dict[str, Any]:
    results = _run_phases(
        [
            ("phase0", lambda: run_phase0(root, attempt_root)),
            ("phase1", lambda: run_phase1(root, attempt_root)),
            ("phase2", lambda: run_phase2(root, attempt_root)),
            ("phase3", lambda: run_phase3(root, attempt_root)),
            ("phase4", lambda: run_phase4(root, attempt_root, attempt_id)),
            ("phase5", lambda: run_phase5(root, attempt_root)),
            ("phase6", lambda: run_phase6(root, attempt_root)),
            ("phase7", lambda: run_phase7(root, attempt_root)),
        ]
    )
    kernel = load_json(
        attempt_root / "phase7_automatic_mapping/feasibility_kernel_bundle.json"
    )
    summary = {
        "schema_version": "food-semantic-kernel-execution-summary-v1",
        "attempt_id": attempt_id,
        "status": kernel["feasibility_kernel_state"],
        "completed_phases": list(results),
        "changes_8_through_13_allowed": kernel["changes_8_through_13_allowed"],
        "authority_claim_emitted_count": 0,
    }
    write_json(attempt_root / "kernel_execution_summary.json", summary)
    return summary


def run_implementation(
    root: Path, attempt_root: Path, attempt_id: str
) -> dict[str, Any]:
    kernel = load_json(
        attempt_root / "phase7_automatic_mapping/feasibility_kernel_bundle.json"
    )
    if (
        kernel["feasibility_kernel_state"] != "PASS"
        or not kernel["changes_8_through_13_allowed"]
    ):
        raise FoodSemanticError("implementation phases require a PASS kernel")
    results = _run_phases(
        [
            ("phase8", lambda: run_phase8(root, attempt_root)),
            ("phase9", lambda: run_phase9(root, attempt_root)),
            ("phase10", lambda: run_phase10(root, attempt_root, attempt_id)),
            ("phase11", lambda: run_phase11(root, attempt_root)),
            ("phase12", lambda: run_phase12(root, attempt_root)),
            (
                "phase13",
                lambda: run_phase13(
                    root, attempt_root, attempt_id, seal_bundle=False
                ),
            ),
        ]
    )
    summary = {
        "schema_version": "food-semantic-implementation-execution-summary-v1",
        "attempt_id": attempt_id,
        "status": "PASS",
        "completed_phases": list(results),
        "changes_8_through_13_implementation_complete": True,
        "implementation_complete_bundle_sealed": False,
        "authority_execution_authorized": False,
        "current_facts_manifest_mutation_count": 0,
        "authority_claim_emitted_count": 0,
    }
    write_json(attempt_root / "implementation_execution_summary.json", summary)
    return summary


def record_focused_validation(
    attempt_root: Path, *, command: str, exit_code: int
) -> dict[str, Any]:
    if command != FOCUSED_VALIDATION_COMMAND:
        raise FoodSemanticError("focused validation command does not match the plan")
    if exit_code != 0:
        raise FoodSemanticError("a non-zero validation result cannot be recorded as PASS")
    record = {
        "schema_version": "food-semantic-focused-validation-result-v1",
        "status": "PASS",
        "command": command,
        "exit_code": exit_code,
        "implementation_machine_validation": "PASS",
    }
    write_json(
        attempt_root / "phase13_closeout/focused_validation_result.json",
        record,
    )
    return record


def seal_implementation_bundle(
    root: Path, attempt_root: Path, attempt_id: str
) -> dict[str, Any]:
    summary = load_json(attempt_root / "implementation_execution_summary.json")
    if not summary["changes_8_through_13_implementation_complete"]:
        raise FoodSemanticError("implementation phases are incomplete")
    validation_path = (
        attempt_root / "phase13_closeout/focused_validation_result.json"
    )
    validation = load_json(validation_path)
    if (
        validation.get("status") != "PASS"
        or validation.get("command") != FOCUSED_VALIDATION_COMMAND
        or validation.get("exit_code") != 0
    ):
        raise FoodSemanticError("focused validation evidence is missing or invalid")
    return run_phase13(root, attempt_root, attempt_id, seal_bundle=True)


def verify_bundle(root: Path, attempt_root: Path) -> dict[str, Any]:
    bundle_path = (
        attempt_root / "phase13_closeout/implementation_complete_bundle.json"
    )
    bundle = load_json(bundle_path)
    mismatches = []
    for row in bundle["artifacts"]:
        path = root / row["path"]
        if not path.is_file():
            mismatches.append({"path": row["path"], "reason": "missing"})
        elif sha256_file(path) != row["sha256"]:
            mismatches.append({"path": row["path"], "reason": "sha256_mismatch"})
    protected = load_json(
        attempt_root / "phase11_successor/protected_surface_hashes_after.json"
    )
    result = {
        "status": "PASS" if not mismatches else "FAIL",
        "bundle_sha256": sha256_file(bundle_path),
        "artifact_count": len(bundle["artifacts"]),
        "artifact_mismatch_count": len(mismatches),
        "artifact_mismatches": mismatches,
        "protected_surface_changed_count": protected["changed_count"],
        "authority_claim_emitted_count": bundle["authority_claim_emitted_count"],
        "current_facts_manifest_mutation_count": bundle[
            "current_facts_manifest_mutation_count"
        ],
        "implementation_complete_bundle_sealed": bundle[
            "implementation_complete_bundle_sealed"
        ],
    }
    if result["status"] != "PASS":
        raise FoodSemanticError(f"implementation bundle verification failed: {result}")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build candidate-only DVF 3-3 food semantic authority contracts "
            "and attempt evidence."
        )
    )
    parser.add_argument(
        "command",
        choices=[
            "kernel",
            "implementation",
            "all",
            "record-validation",
            "seal",
            "verify",
        ],
    )
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--validation-command", default=FOCUSED_VALIDATION_COMMAND)
    parser.add_argument("--validation-exit-code", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = repo_root()
    attempt_root = resolve_attempt_root(root, args.attempt_id)
    try:
        if args.command == "kernel":
            result = run_kernel(root, attempt_root, args.attempt_id)
        elif args.command == "implementation":
            result = run_implementation(root, attempt_root, args.attempt_id)
        elif args.command == "all":
            run_kernel(root, attempt_root, args.attempt_id)
            result = run_implementation(root, attempt_root, args.attempt_id)
        elif args.command == "record-validation":
            if args.validation_exit_code is None:
                raise FoodSemanticError(
                    "--validation-exit-code is required for record-validation"
                )
            result = record_focused_validation(
                attempt_root,
                command=args.validation_command,
                exit_code=args.validation_exit_code,
            )
        elif args.command == "seal":
            result = seal_implementation_bundle(
                root, attempt_root, args.attempt_id
            )
        else:
            result = verify_bundle(root, attempt_root)
    except (FoodSemanticError, FileNotFoundError, KeyError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "BLOCKED", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
