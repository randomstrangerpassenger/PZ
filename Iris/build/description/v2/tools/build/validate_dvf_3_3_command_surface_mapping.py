from __future__ import annotations

import argparse

from dvf_3_3_cutover_tooling_readiness_common import validate_command_surface_mapping


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping")
    parser.add_argument("--evidence-root")
    args = parser.parse_args()
    report = validate_command_surface_mapping(args.mapping, args.evidence_root)
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
