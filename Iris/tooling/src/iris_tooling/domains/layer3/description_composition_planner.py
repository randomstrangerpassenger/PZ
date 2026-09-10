"""Locale-neutral placement and exact-scope clause planning from semantic blocks."""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy

from .composition_model import canonical

# Maintenance, presentation metadata and an already-applied treatment's removal
# belong to the detailed explanation. This applies by meaning, never by item or
# corpus frequency. All remain actual sentences in the same locale.
DETAIL_FUNCTIONS = frozenset({
    "wash_carried_equipment", "wash_equipment", "receive_garment_patch",
    "remove_garment_patch", "unpick_garment_patch", "rename_selected_item",
    "rename_prepared_food", "remove_applied_splint", "remove_applied_bandage",
    "consolidate_drainable_supplies", "pour_water_into_container", "receive_poured_water", "dump_water", "supply_world_water_storage",
    "adjust_device_volume", "control_device_headphones", "edit_radio_presets", "insert_device_battery",
    "remove_device_battery", "open_device_controls", "toggle_radio_microphone",
    "light_candle", "extinguish_candle", "extinguish_on_unequip",
})
PRODUCT_CONTEXTS = frozenset({"campfire_kit_preparation", "tent_kit_making", "spear_crafting",
    "furniture_crafting", "splint_crafting", "trap_crafting", "tool_crafting", "fishing_gear_crafting",
    "mattress_preparation", "hat_crafting", "bandaging_material_preparation", "watermelon_breaking",
    "grain_preparation"})


def plan(item: dict) -> dict:
    qualifiers = {q["qualifier_id"]: deepcopy(q) for q in item["qualifiers"]}
    applications = defaultdict(list)
    for q in qualifiers.values():
        for ref in q["applies_to_fact_refs"]:
            applications[ref].append(q["qualifier_id"])
    units = []
    relations = []
    for block in sorted(item["blocks"], key=lambda b: b["block_id"]):
        relations.extend(deepcopy(block["relations"]))
        for branch in sorted(block["branches"], key=lambda b: b["branch_id"]):
            facts = sorted(branch["facts"], key=lambda f: f["fact_ref"])
            contexts = [f for f in facts if f["fact_kind"] == "use_context"]
            roles = [f for f in facts if f["fact_kind"] == "context_role"]
            consumed = set()
            # The input branch binds roles to exactly one context. Fuse only
            # when the qualifier application is identical for every claim.
            if len(contexts) == 1 and roles:
                context = contexts[0]
                bound = [r for r in roles if sorted(applications[r["fact_ref"]])
                         == sorted(applications[context["fact_ref"]])]
                if bound:
                    units.append(_unit(block, branch, [context, *bound], applications))
                    consumed.update(f["fact_ref"] for f in [context, *bound])
            for fact in facts:
                if fact["fact_ref"] not in consumed:
                    unit = _unit(block, branch, [fact], applications)
                    if fact["fact_kind"] == "context_role":
                        # Context is a referent, not a second qualified claim.
                        unit["context"] = deepcopy(contexts[0]["payload"]) if len(contexts) == 1 else None
                    units.append(unit)
    # When portable-light controls are an admitted capability, the separate
    # activation toggle describes operating that light, not another main use.
    if any(f["payload"].get("function") == "control_portable_light" for u in units for f in u["facts"]):
        for u in units:
            if any(f["payload"].get("function") in {"toggle_activation", "accept_battery_charge"} for f in u["facts"]):
                u["detail_reason"] = "activation or power-supply operation of the admitted portable-light controls"
            contexts = {f["payload"].get("activity") for f in u["facts"]} | {(u.get("context") or {}).get("activity")}
            if contexts & {"battery_insertion", "battery_removal"}:
                u["detail_reason"] = "battery servicing of the portable light; charging procedure remains expanded"
            if "electronic_salvage" in contexts:
                u["detail_reason"] = "specific dismantling participation; the direct salvage capability remains compact"
    # Semantic order serves grammatical attachment only; it is not a use rank.
    units.sort(key=lambda u: (canonical([f["payload"] for f in u["facts"]]), u["fact_refs"]))
    if units and not any(u["detail_reason"] is None for u in units):
        # A recipe-only material still needs a useful first explanation. Keep
        # every recipe role in that case, never choose a representative recipe.
        for u in units:
            if any(f["fact_kind"] in {"use_context", "context_role"} for f in u["facts"]):
                u["detail_reason"] = None
    return {"item_id": item["item_id"], "units": units, "qualifiers": qualifiers,
            "relations": sorted(relations, key=lambda r: r["relation_id"]),
            "unresolved_relations": deepcopy(item["unresolved_relations"])}


