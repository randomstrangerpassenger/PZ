from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import read_json, validate_source_manifest_payload, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 vNext source manifest.")
    parser.add_argument("--schema", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--source-conditions", required=True)
    parser.add_argument("--fingerprint-output", required=True)
    parser.add_argument("--report-output", required=True)
    args = parser.parse_args()

    manifest = read_json(args.manifest)
    report, fingerprint, ok = validate_source_manifest_payload(manifest)
    write_json(args.report_output, report)
    write_json(args.fingerprint_output, fingerprint)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

