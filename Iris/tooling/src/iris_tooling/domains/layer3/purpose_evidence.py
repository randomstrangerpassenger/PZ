"""Bound local consumer relationships used to decide public purposes.

Insertion is not animal acceptance; a control is not its purpose. Preserve the
original facts and attach the reviewed relation before selecting public prose.
"""
import hashlib
import json
import re

PATH = 'Iris/build/description/source_support/b41_dvf_purpose_review.json'
SHA256 = '1b4fd1b1b6b1a5872343a5ad9a0828bb104e8489f2b2564e578a0708448bc9fc'


def load(root):
    raw = (root / PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError('DVF purpose review snapshot changed')
    evidence = json.loads(raw)
    for binding in evidence['consumer_bindings']:
        if hashlib.sha256((root / binding['path']).read_bytes()).hexdigest() != binding['sha256']:
            raise ValueError('reviewed purpose consumer changed: ' + binding['path'])
    text = (root / 'lua/server/Traps/TrapDefinition.lua').read_text(encoding='utf-8-sig')
    registered = set(re.findall(r'table.insert\(Animals,\s*(\w+)\)', text))
    baits = {}
    for animal, item, value in re.findall(r'(\w+)\.baits\["([\w.]+)"\]\s*=\s*(\d+)', text):
        if animal in registered and int(value) > 0:
            baits.setdefault(item, []).append(animal)
    return baits


def for_item(item_id, traits, accepted):
    result = {'source_path': PATH, 'source_sha256': SHA256,
              'accepted_animals': sorted(set(accepted.get(item_id, [])))}
    if traits.get('Type') == 'AlarmClockClothing':
        # Exact native constructor predicate; Tags are not substituted for it.
        result['digital_alarm'] = 'Classic' not in item_id
    if traits.get('Type') == 'Radio' and traits.get('TwoWay', '').lower() == 'true':
        result['speech_transmission'] = True
    return result


LATEST_PATH = 'Iris/build/description/source_support/b41_dvf_latest_purposes.json'
LATEST_SHA256 = '680027b6c530753ebe7f6836eaa42c0d857335c530b53eb30a6fe18cad993a3b'
REVIEW_FUNCTIONS = {
    'check_carried_time': ('time display', '소지해 시간을 확인할 수 있다', 'It can be carried to check the time'),
    'poultice_fracture_recovery': ('poultice treatment', '골절 부위에 발라 회복을 도울 수 있다', 'It can be applied to help a fracture heal'),
    'poultice_wound_recovery': ('poultice treatment', '긁힘, 베임이나 깊은 상처에 발라 회복을 도울 수 있다', 'It can be applied to help scratches, cuts, and deep wounds heal'),
    'poultice_wound_infection': ('poultice treatment', '상처에 발라 상처 감염을 줄이는 데 쓸 수 있다', 'It can be applied to reduce wound infection'),
    'descend_installed_escape_rope': ('escape rope traversal', '설치한 로프를 타고 내려갈 수 있다', 'An installed rope can be used to climb down'),
}


def supplement_latest(root, semantic, by_item, builder, source_hashes):
    from . import source_reader as reader
    raw = (root / LATEST_PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest() != LATEST_SHA256:
        raise ValueError('latest reviewed purpose snapshot changed')
    data = json.loads(raw)
    source_hashes[LATEST_PATH] = LATEST_SHA256
    for binding in data['consumer_bindings']:
        if hashlib.sha256((root / binding['path']).read_bytes()).hexdigest() != binding['sha256']:
            raise ValueError('latest purpose consumer changed: ' + binding['path'])
        source_hashes[binding['path']] = binding['sha256']
    health = (root / 'lua/client/XpSystem/ISUI/ISHealthPanel.lua').read_text(encoding='utf-8-sig')
    dispatch = dict(re.findall(r'HApplyPoultice.new\(self, panel, bodyPart, "(\w+)", "[^"\n]+", IS(\w+)Cataplasm\)', health))
    therapy = {'Comfrey': 'poultice_fracture_recovery', 'Plantain': 'poultice_wound_recovery', 'Garlic': 'poultice_wound_infection'}
    admitted = {}
    for fact in semantic.get('facts', []):
        admitted.setdefault(fact['item_id'], set()).add(fact['payload'].get('function'))
    for item, records in sorted(by_item.items()):
        unique = {(o['source_path'], o['source_sha256'], o['content']['raw'].replace('\r\n', '\n')): (ref, o) for ref, o in records}
        if len(unique) != 1 or any(o['content'].get('property_conflicts') for _, o in records): continue
        ref, observation = next(iter(unique.values()))
        fields = reader.unique_properties(observation['content'])
        if not fields or fields.get('OBSOLETE', '').lower() == 'true': continue
        selected = []
        if fields.get('Type') in {'AlarmClock', 'AlarmClockClothing'}:
            selected.append(('clock', 'check_carried_time'))
        factor = dispatch.get(item.split('.', 1)[-1])
        if factor in therapy and 'apply_poultice' in admitted.get(item, set()):
            action = (root / ('lua/client/TimedActions/IS' + factor + 'Cataplasm.lua')).read_text(encoding='utf-8-sig')
            if ':set' + factor + 'Factor(cataplasmPower)' not in action: raise ValueError('poultice setter changed')
            selected.append((factor, therapy[factor]))
        if {'supply_escape_rope', 'start_escape_rope_ascent'} <= admitted.get(item, set()):
            selected.append(('rope', 'descend_installed_escape_rope'))
        for purpose, function in selected:
            proof = builder.observe(LATEST_PATH, 'native:' + purpose, {'reading': data['readings'][purpose],
                'native_bindings': data['native_bindings'], 'consumer_bindings': data['consumer_bindings'],
                **({'action_transition': data['action_transition']} if purpose == 'rope' else {})})
            builder.observations[ref] = observation
            source_hashes[observation['source_path']] = observation['source_sha256']
            builder.fact(item, 'direct_function', {'function': function}, [ref, proof], 'reviewed_time_treatment_traversal', ['item:direct'])
    return {'reviewed_time_treatment_traversal': {'revision': '1', 'review_state': 'reviewed',
        'preconditions': 'Unique declaration; clock native type or admitted treatment/rope action joined to bound dispatch and consumer.',
        'transformation': 'Independent time display, factor-specific poultice treatment and installed rope descent.',
        'exceptions': 'No ingredient inherits treatment, no universal cure or zombification treatment, no recursive bag search, no guarantee of safe rope traversal.'}}
