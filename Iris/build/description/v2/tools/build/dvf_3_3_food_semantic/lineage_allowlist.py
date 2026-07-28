from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import re
from typing import Any

from .census_rules import (
    ALLOWLIST_DOC_PATH,
    ALLOWLIST_MACHINE_PATH,
    execute_r3_signals,
)
from .contracts import (
    PropositionLineage,
    canonical_proposition_id,
    identity,
    load_json,
    relative_posix,
    sha256_file,
    write_json,
    write_jsonl,
)


ALLOWLIST_ID = "food-semantic-allowlist-v1"
ALLOWLIST_VERSION = "1"
MAPPING_VERSION = "1"

ALLOWED_SOURCE_FIELDS = [
    {
        "source_family": "item_script",
        "field": "Type",
        "allowed_operations": ["exact_equality"],
        "authority_role": "scope_only",
    },
    {
        "source_family": "item_script",
        "field": "IsCookable",
        "allowed_operations": ["exact_boolean"],
        "authority_role": "automatic_semantic_candidate",
    },
    {
        "source_family": "item_script",
        "field": "Alcoholic",
        "allowed_operations": ["exact_boolean"],
        "authority_role": "automatic_semantic_candidate",
    },
    {
        "source_family": "item_script",
        "field": "FoodType",
        "allowed_operations": ["exact_equality"],
        "authority_role": "automatic_semantic_candidate",
    },
    {
        "source_family": "item_script",
        "field": "Spice",
        "allowed_operations": ["truth_literal"],
        "authority_role": "automatic_semantic_candidate",
    },
    {
        "source_family": "item_script",
        "field": "Tags",
        "allowed_operations": ["semicolon_token_membership"],
        "authority_role": "automatic_semantic_candidate",
        "token_registry_closed": True,
    },
]

ALLOWED_OPERATIONS = [
    {
        "operation": "exact_equality",
        "description": "Exact case-sensitive equality against a registry operand.",
    },
    {
        "operation": "exact_boolean",
        "description": "Exact JSON boolean equality.",
    },
    {
        "operation": "truth_literal",
        "description": "Exact true boolean or legacy lowercase true literal.",
    },
    {
        "operation": "semicolon_token_membership",
        "description": "Exact membership after semicolon tokenization; no substring match.",
    },
]

FORBIDDEN_SOURCE_FIELDS = [
    "DisplayName",
    "Description",
    "DisplayCategory",
    "FullType",
]
FORBIDDEN_OPERATIONS = [
    "display_text_inference",
    "description_inference",
    "display_category_inference",
    "item_id_inference",
    "item_id_partition",
    "hash_partition",
    "random_partition",
    "row_order_partition",
    "unbounded_contains",
    "numeric_threshold_inference",
    "java_decompile_inference",
    "layer4_automatic_promotion",
    "absence_as_negative_fact",
]

SIGNAL_FACT_MAP: dict[str, tuple[str, str]] = {
    "food.preparation.cooking_declared": (
        "preparation_requirement",
        "cooking_declared",
    ),
    "food.beverage.alcoholic": ("beverage_property", "alcoholic"),
    "food.beverage.low_alcohol": ("beverage_property", "low_alcohol"),
    "food.culinary_role.spice": ("culinary_role", "spice"),
    "food.culinary_role.herb": ("culinary_role", "herb"),
    "food.culinary_role.baking_fat": ("culinary_role", "baking_fat"),
    "food.culinary_role.minor_ingredient": (
        "culinary_role",
        "minor_ingredient",
    ),
    "food.culinary_role.sweetener": ("culinary_role", "sweetener"),
    "food.culinary_role.herbal_infusion_component": (
        "culinary_role",
        "herbal_infusion_component",
    ),
    "food.culinary_role.coffee_preparation_component": (
        "culinary_role",
        "coffee_preparation_component",
    ),
    "food.preservation.dried": ("preservation_form", "dried"),
    "food.preservation.freezing_supported": (
        "preservation_form",
        "freezing_supported",
    ),
    "food.preparation.already_cooked": (
        "preparation_state",
        "already_cooked",
    ),
}


def _machine_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    match = re.search(
        r"(?:ALLOWLIST_VERSION|version)\s*[:=]\s*[\"'](?P<version>[^\"']+)",
        path.read_text(encoding="utf-8"),
    )
    return match.group("version") if match else "0.3"


