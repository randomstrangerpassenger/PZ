from __future__ import annotations

import hashlib
from typing import Any


def select_rank(candidate_hash: str, stratum_id: str, item_id: str) -> str:
    return hashlib.sha256(
        (candidate_hash + "\0" + stratum_id + "\0" + item_id).encode("utf-8")
    ).hexdigest()


def evaluate_human_review_decision(
    *,
    decision: dict[str, Any],
    candidate_hash: str,
    selected_ordered_digest: str,
    ordered_selected: list[str],
) -> tuple[int, list[str]]:
    errors: list[str] = []
    if decision.get("candidate_rendered_hash") != candidate_hash:
        errors.append("stale_candidate_hash")
    if decision.get("selected_ordered_digest") != selected_ordered_digest:
        errors.append("sample_digest_mismatch")
    required_fields = {
        "readability",
        "naturalness",
        "semantic_fidelity",
        "public_suitability",
    }
    if decision.get("decision_mode") == "exact_full_candidate_external_review":
        if decision.get("reviewed_denominator") != len(ordered_selected):
            errors.append("review_denominator_mismatch")
        if decision.get("reviewed_item_id_binding") != (
            "human_review_sample_manifest.selected_item_ids"
        ):
            errors.append("review_item_binding_mismatch")
        if decision.get("reviewer_role") != "external_codex_reviewer":
            errors.append("external_reviewer_role_invalid")
        if decision.get("all_unlisted_items_pass_all_rubrics") is not True:
            errors.append("full_candidate_default_disposition_missing")
        aggregates = decision.get("rubric_aggregate")
        if not isinstance(aggregates, dict) or not required_fields.issubset(aggregates):
            errors.append("review_rubric_aggregate_missing")
            aggregates = {}
        for field in required_fields:
            counts = aggregates.get(field, {})
            if not isinstance(counts, dict) or (
                counts.get("pass", 0) + counts.get("fail", 0)
                != len(ordered_selected)
            ):
                errors.append(f"review_rubric_denominator_mismatch:{field}")
        blocker_rows = decision.get("blockers")
        if not isinstance(blocker_rows, list):
            errors.append("review_blocker_rows_missing")
            blocker_rows = []
        blocker_ids: set[str] = set()
        selected = set(ordered_selected)
        for row in blocker_rows:
            if not isinstance(row, dict):
                errors.append("review_blocker_row_invalid")
                continue
            item_id = str(row.get("item_id"))
            if item_id not in selected:
                errors.append(f"review_blocker_item_not_selected:{item_id}")
            if item_id in blocker_ids:
                errors.append(f"review_blocker_item_duplicate:{item_id}")
            blocker_ids.add(item_id)
            rubric = row.get("rubric")
            if (
                not isinstance(rubric, dict)
                or not required_fields.issubset(rubric)
                or all(rubric.get(field) == "pass" for field in required_fields)
            ):
                errors.append(f"review_blocker_rubric_invalid:{item_id}")
        if {str(item) for item in decision.get("blocker_item_ids", [])} != blocker_ids:
            errors.append("review_blocker_item_binding_mismatch")
        if decision.get("blocker_count") != len(blocker_ids):
            errors.append("review_blocker_count_mismatch")
        return len(blocker_ids), errors
    if decision.get("decision_mode") == "exact_sample_uniform_owner_approval":
        if decision.get("reviewed_denominator") != len(ordered_selected):
            errors.append("review_denominator_mismatch")
        if decision.get("reviewed_item_id_binding") != (
            "human_review_sample_manifest.selected_item_ids"
        ):
            errors.append("review_item_binding_mismatch")
        uniform_review = decision.get("uniform_review")
        if not isinstance(uniform_review, dict) or not required_fields.issubset(
            uniform_review
        ):
            errors.append("review_rubric_field_missing")
            uniform_review = {}
        blocker_count = (
            len(ordered_selected)
            if any(uniform_review.get(field) != "pass" for field in required_fields)
            else 0
        )
        if decision.get("compiler_or_tool_generated_human_judgment") is not False:
            errors.append("human_judgment_origin_invalid")
        return blocker_count, errors
    rows = decision.get("reviews")
    if not isinstance(rows, list):
        errors.append("review_rows_missing")
        rows = []
    reviewed_ids = {
        str(row.get("item_id")) for row in rows if isinstance(row, dict)
    }
    if reviewed_ids != set(ordered_selected):
        errors.append("review_denominator_mismatch")
    blocker_count = 0
    for row in rows:
        if not isinstance(row, dict) or not required_fields.issubset(row):
            errors.append("review_rubric_field_missing")
            continue
        if any(row[field] != "pass" for field in required_fields):
            blocker_count += 1
    return blocker_count, errors
