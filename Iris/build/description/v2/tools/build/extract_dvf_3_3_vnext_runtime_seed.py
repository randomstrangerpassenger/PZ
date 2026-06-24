from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import load_lua_chunks, write_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract non-authority runtime-derived seed rows.")
    parser.add_argument("--runtime-manifest", required=True)
    parser.add_argument("--runtime-chunk-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--provenance", required=True)
    args = parser.parse_args()

    entries = load_lua_chunks(args.runtime_manifest, args.runtime_chunk_dir)
    rows = [
        {
            "item_id": item_id,
            "runtime_entry": entry,
            "provenance": args.provenance,
            "authority_role": "non_authority_bootstrap_seed",
            "accepted_source_authority": False,
        }
        for item_id, entry in sorted(entries.items())
    ]
    write_jsonl(args.output, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

