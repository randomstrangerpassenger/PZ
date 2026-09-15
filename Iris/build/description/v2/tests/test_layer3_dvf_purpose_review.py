"""Purpose admission, role preservation and corpus-wide regression checks."""
from copy import deepcopy
import json
from pathlib import Path

from iris_tooling.domains.layer3 import purpose_evidence as evidence
from iris_tooling.domains.layer3 import description_composition_results as descriptions
from iris_tooling.domains.layer3 import description_composition_en as en

ROOT = Path(__file__).resolve().parents[5]


def test_consumer_relations_do_not_infer_from_display_names():
    accepted = {'Example.Food': ['bird']}
    assert evidence.for_item('Example.Food', {'DisplayName': 'Stone'}, accepted)['accepted_animals'] == ['bird']
    assert evidence.for_item('Example.Other', {'DisplayName': 'Bread'}, accepted)['accepted_animals'] == []
    assert evidence.for_item('Example.Device', {'Type': 'Radio', 'TwoWay': 'true'}, accepted)['speech_transmission']
    assert 'speech_transmission' not in evidence.for_item('Example.Device', {'Type': 'Radio', 'DisplayName': 'Two Way Radio'}, accepted)
    # This exact string test is the reviewed native constructor, not a tag or
    # human-language guess that all classic-looking watches are analog.
    assert evidence.for_item('Example.ClassicClock', {'Type': 'AlarmClockClothing'}, accepted)['digital_alarm'] is False
    assert evidence.for_item('Example.Clock', {'Type': 'AlarmClockClothing', 'DisplayName': 'Classic'}, accepted)['digital_alarm'] is True


def test_named_result_grammar_preserves_mass_and_count():
    def noun(name, **other):
        return en.object_phrase({'names': {'en': name}, **other})
    assert noun('Amplifier') == 'an amplifier'
    assert noun('Mattress') == 'a mattress'
    assert noun('Electronics Scrap') == 'electronics scrap'
    assert noun('.45 Auto', declared_traits={'DisplayCategory': 'Ammo'}) == '.45 auto rounds'
    assert noun('Biscuit', count='6') == 'biscuits'
    assert en.coordinated_actions(['modifying devices', 'repairing weapons', 'repairing vehicle parts']) == 'modifying devices and repairing weapons and vehicle parts'


def test_all_admitted_scopes_and_renamed_processing_target():
    blocks = json.loads((ROOT / 'Iris/build/description/composition/blocks.json').read_bytes())
    rows = {i['item_id']: i for i in blocks['items']}
    rendered = {i['item_id']: i for i in json.loads((ROOT / 'Iris/build/description/composition/descriptions.json').read_bytes())['items']}
    accepted = evidence.load(ROOT)
    bait_ids = set()
    for item_id, item in rows.items():
        functions = {f['payload'].get('function') for b in item['blocks'] for branch in b['branches'] for f in branch['facts']}
        if 'supply_trap_bait' in functions:
            bait_ids.add(item_id)
            for locale, word in [('ko', '덫의 미끼'), ('en', 'trap bait')]:
                for surface in ('compact', 'expanded'):
                    assert (word in rendered[item_id]['locales'][locale][surface]['text']) == bool(accepted.get(item_id)), item_id
        traits = item.get('source_traits', {}).get('purpose_evidence', {})
        for locale in ('ko', 'en'):
            for surface in ('compact', 'expanded'):
                row = rendered[item_id]['locales'][locale][surface]
                assert row['state'] != 'failed'
                assert not any(s in row['text'] for s in ('for eating', 'rain contribution', 'alarm time and on/off state', 'obtain Amplifier', 'Battery may also', 'making Mattress', 'Strawberries Seeds'))
                if traits.get('digital_alarm') is False:
                    assert ('알람' if locale == 'ko' else 'alarm') not in row['text']
        if 'toggle_radio_microphone' in functions and traits.get('speech_transmission'):
            assert 'transmit speech' in rendered[item_id]['locales']['en']['expanded']['text']
    assert len(bait_ids) == 350
    assert len(bait_ids & accepted.keys()) == 24
    # Processing expression is invariant under unrelated identity/display changes.
    original = rows['Base.BaseballBat']
    renamed = deepcopy(original)
    renamed['item_id'] = 'Example.UnseenProcessingTarget'
    renamed['source_traits']['display_names'] = {'ko': '새 물품', 'en': 'New item'}
    first, second = descriptions.compose_item(original), descriptions.compose_item(renamed)
    for locale in ('ko', 'en'):
        for surface in ('compact', 'expanded'):
            assert first['locales'][locale][surface]['text'] == second['locales'][locale][surface]['text']


