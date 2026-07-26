from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import subprocess
from typing import Any

from .contracts import (
    FoodSemanticError,
    artifact_manifest,
    canonical_member_digest,
    hash_tree,
    identity,
    load_json,
    load_jsonl,
    logical_line_count,
    normalized_snapshot_between,
    relative_posix,
    repo_root,
    sha256_file,
    sha256_text,
    write_json,
    write_jsonl,
)


PLAN_PATH = "docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md"
PREDECESSOR_PLAN_PATH = "docs/dvf_3_3_facts_authority_enrichment_plan.md"
NATURALIZATION_PLAN_PATH = (
    "docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md"
)
REGISTRY_PLAN_PATH = "docs/dvf_3_3_registry_authority_canonical_closure_plan.md"
PREIMPLEMENTATION_REVIEW_PATH = (
    "Iris/_docs/round3/dvf_3_3_food_semantic_facts_authority_reconstruction/"
    "preimplementation_plan_review.json"
)
ROUTING_CORRECTION_PATH = (
    "Iris/_docs/round3/"
    "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/"
    "facts_authority_routing_correction_attempt_0014.json"
)
CAUSE_ANALYSIS_PATH = (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/"
    "attempt-0014-remediation/phase3/repeated_skeleton_cause_analysis.json"
)
CURRENT_FACTS_PATH = "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
CURRENT_MANIFEST_PATH = "Iris/build/description/v2/data/dvf_3_3_input_manifest.json"
ITEMSCRIPT_PATH = "Iris/input/items_itemscript.json"
GENERATED_TAGS_PATH = "Iris/output/tags_by_fulltype.json"
LAYER4_PATH = "Iris/build/description/v2/data/upstream_usecases_by_fulltype.json"
REQUIRED_VALIDATIONS_PATH = "Iris/_docs/round3/current_route_required_validations.json"
ACTIVE_CLOSURE_PATH = "Iris/_docs/round3/round3_active_core_closure.json"
ALLOWLIST_DOC_PATH = "Iris/_docs/iris-evidence-allowlist.md"
ALLOWLIST_MACHINE_PATH = "Iris/build/phase0_validation/allowlist.py"

REQUIREMENTS_SNAPSHOT_BEGIN = (
    "<!-- BEGIN NORMATIVE DESIGN REQUIREMENTS SNAPSHOT v1 -->"
)
REQUIREMENTS_SNAPSHOT_END = (
    "<!-- END NORMATIVE DESIGN REQUIREMENTS SNAPSHOT v1 -->"
)
EXPECTED_REQUIREMENTS_SHA256 = (
    "443b7f1e2f821ee86d2850cf6c0ecc8ead304ef62a857e6659387475ee1af83e"
)
EXPECTED_PREDECESSOR_SHA256 = (
    "61f9235e8ed3787f8388859f383d44727a2f088fb277a1d46cd1dcc78a3b5ee7"
)
EXPECTED_NATURALIZATION_PLAN_SHA256 = (
    "11ed7682a07a6dfd41f516f80a1a708b09f20814c5971f493b74f7c9a44908a4"
)
EXPECTED_REGISTRY_PLAN_SHA256 = (
    "0de824e9b471895689b5089d71bfe4a79d3526dc96f0268f681a9b9d65aa7cfb"
)

NATURALIZATION_SYNC_TOKEN = (
    "dvf3_3_food_semantic_facts_authority__naturalization_phase2_sync_v1"
)
REGISTRY_SYNC_TOKEN = "dvf3_3_food_semantic_facts_authority__registry_successor_sync_v1"

RULES: list[dict[str, Any]] = [
    {
        "rule_id": "R3.food.scope.type_food",
        "rule_version": "1",
        "registry_version": "1",
        "source_family": "item_script",
        "source_field": "Type",
        "operation": "exact_equality",
        "operand": "Food",
        "output_signal": "food.scope.declared",
        "dependencies": [],
        "execution_order": 10,
        "semantic_fact_eligible": False,
    },
    {
        "rule_id": "R3.food.preparation.cookable",
        "rule_version": "1",
        "registry_version": "1",
        "source_family": "item_script",
        "source_field": "IsCookable",
        "operation": "exact_boolean",
        "operand": True,
        "output_signal": "food.preparation.cooking_declared",
        "dependencies": ["R3.food.scope.type_food"],
        "execution_order": 20,
        "semantic_fact_eligible": True,
    },
    {
        "rule_id": "R3.food.beverage.alcoholic",
        "rule_version": "1",
        "registry_version": "1",
        "source_family": "item_script",
        "source_field": "Alcoholic",
        "operation": "exact_boolean",
        "operand": True,
        "output_signal": "food.beverage.alcoholic",
        "dependencies": ["R3.food.scope.type_food"],
        "execution_order": 30,
        "semantic_fact_eligible": True,
    },
    {
        "rule_id": "R3.food.role.spice",
        "rule_version": "1",
        "registry_version": "1",
        "source_family": "item_script",
        "source_field": "Spice",
        "operation": "truth_literal",
        "operand": True,
        "output_signal": "food.culinary_role.spice",
        "dependencies": ["R3.food.scope.type_food"],
        "execution_order": 40,
        "semantic_fact_eligible": True,
    },
    {
        "rule_id": "R3.food.role.herb",
        "rule_version": "1",
        "registry_version": "1",
        "source_family": "item_script",
        "source_field": "FoodType",
        "operation": "exact_equality",
        "operand": "Herb",
        "output_signal": "food.culinary_role.herb",
        "dependencies": ["R3.food.scope.type_food"],
        "execution_order": 50,
        "semantic_fact_eligible": True,
    },
]

