"""Bind moveable, cleaning and learning participants and conditional recipe poison use."""
import hashlib
import json
import re
from . import source_reader as reader

PATH = 'Iris/build/description/source_support/b41_dvf_relations_2026-09-15.json'
SHA256 = 'aee91a325cc1928897a1d135970e1c9cde15582a8e3d95b6601836daeef856e9'
FUNCTIONS = {'supply_recipe_poison': ('food preparation',
    '설정에서 허용되는 경우 음식에 독을 섞는 재료로 쓸 수 있다',
    'Where settings allow it, it can be used to add poison to food')}


def load(root):
    raw = (root / PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError('Participant relation evidence changed')
    data = json.loads(raw)
    for row in data['consumer_bindings']:
        if hashlib.sha256((root / row['path']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('reviewed relation consumer changed: ' + row['path'])
    return data


def admits_recipe_poison(fields):
    # Non-herbal declared poisons have an unconditional known-poison branch;
    # runtime herbal randomization needs its own knowledge/state relationship.
    return (fields.get('Type') == 'Food' and 'NoDetect' not in fields.get('Tags', '').split(';')
            and not fields.get('HerbalistType')
            and re.fullmatch(r'\d+', fields.get('PoisonDetectionLevel', '')) is not None
            and all(re.fullmatch(r'\d+', fields.get(k, '')) and int(fields[k]) > 0
                    for k in ('PoisonPower', 'UseForPoison')))


def supplement(root, semantic, by_item, builder, source_hashes):
    data = load(root)
    source_hashes[PATH] = SHA256
    source_hashes.update({b['path']: b['sha256'] for b in data['consumer_bindings']})
    for item, records in sorted(by_item.items()):
        unique = {(o['source_path'], o['source_sha256'], o['content']['raw'].replace('\r\n', '\n')): (ref, o) for ref, o in records}
        if len(unique) != 1 or any(o['content'].get('property_conflicts') for _, o in records): continue
        ref, observation = next(iter(unique.values()))
        fields = reader.unique_properties(observation['content'])
        if not fields or fields.get('OBSOLETE', '').lower() == 'true' or not admits_recipe_poison(fields): continue
        proof = builder.observe(PATH, 'consumer:poisoning', {'reading': data['readings']['poisoning'],
                    'consumer_bindings': data['consumer_bindings'], 'native_bindings': data['native_bindings']})
        builder.observations[ref] = observation
        source_hashes[observation['source_path']] = observation['source_sha256']
        builder.fact(item, 'direct_function', {'function': 'supply_recipe_poison'}, [ref, proof],
                     'reviewed_recipe_poison', ['item:direct'])
    return {'reviewed_recipe_poison': {'revision': '1', 'review_state': 'reviewed',
        'preconditions': 'Unique nonobsolete Food, positive declared poison power/use, nonnull recipe poison field, no NoDetect or unresolved herbal knowledge.',
        'transformation': 'Conditional poison ingredient use through bound evolved recipe candidates, menu filtering and native result mutation.',
        'exceptions': 'No ingestion warning; no universal food acceptance, no herbal state inference, no victim outcome.'}}


def participant_relations(root):
    data = load(root)
    path = 'Iris/build/description/source_support/b41_placed_object_properties.json'
    raw = (root / path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != '9bad7eb46d3cea3dcef9e4368e73d33643e34105ce157f75982ec0d1b63cd74b':
        raise ValueError('placed property evidence changed')
    placed = json.loads(raw)
    registry = reader.mask((root / 'lua/client/Moveables/ISMoveableDefinitions.lua').read_text(encoding='utf-8-sig'), lua=True)
    definitions = {name: re.findall(r'"([^"]+)"', items) for name, items in
                   re.findall(r'addToolDefinition\(\s*"([^"]+)"\s*,\s*\{([^}]+)\}', registry)}
    moving = {}
    for sprite, entry in placed['sprites'].items():
        fields = entry['properties']
        if 'IsMoveAble' not in fields: continue
        for mode, attribute in (('pickup', 'PickUpTool'), ('place', 'PlaceTool')):
            for item in definitions.get(fields.get(attribute), []):
                if not re.fullmatch(r'Base\.\w+', item): continue
                moving.setdefault(item, []).append({'sprite': sprite, 'mode': mode, 'tool_definition': fields[attribute],
                    'properties': fields, 'property_source': path, 'source': entry['source']})
    cleaning_text = reader.mask((root / 'lua/client/TimedActions/ISCleanBlood.lua').read_text(encoding='utf-8-sig'), lua=True)
    validity = cleaning_text.split('function ISCleanBlood:isValid()', 1)[1].split('\nend', 1)[0]
    consumed = re.search(r'local bleach = .*?getItemFromType\("(\w+)"\)', cleaning_text)[1]
    participants = set(re.findall(r'contains\("(\w+)"\)', validity))
    cleaning = {'Base.' + name: 'cleaning_supply' if name == consumed else 'tool' for name in participants}
    return {'moving': moving, 'cleaning': cleaning, 'mechanics': data['mechanic_targets'],
            'evidence': {'path': PATH, 'sha256': SHA256, 'consumer_bindings': data['consumer_bindings']}}
