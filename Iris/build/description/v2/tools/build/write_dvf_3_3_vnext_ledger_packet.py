from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import phase_statuses, rel, resolve_repo, write_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Write DVF 3-3 vNext staging-only ledger packet.")
    parser.add_argument("--execution-root", required=True)
    parser.add_argument("--packet-output", required=True)
    parser.add_argument("--decisions-output", required=True)
    parser.add_argument("--architecture-output", required=True)
    parser.add_argument("--roadmap-output", required=True)
    args = parser.parse_args()

    root = resolve_repo(args.execution_root)
    statuses = phase_statuses(root)
    terminal = "staging_evidence_produced_for_adversarial_review"
    if statuses.get("phase10") == "FAIL":
        terminal = "failed_protected_surface_mutation"
    elif any(value == "missing" for value in statuses.values()):
        terminal = "partial_blocked_some_phases_incomplete"

    packet = f"""# DVF 3-3 vNext Ledger Update Packet

Status: `{terminal}`.

Evidence root: `{rel(root)}`.

This packet is staging-only. It does not claim successor current authority, sealed baseline identity, runtime cutover, consumer migration execution, package readiness, release readiness, Workshop readiness, B42 readiness, or manual in-game validation.
"""
    write_text(args.packet_output, packet)
    write_text(args.decisions_output, "# Proposed DECISIONS Entry\n\nDraft only. Canon docs remain unchanged by this phase.\n")
    write_text(args.architecture_output, "# Proposed ARCHITECTURE Patch\n\nDraft only. No direct mutation is performed.\n")
    write_text(args.roadmap_output, "# Proposed ROADMAP Patch\n\nDraft only. Staging evidence is review input, not release readiness.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

