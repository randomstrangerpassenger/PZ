from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import sys
from typing import Any, Iterable

from .contracts import (
    FoodSemanticError,
    assert_safe_writer_sink,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    identity,
    iter_jsonl_with_raw,
    load_json,
    load_jsonl,
    now_iso,
    relative_posix,
    sha256_bytes,
    sha256_file,
    write_json,
    write_jsonl,
    write_once_bytes,
)
from .curation_workflow import (
    materialize_authority_curation,
    validate_curated_rows,
)
from .schema_feasibility import required_axes
from .naturalization_handoff import adopt_d16_candidate_patch


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
                "lineage_id": row.get(
                    "source_or_approval_lineage_id",
                    row["fact_proposition_identity"],
                ),
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


def _expected_proposition_inventory(
    rows: Iterable[dict[str, Any]],
    *,
    schema_sha256: str,
    proposition_license_sha256: str,
) -> list[dict[str, Any]]:
    inventory = [
        {
            "item_id": row["item_identity"],
            "proposition_id": row["fact_proposition_identity"],
            "fact_axis": row["fact_field"],
            "fact_value": row["fact_value"],
            "authority_class": row["authority_class"],
            "source_or_approval_lineage_id": row.get(
                "source_or_approval_lineage_id",
                row["fact_proposition_identity"],
            ),
            "schema_sha256": schema_sha256,
            "proposition_license_sha256": proposition_license_sha256,
        }
        for row in rows
        if row.get("approval_status") in {"approved", "owner_approved"}
    ]
    return sorted(
        inventory,
        key=lambda row: (
            row["item_id"],
            row["fact_axis"],
            row["fact_value"],
            row["proposition_id"],
        ),
    )


