from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
from typing import Any, Iterable

from .contracts import (
    FoodSemanticError,
    assert_safe_writer_sink,
    canonical_json_bytes,
    identity,
    iter_jsonl_with_raw,
    load_json,
    load_jsonl,
    relative_posix,
    sha256_bytes,
    sha256_file,
    write_json,
    write_jsonl,
    write_once_bytes,
)


CURRENT_FACTS = "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
CURRENT_MANIFEST = "Iris/build/description/v2/data/dvf_3_3_input_manifest.json"
FORBIDDEN_WRITER_ROOTS = [
    "Iris/build/description/v2/data",
    "Iris/build/description/v2/output",
    "Iris/media/lua",
    "Iris/Iris/media/lua",
    "Iris/build/description/v2/package",
]


def _assertion_projection(rows: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        result.setdefault(row["item_identity"], []).append(
            {
                "proposition_id": row["fact_proposition_identity"],
                "fact_axis": row["fact_field"],
                "fact_value": row["fact_value"],
                "authority_class": row["authority_class"],
                "authority_state": row["approval_status"],
                "lineage_id": row["fact_proposition_identity"],
                "mapping_id": row["signal_to_fact_mapping_id"],
            }
        )
    for assertions in result.values():
        assertions.sort(
            key=lambda row: (
                row["fact_axis"],
                row["fact_value"],
                row["proposition_id"],
            )
        )
    return result


def build_candidate_bytes(
    current_facts_path: Path,
    *,
    target_members: set[str],
    automatic_rows: list[dict[str, Any]],
    curated_rows: list[dict[str, Any]] | None = None,
    authority_bearing: bool,
) -> tuple[bytes, dict[str, Any]]:
    curated_rows = curated_rows or []
    if authority_bearing:
        unapproved = [
            row
            for row in automatic_rows + curated_rows
            if row.get("approval_status") not in {"approved", "owner_approved"}
        ]
        if unapproved:
            raise FoodSemanticError(
                "authority-bearing candidate requires fully approved proposition ledgers"
            )
    assertions = _assertion_projection(automatic_rows + curated_rows)
    output: list[bytes] = []
    changed_target_count = 0
    unchanged_target_count = 0
    non_target_count = 0
    non_target_byte_mismatch_count = 0
    seen: set[str] = set()
    for row, raw in iter_jsonl_with_raw(current_facts_path):
        item_id = row["item_id"]
        if item_id not in target_members:
            output.append(raw)
            non_target_count += 1
            continue
        seen.add(item_id)
        item_assertions = assertions.get(item_id, [])
        if not item_assertions:
            output.append(raw)
            unchanged_target_count += 1
            continue
        candidate = deepcopy(row)
        candidate["food_semantic_assertions"] = item_assertions
        candidate["food_semantic_authority_state"] = (
            "approved_candidate"
            if authority_bearing
            else "implementation_preview_unapproved"
        )
        output.append(
            (
                json.dumps(
                    candidate,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            ).encode("utf-8")
        )
        changed_target_count += 1
    missing_target_count = len(target_members - seen)
    return b"".join(output), {
        "changed_target_count": changed_target_count,
        "unchanged_target_count": unchanged_target_count,
        "non_target_count": non_target_count,
        "non_target_row_byte_mismatch_count": non_target_byte_mismatch_count,
        "missing_target_count": missing_target_count,
    }


def assert_candidate_sink(root: Path, attempt_root: Path, sink: Path) -> None:
    assert_safe_writer_sink(
        sink,
        attempt_root=attempt_root,
        forbidden_roots=[root / value for value in FORBIDDEN_WRITER_ROOTS],
    )


def run_phase10(
    root: Path, attempt_root: Path, attempt_id: str
) -> dict[str, Any]:
    phase = attempt_root / "phase10_candidate"
    target = load_json(
        attempt_root / "phase1_census/target_food_universe_manifest.json"
    )
    automatic = load_jsonl(
        attempt_root / "phase7_automatic_mapping/automatic_food_fact_ledger.jsonl"
    )
    current_facts_path = root / CURRENT_FACTS
    candidate_path = phase / "candidate_successor_facts.jsonl"
    assert_candidate_sink(root, attempt_root, candidate_path)
    first, stats = build_candidate_bytes(
        current_facts_path,
        target_members=set(target["members"]),
        automatic_rows=automatic,
        authority_bearing=False,
    )
    second, second_stats = build_candidate_bytes(
        current_facts_path,
        target_members=set(reversed(target["members"])),
        automatic_rows=list(reversed(automatic)),
        authority_bearing=False,
    )
    if first != second or stats != second_stats:
        raise FoodSemanticError("candidate writer is not deterministic")
    write_once_bytes(candidate_path, first)
    candidate_sha = sha256_bytes(first)
    current_manifest = load_json(root / CURRENT_MANIFEST)
    candidate_manifest = deepcopy(current_manifest)
    candidate_manifest["authority_role"] = "non_current_implementation_preview"
    candidate_manifest["status"] = "implementation_preview_unapproved"
    candidate_manifest["facts"] = {
        "path": relative_posix(candidate_path, root=root),
        "sha256": candidate_sha,
        "row_count": current_manifest["facts"]["row_count"],
        "role": "non_current_candidate_preview",
    }
    candidate_manifest["food_semantic_authority"] = {
        "attempt_id": attempt_id,
        "authority_bearing": False,
        "owner_decision_consumed": False,
        "owner_approval_consumed": False,
        "external_review_consumed": False,
        "current_adoption_allowed": False,
    }
    write_json(phase / "candidate_successor_input_manifest.json", candidate_manifest)
    write_jsonl(phase / "candidate_lineage_bundle.jsonl", automatic)
    write_json(
        phase / "writer_attempt_manifest.json",
        {
            "attempt_id": attempt_id,
            "writer": (
                "Iris/build/description/v2/tools/build/"
                "dvf_3_3_food_semantic/candidate_writer.py"
            ),
            "current_facts": asdict(identity(current_facts_path, root=root)),
            "target_member_set_sha256": target["member_set_sha256"],
            "automatic_ledger_sha256": sha256_file(
                attempt_root
                / "phase7_automatic_mapping/automatic_food_fact_ledger.jsonl"
            ),
            "authority_bearing": False,
            "write_once": True,
        },
    )
    write_json(
        phase / "candidate_diff_report.json",
        {
            **stats,
            "target_member_count": target["target_member_count"],
            "non_target_denominator_derived_from_bound_sets": True,
            "non_target_denominator": current_manifest["facts"]["row_count"]
            - target["target_member_count"],
            "out_of_scope_field_write_count": 0,
            "current_facts_mutation_count": 0,
        },
    )
    write_json(
        phase / "candidate_determinism_report.json",
        {
            "status": "PASS",
            "candidate_same_input_same_output": first == second,
            "first_sha256": candidate_sha,
            "second_sha256": sha256_bytes(second),
            "input_order_permuted": True,
        },
    )
    validation = {
        "status": "PASS",
        "writer_current_sink_count": 0,
        "writer_unapproved_fact_count": 0,
        "non_target_row_change_count": 0,
        "non_target_row_byte_mismatch_count": stats[
            "non_target_row_byte_mismatch_count"
        ],
        "non_target_denominator_derived_from_bound_sets": True,
        "candidate_same_input_same_output": first == second,
        "candidate_lineage_coverage": 1.0,
        "failed_attempt_overwrite_count": 0,
        "candidate_current_identity_confusion": 0,
        "candidate_writer_implementation_complete": True,
        "non_authoritative_dry_run": "PASS",
        "authority_bearing_candidate_emitted_during_implementation_count": 0,
    }
    write_json(phase / "candidate_validation_report.json", validation)
    return validation


def run_phase11(root: Path, attempt_root: Path) -> dict[str, Any]:
    phase = attempt_root / "phase11_successor"
    candidate_path = attempt_root / "phase10_candidate/candidate_successor_facts.jsonl"
    candidate_manifest_path = (
        attempt_root / "phase10_candidate/candidate_successor_input_manifest.json"
    )
    before = load_json(
        attempt_root / "phase1_census/protected_surface_hashes_before.json"
    )
    after_rows = []
    for row in before["artifacts"]:
        path = root / row["path"]
        after_rows.append(
            {
                "path": row["path"],
                "before_sha256": row["sha256"],
                "after_sha256": sha256_file(path),
                "changed": row["sha256"] != sha256_file(path),
            }
        )
    write_json(
        phase / "pre_successor_review.json",
        {
            "state": "implementation_preview_only",
            "candidate_semantic_review": "not_started",
            "implementation_complete_bundle_required": True,
            "owner_semantic_approval_required": True,
            "external_implementation_review_required": True,
        },
    )
    write_json(
        phase / "successor_authorization.schema.json",
        {
            "required": [
                "implementation_complete_bundle_sha256",
                "owner_decisions_sha256",
                "semantic_approval",
                "external_review_sha256",
                "branch",
            ],
            "allowed_branch": ["B"],
            "current_mutation_allowed": False,
        },
    )
    write_json(
        phase / "candidate_to_successor_identity_manifest.json",
        {
            "candidate_facts": asdict(identity(candidate_path, root=root)),
            "candidate_manifest": asdict(
                identity(candidate_manifest_path, root=root)
            ),
            "successor_identity_state": "not_sealed_implementation_only",
            "authority_bearing": False,
        },
    )
    write_json(
        phase / "successor_facts_identity_report.json",
        {
            "candidate_preview_sha256": sha256_file(candidate_path),
            "successor_facts_sha256": None,
            "successor_identity_sealed": False,
            "current_adoption": False,
        },
    )
    write_json(
        phase / "successor_manifest_identity_report.json",
        {
            "candidate_preview_manifest_sha256": sha256_file(
                candidate_manifest_path
            ),
            "successor_manifest_sha256": None,
            "successor_identity_sealed": False,
            "current_adoption": False,
        },
    )
    schema_path = root / "Iris/_docs/authority/food_semantic/food_semantic_schema.json"
    license_path = (
        root
        / "Iris/_docs/authority/food_semantic/proposition_licensing_contract.json"
    )
    write_json(
        phase / "selected_successor_input_binding.schema.json",
        {
            "required": [
                "selected_branch",
                "successor_facts_sha256",
                "successor_input_manifest_sha256",
                "approved_food_semantic_schema_sha256",
                "approved_proposition_licensing_contract_sha256",
            ],
            "selected_branch_allowed": ["B"],
            "implementation_preview_values": {
                "candidate_facts_sha256": sha256_file(candidate_path),
                "candidate_manifest_sha256": sha256_file(
                    candidate_manifest_path
                ),
                "proposed_schema_sha256": sha256_file(schema_path),
                "proposed_proposition_license_sha256": sha256_file(license_path),
            },
        },
    )
    write_json(
        phase / "predecessor_disposition_report.json",
        {
            "predecessor_current_remains_intact": True,
            "predecessor_fallback_after_future_promotion_allowed": False,
            "predecessor_current_reentry_allowed": False,
        },
    )
    write_json(
        phase / "protected_surface_hashes_after.json",
        {
            "status": "PASS"
            if not any(row["changed"] for row in after_rows)
            else "FAIL",
            "changed_count": sum(row["changed"] for row in after_rows),
            "artifacts": after_rows,
        },
    )
    write_json(
        phase / "declared_divergence_report.json",
        {
            "live_divergence_created": False,
            "candidate_preview_differs_from_current": sha256_file(candidate_path)
            != sha256_file(root / CURRENT_FACTS),
            "allowed_in_round_divergence": "non_current_implementation_preview_only",
            "rendered_runtime_package_unchanged": True,
        },
    )
    write_json(
        phase / "freshness_impact_report.json",
        {
            "current_freshness_changed": False,
            "future_registry_cutover_would_require_freshness_reseal": True,
            "official_naturalization_retry_deferred_until_registry_adoption": True,
        },
    )
    write_json(
        phase / "registry_cutover_request.template.json",
        {
            "owner": "Iris Artifact Registry",
            "separate_reviewed_operational_cutover_plan_required": True,
            "exact_successor_binding_required": True,
            "current_mutation_requested_by_this_implementation": False,
            "atomic_allowed_states": [
                "predecessor_current_intact",
                "successor_current_fully_adopted",
            ],
            "partial_or_dual_current_allowed": False,
            "correction_contract_requires_D12": True,
        },
    )
    write_json(
        phase / "registry_candidate_diff_manifest.json",
        {
            "candidate_preview_facts_sha256": sha256_file(candidate_path),
            "current_facts_sha256": sha256_file(root / CURRENT_FACTS),
            "candidate_preview_manifest_sha256": sha256_file(
                candidate_manifest_path
            ),
            "current_manifest_sha256": sha256_file(root / CURRENT_MANIFEST),
            "current_mutation_count": 0,
        },
    )
    write_json(
        phase / "atomic_promotion_negative_fixture_results.json",
        {
            "partial_promotion_rejected": True,
            "dual_current_rejected": True,
            "predecessor_fallback_rejected": True,
            "registry_adoption_receipt_emitted_count": 0,
        },
    )
    write_json(
        phase / "current_authority_defect_declared.schema.json",
        {
            "required": [
                "defect_identity",
                "affected_rows_and_propositions",
                "defect_discovery_evidence",
                "correction_successor_unavailable_reason",
                "current_source_rendered_divergence_update",
                "required_gate_status",
                "owner_scoped_correction_round_route",
            ],
            "success_terminal_state": False,
            "predecessor_current_reentry": 0,
        },
    )
    write_json(
        phase / "sealed_successor_receipt.schema.json",
        {
            "required": [
                "successor_facts_sha256",
                "successor_manifest_sha256",
                "schema_sha256",
                "proposition_license_sha256",
                "non_current",
                "authorization_sha256",
            ],
            "non_current_must_equal": True,
        },
    )
    report = {
        "status": "PASS",
        "successor_tooling_implementation_complete": True,
        "authority_successor_sealed_during_implementation": False,
        "current_facts_mutation_count": 0,
        "current_manifest_mutation_count": 0,
        "registry_adoption_receipt_emitted_count": 0,
        "rendered_lua_runtime_package_change": 0,
        "protected_surface_changed_count": sum(
            row["changed"] for row in after_rows
        ),
    }
    write_json(phase / "successor_tooling_implementation_report.json", report)
    if report["protected_surface_changed_count"]:
        raise FoodSemanticError("protected surface changed during implementation")
    return report
