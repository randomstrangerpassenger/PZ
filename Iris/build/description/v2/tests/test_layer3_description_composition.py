"""One shared production/readback run for the description-composition contract."""
from copy import deepcopy
from pathlib import Path
import random

import pytest

from iris_tooling.domains.layer3 import composition_results as inputs
from iris_tooling.domains.layer3 import composition_rules
from iris_tooling.domains.layer3 import description_composition_results as results
from iris_tooling.domains.layer3 import description_composition_model as model
from iris_tooling.domains.layer3 import description_composition_ko as ko
from iris_tooling.domains.layer3 import description_composition_en as en
from iris_tooling.domains.layer3 import recovery_sources as vocabulary

ROOT = Path(__file__).resolve().parents[5]


def _fixture():
    item = "Base.Fixture"
    rows = []

    def fact(ref, kind, payload, **extra):
        rows.append({"fact_id": "fact:" + ref, "item_id": item, "fact_kind": kind,
                     "payload": payload, "provenance_refs": ["prov:" + ref], **extra})

    fact("repair", "use_context", {"activity": "repair"})
    fact("target", "context_role", {"role": "repair_target"}, context_fact_ref="fact:repair")
    fact("view", "direct_function", {"function": "view_written_note_pages"})
    fact("write", "direct_function", {"function": "record_written_notes"})
    fact("lock", "effect", {"property": "written_note_lock", "direction": "update"})
    fact("editing", "condition", {"predicate": vocabulary.NOTE_EDIT}, applies_to_fact_refs=["fact:write"])
    fact("spear", "direct_function", {"function": "fish_with_spear"})
    fact("wear", "effect", {"property": "item_condition", "direction": "decrease"})
    fact("fuel", "direct_function", {"function": "supply_campfire_fuel"})
    fact("hearth", "direct_function", {"function": "supply_hearth_fuel"})
    acquisition = [{"fact_id": "fact:" + difficulty, "item_id": item, "fact_kind": "acquisition",
                    "payload": {"route": {"method": "new_game", "branch": difficulty},
                                "conditions": {"difficulty": difficulty}},
                    "provenance_refs": ["prov:" + difficulty]} for difficulty in ("Easy", "Normal")]
    blocks, qualifiers, unresolved = composition_rules.semantic_blocks(item, rows)
    blocks.append(composition_rules.acquisition_block(item, acquisition))
    return {"item_id": item, "blocks": sorted(blocks, key=lambda b: b["block_id"]),
            "qualifiers": qualifiers, "unresolved_relations": unresolved}


