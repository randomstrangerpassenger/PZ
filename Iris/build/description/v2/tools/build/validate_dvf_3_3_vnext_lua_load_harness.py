from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import validate_lua_harness, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 vNext staging Lua load harness.")
    parser.add_argument("--staging-data-root", required=True)
    parser.add_argument("--live-data-root", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--loaded-paths-output", required=True)
    parser.add_argument("--leak-report-output", required=True)
    args = parser.parse_args()

    report, loaded, leak_report, chunk_hashes = validate_lua_harness(args.staging_data_root, args.live_data_root)
    write_json(args.report_output, report)
    write_json(args.loaded_paths_output, {"schema_version": "dvf-3-3-vnext-loaded-module-paths-v0", "loaded": loaded})
    write_json(args.leak_report_output, leak_report)
    write_json(f"{args.staging_data_root}/chunk_hashes.json", chunk_hashes)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