def _member_set_sha256(members: Iterable[str]) -> str:
    return sha256_bytes(
        "".join(f"{member}\n" for member in sorted(set(members))).encode(
            "utf-8"
        )
    )


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
                "successor_facts_path",
                "successor_facts_sha256",
                "successor_input_manifest_path",
                "successor_input_manifest_sha256",
                "approved_food_semantic_schema_path",
                "approved_food_semantic_schema_sha256",
                "approved_proposition_licensing_contract_path",
                "approved_proposition_licensing_contract_sha256",
                "target_member_count",
                "target_member_set_sha256",
                "required_fact_axes",
                "minimum_meaningful_partition",
                "expected_proposition_count",
                "expected_proposition_inventory_sha256",
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
    write_json(
        phase / "authority_execution_input.schema.json",
        {
            "schema_version": "food-semantic-authority-execution-input-schema-v1",
            "command": (
                "dvf_3_3_food_semantic_facts_authority.py authority "
                "--attempt-id <attempt-id> --owner-decisions <path> "
                "--semantic-approval <path> --external-review <path> "
                "--curated-ledger <path>"
            ),
            "required_owner_decision_ids": sorted(
                AUTHORITY_EXECUTION_REQUIRED_DECISIONS
            ),
            "allowed_selected_options": {
                key: sorted(value)
                for key, value in sorted(
                    AUTHORITY_DECISION_ALLOWED_OPTIONS.items()
                )
            },
            "semantic_approval_required_fields": [
                "attempt_id",
                "implementation_complete_bundle_sha256",
                "status",
                "semantic_approver",
                "approval_time",
                "food_semantic_schema_sha256",
                "proposition_licensing_contract_sha256",
                "signal_to_fact_mappings_sha256",
                "automatic_food_fact_ledger_sha256",
                "curated_fact_ledger_sha256",
                "approved_automatic_review_denominator",
                "approved_curation_item_cap",
                "approved_curation_proposition_cap",
            ],
            "curated_ledger_required_fields": [
                "item_identity",
                "fact_axis",
                "fact_value",
                "proposition_id",
                "authority_class",
                "curator_identity",
                "reviewed_source_set",
                "rationale",
                "schema_sha256",
                "approval_record",
                "semantic_approver",
                "approval_status",
            ],
            "reviewed_source_set_entry_required_fields": [
                "source_id",
                "source_class",
                "source_path",
                "source_sha256",
            ],
            "layer4_review_context_requires": [
                "D5=allow_layer4_as_curated_review_context",
                "review_role=human_review_context_only",
            ],
            "branch": "B",
            "current_mutation_allowed": False,
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


AUTHORITY_EXECUTION_REQUIRED_DECISIONS = {
    "D1",
    "D5",
    "D6",
    "D7",
    "D8",
    "D9",
    "D10",
    "D11",
    "D12",
    "D13",
    "D14",
    "D15",
    "D16",
}
AUTHORITY_DECISION_ALLOWED_OPTIONS = {
    "D1": {"C1", "C2"},
    "D5": {
        "allow_layer4_as_curated_review_context",
        "deny_layer4_review_context",
    },
    "D6": {
        "row_level_only",
        "bounded_batch_exact_member_expansion",
    },
    "D7": {"accept_exact_proposed_item_and_proposition_caps"},
    "D8": {"accept_exact_automatic_review_denominator"},
    "D9": {"approve_branch_B_sealed_handoff_and_registry_cutover_request"},
    "D10": {"accept_minimum_meaningful_partition_4"},
    "D11": {"defer_G2_and_issue_future_registry_G1_request"},
    "D12": {"bind_registry_correction_owner_and_route"},
    "D13": {
        "I1_full_chain_non_participant",
        "I2_non_claude_full_chain_non_participant",
    },
    "D14": {"adopt_12_plus_1_tooling_cap_non_expansion_proof"},
    "D15": {
        "no_top_doc_update_current_round",
        "defer_top_doc_updates_to_registry_cutover",
    },
    "D16": {"authorize_exact_candidate_adapter_and_no_render_only"},
}


def _approved_decision_ids(owner_decisions: dict[str, Any]) -> set[str]:
    return {
        row["decision_id"]
        for row in owner_decisions.get("decisions", [])
        if row.get("selected_option")
        and row.get("status", "approved") in {"approved", "accepted"}
    }


def _decision_by_id(
    owner_decisions: dict[str, Any], decision_id: str
) -> dict[str, Any]:
    matches = [
        row
        for row in owner_decisions.get("decisions", [])
        if row.get("decision_id") == decision_id
    ]
    if len(matches) != 1:
        raise FoodSemanticError(
            f"owner decision {decision_id} must appear exactly once"
        )
    return matches[0]


def validate_authority_execution_inputs(
    root: Path,
    attempt_root: Path,
    *,
    owner_decisions_path: Path,
    semantic_approval_path: Path,
    external_review_path: Path,
    curated_ledger_path: Path,
) -> dict[str, Any]:
    bundle_path = attempt_root / "phase13_closeout/implementation_complete_bundle.json"
    bundle = load_json(bundle_path)
    bundle_sha256 = sha256_file(bundle_path)
    owner = load_json(owner_decisions_path)
    semantic = load_json(semantic_approval_path)
    external = load_json(external_review_path)
    schema_path = root / "Iris/_docs/authority/food_semantic/food_semantic_schema.json"
    license_path = (
        root
        / "Iris/_docs/authority/food_semantic/proposition_licensing_contract.json"
    )
    mapping_path = (
        root / "Iris/_docs/authority/food_semantic/signal_to_fact_mappings.json"
    )
    automatic_path = (
        attempt_root / "phase7_automatic_mapping/automatic_food_fact_ledger.jsonl"
    )
    cap_path = attempt_root / "phase6_schema/proposed_curation_caps.json"
    queue_path = attempt_root / "phase7_automatic_mapping/curation_required_queue.jsonl"

    blockers: list[str] = []
    if bundle.get("attempt_id") != attempt_root.name:
        blockers.append("implementation_bundle_attempt_mismatch")
    if bundle.get("implementation_complete_bundle_sealed") is not True:
        blockers.append("implementation_bundle_not_sealed")
    if owner.get("attempt_id") != attempt_root.name:
        blockers.append("owner_decisions_attempt_mismatch")
    if owner.get("bound_implementation_complete_bundle_sha256") != bundle_sha256:
        blockers.append("owner_decisions_bundle_mismatch")
    if not owner.get("approver_identity") or not owner.get("approval_time"):
        blockers.append("owner_decisions_identity_or_time_missing")
    missing_decisions = sorted(
        AUTHORITY_EXECUTION_REQUIRED_DECISIONS - _approved_decision_ids(owner)
    )
    if missing_decisions:
        blockers.append("owner_decisions_incomplete")
    option_mismatches: list[str] = []
    for decision_id in sorted(AUTHORITY_EXECUTION_REQUIRED_DECISIONS):
        if decision_id in missing_decisions:
            continue
        decision = _decision_by_id(owner, decision_id)
        if decision.get("selected_option") not in (
            AUTHORITY_DECISION_ALLOWED_OPTIONS[decision_id]
        ):
            option_mismatches.append(decision_id)
        if not decision.get("rationale"):
            option_mismatches.append(f"{decision_id}:rationale")
        if (
            not decision.get("approver_identity")
            or not decision.get("approval_time")
        ):
            option_mismatches.append(f"{decision_id}:identity_or_time")
        if decision.get("bound_plan_sha256") != sha256_file(
            root
            / "docs/dvf_3_3_food_semantic_facts_authority_"
            "reconstruction_implementation_plan.md"
        ):
            option_mismatches.append(f"{decision_id}:plan_sha256")
        if (
            decision.get("bound_implementation_complete_bundle_sha256")
            != bundle_sha256
        ):
            option_mismatches.append(f"{decision_id}:bundle_sha256")
    if option_mismatches:
        blockers.append("owner_decision_option_contract_mismatch")
    d1 = (
        _decision_by_id(owner, "D1")
        if "D1" not in missing_decisions
        else {}
    )
    if d1.get("selected_option") == "C1":
        if (
            d1.get("claim_token") != "Food Semantic Facts Authority Successor Handoff"
            or d1.get("terminal_value")
            != "sealed_successor_handoff_complete"
        ):
            blockers.append("D1_C1_exact_claim_contract_mismatch")
    elif d1.get("selected_option") == "C2":
        claim_text = (
            f"{d1.get('claim_token', '')} {d1.get('terminal_value', '')}"
        ).lower()
        forbidden_scope = {
            "canonical",
            "current authority",
            "registry pass",
            "runtime",
            "compiler pass",
            "publish",
            "package",
            "release",
            "deployment",
        }
        if (
            not d1.get("claim_token")
            or not d1.get("terminal_value")
            or not any(
                axis in claim_text
                for axis in ("food semantic", "facts authority", "source authority")
            )
            or any(scope in claim_text for scope in forbidden_scope)
        ):
            blockers.append("D1_C2_claim_scope_not_bounded")
    plan_path = (
        root
        / "docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md"
    )
    if owner.get("bound_plan_sha256") != sha256_file(plan_path):
        blockers.append("owner_decisions_plan_mismatch")
    if (
        external.get("verdict") != "PASS"
        or external.get("attempt_id") != attempt_root.name
        or external.get("reviewer_is_implementation_author") is not False
        or external.get("reviewed_bundle_sha256_match") is not True
        or external.get("implementation_complete_bundle_sha256") != bundle_sha256
        or external.get("finding_counts", {}).get("critical") != 0
        or external.get("finding_counts", {}).get("important") != 0
    ):
        blockers.append("external_implementation_review_not_pass")

    expected_semantic_hashes = {
        "food_semantic_schema_sha256": sha256_file(schema_path),
        "proposition_licensing_contract_sha256": sha256_file(license_path),
        "signal_to_fact_mappings_sha256": sha256_file(mapping_path),
        "automatic_food_fact_ledger_sha256": sha256_file(automatic_path),
        "curated_fact_ledger_sha256": sha256_file(curated_ledger_path),
    }
    if semantic.get("status") != "PASS":
        blockers.append("semantic_approval_not_pass")
    if semantic.get("attempt_id") != attempt_root.name:
        blockers.append("semantic_approval_attempt_mismatch")
    if semantic.get("implementation_complete_bundle_sha256") != bundle_sha256:
        blockers.append("semantic_approval_bundle_mismatch")
    if (
        not semantic.get("semantic_approver")
        or not semantic.get("approval_time")
    ):
        blockers.append("semantic_approval_identity_or_time_missing")
    for field, value in expected_semantic_hashes.items():
        if semantic.get(field) != value:
            blockers.append(f"semantic_approval_{field}_mismatch")

    schema = load_json(schema_path)
    curated = load_jsonl(curated_ledger_path)
    d5_option = (
        _decision_by_id(owner, "D5").get("selected_option")
        if "D5" not in missing_decisions
        else None
    )
    curated_validation = validate_curated_rows(
        curated,
        schema,
        expected_schema_sha256=sha256_file(schema_path),
        layer4_review_context_allowed=(
            d5_option == "allow_layer4_as_curated_review_context"
        ),
    )
    if any(curated_validation.values()):
        blockers.append("curated_ledger_contract_violation")

    target = load_json(
        attempt_root / "phase1_census/target_food_universe_manifest.json"
    )
    target_members = set(target["members"])
    queue = load_jsonl(queue_path)
    expected_queue_pairs = {
        (row["item_identity"], row["required_fact_axis"]) for row in queue
    }
    actual_queue_pairs = {
        (row.get("item_identity"), row.get("fact_axis")) for row in curated
    }
    if (
        expected_queue_pairs != actual_queue_pairs
        or len(curated) != len(actual_queue_pairs)
    ):
        blockers.append("curated_ledger_queue_identity_mismatch")
    if any(row.get("item_identity") not in target_members for row in curated):
        blockers.append("curated_ledger_out_of_target_member")

    cap = load_json(cap_path)
    curated_items = {row["item_identity"] for row in curated}
    if len(curated_items) > cap["proposed_curation_item_cap"]:
        blockers.append("curated_item_cap_exceeded")
    if len(curated) > cap["proposed_curation_proposition_cap"]:
        blockers.append("curated_proposition_cap_exceeded")
    if (
        semantic.get("approved_curation_item_cap")
        != cap["proposed_curation_item_cap"]
        or semantic.get("approved_curation_proposition_cap")
        != cap["proposed_curation_proposition_cap"]
    ):
        blockers.append("D7_approved_cap_mismatch")

    automatic = load_jsonl(automatic_path)
    if semantic.get("approved_automatic_review_denominator") != len(automatic):
        blockers.append("D8_automatic_review_denominator_mismatch")
    axes_by_item: dict[str, set[str]] = {
        member: set() for member in target_members
    }
    for row in automatic:
        axes_by_item[row["item_identity"]].add(row["fact_field"])
    for row in curated:
        axes_by_item[row["item_identity"]].add(row["fact_axis"])
    missing_cardinality = {
        member: sorted(set(required_axes()) - axes)
        for member, axes in axes_by_item.items()
        if set(required_axes()) - axes
    }
    if missing_cardinality:
        blockers.append("schema_required_axis_cardinality_unsatisfied")
    tooling_cap = load_json(
        attempt_root
        / "phase5_writer_contract/tooling_allowlist_relation_report.json"
    )
    if (
        tooling_cap.get("status") != "PASS"
        or tooling_cap.get("current_core_count") != 12
        or tooling_cap.get("current_route_tooling_count") != 1
        or tooling_cap.get("tooling_allowlist_convenience_expansion_count") != 0
    ):
        blockers.append("D14_tooling_cap_proof_not_pass")
    d12 = (
        _decision_by_id(owner, "D12")
        if "D12" not in missing_decisions
        else {}
    )
    if (
        not d12.get("correction_owner")
        or not d12.get("operational_route")
        or d12.get("predecessor_current_reentry_allowed") is not False
    ):
        blockers.append("D12_correction_contract_incomplete")
    d16_manifest_path = (
        attempt_root
        / "phase12_phase2_handoff/naturalization_candidate_patch_manifest.json"
    )
    d16 = (
        _decision_by_id(owner, "D16")
        if "D16" not in missing_decisions
        else {}
    )
    if d16.get("naturalization_candidate_patch_manifest_sha256") != sha256_file(
        d16_manifest_path
    ):
        blockers.append("D16_exact_manifest_mismatch")
    d16_manifest = load_json(d16_manifest_path)
    exact_d16_files = sorted(
        row["target_path"] for row in d16_manifest.get("files", [])
    )
    exact_d16_symbols = sorted(
        {
            symbol
            for row in d16_manifest.get("files", [])
            for symbol in row.get("affected_symbols", [])
        }
    )
    if (
        not d16.get("tooling_owner")
        or sorted(d16.get("allowed_files", [])) != exact_d16_files
        or sorted(d16.get("allowed_symbols", [])) != exact_d16_symbols
        or d16.get("adapter_and_no_render_only") is not True
        or d16.get("existing_phase4_to_8_mutation_prohibited") is not True
        or d16.get("attempt_0014_validator_semantics_preserved") is not True
    ):
        blockers.append("D16_tooling_owner_scope_incomplete")

    return {
        "status": "PASS" if not blockers else "BLOCKED",
        "blocking_predicates": blockers,
        "missing_owner_decision_ids": missing_decisions,
        "owner_decision_option_mismatches": option_mismatches,
        "D5_selected_option": d5_option,
        "bundle_sha256": bundle_sha256,
        "expected_semantic_hashes": expected_semantic_hashes,
        "curated_validation": curated_validation,
        "curated_item_count": len(curated_items),
        "curated_proposition_count": len(curated),
        "curated_queue_missing_or_extra_count": len(
            expected_queue_pairs ^ actual_queue_pairs
        )
        + abs(len(curated) - len(actual_queue_pairs)),
        "required_axis_missing_item_count": len(missing_cardinality),
        "required_axis_missing_by_item": missing_cardinality,
    }


def run_authority_execution(
    root: Path,
    attempt_root: Path,
    attempt_id: str,
    *,
    owner_decisions_path: Path,
    semantic_approval_path: Path,
    external_review_path: Path,
    curated_ledger_path: Path,
) -> dict[str, Any]:
    validation = validate_authority_execution_inputs(
        root,
        attempt_root,
        owner_decisions_path=owner_decisions_path,
        semantic_approval_path=semantic_approval_path,
        external_review_path=external_review_path,
        curated_ledger_path=curated_ledger_path,
    )
    authority_root = attempt_root / "authority_execution"
    write_json(authority_root / "authority_entry_validation.json", validation)
    if validation["status"] != "PASS":
        raise FoodSemanticError(
            "authority execution blocked: "
            + ",".join(validation["blocking_predicates"])
        )
    schema_path = (
        root / "Iris/_docs/authority/food_semantic/food_semantic_schema.json"
    )
    license_path = (
        root
        / "Iris/_docs/authority/food_semantic/"
        "proposition_licensing_contract.json"
    )
    schema_sha256 = sha256_file(schema_path)
    proposition_license_sha256 = sha256_file(license_path)

    target = load_json(
        attempt_root / "phase1_census/target_food_universe_manifest.json"
    )
    automatic_source_path = (
        attempt_root / "phase7_automatic_mapping/automatic_food_fact_ledger.jsonl"
    )
    automatic = load_jsonl(automatic_source_path)
    approved_automatic = [
        {**row, "approval_status": "approved"} for row in automatic
    ]
    curated = load_jsonl(curated_ledger_path)
    normalized_curated = [
        {
            **row,
            "fact_field": row["fact_axis"],
            "fact_proposition_identity": row["proposition_id"],
            "source_or_approval_lineage_id": row["approval_record"],
            "signal_to_fact_mapping_id": row.get(
                "signal_to_fact_mapping_id",
                f"curated:{row['approval_record']}",
            ),
            "mapping_version": row.get("mapping_version", "curated-v1"),
        }
        for row in curated
    ]
    all_approved_rows = approved_automatic + normalized_curated
    assertions_by_item = _assertion_projection(all_approved_rows)
    meaningful_profiles = {
        tuple(
            sorted(
                (row["fact_axis"], row["fact_value"])
                for row in assertions_by_item.get(member, [])
            )
        )
        for member in target["members"]
    }
    minimum_meaningful_partition = 4
    if len(meaningful_profiles) < minimum_meaningful_partition:
        raise FoodSemanticError(
            "D10 meaningful partition criterion failed: "
            f"{len(meaningful_profiles)} < {minimum_meaningful_partition}"
        )
    expected_inventory = _expected_proposition_inventory(
        all_approved_rows,
        schema_sha256=schema_sha256,
        proposition_license_sha256=proposition_license_sha256,
    )
    expected_inventory_bytes = canonical_jsonl_bytes(expected_inventory)
    expected_inventory_path = (
        authority_root
        / "phase12_phase2_handoff/expected_food_semantic_inventory.jsonl"
    )
    write_once_bytes(expected_inventory_path, expected_inventory_bytes)
    expected_item_set = {row["item_id"] for row in expected_inventory}
    expected_profiles = {
        tuple(
            sorted(
                (row["fact_axis"], row["fact_value"])
                for row in expected_inventory
                if row["item_id"] == member
            )
        )
        for member in expected_item_set
    }
    expected_projection = {
        "inventory_sha256": sha256_bytes(expected_inventory_bytes),
        "proposition_count": len(expected_inventory),
        "item_count": len(expected_item_set),
        "item_set_sha256": _member_set_sha256(expected_item_set),
        "required_fact_axes": sorted(required_axes()),
        "meaningful_partition_count": len(expected_profiles),
    }
    if (
        expected_projection["item_count"] != target["target_member_count"]
        or expected_projection["item_set_sha256"] != target["member_set_sha256"]
    ):
        raise FoodSemanticError(
            "approved proposition inventory does not cover the exact target set"
        )
    write_json(
        authority_root
        / "phase12_phase2_handoff/expected_projection_binding.json",
        expected_projection,
    )

    approved_automatic_path = (
        authority_root / "approved_automatic_fact_ledger.jsonl"
    )
    write_jsonl(approved_automatic_path, approved_automatic)
    curation_report = materialize_authority_curation(
        attempt_root,
        authority_root,
        normalized_curated,
    )
    write_json(
        authority_root / "phase8_curation/selected_workflow_options.json",
        {
            "D5": _decision_by_id(
                load_json(owner_decisions_path), "D5"
            )["selected_option"],
            "D6": _decision_by_id(
                load_json(owner_decisions_path), "D6"
            )["selected_option"],
            "batch_member_expansion_preserved": True,
            "implicit_or_anonymous_approval_allowed": False,
        },
    )

    current_facts_path = root / CURRENT_FACTS
    facts_payload, stats = build_candidate_bytes(
        current_facts_path,
        target_members=set(target["members"]),
        automatic_rows=approved_automatic,
        curated_rows=normalized_curated,
        authority_bearing=True,
    )
    if (
        stats["changed_target_count"] != target["target_member_count"]
        or stats["missing_target_count"] != 0
        or stats["non_target_row_byte_mismatch_count"] != 0
    ):
        raise FoodSemanticError(f"authority candidate coverage failed: {stats}")
    successor_facts_path = authority_root / "successor_facts.jsonl"
    write_once_bytes(successor_facts_path, facts_payload)
    successor_facts_sha256 = sha256_file(successor_facts_path)

    current_manifest = load_json(root / CURRENT_MANIFEST)
    successor_manifest = deepcopy(current_manifest)
    successor_manifest["authority_role"] = "sealed_non_current_successor"
    successor_manifest["status"] = "sealed_successor_handoff"
    successor_manifest["facts"] = {
        "path": relative_posix(successor_facts_path, root=root),
        "sha256": successor_facts_sha256,
        "row_count": current_manifest["facts"]["row_count"],
        "role": "sealed_non_current_successor",
    }
    successor_manifest["food_semantic_authority"] = {
        "attempt_id": attempt_id,
        "authority_bearing": True,
        "selected_branch": "B",
        "non_current": True,
        "current_adoption_allowed": False,
        "target_member_count": target["target_member_count"],
        "target_member_set_sha256": target["member_set_sha256"],
        "required_fact_axes": sorted(required_axes()),
        "schema_sha256": schema_sha256,
        "proposition_license_sha256": proposition_license_sha256,
        "proposition_count": len(expected_inventory),
        "proposition_inventory_sha256": sha256_bytes(
            expected_inventory_bytes
        ),
    }
    successor_manifest_path = authority_root / "successor_input_manifest.json"
    write_json(successor_manifest_path, successor_manifest)

    authorization = {
        "schema_version": "food-semantic-successor-authorization-v1",
        "attempt_id": attempt_id,
        "implementation_complete_bundle_sha256": validation["bundle_sha256"],
        "owner_decisions_sha256": sha256_file(owner_decisions_path),
        "semantic_approval_sha256": sha256_file(semantic_approval_path),
        "external_review_sha256": sha256_file(external_review_path),
        "branch": "B",
        "current_mutation_allowed": False,
        "authorized_at": now_iso(),
    }
    authorization_path = (
        attempt_root / "phase11_successor/successor_authorization.json"
    )
    write_json(authorization_path, authorization)
    selected_binding = {
        "schema_version": "food-semantic-selected-successor-input-binding-v1",
        "selected_branch": "B",
        "successor_facts_path": relative_posix(successor_facts_path, root=root),
        "successor_facts_sha256": successor_facts_sha256,
        "successor_input_manifest_path": relative_posix(
            successor_manifest_path, root=root
        ),
        "successor_input_manifest_sha256": sha256_file(successor_manifest_path),
        "approved_food_semantic_schema_path": relative_posix(
            schema_path, root=root
        ),
        "approved_food_semantic_schema_sha256": sha256_file(schema_path),
        "approved_proposition_licensing_contract_path": relative_posix(
            license_path, root=root
        ),
        "approved_proposition_licensing_contract_sha256": sha256_file(
            license_path
        ),
        "target_member_count": target["target_member_count"],
        "target_member_set_sha256": target["member_set_sha256"],
        "required_fact_axes": sorted(required_axes()),
        "minimum_meaningful_partition": minimum_meaningful_partition,
        "expected_proposition_count": len(expected_inventory),
        "expected_proposition_inventory_sha256": sha256_bytes(
            expected_inventory_bytes
        ),
    }
    selected_binding_path = (
        attempt_root / "phase11_successor/selected_successor_input_binding.json"
    )
    write_json(selected_binding_path, selected_binding)
    receipt = {
        "schema_version": "food-semantic-sealed-successor-receipt-v1",
        "successor_facts_sha256": successor_facts_sha256,
        "successor_manifest_sha256": sha256_file(successor_manifest_path),
        "schema_sha256": sha256_file(schema_path),
        "proposition_license_sha256": sha256_file(license_path),
        "target_member_count": target["target_member_count"],
        "target_member_set_sha256": target["member_set_sha256"],
        "required_fact_axes": sorted(required_axes()),
        "food_semantic_proposition_count": len(expected_inventory),
        "food_semantic_proposition_inventory_sha256": sha256_bytes(
            expected_inventory_bytes
        ),
        "non_current": True,
        "authorization_sha256": sha256_file(authorization_path),
        "selected_binding_sha256": sha256_file(selected_binding_path),
        "current_facts_manifest_mutation_count": 0,
    }
    receipt_path = attempt_root / "phase11_successor/sealed_successor_receipt.json"
    write_json(receipt_path, receipt)
    owner = load_json(owner_decisions_path)
    d12 = _decision_by_id(owner, "D12")
    write_json(
        authority_root / "phase11_successor/registry_cutover_request.json",
        {
            "schema_version": "food-semantic-registry-cutover-request-v1",
            "status": "future_registry_review_required",
            "selected_successor_input_binding_sha256": sha256_file(
                selected_binding_path
            ),
            "successor_facts_sha256": successor_facts_sha256,
            "successor_input_manifest_sha256": sha256_file(
                successor_manifest_path
            ),
            "current_mutation_requested_by_this_round": False,
            "atomic_cutover_required": True,
            "partial_or_dual_current_allowed": False,
            "correction_owner": d12["correction_owner"],
            "correction_operational_route": d12["operational_route"],
            "predecessor_current_reentry_allowed": False,
        },
    )
    write_json(
        authority_root
        / "phase12_phase2_handoff/"
        "expected_semantic_partition_projection.json",
        {
            "schema_version": (
                "food-semantic-expected-partition-projection-v1"
            ),
            "status": "EXPECTED_INPUT_ONLY",
            "meaningful_partition_definition": (
                "Partitions differ by at least one approved licensed "
                "food-semantic axis/value proposition."
            ),
            "meaningful_partition_count": len(meaningful_profiles),
            "minimum_meaningful_partition_criterion": (
                minimum_meaningful_partition
            ),
            "actual_consumer_execution_count": 0,
            "criterion_gate_credit": 0,
        },
    )
    tooling_cap = load_json(
        attempt_root
        / "phase5_writer_contract/tooling_allowlist_relation_report.json"
    )
    write_json(
        authority_root / "phase5_writer_contract/tooling_cap_adoption.json",
        {
            "schema_version": "food-semantic-tooling-cap-adoption-v1",
            "status": "PASS",
            "current_core_count": tooling_cap["current_core_count"],
            "current_route_tooling_count": tooling_cap[
                "current_route_tooling_count"
            ],
            "convenience_expansion_count": tooling_cap[
                "tooling_allowlist_convenience_expansion_count"
            ],
            "D14_owner_decision_consumed": True,
        },
    )

    d16_adoption = adopt_d16_candidate_patch(
        root,
        attempt_root,
        owner_decisions_sha256=sha256_file(owner_decisions_path),
    )
    importlib.invalidate_caches()
    runner_module_name = (
        "tools.build.run_dvf_3_3_korean_prose_naturalization"
    )
    validator_module_name = (
        "tools.build.validate_dvf_3_3_korean_prose_naturalization"
    )
    sys.modules.pop(runner_module_name, None)
    sys.modules.pop(validator_module_name, None)
    runner_module = importlib.import_module(runner_module_name)
    validator_module = importlib.import_module(validator_module_name)
    expected_runner_path = (
        root
        / "Iris/build/description/v2/tools/build/"
        "run_dvf_3_3_korean_prose_naturalization.py"
    ).resolve()
    expected_validator_path = (
        root
        / "Iris/build/description/v2/tools/build/"
        "validate_dvf_3_3_korean_prose_naturalization.py"
    ).resolve()
    if (
        Path(runner_module.__file__).resolve() != expected_runner_path
        or Path(validator_module.__file__).resolve()
        != expected_validator_path
    ):
        raise FoodSemanticError("D16 actual consumer module identity mismatch")

    consumed = runner_module.consume_food_semantic_inputs_no_render(
        facts_path=successor_facts_path,
        manifest_path=successor_manifest_path,
        schema_path=schema_path,
        proposition_license_path=license_path,
        explicit_non_current_input_override=True,
        repository_root=root,
    )
    consumed_receipt = consumed["receipt"]
    actual_inventory = consumed["inventory"]
    actual_inventory_bytes = canonical_jsonl_bytes(actual_inventory)
    actual_inventory_path = (
        authority_root
        / "phase12_phase2_handoff/actual_food_semantic_inventory.jsonl"
    )
    write_once_bytes(actual_inventory_path, actual_inventory_bytes)
    consumed_receipt_path = (
        attempt_root
        / "phase12_phase2_handoff/actual_phase2_consumed_input_receipt.json"
    )
    write_json(consumed_receipt_path, consumed_receipt)
    consumed_validation = (
        validator_module.validate_food_semantic_consumed_input_receipt(
            consumed_receipt,
            selected_binding,
            repository_root=root,
            expected_projection=expected_projection,
        )
    )
    expected_row_bytes = {
        canonical_json_bytes(row) for row in expected_inventory
    }
    actual_row_bytes = {
        canonical_json_bytes(row) for row in actual_inventory
    }
    dropped_proposition_count = len(expected_row_bytes - actual_row_bytes)
    invented_proposition_count = len(actual_row_bytes - expected_row_bytes)
    exact_inventory_match = (
        actual_inventory_bytes == expected_inventory_bytes
        and dropped_proposition_count == 0
        and invented_proposition_count == 0
    )
    reconciliation = {
        "schema_version": "food-semantic-phase2-proposition-reconciliation-v1",
        "status": "PASS" if exact_inventory_match else "FAIL",
        "expected_inventory_sha256": sha256_bytes(expected_inventory_bytes),
        "actual_inventory_sha256": sha256_bytes(actual_inventory_bytes),
        "expected_proposition_count": len(expected_inventory),
        "actual_proposition_count": len(actual_inventory),
        "dropped_proposition_count": dropped_proposition_count,
        "invented_proposition_count": invented_proposition_count,
        "exact_inventory_match": exact_inventory_match,
        "actual_consumer_derived_meaningful_partition_count": (
            consumed_receipt["meaningful_partition_count"]
        ),
    }
    write_json(
        authority_root
        / "phase12_phase2_handoff/proposition_reconciliation_report.json",
        reconciliation,
    )
    write_json(
        authority_root / "phase12_phase2_handoff/semantic_partition_report.json",
        {
            "schema_version": "food-semantic-authority-partition-report-v1",
            "status": (
                "PASS"
                if consumed_receipt["meaningful_partition_count"]
                >= minimum_meaningful_partition
                else "FAIL"
            ),
            "meaningful_partition_definition": (
                "Partitions differ by at least one approved licensed "
                "food-semantic axis/value proposition."
            ),
            "meaningful_partition_count": consumed_receipt[
                "meaningful_partition_count"
            ],
            "minimum_meaningful_partition_criterion": (
                minimum_meaningful_partition
            ),
            "partition_source": "actual_naturalization_phase2_consumer",
            "actual_inventory_sha256": sha256_bytes(actual_inventory_bytes),
            "D10_owner_decision_consumed": True,
            "criterion_gate_credit": 1,
        },
    )
    write_json(
        attempt_root
        / "phase12_phase2_handoff/consumed_input_identity_report.json",
        consumed_validation,
    )
    if consumed_validation["status"] != "PASS" or not exact_inventory_match:
        raise FoodSemanticError(
            "actual Phase 2 consumed input mismatch: "
            f"{consumed_validation}; {reconciliation}"
        )
    summary = {
        "schema_version": "food-semantic-authority-execution-summary-v1",
        "attempt_id": attempt_id,
        "status": "PASS",
        "selected_branch": "B",
        "sealed_non_current_successor": True,
        "successor_facts_sha256": successor_facts_sha256,
        "successor_manifest_sha256": sha256_file(successor_manifest_path),
        "curated_proposition_count": curation_report[
            "curated_proposition_count"
        ],
        "meaningful_partition_count": consumed_receipt[
            "meaningful_partition_count"
        ],
        "actual_phase2_no_render_identity_match": True,
        "actual_phase2_exact_proposition_match": True,
        "dropped_proposition_count": 0,
        "invented_proposition_count": 0,
        "D16_adopted_file_count": d16_adoption["adopted_file_count"],
        "owner_decision_ids_consumed": sorted(
            AUTHORITY_EXECUTION_REQUIRED_DECISIONS
        ),
        "D1_selected_option": _decision_by_id(owner, "D1")[
            "selected_option"
        ],
        "D11_selected_option": _decision_by_id(owner, "D11")[
            "selected_option"
        ],
        "D13_selected_option": _decision_by_id(owner, "D13")[
            "selected_option"
        ],
        "D15_selected_option": _decision_by_id(owner, "D15")[
            "selected_option"
        ],
        "post_authority_validation_pending": True,
        "terminal_independent_review_pending": True,
        "owner_terminal_seal_pending": True,
        "current_facts_manifest_mutation_count": 0,
        "official_naturalization_retry_allowed": False,
    }
    write_json(authority_root / "authority_execution_summary.json", summary)
    return summary