def _compare_meaning(source, output):
    assert output["item_id"] == source["item_id"]
    anchors = {f["fact_ref"]: (block["block_id"], branch["branch_id"])
               for block in source["blocks"] for branch in block["branches"] for f in branch["facts"]}
    qualifiers = {q["qualifier_id"]: q for q in source["qualifiers"]}
    assert output["qualifiers"] == [qualifiers[q] for q in sorted(qualifiers)]
    all_refs = set(anchors) | {r for q in qualifiers.values() for r in q["fact_refs"]}
    assert set(output['preserved_fact_refs']) == all_refs
    assert output["relations"] == sorted([r for b in source["blocks"] for r in b["relations"]],
                                          key=lambda r: r["relation_id"])
    assert output["unresolved_relations"] == source["unresolved_relations"]
    for locale in ("ko", "en"):
        expanded = output["locales"][locale]["expanded"]
        # Missing rules are failures, not an accepted corpus-sized silence.
        assert expanded['state'] != 'failed', (source['item_id'], expanded['reason'])
        represented = set()
        for segment in expanded["segments"]:
            represented.update(segment["fact_refs"])
            refs = set(segment["fact_refs"]) & anchors.keys()
            expected_q = {q for q, value in qualifiers.items() if refs & set(value["applies_to_fact_refs"])}
            expected_q = {q for q in expected_q if not (refs & set(qualifiers[q]['applies_to_fact_refs'])) <= {
                r for decision in output['public_plan'] if decision['disposition'] == 'internal'
                and set(qualifiers[q]['fact_refs']) <= set(decision['fact_refs'])
                for r in decision.get('applies_to_fact_refs', [])}}
            if segment['expression'] == 'public_use':
                expected_q = set()  # capability/result claims do not assert full execution predicates
            assert set(segment["qualifier_refs"]) == expected_q
            for q in expected_q:
                # No condition may spread to a co-ordinated independent claim.
                if segment['expression'] == 'exact_scope':
                    assert refs <= set(qualifiers[q]["applies_to_fact_refs"])
                elif segment['expression'] == 'equivalent_scope':
                    same_condition = {r for other in expected_q if qualifiers[other]['payload'] == qualifiers[q]['payload']
                                      for r in qualifiers[other]['applies_to_fact_refs']}
                    assert refs <= same_condition
            assert segment["qualifier_applications"] == [{"qualifier_id": q,
                "applies_to_fact_refs": qualifiers[q]["applies_to_fact_refs"]} for q in sorted(expected_q)]
            assert set(segment["block_refs"]) == {anchors[r][0] for r in refs}
            assert set(segment["branch_refs"]) == {anchors[r][1] for r in refs}
        assert represented <= all_refs
        hidden = {r for u in output['internal_uses'] for r in u['fact_refs']}
        assert not hidden & represented
        # Every independently admitted use remains public, including recipe-only
        # materials and transformation targets. Only the named maintenance and
        # portable-light toggle are exempt, never a length or primary-use rank.
        independent = {f['fact_ref'] for b in source['blocks'] for br in b['branches'] for f in br['facts']
                       if f['fact_kind'] in {'direct_function', 'use_context', 'context_role'}
                       and f['payload'].get('function') != 'toggle_activation'} - hidden
        assert independent <= represented, (source['item_id'], independent - represented)
        compact = output["locales"][locale]["compact"]
        assert compact["state"] != "failed", (source["item_id"], compact["reason"])
        compact_refs = {r for segment in compact['segments'] for r in segment['fact_refs']}
        assert independent <= compact_refs, (source['item_id'], independent - compact_refs)
        assert "\n" not in compact["text"]
        for segment in compact["segments"]:
            for disposition in segment.get("qualifier_dispositions", []):
                q = qualifiers[disposition["qualifier_ref"]]
                assert set(disposition["applies_to_fact_refs"]) <= set(q["applies_to_fact_refs"])
                if disposition["placement"] in {"compact_summary", "compact_core"}:
                    assert disposition["text"] in segment["text"]
                else:
                    assert disposition["placement"] == "expanded" and disposition["text"] is None
        linked = set()
        for link in compact["detail_links"]:
            assert link["fact_refs"] == expanded["segments"][link["segment"]]["fact_refs"]
            linked.update(link["fact_refs"])
        assert linked == represented
    for surface in ("compact", "expanded"):
        a, b = (output["locales"][loc][surface] for loc in ("ko", "en"))
        assert a["state"] == b["state"]
        assert {r for s in a["segments"] for r in s["fact_refs"]} == {
            r for s in b["segments"] for r in s["fact_refs"]}