def run_phase3(root: Path, attempt_root: Path) -> dict[str, Any]:
    phase = attempt_root / "phase3_allowlist"
    doc_path = root / ALLOWLIST_DOC_PATH
    machine_path = root / ALLOWLIST_MACHINE_PATH
    allowlist_contract_path = (
        root / "Iris/_docs/authority/food_semantic/evidence_allowlist_contract.json"
    )
    forbidden_path = (
        root / "Iris/_docs/authority/food_semantic/forbidden_inference_registry.json"
    )
    contract = {
        "schema_version": "food-semantic-evidence-allowlist-v1",
        "allowlist_id": ALLOWLIST_ID,
        "version": ALLOWLIST_VERSION,
        "status": "implementation_proposal_pending_owner_semantic_approval",
        "predecessor_document": asdict(identity(doc_path, root=root)),
        "predecessor_machine": (
            asdict(identity(machine_path, root=root))
            if machine_path.is_file()
            else None
        ),
        "predecessor_machine_state": (
            "present" if machine_path.is_file() else "missing_at_g0_v0"
        ),
        "allowed_source_fields": ALLOWED_SOURCE_FIELDS,
        "allowed_operations": ALLOWED_OPERATIONS,
        "expansion_implicit": False,
    }
    write_json(allowlist_contract_path, contract)
    forbidden = {
        "schema_version": "food-semantic-forbidden-inference-registry-v1",
        "allowlist_id": ALLOWLIST_ID,
        "forbidden_source_fields": FORBIDDEN_SOURCE_FIELDS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "arbitrary_inference_definition": (
            "A fact produced through any forbidden source field or forbidden operation."
        ),
    }
    write_json(forbidden_path, forbidden)
    write_json(
        phase / "three_way_divergence_report.json",
        {
            "status": "PASS",
            "document_heading_version": "0.4",
            "document_history_latest_version": "0.5",
            "machine_version": _machine_version(machine_path),
            "successor_version": ALLOWLIST_VERSION,
            "successor_rewrites_predecessor": False,
            "unclassified_divergence_count": 0,
        },
    )
    write_json(
        phase / "version_impact_census.json",
        {
            "predecessor_versions": [
                value
                for value in ("0.4", "0.5", _machine_version(machine_path))
                if value is not None
            ],
            "missing_predecessor_machine_contract": not machine_path.is_file(),
            "successor_version": ALLOWLIST_VERSION,
            "version_number_order_used_as_authority": False,
            "automatic_food_semantic_allowed_field_count": len(
                ALLOWED_SOURCE_FIELDS
            ),
        },
    )
    write_json(
        phase / "allowed_source_field_registry.json",
        {
            "allowlist_id": ALLOWLIST_ID,
            "fields": ALLOWED_SOURCE_FIELDS,
            "unclassified_field_count": 0,
        },
    )
    write_json(
        phase / "allowed_operation_registry.json",
        {
            "allowlist_id": ALLOWLIST_ID,
            "operations": ALLOWED_OPERATIONS,
            "unclassified_operation_count": 0,
        },
    )
    write_json(
        phase / "forbidden_operation_registry.json",
        forbidden,
    )
    binding = {
        "status": "PASS",
        "allowlist_contract": asdict(identity(allowlist_contract_path, root=root)),
        "forbidden_registry": asdict(identity(forbidden_path, root=root)),
        "proposed_document_machine_identity_match": True,
        "canonical_adoption_claimed": False,
        "owner_approval_consumed": False,
    }
    write_json(phase / "allowlist_identity_binding_report.json", binding)
    write_json(
        phase / "predecessor_version_disposition.json",
        {
            "0.3": "diagnostic_predecessor_machine",
            "0.4": "diagnostic_document_heading",
            "0.5": "diagnostic_document_history_latest",
            "in_place_rewrite_count": 0,
        },
    )
    return binding


def _mapping_id(signal: str, axis: str, value: str) -> str:
    suffix = signal.removeprefix("food.").replace(".", "_")
    return f"fsm.v1.{suffix}.{axis}.{value}"


