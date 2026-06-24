from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import build_source_manifest_payload, source_attempt_order_text, source_schema, write_json, write_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Build DVF 3-3 vNext source manifest.")
    parser.add_argument("--source-conditions", required=True)
    parser.add_argument("--partial-input-manifest", required=True)
    parser.add_argument("--runtime-seed", required=True)
    parser.add_argument("--schema-output", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--attempt-order-output", required=True)
    parser.add_argument("--blocked-output", required=True)
    args = parser.parse_args()

    payload, status = build_source_manifest_payload(args.partial_input_manifest, args.runtime_seed)
    write_json(args.schema_output, source_schema())
    write_json(args.output, payload)
    write_text(args.attempt_order_output, source_attempt_order_text(status))
    write_text(args.blocked_output, f"# Source Blocked State\n\nStatus: `{status}`.\n")
    return 0 if status == "confirmed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

