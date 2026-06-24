from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import diff_surface, hash_surface, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Hash DVF 3-3 vNext protected surfaces.")
    parser.add_argument("--surface", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--compare")
    parser.add_argument("--diff-output")
    parser.add_argument("--verdict-output")
    args = parser.parse_args()

    payload = hash_surface(args.surface)
    write_json(args.output, payload)
    if args.compare:
        diff = diff_surface(args.compare, payload)
        if args.diff_output:
            write_json(args.diff_output, diff)
        if args.verdict_output:
            write_json(
                args.verdict_output,
                {
                    "schema_version": "dvf-3-3-vnext-protected-surface-no-mutation-verdict-v0",
                    "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
                    "changed_count": diff["changed_count"],
                    "failed_state": None if diff["changed_count"] == 0 else "failed_protected_surface_mutation",
                },
            )
        return 0 if diff["changed_count"] == 0 else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