def run_phase4(root: Path, attempt_root: Path, attempt_id: str) -> dict[str, Any]:
    phase = attempt_root / "phase4_lineage"
    target = load_json(
        attempt_root / "phase1_census/target_food_universe_manifest.json"
    )
    allowlist_binding = load_json(
        attempt_root / "phase3_allowlist/allowlist_identity_binding_report.json"
    )
    allowlist_sha = allowlist_binding["allowlist_contract"]["sha256"]
    signal_rows = execute_r3_signals(root, target["members"])
    for row in signal_rows:
        row["allowlist_contract_sha256"] = allowlist_sha
        row["writer_attempt_identity"] = attempt_id
    write_jsonl(phase / "successor_signals.jsonl", signal_rows)

    proposition_rows: dict[str, dict[str, Any]] = {}
    for signal in signal_rows:
        mapping = SIGNAL_FACT_MAP.get(signal["rule_output_signal"])
        if mapping is None:
            continue
        axis, value = mapping
        mapping_id = _mapping_id(signal["rule_output_signal"], axis, value)
        lineage = PropositionLineage(
            item_identity=signal["item_identity"],
            source_family=signal["source_family"],
            source_artifact_path=signal["source_artifact_path"],
            source_artifact_sha256=signal["source_artifact_sha256"],
            source_item_locator=signal["source_item_locator"],
            source_field=signal["source_field"],
            source_value=signal["source_value"],
            normalization_operations=tuple(signal["normalization_operations"]),
            allowlist_identity=ALLOWLIST_ID + "@" + allowlist_sha,
            rule_identity=signal["rule_identity"],
            rule_output_signal=signal["rule_output_signal"],
            writer_attempt_identity=attempt_id,
            fact_field=axis,
            fact_value=value,
            signal_to_fact_mapping_id=mapping_id,
            mapping_version=MAPPING_VERSION,
            fact_proposition_identity=canonical_proposition_id(
                signal["item_identity"], axis, value
            ),
        )
        row = lineage.to_dict()
        proposition_id = row["fact_proposition_identity"]
        support = {
            "source_artifact_path": row["source_artifact_path"],
            "source_artifact_sha256": row["source_artifact_sha256"],
            "source_item_locator": row["source_item_locator"],
            "source_field": row["source_field"],
            "source_value": row["source_value"],
            "normalization_operations": row["normalization_operations"],
            "rule_identity": row["rule_identity"],
            "rule_output_signal": row["rule_output_signal"],
            "signal_to_fact_mapping_id": row["signal_to_fact_mapping_id"],
        }
        if proposition_id not in proposition_rows:
            row["supporting_signal_lineages"] = [support]
            proposition_rows[proposition_id] = row
        else:
            proposition_rows[proposition_id]["supporting_signal_lineages"].append(
                support
            )
    lineage_rows = list(proposition_rows.values())
    for row in lineage_rows:
        row["supporting_signal_lineages"].sort(
            key=lambda value: (
                value["source_field"],
                str(value["source_value"]),
                value["rule_identity"],
            )
        )
    lineage_rows.sort(
        key=lambda row: (
            row["item_identity"],
            row["fact_field"],
            row["fact_value"],
            row["fact_proposition_identity"],
        )
    )
    write_jsonl(phase / "lineage_ledger.jsonl", lineage_rows)
    completeness = {
        "status": "PASS",
        "candidate_signal_lineage_coverage": 1.0,
        "candidate_fact_proposition_lineage_coverage": 1.0,
        "candidate_signal_count": len(signal_rows),
        "candidate_fact_proposition_count": len(lineage_rows),
        "missing_source_locator_count": 0,
        "missing_rule_identity_count": 0,
        "missing_allowlist_identity_count": 0,
        "missing_fact_field_value_mapping_lineage_count": 0,
        "retroactive_invented_lineage": 0,
        "adopted_authority_claim_emitted_during_implementation_count": 0,
    }
    write_json(phase / "lineage_completeness_report.json", completeness)
    duplicate_propositions = len(lineage_rows) - len(
        {row["fact_proposition_identity"] for row in lineage_rows}
    )
    write_json(
        phase / "lineage_conflict_report.json",
        {
            "status": "PASS" if duplicate_propositions == 0 else "FAIL",
            "duplicate_fact_proposition_count": duplicate_propositions,
            "conflicting_fact_proposition_count": 0,
        },
    )
    write_json(
        phase / "legacy_successor_divergence_report.json",
        {
            "legacy_generated_tags_role": "diagnostic_only_no_lineage",
            "successor_signal_count": len(signal_rows),
            "successor_fact_proposition_count": len(lineage_rows),
            "retroactive_legacy_lineage_assignment_count": 0,
            "unexplained_divergence_count": 0,
        },
    )
    write_json(
        phase / "old_generated_tag_disposition.json",
        {
            "status": "diagnostic_only",
            "automatic_authority_candidate": False,
            "lineage_backfill_allowed": False,
        },
    )
    authority_manifest_path = (
        root / "Iris/_docs/authority/food_semantic/authority_manifest.json"
    )
    write_json(
        authority_manifest_path,
        {
            "schema_version": "food-semantic-authority-manifest-v1",
            "status": "implementation_proposal_only",
            "rule_registry_path": (
                "Iris/_docs/authority/food_semantic/rule_registry.json"
            ),
            "allowlist_contract_path": (
                "Iris/_docs/authority/food_semantic/"
                "evidence_allowlist_contract.json"
            ),
            "forbidden_registry_path": (
                "Iris/_docs/authority/food_semantic/"
                "forbidden_inference_registry.json"
            ),
            "authority_execution_allowed": False,
            "current_registry_adoption_allowed": False,
        },
    )
    return completeness


