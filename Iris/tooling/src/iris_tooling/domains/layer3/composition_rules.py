"""Evidence-bound rules that assemble accepted Layer 3 facts into meaning blocks."""
from __future__ import annotations

from collections import Counter, defaultdict
from . import composition_model as model


# Relation overlays over accepted function/context values, not item exceptions
# or token heuristics. Their source/admission grounding and compatibility limits
# are recorded in the composition contract.
FUNCTION_VARIANT_GROUPS = {
    "fuel_targets": frozenset({"supply_campfire_fuel", "supply_hearth_fuel", "supply_furnace_fuel"}),
    "tinder_targets": frozenset({"provide_campfire_tinder", "provide_hearth_tinder",
                                  "provide_industrial_tinder"}),
    "friction_targets": frozenset({"light_campfire_by_friction", "kindle_heat_sources"}),
}
CONTEXT_REFINEMENTS = {
    "carpentry_menu_construction": "construction",
    "smithing_parts": "metal_forging",
    "shovel_smithing": "metal_forging",
}
COMPOUND_MEANINGS = {
    "written_notes": frozenset({
        ("direct_function", (("function", "view_written_note_pages"),)),
        ("direct_function", (("function", "record_written_notes"),)),
        ("effect", (("direction", "update"), ("property", "written_note_pages"))),
        ("effect", (("direction", "update"), ("property", "written_note_title"))),
        ("effect", (("direction", "update"), ("property", "written_note_lock"))),
    }),
}
# Function/effect direction is explicit and reusable. Each entry is grounded in
# the named r6 admission/source rule; neither a shared rule nor a shared
# qualifier is sufficient unless the payload pair appears here.
FUNCTION_EFFECT_RESULTS = {
    "wash_carried_equipment": ("washing_target", frozenset({
        ("item_surface_blood", "remove_by_washing"),
        ("clothing_surface_dirt", "remove_by_washing"),
        ("clothing_wetness", "set_100_by_washing"),
    })),
    "drink_stored_water": ("drinking_water", frozenset({
        ("thirst", "decrease"), ("poison_level", "increase")})),
    "water_seeded_crop": ("water_consumers", frozenset({
        ("crop_water_level", "increase_five_per_use")})),
    "clean_burn": ("burn_cleaning", frozenset({
        ("doctor_experience", "add_10"), ("burn_wash_requirement", "clear"),
        ("additional_pain", "add_60_minus_doctor_level")})),
    "read_literature": ("reading", frozenset({
        (f"{skill}_experience_multiplier", "increase") for skill in (
            "Blacksmith", "Carpentry", "Cooking", "Electricity", "Farming", "FirstAid",
            "Fishing", "Foraging", "Mechanics", "MetalWelding", "Tailoring", "Trapping")})),
    "pickup_floor_glass": ("floor_glass", frozenset({
        ("hand_embedded_glass", "apply_during_glass_pickup"),
        ("hand_scratch", "apply_during_glass_pickup")})),
    "disinfect_wound": ("health_actions", frozenset({
        ("wound_alcohol_level", "increase"), ("additional_pain", "increase")})),
    "dry_the_body": ("drying", frozenset({("body_wetness", "decrease")})),
    "apply_fertilizer": ("fertilizing", frozenset({
        ("crop_state", "set_rotten"), ("crop_growth_schedule", "advance")})),
    "use_furnace_bellows": ("heat_controls", frozenset({
        ("forge_temperature", "increase")})),
    "smoke_cigarette": ("food_callbacks", frozenset({
        ("stress", "decrease"), ("unhappiness", "decrease"),
        ("food_sickness", "increase")})),
    "treat_crop_flies": ("crop_treatment", frozenset({
        ("crop_flies_level", "decrease")})),
    "treat_crop_mildew": ("crop_treatment", frozenset({
        ("crop_mildew_level", "decrease")})),
    "apply_splint": ("health_actions/splint_lifecycle", frozenset({
        ("splint_factor", "set_doctor_half")})),
    "wash_body": ("washing_supplies", frozenset({
        ("washed_surface_blood", "remove")})),
}
UNRESOLVED_MEANINGS = {
    "spear_fishing_wear": frozenset({
        ("direct_function", (("function", "fish_with_spear"),)),
        ("effect", (("direction", "decrease"), ("property", "item_condition"))),
    }),
}