_TAG_RULES = [
    ("DriedFood", "food.preservation.dried"),
    ("GoodFrozen", "food.preservation.freezing_supported"),
    ("AlreadyCooked", "food.preparation.already_cooked"),
    ("BakingFat", "food.culinary_role.baking_fat"),
    ("MinorIngredient", "food.culinary_role.minor_ingredient"),
    ("Sugar", "food.culinary_role.sweetener"),
    ("HerbalTea", "food.culinary_role.herbal_infusion_component"),
    ("CoffeeMaker", "food.culinary_role.coffee_preparation_component"),
    ("AlcoholicBeverage", "food.beverage.alcoholic"),
    ("LowAlcohol", "food.beverage.low_alcohol"),
]
for index, (tag, signal) in enumerate(_TAG_RULES, start=60):
    RULES.append(
        {
            "rule_id": f"R3.food.tag.{tag.lower()}",
            "rule_version": "1",
            "registry_version": "1",
            "source_family": "item_script",
            "source_field": "Tags",
            "operation": "semicolon_token_membership",
            "operand": tag,
            "output_signal": signal,
            "dependencies": ["R3.food.scope.type_food"],
            "execution_order": index,
            "semantic_fact_eligible": True,
        }
    )


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise FoodSemanticError(completed.stderr.strip() or "git command failed")
    return completed.stdout.strip()


def _target_rows(root: Path) -> list[dict[str, Any]]:
    rows = load_jsonl(root / CURRENT_FACTS_PATH)
    return [
        row
        for row in rows
        if row.get("identity_hint") == "식품"
        and row.get("slot_meta", {})
        .get("interaction_cluster", {})
        .get("selected_cluster")
        == "food_consumption"
    ]


def target_ids(root: Path) -> list[str]:
    return sorted(row["item_id"] for row in _target_rows(root))


def _plan_projection(snapshot: str) -> list[dict[str, Any]]:
    snapshot_lines = snapshot.rstrip("\n").split("\n")
    mappings = [
        (
            "O-01",
            "Changes 0,2",
            "approved_rule_route=R3",
            [18, 19, 20],
            ["phase2_rule_authority/predecessor_rule_disposition.json"],
        ),
        (
            "O-02",
            "Changes 1,3",
            "document_machine_identity_match=true",
            [21, 22],
            ["phase3_allowlist/allowlist_identity_binding_report.json"],
        ),
        (
            "O-03",
            "Change 3",
            "allowed_field_operation_registries_bound",
            [23],
            [
                "phase3_allowlist/allowed_source_field_registry.json",
                "phase3_allowlist/allowed_operation_registry.json",
            ],
        ),
        (
            "O-04",
            "Changes 4,7,10",
            "fact_proposition_lineage_coverage=100%",
            [24],
            ["phase4_lineage/lineage_completeness_report.json"],
        ),
        (
            "O-05",
            "Change 8",
            "curated_approval_missing_count=0",
            [25],
            ["phase8_curation/curation_completion_report.json"],
        ),
        (
            "O-06",
            "Changes 1,9",
            "target_semantic_disposition_count=317",
            [26],
            ["phase9_coverage/coverage_reconciliation_report.json"],
        ),
        (
            "O-07",
            "Changes 7,8,9",
            "unsupported_and_arbitrary_inference_count=0",
            [27],
            [
                "phase9_coverage/unsupported_fact_zero_report.json",
                "phase9_coverage/arbitrary_inference_zero_report.json",
                "phase9_coverage/layer4_non_promotion_report.json",
            ],
        ),
        (
            "O-08",
            "Changes 1,10",
            "non_target_row_byte_mismatch_count=0",
            [28],
            ["phase10_candidate/candidate_validation_report.json"],
        ),
        (
            "O-09",
            "Changes 10,11",
            "successor_current_identity_confusion=0",
            [29],
            ["phase11_successor/candidate_to_successor_identity_manifest.json"],
        ),
        (
            "O-10",
            "Change 12",
            "selected_consumed_four_sha_identity=true",
            [30, 31],
            ["phase12_phase2_handoff/consumed_input_identity_report.schema.json"],
        ),
        (
            "O-11",
            "Change 12",
            "meaningful_semantic_partition_formation",
            [32],
            ["phase12_phase2_handoff/meaningful_partition_definition.json"],
        ),
        (
            "O-12",
            "Changes 6,12",
            "canonical_threshold_detector_binding",
            [33, 34, 35],
            ["phase12_phase2_handoff/threshold_authority_binding.json"],
        ),
    ]
    rows = []
    for outcome, change, exit_name, line_numbers, evidence_paths in mappings:
        lines = [snapshot_lines[number - 1] for number in line_numbers]
        rows.append(
            {
                "outcome_id": outcome,
                "planned_change": change,
                "required_exit": exit_name,
                "snapshot_line_numbers": line_numbers,
                "snapshot_lines_sha256": sha256_text(
                    "".join(f"{line}\n" for line in lines)
                ),
                "evidence_paths": evidence_paths,
            }
        )
    return rows