def test_recovery_identity_and_camping_purposes_across_corpus():
    from iris_tooling.domains.layer3 import description_composition_planner as planner
    blocks = json.loads((ROOT / 'Iris/build/description/composition/blocks.json').read_bytes())
    rows = {i['item_id']: i for i in blocks['items']}
    rendered = {i['item_id']: i for i in json.loads((ROOT / 'Iris/build/description/composition/descriptions.json').read_bytes())['items']}
    materials = {'Base.RippedSheets': ('천 조각', 'cloth scraps'),
                 'Base.DenimStrips': ('데님 조각', 'denim strips'),
                 'Base.LeatherStrips': ('가죽 조각', 'leather strips')}
    for item_id, item in rows.items():
        plan = planner.plan(item)
        acts = {f['payload'].get('activity') for u in plan['units'] for f in u['facts']}
        result = item.get('source_traits', {}).get('fabric_result')
        for locale, index in [('ko', 0), ('en', 1)]:
            compact = rendered[item_id]['locales'][locale]['compact']['text']
            expanded = rendered[item_id]['locales'][locale]['expanded']['text']
            assert ('직물 재료' if locale == 'ko' else 'textile material') not in compact
            assert ('야영 장비' if locale == 'ko' else 'camping equipment') not in expanded
            if result and 'fabric_recovery' in acts:
                assert materials[result['item_id']][index] in compact, item_id
            for activity, words in [('campfire_kit_preparation', ('모닥불 도구', 'campfire kits')),
                                    ('mattress_preparation', ('매트리스', 'mattress')),
                                    ('tent_kit_making', ('텐트', 'tents'))]:
                if activity in acts: assert words[index] in expanded, item_id
    # Change only the resolved result while retaining the original FabricType.
    # The output must follow that relation, not a garment ID or material tag.
    altered = deepcopy(rows['Base.Gloves_LeatherGloves'])
    altered['item_id'] = 'Example.UnseenGarment'
    altered['source_traits']['fabric_result'] = deepcopy(rows['Base.Shirt_Denim']['source_traits']['fabric_result'])
    text = descriptions.compose_item(altered)['locales']['en']['compact']['text']
    assert 'denim strips' in text and 'leather strips' not in text


def test_unrelated_material_and_tool_purposes_are_not_absorbed():
    # Exercise the summary boundary with distinct purposes sharing the same role.
    payloads = [{'activity': 'fabric_recovery'}, {'role': 'material'},
                {'role': 'material'}, {'role': 'tool'},
                {'function': 'groom_hair'}, {'function': 'groom_beard'}]
    segments = [{'text': 'Independent purpose ' + str(n), 'fact_refs': [str(n)]}
                for n in range(len(payloads))]
    plan = {'units': [{'facts': [{'fact_ref': str(n), 'payload': p}]} for n, p in enumerate(payloads)]}
    assert descriptions._compact_purposes(deepcopy(segments), plan, 'en') == segments


