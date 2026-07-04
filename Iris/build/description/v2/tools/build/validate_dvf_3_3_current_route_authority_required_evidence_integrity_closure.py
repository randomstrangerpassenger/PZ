#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os

from dvf_3_3_current_route_authority_required_evidence_integrity_closure import (
    EVIDENCE_ROOT,
    read_json_object,
    record_command_matrix_exit,
    validate_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate DVF 3-3 current-route authority required-evidence integrity closure."
    )
    parser.add_argument("--require-scaffold", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    run_focused = (
        args.require_complete and os.environ.get("DVF_CURRENT_ROUTE_CLOSURE_SKIP_NESTED_FOCUSED") != "1"
    )
    report, ok = validate_artifacts(
        require_scaffold=args.require_scaffold,
        require_complete=args.require_complete,
        run_focused=run_focused,
    )
    print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
    exit_code = 0 if ok else 1
    if args.require_complete and run_focused:
        focused = read_json_object(EVIDENCE_ROOT / "phase8" / "focused_unittest_result.json")
        record_command_matrix_exit(7, focused.get("exit_code"))
        record_command_matrix_exit(6, exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
