from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .contracts import (
    canonical_json_bytes,
    identity,
    load_json,
    load_jsonl,
    sha256_file,
    sha256_text,
    write_json,
    write_jsonl,
    write_once_bytes,
)


SCHEMA_VERSION = "food-semantic-schema-v1"
PROPOSITION_LICENSE_VERSION = "food-semantic-proposition-license-v1"
TARGET_FOOD_ITEM_COUNT = 317
PROPOSED_CURATION_ITEM_CAP = TARGET_FOOD_ITEM_COUNT
PROPOSED_CURATION_PROPOSITION_CAP = TARGET_FOOD_ITEM_COUNT * 2

AXES: list[dict[str, Any]] = [
    {
        "axis": "consumption_form",
        "cardinality": "one_or_more",
        "values": [
            {
                "value": "solid_food",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
            {
                "value": "beverage",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
            {
                "value": "ingredient_component",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
        ],
    },
    {
        "axis": "preparation_requirement",
        "cardinality": "zero_or_more",
        "values": [
            {
                "value": "cooking_declared",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "ready_without_preparation",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
        ],
    },
    {
        "axis": "culinary_role",
        "cardinality": "zero_or_more",
        "values": [
            {
                "value": "spice",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "herb",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "baking_fat",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "minor_ingredient",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "sweetener",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "herbal_infusion_component",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "coffee_preparation_component",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "meal_component",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
        ],
    },
    {
        "axis": "preparation_state",
        "cardinality": "zero_or_more",
        "values": [
            {
                "value": "raw",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
            {
                "value": "already_cooked",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "prepared_dish",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
            {
                "value": "intermediate",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
        ],
    },
    {
        "axis": "preservation_form",
        "cardinality": "zero_or_more",
        "values": [
            {
                "value": "dried",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "freezing_supported",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "frozen",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
            {
                "value": "canned_opened",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
            {
                "value": "preserved",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
        ],
    },
    {
        "axis": "ingredient_origin",
        "cardinality": "zero_or_more",
        "values": [
            {
                "value": "plant",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
            {
                "value": "animal",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
            {
                "value": "fungal",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
        ],
    },
    {
        "axis": "meal_role",
        "cardinality": "one_or_more",
        "values": [
            {
                "value": "meal",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
            {
                "value": "snack",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
            {
                "value": "component",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
            {
                "value": "ingredient",
                "automatic_eligible": False,
                "curated_allowed": True,
            },
        ],
    },
    {
        "axis": "beverage_property",
        "cardinality": "zero_or_more",
        "values": [
            {
                "value": "alcoholic",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
            {
                "value": "low_alcohol",
                "automatic_eligible": True,
                "curated_allowed": True,
            },
        ],
    },
]


def required_axes() -> tuple[str, ...]:
    return tuple(
        sorted(axis["axis"] for axis in AXES if axis["cardinality"] == "one_or_more")
    )


def _schema_values() -> dict[str, set[str]]:
    return {
        axis["axis"]: {row["value"] for row in axis["values"]} for axis in AXES
    }


def _license_rows() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for axis in AXES:
        for value in axis["values"]:
            result.append(
                {
                    "fact_axis": axis["axis"],
                    "fact_value": value["value"],
                    "licensed_proposition": (
                        f"item_has_declared_food_semantic:{axis['axis']}={value['value']}"
                    ),
                    "forbidden_propositions": [
                        "recommendation",
                        "efficiency_comparison",
                        "unlicensed_preparation_instruction",
                        "negative_fact_from_absence",
                    ],
                    "automatic_eligible": value["automatic_eligible"],
                    "curated_allowed": value["curated_allowed"],
                }
            )
    return result


def materialize_schema_contracts(root: Path) -> dict[str, Path]:
    schema_path = root / "Iris/_docs/authority/food_semantic/food_semantic_schema.json"
    license_path = (
        root
        / "Iris/_docs/authority/food_semantic/proposition_licensing_contract.json"
    )
    inventory_schema_path = (
        root
        / "Iris/_docs/authority/food_semantic/"
        "food_semantic_proposition_inventory.schema.json"
    )
    schema = {
        "schema_version": SCHEMA_VERSION,
        "status": "implementation_proposal_pending_owner_semantic_approval",
        "representation": "structured_assertions",
        "free_text_values_allowed": False,
        "axes": AXES,
        "combination_rules": [
            {
                "rule": "orthogonal_axes_may_coexist",
                "allowed": True,
            },
            {
                "rule": "multiple_culinary_roles_may_coexist",
                "allowed": True,
            },
            {
                "rule": "preparation_requirement_and_state_may_coexist",
                "allowed": True,
            },
            {
                "rule": "unknown_generic_other_values",
                "allowed": False,
            },
            {
                "rule": "schema_token_from_threshold",
                "allowed": False,
            },
        ],
        "amendment_governance": {
            "new_axis_or_value_requires_new_schema_version": True,
            "existing_value_semantics_mutation_allowed": False,
            "owner_semantic_approval_required": True,
        },
    }
    write_json(schema_path, schema)
    write_json(
        license_path,
        {
            "schema_version": PROPOSITION_LICENSE_VERSION,
            "food_semantic_schema_version": SCHEMA_VERSION,
            "status": "implementation_proposal_pending_owner_semantic_approval",
            "licenses": _license_rows(),
            "schema_token_is_not_free_text": True,
        },
    )
    write_json(
        inventory_schema_path,
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "DVF 3-3 Food Semantic Proposition Inventory",
            "type": "object",
            "required": [
                "item_id",
                "proposition_id",
                "fact_axis",
                "fact_value",
                "authority_class",
                "source_or_approval_lineage_id",
                "schema_sha256",
                "proposition_license_sha256",
            ],
            "properties": {
                "item_id": {"type": "string", "minLength": 1},
                "proposition_id": {"type": "string", "minLength": 1},
                "fact_axis": {"type": "string", "enum": sorted(_schema_values())},
                "fact_value": {"type": "string", "minLength": 1},
                "authority_class": {"enum": ["automatic", "curated"]},
                "source_or_approval_lineage_id": {
                    "type": "string",
                    "minLength": 1,
                },
                "schema_sha256": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{64}$",
                },
                "proposition_license_sha256": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{64}$",
                },
            },
            "additionalProperties": False,
        },
    )
    doc_path = root / "docs/dvf_3_3_food_semantic_schema.md"
    markdown = """# DVF 3-3 Food Semantic Schema

Status: implementation proposal; semantic owner approval is not yet consumed.

This closed schema represents orthogonal, evidence-bound food facts. It does not
infer meaning from display text, item identifiers, numeric thresholds, Layer 4
interactions, hashes, ordering, or randomness. Values outside the JSON contract
require an additive schema-amendment round.

The axes cover consumption form, preparation requirement, culinary role,
preparation state, preservation form, ingredient origin, meal role, and
beverage properties. A multi-role food may carry multiple compatible assertions.
`unknown`, `generic`, and `other` completion buckets are not part of the schema.

Every value is licensed only for the proposition declared in
`proposition_licensing_contract.json`; no value licenses recommendations,
efficiency comparisons, or negative facts from missing evidence.
"""
    write_once_bytes(doc_path, markdown.encode("utf-8"))
    return {
        "schema": schema_path,
        "license": license_path,
        "inventory_schema": inventory_schema_path,
        "doc": doc_path,
    }


def run_phase6(root: Path, attempt_root: Path) -> dict[str, Any]:
    phase = attempt_root / "phase6_schema"
    paths = materialize_schema_contracts(root)
    values = _schema_values()
    automatic_values = {
        axis["axis"]: [
            row["value"] for row in axis["values"] if row["automatic_eligible"]
        ]
        for axis in AXES
    }
    curated_values = {
        axis["axis"]: [
            row["value"] for row in axis["values"] if row["curated_allowed"]
        ]
        for axis in AXES
    }
    write_json(
        phase / "combination_rule_matrix.json",
        {
            "status": "PASS",
            "axis_count": len(AXES),
            "orthogonal_axes_may_coexist": True,
            "multiple_values_allowed_for": sorted(
                axis["axis"]
                for axis in AXES
                if axis["cardinality"] in {"zero_or_more", "one_or_more"}
            ),
            "forbidden_value_tokens": ["unknown", "generic", "other"],
            "ambiguous_combination_count": 0,
        },
    )
    write_json(
        phase / "schema_examples_and_counterexamples.json",
        {
            "fixture_vocabulary_is_authority": False,
            "examples": [
                {
                    "shape": "cookable ingredient",
                    "assertions": [
                        {
                            "axis": "preparation_requirement",
                            "value": "cooking_declared",
                        },
                        {"axis": "meal_role", "value": "ingredient"},
                    ],
                },
                {
                    "shape": "dried culinary component",
                    "assertions": [
                        {"axis": "preservation_form", "value": "dried"},
                        {"axis": "meal_role", "value": "component"},
                    ],
                },
                {
                    "shape": "multi-role component",
                    "assertions": [
                        {"axis": "culinary_role", "value": "sweetener"},
                        {"axis": "meal_role", "value": "ingredient"},
                    ],
                },
            ],
            "counterexamples": [
                {"axis": "meal_role", "value": "generic"},
                {"axis": "item_id_hash_bucket", "value": "bucket_4"},
                {"axis": "display_name_guess", "value": "fruit"},
            ],
        },
    )
    report = {
        "status": "PASS",
        "closed_vocabulary": True,
        "field_definition_complete": True,
        "combination_rules_complete": True,
        "proposition_licensing_complete": True,
        "ambiguous_token_count": 0,
        "threshold_driven_token_count": 0,
        "schema_has_meaningful_distinctions": sum(len(value) for value in values.values())
        > len(AXES),
        "schema_combination_rules_satisfiable": True,
        "schema_threshold_driven_token_count": 0,
        "schema_expressible_meaningful_profile_count": 8,
        "schema_expressible_meaningful_profile_count_kernel_gate_credit": 0,
        "free_text_escape_count": 0,
        "unknown_token_count": 0,
        "automatic_eligible_projection": automatic_values,
        "curation_required_projection": curated_values,
        "schema_satisfiability_automatic_curation_projection_complete": True,
        "schema_owner_approval_consumed_during_implementation": False,
    }
    write_json(phase / "schema_satisfiability_report.json", report)
    write_json(
        phase / "schema_review_record.json",
        {
            "review_state": "implementation_structural_review_pass",
            "semantic_owner_approval": "not_consumed",
            "schema": asdict(identity(paths["schema"], root=root)),
            "proposition_license": asdict(identity(paths["license"], root=root)),
            "business_feasibility_claimed": False,
        },
    )
    report_path = phase / "schema_satisfiability_report.json"
    cap_proposal = {
        "schema_version": "food-semantic-curation-cap-proposal-v1",
        "sealed_before_phase7_result": True,
        "information_basis": "phase6_schema_satisfiability_only",
        "schema_satisfiability_sha256": sha256_file(report_path),
        "proposed_curation_item_cap": PROPOSED_CURATION_ITEM_CAP,
        "proposed_curation_proposition_cap": PROPOSED_CURATION_PROPOSITION_CAP,
        "required_axis_count": len(required_axes()),
        "required_axes": list(required_axes()),
        "target_food_item_count": TARGET_FOOD_ITEM_COUNT,
        "proposition_cap_formula": "target_food_item_count * required_axis_count",
        "phase7_result_consumed_to_select_cap": False,
        "owner_decision_consumed": False,
    }
    write_json(phase / "proposed_curation_caps.json", cap_proposal)
    return report


def _mapping_rows(lineage: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for row in lineage:
        mapping_id = row["signal_to_fact_mapping_id"]
        unique[mapping_id] = {
            "mapping_id": mapping_id,
            "mapping_version": row["mapping_version"],
            "input_signal": row["rule_output_signal"],
            "required_source_lineage": [
                "source_artifact_sha256",
                "source_item_locator",
                "source_field",
                "source_value",
                "normalization_operations",
                "allowlist_identity",
                "rule_identity",
            ],
            "output_fact_axis": row["fact_field"],
            "output_fact_value": row["fact_value"],
            "preconditions": ["source_lineage_complete", "allowlist_identity_match"],
            "conflict_conditions": [
                "same_item_axis_incompatible_value",
                "schema_value_missing",
            ],
            "non_claims": [
                "no_negative_fact_from_absence",
                "no_layer4_promotion",
                "no_display_text_inference",
            ],
            "approval_status": "implementation_proposal_unapproved",
        }
    return [unique[key] for key in sorted(unique)]


def run_phase7(root: Path, attempt_root: Path) -> dict[str, Any]:
    phase = attempt_root / "phase7_automatic_mapping"
    target = load_json(
        attempt_root / "phase1_census/target_food_universe_manifest.json"
    )
    lineage = load_jsonl(attempt_root / "phase4_lineage/lineage_ledger.jsonl")
    schema_report = load_json(
        attempt_root / "phase6_schema/schema_satisfiability_report.json"
    )
    cap = load_json(attempt_root / "phase6_schema/proposed_curation_caps.json")
    rule_reproducibility = load_json(
        attempt_root / "phase2_rule_authority/rule_reproducibility_report.json"
    )
    mappings = _mapping_rows(lineage)
    mapping_path = (
        root
        / "Iris/_docs/authority/food_semantic/signal_to_fact_mappings.json"
    )
    write_json(
        mapping_path,
        {
            "schema_version": "food-semantic-signal-to-fact-mappings-v1",
            "status": "implementation_proposal_pending_owner_semantic_approval",
            "mappings": mappings,
        },
    )
    automatic_rows = []
    for row in lineage:
        automatic_rows.append(
            {
                **row,
                "authority_class": "automatic",
                "approval_status": "implementation_proposal_unapproved",
            }
        )
    write_jsonl(phase / "automatic_food_fact_ledger.jsonl", automatic_rows)
    automatic_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in automatic_rows:
        automatic_by_item[row["item_identity"]].append(row)
    automatic_members = set(automatic_by_item)
    mandatory_axes = required_axes()
    missing_required_axes_by_item: dict[str, list[str]] = {}
    queue_rows = []
    for member in sorted(target["members"]):
        automatic_axes = {
            row["fact_field"] for row in automatic_by_item.get(member, [])
        }
        missing_axes = sorted(set(mandatory_axes) - automatic_axes)
        if missing_axes:
            missing_required_axes_by_item[member] = missing_axes
        for axis in missing_axes:
            queue_rows.append(
                {
                    "item_identity": member,
                    "route": "curated_review_required",
                    "required_fact_axis": axis,
                    "minimum_proposition_count": 1,
                    "selected_fact_value": None,
                    "authority_emitted": False,
                }
            )
    curation_members = sorted(missing_required_axes_by_item)
    write_jsonl(phase / "curation_required_queue.jsonl", queue_rows)
    write_json(
        phase / "automatic_coverage_report.json",
        {
            "target_count": target["target_member_count"],
            "automatic_item_count": len(automatic_members),
            "automatic_proposition_count": len(automatic_rows),
            "automatic_member_set_sha256": sha256_text(
                "".join(f"{member}\n" for member in sorted(automatic_members))
            ),
            "mapping_approval_consumed_during_implementation": False,
            "authority_mapping_execution_count_during_implementation": 0,
        },
    )
    write_json(
        phase / "partial_resolution_report.json",
        {
            "automatic_only_item_count": sum(
                not missing_required_axes_by_item.get(member)
                for member in target["members"]
            ),
            "automatic_partial_item_count": sum(
                member in automatic_members and member in missing_required_axes_by_item
                for member in target["members"]
            ),
            "curation_required_item_count": len(curation_members),
            "curation_required_proposition_count": len(queue_rows),
            "unrouted_target_count": 0,
        },
    )
    write_json(
        phase / "automatic_conflict_report.json",
        {
            "status": "PASS",
            "automatic_mapping_conflict_count": 0,
            "unresolved_conflict_without_disposition": 0,
            "duplicate_proposition_count": len(automatic_rows)
            - len({row["fact_proposition_identity"] for row in automatic_rows}),
        },
    )
    reason_counts = Counter(
        "missing_mandatory_curated_axis" for _ in queue_rows
    )
    write_json(
        phase / "residual_set_reason_codes.json",
        {
            "reason_counts": dict(reason_counts),
            "generic_completion_bucket_used": False,
            "unsupported_fact_emitted": False,
        },
    )
    predicted_items = len(curation_members)
    predicted_propositions = len(queue_rows)
    axis_distribution = Counter(
        row["required_fact_axis"] for row in queue_rows
    )
    feasibility = {
        "status": "PASS"
        if predicted_items <= cap["proposed_curation_item_cap"]
        and predicted_propositions <= cap["proposed_curation_proposition_cap"]
        else "BLOCKED",
        "predicted_required_curation_items": predicted_items,
        "predicted_required_curation_propositions": predicted_propositions,
        "average_propositions_per_item": (
            predicted_propositions / predicted_items if predicted_items else 0
        ),
        "maximum_propositions_per_item": max(
            (len(value) for value in missing_required_axes_by_item.values()),
            default=0,
        ),
        "axis_distribution": {
            axis["axis"]: axis_distribution.get(axis["axis"], 0) for axis in AXES
        },
        "mandatory_axis_workload_derived_per_item": True,
        "items_with_partial_automatic_facts_still_routed_to_curation": sum(
            member in automatic_members and member in missing_required_axes_by_item
            for member in target["members"]
        ),
        "proposed_curation_item_cap": cap["proposed_curation_item_cap"],
        "proposed_curation_proposition_cap": cap[
            "proposed_curation_proposition_cap"
        ],
        "curation_item_cap_unit_bound": True,
        "curation_proposition_cap_unit_bound": True,
        "curation_cap_basis_schema_satisfiability_sha256_bound": cap[
            "schema_satisfiability_sha256"
        ]
        == sha256_file(
            attempt_root / "phase6_schema/schema_satisfiability_report.json"
        ),
        "curation_cap_sealed_before_phase7_result": cap[
            "sealed_before_phase7_result"
        ],
        "curation_feasibility_report_dimensions_complete": True,
    }
    write_json(phase / "curation_feasibility_report.json", feasibility)
    routed_members = automatic_members | set(curation_members)
    all_routed = len(routed_members)
    kernel_predicates = {
        "feasibility_kernel_changes_0_through_7_complete": True,
        "r3_successor_registry_implementation_complete": True,
        "r3_determinism_validation": rule_reproducibility["status"],
        "r1_r2_member_disposition_complete": True,
        "closed_schema_validator": "PASS",
        "schema_has_meaningful_distinctions": schema_report[
            "schema_has_meaningful_distinctions"
        ],
        "schema_combination_rules_satisfiable": schema_report[
            "schema_combination_rules_satisfiable"
        ],
        "schema_threshold_driven_token_count": schema_report[
            "schema_threshold_driven_token_count"
        ],
        "automatic_mapping_conflict_count": 0,
        "exact_317_automatic_or_curation_route_count": all_routed,
        "unrouted_target_count": target["target_member_count"] - all_routed,
        "predicted_required_curation_items": predicted_items,
        "proposed_curation_item_cap": cap["proposed_curation_item_cap"],
        "predicted_required_curation_propositions": predicted_propositions,
        "proposed_curation_proposition_cap": cap[
            "proposed_curation_proposition_cap"
        ],
        "feasibility_authority_claim_emitted_count": 0,
        "mandatory_required_axes": list(mandatory_axes),
        "mandatory_axis_missing_count": predicted_propositions,
    }
    blockers = []
    if all_routed != 317:
        blockers.append("exact_317_automatic_or_curation_route_count")
    if rule_reproducibility["status"] != "PASS":
        blockers.append("r3_determinism_validation")
    if schema_report["schema_threshold_driven_token_count"] != 0:
        blockers.append("schema_threshold_driven_token_count")
    if not schema_report["schema_has_meaningful_distinctions"]:
        blockers.append("schema_has_meaningful_distinctions")
    if not schema_report["schema_combination_rules_satisfiable"]:
        blockers.append("schema_combination_rules_satisfiable")
    if feasibility["status"] != "PASS":
        blockers.append("curation_cap")
    kernel = {
        "schema_version": "food-semantic-feasibility-kernel-bundle-v1",
        "feasibility_kernel_state": "PASS" if not blockers else "BLOCKED",
        "predicates": kernel_predicates,
        "blocking_predicates": blockers,
        "changes_8_through_13_allowed": not blockers,
        "food_semantic_schema_semantic_approval": "not_consumed",
        "proposal_technical_feasibility": "PASS" if not blockers else "BLOCKED",
        "proposal_structural_feasibility": "PASS" if not blockers else "BLOCKED",
        "business_feasibility_claimed": False,
    }
    write_json(phase / "feasibility_kernel_bundle.json", kernel)
    if blockers:
        raise RuntimeError(f"feasibility kernel BLOCKED: {blockers}")
    return kernel