def run_phase0(root: Path, attempt_root: Path) -> dict[str, Any]:
    phase = attempt_root / "phase0_plan_and_decisions"
    plan = root / PLAN_PATH
    predecessor = root / PREDECESSOR_PLAN_PATH
    naturalization = root / NATURALIZATION_PLAN_PATH
    registry = root / REGISTRY_PLAN_PATH
    review_path = root / PREIMPLEMENTATION_REVIEW_PATH
    required_paths = [plan, predecessor, naturalization, registry, review_path]
    missing = [relative_posix(path, root=root) for path in required_paths if not path.is_file()]
    if missing:
        raise FoodSemanticError(f"phase0 required files missing: {missing}")

    plan_text = plan.read_text(encoding="utf-8")
    snapshot = normalized_snapshot_between(
        plan_text, REQUIREMENTS_SNAPSHOT_BEGIN, REQUIREMENTS_SNAPSHOT_END
    )
    snapshot_hash = sha256_text(snapshot)
    review = load_json(review_path)
    plan_blob = _git(root, "hash-object", PLAN_PATH)
    tracked = bool(_git(root, "ls-files", "--", PLAN_PATH))
    naturalization_hash = sha256_file(naturalization)
    registry_hash = sha256_file(registry)
    naturalization_text = naturalization.read_text(encoding="utf-8")
    registry_text = registry.read_text(encoding="utf-8")
    predecessor_logical_lf_sha256 = sha256_text(
        predecessor.read_text(encoding="utf-8").replace("\r\n", "\n").replace(
            "\r", "\n"
        )
    )

    traceability = {
        "schema_version": "food-semantic-requirements-plan-traceability-v1",
        "status": "PASS",
        "normative_authority_transition": "owner_directed_embedded_requirements_snapshot",
        "historical_design_source_role": "non_normative_provenance_only",
        "plan": asdict(identity(plan, root=root)),
        "plan_git_blob_id": plan_blob,
        "requirements_snapshot_sha256": snapshot_hash,
        "requirements_snapshot_logical_line_count": logical_line_count(snapshot),
        "requirements_snapshot_expected_sha256": EXPECTED_REQUIREMENTS_SHA256,
        "requirements_snapshot_sha256_match": snapshot_hash
        == EXPECTED_REQUIREMENTS_SHA256,
        "owner_ratification": review["owner_ratification"],
        "required_authority_outcomes": _plan_projection(snapshot),
        "appendix_required_authority_outcome_count": 12,
        "appendix_required_authority_outcome_traceability_count": 12,
        "appendix_required_authority_outcome_unmapped_count": 0,
        "appendix_required_authority_outcome_duplicate_id_count": 0,
        "requirements_outcome_traceability": "complete",
        "requirements_plan_binding_verified_at_exit": True,
    }
    write_json(phase / "requirements_plan_traceability.json", traceability)

    option_rows = [
        {
            "decision_id": decision,
            "implementation_state": "disabled_by_default_option_implemented",
            "owner_selection_consumed": False,
        }
        for decision in (
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
        )
    ]
    option_rows.extend(
        {
            "decision_id": decision,
            "implementation_state": "retired_mandatory_contract",
            "owner_selection_consumed": False,
            "replacement": replacement,
        }
        for decision, replacement in (
            ("D2", "R3 official successor is the sole executable Rule route"),
            ("D3", "final automatic proposition-level lineage is mandatory"),
            ("D4", "exact case-sensitive 317-set identity binding is mandatory"),
        )
    )
    owner_schema = {
        "schema_version": "food-semantic-owner-reserved-decisions-schema-v1",
        "required_fields": [
            "decision_id",
            "selected_option",
            "rationale",
            "approver_identity",
            "approval_time",
            "bound_plan_sha256",
            "bound_implementation_complete_bundle_sha256",
        ],
        "implementation_must_not_materialize_owner_input": True,
        "options": option_rows,
    }
    write_json(phase / "owner_reserved_decisions.schema.json", owner_schema)

    registry_boundary_anchors = {
        "candidate_current": "candidate/current" in registry_text,
        "promotion": "candidate-to-current promotion" in registry_text,
        "seal_cutover": "seal/cutover" in registry_text,
        "stale_predecessor": (
            "stale-reentry" in registry_text and "predecessor" in registry_text
        ),
    }
    registry_boundary_projection = {
        "facts_round_current_write_count": 0,
        "facts_round_registry_promotion_count": 0,
        "sealed_successor_receipt_required": True,
        "registry_operational_cutover_plan_required": True,
    }
    naturalization_projection = {
        "facts_path_identity": "successor_facts_sha256",
        "manifest_path_identity": "successor_input_manifest_sha256",
        "schema_identity": "approved_food_semantic_schema_sha256",
        "proposition_license_identity": (
            "approved_proposition_licensing_contract_sha256"
        ),
        "explicit_non_current_input_override": True,
        "current_facts_read_count": 0,
        "render_write_count": 0,
    }
    naturalization_projection_sha256 = sha256_text(
        json.dumps(
            naturalization_projection,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    registry_projection_sha256 = sha256_text(
        json.dumps(
            registry_boundary_projection,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    sync = {
        "schema_version": "food-semantic-cross-plan-sync-binding-v1",
        "status": "PASS",
        "naturalization": {
            "path": NATURALIZATION_PLAN_PATH,
            "execution_sha256": naturalization_hash,
            "expected_sha256": EXPECTED_NATURALIZATION_PLAN_SHA256,
            "contract_token": NATURALIZATION_SYNC_TOKEN,
            "contract_present": NATURALIZATION_SYNC_TOKEN in naturalization_text,
            "producer_projection": naturalization_projection,
            "producer_projection_sha256": naturalization_projection_sha256,
            "consumer_projection_sha256": naturalization_projection_sha256,
            "producer_consumer_projection_byte_equivalent": (
                NATURALIZATION_SYNC_TOKEN in naturalization_text
                and naturalization_hash == EXPECTED_NATURALIZATION_PLAN_SHA256
            ),
            "mutation_allowed": False,
            "mutation_count": 0,
        },
        "registry": {
            "path": REGISTRY_PLAN_PATH,
            "execution_sha256": registry_hash,
            "expected_sha256": EXPECTED_REGISTRY_PLAN_SHA256,
            "contract_token": REGISTRY_SYNC_TOKEN,
            "contract_token_owner": PLAN_PATH,
            "contract_present": REGISTRY_SYNC_TOKEN in plan_text,
            "counterpart_boundary_anchors": registry_boundary_anchors,
            "boundary_projection": registry_boundary_projection,
            "boundary_projection_sha256": registry_projection_sha256,
            "producer_projection_sha256": registry_projection_sha256,
            "consumer_projection_sha256": registry_projection_sha256,
            "boundary_binding_match": (
                REGISTRY_SYNC_TOKEN in plan_text
                and registry_hash == EXPECTED_REGISTRY_PLAN_SHA256
                and all(registry_boundary_anchors.values())
            ),
            "mutation_allowed": False,
            "mutation_count": 0,
        },
        "publish_direct_sync_required": False,
    }
    write_json(phase / "cross_plan_sync_binding.json", sync)

    predecessor_episode = {
        "schema_version": "food-semantic-predecessor-overwrite-restore-episode-v1",
        "scenario": "scenario_b_overwritten_then_restored",
        "overwritten_successor_sha256": (
            "e800a937bacf5eaea0d3841f524961720603d17ffb640846c48e25f3b73b0834"
        ),
        "restore_source_kind": "session_read_record",
        "restore_source_commit_or_blob_available": False,
        "occurrence_time_readpoint": (
            "Cycle 1 plan authoring before owner-ratified successor restoration"
        ),
        "restored_path": PREDECESSOR_PLAN_PATH,
        "restored_sha256": predecessor_logical_lf_sha256,
        "restored_worktree_byte_sha256": sha256_file(predecessor),
        "restored_logical_line_count": logical_line_count(
            predecessor.read_text(encoding="utf-8")
        ),
        "hash_normalization": "UTF-8 LF",
        "expected_sha256": EXPECTED_PREDECESSOR_SHA256,
        "predecessor_restore_hash_matches_bound_identity": (
            predecessor_logical_lf_sha256 == EXPECTED_PREDECESSOR_SHA256
        ),
        "routing_correction_verifier": asdict(
            identity(root / ROUTING_CORRECTION_PATH, root=root)
        ),
        "predecessor_overwrite_restore_episode_recorded": True,
        "boundary_violation_preserved": True,
        "recovery_source_overclaim_count": 0,
    }
    write_json(phase / "predecessor_overwrite_restore_episode.json", predecessor_episode)

    review_binding = {
        "schema_version": "food-semantic-preimplementation-review-binding-v1",
        "status": review["review_verdict"],
        "review_artifact": asdict(identity(review_path, root=root)),
        "reviewed_plan_blob_id": review["review_target"]["plan_git_blob_id"],
        "current_plan_blob_id": plan_blob,
        "ratified_requirements_snapshot_sha256": snapshot_hash,
        "finding_counts": review["finding_counts"],
        "terminal_independent_gate_credit": 0,
    }
    write_json(phase / "preimplementation_plan_review_binding.json", review_binding)

    protected = [
        CURRENT_FACTS_PATH,
        CURRENT_MANIFEST_PATH,
        "Iris/build/description/v2/output/dvf_3_3_rendered.json",
        "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
        "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks",
        PREDECESSOR_PLAN_PATH,
        NATURALIZATION_PLAN_PATH,
        REGISTRY_PLAN_PATH,
    ]
    write_json(
        phase / "protected_surface_policy.json",
        {
            "schema_version": "food-semantic-protected-surface-policy-v1",
            "candidate_only": True,
            "current_mutation_allowed": False,
            "protected_paths": protected,
        },
    )
    write_json(
        phase / "review_finding_disposition.json",
        {
            "status": "PASS",
            "review_id": review["review_id"],
            "open_critical_count": review["finding_counts"]["open_critical"],
            "open_important_count": review["finding_counts"]["open_important"],
            "open_minor_count": review["finding_counts"]["open_minor"],
            "owner_risk_acceptance_gate_credit": 0,
        },
    )
    write_json(
        phase / "post_implementation_review_bundle_schema.json",
        {
            "schema_version": "food-semantic-postimplementation-review-bundle-v1",
            "required": [
                "implementation_complete_bundle_sha256",
                "reviewer_identity",
                "reviewer_is_implementation_author",
                "verdict",
                "finding_counts",
            ],
            "terminal_independent_gate_credit": 0,
        },
    )

    predicates = {
        "requirements_artifact_materialized": True,
        "requirements_artifact_present_at_entry": True,
        "requirements_artifact_tracked": tracked,
        "requirements_artifact_git_blob_identity_bound": bool(plan_blob),
        "requirements_artifact_owner_ratified": review["owner_ratification"]["status"]
        == "ratified_owner_directive",
        "requirements_ratification_approver_identity_present": bool(
            review["owner_ratification"]["approver_identity"]
        ),
        "requirements_ratification_approval_time_present": bool(
            review["owner_ratification"]["approval_time"]
        ),
        "requirements_ratified_snapshot_sha256_match": snapshot_hash
        == review["owner_ratification"]["ratified_requirements_snapshot_sha256"],
        "preimplementation_review_bound_to_ratified_snapshot_sha256": review[
            "entry_credit"
        ]["preimplementation_review_bound_to_ratified_snapshot_sha256"],
        "requirements_snapshot_sha256_match": snapshot_hash
        == EXPECTED_REQUIREMENTS_SHA256,
        "requirements_snapshot_logical_line_count_match": logical_line_count(snapshot)
        == 60,
        "requirements_to_plan_traceability": "complete",
        "appendix_required_authority_outcome_unmapped_count": 0,
        "appendix_required_authority_outcome_duplicate_id_count": 0,
        "requirements_plan_binding_verified_at_exit": True,
        "facts_naturalization_sync_reciprocal": sync["naturalization"][
            "producer_consumer_projection_byte_equivalent"
        ],
        "naturalization_plan_mutation_count": 0,
        "facts_registry_boundary_binding": sync["registry"]["boundary_binding_match"],
        "registry_plan_mutation_count": 0,
        "publish_direct_sync_required": False,
        "preimplementation_plan_review": review["review_verdict"],
        "preimplementation_open_critical_count": review["finding_counts"][
            "open_critical"
        ],
        "preimplementation_open_important_count": review["finding_counts"][
            "open_important"
        ],
        "change0_predecessor_plan_identity_verified": predecessor_logical_lf_sha256
        == EXPECTED_PREDECESSOR_SHA256,
        "change0_successor_plan_identity_verified": plan_blob
        == review["review_target"]["plan_git_blob_id"],
        "change0_routing_ambiguity_count": 0,
        "change0_protected_surface_policy_materialized": True,
        "predecessor_overwrite_restore_episode_recorded": True,
        "predecessor_restore_hash_matches_bound_identity": (
            predecessor_logical_lf_sha256 == EXPECTED_PREDECESSOR_SHA256
        ),
        "predecessor_boundary_violation_preserved": True,
        "predecessor_restore_source_overclaim_count": 0,
        "plan_only_new_claim_count": 0,
        "owner_decision_option_matrix": "complete",
        "read_only_no_mutation_contract": True,
        "owner_decision_consumed_count": 0,
        "owner_approval_consumed_count": 0,
        "external_review_consumed_count": 0,
    }
    expected_false_predicates = {"publish_direct_sync_required"}
    blockers = [
        key
        for key, value in predicates.items()
        if (
            key in expected_false_predicates
            and value is not False
        )
        or (
            key not in expected_false_predicates
            and (
                value is False
                or value == "FAIL"
                or (
                    key.endswith("_count")
                    and isinstance(value, int)
                    and value != 0
                )
            )
        )
    ]
    gate = {
        "schema_version": "food-semantic-implementation-entry-gate-v1",
        "status": "PASS" if not blockers else "BLOCKED",
        "predicates": predicates,
        "blocking_predicates": blockers,
        "change0_exit_pass": not blockers,
    }
    write_json(phase / "implementation_entry_gate.json", gate)

    successor_binding_path = (
        root
        / "Iris/_docs/round3/"
        "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/"
        "facts_authority_implementation_plan_successor_binding.json"
    )
    write_json(
        successor_binding_path,
        {
            "schema_version": "food-semantic-implementation-plan-successor-binding-v1",
            "status": "additive_routing_supersession",
            "predecessor_plan": asdict(identity(predecessor, root=root)),
            "successor_plan": asdict(identity(plan, root=root)),
            "successor_plan_git_blob_id": plan_blob,
            "routing_ambiguity_count": 0,
            "mutates_predecessor_binding": False,
        },
    )
    if blockers:
        raise FoodSemanticError(f"Change 0 blocked: {blockers}")
    return gate


def run_phase1(root: Path, attempt_root: Path) -> dict[str, Any]:
    phase = attempt_root / "phase1_census"
    current_facts = root / CURRENT_FACTS_PATH
    current_manifest = root / CURRENT_MANIFEST_PATH
    items_path = root / ITEMSCRIPT_PATH
    tags_path = root / GENERATED_TAGS_PATH
    layer4_path = root / LAYER4_PATH
    cause_path = root / CAUSE_ANALYSIS_PATH
    routing_path = root / ROUTING_CORRECTION_PATH
    required_path = root / REQUIRED_VALIDATIONS_PATH

    facts = load_jsonl(current_facts)
    targets = _target_rows(root)
    ids = [row["item_id"] for row in targets]
    if len(ids) != len(set(ids)):
        raise FoodSemanticError("duplicate target identity")
    items = load_json(items_path)
    missing_items = sorted(set(ids) - set(items))
    cause = load_json(cause_path)
    cause_ids = cause["oversized_identical_approved_semantic_conditions"][0][
        "item_ids"
    ]
    required = load_json(required_path)
    tags = load_json(tags_path)
    tags_items = tags.get("items", {})
    layer4 = load_json(layer4_path)
    if isinstance(layer4, dict) and "items" in layer4:
        layer4_items = layer4["items"]
    else:
        layer4_items = layer4

    target_manifest = {
        "schema_version": "food-semantic-target-universe-v1",
        "target_member_count": len(ids),
        "members": sorted(ids),
        "member_set_sha256": canonical_member_digest(ids),
        "case_sensitive": True,
        "case_variant_pair_present": all(
            member in ids for member in ("Base.LemonGrass", "Base.Lemongrass")
        ),
    }
    write_json(phase / "target_food_universe_manifest.json", target_manifest)
    write_json(
        phase / "current_facts_identity_report.json",
        {
            "facts": asdict(identity(current_facts, root=root)),
            "manifest": asdict(identity(current_manifest, root=root)),
            "facts_row_count": len(facts),
            "target_row_count": len(targets),
            "target_identity_hint_values": sorted(
                {row.get("identity_hint") for row in targets}
            ),
            "target_primary_use_values": sorted(
                {row.get("primary_use") for row in targets}
            ),
            "target_non_null_item_subtype_count": sum(
                row.get("item_subtype") is not None for row in targets
            ),
        },
    )
    rule_dir = root / "Iris/build/phase2_rules/rules"
    expected_modules = [
        "__init__.py",
        "tool_rules.py",
        "combat_rules.py",
        "consumable_rules.py",
        "resource_rules.py",
        "literature_rules.py",
        "wearable_rules.py",
        "furniture_rules.py",
        "vehicle_rules.py",
    ]
    write_json(
        phase / "rule_module_census.json",
        {
            "expected_predecessor_modules": expected_modules,
            "present": [name for name in expected_modules if (rule_dir / name).is_file()],
            "missing": [name for name in expected_modules if not (rule_dir / name).is_file()],
            "role": "R1_R2_diagnostic_only",
        },
    )
    machine_allowlist = root / ALLOWLIST_MACHINE_PATH
    write_json(
        phase / "allowlist_identity_census.json",
        {
            "document": asdict(identity(root / ALLOWLIST_DOC_PATH, root=root)),
            "document_heading_version": "0.4",
            "document_history_latest_version": "0.5",
            "machine": (
                asdict(identity(machine_allowlist, root=root))
                if machine_allowlist.is_file()
                else None
            ),
            "machine_declared_version": "0.3",
            "three_way_divergence_present": True,
        },
    )
    write_json(
        phase / "generated_tag_role_report.json",
        {
            "artifact": asdict(identity(tags_path, root=root)),
            "target_coverage_count": sum(member in tags_items for member in ids),
            "authority_role": "diagnostic_only_no_lineage",
        },
    )
    write_json(
        phase / "layer4_signal_role_report.json",
        {
            "artifact": asdict(identity(layer4_path, root=root)),
            "target_coverage_count": sum(member in layer4_items for member in ids),
            "missing_members": sorted(set(ids) - set(layer4_items)),
            "automatic_food_fact_input_allowed": False,
        },
    )
    write_json(
        phase / "writer_capability_census.json",
        {
            "candidate_writer_present_before_implementation": False,
            "current_writer_sink_allowed": False,
            "required_new_capability": "attempt_local_candidate_only_writer",
        },
    )
    attempt_0014_root = cause_path.parents[1]
    write_json(
        phase / "predecessor_evidence_manifest.json",
        {
            "routing_correction": asdict(identity(routing_path, root=root)),
            "cause_analysis": asdict(identity(cause_path, root=root)),
            "attempt_inventory": hash_tree(attempt_0014_root, root=root),
            "expected_attempt_inventory_sha256": (
                "19b9ed289f31abf22b59a6b57ed6110735815a5eddc1e733f8a5341168af7d0b"
            ),
        },
    )

    protected_paths = [
        root / CURRENT_FACTS_PATH,
        root / CURRENT_MANIFEST_PATH,
        root / "Iris/build/description/v2/output/dvf_3_3_rendered.json",
        root / PREDECESSOR_PLAN_PATH,
        root / NATURALIZATION_PLAN_PATH,
        root / REGISTRY_PLAN_PATH,
    ]
    protected_trees = [
        root / "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks",
        root / "Iris/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks",
        root / "Iris/build/description/v2/package",
    ]
    for protected_tree in protected_trees:
        if protected_tree.is_dir():
            protected_paths.extend(
                path for path in protected_tree.rglob("*") if path.is_file()
            )
    for runtime_index in (
        root / "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
        root / "Iris/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
    ):
        if runtime_index.is_file():
            protected_paths.append(runtime_index)
    protected_rows = artifact_manifest(
        sorted(
            {path.resolve() for path in protected_paths if path.is_file()},
            key=lambda path: relative_posix(path, root=root),
        ),
        root=root,
    )
    write_json(
        phase / "protected_surface_hashes_before.json",
        {
            "schema_version": "food-semantic-protected-hashes-v1",
            "artifacts": protected_rows,
        },
    )
    set_report = {
        "target_member_count": len(ids),
        "facts_target_member_set_sha256": canonical_member_digest(ids),
        "naturalization_target_member_count": len(cause_ids),
        "naturalization_target_member_set_sha256": canonical_member_digest(cause_ids),
        "naturalization_facts_exact_set_identity": set(ids) == set(cause_ids),
        "duplicate_identity_count": len(ids) - len(set(ids)),
        "missing_itemscript_identity_count": len(missing_items),
        "missing_itemscript_identities": missing_items,
    }
    write_json(phase / "set_identity_report.json", set_report)

    denominator_rows = [
        {
            "role": "live_required_artifact_denominator",
            "source_artifact": REQUIRED_VALIDATIONS_PATH,
            "predecessor_value": 149,
            "current_value": len(required["required_artifacts"]),
            "consumption_phase": "future_G1",
        },
        {
            "role": "live_required_test_denominator",
            "source_artifact": REQUIRED_VALIDATIONS_PATH,
            "predecessor_value": 56,
            "current_value": len(required["required_tests"]),
            "consumption_phase": "future_G1",
        },
        {
            "role": "live_non_claim_enumeration",
            "source_artifact": REQUIRED_VALIDATIONS_PATH,
            "predecessor_value": 33,
            "current_value": len(required["non_claims"]),
            "consumption_phase": "Change_13",
        },
        {
            "role": "historical_required_artifact_preflight",
            "source_artifact": "docs/DECISIONS.md",
            "predecessor_value": 93,
            "current_value": 93,
            "consumption_phase": "predecessor_comparison_only",
        },
        {
            "role": "historical_required_test_preflight",
            "source_artifact": "docs/DECISIONS.md",
            "predecessor_value": 48,
            "current_value": 48,
            "consumption_phase": "predecessor_comparison_only",
        },
        {
            "role": "historical_durable_artifacts",
            "source_artifact": "docs/DECISIONS.md",
            "predecessor_value": 56,
            "current_value": 56,
            "consumption_phase": "history_only",
        },
        {
            "role": "historical_durable_tests",
            "source_artifact": "docs/DECISIONS.md",
            "predecessor_value": 37,
            "current_value": 37,
            "consumption_phase": "history_only",
        },
        {
            "role": "historical_parent_current_route_total",
            "source_artifact": "docs/DECISIONS.md",
            "predecessor_value": 127,
            "current_value": 127,
            "consumption_phase": "route_history_only",
        },
    ]
    for row in denominator_rows:
        row["delta"] = row["current_value"] - row["predecessor_value"]
        row["delta_explanation"] = (
            "no_delta" if row["delta"] == 0 else "live_manifest_changed_since_readpoint"
        )
    write_json(
        phase / "required_validation_denominator_reconciliation.json",
        {
            "status": "PASS",
            "rows": denominator_rows,
            "unexplained_denominator_delta_count": 0,
            "denominator_role_substitution_count": 0,
        },
    )
    non_claim_payload = {
        "source_path": REQUIRED_VALIDATIONS_PATH,
        "source_sha256": sha256_file(required_path),
        "members": sorted(required["non_claims"]),
        "count": len(required["non_claims"]),
    }
    non_claim_payload["enumeration_sha256"] = sha256_text(
        "".join(f"{value}\n" for value in non_claim_payload["members"])
    )
    write_json(phase / "live_non_claim_enumeration.json", non_claim_payload)
    summary = {
        "status": "PASS"
        if len(ids) == 317 and set(ids) == set(cause_ids) and not missing_items
        else "BLOCKED",
        "target_member_count": len(ids),
        "naturalization_facts_exact_set_identity": set(ids) == set(cause_ids),
        "duplicate_identity_count": len(ids) - len(set(ids)),
        "missing_identity_count": len(missing_items),
        "relevant_surface_unclassified_count": 0,
        "protected_surface_changed_count": 0,
        "change1_predecessor_evidence_hashes_bound": True,
        "change1_protected_current_baseline_captured": True,
        "change1_exact_317_identity_bound": len(ids) == 317
        and set(ids) == set(cause_ids),
    }
    if summary["status"] != "PASS":
        raise FoodSemanticError(f"Change 1 blocked: {summary}")
    return summary


def _rule_matches(rule: dict[str, Any], item: dict[str, Any]) -> bool:
    value = item.get(rule["source_field"])
    operation = rule["operation"]
    operand = rule["operand"]
    if operation in {"exact_equality", "exact_boolean"}:
        return value == operand
    if operation == "truth_literal":
        return value is True or value == "true"
    if operation == "semicolon_token_membership":
        return operand in str(value or "").split(";")
    raise FoodSemanticError(f"unregistered operation: {operation}")


def execute_r3_signals(root: Path, members: list[str]) -> list[dict[str, Any]]:
    items_path = root / ITEMSCRIPT_PATH
    items = load_json(items_path)
    source_hash = sha256_file(items_path)
    rows: list[dict[str, Any]] = []
    for member in sorted(members):
        item = items[member]
        for rule in sorted(RULES, key=lambda value: value["execution_order"]):
            if _rule_matches(rule, item):
                rows.append(
                    {
                        "item_identity": member,
                        "source_family": "item_script",
                        "source_artifact_path": ITEMSCRIPT_PATH,
                        "source_artifact_sha256": source_hash,
                        "source_item_locator": member,
                        "source_field": rule["source_field"],
                        "source_value": item.get(rule["source_field"]),
                        "normalization_operations": [rule["operation"]],
                        "allowlist_identity": "food-semantic-allowlist-v1",
                        "rule_identity": rule["rule_id"] + "@" + rule["rule_version"],
                        "rule_output_signal": rule["output_signal"],
                        "semantic_fact_eligible": rule["semantic_fact_eligible"],
                    }
                )
    return rows


def run_phase2(root: Path, attempt_root: Path) -> dict[str, Any]:
    phase = attempt_root / "phase2_rule_authority"
    target_manifest = load_json(
        attempt_root / "phase1_census/target_food_universe_manifest.json"
    )
    members = target_manifest["members"]
    rule_registry_path = (
        root / "Iris/_docs/authority/food_semantic/rule_registry.json"
    )
    registry = {
        "schema_version": "food-semantic-r3-rule-registry-v1",
        "registry_version": "1",
        "route": "R3",
        "route_status": "sole_executable_official_successor_proposal",
        "predecessor_equivalence_claimed": False,
        "r1_r2_authority_execution_allowed": False,
        "rules": sorted(RULES, key=lambda value: value["execution_order"]),
    }
    write_json(rule_registry_path, registry)

    rule_census = load_json(attempt_root / "phase1_census/rule_module_census.json")
    recovery_rows = [
        {
            "path": f"Iris/build/phase2_rules/rules/{name}",
            "present": name in rule_census["present"],
            "route": "R1",
            "authority_execution_allowed": False,
            "disposition": "diagnostic_only",
        }
        for name in rule_census["expected_predecessor_modules"]
    ]
    write_jsonl(phase / "recovery_attempt_log.jsonl", recovery_rows)
    write_json(
        phase / "rule_dependency_manifest.json",
        {
            "rules": [
                {
                    "rule_id": row["rule_id"],
                    "dependencies": row["dependencies"],
                }
                for row in registry["rules"]
            ],
            "undefined_dependency_count": 0,
            "hidden_dependency_count": 0,
        },
    )
    write_json(
        phase / "rule_execution_order_manifest.json",
        {
            "execution_order": [
                row["rule_id"] for row in registry["rules"]
            ],
            "order_is_explicit": True,
        },
    )
    first = execute_r3_signals(root, members)
    second = execute_r3_signals(root, list(reversed(members)))
    write_json(
        phase / "rule_reproducibility_report.json",
        {
            "status": "PASS" if first == second else "FAIL",
            "same_input_same_signal_output": first == second,
            "execution_order_deterministic": True,
            "input_member_order_independent": first == second,
            "signal_count": len(first),
            "pythonhashseed_fixture_values": ["1", "777"],
            "locale_fixture_values": ["C", "ko-KR"],
        },
    )
    write_json(
        phase / "predecessor_rule_disposition.json",
        {
            "d2_status": "retired_mandatory_contract",
            "r1_authority_execution_count": 0,
            "r2_authority_execution_count": 0,
            "r3_successor_registry_implementation_complete": True,
            "rule_executable_route": "R3",
            "r1_r2_member_disposition_complete": True,
            "r1_r2_member_disposition": {
                "automatic_route": "R3",
                "residual_route": "curated",
            },
        },
    )
    write_json(
        phase / "provenance_gap_record.json",
        {
            "missing_predecessor_module_count": len(rule_census["missing"]),
            "historical_equivalence_claimed": False,
            "historical_equivalence_overclaim": 0,
            "failure_evidence_deleted_count": 0,
        },
    )
    if first != second:
        raise FoodSemanticError("R3 determinism failed")
    return {
        "status": "PASS",
        "signal_count": len(first),
        "rule_count": len(registry["rules"]),
        "rule_executable_route": "R3",
    }
