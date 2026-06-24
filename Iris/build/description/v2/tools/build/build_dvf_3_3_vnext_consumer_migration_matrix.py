from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import build_migration_matrix, write_json, write_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description="Build DVF 3-3 vNext consumer migration matrix.")
    parser.add_argument("--classified-ledger", required=True)
    parser.add_argument("--change-required", required=True)
    parser.add_argument("--change-forbidden", required=True)
    parser.add_argument("--executing-impact", required=True)
    parser.add_argument("--input-manifest-output", required=True)
    parser.add_argument("--matrix-output", required=True)
    parser.add_argument("--expected-change-required", type=int, required=True)
    parser.add_argument("--expected-change-forbidden", type=int, required=True)
    args = parser.parse_args()

    manifest, rows = build_migration_matrix(
        args.classified_ledger,
        args.change_required,
        args.change_forbidden,
        args.executing_impact,
        args.expected_change_required,
        args.expected_change_forbidden,
    )
    write_json(args.input_manifest_output, manifest)
    write_jsonl(args.matrix_output, rows)
    return 0 if manifest["count_reconciliation"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

