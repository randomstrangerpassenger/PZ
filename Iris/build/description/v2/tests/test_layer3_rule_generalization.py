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


def test_device_effects_require_consumed_properties_and_reachable_consumer():
    from pathlib import Path
    from iris_tooling.domains.layer3 import recovery_sources

    class Builder:
        def __init__(self):
            self.observations, self.facts = {}, []
        def observe(self, *args):
            return 'proof:native'
        def fact(self, item, kind, payload, *args):
            self.facts.append((item, payload['function']))

    def admit(name, fields, action):
        item = 'ExampleMod.' + name
        fields = {'Type': 'Weapon', **fields}
        semantic = {'facts': [{'item_id': item, 'payload': {'function': action}}]}
        obs = {'source_path': 'fixture', 'source_sha256': 'fixture', 'locator': 'item:' + item,
               'content': {'raw': 'item ' + item, 'clauses': [k + ' = ' + v for k, v in fields.items()]}}
        builder = Builder()
        recovery_sources.supplement_native_device_purposes(Path(__file__).resolve().parents[5],
                                                          semantic, {item: [('fixture', obs)]}, builder, {})
        return {fn for _, fn in builder.facts}

    blast = {'ExplosionPower': '70', 'ExplosionRange': '6'}
    assert admit('New', blast, 'place_trigger_device') == {'device_explosion_damage'}
    assert admit('Renamed', blast, 'place_trigger_device') == admit('New', blast, 'place_trigger_device')
    assert not admit('NoRange', {'ExplosionPower': '70'}, 'place_trigger_device')
    assert not admit('ZeroRange', {**blast, 'ExplosionRange': '0'}, 'place_trigger_device')
    assert not admit('UnknownPower', {**blast, 'ExplosionPower': 'unknown'}, 'place_trigger_device')
    assert not admit('Unjoined', blast, None)
    assert admit('Smoke', {'SmokeRange': '5'}, 'place_trigger_device') == {'device_smoke_distraction'}
    assert admit('Fire', {'FireRange': '4', 'FirePower': '90'}, 'place_trigger_device') == {'device_start_fire'}
    thrown = {**blast, 'PhysicsObject': 'UnseenTexture'}
    assert admit('Throw', thrown, 'request_physics_attack') == {'device_explosion_damage'}
    for extra in ({'PhysicsObject': 'Ball'}, {'SensorRange': '3'}, {'ExplosionTimer': '5'},
                  {'ExplosionTimer': 'unknown'}, {'CanBeRemote': 'true'}):
        assert not admit('NotInstant', {**thrown, **extra}, 'request_physics_attack')


def test_relation_rendering_does_not_use_item_identity():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[5]
    blocks = json.loads((root/'Iris/build/description/composition/blocks.json').read_text())
    items = {i['item_id']: i for i in blocks['items']}
    for key in ('Base.PlasterPowder', 'Base.BucketEmpty', 'Base.Jack', 'Base.LugWrench',
                'Base.Screwdriver', 'Base.Wrench', 'Base.SmokeBombSensorV1'):
        a = results.compose_item(items[key])
        renamed = deepcopy(items[key])
        renamed['item_id'] = 'ExampleMod.UnrelatedName'
        b = results.compose_item(renamed)
        for locale in ('ko', 'en'):
            for surface in ('compact', 'expanded'):
                assert a['locales'][locale][surface]['text'] == b['locales'][locale][surface]['text']
    for key in ('Base.SmokeBomb', 'Base.NoiseTrap'):
        assert '설치하거나 던져서' in results.compose_item(items[key])['locales']['ko']['expanded']['text']
    for key, method in (('Base.SmokeBombSensorV1','움직임을 감지'), ('Base.SmokeBombTriggered','지연 작동')):
        text = results.compose_item(items[key])['locales']['ko']['expanded']['text']
        assert method in text and '던져서' not in text
    powder = deepcopy(items['Base.PlasterPowder'])
    powder['use_relations'] = []
    # The noun alone cannot license inheriting the result's painting purpose.
    assert '도색' not in results.compose_item(powder)['locales']['ko']['expanded']['text']


def test_vehicle_tool_role_comes_from_paired_operation_requirements():
    from iris_tooling.domains.layer3.recovery_relations import vehicle_tool_roles
    def tables(name, equip='', keep='true', operations=('install', 'uninstall')):
        return ''.join('table ' + op + ' { items { 1 { type = ' + name +
                       ', keep = ' + keep + (', equip = ' + equip if equip else '') + ', } } }'
                       for op in operations)
    assert vehicle_tool_roles(tables('Mod.Tool', 'primary'), 'Mod.Tool') == {'direct'}
    assert vehicle_tool_roles(tables('Other.Renamed', 'primary'), 'Other.Renamed') == {'direct'}
    assert vehicle_tool_roles(tables('Mod.Tool'), 'Mod.Tool') == {'support'}
    assert vehicle_tool_roles(tables('Mod.Tool', 'secondary'), 'Mod.Tool') == {'support'}
    assert not vehicle_tool_roles(tables('Mod.Tool', 'primary', operations=('install',)), 'Mod.Tool')
    assert not vehicle_tool_roles(tables('Mod.Tool', 'primary', keep='false'), 'Mod.Tool')
    assert not vehicle_tool_roles(tables('Mod.Tool', 'primary'), 'Mod.Unrelated')
