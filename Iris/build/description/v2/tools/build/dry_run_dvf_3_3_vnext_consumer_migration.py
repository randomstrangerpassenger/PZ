from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import dry_run_migration, write_json, write_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run DVF 3-3 vNext consumer migration without mutation.")
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--dry-run-output", required=True)
    parser.add_argument("--consumer-before-hashes", required=True)
    parser.add_argument("--consumer-after-hashes", required=True)
    parser.add_argument("--consumer-hash-diff", required=True)
    parser.add_argument("--forbidden-touch-output", required=True)
    parser.add_argument("--blockers-output", required=True)
    args = parser.parse_args()

    dry_run, before, after, diff, blockers, forbidden = dry_run_migration(args.matrix)
    write_json(args.dry_run_output, dry_run)
    write_json(args.consumer_before_hashes, before)
    write_json(args.consumer_after_hashes, after)
    write_json(args.consumer_hash_diff, diff)
    write_json(args.forbidden_touch_output, forbidden)
    write_text(args.blockers_output, blockers)
    ok = dry_run["status"] == "PASS" and diff["changed_count"] == 0 and forbidden["status"] == "PASS"
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