def _signature(fact: dict) -> tuple[str, tuple[tuple[str, object], ...]]:
    return fact["fact_kind"], tuple(sorted(fact["payload"].items()))


def _fact_node(fact: dict) -> dict:
    return {"fact_ref": fact["fact_id"], "item_id": fact["item_id"],
            "fact_kind": fact["fact_kind"], "payload": fact["payload"],
            "provenance_refs": sorted(set(fact["provenance_refs"])),
            "admission_rule_ref": fact.get("admission", {}).get("rule_ref", "fixture")}


class _DisjointSet:
    def __init__(self, values):
        self.parent = {value: value for value in values}

    def find(self, value):
        parent = self.parent[value]
        if parent != value:
            self.parent[value] = self.find(parent)
        return self.parent[value]

    def union(self, left, right):
        left, right = self.find(left), self.find(right)
        if left != right:
            self.parent[max(left, right)] = min(left, right)


def _relation(item_id: str, kind: str, *, branch_refs=(), fact_refs=(), basis: str,
              direction=None) -> dict:
    relation = {"kind": kind, "branch_refs": sorted(set(branch_refs)),
                "fact_refs": sorted(set(fact_refs)), "basis": basis}
    if direction:
        relation["direction"] = direction
    relation["relation_id"] = model.relation_identity(item_id, relation)
    return relation


def _branch_units(anchors: list[dict]) -> list[list[str]]:
    role_refs = {fact["fact_id"] for fact in anchors if fact["fact_kind"] == "context_role"}
    units, consumed_roles = [], set()
    for fact in anchors:
        if fact["fact_kind"] != "use_context":
            continue
        members = [fact["fact_id"]] + sorted(role["fact_id"] for role in anchors
            if role["fact_kind"] == "context_role" and role.get("context_fact_ref") == fact["fact_id"])
        consumed_roles.update(set(members) & role_refs)
        units.append(sorted(members))
    units.extend([fact["fact_id"]] for fact in anchors
                 if fact["fact_kind"] != "use_context" and fact["fact_id"] not in consumed_roles)
    return units


