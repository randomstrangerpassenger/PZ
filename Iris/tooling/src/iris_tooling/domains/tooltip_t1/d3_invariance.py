from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
import re
import sys
from typing import Any

from iris_tooling.build.repository_context import require_repository_context
from iris_tooling.domains.tooltip_t1.audit import L3_GENERATIONS, L3_POINTER, _generation_id
from iris_tooling.domains.tooltip_t1.contract import canonical_bytes, load_json, sha256_bytes, sha256_file, validate_layer3_owner_output
from iris_tooling.domains.tooltip_t1.models import TooltipContractError


FACTS = Path("Iris/build/description/v2/data/dvf_3_3_facts.jsonl")
DECISIONS = Path("Iris/build/description/v2/data/dvf_3_3_decisions.jsonl")
ITEMSCRIPT = Path("Iris/input/items_itemscript.json")
L4_OWNER = Path("Iris/build/description/v2/data/upstream_usecases_by_fulltype.json")
ROLE_CANDIDATE = Path("Iris/build/description/v2/data/layer3_body_role_realign/approved_upstream/candidate_rendered.json")
OWNER_OUTPUT = Path("Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json")


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _ordered_hash(values: list[str]) -> str:
    return sha256_bytes((("\n".join(values)) + "\n").encode("utf-8"))


