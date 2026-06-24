from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import validate_facts_decisions_payload, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 vNext facts and decisions.")
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--facts", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--report-output", required=True)
    args = parser.parse_args()

    report, ok = validate_facts_decisions_payload(args.source_manifest, args.facts, args.decisions)
    write_json(args.report_output, report)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

