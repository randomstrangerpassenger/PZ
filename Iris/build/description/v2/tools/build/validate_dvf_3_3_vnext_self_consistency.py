from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import self_consistency_report, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 vNext source-to-runtime self consistency.")
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--facts", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--compose-binding", required=True)
    parser.add_argument("--rendered", required=True)
    parser.add_argument("--bridge-report", required=True)
    parser.add_argument("--chunk-manifest", required=True)
    parser.add_argument("--chunk-dir", required=True)
    parser.add_argument("--lua-load-report", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--fingerprint-output", required=True)
    args = parser.parse_args()

    report, fingerprint, ok = self_consistency_report(
        args.source_manifest,
        args.facts,
        args.decisions,
        args.compose_binding,
        args.rendered,
        args.bridge_report,
        args.chunk_manifest,
        args.chunk_dir,
        args.lua_load_report,
    )
    write_json(args.report_output, report)
    write_json(args.fingerprint_output, fingerprint)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

