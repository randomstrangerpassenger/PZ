from __future__ import annotations

import argparse

from dvf_3_3_cutover_tooling_readiness_common import (
    CLAIM_BOUNDARY,
    assert_destructive_target_allowed,
    replace_target_with_candidate,
    restore_target_from_snapshot,
    snapshot_runtime_target,
    validate_candidate_bundle,
    write_json,
    write_runtime_cutover_readiness,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true")
    parser.add_argument("--validate-candidate", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--restore", action="store_true")
    parser.add_argument("--target-kind", default="staging-copy")
    parser.add_argument("--target-data-dir")
    parser.add_argument("--candidate-data-dir")
    parser.add_argument("--snapshot-dir")
    parser.add_argument("--snapshot-manifest")
    parser.add_argument("--output")
    args = parser.parse_args()

    if not any([args.snapshot, args.validate_candidate, args.apply, args.restore]):
        report = write_runtime_cutover_readiness()
        return 0 if report.get("status") == "PASS" else 1

    if args.snapshot:
        if not args.target_data_dir or not args.snapshot_dir or not args.snapshot_manifest:
            parser.error("--snapshot requires --target-data-dir, --snapshot-dir, and --snapshot-manifest")
        report = snapshot_runtime_target(args.target_data_dir, args.snapshot_dir, args.snapshot_manifest)
        if args.output:
            write_json(args.output, report)
        return 0 if report.get("status") == "PASS" else 1

    if args.validate_candidate:
        if not args.candidate_data_dir:
            parser.error("--validate-candidate requires --candidate-data-dir")
        report = validate_candidate_bundle(args.candidate_data_dir)
        if args.output:
            write_json(args.output, report)
        return 0 if report.get("status") == "PASS" else 1

    if args.apply:
        if not args.target_data_dir or not args.candidate_data_dir:
            parser.error("--apply requires --target-data-dir and --candidate-data-dir")
        assert_destructive_target_allowed(args.target_data_dir, args.target_kind, True)
        replace_target_with_candidate(args.target_data_dir, args.candidate_data_dir)
        report = validate_candidate_bundle(args.target_data_dir)
        report.update({"mode": "apply", "target_kind": args.target_kind, "claim_boundary": CLAIM_BOUNDARY})
        if args.output:
            write_json(args.output, report)
        return 0 if report.get("status") == "PASS" else 1

    if args.restore:
        if not args.target_data_dir or not args.snapshot_dir:
            parser.error("--restore requires --target-data-dir and --snapshot-dir")
        assert_destructive_target_allowed(args.target_data_dir, args.target_kind, True)
        restore_target_from_snapshot(args.target_data_dir, args.snapshot_dir)
        report = validate_candidate_bundle(args.target_data_dir)
        report.update({"mode": "restore", "target_kind": args.target_kind, "claim_boundary": CLAIM_BOUNDARY})
        if args.output:
            write_json(args.output, report)
        return 0 if report.get("status") == "PASS" else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
