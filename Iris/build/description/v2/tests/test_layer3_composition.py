"""Single focused acceptance entry point for DVF semantic composition."""
from copy import deepcopy
from pathlib import Path
import random
import sys

import pytest

from iris_tooling.domains.layer3 import composition_model as model
from iris_tooling.domains.layer3 import composition_results as results
from iris_tooling.domains.layer3 import composition_rules as rules


REPO = Path(__file__).resolve().parents[5]


def _fact(ref, item, kind, payload, *, applies=None, context=None, rule=None):
    row = {"fact_id": f"fact:{ref}", "item_id": item, "fact_kind": kind,
           "payload": payload, "provenance_refs": [f"prov:{ref}"]}
    if applies is not None:
        row["applies_to_fact_refs"] = [f"fact:{value}" for value in applies]
    if context is not None:
        row["context_fact_ref"] = f"fact:{context}"
    if rule is not None:
        row["admission"] = {"rule_ref": rule, "supported": True}
    return row


def _small_inputs():
    item = "Base.CompositionFixture"
    semantic_facts = [
        _fact("construction", item, "use_context", {"activity": "construction"}),
        _fact("construction_role", item, "context_role", {"role": "material"},
              context="construction"),
        _fact("carpentry", item, "use_context", {"activity": "carpentry_menu_construction"}),
        _fact("carpentry_role", item, "context_role", {"role": "material"}, context="carpentry"),
        _fact("construction_condition", item, "condition", {"predicate": "materials are available"},
              applies=["construction", "construction_role"]),
        _fact("carpentry_condition", item, "condition", {"predicate": "materials are available"},
              applies=["carpentry", "carpentry_role"]),
        _fact("campfire_fuel", item, "direct_function", {"function": "supply_campfire_fuel"}),
        _fact("hearth_fuel", item, "direct_function", {"function": "supply_hearth_fuel"}),
        _fact("campfire_condition", item, "condition", {"predicate": "a campfire is reachable"},
              applies=["campfire_fuel"]),
        _fact("apply_splint", item, "direct_function", {"function": "apply_splint"}),
        _fact("remove_splint", item, "direct_function", {"function": "remove_applied_splint"}),
        _fact("spear_fishing", item, "direct_function", {"function": "fish_with_spear"}),
        _fact("spear_wear", item, "effect", {"property": "item_condition", "direction": "decrease"}),
        _fact("alarm", item, "direct_function", {"function": "toggle_alarm"}, rule="alarm_controls"),
        _fact("alarm_effect", item, "effect", {"property": "alarm_state", "direction": "toggle"},
              rule="alarm_controls"),
        _fact("alarm_condition", item, "condition", {"predicate": "the alarm is available"},
              applies=["alarm", "alarm_effect"], rule="alarm_controls"),
    ]
    acquisition_facts = [
        _fact("foraging", item, "acquisition", {"route": {"method": "foraging"},
                                                 "conditions": {"eligible": True}}),
        _fact("new_game", item, "acquisition", {"route": {"method": "new_game", "branch": "Easy"},
                                                 "conditions": {"difficulty": "Easy"}}),
    ]
    source = {"adoption": results.ADOPTION_REF, "fact_counts": {
        "semantic": len(semantic_facts), "acquisition": len(acquisition_facts)}}
    return ({"target_ids": [item], "facts": semantic_facts},
            {"target_ids": [item], "facts": acquisition_facts}, source)


def _block_with_fact(item, fact_ref):
    return next(block for block in item["blocks"] for branch in block["branches"]
                if any(node["fact_ref"] == fact_ref for node in branch["facts"]))


def _branch_with_fact(item, fact_ref):
    return next(branch for block in item["blocks"] for branch in block["branches"]
                if any(node["fact_ref"] == fact_ref for node in branch["facts"]))


def _qualifiers(item):
    return {ref: qualifier for qualifier in item["qualifiers"]
            for ref in qualifier["fact_refs"]}


