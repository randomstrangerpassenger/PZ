from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Iterable

from .contracts import (
    FoodSemanticError,
    canonical_json_bytes,
    canonical_proposition_id,
    load_json,
    load_jsonl,
    relative_posix,
    sha256_bytes,
    sha256_file,
    write_json,
    write_jsonl,
)


CURATION_PROPOSAL_VERSION = "food-semantic-ai-assisted-curation-proposal-v1"
APPROVAL_PACKET_VERSION = "food-semantic-curation-approval-packet-v1"
AI_CURATOR_IDENTITY = "codex_ai_curator"
FORBIDDEN_CONTEXT_FIELDS = {
    "Description",
    "DisplayCategory",
    "DisplayName",
    "FullType",
}
FORBIDDEN_CONTEXT_OPERATIONS = {
    "description_inference",
    "display_category_inference",
    "display_text_inference",
    "item_id_inference",
}
REVIEWED_CONTEXT_FIELDS = {
    "Alcoholic",
    "BadInMicrowave",
    "CanBeFrozen",
    "DaysFresh",
    "DaysTotallyRotten",
    "EvolvedRecipe",
    "FoodType",
    "HungerChange",
    "IsCookable",
    "ReplaceOnCooked",
    "ReplaceOnUse",
    "Spice",
    "Tags",
    "ThirstChange",
    "Type",
}
PLANT_FOOD_TYPES = {
    "Bean",
    "Berry",
    "Fruits",
    "Greens",
    "Herb",
    "HotPepper",
    "Nut",
    "Seed",
    "Vegetables",
}
ANIMAL_FOOD_TYPES = {
    "Beef",
    "Egg",
    "Fish",
    "Meat",
    "Sausage",
    "Seafood",
}
FUNGAL_FOOD_TYPES = {"Mushroom"}
SOLID_FOOD_TYPES = {
    "Bread",
    "Candy",
    "Cheese",
    "Chocolate",
    "Cocoa",
    "NoExplicit",
}
BEVERAGE_FOOD_TYPES = {"Juice"}
ITEM_START = re.compile(r"^\s*item\s+([A-Za-z0-9_]+)\s*$")
MODULE_START = re.compile(r"^\s*module\s+([A-Za-z0-9_]+)\s*$")
FIELD_LINE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*(.*?)\s*,\s*$")


@dataclass(frozen=True)
class ScriptItem:
    item_identity: str
    source_path: Path
    source_sha256: str
    block_sha256: str
    start_line: int
    end_line: int
    fields: dict[str, Any]


def _coerce_script_value(value: str) -> Any:
    stripped = value.strip()
    lowered = stripped.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", stripped):
        return int(stripped)
    if re.fullmatch(r"-?(?:\d+\.\d*|\d*\.\d+)", stripped):
        return float(stripped)
    return stripped


def parse_script_items(script_root: Path) -> dict[str, list[ScriptItem]]:
    result: dict[str, list[ScriptItem]] = {}
    for path in sorted(script_root.rglob("*.txt")):
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        module = "Base"
        source_hash = sha256_file(path)
        index = 0
        while index < len(lines):
            module_match = MODULE_START.match(lines[index])
            if module_match:
                module = module_match.group(1)
                index += 1
                continue
            item_match = ITEM_START.match(lines[index])
            if not item_match:
                index += 1
                continue
            item_name = item_match.group(1)
            start = index
            cursor = index + 1
            while cursor < len(lines) and lines[cursor].strip() != "{":
                cursor += 1
            if cursor >= len(lines):
                raise FoodSemanticError(f"unterminated item header: {path}:{start + 1}")
            depth = 0
            end = None
            fields: dict[str, Any] = {}
            for body_index in range(cursor, len(lines)):
                stripped = lines[body_index].strip()
                if stripped == "{":
                    depth += 1
                    continue
                if stripped == "}":
                    depth -= 1
                    if depth == 0:
                        end = body_index
                        break
                    continue
                if depth == 1:
                    field_match = FIELD_LINE.match(lines[body_index])
                    if field_match:
                        fields[field_match.group(1)] = _coerce_script_value(
                            field_match.group(2)
                        )
            if end is None:
                raise FoodSemanticError(f"unterminated item block: {path}:{start + 1}")
            block = "\n".join(lines[start : end + 1]) + "\n"
            item_identity = f"{module}.{item_name}"
            result.setdefault(item_identity, []).append(
                ScriptItem(
                    item_identity=item_identity,
                    source_path=path,
                    source_sha256=source_hash,
                    block_sha256=sha256_bytes(block.encode("utf-8")),
                    start_line=start + 1,
                    end_line=end + 1,
                    fields=fields,
                )
            )
            index = end + 1
    return result