def test_layer3_description_composition(monkeypatch):
    assert ko.instrumental("도구") == "도구로"
    assert ko.instrumental("재료") == "재료로"
    assert ko.instrumental("부착물") == "부착물로"
    assert ko.instrumental("수리 대상") == "수리 대상으로"
    assert ko.parallel(["착용할 수 있다", "보관할 수 있다"]) == "착용하거나 보관할 수 있다."
    assert en.parallel(["It can store water", "It can carry food"]) == "It can store water and carry food."
    fixture = _fixture()
    first = results.compose_item(fixture)
    _compare_meaning(fixture, first)
    shuffled = deepcopy(fixture)
    rng = random.Random(27)
    rng.shuffle(shuffled["blocks"])
    rng.shuffle(shuffled["qualifiers"])
    for block in shuffled["blocks"]:
        rng.shuffle(block["branches"])
        for branch in block["branches"]:
            rng.shuffle(branch["facts"])
    assert first == results.compose_item(shuffled)
    text = first["locales"]["en"]["expanded"]["text"]
    assert "item to be repaired" not in text and "as a tool" not in text
    assert 'fact:target' in {r for entry in first['internal_uses'] for r in entry['fact_refs']}
    assert "Easy difficulty" not in text and "Normal difficulty" not in text
    assert "therefore" not in text and "fishing causes" not in text
    assert first["unresolved_relations"]
    assert "fact:wear" not in {r for s in first["locales"]["en"]["compact"]["segments"] for r in s["fact_refs"]}
    assert "fact:wear" in {r for s in first["locales"]["en"]["expanded"]["segments"] for r in s["fact_refs"]}
    both_roles = deepcopy(fixture)
    fuel_fact = next(f for b in both_roles["blocks"] for branch in b["branches"] for f in branch["facts"]
                     if f["payload"].get("function") == "supply_hearth_fuel")
    fuel_fact["payload"] = {"function": "provide_campfire_tinder"}
    consumed = results.compose_item(both_roles)["locales"]["en"]["compact"]["text"]
    assert "fuel" in consumed and "tinder" in consumed
    assert "with an igniter and fuel" not in consumed
    for loc in ("ko", "en"):
        assert 'fact:lock' in first['preserved_fact_refs']
        assert not any('fact:lock' in s['fact_refs'] for s in first['locales'][loc]['expanded']['segments'])
    extra_condition = deepcopy(fixture)
    extra = deepcopy(extra_condition["qualifiers"][0])
    extra.update(qualifier_id="qualifier:additional", fact_refs=["fact:additional"],
                 payload={"predicate": vocabulary.SMOKING})
    extra_condition["qualifiers"].append(extra)
    additionally_scoped = results.compose_item(extra_condition)
    _compare_meaning(extra_condition, additionally_scoped)
    # A known additional predicate must defeat the closed note frame, rather
    # than vanish because the frame recognizes the function name.
    assert "A match or lighter is required" in additionally_scoped["locales"]["en"]["compact"]["text"]
    broken = deepcopy(fixture)
    broken["qualifiers"][0]["payload"] = {"predicate": "unimplemented qualifier"}
    failure = results.compose_item(broken)
    assert all(row["state"] == "failed" and row["text"] == "" for surfaces in failure["locales"].values()
               for row in surfaces.values())

    # Overlapping wording may be shared only inside the same application scope.
    rows = []
    def claim(name, kind, payload, **extra):
        rows.append(dict(fact_id='fact:' + name, item_id='Base.Fixture', fact_kind=kind,
                         payload=payload, provenance_refs=['prov:' + name], **extra))
    claim('ammo', 'direct_function', {'function': 'load_matching_ammunition'})
    claim('load', 'condition', {'predicate': vocabulary.LOADING}, applies_to_fact_refs=['fact:ammo'])
    claim('path', 'condition', {'predicate': vocabulary.AMMUNITION_LOADING_PATHS}, applies_to_fact_refs=['fact:ammo'])
    claim('paint', 'direct_function', {'function': 'paint_supported_surface'})
    claim('sign', 'direct_function', {'function': 'paint_wall_sign'})
    claim('paint_condition', 'condition', {'predicate': vocabulary.PAINTING}, applies_to_fact_refs=['fact:paint'])
    claim('sign_condition', 'condition', {'predicate': vocabulary.PAINT_ACTIONS}, applies_to_fact_refs=['fact:sign'])
    claim('ignition', 'direct_function', {'function': 'ignite_hearth_with_petrol'})
    claim('ignite_condition', 'condition', {'predicate': vocabulary.HEARTH_PETROL}, applies_to_fact_refs=['fact:ignition'])
    blocks, qualifiers, unresolved = composition_rules.semantic_blocks('Base.Fixture', rows)
    overlap = dict(item_id='Base.Fixture', blocks=blocks, qualifiers=qualifiers, unresolved_relations=unresolved)
    rendered = results.compose_item(overlap)
    _compare_meaning(overlap, rendered)
    for loc in ('ko', 'en'):
        detail = rendered['locales'][loc]['expanded']
        ammo = next(s for s in detail['segments'] if 'fact:ammo' in s['fact_refs'])
        assert {'fact:load', 'fact:path'} <= set(ammo['fact_refs'])
        assert ('달리면' if loc == 'ko' else 'Running interrupts') not in ammo['text']
        assert not any({'fact:paint', 'fact:sign'} <= set(s['fact_refs']) for s in detail['segments'])
        ignition = next(s for s in rendered['locales'][loc]['compact']['segments'] if 'fact:ignition' in s['fact_refs'])
        assert ('도구' if loc == 'ko' else 'tool') not in ignition['text']
    # A new, known condition must prevent the short ammunition frame from
    # silently absorbing an additional requirement.
    more = deepcopy(overlap)
    extra = deepcopy(next(q for q in more['qualifiers'] if 'fact:load' in q['fact_refs']))
    extra.update(qualifier_id='qualifier:ammo-extra', fact_refs=['fact:ammo-extra'],
                 payload={'predicate': vocabulary.SMOKING})
    more['qualifiers'].append(extra)
    guarded = results.compose_item(more)
    _compare_meaning(more, guarded)
    assert 'A match or lighter is required' in guarded['locales']['en']['compact']['text']

    # A repair target sharing its branch with a repair-material role must not
    # hide that independently useful material role in the maintenance detail.
    rows = []
    claim('repair-context', 'use_context', {'activity': 'repair'})
    claim('repair-target', 'context_role', {'role': 'repair_target'}, context_fact_ref='fact:repair-context')
    claim('repair-material', 'context_role', {'role': 'repair_material'}, context_fact_ref='fact:repair-context')
    blocks, qualifiers, unresolved = composition_rules.semantic_blocks('Base.Fixture', rows)
    repair = dict(item_id='Base.Fixture', blocks=blocks, qualifiers=qualifiers, unresolved_relations=unresolved)
    repaired = results.compose_item(repair)
    _compare_meaning(repair, repaired)
    for loc in ('ko', 'en'):
        assert 'fact:repair-material' in {r for s in repaired['locales'][loc]['compact']['segments'] for r in s['fact_refs']}

    # A complete treatment sentence can represent the action and state only
    # when they share the very same qualifier application, not merely wording.
    rows = []
    claim('stitch', 'direct_function', {'function': 'stitch_wound'})
    claim('stitched', 'effect', {'property': 'stitched_state', 'direction': 'set_true'})
    claim('stitch-scope', 'condition', {'predicate': vocabulary.STITCHING},
          applies_to_fact_refs=['fact:stitch', 'fact:stitched'])
    blocks, qualifiers, unresolved = composition_rules.semantic_blocks('Base.Fixture', rows)
    treatment = dict(item_id='Base.Fixture', blocks=blocks, qualifiers=qualifiers, unresolved_relations=unresolved)
    treated = results.compose_item(treatment)
    _compare_meaning(treatment, treated)
    assert treated['relations'] == []
    for loc in ('ko', 'en'):
        for depth in ('compact', 'expanded'):
            combined = [s for s in treated['locales'][loc][depth]['segments']
                        if {'fact:stitch', 'fact:stitched'} <= set(s['fact_refs'])]
            assert len(combined) == 1
            assert combined[0]['text'].count('붕대' if loc == 'ko' else 'unbandaged') == 1
    split = deepcopy(treatment)
    scope = split['qualifiers'][0]
    scope['applies_to_fact_refs'] = ['fact:stitch']
    other = deepcopy(scope)
    other.update(qualifier_id='qualifier:separate-effect', fact_refs=['fact:separate-effect'],
                 applies_to_fact_refs=['fact:stitched'])
    split['qualifiers'].append(other)
    split_result = results.compose_item(split)
    _compare_meaning(split, split_result)
    assert not any({'fact:stitch', 'fact:stitched'} <= set(s['fact_refs'])
                   for s in split_result['locales']['en']['expanded']['segments'])

    # The only full source read and full production in this acceptance command.
    source, result = results.produce(ROOT)
    assert len(source["items"]) == len(result["items"]) == 2105
    assert result["summary"]["surfaces"] == 8420
    examples = {i['item_id']: i['locales']['ko'] for i in result['items']}
    socks = examples['Base.Socks_Ankle']['expanded']['text']
    assert all(word not in socks for word in ('씻', '젖', '패딩', '중단', '데님', '가위'))
    assert all(word in socks for word in ('신을 수 있다', '연료', '불쏘시개', '찢어진 천', '로프'))
    assert '몸과 의류, 장비' in examples['Base.Soap2']['compact']['text']
    assert '통조림 따개' in examples['Base.CannedCorn']['compact']['text']
    assert '옥수수' in examples['Base.CannedCorn']['compact']['text']
    assert '도구 없이' not in examples['Base.223Box']['expanded']['text']
    assert '.223' in examples['Base.223Box']['compact']['text']
    assert '당근 씨앗' in examples['farming.CarrotBagSeed']['compact']['text']
    assert '칼로 손질해 개구리 고기' in examples['Base.Frog']['expanded']['text']
    assert len(examples['Base.Socks_Ankle']['expanded']['use_units']) == 4
    assert all(name not in examples['Base.Screwdriver']['expanded']['text'] for name in ('V1', 'V2', 'V3', '회수량'))
    # The opened result admits drink_food_contents, overriding the generic
    # native eat dispatch on the sealed item without transferring other uses.
    assert '연유를 마실 수 있다' in examples['Base.CannedMilk']['expanded']['text']
    assert '개봉해 옥수수를 먹을 수 있다' in examples['Base.CannedCorn']['expanded']['text']
    assert '통조림 따개로 개봉해 스프를 마실 수 있다' in examples['Base.TinnedSoup']['expanded']['text']
    for item_id, name in (('Base.CannedCarrots2', '당근을'), ('Base.CannedMushroomSoup', '버섯스프를'),
                          ('Base.Dogfood', '개 사료를'), ('Base.CannedSardines', '정어리를')):
        assert '개봉해 ' + name + ' 먹을 수 있다' in examples[item_id]['expanded']['text']
        assert '미끼' not in examples[item_id]['expanded']['text']
    assert '통조림 따개' not in examples['Base.CannedSardines']['compact']['text']
    for surface in ('compact', 'expanded'):
        assert examples['Base.CannedMilk'][surface]['text'].count('연유') == 2
        assert '내용물' not in examples['Base.CannedMilk'][surface]['text']
        assert '요리' not in examples['Base.Dogfood'][surface]['text']
    english = {i['item_id']: i['locales']['en'] for i in result['items']}
    # Tool purpose is distinct from the material's recovery conditions.
    for surface in ('compact', 'expanded'):
        scissors = examples['Base.Scissors'][surface]['text']
        assert all(word in scissors for word in ('데님', '가죽', '의류', '회수'))
        assert all(word not in scissors for word in ('실도 회수', '가위가 필요', '직물 회수'))
        assert 'scissors' not in english['Base.Scissors'][surface]['text'].lower()
        assert '가위' in examples['Base.Gloves_LeatherGloves'][surface]['text']
    furniture_tools = [i['item_id'] for i in source['items'] if any(
        f['payload'].get('activity') == 'moving_furniture'
        for b in i['blocks'] for branch in b['branches'] for f in branch['facts'])]
    for item_id in furniture_tools:
        assert '일부 가구를 집어 들거나 설치' not in examples[item_id]['expanded']['text']
        assert 'pick up or place certain furniture' not in english[item_id]['expanded']['text']
        item = next(row for row in result['items'] if row['item_id'] == item_id)
        assert any('concrete PickUpTool/PlaceTool' in d['reason'] for d in item['internal_uses'])
    assert '0이 된다' in examples['Base.Wrench']['expanded']['text']
    assert '좀비화는 막지 못한다' in examples['Base.Antibiotics']['expanded']['text']
    for item_id in ('Base.Pasta', 'Base.Rice'):
        assert examples[item_id]['compact']['text'] == '먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.'
        assert 'It can be eaten or used as a cooking ingredient.' in english[item_id]['compact']['text']
        assert all(word in examples[item_id]['expanded']['text'] for word in ('먹을 수 있다', '요리 재료', '미끼'))
    for item_id in ('Base.Teacup', 'Base.MugWhite'):
        for surface in ('compact', 'expanded'):
            assert examples[item_id][surface]['text'] == '물을 담아 보관하거나 운반할 수 있다.'
            assert english[item_id][surface]['text'] == 'It can hold water for storage or carrying.'
    for surface in ('compact', 'expanded'):
        assert 'eat the Carrots' in english['Base.CannedCarrots2'][surface]['text']
        assert 'eat the Mushroom Soup' in english['Base.CannedMushroomSoup'][surface]['text']
        assert 'drink the Vegetable Soup' in english['Base.TinnedSoup'][surface]['text']
        assert 'Can Opener' not in english['Base.CannedSardines'][surface]['text']
        assert 'cooking ingredient' not in english['Base.Dogfood'][surface]['text']
    # Individual serving results belong to the recipe relation, while the
    # independent opening, eating and cooking uses remain in both surfaces.
    for surface in ('compact', 'expanded'):
        beans = examples['Base.TinnedBeans'][surface]['text']
        assert '그릇 (콩)' not in beans
        assert all(word in beans for word in ('통조림 따개', '먹을 수 있다', '요리 재료'))
    assert '원래 음식' not in examples['Base.Axe']['expanded']['text']
    assert all(name in examples['Base.Remote']['expanded']['text'] for name in ('수신기', '건전지도 나올 수', '원격제어 조정기'))
    for item_id in ('Base.GardenSaw', 'Base.Saw'):
        for surface in ('compact', 'expanded'):
            assert '파이프 폭탄' in examples[item_id][surface]['text']
            assert '신호 장치' not in examples[item_id][surface]['text']
    for item_id in ('Base.Flour', 'Base.Cornflour'):
        assert len(examples[item_id]['expanded']['use_units']) == 1
        assert all(examples[item_id][surface]['text'] == '요리 재료로 쓸 수 있다.' for surface in ('compact', 'expanded'))
    assert '반죽' in examples['Base.Yeast']['expanded']['text']
    for item_id in ('Base.RemoteCraftedV1', 'Base.RemoteCraftedV2', 'Base.RemoteCraftedV3'):
        assert len(examples[item_id]['expanded']['use_units']) == 1
        assert all(word in examples[item_id]['expanded']['text'] for word in ('함께 소지', '호환', '조종 범위'))
    for item_id in ('Base.FishingRod', 'Base.FishingRodTwineLine', 'Base.CraftedFishingRod', 'Base.CraftedFishingRodTwineLine'):
        lines = examples[item_id]['expanded']['text'].splitlines()
        assert all(word in lines[0] for word in ('낚시', '낚싯줄', '미끼를 잃는다'))
        assert len(examples[item_id]['expanded']['use_units']) == 2
    assert '소모될 수 있다' in examples['Base.SharpedStone']['expanded']['text'].splitlines()[0]
    # Optional eating utensils are internal; actual cooking, spear and melee
    # purposes remain public in the common producer.
    assert all(word in examples['Base.Fork']['expanded']['text'] for word in ('음식 준비', '창', '무기'))
    assert '식기' not in examples['Base.Fork']['expanded']['text']
    assert '타이머' not in examples['Base.Remote']['expanded']['text']
    assert len(examples['Base.Tongs']['expanded']['use_units']) == 1
    assert '0.6' in examples['Base.Bass']['expanded']['text']
    assert '0.6' not in examples['Base.KitchenKnife']['expanded']['text']
    assert '소음 발생 장치' in examples['Base.ElectronicsScrap']['expanded']['text']
    assert '폭발 장치' in examples['Base.ElectronicsScrap']['expanded']['text']
    # Participant roles and compact grouping must not turn a processed item
    # into a processing supply or erase another independently admitted use.
    assert '상처에 감을 수 있다. 소독해서 쓸 수도 있다' in examples['Base.Bandage']['expanded']['text']
    assert len(examples['Base.Bandage']['expanded']['use_units']) == 2
    for item_id in ('Base.Watermelon', 'Base.Muffintray_Biscuit'):
        for surface in ('compact', 'expanded'):
            assert examples[item_id][surface]['text'] == '덫의 미끼로 쓸 수 있다.'
    assert '수박 쪼개기' in examples['Base.Plank']['expanded']['text']
    assert '칼로 손질해 개구리 고기' in examples['Base.Frog']['expanded']['text']
    assert '천 조각' in examples['Base.Sheet']['compact']['text']
    assert '찢어진 천 (오염됨)' in examples['Base.Sheet']['expanded']['text']
    assert '설치 후 열고' not in examples['Base.Sheet']['expanded']['text']
    assert '소독솜을 만드는' in examples['Base.CottonBalls']['compact']['text']
    assert '천이나 솜을 소독' in examples['Base.Disinfectant']['compact']['text']
    assert '손질해 살을' in examples['Base.Bass']['compact']['text']
    assert '수박 쪼개기' in examples['Base.Plank']['compact']['text']
    assert '시트 로프 제작 재료로' in examples['Base.Sheet']['expanded']['text']
    assert '달걀곽에' in examples['Base.Egg']['expanded']['text']
    assert '제작 대상:' not in examples['Base.Egg']['expanded']['text']
    assert examples['Base.Nails']['compact']['text'].count('수리') == 1
    assert '나무 막대가' not in examples['Base.CraftedFishingRod']['expanded']['text']
    assert '휴대 조명' in examples['Base.Lighter']['expanded']['text']
    assert '중단' not in examples['Base.Lighter']['expanded']['text']
    assert '3개' not in examples['Base.BrokenFishingNet']['expanded']['text']
    for original, rendered in zip(source["items"], result["items"], strict=True):
        _compare_meaning(original, rendered)
        assert all('·' not in row['text'] for surfaces in rendered['locales'].values() for row in surfaces.values())
        functions = {f["payload"].get("function") for b in original["blocks"] for branch in b["branches"] for f in branch["facts"]}
        if "control_portable_light" in functions:
            operations = {f["fact_ref"] for b in original["blocks"] for branch in b["branches"] for f in branch["facts"]
                          if f["payload"].get("function") in {"toggle_activation", "extinguish_candle", "extinguish_on_unequip"}}
            overview_refs = {ref for s in rendered["locales"]["en"]["compact"]["segments"] for ref in s["fact_refs"]}
            assert not operations & overview_refs
        for segment in rendered["locales"]["en"]["compact"]["segments"]:
            reason = segment.get("placement_reason", "")
            if reason.startswith("factor common ignition"):
                # An implement overview must not turn the target/method
                # branches into a promise that every method lights every target.
                assert segment["text"].count("lighting") == 1
                assert "petrol" not in segment["text"] and "tinder" not in segment["text"]
                if "ignite_industrial_fire_with_petrol" in functions:
                    assert "petrol" in rendered["locales"]["en"]["expanded"]["text"].lower()
            if reason.startswith("water storage/use purposes"):
                assert "0.3" not in segment["text"] and "20" not in segment["text"]
                if "poisoning" in segment["text"]:
                    detailed = rendered["locales"]["en"]["expanded"]["text"]
                    assert "tainted" in detailed.lower() and "poison" in detailed.lower()
                    assert any('0.3' in q['payload']['predicate'] for q in rendered['qualifiers'])
    results.write_result(ROOT, result)
    with monkeypatch.context() as patch:
        def forbidden(*args, **kwargs):
            raise AssertionError("reader must not invoke production or reread semantic input")
        patch.setattr(results, "produce", forbidden)
        patch.setattr(results, "compose", forbidden)
        patch.setattr(inputs, "read_result", forbidden)
        restored = results.read_result(ROOT)
    assert restored == result
    bad = deepcopy(result)
    bad["items"][0]["locales"]["ko"]["compact"]["locale"] = "en"
    with pytest.raises(ValueError, match="identity"):
        model.validate_result(bad)
    bad = {**result, "schema": "invalid"}
    with pytest.raises(ValueError, match="schema"):
        model.validate_result(bad)
