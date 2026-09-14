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
    semantic_payload = loaded["composition_semantic"]
    acquisition_payload = loaded["payloads"]["acquisition"]
    # The immutable r6 payload remains the predecessor. The existing recovery
    # owner supplies a separately identified, bounded successor fact delta.
    predecessor_refs = {f['fact_id'] for f in loaded['payloads']['semantic']['facts']}
    correction = composed['source']['semantic_correction']
    corrected_refs = {f['fact_id'] for f in correction['facts']}
    assert not predecessor_refs & corrected_refs
    assert {f['fact_id'] for f in semantic_payload['facts']} == predecessor_refs | corrected_refs
    assert {f['item_id'] for f in correction['facts'] if f['admission']['rule_ref'] not in {'declared_learning_and_recorded_content', 'installed_battery_power_purpose', 'installed_vehicle_light_purpose', 'declared_morale_reading_purpose', 'declared_attachment_purpose', 'placed_sprite_purpose', 'native_attachment_purpose', 'native_device_purpose'}} == {
        'Base.UmbrellaBlack', 'Base.UmbrellaBlue', 'Base.UmbrellaRed', 'Base.UmbrellaWhite',
        'Base.Pills', 'Base.PillsAntiDep', 'Base.PillsBeta', 'Base.PillsSleepingTablets',
        'Base.PillsVitamins', 'Base.Antibiotics', 'Base.Generator'}
    devices = [f for f in correction['facts'] if f['admission']['rule_ref'] == 'native_device_purpose']
    assert len(devices) == 7
    assert {f['item_id'] for f in devices if f['payload']['function'] == 'supply_nearby_electricity'} == {'Base.Generator'}
    assert {f['item_id'] for f in devices if f['payload']['function'] == 'emit_attracting_noise'} == {
        'Base.NoiseTrap', 'Base.NoiseTrapTriggered', 'Base.NoiseTrapRemote',
        'Base.NoiseTrapSensorV1', 'Base.NoiseTrapSensorV2', 'Base.NoiseTrapSensorV3'}
    lessons = [f for f in correction['facts'] if f['payload'].get('function', '').startswith('learn_literature_')]
    assert len(lessons) == 30
    assert {f['payload']['function'] for f in lessons if f['item_id'] == 'Base.CookingMag1'} == {'learn_literature_cooking'}
    # Recipe-name overloads must not discard the supported common lesson.
    assert {f['payload']['function'] for f in lessons if f['item_id'] == 'Base.FishingMag1'} == {'learn_literature_fishing'}
    assert {f['payload']['function'] for f in lessons if f['item_id'] == 'Base.ElectronicsMag3'} == {'learn_literature_electrical'}
    media = [f for f in correction['facts'] if f['payload'].get('function', '').startswith('recorded_content_')]
    assert {f['payload']['function'] for f in media if f['item_id'] == 'Base.Disc_Retail'} == {'recorded_content_boredom'}
    assert {f['item_id'] for f in media} == {'Base.Disc_Retail', 'Base.VHS_Retail', 'Base.VHS_Home'}
    native_attachments = [f for f in correction['facts'] if f['admission']['rule_ref'] == 'native_attachment_purpose']
    assert {f['item_id'] for f in native_attachments} == {'Base.Bayonnet', 'Base.GunLight', 'Base.RedDot'}
    assert all(f['payload'] == {'function': 'attachment_purpose_movement_aim'} for f in native_attachments)
    placed = [f for f in correction['facts'] if f['admission']['rule_ref'] == 'placed_sprite_purpose']
    assert placed and all(f['payload']['function'].startswith('placed_purpose_') for f in placed)
    assert any(f['item_id'] == 'Base.Mov_BluePlasticChair' and f['payload']['function'] == 'placed_purpose_sleep' for f in placed)
    assert any(f['item_id'] == 'Base.Mov_AirConditioner' and f['payload']['function'] == 'placed_purpose_salvage_welding' for f in placed)
    assert not any(f['item_id'] == 'Base.Mov_AirConditioner' and f['payload']['function'] != 'placed_purpose_salvage_welding' for f in placed)
    attachments = [f for f in correction['facts'] if f['admission']['rule_ref'] == 'declared_attachment_purpose']
    assert len(attachments) == 12
    assert not {'Base.Bayonnet', 'Base.GunLight'} & {f['item_id'] for f in attachments}
    assert {f['payload']['function'] for f in attachments if f['item_id'] == 'Base.AmmoStraps'} == {'attachment_purpose_reload'}
    assert len(corrected_refs) == 88 + len(placed) + len(native_attachments) + len(devices)
    assert {f['item_id'] for f in correction['facts'] if f['payload'].get('function') == 'supply_vehicle_electrical_power'} == {'Base.CarBattery1', 'Base.CarBattery2', 'Base.CarBattery3'}
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
    for item in composed['items']:
        for relation in item.get('use_relations', []):
            assert set(relation['fact_refs']) <= expected.keys()
            assert set(relation['observation_refs']) <= semantic_payload['observations'].keys()
            assert all(':' not in tool['item_id'] for g in relation['tools'] for tool in g['items'])
    juice = by_item['Base.CannedFruitBeverage']['use_relations'][0]
    assert juice['results'][0]['item_id'] == 'Base.CannedFruitBeverageOpen'
    assert juice['results'][0]['food_type'] == 'Juice'
    assert juice['result_consumption']['fact']['payload'] == {'function': 'eat_food'}
    corn = by_item['Base.CannedCorn']['use_relations'][0]
    assert corn['results'][0]['item_id'] == 'Base.CannedCornOpen'
    assert corn['results'][0]['names']['ko'] == '옥수수'
    assert corn['tools'][0]['items'][0]['item_id'] == 'Base.TinOpener'
    assert corn['result_consumption']['fact']['item_id'] == 'Base.CannedCornOpen'
    assert corn['result_consumption']['fact']['payload'] == {'function': 'eat_food'}
    invalid = deepcopy(composed)
    next(i for i in invalid['items'] if i['item_id'] == 'Base.CannedCorn')['use_relations'][0]['result_consumption']['fact']['item_id'] = 'Base.CannedCarrotsOpen'
    with pytest.raises(model.CompositionError, match='exact target fact'):
        model.validate_result(invalid)
    drinking = by_item['Base.TinnedSoup']['use_relations'][0]['result_consumption']
    assert drinking['fact']['payload'] == {'function': 'drink_food_contents'}
    assert drinking['qualifiers']
    invalid = deepcopy(composed)
    next(i for i in invalid['items'] if i['item_id'] == 'Base.TinnedSoup')['use_relations'][0]['result_consumption']['qualifiers'] = []
    with pytest.raises(model.CompositionError, match='scope drift'):
        model.validate_result(invalid)
    soup = by_item['Base.CannedMushroomSoup']['use_relations'][0]['results'][0]
    assert soup['names']['en'] == 'Mushroom Soup' and soup['names']['ko'] == '버섯스프'
    from iris_tooling.domains.layer3 import recovery_sources
    rejected = {'target_ids': ['Base.UmbrellaBlack'], 'observations': {}}
    declaration = next(o for o in correction['observations'].values()
        if o.get('content', {}).get('raw', '').lstrip().startswith('item UmbrellaBlack'))
    changed = deepcopy(declaration)
    # Property conflicts are never resolved by selecting a first declaration.
    changed['content']['property_conflicts'] = {'ProtectFromRainWhenEquipped': ['TRUE', 'FALSE']}
    rejected['observations']['obs:conflicting'] = changed
    assert recovery_sources.supplement_player_uses(REPO, rejected)['facts'] == []
    assert by_item['Base.CannedSardines']['use_relations'][0]['tools'] == []
    assert by_item['Base.223Box']['use_relations'][0]['tools'] == []
    frog = by_item['Base.Frog']['use_relations'][0]
    assert len(frog['tools']) == 1 and len(frog['tools'][0]['items']) == 5
    assert frog['result_use'] is None
    remote = by_item['Base.Remote']['use_relations'][0]
    assert {(r['item_id'], r['kind']) for r in remote['results']} == {
        ('Base.Receiver', 'declared'), ('Base.ElectronicsScrap', 'callback_unconditional'),
        ('Base.Battery', 'callback_conditional')}
    assert by_item['Base.BrokenFishingNet']['use_relations'] == []
    onion = by_item['Base.SackProduce_Onion']['use_relations'][0]
    assert onion['results'][0]['names']['ko'] == '양파' and onion['result_use'] is None
    assert by_item['farming.CarrotBagSeed']['use_relations'][0]['results'][0]['count'] == '50'
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
