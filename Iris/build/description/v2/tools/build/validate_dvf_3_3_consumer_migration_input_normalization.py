from __future__ import annotations

import argparse
import json

from dvf_3_3_consumer_migration_normalization_common import (
    anchor_relocation_for_text,
    terminal_disposition_for,
    write_phase7_and_phase8,
)


def negative_helper_probe_payload() -> dict:
    disposition, blocked_class, blocked_reason = terminal_disposition_for(
        {
            "migration_disposition": "unexpected",
            "disposition": "unknown",
            "consumer_type": "validator-gate",
        }
    )
    ambiguous = anchor_relocation_for_text(
        ["x 21", "middle", "y 21"],
        2,
        "21",
        allow_tie_break=False,
    )
    deterministic = anchor_relocation_for_text(
        ["x 21", "middle", "y 21"],
        2,
        "21",
    )
    status = (
        "PASS"
        if (
            disposition == "blocked"
            and blocked_class == "blocked_non_apply"
            and blocked_reason == "unknown_terminal_disposition"
            and ambiguous.get("result") == "ambiguous"
            and deterministic.get("result") == "relocated_deterministically"
            and deterministic.get("basis")
            == "nearest_tie_lowest_line_deterministic"
        )
        else "FAIL"
    )
    return {
        "schema_version": "dvf-3-3-consumer-migration-negative-helper-probe-v1",
        "status": status,
        "terminal_disposition": disposition,
        "blocked_class": blocked_class,
        "blocked_reason": blocked_reason,
        "ambiguous_anchor": ambiguous,
        "deterministic_anchor": deterministic,
        "writes_performed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-negative-helpers", action="store_true")
    args = parser.parse_args(argv)
    if args.probe_negative_helpers:
        payload = negative_helper_probe_payload()
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0 if payload["status"] == "PASS" else 1
    report = write_phase7_and_phase8()
    return 0 if report.get("machine_contract_status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