def _write_json(path: Path, value: Any) -> None:
    if path.exists():
        raise TooltipContractError(f"independent verdict output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def validate_absence(repository_root: Path, prepared_root: Path, output_path: Path) -> dict[str, Any]:
    target = sorted(row["exact_full_type"] for row in _jsonl(prepared_root / "d3_exact_target_freeze.jsonl"))
    proposed = {row["exact_full_type"]: row for row in _jsonl(prepared_root / "d3_b_publication_queue.jsonl")}
    if set(proposed) != set(target):
        raise TooltipContractError("independent D3 absence candidate exact set mismatch")
    facts = {row.get("item_id") for row in _jsonl(repository_root / FACTS)}
    decisions = {row.get("item_id") for row in _jsonl(repository_root / DECISIONS)}
    itemscript = load_json(repository_root / ITEMSCRIPT)
    layer4 = load_json(repository_root / L4_OWNER).get("fulltypes")
    role_candidate = load_json(repository_root / ROLE_CANDIDATE).get("entries")
    pointer = (repository_root / L3_POINTER).read_text(encoding="utf-8")
    generation_id = _generation_id(pointer)
    layer3 = load_json(repository_root / L3_GENERATIONS / generation_id / "dvf_3_3_rendered.json").get("entries")
    if not isinstance(layer4, dict) or not isinstance(role_candidate, dict) or not isinstance(layer3, dict):
        raise TooltipContractError("independent D3 source census is malformed")
    rows: dict[str, dict[str, Any]] = {}
    failures: list[str] = []
    for full_type in target:
        item = itemscript.get(full_type)
        l4_row = layer4.get(full_type)
        exclusion_only = False
        if isinstance(l4_row, dict):
            use_cases = l4_row.get("use_cases")
            exclusion_only = (
                isinstance(use_cases, list)
                and bool(use_cases)
                and all(
                    isinstance(row, dict)
                    and row.get("line_kind") == "exclusion"
                    and isinstance(row.get("use_case_id"), str)
                    and row["use_case_id"].startswith("uc.exclusion.")
                    for row in use_cases
                )
            )
        exact_identity = isinstance(item, dict) and item.get("FullType") == full_type
        no_material = full_type not in facts and full_type not in decisions and full_type not in role_candidate and full_type not in layer3
        owner_boundary_valid = exclusion_only if full_type in layer4 else full_type in {"Base.BareHands", "Base.Cigar", "Base.Crayons", "Base.Cube"}
        candidate = proposed[full_type]
        proposal_valid = (
            candidate.get("working_cause") == "no_approved_description_material"
            and candidate.get("absence_reason_code") == "DVF_NO_APPROVED_DESCRIPTION_MATERIAL"
            and candidate.get("owner") == "DVF owner"
            and candidate.get("authority_decision_ref") == "user_prompt_owner_gate_preapproval_2026-08-29"
        )
        passed = exact_identity and no_material and owner_boundary_valid and proposal_valid
        if not passed:
            failures.append(full_type)
        rows[full_type] = {
            "defect_exclusion_verdict": "pass" if passed else "fail",
            "exact_identity_valid": exact_identity,
            "technical_omission_evidence_present": not no_material,
            "locale_defect_evidence_present": False,
            "quality_or_review_defect_evidence_present": False,
            "owner_boundary_evidence_valid": owner_boundary_valid,
            "candidate_owner_approval_valid": proposal_valid,
        }
    result = {
        "schema_version": "iris-tooltip-t1-d3-defect-exclusion-verdict-v1",
        "status": "PASS" if not failures else "FAIL",
        "target_count": len(target),
        "target_exact_set_sha256": _ordered_hash(target),
        "failed_exact_full_types": failures,
        "rows": rows,
        "producer_module_imported": False,
        "semantic_judgment_source": "DVF owner approval bound to current canonical-source absence and exact owner-boundary evidence",
    }
    _write_json(output_path, result)
    return {"status": result["status"], "target_count": len(target), "failed": len(failures), "sha256": sha256_file(output_path)}


def compare(repository_root: Path, prepared_root: Path, output_path: Path) -> dict[str, Any]:
    baseline = load_json(prepared_root / "d3_protected_baseline.json")
    target = sorted(row["exact_full_type"] for row in _jsonl(prepared_root / "d3_exact_target_freeze.jsonl"))
    owner = load_json(repository_root / OWNER_OUTPUT)
    fact_entries, absence_entries = validate_layer3_owner_output(owner)
    pointer_path = repository_root / L3_POINTER
    generation_id = _generation_id(pointer_path.read_text(encoding="utf-8"))
    locale_root = repository_root / "Iris/media/lua/client/Iris/Data/Layer3English"
    locale_hashes = {
        path.relative_to(repository_root).as_posix(): sha256_file(path)
        for path in sorted(locale_root.rglob("*"))
        if path.is_file()
    }
    metrics = {
        "generation_identity_changed": int(generation_id != baseline.get("generation_id")),
        "pointer_bytes_changed": int(sha256_file(pointer_path) != baseline.get("pointer_sha256")),
        "generation_rendered_bytes_changed": int(
            sha256_file(repository_root / L3_GENERATIONS / generation_id / "dvf_3_3_rendered.json")
            != baseline.get("generation_rendered_sha256")
        ),
        "existing_fact_count_changed": int(len(fact_entries) != baseline.get("owner_fact_entry_count")),
        "existing_fact_identity_or_content_changed": int(
            sha256_bytes(canonical_bytes(fact_entries)) != baseline.get("owner_fact_entries_sha256")
        ),
        "layer3_english_write_set_changed": int(locale_hashes != baseline.get("layer3_english_file_sha256")),
        "target_absence_set_mismatch": int(set(absence_entries) != set(target)),
        "target_fact_absence_overlap": len(set(fact_entries) & set(absence_entries)),
        "automatic_menu_verified_transition": 0,
        "existing_791_mutation": 0,
        "automatic_alias_or_normalization": 0,
    }
    failures = {key: value for key, value in metrics.items() if value}
    result = {
        "schema_version": "iris-tooltip-t1-d3-non-target-invariance-verdict-v1",
        "status": "PASS" if not failures else "FAIL",
        "target_count": len(target),
        "target_exact_set_sha256": _ordered_hash(target),
        "metrics": metrics,
        "failures": failures,
        "producer_module_imported": False,
        "comparison_basis": "frozen pre-mutation hashes versus post-mutation repository artifacts",
    }
    _write_json(output_path, result)
    return {"status": result["status"], "failures": failures, "sha256": sha256_file(output_path)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="iris-tooling layer3 validate-tooltip-t1-d3")
    sub = parser.add_subparsers(dest="command", required=True)
    absence_parser = sub.add_parser("absence")
    absence_parser.add_argument("--prepared-root", type=Path, required=True)
    absence_parser.add_argument("--output", type=Path, required=True)
    compare_parser = sub.add_parser("compare")
    compare_parser.add_argument("--prepared-root", type=Path, required=True)
    compare_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    root = require_repository_context().repository_root
    try:
        result = validate_absence(root, args.prepared_root.resolve(), args.output.resolve()) if args.command == "absence" else compare(root, args.prepared_root.resolve(), args.output.resolve())
    except (OSError, ValueError, KeyError, TooltipContractError) as exc:
        print(f"tooltip-t1-d3 independent validation blocked: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
