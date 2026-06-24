from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import (
    build_command_inventory,
    build_input_readpoint,
    build_template_anchor,
    command_contract_text,
    protected_surface_payload,
    write_json,
    write_text,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write DVF 3-3 vNext Phase 0 contract inputs.")
    parser.add_argument("--execution-root", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--source-authority-conditions", required=True)
    parser.add_argument("--cutover-contract", required=True)
    parser.add_argument("--input-readpoint-output", required=True)
    parser.add_argument("--template-anchor-output", required=True)
    parser.add_argument("--protected-surface-output", required=True)
    parser.add_argument("--command-contract-output", required=True)
    args = parser.parse_args()

    write_json(
        args.input_readpoint_output,
        build_input_readpoint(args.plan, args.template, args.source_authority_conditions, args.cutover_contract),
    )
    write_json(args.template_anchor_output, build_template_anchor(args.template, args.plan))
    write_json(args.protected_surface_output, protected_surface_payload())
    write_text(args.command_contract_output, command_contract_text())
    write_json(f"{args.execution_root}/phase0/command_surface_inventory.json", build_command_inventory())
    write_text(f"{args.execution_root}/EXECUTION_CONTRACT.md", command_contract_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

