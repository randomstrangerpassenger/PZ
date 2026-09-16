"""Shared declaration and recipe indexes for source recovery."""
from collections import defaultdict
import re
from . import source_reader as reader
from . import semantic_results as semantic


def stable_properties(record):
    """A property conflict is local, not a reason to discard an entire item.

    Repeatable properties are retained in the original observation. A scalar
    is returned only if every declaration of that exact key has the same value;
    choosing first/last values is forbidden. Consumers still require their own
    relevant keys to be non-conflicting.
    """
    properties = reader.properties(record)
    conflicts = {key: values for key, values in properties.items() if len(set(values)) > 1}
    return {key: values[0] for key, values in properties.items() if key not in conflicts}, conflicts


def water_form(item, fields):
    """Require a single coherent target across legacy/current water mappings."""
    f = fields[item]
    if f.get('CanStoreWater', '').lower() != 'true':
        return None
    if f.get('IsWaterSource', '').lower() == 'true':
        candidates = {item}
    else:
        tokens = re.findall(r'(?:^|;)\s*WaterSource\s*-\s*([A-Za-z0-9_.]+)\s*(?=;|$)', f.get('ReplaceOnUseOn', ''))
        tokens += re.findall(r'(?:^|;)\s*WaterSource\s+([A-Za-z0-9_.]+)\s*(?=;|$)', f.get('ReplaceTypes', ''))
        candidates = {reader.qualify(item.split('.', 1)[0], t) for t in tokens}
    if len(candidates) != 1:
        return None
    target = next(iter(candidates))
    destination = fields.get(target, {})
    try:
        positive_uses = float(destination.get('UseDelta', '0')) > 0
    except ValueError:
        positive_uses = False
    if (destination.get('Type') == 'Drainable' and destination.get('IsWaterSource', '').lower() == 'true'
            and destination.get('CanStoreWater', '').lower() == 'true' and positive_uses):
        return target
    return None


def module_imports(text, path):
    """Read explicit plain import headers without changing the historical reader."""
    masked = reader.mask(text, strings=True)
    rows = []
    for match in re.finditer(r'\bmodule\s+(\w+)\s*\{\s*imports\s*\{([^{}]*)\}', masked):
        names = [name.strip() for name in match[2].split(',') if name.strip()]
        if names and all(re.fullmatch(r'\w+', name) for name in names):
            rows.append({'module': match[1], 'imports': names, 'path': path,
                         'line': text.count('\n', 0, match.start()) + 1,
                         'raw': text[match.start():match.end()]})
    return rows


def recipe_participants(record, fields, groups):
    """Retain historical parsing and recover identities in opaque numeric operands.

    This identifies source participation only. The numeric literal is deliberately
    not translated into the historical equals grammar or a consumption amount.
    Result clauses and unsupported expressions retain their opaque boundary.
    """
    rows, opaque = reader.recipe_participants(record, fields, groups)
    for ordinal, clause in enumerate(record['clauses']):
        if re.match(r'^\w+\s*:', clause):
            continue
        prefix = re.match(r'^(keep|destroy)\s+', clause)
        role = prefix[1] if prefix else 'input'
        expression = clause[prefix.end():] if prefix else clause
        for token in expression.split('/'):
            match = re.fullmatch(r'\s*(\[[\w.]+\]|[\w.]+)\s*([;=])\s*(\d+(?:\.\d+)?)\s*', token)
            if not match:
                continue
            if match[2] == '=' and re.fullmatch(r'(\[[\w.]+\]|[\w.]+)=\d+(?:\.\d+)?', token.strip()):
                continue  # Already admitted by the historical grammar.
            bare = {**record, 'clauses': [match[1]]}
            participants, unsupported = reader.recipe_participants(bare, fields, groups)
            if unsupported:
                continue
            rows.extend({**p, 'role': role, 'clause': clause, 'ordinal': ordinal,
                         'source_token': token, 'numeric_suffix': {'separator': match[2], 'literal': match[3],
                             'meaning': 'not interpreted; participation admission only'},
                         'recovery_reason': 'Historical participant grammar omitted this numeric operand spelling.'}
                        for p in participants)
    # An explicit import contributes a unique absent-local identity. Preserve
    # historical rows, even their unbound module-qualified spelling, as lineage.
    headers = record.get('module_imports', [])
    ambiguous = set(record.get('ambiguous_item_ids', []))
    if headers:
        modules = headers[0]['imports']
        for ordinal, clause in enumerate(record['clauses']):
            result = re.fullmatch(r'Result\s*:\s*(\w+)(?:\s*=\s*\d+(?:\.\d+)?)?', clause)
            if re.match(r'^\w+\s*:', clause) and not result:
                continue
            prefix = re.match(r'^(keep|destroy)\s+', clause)
            role = 'result' if result else prefix[1] if prefix else 'input'
            expression = result[1] if result else clause[prefix.end():] if prefix else clause
            for token in expression.split('/'):
                match = re.fullmatch(r'\s*(\w+)(?:\s*([;=])\s*(\d+(?:\.\d+)?))?\s*', token)
                if not match:
                    continue
                local = reader.qualify(record['module'], match[1])
                candidates = {reader.qualify(module, match[1]) for module in modules}
                if local in fields or local in ambiguous or candidates & ambiguous:
                    continue
                candidates &= fields.keys()
                if len(candidates) != 1:
                    continue
                target = next(iter(candidates))
                imported = {'item_id': target, 'role': role, 'clause': clause, 'ordinal': ordinal,
                            'group': None, 'source_token': token,
                            'import_resolution': {'local_spelling': local, 'resolved_item': target,
                                                  'headers': headers, 'explicit_imports': modules},
                            'recovery_reason': 'Historical participant qualification omitted explicit module imports.'}
                if match[2]:
                    imported['numeric_suffix'] = {'separator': match[2], 'literal': match[3],
                        'meaning': 'not interpreted; participation admission only'}
                rows.append(imported)
    # Historical opaque entries are preserved, including the now recognized
    # token: recognizing its identity has not resolved its numeric semantics.
    return rows, opaque