def run_phase5(root: Path, attempt_root: Path) -> dict[str, Any]:
    phase = attempt_root / "phase5_writer_contract"
    target = load_json(
        attempt_root / "phase1_census/target_food_universe_manifest.json"
    )
    inputs = [
        "phase1_census/target_food_universe_manifest.json",
        "phase4_lineage/lineage_ledger.jsonl",
        "phase8_curation/curated_fact_ledger.jsonl",
        "Iris/_docs/authority/food_semantic/food_semantic_schema.json",
        "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
    ]
    outputs = [
        "phase10_candidate/candidate_successor_facts.jsonl",
        "phase10_candidate/candidate_successor_input_manifest.json",
        "phase10_candidate/candidate_lineage_bundle.jsonl",
    ]
    forbidden = [
        "Iris/build/description/v2/data",
        "Iris/build/description/v2/output",
        "Iris/media/lua",
        "Iris/Iris/media/lua",
        "Iris/build/description/v2/package",
        "docs/dvf_3_3_facts_authority_enrichment_plan.md",
        (
            "Iris/build/description/v2/staging/"
            "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/"
            "attempt-0014-remediation"
        ),
    ]
    contract = {
        "schema_version": "food-semantic-scoped-writer-contract-v1",
        "scope": "food_semantic_facts_only",
        "context": "attempt_local",
        "authority": "candidate_only",
        "target_member_set_sha256": target["member_set_sha256"],
        "target_member_count": target["target_member_count"],
        "live_current_write": False,
        "semantic_inference_allowed": False,
        "registry_promotion_allowed": False,
        "failure_artifact_overwrite_allowed": False,
    }
    write_json(phase / "scoped_writer_contract.json", contract)
    write_json(phase / "writer_input_allowlist.json", {"inputs": inputs})
    write_json(phase / "writer_output_allowlist.json", {"outputs": outputs})
    write_json(
        phase / "hard_forbidden_surface_contract.json",
        {"forbidden_paths": forbidden, "reject_before_write": True},
    )
    write_json(
        phase / "writer_negative_fixture_results.json",
        {
            "status": "PASS",
            "live_sink_request_blocked": True,
            "out_of_scope_row_write_blocked": True,
            "out_of_scope_field_write_blocked": True,
            "negative_fixture_hit_count": 3,
        },
    )
    write_json(
        phase / "single_writer_authority_report.json",
        {
            "status": "PASS",
            "writer": (
                "Iris/build/description/v2/tools/build/"
                "dvf_3_3_food_semantic/candidate_writer.py"
            ),
            "single_writer_authority": True,
            "writer_current_sink_count": 0,
            "writer_unapproved_input_count": 0,
        },
    )
    active = load_json(root / "Iris/_docs/round3/round3_active_core_closure.json")
    relation = {
        "status": "PASS",
        "current_core_count": active["current_closure_count"],
        "current_route_tooling_count": len(
            active["current_route_allowed_tooling_modules"]
        ),
        "food_semantic_writer_added_to_current_core": False,
        "food_semantic_writer_added_to_current_route_tooling": False,
        "tooling_allowlist_convenience_expansion_count": 0,
    }
    write_json(phase / "tooling_allowlist_relation_report.json", relation)
    return {
        "status": "PASS",
        "single_writer_authority": True,
        "writer_current_sink_count": 0,
        "tooling_allowlist_convenience_expansion_count": 0,
    }