def test_package_result_identity_survives_generic_or_partial_labels():
    def result(name): return [{'names': {'en': name}}]
    assert en.package_identifies_results('Sack of Cherries', result('Cherry'))
    assert en.package_identifies_results('Tomato Seeds Packet', result('Tomato Seeds'))
    assert not en.package_identifies_results('Canned Bolognese', result('Spaghetti Bolognese'))
    assert not en.package_identifies_results('Unmarked Packet', result('Tomato Seeds'))
    rows = {i['item_id']: i for i in json.loads((ROOT / 'Iris/build/description/composition/blocks.json').read_bytes())['items']}
    for item_id, word in [('Base.CannedBolognese', 'spaghetti bolognese'),
                          ('Base.SackProduce_Apple', 'apples'), ('farming.TomatoBagSeed', 'tomato seeds')]:
        altered = deepcopy(rows[item_id])
        altered['item_id'] = 'Example.UnmarkedPackage'
        altered['source_traits']['display_names']['en'] = 'Unmarked Package'
        for surface in ('compact', 'expanded'):
            text = descriptions.compose_item(altered)['locales']['en'][surface]['text']
            assert word in text, (item_id, text)


def test_tool_material_results_distinguish_stone_tools_and_saw():
    rows = {i['item_id']: i for i in json.loads((ROOT / 'Iris/build/description/composition/blocks.json').read_bytes())['items']}
    for item_id in ('Base.RippedSheets', 'Base.RippedSheetsDirty', 'Base.DenimStrips',
                    'Base.DenimStripsDirty', 'Base.TreeBranch', 'Base.Twine', 'Base.SharpedStone'):
        result = descriptions.compose_item(rows[item_id])
        assert '돌 도구' in result['locales']['ko']['expanded']['text']
        assert 'stone tools' in result['locales']['en']['expanded']['text']
    plank = deepcopy(rows['Base.Plank'])
    plank['item_id'] = 'Example.UnseenHandleMaterial'
    result = descriptions.compose_item(plank)
    assert '톱' in result['locales']['ko']['expanded']['text']
    assert 'a saw' in result['locales']['en']['expanded']['text']
    assert '돌 망치' in descriptions.compose_item(rows['Base.Stone'])['locales']['ko']['expanded']['text']


def test_tool_domains_preserve_unrelated_roles_purposes_and_conditions():
    from iris_tooling.domains.layer3 import composition_rules, description_composition_planner as planner
    from iris_tooling.domains.layer3 import description_composition_uses as uses
    def planned(extra_role='tool'):
        facts = []
        for n, (activity, role) in enumerate([('food_portioning', 'tool'), ('woodworking', 'tool'),
                                             ('electronic_assembly', 'tool'), ('batter_preparation', extra_role)]):
            context = 'fact:context-' + str(n)
            facts += [{'fact_id': context, 'item_id': 'Example.New', 'fact_kind': 'use_context',
                       'payload': {'activity': activity}, 'provenance_refs': ['prov:test']},
                      {'fact_id': 'fact:role-' + str(n), 'item_id': 'Example.New', 'fact_kind': 'context_role',
                       'payload': {'role': role}, 'context_fact_ref': context, 'provenance_refs': ['prov:test']}]
        blocks, qualifiers, unresolved = composition_rules.semantic_blocks('Example.New', facts)
        plan = uses.prepare(planner.plan({'item_id': 'Example.New', 'blocks': blocks,
                            'qualifiers': qualifiers, 'unresolved_relations': unresolved}))
        for unit in plan['units']:
            if 'batter_preparation' in uses.purpose_tokens(unit):
                if unit.get('context'): unit['context']['activity'] = 'unrecognized_mod_activity'
                for fact in unit['facts']:
                    if fact['payload'].get('activity') == 'batter_preparation': fact['payload']['activity'] = 'unrecognized_mod_activity'
        return plan
    for role in ('tool', 'attachment', 'material'):
        plan = planned(role)
        segments, used = uses.frames(plan, 'en', descriptions._links, True)
        text = ' '.join(s['text'] for s in segments)
        assert all(word in text for word in ('food', 'wood', 'electronic')), text
        assert not {'fact:context-3', 'fact:role-3'} & used
        renamed = deepcopy(plan)
        renamed['item_id'] = 'Another.UnrelatedName'
        assert uses.frames(renamed, 'en', descriptions._links, True) == (segments, used)
    plan = planned()
    target = next(u for u in plan['units'] if 'woodworking' in uses.purpose_tokens(u))
    target['qualifier_refs'] = ['qualifier:new-condition']
    plan['qualifiers']['qualifier:new-condition'] = {'payload': {'predicate': 'Only during a new mod-specific event.'}}
    _, used = uses.frames(plan, 'en', descriptions._links, True)
    assert not set(target['fact_refs']) & used