def _select_script_item(
    item_identity: str, candidates: list[ScriptItem], *, root: Path
) -> ScriptItem:
    if not candidates:
        raise FoodSemanticError(f"no item-script source found: {item_identity}")
    projections = {
        canonical_json_bytes(
            {
                key: value
                for key, value in row.fields.items()
                if key in REVIEWED_CONTEXT_FIELDS
            }
        )
        for row in candidates
    }
    if len(projections) != 1:
        paths = [relative_posix(row.source_path, root=root) for row in candidates]
        raise FoodSemanticError(
            f"conflicting reviewed source contexts for {item_identity}: {paths}"
        )
    return sorted(
        candidates,
        key=lambda row: (relative_posix(row.source_path, root=root), row.start_line),
    )[0]


def build_source_contexts(
    root: Path, attempt_root: Path
) -> list[dict[str, Any]]:
    queue = load_jsonl(
        attempt_root / "phase7_automatic_mapping/curation_required_queue.jsonl"
    )
    parsed = parse_script_items(root / "scripts")
    contexts: list[dict[str, Any]] = []
    for queue_row in queue:
        item_identity = queue_row["item_identity"]
        source = _select_script_item(
            item_identity, parsed.get(item_identity, []), root=root
        )
        reviewed_fields = {
            key: value
            for key, value in sorted(source.fields.items())
            if key in REVIEWED_CONTEXT_FIELDS
        }
        forbidden_present = sorted(
            key for key in source.fields if key in FORBIDDEN_CONTEXT_FIELDS
        )
        contexts.append(
            {
                "item_identity": item_identity,
                "queue_proposition_id": (
                    f"curation-pending:{item_identity}"
                ),
                "review_axes": queue_row["review_axes"],
                "reviewed_source_set": [
                    {
                        "source_family": "raw_item_script_human_review_context",
                        "source_artifact_path": relative_posix(
                            source.source_path, root=root
                        ),
                        "source_artifact_sha256": source.source_sha256,
                        "source_item_locator": (
                            f"{item_identity}@L{source.start_line}-L{source.end_line}"
                        ),
                        "source_block_sha256": source.block_sha256,
                        "reviewed_fields": reviewed_fields,
                        "forbidden_fields_present_but_not_consumed": forbidden_present,
                        "normalization_operations": [
                            "exact_field_read",
                            "human_semantic_review",
                        ],
                    }
                ],
                "forbidden_context_field_consumed_count": 0,
                "forbidden_context_operation_consumed_count": 0,
            }
        )
    return contexts


def source_context_diagnostics(
    contexts: Iterable[dict[str, Any]]
) -> dict[str, Any]:
    rows = list(contexts)
    field_counts: Counter[str] = Counter()
    food_type_counts: Counter[str] = Counter()
    missing_reviewed_context = 0
    for row in rows:
        fields = row["reviewed_source_set"][0]["reviewed_fields"]
        field_counts.update(fields.keys())
        if "FoodType" in fields:
            food_type_counts[str(fields["FoodType"])] += 1
        if not fields:
            missing_reviewed_context += 1
    return {
        "schema_version": "food-semantic-curation-source-context-diagnostics-v1",
        "target_count": len(rows),
        "reviewed_field_presence": dict(sorted(field_counts.items())),
        "food_type_distribution": dict(sorted(food_type_counts.items())),
        "missing_reviewed_context_count": missing_reviewed_context,
        "forbidden_context_field_consumed_count": sum(
            row["forbidden_context_field_consumed_count"] for row in rows
        ),
        "forbidden_context_operation_consumed_count": sum(
            row["forbidden_context_operation_consumed_count"] for row in rows
        ),
    }


def write_source_context_bundle(
    root: Path, attempt_root: Path, output_root: Path
) -> dict[str, Any]:
    contexts = build_source_contexts(root, attempt_root)
    diagnostics = source_context_diagnostics(contexts)
    write_jsonl(
        output_root / "curation_source_context.jsonl",
        contexts,
        write_once=False,
    )
    write_json(
        output_root / "curation_source_context_diagnostics.json",
        diagnostics,
        write_once=False,
    )
    return diagnostics


