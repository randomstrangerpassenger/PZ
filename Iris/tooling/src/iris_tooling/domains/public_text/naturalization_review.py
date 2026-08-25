from __future__ import annotations

from .naturalization_transformation import *  # noqa: F401,F403

def select_rank(
    candidate_hash: str,
    stratum_id: str,
    item_id: str,
) -> str:
    return select_candidate_rank(candidate_hash, stratum_id, item_id)


def evaluate_human_review_decision(
    *,
    decision: dict[str, Any],
    candidate_hash: str,
    selected_ordered_digest: str,
    ordered_selected: list[str],
) -> tuple[int, list[str]]:
    return evaluate_review_decision(
        decision=decision,
        candidate_hash=candidate_hash,
        selected_ordered_digest=selected_ordered_digest,
        ordered_selected=ordered_selected,
    )

def build_phase7(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    p4 = phase_root(attempt_root, 4)
    p5 = phase_root(attempt_root, 5)
    p6 = phase_root(attempt_root, 6)
    require_files(
        (
            p4 / "candidate_rendered.json",
            p5 / "structural_satisfaction_ledger.jsonl",
            p6 / "raw_detector_hit_ledger.jsonl",
        )
    )
    root = phase_root(attempt_root, 7)
    root.mkdir(parents=True, exist_ok=True)
    candidate_hash = sha256_file(p4 / "candidate_rendered.json")
    candidate = load_json(p4 / "candidate_rendered.json")
    eligible = {
        item_id: entry
        for item_id, entry in candidate["entries"].items()
        if entry.get("source") == "korean_prose_candidate_v1"
    }
    foundation = load_json(FOUNDATION_CONTRACT)
    contract = foundation["human_review_selection_contract"]
    base = contract["base_sample"]
    base_size = math.ceil(
        len(eligible)
        * int(base["ratio"]["numerator"])
        / int(base["ratio"]["denominator"])
    )
    base_size = max(int(base["minimum_rows"]), base_size)
    base_size = min(int(base["maximum_rows"]), base_size, len(eligible))
    selected: set[str] = set(
        sorted(
            eligible,
            key=lambda item_id: select_rank(
                candidate_hash,
                "base",
                item_id,
            ),
        )[:base_size]
    )
    strata: dict[str, set[str]] = defaultdict(set)
    for item_id, entry in eligible.items():
        strata[f"resolved_profile:{entry['resolved_profile']}"].add(item_id)
    structural = load_jsonl(p5 / "structural_satisfaction_ledger.jsonl")
    for row in structural:
        if row.get("status") in {
            "satisfied_by_verified_fusion",
            "satisfied_by_verified_suppression",
        }:
            strata["structural_fusion_or_suppression:present"].add(
                str(row["item_id"])
            )
    for row in load_jsonl(p6 / "raw_detector_hit_ledger.jsonl"):
        if row.get("hit") is True:
            strata[f"raw_detector_id:{row['detector_id']}"].add(str(row["item_id"]))
    stratum_selections: list[dict[str, Any]] = []
    for stratum_id in sorted(strata):
        minimum = (
            16
            if stratum_id.startswith("structural_fusion_or_suppression")
            else 8
        )
        members = sorted(
            strata[stratum_id],
            key=lambda item_id: select_rank(
                candidate_hash,
                stratum_id,
                item_id,
            ),
        )
        picked = members[: min(minimum, len(members))]
        selected.update(picked)
        stratum_selections.append(
            {
                "stratum_id": stratum_id,
                "eligible_count": len(members),
                "minimum_rows_per_nonempty_stratum": minimum,
                "selected_item_ids": picked,
            }
        )
    minimum_selected = sorted(
        selected,
        key=lambda item_id: select_rank(candidate_hash, "final_union", item_id),
    )
    ordered_selected = sorted(
        eligible,
        key=lambda item_id: select_rank(candidate_hash, "final_union", item_id),
    )
    manifest = {
        "schema_version": "dvf-3-3-human-review-sample-manifest-v2",
        "naturalization_attempt_id": attempt_id,
        "candidate_rendered_hash": candidate_hash,
        "selection_scope": "full_candidate_review_owner_directive",
        "selection_algorithm_id": contract["algorithm_id"],
        "selection_algorithm_hash": foundation[
            "human_review_selection_contract_hash"
        ],
        "required_review_denominator_id": contract["required_denominator_id"],
        "full_candidate_denominator": len(eligible),
        "eligible_review_denominator": len(eligible),
        "base_selected_denominator": base_size,
        "minimum_contract_selected_denominator": len(minimum_selected),
        "minimum_contract_selected_item_ids": minimum_selected,
        "minimum_contract_selected_ordered_digest": canonical_hash(
            minimum_selected
        ),
        "selected_required_denominator": len(ordered_selected),
        "selected_item_ids": ordered_selected,
        "selected_ordered_digest": canonical_hash(ordered_selected),
        "stratum_selections": stratum_selections,
        "corpus_wide_human_only_blocker_zero_claimed": False,
    }
    write_once_or_same(root / "human_review_sample_manifest.json", manifest)
    decision_present = HUMAN_REVIEW_DECISION_PATH.is_file()
    binding_status = "blocked_human_review_required"
    blocker_count: int | None = None
    decision_hash: str | None = None
    errors: list[str] = []
    if decision_present:
        decision = load_json(HUMAN_REVIEW_DECISION_PATH)
        decision_hash = sha256_file(HUMAN_REVIEW_DECISION_PATH)
        blocker_count, errors = evaluate_human_review_decision(
            decision=decision,
            candidate_hash=candidate_hash,
            selected_ordered_digest=manifest["selected_ordered_digest"],
            ordered_selected=ordered_selected,
        )
        if not errors:
            binding_status = "PASS" if blocker_count == 0 else "FAIL"
    binding = {
        "schema_version": "dvf-3-3-human-review-binding-report-v1",
        "status": binding_status,
        "candidate_rendered_hash": candidate_hash,
        "human_review_decision_path": repo_relative(HUMAN_REVIEW_DECISION_PATH),
        "human_review_decision_present": decision_present,
        "human_review_decision_hash": decision_hash,
        "human_review_decision_mode": (
            load_json(HUMAN_REVIEW_DECISION_PATH).get("decision_mode")
            if decision_present
            else None
        ),
        "required_review_denominator": len(ordered_selected),
        "expanded_review_row_count": (
            len(ordered_selected) if decision_present and not errors else None
        ),
        "human_review_blocker_count_within_required_denominator": blocker_count,
        "errors": errors,
        "corpus_wide_human_only_blocker_zero_claimed": (
            decision_present
            and not errors
            and blocker_count == 0
            and len(ordered_selected) == len(eligible)
        ),
    }
    write_once_or_same(root / "human_review_binding_report.json", binding)
    eligibility = {
        "schema_version": "dvf-3-3-human-review-eligibility-report-v1",
        "status": binding_status,
        "reviewer_identity_present": (
            decision_present
            and isinstance(load_json(HUMAN_REVIEW_DECISION_PATH).get("reviewer_id"), str)
        ),
        "reviewer_is_not_compiler": (
            decision_present
            and load_json(HUMAN_REVIEW_DECISION_PATH).get("reviewer_role")
            in {"human_public_text_reviewer", "external_codex_reviewer"}
        ),
        "full_candidate_review": len(ordered_selected) == len(eligible),
        "independent_terminal_reviewer_claimed": False,
    }
    write_once_or_same(root / "human_review_eligibility_report.json", eligibility)
    return binding

__all__ = [
    name for name in globals() if not name.startswith("__")
]
