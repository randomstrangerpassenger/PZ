from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from layer3_body_role_realign import (
        RoleRealignError,
        canonical_sha256,
        has_text,
        index_rows,
        load_json,
        load_jsonl,
        raw_sha256,
        repository_root_from_script,
        resolve_current_generation,
        set_sha256,
    )
else:
    from .layer3_body_role_realign import (
        RoleRealignError,
        canonical_sha256,
        has_text,
        index_rows,
        load_json,
        load_jsonl,
        raw_sha256,
        repository_root_from_script,
        resolve_current_generation,
        set_sha256,
    )


REQUIRED_FILES = (
    "phase0/input_identity_manifest.json",
    "phase0/problem1_evidence_drift_report.json",
    "phase1/item_denominator.jsonl",
    "phase1/existing_body_denominator.jsonl",
    "phase2/fact_composition_inventory.jsonl",
    "phase2/fact_kind_mapping_coverage.json",
    "phase3/body_disposition_ledger.jsonl",
    "phase3/description_readiness_ledger.jsonl",
    "phase3/review_queue.jsonl",
    "phase4/role_material_by_fulltype.jsonl",
    "phase4/acquisition_preservation_report.json",
    "phase4/acquisition_projection_ledger.jsonl",
    "phase5/successor_rendered.json",
    "phase5/current_vs_successor_delta.jsonl",
    "phase6/public_text_assessment_input.json",
    "phase6/public_text_assessment_result.json",
    "phase7/candidate_replay_determinism_report.json",
    "phase7/protected_surface_non_mutation_report.json",
    "phase8/problem_5a_candidate_set.jsonl",
    "phase8/terminal_validation_report.json",
    "phase8/tool_dependency_disposition_report.json",
    "phase8/clean_checkout_terminal_subject_binding.json",
)


