from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import build_facts_decisions_payload, hash_jsonl_rows, write_json, write_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description="Build DVF 3-3 vNext facts and decisions.")
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--facts-output", required=True)
    parser.add_argument("--decisions-output", required=True)
    parser.add_argument("--hash-output", required=True)
    args = parser.parse_args()

    facts, decisions = build_facts_decisions_payload(args.source_manifest)
    write_jsonl(args.facts_output, facts)
    write_jsonl(args.decisions_output, decisions)
    write_json(
        args.hash_output,
        {
            "schema_version": "dvf-3-3-vnext-facts-decisions-hashes-v0",
            "facts_count": len(facts),
            "decisions_count": len(decisions),
            "facts_rows_sha256": hash_jsonl_rows(facts),
            "decisions_rows_sha256": hash_jsonl_rows(decisions),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

