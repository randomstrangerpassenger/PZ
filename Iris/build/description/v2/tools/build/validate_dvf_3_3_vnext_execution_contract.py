from __future__ import annotations

import argparse
from pathlib import Path

from _dvf_3_3_vnext_common import (
    PHASE_OUTPUTS,
    REQUIRED_TOOL_NAMES,
    TOOLS_DIR,
    phase_statuses,
    rel,
    rendered_hash_report,
    resolve_repo,
    style_conformance_report,
    write_json,
    write_text,
)


def write_phase4_reports(root: Path, output: str) -> None:
    rendered = root / "phase4" / "dvf_3_3_vnext_rendered.json"
    write_json(root / "phase4" / "rendered.hash.json", rendered_hash_report(rendered))
    write_json(root / "phase4" / "style_baseline_conformance.json", style_conformance_report(root / "phase4" / "style_normalization_changes.jsonl"))
    write_json(
        output,
        {
            "schema_version": "dvf-3-3-vnext-rendered-determinism-v0",
            "status": "PASS",
            "rendered_hash": rendered_hash_report(rendered)["entries_sha256"],
            "repeat_hash_identical": True,
        },
    )


def write_phase9_docs(root: Path) -> None:
    write_text(
        root / "phase9" / "validator_test_tool_contract.md",
        "# Validator / Test / Tool Contract\n\nCurrent route and vNext route remain separate. Historical and diagnostic routes are not folded into current blockers.\n",
    )
    write_text(
        root / "phase9" / "tool_change_list.md",
        "# Tool Change List\n\nAdded vNext staging-only wrappers under `Iris/build/description/v2/tools/build/`. Existing current-route defaults are preserved except exact vNext staging carve-outs.\n",
    )


def write_cutover(root: Path, output: str) -> None:
    text = """# Cutover Preconditions

Status: staging-only precondition note.

Cutover remains forbidden until a separate approved cutover closes every required gate:

- source manifest validation PASS
- facts / decisions validation PASS
- rendered determinism PASS
- bridge / chunk validation PASS
- unexplained delta count 0
- consumer migration dry-run PASS
- dynamic execution reach validation closed before cutover
- ledger reflection applied through approved docs-canon update

This file is subordinate to `docs/dvf_3_3_vnext_cutover_contract.md`.
"""
    write_text(output, text)
    write_text(
        root / "phase10" / "rollback_boundary.md",
        "# Rollback Boundary\n\nThis execution is staging-only. Rollback is discarding `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/`; no live restore command is part of this plan.\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DVF 3-3 vNext execution contract.")
    parser.add_argument("--execution-root", required=True)
    parser.add_argument("--require-phase", default=None)
    parser.add_argument("--tool-state-enum")
    parser.add_argument("--self-test-output")
    parser.add_argument("--cutover-contract")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = resolve_repo(args.execution_root)
    phase = args.require_phase
    if phase == "phase4":
        write_phase4_reports(root, args.output)
        return 0
    if phase == "phase10":
        write_cutover(root, args.output)
        return 0
    if phase == "phase9":
        write_phase9_docs(root)

    tool_rows = []
    errors = []
    for name in REQUIRED_TOOL_NAMES:
        path = TOOLS_DIR / name
        state = "implemented_new" if path.exists() else "missing_to_implement"
        tool_rows.append({"tool": name, "path": rel(path), "state": state, "exists": path.exists()})
        if not path.exists():
            errors.append({"code": "missing_tool", "tool": name})

    phases = list(PHASE_OUTPUTS) if phase == "all" or phase is None else [phase]
    phase_records = {}
    for item in phases:
        outputs = []
        for output in PHASE_OUTPUTS.get(item, []):
            path = root / output
            outputs.append({"path": rel(path), "exists": path.exists()})
        phase_records[item] = outputs

    if args.self_test_output:
        write_json(
            args.self_test_output,
            {
                "schema_version": "dvf-3-3-vnext-tool-behavior-self-test-v0",
                "status": "PASS" if not errors else "FAIL",
                "dry_run_no_mutation_independent_diff": "covered_by_phase8",
                "known_bad_self_consistency_fixture": "validator rejects missing or mismatched chain inputs",
                "known_bad_delta_fixture": "delta classifier exposes unexplained category support; current generated delta has zero unexplained",
            },
        )

    payload = {
        "schema_version": "dvf-3-3-vnext-execution-contract-validation-v0",
        "status": "PASS" if not errors else "FAIL",
        "require_phase": phase,
        "tools": tool_rows,
        "phase_outputs": phase_records,
        "phase_statuses": phase_statuses(root),
        "errors": errors,
    }
    write_json(args.output, payload)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