def _proposal_from_context(
    context: dict[str, Any],
    *,
    schema_sha256: str,
    proposition_license_sha256: str,
) -> dict[str, Any]:
    item_identity = context["item_identity"]
    fields = context["reviewed_source_set"][0]["reviewed_fields"]
    fact_axis: str | None = None
    fact_value: str | None = None
    confidence = "high"
    judgment_rule: str | None = None
    rationale: str | None = None
    consumed_fields: list[str] = []

    if fields.get("Type") != "Food":
        disposition = "needs_rework"
        rework_reason = "reviewed_source_does_not_establish_food_semantic_scope"
    elif fields.get("FoodType") in BEVERAGE_FOOD_TYPES:
        disposition = "proposed"
        rework_reason = None
        fact_axis = "consumption_form"
        fact_value = "beverage"
        judgment_rule = "curated_exact_food_type_beverage_context"
        consumed_fields = ["FoodType", "Type"]
        rationale = (
            "Human-review proposal: the exact FoodType value denotes a beverage "
            "context and the item-script Type is Food."
        )
    elif fields.get("EvolvedRecipe"):
        disposition = "proposed"
        rework_reason = None
        fact_axis = "meal_role"
        fact_value = "ingredient"
        judgment_rule = "curated_explicit_recipe_participation"
        consumed_fields = ["EvolvedRecipe", "Type"]
        rationale = (
            "Human-review proposal: the item script explicitly lists one or more "
            "EvolvedRecipe uses, supporting an ingredient role."
        )
    elif fields.get("FoodType") in PLANT_FOOD_TYPES:
        disposition = "proposed"
        rework_reason = None
        fact_axis = "ingredient_origin"
        fact_value = "plant"
        judgment_rule = "curated_exact_food_type_origin_context"
        consumed_fields = ["FoodType", "Type"]
        rationale = (
            "Human-review proposal: the exact FoodType value is within the "
            "reviewed plant-origin category set."
        )
    elif fields.get("FoodType") in ANIMAL_FOOD_TYPES:
        disposition = "proposed"
        rework_reason = None
        fact_axis = "ingredient_origin"
        fact_value = "animal"
        judgment_rule = "curated_exact_food_type_origin_context"
        consumed_fields = ["FoodType", "Type"]
        rationale = (
            "Human-review proposal: the exact FoodType value is within the "
            "reviewed animal-origin category set."
        )
    elif fields.get("FoodType") in FUNGAL_FOOD_TYPES:
        disposition = "proposed"
        rework_reason = None
        fact_axis = "ingredient_origin"
        fact_value = "fungal"
        judgment_rule = "curated_exact_food_type_origin_context"
        consumed_fields = ["FoodType", "Type"]
        rationale = (
            "Human-review proposal: the exact FoodType value is within the "
            "reviewed fungal-origin category set."
        )
    elif fields.get("FoodType") in SOLID_FOOD_TYPES:
        disposition = "proposed"
        rework_reason = None
        fact_axis = "consumption_form"
        fact_value = "solid_food"
        judgment_rule = "curated_exact_food_type_solid_context"
        consumed_fields = ["FoodType", "Type"]
        confidence = "medium"
        rationale = (
            "Human-review proposal: the exact FoodType value and Food script "
            "type support a solid-food context."
        )
    elif fields.get("Tags") and "FitsToaster" in str(fields["Tags"]).split(";"):
        disposition = "proposed"
        rework_reason = None
        fact_axis = "consumption_form"
        fact_value = "solid_food"
        judgment_rule = "curated_exact_toaster_tag_context"
        consumed_fields = ["Tags", "Type"]
        confidence = "medium"
        rationale = (
            "Human-review proposal: exact FitsToaster membership supplies a "
            "physical solid-food context."
        )
    else:
        disposition = "proposed"
        rework_reason = None
        fact_axis = "consumption_form"
        fact_value = "solid_food"
        judgment_rule = "curated_food_consumption_mechanics_review"
        consumed_fields = [
            key
            for key in ("Type", "HungerChange", "DaysFresh", "DaysTotallyRotten")
            if key in fields
        ]
        confidence = "requires_owner_attention"
        rationale = (
            "AI curator proposal for explicit human confirmation: the reviewed "
            "food-consumption mechanics support solid-food treatment, but no "
            "automatic allowlisted semantic signal licenses this value."
        )

    proposal: dict[str, Any] = {
        "item_identity": item_identity,
        "curator_identity": AI_CURATOR_IDENTITY,
        "curation_mode": "ai_proposal_requiring_human_semantic_approval",
        "disposition": disposition,
        "confidence": confidence if disposition == "proposed" else "blocked",
        "reviewed_source_set": context["reviewed_source_set"],
        "consumed_reviewed_fields": consumed_fields,
        "forbidden_context_field_consumed_count": 0,
        "forbidden_context_operation_consumed_count": 0,
        "schema_sha256": schema_sha256,
        "proposition_license_sha256": proposition_license_sha256,
        "approval_status": "pending_human_semantic_approval",
        "semantic_approver": None,
        "approval_record": None,
    }
    if disposition == "proposed":
        assert fact_axis is not None
        assert fact_value is not None
        proposition_id = canonical_proposition_id(
            item_identity, fact_axis, fact_value
        )
        proposal.update(
            {
                "proposition_id": proposition_id,
                "fact_axis": fact_axis,
                "fact_value": fact_value,
                "authority_class": "curated",
                "judgment_rule": judgment_rule,
                "rationale": rationale,
            }
        )
    else:
        proposal.update(
            {
                "proposition_id": None,
                "fact_axis": None,
                "fact_value": None,
                "authority_class": None,
                "judgment_rule": None,
                "rationale": (
                    "No in-schema food semantic proposition is supported by the "
                    "reviewed source context."
                ),
                "rework_reason": rework_reason,
            }
        )
    return proposal


