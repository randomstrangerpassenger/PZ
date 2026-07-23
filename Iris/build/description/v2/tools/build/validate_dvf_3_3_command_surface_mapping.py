from __future__ import annotations

import argparse
import json

from dvf_3_3_cutover_tooling_readiness_common import (
    MANDATORY_COMMAND_FIELDS,
    validate_command_surface_mapping,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping")
    parser.add_argument("--evidence-root")
    parser.add_argument("--describe-contract", action="store_true")
    args = parser.parse_args()
    if args.describe_contract:
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "mandatory_command_fields": list(MANDATORY_COMMAND_FIELDS),
                },
                sort_keys=True,
            )
        )
        return 0
    report = validate_command_surface_mapping(args.mapping, args.evidence_root)
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