def semantic_blocks(item_id: str, facts: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """Compose one item without consulting Profile names or generated prose."""
    facts = sorted(facts, key=lambda row: row["fact_id"])
    by_ref = {fact["fact_id"]: fact for fact in facts}
    qualifiers = [fact for fact in facts if fact["fact_kind"] in model.QUALIFIER_KINDS]
    anchors = [fact for fact in facts if fact["fact_kind"] not in model.QUALIFIER_KINDS]
    anchor_refs = {fact["fact_id"] for fact in anchors}
    dsu = _DisjointSet(anchor_refs)
    result_links = set()

    # Explicit context-role refinement is compatible by the adopted schema.
    for fact in anchors:
        if fact["fact_kind"] == "context_role" and fact.get("context_fact_ref") in anchor_refs:
            dsu.union(fact["fact_id"], fact["context_fact_ref"])

    functions = defaultdict(list)
    for fact in anchors:
        if fact["fact_kind"] == "direct_function":
            functions[fact["payload"]["function"]].append(fact["fact_id"])
    for names in FUNCTION_VARIANT_GROUPS.values():
        refs = sorted(ref for name in names for ref in functions.get(name, []))
        for left, right in zip(refs, refs[1:]):
            dsu.union(left, right)

    effects = defaultdict(list)
    for fact in anchors:
        if fact["fact_kind"] == "effect":
            effects[(fact["payload"]["property"], fact["payload"]["direction"])].append(fact["fact_id"])
    for function_name, (source_rule, effect_payloads) in FUNCTION_EFFECT_RESULTS.items():
        for function_ref in functions.get(function_name, []):
            for effect_payload in effect_payloads:
                for effect_ref in effects.get(effect_payload, []):
                    dsu.union(function_ref, effect_ref)
                    result_links.add((function_ref, effect_ref, source_rule))

    # Context refinement requires both the reviewed direction and a compatible
    # item role; it cannot merge repair-target/tool or material/tool conflicts.
    contexts = {fact["payload"]["activity"]: fact for fact in anchors
                if fact["fact_kind"] == "use_context"}
    roles_by_context = defaultdict(set)
    for fact in anchors:
        if fact["fact_kind"] == "context_role":
            roles_by_context[fact["context_fact_ref"]].add(fact["payload"]["role"])
    for child_name, parent_name in CONTEXT_REFINEMENTS.items():
        child, parent = contexts.get(child_name), contexts.get(parent_name)
        if (child and parent and roles_by_context[child["fact_id"]]
                and roles_by_context[child["fact_id"]] == roles_by_context[parent["fact_id"]]):
            dsu.union(child["fact_id"], parent["fact_id"])

    signatures = defaultdict(list)
    for fact in anchors:
        signatures[_signature(fact)].append(fact["fact_id"])
    for wanted in COMPOUND_MEANINGS.values():
        refs = sorted(ref for signature in wanted for ref in signatures.get(signature, []))
        if len({signature for signature in wanted if signatures.get(signature)}) > 1:
            for left, right in zip(refs, refs[1:]):
                dsu.union(left, right)

    units = _branch_units(anchors)
    component_units = defaultdict(list)
    for members in units:
        component_units[dsu.find(members[0])].append(members)
    blocks, fact_to_branch, fact_to_block = [], {}, {}
    for _, members_collection in sorted(component_units.items()):
        branches = []
        for members in members_collection:
            branch_id = model.branch_identity(item_id, "semantic", members)
            for ref in members:
                fact_to_branch[ref] = branch_id
            member_facts = [by_ref[ref] for ref in members]
            branches.append({"branch_id": branch_id,
                "kind": "context" if any(fact["fact_kind"] == "use_context" for fact in member_facts)
                else member_facts[0]["fact_kind"],
                "facts": [_fact_node(by_ref[ref]) for ref in members]})
        branches.sort(key=lambda row: row["branch_id"])
        refs = sorted(node["fact_ref"] for branch in branches for node in branch["facts"])
        block_id = model.block_identity(item_id, "semantic", refs)
        for ref in refs:
            fact_to_block[ref] = block_id
        blocks.append({"block_id": block_id, "class": "semantic", "branches": branches,
                       "relations": []})

    block_by_id = {block["block_id"]: block for block in blocks}
    for block in blocks:
        block_refs = {node["fact_ref"] for branch in block["branches"] for node in branch["facts"]}
        relations = []
        for ref in block_refs:
            fact = by_ref[ref]
            if fact["fact_kind"] == "context_role":
                relations.append(_relation(item_id, "refinement",
                    branch_refs=[fact_to_branch[ref]], fact_refs=[ref, fact["context_fact_ref"]],
                    basis="explicit context_fact_ref",
                    direction={"from_fact_ref": ref, "to_fact_ref": fact["context_fact_ref"]}))
        for group_name, names in FUNCTION_VARIANT_GROUPS.items():
            refs = sorted(ref for name in names for ref in functions.get(name, []) if ref in block_refs)
            if len(refs) > 1:
                relations.append(_relation(item_id, "context_variant",
                    branch_refs=[fact_to_branch[ref] for ref in refs], fact_refs=refs,
                    basis=f"reviewed function target group: {group_name}"))
        for child_name, parent_name in CONTEXT_REFINEMENTS.items():
            child, parent = contexts.get(child_name), contexts.get(parent_name)
            if child and parent and {child["fact_id"], parent["fact_id"]} <= block_refs:
                relations.append(_relation(item_id, "refinement",
                    branch_refs=[fact_to_branch[child["fact_id"]], fact_to_branch[parent["fact_id"]]],
                    fact_refs=[child["fact_id"], parent["fact_id"]],
                    basis="reviewed context refinement with matching role",
                    direction={"from_branch_ref": fact_to_branch[child["fact_id"]],
                               "to_branch_ref": fact_to_branch[parent["fact_id"]]}))
        for name, wanted in COMPOUND_MEANINGS.items():
            refs = sorted(ref for signature in wanted for ref in signatures.get(signature, []) if ref in block_refs)
            if len(refs) > 1:
                relations.append(_relation(item_id, "compound",
                    branch_refs=[fact_to_branch[ref] for ref in refs], fact_refs=refs,
                    basis=f"reviewed compound meaning: {name}"))
        for function_ref, effect_ref, rule_ref in sorted(result_links):
            if {function_ref, effect_ref} <= block_refs:
                relations.append(_relation(item_id, "result",
                    branch_refs=[fact_to_branch[function_ref], fact_to_branch[effect_ref]],
                    fact_refs=[function_ref, effect_ref],
                    basis=f"accepted function/effect mapping from source rule: {rule_ref}",
                    direction={"from_fact_ref": function_ref, "to_fact_ref": effect_ref}))
        unique_relations = {}
        for relation in relations:
            key = (relation["kind"], tuple(relation["branch_refs"]), tuple(relation["fact_refs"]),
                   model.canonical(relation.get("direction")))
            unique_relations.setdefault(key, relation)
        block["relations"] = sorted(unique_relations.values(), key=lambda row: row["relation_id"])

    # Qualifiers are item-level. Sharing a condition never merges independent
    # meanings; one collapsed qualifier can explicitly point across blocks.
    qualifier_groups = defaultdict(list)
    for qualifier in qualifiers:
        qualifier_groups[_signature(qualifier)].append(qualifier)
    composed_qualifiers = []
    for (kind, payload_items), group in sorted(qualifier_groups.items(), key=lambda row: row[0]):
        refs = sorted(fact["fact_id"] for fact in group)
        applies = sorted({ref for fact in group for ref in fact["applies_to_fact_refs"]})
        branch_refs = sorted({fact_to_branch[ref] for ref in applies})
        block_refs = sorted({fact_to_block[ref] for ref in applies})
        scope = ("block_common" if len(block_refs) == 1
                 and set(branch_refs) == {branch["branch_id"] for branch in block_by_id[block_refs[0]]["branches"]}
                 else "branch_local")
        composed_qualifiers.append({"qualifier_id": model.qualifier_identity(item_id, refs),
            "fact_refs": refs, "fact_kind": kind, "payload": dict(payload_items),
            "provenance_refs": sorted({ref for fact in group for ref in fact["provenance_refs"]}),
            "applies_to_fact_refs": applies, "branch_refs": branch_refs,
            "block_refs": block_refs, "scope": scope,
            "basis": "exact accepted qualifier payload; exact application refs retained"})

    blocks.sort(key=lambda row: row["block_id"])
    return blocks, sorted(composed_qualifiers, key=lambda row: row["qualifier_id"]), \
        _unresolved_relations(item_id, anchors, fact_to_block)


def _unresolved_relations(item_id: str, anchors: list[dict], fact_to_block: dict[str, str]) -> list[dict]:
    """Retain reviewed real candidates whose accepted direction is still absent."""
    signatures = defaultdict(list)
    for fact in anchors:
        signatures[_signature(fact)].append(fact)
    unresolved = []
    for name, wanted in UNRESOLVED_MEANINGS.items():
        facts = [fact for signature in wanted for fact in signatures.get(signature, [])]
        block_refs = sorted({fact_to_block[fact["fact_id"]] for fact in facts})
        if len(facts) != len(wanted) or len(block_refs) != 2:
            continue
        relation = {"kind": "undetermined", "block_refs": block_refs,
                    "fact_refs": sorted(fact["fact_id"] for fact in facts),
                    "reason": (f"{name} has an accepted function and wear effect but no accepted "
                               "application or direction reference between them"),
                    "consumer_effect": "keep fishing use and condition loss separate; do not claim causation"}
        relation["relation_id"] = model.relation_identity(item_id, relation)
        unresolved.append(relation)
    return sorted(unresolved, key=lambda row: row["relation_id"])


def acquisition_block(item_id: str, facts: list[dict]) -> dict | None:
    if not facts:
        return None
    branches = []
    for fact in sorted(facts, key=lambda row: row["fact_id"]):
        branch_id = model.branch_identity(item_id, "acquisition", [fact["fact_id"]])
        branches.append({"branch_id": branch_id, "kind": "acquisition_route",
                         "facts": [_fact_node(fact)]})
    relations = []
    if len(branches) > 1:
        relations.append(_relation(item_id, "alternative",
            branch_refs=[branch["branch_id"] for branch in branches],
            fact_refs=[fact["fact_id"] for fact in facts],
            basis="accepted acquisition facts describe distinct obtainable routes"))
    refs = sorted(fact["fact_id"] for fact in facts)
    return {"block_id": model.block_identity(item_id, "acquisition", refs),
            "class": "acquisition", "branches": sorted(branches, key=lambda row: row["branch_id"]),
            "relations": relations}


def compose(semantic: dict, acquisition: dict, source: dict) -> dict:
    model.require(semantic["target_ids"] == acquisition["target_ids"], "input target mismatch")
    semantic_by_item, acquisition_by_item = defaultdict(list), defaultdict(list)
    for fact in semantic["facts"]:
        semantic_by_item[fact["item_id"]].append(fact)
    for fact in acquisition["facts"]:
        acquisition_by_item[fact["item_id"]].append(fact)

    items, relation_counts, qualifier_counts, grouped_blocks = [], Counter(), Counter(), 0
    for item_id in semantic["target_ids"]:
        blocks, qualifiers, unresolved = semantic_blocks(item_id, semantic_by_item[item_id])
        acquisition_result = acquisition_block(item_id, acquisition_by_item[item_id])
        if acquisition_result:
            blocks.append(acquisition_result)
        blocks.sort(key=lambda row: row["block_id"])
        for block in blocks:
            grouped_blocks += len(block["branches"]) > 1
            relation_counts.update(relation["kind"] for relation in block["relations"])
        relation_counts["equivalent"] += sum(len(row["fact_refs"]) > 1 for row in qualifiers)
        relation_counts["undetermined"] += len(unresolved)
        qualifier_counts.update(row["scope"] for row in qualifiers)
        items.append({"item_id": item_id, "blocks": blocks, "qualifiers": qualifiers,
                      "separate_block_refs": [block["block_id"] for block in blocks],
                      "unresolved_relations": unresolved})
    input_facts = len(semantic["facts"]) + len(acquisition["facts"])
    result = {"schema": model.SCHEMA, "contract_version": model.CONTRACT_VERSION,
              "source": source, "items": items,
              "summary": {"targets": len(items), "input_facts": input_facts,
                  "blocks": sum(len(item["blocks"]) for item in items),
                  "grouped_blocks": grouped_blocks,
                  "dispositions": {"represented": input_facts, "residual": 0, "non_public": 0},
                  "relation_kinds": dict(sorted(relation_counts.items())),
                  "qualifier_scopes": dict(sorted(qualifier_counts.items()))}}
    return model.validate_result(result)
