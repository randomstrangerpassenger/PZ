#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from dvf_3_3_core_registry_boundary_required_gate_adoption import (
    EVIDENCE_ROOT,
    ROUND_REQUIRED_TESTS,
    live_claim_rescan,
    round_required_artifacts,
    validate_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate DVF 3-3 Core / Registry boundary required gate adoption artifacts."
    )
    parser.add_argument("--root", type=Path, default=EVIDENCE_ROOT)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--skip-route-requirements", action="store_true")
    parser.add_argument("--probe-contract", action="store_true")
    args = parser.parse_args()

    if args.probe_contract:
        clean_scan = live_claim_rescan(mode="pre_route", root=args.root)
        with tempfile.TemporaryDirectory(prefix="dvf_claim_inject_") as temp_dir:
            injected = Path(temp_dir) / "forbidden_claim.md"
            injected.write_text(
                "Current DVF PASS is sufficient for release readiness.\n",
                encoding="utf-8",
            )
            injected_scan = live_claim_rescan(
                mode="pre_route",
                root=args.root,
                extra_paths=[injected],
            )
        payload = {
            "status": (
                "PASS"
                if clean_scan.get("status") == "PASS"
                and injected_scan.get("forbidden_overclaim_count", 0) > 0
                else "FAIL"
            ),
            "clean_scan": clean_scan,
            "injected_scan": injected_scan,
            "round_required_artifacts": round_required_artifacts(),
            "round_required_tests": list(ROUND_REQUIRED_TESTS),
        }
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0 if payload["status"] == "PASS" else 1

    report, ok = validate_artifacts(
        args.root,
        require_complete=args.require_complete,
        skip_route_requirements=args.skip_route_requirements,
    )
    print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