def _unit(block, branch, facts, applications):
    kind = facts[0]["fact_kind"]
    function = facts[0]["payload"].get("function")
    if block["class"] == "acquisition":
        placement = "acquisition routes and their conditions are expanded; S3 is separate"
    elif any(f["payload"].get("activity") in PRODUCT_CONTEXTS for f in facts):
        placement = "specific recipe product and its input requirements; not asserted to be a subtype of another use"
    elif any(f["payload"].get("role") == "repair_target" for f in facts):
        placement = "repair of the item itself is maintenance; repair-material and tool roles stay distinct"
    elif any(f["payload"].get("role") == "transformation_target" for f in facts) and any(
            f["payload"].get("activity") in {"candle_lighting", "candle_extinguishing"} for f in branch["facts"]):
        placement = "own light-form activation/deactivation procedure; ignition-tool roles remain distinct"
    elif kind == "use_context" and facts[0]["payload"].get("activity") in {"candle_lighting", "candle_extinguishing"} and any(
            f["payload"].get("role") == "transformation_target" for f in branch["facts"]):
        placement = "own light-form activation/deactivation recipe context"
    elif kind == "state" and facts[0]["payload"]["state"] in {"reading_page_count", "skill_book_progress_step"}:
        placement = "page count or calculation increment; learning effect and maximum remain in compact"
    elif kind == "effect" and facts[0]["payload"]["property"] in {
        "treatment_panic", "bandage_patient_infection", "installed_vehicle_part_condition",
        "installed_tire_air_or_attachment", "installed_vehicle_battery_charge",
    }:
        placement = "conditional treatment side effect or installed-part state change, with exact scope in expanded"
    elif kind == "effect" and facts[0]["payload"]["property"] in {
        "food_chef_attribution", "food_preservation_age", "fish_size_nutrition",
        "written_note_title", "written_note_pages", "written_note_lock", "reading_page_progress",
    }:
        placement = "attribution, preparation metadata, or note editing detail"
    elif kind == "effect" and facts[0]["payload"]["property"] in {
        "splint_factor", "doctor_experience", "additional_pain", "treatment_panic", "crop_water_level", "burn_wash_requirement",
    } and any(r["kind"] == "result" for r in block["relations"]):
        placement = "treatment coefficient, numerical per-use result or caregiver side effect of an explicitly linked function"
    elif kind == "effect" and facts[0]["payload"] == {"property": "applied_bandage_life", "direction": "set_skill_random_plus_power"}:
        placement = "bandage-duration calculation detail; a zero-life distinction is not excluded by this rule"
    elif kind == "effect" and facts[0]["payload"]["property"] in {
        "item_surface_blood", "clothing_surface_dirt", "clothing_wetness",
    } and any(r["kind"] == "result" for r in block["relations"]):
        placement = "result of the detailed equipment-washing operation"
    elif function in DETAIL_FUNCTIONS:
        placement = "maintenance, naming or removal of an applied treatment"
    else:
        placement = None
    return {"block_refs": [block["block_id"]], "branch_refs": [branch["branch_id"]],
            "fact_refs": sorted(f["fact_ref"] for f in facts), "facts": deepcopy(facts),
            "qualifier_refs": sorted(applications[facts[0]["fact_ref"]]),
            "relation_refs": sorted(r["relation_id"] for r in block["relations"]
                                    if set(r.get("fact_refs", [])) & {f["fact_ref"] for f in facts}
                                    or branch["branch_id"] in r.get("branch_refs", [])),
            "detail_reason": placement}
