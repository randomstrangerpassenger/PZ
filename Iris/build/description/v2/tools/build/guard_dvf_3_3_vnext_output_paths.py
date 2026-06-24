from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import (
    EXECUTION_ROOT,
    output_paths_for_phase,
    path_intersects_surface,
    read_json,
    rel,
    resolve_repo,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard DVF 3-3 vNext writable output paths.")
    parser.add_argument("--command-contract", required=True)
    parser.add_argument("--protected-surface", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--known-protected-output")
    parser.add_argument("--expect-fail", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    surface = read_json(args.protected_surface)
    outputs = output_paths_for_phase(args.phase)
    if args.known_protected_output:
        outputs.append(resolve_repo(args.known_protected_output))
    records = []
    violations = []
    for output in outputs:
        output = resolve_repo(output)
        phase_local = output == (EXECUTION_ROOT / args.phase).resolve() or (EXECUTION_ROOT / args.phase).resolve() in output.parents
        protected = path_intersects_surface(output, surface)
        record = {
            "path": rel(output),
            "phase_local": phase_local,
            "protected_surface_intersection": protected,
        }
        records.append(record)
        if protected or (not phase_local and args.phase != "phase0"):
            violations.append(record)
    guard_failed = bool(violations)
    status = "PASS"
    if guard_failed:
        status = "EXPECTED_FAIL" if args.expect_fail else "FAIL"
    payload = {
        "schema_version": "dvf-3-3-vnext-output-path-preflight-guard-v0",
        "phase": args.phase,
        "status": status,
        "guard_failed": guard_failed,
        "expect_fail": args.expect_fail,
        "checked_count": len(records),
        "violation_count": len(violations),
        "records": records,
        "violations": violations,
    }
    write_json(args.output, payload)
    if args.expect_fail:
        return 0 if guard_failed else 1
    return 1 if guard_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