def validate_subject(
    *, repository_root: Path, subject_root: Path, require_complete: bool
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    subject_root = subject_root.resolve()
    try:
        subject_root.relative_to(repository_root)
    except ValueError as exc:
        raise RoleRealignError(f"SUBJECT_ROOT_OUTSIDE_REPOSITORY: {subject_root}") from exc
    missing = [relative for relative in REQUIRED_FILES if not (subject_root / relative).is_file()]
    if missing:
        raise RoleRealignError(f"MISSING_REQUIRED_ARTIFACTS: {missing}")

    items = load_jsonl(subject_root / "phase1/item_denominator.jsonl")
    bodies = load_jsonl(subject_root / "phase1/existing_body_denominator.jsonl")
    facts = load_jsonl(subject_root / "phase2/fact_composition_inventory.jsonl")
    mapping = load_json(subject_root / "phase2/fact_kind_mapping_coverage.json")
    dispositions = load_jsonl(subject_root / "phase3/body_disposition_ledger.jsonl")
    readiness = load_jsonl(subject_root / "phase3/description_readiness_ledger.jsonl")
    reviews = load_jsonl(subject_root / "phase3/review_queue.jsonl")
    material = load_jsonl(subject_root / "phase4/role_material_by_fulltype.jsonl")
    acquisition = load_json(subject_root / "phase4/acquisition_preservation_report.json")
    successor = load_json(subject_root / "phase5/successor_rendered.json")
    assessment = load_json(subject_root / "phase6/public_text_assessment_result.json")
    replay = load_json(subject_root / "phase7/candidate_replay_determinism_report.json")
    nonmutation = load_json(subject_root / "phase7/protected_surface_non_mutation_report.json")
    problem_5a = load_jsonl(subject_root / "phase8/problem_5a_candidate_set.jsonl")
    terminal = load_json(subject_root / "phase8/terminal_validation_report.json")
    tooling = load_json(subject_root / "phase8/tool_dependency_disposition_report.json")
    terminal_binding = load_json(subject_root / "phase8/clean_checkout_terminal_subject_binding.json")
    manifest = load_json(subject_root / "phase0/input_identity_manifest.json")

    item_by_id = index_rows(items, "item_id", "ITEM_DENOMINATOR")
    body_by_id = index_rows(bodies, "item_id", "BODY_DENOMINATOR")
    disposition_by_id = index_rows(dispositions, "item_id", "DISPOSITION")
    readiness_by_id = index_rows(readiness, "item_id", "READINESS")
    material_by_id = index_rows(material, "item_id", "ROLE_MATERIAL")
    problem_by_id = index_rows(problem_5a, "item_id", "PROBLEM_5A")

    errors: list[str] = []
    if set(body_by_id) != set(disposition_by_id):
        errors.append("existing_body_disposition_set_mismatch")
    if set(item_by_id) != set(readiness_by_id):
        errors.append("item_readiness_set_mismatch")
    if set(item_by_id) != set(material_by_id):
        errors.append("item_role_material_set_mismatch")
    expected_5a = {
        item_id for item_id, row in readiness_by_id.items()
        if row.get("readiness") == "insufficient_material"
    }
    if expected_5a != set(problem_by_id):
        errors.append("problem_5a_projection_set_mismatch")
    if any(row.get("readiness") == "review_required" for row in problem_5a):
        errors.append("review_required_leaked_to_problem_5a")
    if mapping.get("unresolved_mapping_count") != 0:
        errors.append("unresolved_mapping_nonzero")
    if mapping.get("new_layer4_promotion_count") != 0:
        errors.append("new_layer4_promotion_nonzero")
    if mapping.get("semantic_rendered_string_parsing_count") != 0:
        errors.append("semantic_rendered_string_parsing_nonzero")
    if acquisition.get("source_bound_loss_count") != 0:
        errors.append("acquisition_source_bound_loss_nonzero")
    if acquisition.get("unbound_or_additional_count") != 0:
        errors.append("acquisition_unbound_or_additional_nonzero")
    if assessment.get("blocking_finding_count") != 0:
        errors.append("public_text_blocking_finding_nonzero")
    for field in (
        "acquisition_to_description_leakage_count",
        "governance_vocabulary_public_text_leakage_count",
        "unsupported_fact_count",
        "fact_strengthening_count",
        "unregistered_transform_application_count",
        "technical_failure_count",
    ):
        if assessment.get(field) != 0:
            errors.append(f"{field}_nonzero")
    if replay.get("raw_byte_mismatch_count") != 0 or replay.get("unclassified_artifact_count") != 0:
        errors.append("candidate_replay_not_exact")
    if nonmutation.get("mutation_count") != 0:
        errors.append("protected_surface_mutation_nonzero")
    if tooling.get("unresolved_or_unclassified_count") != 0:
        errors.append("unclassified_tool_dependency_nonzero")
    if terminal_binding.get("external_result_hash_count") != 0:
        errors.append("pre_run_contract_contains_result_hash")
    if any(not row.get("review_completed") for row in reviews):
        errors.append("required_review_incomplete")

    current = resolve_current_generation(repository_root)
    if manifest.get("current_generation_id") != current.generation_id:
        errors.append("current_generation_drift_after_staging")
    if manifest.get("item_denominator_count") != len(item_by_id):
        errors.append("item_denominator_manifest_count_mismatch")
    if manifest.get("item_denominator_set_sha256") != set_sha256(item_by_id):
        errors.append("item_denominator_manifest_hash_mismatch")
    if manifest.get("existing_body_denominator_count") != len(body_by_id):
        errors.append("body_denominator_manifest_count_mismatch")
    if manifest.get("existing_body_denominator_set_sha256") != set_sha256(body_by_id):
        errors.append("body_denominator_manifest_hash_mismatch")

    successor_entries = successor.get("entries", {})
    current_entries = load_json(current.rendered_path).get("entries", {})
    if set(successor_entries) != set(current_entries):
        errors.append("successor_current_entry_key_set_mismatch")
    if successor.get("meta", {}).get("entries_sha256") != canonical_sha256(successor_entries):
        errors.append("successor_entries_hash_mismatch")
    for item_id, entry in successor_entries.items():
        if entry.get("text_ko") != material_by_id[item_id].get("menu_text_ko"):
            errors.append(f"successor_material_projection_mismatch:{item_id}")
            break
    internal_tokens = ("review_hold", "review_required", "insufficient_material", "description_ready")
    if any(
        token in (entry.get("text_ko") or "")
        for entry in successor_entries.values() for token in internal_tokens
    ):
        errors.append("internal_governance_token_leakage")

    if require_complete and terminal.get("status") != "candidate_complete":
        errors.append(f"terminal_status_not_candidate_complete:{terminal.get('status')}")
    if require_complete and terminal.get("staging_candidate_complete") is not True:
        errors.append("staging_candidate_complete_false")
    if terminal.get("repository_clean_checkout_complete") is not False:
        errors.append("repository_gate_improperly_claimed_by_staging_validator")
    if terminal.get("closeout_token") is not None:
        errors.append("staging_validator_improperly_emitted_closeout_token")

    if errors:
        raise RoleRealignError("VALIDATION_FAILED: " + ";".join(errors))
    return {
        "status": "PASS",
        "subject_root": str(subject_root),
        "item_count": len(item_by_id),
        "existing_body_count": len(body_by_id),
        "fact_count": len(facts),
        "readiness_counts": dict(sorted(Counter(row["readiness"] for row in readiness).items())),
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in dispositions).items())),
        "problem_5a_count": len(problem_5a),
        "review_record_count": len(reviews),
        "successor_entries_sha256": successor["meta"]["entries_sha256"],
        "authority_effect": "none",
        "current_install_claimed": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only validation for a Layer 3 role realignment staging subject.")
    parser.add_argument("--subject-root", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, default=repository_root_from_script())
    parser.add_argument("--require-complete", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = validate_subject(
            repository_root=args.repository_root,
            subject_root=args.subject_root,
            require_complete=args.require_complete,
        )
    except RoleRealignError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