def test_layer3_composition_contract():
    assert sys.flags.isolated and sys.flags.dont_write_bytecode

    # Small evidence-shaped input covers positive grouping, separation,
    # alternatives, qualifier scope, and order-independent identity.
    semantic, acquisition, source = _small_inputs()
    first = rules.compose(semantic, acquisition, source)
    shuffled_semantic, shuffled_acquisition = deepcopy(semantic), deepcopy(acquisition)
    random.Random(3101).shuffle(shuffled_semantic["facts"])
    random.Random(3102).shuffle(shuffled_acquisition["facts"])
    second = rules.compose(shuffled_semantic, shuffled_acquisition, source)
    assert model.canonical(first) == model.canonical(second)
    fixture = first["items"][0]
    construction = _block_with_fact(fixture, "fact:construction")
    assert "fact:carpentry" in {node["fact_ref"] for branch in construction["branches"]
                                for node in branch["facts"]}
    assert "refinement" in {relation["kind"] for relation in construction["relations"]}
    shared_condition = next(qualifier for qualifier in fixture["qualifiers"]
                            if set(qualifier["fact_refs"])
                            == {"fact:construction_condition", "fact:carpentry_condition"})
    assert shared_condition["scope"] == "block_common"
    assert first["summary"]["relation_kinds"]["equivalent"] == 1
    fuel = _block_with_fact(fixture, "fact:campfire_fuel")
    assert "fact:hearth_fuel" in {node["fact_ref"] for branch in fuel["branches"]
                                  for node in branch["facts"]}
    assert _qualifiers(fixture)["fact:campfire_condition"]["scope"] == "branch_local"
    assert _block_with_fact(fixture, "fact:apply_splint")["block_id"] != \
           _block_with_fact(fixture, "fact:remove_splint")["block_id"]
    assert fixture["unresolved_relations"]
    assert "keep" in fixture["unresolved_relations"][0]["consumer_effect"]
    assert "do not claim causation" in fixture["unresolved_relations"][0]["consumer_effect"]
    assert _block_with_fact(fixture, "fact:alarm")["block_id"] != \
           _block_with_fact(fixture, "fact:alarm_effect")["block_id"]
    acquisition_block = next(block for block in fixture["blocks"] if block["class"] == "acquisition")
    assert [relation["kind"] for relation in acquisition_block["relations"]] == ["alternative"]

    invalid = deepcopy(first)
    invalid["items"][0]["qualifiers"][0]["applies_to_fact_refs"] = ["fact:missing"]
    with pytest.raises(model.CompositionError, match="qualifier application"):
        model.validate_result(invalid)

    # Full adopted input is loaded once. The same in-memory source proves exact
    # fact disposition and the durable result is read back once for Problem 2.
    loaded, composed = results.produce(REPO)
    semantic_payload = loaded["payloads"]["semantic"]
    acquisition_payload = loaded["payloads"]["acquisition"]
    expected = {fact["fact_id"]: fact["item_id"]
                for payload in (semantic_payload, acquisition_payload) for fact in payload["facts"]}
    represented = {}
    for item in composed["items"]:
        for block in item["blocks"]:
            for branch in block["branches"]:
                for node in branch["facts"]:
                    assert node["fact_ref"] not in represented
                    represented[node["fact_ref"]] = item["item_id"]
        for qualifier in item["qualifiers"]:
            for ref in qualifier["fact_refs"]:
                assert ref not in represented
                represented[ref] = item["item_id"]
            assert set(qualifier["applies_to_fact_refs"]) <= expected.keys()
            assert all(expected[ref] == item["item_id"] for ref in qualifier["applies_to_fact_refs"])
    assert represented == expected
    assert composed["summary"]["grouped_blocks"] > 0
    assert set(composed["summary"]["relation_kinds"]) >= {
        "equivalent", "refinement", "context_variant", "alternative"}

    by_item = {item["item_id"]: item for item in composed["items"]}
    hammer = by_item["Base.Hammer"]
    repair_role = next(node for block in hammer["blocks"] for branch in block["branches"]
                       for node in branch["facts"]
                       if node["fact_kind"] == "context_role"
                       and node["payload"] == {"role": "repair_target"})
    assert repair_role["payload"] != {"role": "tool"}
    repair_block = _block_with_fact(hammer, repair_role["fact_ref"])
    repair_relation = next(relation for relation in repair_block["relations"]
                           if repair_role["fact_ref"] in relation["fact_refs"])
    assert repair_relation["direction"]["from_fact_ref"] == repair_role["fact_ref"]

    notebook = by_item["Base.Notebook"]
    record_ref = next(node["fact_ref"] for block in notebook["blocks"] for branch in block["branches"]
                      for node in branch["facts"]
                      if node["fact_kind"] == "direct_function"
                      and node["payload"] == {"function": "record_written_notes"})
    lock_ref = next(node["fact_ref"] for block in notebook["blocks"] for branch in block["branches"]
                    for node in branch["facts"]
                    if node["fact_kind"] == "effect"
                    and node["payload"] == {"property": "written_note_lock", "direction": "update"})
    assert _branch_with_fact(notebook, record_ref)["branch_id"] != _branch_with_fact(notebook, lock_ref)["branch_id"]
    record_qualifiers = {ref: qualifier for ref, qualifier in _qualifiers(notebook).items()
                         if record_ref in qualifier["applies_to_fact_refs"]}
    assert all(record_ref in qualifier["applies_to_fact_refs"] for qualifier in record_qualifiers.values())
    assert all(lock_ref not in qualifier["applies_to_fact_refs"] for qualifier in record_qualifiers.values())

    molotov = by_item["Base.Molotov"]
    attack_ref = next(node["fact_ref"] for block in molotov["blocks"] for branch in block["branches"]
                      for node in branch["facts"] if node["payload"] == {"function": "request_physics_attack"})
    wash_ref = next(node["fact_ref"] for block in molotov["blocks"] for branch in block["branches"]
                    for node in branch["facts"] if node["payload"] == {"function": "wash_carried_equipment"})
    assert _block_with_fact(molotov, attack_ref)["block_id"] != _block_with_fact(molotov, wash_ref)["block_id"]

    plank = by_item["Base.Plank"]
    construction_ref = next(node["fact_ref"] for block in plank["blocks"] for branch in block["branches"]
                            for node in branch["facts"]
                            if node["payload"] == {"activity": "construction"})
    carpentry_ref = next(node["fact_ref"] for block in plank["blocks"] for branch in block["branches"]
                         for node in branch["facts"]
                         if node["payload"] == {"activity": "carpentry_menu_construction"})
    assert _block_with_fact(plank, construction_ref)["block_id"] == _block_with_fact(plank, carpentry_ref)["block_id"]
    apply_ref = next(node["fact_ref"] for block in plank["blocks"] for branch in block["branches"]
                     for node in branch["facts"] if node["payload"] == {"function": "apply_splint"})
    remove_ref = next(node["fact_ref"] for block in plank["blocks"] for branch in block["branches"]
                      for node in branch["facts"] if node["payload"] == {"function": "remove_applied_splint"})
    assert _block_with_fact(plank, apply_ref)["block_id"] != _block_with_fact(plank, remove_ref)["block_id"]

    output = results.write_result(REPO, composed, replace=True)
    readback = results.read_result(REPO)
    assert output == REPO / results.DEFAULT_OUTPUT
    assert model.canonical(readback) == model.canonical(composed)
    assert not any("rule_gap" in relation["reason"] or "metadata_needed" in relation["reason"]
                   for item in readback["items"] for relation in item["unresolved_relations"])