def test_latest_purposes_and_specific_relation_scopes():
    rows = {i['item_id']: i for i in json.loads((ROOT / 'Iris/build/description/composition/blocks.json').read_bytes())['items']}
    rendered = {key: descriptions.compose_item(row) for key, row in rows.items()}
    for item_id, term in [('Base.ComfreyCataplasm', 'fracture'), ('Base.PlantainCataplasm', 'deep wounds'),
                          ('Base.WildGarlicCataplasm', 'wound infection'), ('Base.FishingRodBreak', 'repaired'),
                          ('Base.Rope', 'between floors'), ('Base.SheetRope', 'between floors')]:
        for surface in ('compact', 'expanded'):
            assert term in rendered[item_id]['locales']['en'][surface]['text']
    scopes = json.loads((ROOT / 'docs/iris_dvf_latest_full_evaluation_2026-09-14_scopes.json').read_bytes())['scopes']
    for key in scopes['clock_time_purpose_missing']:
        for surface in ('compact', 'expanded'):
            assert 'check the time' in rendered[key]['locales']['en'][surface]['text']
    for key in ('Base.AlarmClock2', 'Base.DigitalWatch2'):
        assert 'worn' not in rendered[key]['locales']['en']['expanded']['text']
    for key in scopes['drink_purpose_as_food']:
        for surface in ('compact', 'expanded'):
            assert 'prepare food' not in rendered[key]['locales']['en'][surface]['text']
    for key in ('Base.GlassTumbler', 'Base.PlasticCup'):
        assert 'as a glass' not in rendered[key]['locales']['en']['expanded']['text']
    for key in scopes['english_bottle_result_article']:
        assert 'a smashed bottle' in rendered[key]['locales']['en']['expanded']['text']
    for key, purpose in [('Base.Garbagebag', 'rain collectors'), ('Base.Doorknob', 'doors'),
                         ('Base.Drawer', 'tables with drawers'), ('Base.MeatCleaver', 'hunting')]:
        surface = 'compact' if key == 'Base.MeatCleaver' else 'expanded'
        assert purpose in rendered[key]['locales']['en'][surface]['text']
    for key in ('Base.Bowl', 'Base.Pan', 'Base.WaterPot'):
        text = rendered[key]['locales']['en']['expanded']['text']
        assert 'hold ingredients for cooking' not in text
    altered = deepcopy(rows['Base.FishingRodBreak'])
    altered['item_id'] = 'Example.NewRestorationTarget'
    assert 'repaired' in descriptions.compose_item(altered)['locales']['en']['compact']['text']
    altered['use_relations'] = []
    assert 'repaired' not in descriptions.compose_item(altered)['locales']['en']['compact']['text']


def test_furniture_result_does_not_require_unrelated_construction_targets():
    from iris_tooling.domains.layer3 import description_composition_planner as planner, description_composition_uses as uses
    rows = {i['item_id']: i for i in json.loads((ROOT / 'Iris/build/description/composition/blocks.json').read_bytes())['items']}
    plan = uses.prepare(planner.plan(rows['Base.Doorknob']))
    plan['item_id'] = 'Example.FurnitureMaterial'
    plan['units'] = [u for u in plan['units'] if 'furniture_crafting' in uses.purpose_tokens(u)]
    plan['source_traits'] = {}
    for locale, word in [('ko', '서랍'), ('en', 'drawer')]:
        baseline, _ = uses.frames(plan, locale, descriptions._links, False)
        assert word in ' '.join(s['text'] for s in baseline)
        unrelated = deepcopy(plan)
        unrelated['source_traits']['construction_targets'] = [{'names': None, 'callback': 'Unknown'}]
        assert uses.frames(unrelated, locale, descriptions._links, False)[0] == baseline
    parent = uses.prepare(planner.plan(rows['Base.Nails']))
    wood = deepcopy(next(u for u in parent['units'] if uses.purpose_tokens(u) - {None} == {'woodworking'}))
    plan['qualifiers'].update(parent['qualifiers'])
    plan['units'].append(wood)
    merged, _ = uses.frames(plan, 'en', descriptions._links, False)
    assert 'woodworking' in ' '.join(s['text'] for s in merged)
    assert 'drawer' not in ' '.join(s['text'] for s in merged)
    # A tool's woodworking purpose does not cover a furniture material's role.
    for fact in wood['facts']:
        if fact['payload'].get('role') == 'material': fact['payload']['role'] = 'tool'
    distinct, _ = uses.frames(plan, 'en', descriptions._links, False)
    assert 'drawer' in ' '.join(s['text'] for s in distinct)


