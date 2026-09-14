"""Synthetic item capabilities must not depend on a vanilla signature."""
from copy import deepcopy

from iris_tooling.domains.layer3 import description_composition_results as results


def fixture(functions):
    units, segments = [], []
    for n, function in enumerate(functions):
        ref = f'fact:mod-{n}'
        links = {key: [] for key in ('block_refs', 'branch_refs', 'qualifier_refs', 'relation_refs')}
        links['fact_refs'] = [ref]
        units.append({**links, 'facts': [{'fact_ref': ref, 'payload': {'function': function}}]})
        segments.append({**links, 'text': function + '.', 'expression': 'public_use'})
    return segments, {'item_id': 'ExampleMod.UnseenContainer', 'units': units, 'qualifiers': {}}


def test_liquid_capability_subsets_and_unknowns():
    # This water-only combination never requires a fuel capability or item ID.
    segments, plan = fixture(['store_water', 'carry_water'])
    first = results._compact_liquid_containers(segments, plan, 'en')
    assert first[0]['text'] == 'It can store and carry water.'
    renamed = deepcopy(plan)
    renamed['item_id'] = 'AnotherMod.DifferentName'
    assert results._compact_liquid_containers(segments, renamed, 'en') == first

    # Adding fuel transfer must not grant storage/carrying to that liquid.
    segments, plan = fixture(['store_water', 'carry_water', 'transfer_vehicle_fuel', 'mod_unknown_operation'])
    combined = results._compact_liquid_containers(segments, plan, 'en')
    assert combined[0]['text'] == 'It can store and carry water. It can receive and supply fuel.'
    assert combined[-1] == segments[-1]
    assert {r for s in combined for r in s['fact_refs']} == {r for s in segments for r in s['fact_refs']}

    # An unhandled public condition prevents that segment from being abstracted.
    segments[0]['qualifier_refs'] = ['qualifier:unknown']
    combined = results._compact_liquid_containers(segments, plan, 'en')
    assert combined[0] == segments[0]

    segments, plan = fixture(['receive_poured_water', 'store_water', 'carry_water', 'transfer_vehicle_fuel'])
    text = results._compact_liquid_containers(segments, plan, 'ko')[0]['text']
    assert text == '물을 담아 보관하거나 운반할 수 있다. 연료를 담아 공급할 수 있다.'


def test_material_roles_without_vanilla_item_combinations():
    from iris_tooling.domains.layer3 import composition_rules

    def compose(item_id, activities):
        facts = []
        for n, activity in enumerate(activities):
            context = f'fact:context-{n}'
            facts += [
                {'fact_id': context, 'item_id': item_id, 'fact_kind': 'use_context',
                 'payload': {'activity': activity}, 'provenance_refs': [f'prov:{n}']},
                {'fact_id': f'fact:role-{n}', 'item_id': item_id, 'fact_kind': 'context_role',
                 'payload': {'role': 'material'}, 'context_fact_ref': context, 'provenance_refs': [f'prov:{n}']},
            ]
        blocks, qualifiers, unresolved = composition_rules.semantic_blocks(item_id, facts)
        return results.compose_item({'item_id': item_id, 'blocks': blocks, 'qualifiers': qualifiers,
                                     'unresolved_relations': unresolved})

    # No charcoal/log binding or nail/repair/rope signature is present.
    for activities in (['construction', 'campfire_kit_preparation'],
                       ['construction', 'fishing_gear_crafting'],
                       ['radio_crafting', 'campfire_kit_preparation'],
                       ['radio_crafting', 'campfire_kit_preparation', 'trap_crafting'],
                       ['tool_crafting', 'campfire_kit_preparation', 'trap_crafting']):
        a = compose('ModA.NewMaterial', activities)
        b = compose('ModB.RenamedMaterial', activities)
        for locale in ('ko', 'en'):
            row = a['locales'][locale]['compact']
            assert row['state'] == 'present'
            assert row['text'] == b['locales'][locale]['compact']['text']
            detail = a['locales'][locale]['expanded']
            assert len({r for s in detail['segments'] for r in s['fact_refs']}) == 2 * len(activities)
            if 'construction' in activities:
                assert ('건축' if locale == 'ko' else 'construction') in row['text']
                assert len({r for s in row['segments'] for r in s['fact_refs']}) == 2
            if len(activities) == 3:
                assert ('야외 활동 장비' if locale == 'ko' else 'outdoor equipment') in row['text']
                assert all(word in detail['text'] for word in (('야영', '사냥') if locale == 'ko' else ('camping', 'hunting')))
                if 'tool_crafting' in activities:
                    assert row['text'].index('도구' if locale == 'ko' else 'tools') < row['text'].index('야외' if locale == 'ko' else 'outdoor')

    # Construction does not swallow an independent technical-device domain.
    mixed = compose('ModC.MixedDomains', ['construction', 'radio_crafting'])
    for locale in ('ko', 'en'):
        text = mixed['locales'][locale]['compact']['text']
        assert all(word in text for word in (('건축', '전자') if locale == 'ko' else ('construction', 'electronic')))


def test_native_purpose_requires_admitted_action_and_positive_property():
    from pathlib import Path
    from iris_tooling.domains.layer3 import recovery_sources

    class Builder:
        def __init__(self):
            self.observations = {}
            self.facts = []

        def observe(self, *args):
            return 'proof:native'

        def fact(self, item, kind, payload, *args):
            self.facts.append((item, payload['function']))

    semantic = {'facts': []}
    declarations = {}
    for item, noise, action in [('ModA.Sound', '8', 'place_trigger_device'),
                                 ('ModB.Renamed', '8', 'place_trigger_device'),
                                 ('ModA.Silent', '0', 'place_trigger_device'),
                                 ('ModA.Unjoined', '8', None),
                                 ('ModA.Unknown', 'unknown', 'place_trigger_device'),
                                 ('ModA.Power', '0', 'control_installed_generator')]:
        semantic['facts'].append({'item_id': item, 'payload': {'function': action}})
        declarations[item] = [('declaration:' + item, {'source_path': 'fixture', 'source_sha256': 'fixture',
            'locator': 'item:' + item, 'content': {'raw': 'item ' + item,
            'clauses': ['Type = Weapon', 'NoiseRange = ' + noise]}})]
    builder = Builder()
    root = Path(__file__).resolve().parents[5]
    recovery_sources.supplement_native_device_purposes(root, semantic, declarations, builder, {})
    assert set(builder.facts) == {('ModA.Sound', 'emit_attracting_noise'),
                                 ('ModB.Renamed', 'emit_attracting_noise'),
                                 ('ModA.Power', 'supply_nearby_electricity')}
