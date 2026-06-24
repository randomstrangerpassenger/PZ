from __future__ import annotations

import argparse
from pathlib import Path

from _dvf_3_3_vnext_common import compose_binding_payload, read_jsonl, resolve_repo, write_json, write_jsonl, write_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 vNext compose binding.")
    parser.add_argument("--profiles", required=True)
    parser.add_argument("--identity-rules", required=True)
    parser.add_argument("--precedence-rules", required=True)
    parser.add_argument("--binding-output", required=True)
    parser.add_argument("--fingerprint-output", required=True)
    parser.add_argument("--overlay-disposition-output", required=True)
    args = parser.parse_args()

    binding, fingerprint, overlay = compose_binding_payload(args.profiles, args.identity_rules, args.precedence_rules)
    phase3_dir = resolve_repo(args.binding_output).parent
    execution_root = phase3_dir.parent
    facts_path = execution_root / "phase2" / "dvf_3_3_vnext_facts.jsonl"
    accepted_overlay_path = phase3_dir / "accepted_overlay.jsonl"
    if facts_path.exists():
        overlay_rows = [
            {
                "item_id": row["item_id"],
                "layer1_identity_hint": row.get("identity_hint"),
                "layer2_anchor_hint": None,
                "layer4_context_hint": None,
                "overlay_role": "generated_from_accepted_vnext_facts_for_body_plan_v2",
            }
            for row in read_jsonl(facts_path)
            if row.get("item_id") is not None
        ]
        write_jsonl(accepted_overlay_path, overlay_rows)
        overlay = overlay.rstrip() + (
            "\n\nAccepted minimal overlay generated from Phase 2 facts for body-plan v2 composer support: "
            f"`{Path(accepted_overlay_path).as_posix()}`.\n"
        )
        binding["accepted_overlay_path"] = str(accepted_overlay_path)
        binding["accepted_overlay_role"] = "compose_support_not_source_authority"
    write_json(args.binding_output, binding)
    write_json(args.fingerprint_output, fingerprint)
    write_text(args.overlay_disposition_output, overlay)
    return 0 if binding["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
