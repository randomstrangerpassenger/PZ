from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Callable

from .contracts import (
    FoodSemanticError,
    canonical_batch_id,
    canonical_jsonl_bytes,
    canonical_proposition_id,
    load_json,
    load_jsonl,
    relative_posix,
    sha256_bytes,
    sha256_file,
    write_json,
    write_jsonl,
)
from .curation_proposals import (
    AI_CURATOR_IDENTITY,
    _review_batch_proposal_hash,
    approval_packet_schema,
    assert_curation_authority_sink,
    parse_script_items,
    validate_batch_approvals,
)


REWORK_RESOLUTION_VERSION = "food-semantic-curation-rework-resolution-v1"
EXPECTED_REWORK_ITEMS = ("Base.Comfrey", "Base.Plantain")
FORAGING_PATH = Path("lua/shared/Foraging/forageDefinitions.lua")
RECIPE_PATH = Path("scripts/recipes.txt")


def _extract_braced_block(
    path: Path,
    *,
    start_matches: Callable[[str], bool],
) -> tuple[int, int, str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = next(
        (index for index, line in enumerate(lines) if start_matches(line)),
        None,
    )
    if start is None:
        raise FoodSemanticError(f"source block start not found: {path}")
    depth = 0
    opened = False
    for index in range(start, len(lines)):
        line = lines[index]
        depth += line.count("{")
        if "{" in line:
            opened = True
        depth -= line.count("}")
        if opened and depth == 0:
            block = "\n".join(lines[start : index + 1]) + "\n"
            return start + 1, index + 1, block
    raise FoodSemanticError(f"unterminated source block: {path}:{start + 1}")


def _source_record(
    path: Path,
    *,
    root: Path,
    start_line: int,
    end_line: int,
    block: str,
    source_family: str,
    locator: str,
    reviewed_fields: dict[str, Any],
    normalization_operations: list[str],
) -> dict[str, Any]:
    return {
        "source_family": source_family,
        "source_artifact_path": relative_posix(path, root=root),
        "source_artifact_sha256": sha256_file(path),
        "source_item_locator": (
            f"{locator}@L{start_line}-L{end_line}"
        ),
        "source_block_sha256": sha256_bytes(block.encode("utf-8")),
        "reviewed_fields": reviewed_fields,
        "forbidden_fields_present_but_not_consumed": [],
        "normalization_operations": normalization_operations,
    }


def _build_resolution_proposal(
    root: Path,
    *,
    item_identity: str,
    prior_rework: dict[str, Any],
    schema_sha256: str,
    proposition_license_sha256: str,
) -> dict[str, Any]:
    short_name = item_identity.split(".", 1)[1]
    script_candidates = parse_script_items(root / "scripts").get(
        item_identity,
        [],
    )
    script_candidates = [
        candidate
        for candidate in script_candidates
        if relative_posix(candidate.source_path, root=root)
        == "scripts/newitems.txt"
    ]
    if len(script_candidates) != 1:
        raise FoodSemanticError(
            f"expected one raw item source for {item_identity}"
        )
    script_item = script_candidates[0]
    if script_item.fields.get("Type") != "Normal":
        raise FoodSemanticError(
            f"rework resolution expects Type=Normal: {item_identity}"
        )
    script_lines = script_item.source_path.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines()
    script_block = (
        "\n".join(
            script_lines[script_item.start_line - 1 : script_item.end_line]
        )
        + "\n"
    )
    raw_source = _source_record(
        script_item.source_path,
        root=root,
        start_line=script_item.start_line,
        end_line=script_item.end_line,
        block=script_block,
        source_family="raw_item_script_human_review_context",
        locator=item_identity,
        reviewed_fields={"Type": "Normal"},
        normalization_operations=[
            "exact_field_read",
            "human_semantic_review",
        ],
    )
    raw_source["forbidden_fields_present_but_not_consumed"] = sorted(
        field
        for field in ("DisplayCategory", "DisplayName")
        if field in script_item.fields
    )

    foraging_path = root / FORAGING_PATH
    forage_start, forage_end, forage_block = _extract_braced_block(
        foraging_path,
        start_matches=lambda line: bool(
            re.match(
                rf"^\s*{re.escape(short_name)}\s*=\s*\{{\s*$",
                line,
            )
        ),
    )
    required_forage_tokens = (
        f'type = "{item_identity}"',
        'categories = { "MedicinalPlants" }',
        'recipes = { "Herbalist" }',
    )
    if not all(token in forage_block for token in required_forage_tokens):
        raise FoodSemanticError(
            f"foraging medicinal-plant binding mismatch: {item_identity}"
        )
    foraging_source = _source_record(
        foraging_path,
        root=root,
        start_line=forage_start,
        end_line=forage_end,
        block=forage_block,
        source_family="foraging_definition_human_review_context",
        locator=f"{short_name}[type={item_identity}]",
        reviewed_fields={
            "type": item_identity,
            "categories": ["MedicinalPlants"],
            "recipes": ["Herbalist"],
        },
        normalization_operations=[
            "exact_item_identity_join",
            "exact_category_membership_read",
            "human_semantic_review",
        ],
    )

    recipe_path = root / RECIPE_PATH
    recipe_start, recipe_end, recipe_block = _extract_braced_block(
        recipe_path,
        start_matches=lambda line: bool(
            re.match(
                rf"^\s*recipe\s+Make\s+{re.escape(short_name)}\s+Poultice\s*$",
                line,
            )
        ),
    )
    required_recipe_tokens = (
        f"{short_name}=5",
        f"Result:{short_name}Cataplasm",
        "Category:Health",
    )
    if not all(token in recipe_block for token in required_recipe_tokens):
        raise FoodSemanticError(
            f"health recipe binding mismatch: {item_identity}"
        )
    recipe_source = _source_record(
        recipe_path,
        root=root,
        start_line=recipe_start,
        end_line=recipe_end,
        block=recipe_block,
        source_family="recipe_definition_human_review_context",
        locator=f"Make {short_name} Poultice",
        reviewed_fields={
            "ingredient_item_identity": item_identity,
            "ingredient_count": 5,
            "result_item_identity": f"Base.{short_name}Cataplasm",
            "category": "Health",
        },
        normalization_operations=[
            "exact_recipe_ingredient_join",
            "exact_recipe_category_read",
            "human_semantic_review",
        ],
    )

    proposition_id = canonical_proposition_id(
        item_identity,
        "ingredient_origin",
        "plant",
    )
    return {
        "item_identity": item_identity,
        "curator_identity": AI_CURATOR_IDENTITY,
        "curation_mode": (
            "ai_rework_resolution_requiring_human_semantic_approval"
        ),
        "disposition": "proposed",
        "confidence": "high",
        "reviewed_source_set": [
            raw_source,
            foraging_source,
            recipe_source,
        ],
        "consumed_reviewed_fields": [
            "foraging_definition.type",
            "foraging_definition.categories",
        ],
        "forbidden_context_field_consumed_count": 0,
        "forbidden_context_operation_consumed_count": 0,
        "schema_sha256": schema_sha256,
        "proposition_license_sha256": proposition_license_sha256,
        "approval_status": "pending_human_semantic_approval",
        "semantic_approver": None,
        "approval_record": None,
        "proposition_id": proposition_id,
        "fact_axis": "ingredient_origin",
        "fact_value": "plant",
        "authority_class": "curated",
        "judgment_rule": (
            "curated_exact_foraging_medicinal_plant_category"
        ),
        "rationale": (
            "The exact foraging record joins this FullType to the "
            "MedicinalPlants category, supporting only plant origin. "
            "Type=Normal and the Health poultice recipe are retained as "
            "negative scope controls: no food-consumption, meal, or culinary "
            "role proposition is claimed."
        ),
        "resolves_prior_rework": {
            "reason": prior_rework["rework_reason"],
            "approval_record": prior_rework["approval_record"],
        },
    }


def validate_rework_resolution_proposals(
    root: Path,
    *,
    prior_authority_root: Path,
    proposals: list[dict[str, Any]],
) -> dict[str, Any]:
    prior_rework = load_jsonl(
        prior_authority_root / "phase8_curation/curation_rework_queue.jsonl"
    )
    expected_items = sorted(row["item_identity"] for row in prior_rework)
    proposed_items = sorted(row["item_identity"] for row in proposals)
    schema = load_json(
        root / "Iris/_docs/authority/food_semantic/food_semantic_schema.json"
    )
    allowed = {
        axis["axis"]: {value["value"] for value in axis["values"]}
        for axis in schema["axes"]
    }
    blockers: list[str] = []
    if expected_items != list(EXPECTED_REWORK_ITEMS):
        blockers.append("prior_rework_exact_set_mismatch")
    if proposed_items != expected_items:
        blockers.append("resolution_proposal_exact_set_mismatch")
    if len({row["proposition_id"] for row in proposals}) != len(proposals):
        blockers.append("duplicate_resolution_proposition")
    for row in proposals:
        if row["disposition"] != "proposed":
            blockers.append("resolution_not_proposed")
        if row["fact_value"] not in allowed.get(row["fact_axis"], set()):
            blockers.append("resolution_schema_violation")
        if (
            row["fact_axis"] != "ingredient_origin"
            or row["fact_value"] != "plant"
        ):
            blockers.append("resolution_scope_expansion")
        if row["forbidden_context_field_consumed_count"] != 0:
            blockers.append("forbidden_context_field_consumed")
        if row["forbidden_context_operation_consumed_count"] != 0:
            blockers.append("forbidden_context_operation_consumed")
        forage = row["reviewed_source_set"][1]["reviewed_fields"]
        if (
            forage.get("type") != row["item_identity"]
            or forage.get("categories") != ["MedicinalPlants"]
        ):
            blockers.append("medicinal_plant_source_binding_mismatch")
        if row["reviewed_source_set"][0]["reviewed_fields"] != {
            "Type": "Normal"
        }:
            blockers.append("non_food_scope_control_missing")
        if row["reviewed_source_set"][2]["reviewed_fields"].get(
            "category"
        ) != "Health":
            blockers.append("health_scope_control_missing")
    return {
        "schema_version": (
            "food-semantic-curation-rework-resolution-validation-v1"
        ),
        "status": "PASS" if not blockers else "FAIL",
        "prior_rework_count": len(prior_rework),
        "resolution_proposal_count": len(proposals),
        "resolved_item_count": len(set(expected_items) & set(proposed_items)),
        "proposed_items": proposed_items,
        "proposed_proposition_count": len(proposals),
        "forbidden_context_field_consumed_count": sum(
            row["forbidden_context_field_consumed_count"]
            for row in proposals
        ),
        "forbidden_context_operation_consumed_count": sum(
            row["forbidden_context_operation_consumed_count"]
            for row in proposals
        ),
        "blockers": sorted(set(blockers)),
        "authority_effect": False,
    }


def write_rework_resolution_bundle(
    root: Path,
    attempt_root: Path,
    *,
    prior_authority_root: Path,
    output_root: Path,
) -> dict[str, Any]:
    prior_rework = load_jsonl(
        prior_authority_root / "phase8_curation/curation_rework_queue.jsonl"
    )
    prior_by_item = {
        row["item_identity"]: row for row in prior_rework
    }
    schema_path = (
        root / "Iris/_docs/authority/food_semantic/food_semantic_schema.json"
    )
    license_path = (
        root
        / "Iris/_docs/authority/food_semantic/"
        "proposition_licensing_contract.json"
    )
    schema_sha256 = sha256_file(schema_path)
    license_sha256 = sha256_file(license_path)
    proposals = [
        _build_resolution_proposal(
            root,
            item_identity=item_identity,
            prior_rework=prior_by_item[item_identity],
            schema_sha256=schema_sha256,
            proposition_license_sha256=license_sha256,
        )
        for item_identity in EXPECTED_REWORK_ITEMS
    ]
    validation = validate_rework_resolution_proposals(
        root,
        prior_authority_root=prior_authority_root,
        proposals=proposals,
    )
    if validation["status"] != "PASS":
        raise FoodSemanticError(
            f"rework resolution proposal validation failed: "
            f"{validation['blockers']}"
        )
    implementation_bundle_path = (
        attempt_root / "phase13_closeout/implementation_complete_bundle.json"
    )
    bundle_sha256 = sha256_file(implementation_bundle_path)
    queue_rows = [
        {
            "item_identity": row["item_identity"],
            "proposition_id": row["proposition_id"],
        }
        for row in proposals
    ]
    queue_sha256 = sha256_bytes(canonical_jsonl_bytes(queue_rows))
    ordered_members = [row["item_identity"] for row in proposals]
    batch = {
        "schema_version": REWORK_RESOLUTION_VERSION,
        "approval_state": "pending_human_semantic_approval",
        "authority_effect": False,
        "batch": {
            "batch_id": canonical_batch_id(
                schema_sha256,
                queue_sha256,
                ordered_members,
            ),
            "schema_sha256": schema_sha256,
            "queue_sha256": queue_sha256,
            "ordered_members": ordered_members,
            "member_count": len(ordered_members),
            "authority_class": "curated",
            "approval_state": "unapproved",
        },
        "members": proposals,
        "bound_implementation_complete_bundle_sha256": bundle_sha256,
        "curator_identity": AI_CURATOR_IDENTITY,
        "owner_approval": None,
    }
    batch["proposal_content_sha256"] = _review_batch_proposal_hash(batch)
    write_jsonl(
        output_root / "curation_rework_resolution_proposals.jsonl",
        proposals,
        write_once=False,
    )
    write_json(
        output_root / "curation_rework_resolution_validation.json",
        validation,
        write_once=False,
    )
    review_root = output_root / "review_batches"
    filename = batch["batch"]["batch_id"].replace(":", "_") + ".json"
    write_json(review_root / filename, batch, write_once=False)
    write_json(
        output_root / "curation_batch_approval.schema.json",
        approval_packet_schema(),
        write_once=False,
    )
    summary = {
        "schema_version": REWORK_RESOLUTION_VERSION,
        "status": "READY_FOR_HUMAN_BATCH_REVIEW",
        "bound_attempt_id": attempt_root.name,
        "bound_implementation_complete_bundle_sha256": bundle_sha256,
        "bound_prior_authority_execution_receipt_sha256": sha256_file(
            prior_authority_root / "authority_execution_receipt.json"
        ),
        "curator_identity": AI_CURATOR_IDENTITY,
        "target_count": len(proposals),
        "proposed_proposition_count": len(proposals),
        "needs_rework_count": 0,
        "review_batch_count": 1,
        "maximum_batch_member_count": len(proposals),
        "human_semantic_approval_required": True,
        "authority_effect": False,
        "validation_status": validation["status"],
        "proposal_ledger_sha256": sha256_file(
            output_root / "curation_rework_resolution_proposals.jsonl"
        ),
    }
    write_json(
        output_root / "curation_proposal_summary.json",
        summary,
        write_once=False,
    )
    markdown = "\n".join(
        [
            "# Food Semantic Rework Resolution Review",
            "",
            "This packet proposes only `ingredient_origin=plant` for the two "
            "previously acknowledged rework items.",
            "",
            "It does not claim either item is food, edible, a meal component, "
            "or a culinary herb.",
            "",
            "| Item | Exact proposal | Primary reviewed signal |",
            "|---|---|---|",
            "| `Base.Comfrey` | `ingredient_origin=plant` | "
            "`categories={MedicinalPlants}` |",
            "| `Base.Plantain` | `ingredient_origin=plant` | "
            "`categories={MedicinalPlants}` |",
            "",
            f"Batch: `{batch['batch']['batch_id']}`",
            "",
            f"Proposal SHA-256: `{batch['proposal_content_sha256']}`",
            "",
            "Authority effect before owner approval: `false`",
            "",
        ]
    )
    (output_root / "curation_rework_resolution_review.md").parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    (output_root / "curation_rework_resolution_review.md").write_text(
        markdown,
        encoding="utf-8",
    )
    return summary


def materialize_resolved_curation(
    proposal_root: Path,
    *,
    prior_authority_root: Path,
    successor_authority_root: Path,
    owner_decisions_path: Path,
) -> dict[str, Any]:
    assert_curation_authority_sink(successor_authority_root)
    validation = validate_batch_approvals(
        proposal_root,
        owner_decisions_path=owner_decisions_path,
        require_all_approved=True,
    )
    if validation["status"] != "PASS":
        raise FoodSemanticError(
            "rework resolution approval validation is not PASS"
        )
    prior_phase = prior_authority_root / "phase8_curation"
    prior_report = load_json(
        prior_phase / "curation_authority_execution_report.json"
    )
    prior_rework = load_jsonl(
        prior_phase / "curation_rework_queue.jsonl"
    )
    if (
        prior_report.get("status") != "PASS_WITH_REWORK"
        or sorted(row["item_identity"] for row in prior_rework)
        != list(EXPECTED_REWORK_ITEMS)
    ):
        raise FoodSemanticError("prior authority rework state mismatch")
    batches = sorted(
        (
            load_json(path)
            for path in (proposal_root / "review_batches").glob("*.json")
        ),
        key=lambda row: row["batch"]["batch_id"],
    )
    members = [member for batch in batches for member in batch["members"]]
    if sorted(row["item_identity"] for row in members) != list(
        EXPECTED_REWORK_ITEMS
    ):
        raise FoodSemanticError("resolution member set mismatch")

    curated_rows = load_jsonl(prior_phase / "curated_fact_ledger.jsonl")
    approval_rows = load_jsonl(
        prior_phase / "semantic_authority_approval_ledger.jsonl"
    )
    event_rows = load_jsonl(prior_phase / "curation_event_ledger.jsonl")
    existing_items = {row["item_identity"] for row in curated_rows}
    existing_propositions = {
        row["fact_proposition_identity"] for row in curated_rows
    }
    for batch in batches:
        approval = batch["owner_approval"]
        assert approval is not None
        approval_record = (
            f"{batch['batch']['batch_id']}@"
            f"{batch['proposal_content_sha256']}"
        )
        for member in batch["members"]:
            if member["item_identity"] in existing_items:
                raise FoodSemanticError("resolution duplicates curated item")
            if member["proposition_id"] in existing_propositions:
                raise FoodSemanticError(
                    "resolution duplicates curated proposition"
                )
            pending_id = f"curation-pending:{member['item_identity']}"
            curated_rows.append(
                {
                    "item_identity": member["item_identity"],
                    "fact_proposition_identity": member["proposition_id"],
                    "fact_field": member["fact_axis"],
                    "fact_value": member["fact_value"],
                    "authority_class": "curated",
                    "approval_status": "owner_approved",
                    "signal_to_fact_mapping_id": (
                        "curated.owner_approved."
                        f"{member['proposition_id']}"
                    ),
                    "curator_identity": member["curator_identity"],
                    "reviewed_source_set": member["reviewed_source_set"],
                    "rationale": member["rationale"],
                    "schema_sha256": member["schema_sha256"],
                    "proposition_license_sha256": member[
                        "proposition_license_sha256"
                    ],
                    "semantic_approver": approval["approver_identity"],
                    "approval_record": approval_record,
                }
            )
            approval_rows.append(
                {
                    "proposition_id": member["proposition_id"],
                    "item_identity": member["item_identity"],
                    "batch_id": batch["batch"]["batch_id"],
                    "proposal_content_sha256": batch[
                        "proposal_content_sha256"
                    ],
                    "approval_state": "approved",
                    "semantic_approver": approval["approver_identity"],
                    "approval_time": approval["approval_time"],
                    "approval_rationale": approval["rationale"],
                    "approval_record": approval_record,
                }
            )
            event_rows.extend(
                [
                    {
                        "event_id": f"{pending_id}:superseded:2",
                        "proposition_id": pending_id,
                        "event": "superseded",
                        "batch_id": batch["batch"]["batch_id"],
                        "superseded_by_proposition_id": member[
                            "proposition_id"
                        ],
                        "authority_effect": False,
                    },
                    {
                        "event_id": (
                            f"{member['proposition_id']}:accepted:2"
                        ),
                        "proposition_id": member["proposition_id"],
                        "event": "accepted",
                        "batch_id": batch["batch"]["batch_id"],
                        "authority_effect": True,
                    },
                ]
            )

    curated_rows.sort(
        key=lambda row: (
            row["item_identity"],
            row["fact_field"],
            row["fact_value"],
            row["fact_proposition_identity"],
        )
    )
    approval_rows.sort(
        key=lambda row: (
            row["item_identity"],
            row["proposition_id"],
        )
    )
    if len({row["event_id"] for row in event_rows}) != len(event_rows):
        raise FoodSemanticError("duplicate curation event after resolution")
    phase = successor_authority_root / "phase8_curation"
    write_jsonl(phase / "curated_fact_ledger.jsonl", curated_rows)
    write_jsonl(
        phase / "semantic_authority_approval_ledger.jsonl",
        approval_rows,
    )
    write_jsonl(phase / "curation_event_ledger.jsonl", event_rows)
    write_jsonl(phase / "curation_rework_queue.jsonl", [])
    event_path = phase / "curation_event_ledger.jsonl"
    write_json(
        phase / "curation_checkpoint.json",
        {
            "last_fully_committed_batch_id": (
                batches[-1]["batch"]["batch_id"]
            ),
            "event_ledger_sha256": sha256_file(event_path),
            "accepted_count": len(curated_rows),
            "rejected_count": 0,
            "rework_count": 0,
            "next_canonical_cursor": None,
            "authority_execution_started": True,
        },
    )
    report = {
        "schema_version": (
            "food-semantic-curation-rework-materialization-v1"
        ),
        "status": "PASS_COMPLETE",
        "approved_curated_proposition_count": len(curated_rows),
        "resolved_prior_rework_count": len(members),
        "unresolved_rework_count": 0,
        "approved_batch_count": validation["approved_batch_count"],
        "duplicate_approval_event_count": 0,
        "curated_schema_violation_count": 0,
        "curated_approval_missing_count": 0,
        "candidate_generation_authorized": True,
        "current_mutation_authorized": False,
        "bound_prior_authority_execution_receipt_sha256": sha256_file(
            prior_authority_root / "authority_execution_receipt.json"
        ),
        "bound_resolution_proposal_summary_sha256": sha256_file(
            proposal_root / "curation_proposal_summary.json"
        ),
    }
    write_json(
        phase / "curation_authority_execution_report.json",
        report,
    )
    return report