def recover_participation(base, builder, recipes, fields, groups, declaration):
    recovered = defaultdict(list)
    targets = set(base['semantic']['target_ids'])
    baseline_rows = set()
    for attempt in base['semantic']['attempts'].values():
        if attempt['route'] != 'B':
            continue
        for participant in attempt['finding'].get('participants', []):
            observation = base['semantic']['observations'][participant['observation_ref']]
            baseline_rows.add((participant['item_id'], observation['source_path'],
                tuple(observation['content'].get('clauses', [])), participant['role'], participant['ordinal'], participant.get('group')))
    for record in recipes:
        participants, _ = recipe_participants(record, fields, groups)
        additions = [p for p in participants if ('numeric_suffix' in p or 'import_resolution' in p) and p['item_id'] in targets]
        for participant in participants:
            item, group_name = participant['item_id'], participant.get('group')
            if item not in targets or not group_name or participant in additions:
                continue
            rows = base['declarations'].get(item, [])
            if len(rows) != 1 or reader.unique_properties(rows[0]) is not None:
                continue
            old_key = (item, record['path'], tuple(record['clauses']), participant['role'], participant['ordinal'], group_name)
            if old_key in baseline_rows:
                continue
            stable, conflicts = stable_properties(rows[0])
            group = groups[group_name]
            tags = set(stable.get('Tags', '').split(';')) & set(group.get('tags', []))
            type_match = item.split('.', 1)[1] in group.get('types', [])
            if not tags and not type_match:
                continue
            repeated = {k: v for k, v in reader.properties(rows[0]).items() if len(v) > 1}
            additions.append({**participant, 'stable_group_resolution': {
                'declaration_path': rows[0]['path'], 'repeated_fields': repeated,
                'membership_tags': sorted(tags), 'membership_short_type': item.split('.', 1)[1] if type_match else None,
                'stable_membership': {k: stable[k] for k in ('Tags',) if k in stable},
                'unrelated_conflicts': conflicts},
                'recovery_reason': 'Historical whole-declaration unique-properties rejection hid this stable exact group membership.'})
        if not additions:
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{record['name']}",
                              {'raw': record['raw'], 'clauses': record['clauses'],
                               'module': record['module'], 'recipe': record['name']})
        for participant in additions:
            item = participant['item_id']
            # Ambiguous declarations remain a local attribution failure. They
            # cannot supply a guessed group membership or declaration winner.
            declarations = base['declarations'].get(item, [])
            evidence = [ref]
            evidence.extend(import_evidence(builder, participant))
            if len(declarations) == 1:
                evidence.append(declaration(item))
            if participant['group']:
                group = groups[participant['group']]
                evidence.append(builder.observe(semantic.GROUPS, f"L{group['line']}:{participant['group']}", group))
            recovered[item].append({**participant, 'observation_ref': ref,
                                    'evidence_refs': sorted(set(evidence))})
    base['recovered_participation'] = dict(recovered)
    base['participation_provenance'] = {
        item: builder.explain(item, 'investigation', sorted({r for p in links for r in p['evidence_refs']}),
            'Same-definition recipe participation recovered from a raw numeric operand, explicit module import or stable group membership hidden by repeated declaration properties. '
            'Role, numeric semantics, callback effects and eligibility still require question-local interpretation.')
        for item, links in recovered.items()}


def import_evidence(builder, participant):
    return [builder.observe(header['path'], f"L{header['line']}:module imports", header)
            for header in participant.get('import_resolution', {}).get('headers', [])]