def test_september15_relations_and_user_drinking_boundary():
    from iris_tooling.domains.layer3 import purpose_participant_relations as review
    from iris_tooling.domains.layer3 import description_composition_planner as planner, description_composition_uses as uses
    rows = {i['item_id']: i for i in json.loads((ROOT / 'Iris/build/description/composition/blocks.json').read_bytes())['items']}
    relations = review.participant_relations(ROOT)
    assert set(relations['moving']) == {'Base.Hammer', 'Base.Screwdriver', 'Base.Shovel', 'Base.Wrench', 'Base.PipeWrench'}
    for item_id in relations['moving']:
        item = deepcopy(rows[item_id]); item['item_id'] = 'Example.UnseenTool'
        output = descriptions.compose_item(item)
        assert 'move or install' in output['locales']['en']['expanded']['text']
        item['source_traits'].pop('moving_tool_targets')
        assert 'move or install' not in descriptions.compose_item(item)['locales']['en']['expanded']['text']
    fields = {'Type': 'Food', 'PoisonPower': '120', 'UseForPoison': '38', 'PoisonDetectionLevel': '7'}
    assert review.admits_recipe_poison(fields)
    for change in ({'Type': 'Normal'}, {'PoisonPower': '0'}, {'UseForPoison': '0'},
                   {'PoisonDetectionLevel': ''}, {'Tags': 'NoDetect'}, {'HerbalistType': 'Berry'}):
        assert not review.admits_recipe_poison({**fields, **change})
    for item_id, role in relations['cleaning'].items():
        text = descriptions.compose_item(rows[item_id])['locales']['en']['expanded']['text']
        assert ('with a towel or cleaning tool' if role == 'cleaning_supply' else 'with bleach') in text
    bleach = descriptions.compose_item(rows['Base.Bleach'])
    for locale, sentence in [('ko', '마실 수 있다.'), ('en', 'It can be drunk.')]:
        for surface in ('compact', 'expanded'):
            row = bleach['locales'][locale][surface]
            assert any(segment['text'] == sentence for segment in row['segments'])
            assert all(term not in row['text'] for term in ('중독', '독성', 'poisoning', 'toxic', 'fatal'))
    for n, word in [(1, 'standard and family'), (2, 'vans and pickup'), (3, 'performance')]:
        row = descriptions.compose_item(rows['Base.MechanicMag' + str(n)])['locales']['en']['expanded']
        assert word in row['text'] and 'It can be read.' not in row['text']
    for item_id in ('Base.FlintKnife', 'Base.HuntingKnife', 'Base.KitchenKnife', 'Base.Machete', 'Base.MeatCleaver'):
        text = descriptions.compose_item(rows[item_id])['locales']['en']['expanded']['text']
        assert all(word in text for word in ('animals', 'fish fillets', 'portioning', 'tree branch', 'stake'))
    plan = uses.prepare(planner.plan(rows['Base.HuntingKnife']))
    plan['units'] = [u for u in plan['units'] if not uses.purpose_tokens(u) & {'fish_preparation'}]
    segments, _ = uses.frames(plan, 'en', descriptions._links, False)
    assert 'fish fillets' not in ' '.join(s['text'] for s in segments)
    assert 'animals' in ' '.join(s['text'] for s in segments)
    assert 'cover and dress wounds' in descriptions.compose_item(rows['Base.Bandaid'])['locales']['en']['compact']['text']