def build_curation_proposals(
    root: Path, attempt_root: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    contexts = build_source_contexts(root, attempt_root)
    schema_path = root / "Iris/_docs/authority/food_semantic/food_semantic_schema.json"
    license_path = (
        root
        / "Iris/_docs/authority/food_semantic/"
        "proposition_licensing_contract.json"
    )
    proposals = [
        _proposal_from_context(
            row,
            schema_sha256=sha256_file(schema_path),
            proposition_license_sha256=sha256_file(license_path),
        )
        for row in contexts
    ]
    report = validate_curation_proposals(root, attempt_root, proposals)
    return proposals, report


def validate_curation_proposals(
    root: Path,
    attempt_root: Path,
    proposals: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    rows = list(proposals)
    queue = load_jsonl(
        attempt_root / "phase7_automatic_mapping/curation_required_queue.jsonl"
    )
    queue_members = [row["item_identity"] for row in queue]
    proposal_members = [row["item_identity"] for row in rows]
    schema = load_json(
        root / "Iris/_docs/authority/food_semantic/food_semantic_schema.json"
    )
    allowed = {
        axis["axis"]: {value["value"] for value in axis["values"]}
        for axis in schema["axes"]
    }
    proposed = [row for row in rows if row["disposition"] == "proposed"]
    rework = [row for row in rows if row["disposition"] == "needs_rework"]
    schema_violation_count = sum(
        row.get("fact_axis") not in allowed
        or row.get("fact_value") not in allowed.get(row.get("fact_axis"), set())
        for row in proposed
    )
    duplicate_proposition_count = len(proposed) - len(
        {row["proposition_id"] for row in proposed}
    )
    required_fields = {
        "item_identity",
        "curator_identity",
        "reviewed_source_set",
        "rationale",
        "schema_sha256",
        "proposition_license_sha256",
        "approval_status",
        "disposition",
    }
    missing_field_count = sum(
        not required_fields.issubset(row) for row in rows
    )
    cap = load_json(attempt_root / "phase6_schema/proposed_curation_caps.json")
    blockers = []
    if queue_members != proposal_members:
        blockers.append("proposal_member_order_or_identity_mismatch")
    if len(rows) > cap["proposed_curation_item_cap"]:
        blockers.append("curation_item_cap_exceeded")
    if len(proposed) > cap["proposed_curation_proposition_cap"]:
        blockers.append("curation_proposition_cap_exceeded")
    if schema_violation_count:
        blockers.append("curation_schema_violation")
    if duplicate_proposition_count:
        blockers.append("duplicate_proposition")
    if missing_field_count:
        blockers.append("proposal_required_field_missing")
    forbidden_field_count = sum(
        row["forbidden_context_field_consumed_count"] for row in rows
    )
    forbidden_operation_count = sum(
        row["forbidden_context_operation_consumed_count"] for row in rows
    )
    if forbidden_field_count:
        blockers.append("forbidden_context_field_consumed")
    if forbidden_operation_count:
        blockers.append("forbidden_context_operation_consumed")
    return {
        "schema_version": "food-semantic-curation-proposal-validation-v1",
        "status": "PASS" if not blockers else "FAIL",
        "target_queue_count": len(queue_members),
        "proposal_row_count": len(rows),
        "proposed_proposition_count": len(proposed),
        "needs_rework_count": len(rework),
        "needs_rework_items": [row["item_identity"] for row in rework],
        "confidence_distribution": dict(
            sorted(Counter(row["confidence"] for row in rows).items())
        ),
        "judgment_rule_distribution": dict(
            sorted(
                Counter(
                    row["judgment_rule"]
                    for row in proposed
                    if row.get("judgment_rule")
                ).items()
            )
        ),
        "curation_item_cap": cap["proposed_curation_item_cap"],
        "curation_proposition_cap": cap["proposed_curation_proposition_cap"],
        "schema_violation_count": schema_violation_count,
        "duplicate_proposition_count": duplicate_proposition_count,
        "missing_required_field_count": missing_field_count,
        "forbidden_context_field_consumed_count": forbidden_field_count,
        "forbidden_context_operation_consumed_count": forbidden_operation_count,
        "blockers": blockers,
        "authority_effect": False,
        "human_semantic_approval_required": True,
    }


def build_review_batches(
    attempt_root: Path,
    proposals: list[dict[str, Any]],
    *,
    bundle_sha256: str,
) -> list[dict[str, Any]]:
    manifests = load_jsonl(
        attempt_root / "phase8_curation/curation_batch_manifest.jsonl"
    )
    by_member = {row["item_identity"]: row for row in proposals}
    result: list[dict[str, Any]] = []
    for manifest in manifests:
        members = [by_member[item] for item in manifest["ordered_members"]]
        review_payload = {
            "schema_version": CURATION_PROPOSAL_VERSION,
            "batch": manifest,
            "bound_implementation_complete_bundle_sha256": bundle_sha256,
            "curator_identity": AI_CURATOR_IDENTITY,
            "members": members,
            "owner_approval": None,
            "approval_state": "pending_human_semantic_approval",
            "authority_effect": False,
        }
        review_payload["proposal_content_sha256"] = sha256_bytes(
            canonical_json_bytes(
                {
                    "batch": manifest,
                    "members": members,
                    "bound_implementation_complete_bundle_sha256": bundle_sha256,
                }
            )
        )
        result.append(review_payload)
    return result


def approval_packet_schema() -> dict[str, Any]:
    return {
        "schema_version": APPROVAL_PACKET_VERSION,
        "description": (
            "Owner approval is valid only when every member disposition and "
            "proposition identity is reviewed and the proposal content hash matches."
        ),
        "required_owner_approval_fields": [
            "approval_state",
            "approver_identity",
            "approval_time",
            "proposal_content_sha256",
            "approved_proposition_ids",
            "accepted_needs_rework_items",
            "rationale",
        ],
        "allowed_approval_state": ["approved", "rejected", "needs_rework"],
        "implicit_or_anonymous_approval_allowed": False,
        "maximum_batch_member_count": 24,
        "authority_effect_before_import": False,
    }


def build_review_index_markdown(
    batches: list[dict[str, Any]],
    validation: dict[str, Any],
) -> str:
    lines = [
        "# DVF 3-3 Food Semantic Curation Review Index",
        "",
        "Status: AI curator proposals; no authority effect until exact owner approval.",
        "",
        "Each batch is bounded to at most 24 members. Approval must bind the exact",
        "`proposal_content_sha256`, the complete proposed proposition ID set, and",
        "the exact acknowledged rework item set. Blanket or anonymous approval is",
        "not valid.",
        "",
        "## Summary",
        "",
        f"- Target items: {validation['proposal_row_count']}",
        f"- Proposed propositions: {validation['proposed_proposition_count']}",
        f"- Needs rework: {validation['needs_rework_count']}",
        (
            "- Confidence: "
            + ", ".join(
                f"{key}={value}"
                for key, value in validation[
                    "confidence_distribution"
                ].items()
            )
        ),
        "",
        "## Batches",
        "",
    ]
    for number, batch in enumerate(batches, start=1):
        batch_id = batch["batch"]["batch_id"]
        filename = batch_id.replace(":", "_") + ".json"
        lines.extend(
            [
                f"### Batch {number}: `{batch_id}`",
                "",
                f"- Members: {batch['batch']['member_count']}",
                f"- Proposal SHA-256: `{batch['proposal_content_sha256']}`",
                f"- Packet: `review_batches/{filename}`",
                "",
                "| Item | Proposed fact | Confidence | Disposition |",
                "|---|---|---|---|",
            ]
        )
        for member in batch["members"]:
            fact = (
                f"`{member['fact_axis']}={member['fact_value']}`"
                if member["disposition"] == "proposed"
                else "—"
            )
            lines.append(
                f"| `{member['item_identity']}` | {fact} | "
                f"`{member['confidence']}` | `{member['disposition']}` |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_curation_proposal_bundle(
    root: Path, attempt_root: Path, output_root: Path
) -> dict[str, Any]:
    contexts = build_source_contexts(root, attempt_root)
    proposals, validation = build_curation_proposals(root, attempt_root)
    if validation["status"] != "PASS":
        raise FoodSemanticError(
            f"curation proposal validation failed: {validation['blockers']}"
        )
    implementation_bundle_path = (
        attempt_root / "phase13_closeout/implementation_complete_bundle.json"
    )
    bundle_sha256 = sha256_file(implementation_bundle_path)
    batches = build_review_batches(
        attempt_root, proposals, bundle_sha256=bundle_sha256
    )
    write_jsonl(
        output_root / "curation_source_context.jsonl",
        contexts,
        write_once=False,
    )
    write_json(
        output_root / "curation_source_context_diagnostics.json",
        source_context_diagnostics(contexts),
        write_once=False,
    )
    write_jsonl(
        output_root / "curation_proposition_proposals.jsonl",
        proposals,
        write_once=False,
    )
    batch_root = output_root / "review_batches"
    for batch in batches:
        filename = batch["batch"]["batch_id"].replace(":", "_") + ".json"
        write_json(batch_root / filename, batch, write_once=False)
    write_json(
        output_root / "curation_batch_approval.schema.json",
        approval_packet_schema(),
        write_once=False,
    )
    write_json(
        output_root / "curation_proposal_validation.json",
        validation,
        write_once=False,
    )
    summary = {
        "schema_version": CURATION_PROPOSAL_VERSION,
        "status": "READY_FOR_HUMAN_BATCH_REVIEW",
        "bound_attempt_id": attempt_root.name,
        "bound_implementation_complete_bundle_sha256": bundle_sha256,
        "curator_identity": AI_CURATOR_IDENTITY,
        "target_count": len(proposals),
        "proposed_proposition_count": validation[
            "proposed_proposition_count"
        ],
        "needs_rework_count": validation["needs_rework_count"],
        "needs_rework_items": validation["needs_rework_items"],
        "review_batch_count": len(batches),
        "maximum_batch_member_count": max(
            batch["batch"]["member_count"] for batch in batches
        ),
        "human_semantic_approval_required": True,
        "authority_effect": False,
        "validation_status": validation["status"],
        "proposal_ledger_sha256": sha256_file(
            output_root / "curation_proposition_proposals.jsonl"
        ),
    }
    write_json(
        output_root / "curation_proposal_summary.json",
        summary,
        write_once=False,
    )
    review_index_path = output_root / "curation_review_index.md"
    review_index_path.parent.mkdir(parents=True, exist_ok=True)
    review_index_path.write_text(
        build_review_index_markdown(batches, validation),
        encoding="utf-8",
        newline="\n",
    )
    return summary


def _review_batch_proposal_hash(batch: dict[str, Any]) -> str:
    return sha256_bytes(
        canonical_json_bytes(
            {
                "batch": batch["batch"],
                "members": batch["members"],
                "bound_implementation_complete_bundle_sha256": batch[
                    "bound_implementation_complete_bundle_sha256"
                ],
            }
        )
    )


def load_review_batches(proposal_root: Path) -> list[dict[str, Any]]:
    paths = sorted((proposal_root / "review_batches").glob("*.json"))
    if not paths:
        raise FoodSemanticError("no curation review batches found")
    batches = [load_json(path) for path in paths]
    return sorted(
        batches,
        key=lambda row: tuple(row["batch"]["ordered_members"]),
    )


def validate_batch_approvals(
    proposal_root: Path,
    *,
    owner_decisions_path: Path,
    require_all_approved: bool,
) -> dict[str, Any]:
    summary = load_json(proposal_root / "curation_proposal_summary.json")
    decisions = load_json(owner_decisions_path)
    batches = load_review_batches(proposal_root)
    decision_rows = {
        row["decision_id"]: row for row in decisions.get("decisions", [])
    }
    blockers: list[str] = []
    if decisions.get("bound_implementation_complete_bundle_sha256") != summary.get(
        "bound_implementation_complete_bundle_sha256"
    ):
        blockers.append("owner_decision_bundle_binding_mismatch")
    for decision_id in ("D5", "D6", "D7", "D8"):
        if decision_rows.get(decision_id, {}).get("status") != "approved":
            blockers.append(f"{decision_id}_not_approved")

    approved_batch_count = 0
    pending_batch_count = 0
    invalid_batch_count = 0
    approved_proposition_count = 0
    acknowledged_rework_count = 0
    seen_members: set[str] = set()
    seen_propositions: set[str] = set()
    batch_results: list[dict[str, Any]] = []
    for batch in batches:
        batch_id = batch["batch"]["batch_id"]
        errors: list[str] = []
        computed_hash = _review_batch_proposal_hash(batch)
        if computed_hash != batch.get("proposal_content_sha256"):
            errors.append("proposal_content_hash_mismatch")
        members = batch.get("members", [])
        if len(members) != batch["batch"].get("member_count"):
            errors.append("batch_member_count_mismatch")
        if len(members) > 24:
            errors.append("batch_member_count_exceeds_D6")
        member_ids = [row["item_identity"] for row in members]
        if member_ids != batch["batch"].get("ordered_members"):
            errors.append("batch_member_order_mismatch")
        duplicate_members = seen_members.intersection(member_ids)
        if duplicate_members:
            errors.append("cross_batch_duplicate_member")
        seen_members.update(member_ids)

        owner_approval = batch.get("owner_approval")
        if owner_approval is None:
            pending_batch_count += 1
            state = "pending"
            if require_all_approved:
                errors.append("owner_approval_missing")
        else:
            state = str(owner_approval.get("approval_state"))
            required = {
                "approval_state",
                "approver_identity",
                "approval_time",
                "proposal_content_sha256",
                "approved_proposition_ids",
                "accepted_needs_rework_items",
                "rationale",
            }
            if not required.issubset(owner_approval):
                errors.append("owner_approval_required_field_missing")
            if state != "approved":
                errors.append("batch_not_approved")
            if not owner_approval.get("approver_identity"):
                errors.append("anonymous_approval_forbidden")
            if owner_approval.get("proposal_content_sha256") != computed_hash:
                errors.append("approval_proposal_hash_mismatch")
            expected_propositions = sorted(
                row["proposition_id"]
                for row in members
                if row["disposition"] == "proposed"
            )
            expected_rework = sorted(
                row["item_identity"]
                for row in members
                if row["disposition"] == "needs_rework"
            )
            approved_ids = sorted(
                owner_approval.get("approved_proposition_ids", [])
            )
            accepted_rework = sorted(
                owner_approval.get("accepted_needs_rework_items", [])
            )
            if approved_ids != expected_propositions:
                errors.append("approved_proposition_set_mismatch")
            if accepted_rework != expected_rework:
                errors.append("accepted_rework_set_mismatch")
            duplicate_propositions = seen_propositions.intersection(approved_ids)
            if duplicate_propositions:
                errors.append("cross_batch_duplicate_proposition")
            seen_propositions.update(approved_ids)
            if not errors:
                approved_batch_count += 1
                approved_proposition_count += len(approved_ids)
                acknowledged_rework_count += len(accepted_rework)

        if errors:
            invalid_batch_count += 1
        batch_results.append(
            {
                "batch_id": batch_id,
                "state": state,
                "member_count": len(members),
                "computed_proposal_content_sha256": computed_hash,
                "errors": errors,
            }
        )

    if invalid_batch_count:
        blockers.append("invalid_batch_approval_present")
    if require_all_approved and pending_batch_count:
        blockers.append("pending_batch_approval_present")
    status = "PASS" if not blockers and pending_batch_count == 0 else (
        "PENDING" if not blockers else "BLOCKED"
    )
    return {
        "schema_version": "food-semantic-curation-batch-approval-validation-v1",
        "status": status,
        "review_batch_count": len(batches),
        "approved_batch_count": approved_batch_count,
        "pending_batch_count": pending_batch_count,
        "invalid_batch_count": invalid_batch_count,
        "approved_proposition_count": approved_proposition_count,
        "acknowledged_rework_count": acknowledged_rework_count,
        "reviewed_member_count": len(seen_members),
        "blockers": blockers,
        "batch_results": batch_results,
        "authority_effect": False,
    }


def materialize_approved_curation(
    proposal_root: Path,
    authority_root: Path,
    *,
    owner_decisions_path: Path,
) -> dict[str, Any]:
    validation = validate_batch_approvals(
        proposal_root,
        owner_decisions_path=owner_decisions_path,
        require_all_approved=True,
    )
    if validation["status"] != "PASS":
        raise FoodSemanticError(
            f"curation approval validation is not PASS: {validation['blockers']}"
        )
    batches = load_review_batches(proposal_root)
    curated_rows: list[dict[str, Any]] = []
    approval_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    rework_rows: list[dict[str, Any]] = []
    last_batch_id: str | None = None
    for batch in batches:
        approval = batch["owner_approval"]
        assert approval is not None
        approval_record = (
            f"{batch['batch']['batch_id']}@"
            f"{batch['proposal_content_sha256']}"
        )
        for member in batch["members"]:
            pending_id = f"curation-pending:{member['item_identity']}"
            event_rows.append(
                {
                    "event_id": f"{pending_id}:queued:1",
                    "proposition_id": pending_id,
                    "event": "queued",
                    "batch_id": batch["batch"]["batch_id"],
                    "authority_effect": False,
                }
            )
            event_rows.append(
                {
                    "event_id": f"{pending_id}:review_started:1",
                    "proposition_id": pending_id,
                    "event": "review_started",
                    "batch_id": batch["batch"]["batch_id"],
                    "authority_effect": False,
                }
            )
            if member["disposition"] == "needs_rework":
                event_rows.append(
                    {
                        "event_id": f"{pending_id}:needs_rework:1",
                        "proposition_id": pending_id,
                        "event": "needs_rework",
                        "batch_id": batch["batch"]["batch_id"],
                        "authority_effect": False,
                    }
                )
                rework_rows.append(
                    {
                        "item_identity": member["item_identity"],
                        "batch_id": batch["batch"]["batch_id"],
                        "rework_reason": member["rework_reason"],
                        "reviewed_source_set": member["reviewed_source_set"],
                        "owner_acknowledged": True,
                        "approval_record": approval_record,
                    }
                )
                continue
            proposition_id = member["proposition_id"]
            curated_rows.append(
                {
                    "item_identity": member["item_identity"],
                    "fact_proposition_identity": proposition_id,
                    "fact_field": member["fact_axis"],
                    "fact_value": member["fact_value"],
                    "authority_class": "curated",
                    "approval_status": "owner_approved",
                    "signal_to_fact_mapping_id": (
                        f"curated.owner_approved.{proposition_id}"
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
                    "proposition_id": proposition_id,
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
            event_rows.append(
                {
                    "event_id": f"{proposition_id}:accepted:1",
                    "proposition_id": proposition_id,
                    "event": "accepted",
                    "batch_id": batch["batch"]["batch_id"],
                    "authority_effect": True,
                }
            )
        last_batch_id = batch["batch"]["batch_id"]

    phase = authority_root / "phase8_curation"
    write_jsonl(phase / "curated_fact_ledger.jsonl", curated_rows)
    write_jsonl(
        phase / "semantic_authority_approval_ledger.jsonl", approval_rows
    )
    write_jsonl(phase / "curation_event_ledger.jsonl", event_rows)
    write_jsonl(phase / "curation_rework_queue.jsonl", rework_rows)
    event_path = phase / "curation_event_ledger.jsonl"
    write_json(
        phase / "curation_checkpoint.json",
        {
            "last_fully_committed_batch_id": last_batch_id,
            "event_ledger_sha256": sha256_file(event_path),
            "accepted_count": len(curated_rows),
            "rejected_count": 0,
            "rework_count": len(rework_rows),
            "next_canonical_cursor": (
                (
                    f"{rework_rows[0]['item_identity']}\0\0"
                    f"curation-pending:{rework_rows[0]['item_identity']}"
                )
                if rework_rows
                else None
            ),
            "authority_execution_started": True,
        },
    )
    report = {
        "schema_version": "food-semantic-curation-materialization-v1",
        "status": (
            "PASS_COMPLETE" if not rework_rows else "PASS_WITH_REWORK"
        ),
        "approved_curated_proposition_count": len(curated_rows),
        "unresolved_rework_count": len(rework_rows),
        "approved_batch_count": validation["approved_batch_count"],
        "duplicate_approval_event_count": 0,
        "curated_schema_violation_count": 0,
        "curated_approval_missing_count": 0,
        "candidate_generation_authorized": not rework_rows,
        "current_mutation_authorized": False,
    }
    write_json(phase / "curation_authority_execution_report.json", report)
    return report
