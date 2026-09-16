"""Question/result assembly and independent predecessor-claim reconciliation."""
from .recovery_question_rules import (
    defaultdict,
    deepcopy,
    re,
    model,
    semantic,
    sources,
    NATIVE_FIELDS,
    CONSUMERS,
    PLAIN_MELEE_ITEMS,
    PLAIN_MELEE_FIELDS,
)
from . import recovery_direct_review as direct_review
from . import recovery_activities_review as activities_review


def reassess(base, payload, audit):
    location_source = base['reader'].read(sources.BODY_LOCATIONS).decode('utf-8-sig')
    exclusive_pairs = re.findall(r'^group:setExclusive\("([^"]+)",\s*"([^"]+)"\)', location_source, re.M)
    hidden_pairs = re.findall(r'^group:setHideModel\("([^"]+)",\s*"([^"]+)"\)', location_source, re.M)
    facts = {f['fact_id']: f for f in payload['facts']}
    by_question = defaultdict(list)
    for binding in payload['fact_question_bindings']:
        by_question[tuple(binding['question_key'])].append(binding)
    attempts = defaultdict(dict)
    for ref, attempt in payload['attempts'].items():
        attempts[attempt['item_id']][attempt['route']] = (ref, attempt)
    observations = payload['observations']
    results = {model.question_key(r): r for r in payload['results']}
    for row in audit:
        if row['attribution_status'] == 'attributed':
            continue  # The independently reviewed writable-note branch.
        key = tuple(row['question_key'])
        item, axis, scope = key
        result = results[key]
        records = base['declarations'].get(item, [])
        fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
        related = [facts[b['fact_ref']] for b in by_question[key]]
        partial_refs = sorted(f['fact_id'] for f in related)
        route = {'activity:crafting': 'B', 'activity:cooking': 'C', 'activity:world_work': 'D',
                 'item:direct': 'E'}.get(scope, 'A')
        attempt_ref, attempt = attempts[item][route]
        refs = sorted(set(attempt['observation_refs']) | {
            oid for f in related for p in f['provenance_refs'] for oid in payload['provenance'][p]['observation_refs']})
        applied = {'declarations': [{'path': r['path'], 'line': r['line'], 'end_line': r['end_line']} for r in records],
                   'field_values': {k: fields[k] for k in NATIVE_FIELDS.get(scope, ()) if k in fields},
                   'field_conflicts': {k: v for k, v in conflicts.items() if k in NATIVE_FIELDS.get(scope, ())},
                   'consumer': CONSUMERS[scope], 'route_observation_ref': attempt_ref,
                   'participation': deepcopy(attempt['finding']) if route in 'BCD' else None}
        answered = [{'fact_ref': f['fact_id'], 'fact_kind': f['fact_kind'], 'payload': f['payload']} for f in related]
        result['provenance_refs'] = sorted(set(result['provenance_refs']) |
                                           {p for f in related for p in f['provenance_refs']})
        residual, work, failure = None, None, False
        terminal_reason = None
        if len(records) != 1:
            failure = True
            residual = {'meaning': axis + ' in ' + scope,
                        'required_input': 'an exact runtime declaration binding for ' + item,
                        'reason': ('No exact declaration exists in the bound raw script snapshot.' if not records else
                                   'Multiple raw declarations remain; their load order/winner is not established by this snapshot.')}
        elif applied['field_conflicts']:
            failure = True
            residual = {'meaning': axis + ' interpretation of ' + ', '.join(applied['field_conflicts']),
                        'required_input': 'consumer-compatible resolution of the conflicting scalar properties',
                        'reason': 'The listed exact relevant properties conflict; unrelated repeated properties do not block this question.'}
        elif result['state'] == 'evidence_backed_not_applicable':
            if scope == 'activity:ingestion' and axis in {'operation', 'effects'} and fields.get('Type') == 'Food' and fields.get('CantEat', '').lower() == 'true':
                terminal_reason = 'The exact Food/CantEat=true declaration is excluded by the native eating menu predicate; transformed forms and independent direct actions remain separate.'
            else:
                raise ValueError('historical negative requires new scoped exclusion evidence')
        elif scope == 'item:direct':
            refs, residual, work, failure, terminal_reason = direct_review.review(PLAIN_MELEE_FIELDS, PLAIN_MELEE_ITEMS, applied, axis, base, conflicts, facts, failure, fields, item, key, observations, payload, partial_refs, records, refs, residual, result, terminal_reason, work)
        elif scope == 'activity:ingestion':
            residual = {'meaning': ('native consumption state changes' if axis in {'operation', 'effects'} else 'conditions that change the native consumption effects'),
                        'required_input': 'IsoGameCharacter.Eat interpretation for the listed food fields and any OnEat callback dispatch',
                        'reason': 'ISEatFoodAction checks inventory/companions/start state, then delegates nutrition and food-state effects to character:Eat; field signs alone do not establish all applied changes.'}
            if fields.get('CustomContextMenu', '') not in {'', 'Drink'} or fields.get('CustomMenuOption'):
                item_facts = [f for f in facts.values() if f['item_id'] == item]
                if any(f['payload'].get('function') in {'smoke_cigarette', 'take_food_medicine'} for f in item_facts):
                    applied['custom_consumption'] = {
                        'label': fields.get('CustomContextMenu'), 'callback': fields.get('OnEat'),
                        'meaning': 'Custom label shares native food dispatch; admitted smoking/taking and explicit callback effects retain their own qualifiers. Other Eat/ReduceInfectionPower effects remain engine-owned.'}
                else:
                    work = 'Interpret this exact custom consumption label/callback before completing its local operation and conditions.'
        elif scope == 'activity:reading':
            item_payloads = [f['payload'] for f in facts.values() if f['item_id'] == item]
            if (fields.get('SkillTrained') and not fields.get('TeachedRecipes')
                    and {'property': 'reading_page_progress', 'direction': 'update'} in item_payloads
                    and {'property': fields['SkillTrained'] + '_experience_multiplier', 'direction': 'increase'} in item_payloads):
                terminal_reason = ('The registered skill-book branch records/resets page progress and conditionally increases its skill multiplier. '
                                   'The native entry, literacy, skill/page/driving conditions and progress/multiplier restrictions are bound facts; '
                                   'the non-skill ReadLiterature branch is not invoked for this book.')
                if axis == 'conditions' and fields.get('LvlSkillTrained') and fields.get('NumLevelsTrained'):
                    terminal_reason = None
                    applied['skill_level_consumer'] = {
                        'lower_level': fields['LvlSkillTrained'], 'level_count': fields['NumLevelsTrained'],
                        'comparison': 'getLvlSkillTrained <= current perk level + 1 <= getMaxLevelTrained',
                        'effect_arguments': 'addXpMultiplier receives the two level getters',
                        'source': semantic.READ}
                    residual = {'meaning': 'The numeric upper endpoint of the supported skill-level interval for ' + fields['SkillTrained'],
                                'required_input': 'Literature.getMaxLevelTrained mapping of the exact LvlSkillTrained/NumLevelsTrained declaration',
                                'reason': 'The Lua lower/upper comparisons and multiplier dispatch have been interpreted, and their conditional behavior is represented. The native maximum-level getter is consumed rather than calculated in this source; its exact numeric mapping remains separate from the answered literacy, progress, possession and driving conditions.'}
            elif fields.get('SkillTrained'):
                residual = {'meaning': 'reading progress and skill-book conditions beyond the accepted multiplier facts',
                            'required_input': semantic.READ,
                            'reason': 'The Lua action records page progress and evaluates skill levels; these available branches must be represented before whole-scope closure.'}
                work = 'Admit and compose the remaining page-progress/reading-condition meanings from the bound action.'
            else:
                residual = {'meaning': ('non-skill literature effects' if axis in {'operation', 'effects'} else 'conditions changing non-skill literature effects'),
                            'required_input': 'IsoGameCharacter.ReadLiterature and recipe-learning dispatch for the exact declared fields',
                            'reason': 'The non-skill branch calls ReadLiterature; the bound Lua call does not define mood or learned-recipe changes.'}
        elif scope == 'activity:wearing':
            location = fields.get('BodyLocation', fields.get('CanBeEquipped'))
            applied['location_relations'] = {
                'location': location,
                'exclusive_declarations': [list(p) for p in exclusive_pairs if location in p],
                'hidden_model_declarations': [list(p) for p in hidden_pairs if location in p],
                'source': base['reader'].bindings[sources.BODY_LOCATIONS],
                'consumer_handoff': 'ISWearClothing.perform: character:setWornItem(location, item)',
            }
            if item in base.get('unsupported_wear', {}):
                applied['unsupported_location'] = base['unsupported_wear'][item]
                residual = {'meaning': 'wearing behavior at ' + fields['BodyLocation'],
                            'required_input': 'a verified runtime registration/interpretation for the obsolete declaration location ' + fields['BodyLocation'],
                            'reason': base['unsupported_wear'][item]['reason']}
            elif axis == 'operation' and any(f['payload'].get('state') == 'worn_location' for f in related):
                terminal_reason = 'The exact registered BodyLocation is passed to setWornItem by the native wear action; accepted wear/location facts answer the item operation. Protection and insulation are not inferred.'
            else:
                residual = {'meaning': 'runtime replacement and visual handling of the listed conflicting equipment locations',
                            'required_input': 'setWornItem/BodyLocationGroup interpretation for the exact location relations',
                            'reason': 'The raw location relation declarations and native inventory/action conditions were examined. Lua delegates actual replacement to setWornItem; tooltip replacement predictions are not fact-admission evidence.',
                            'exact_location_relations': applied['location_relations']}
                if not any(f['payload'] == {'predicate': sources.WEAR_ACTION} for f in related):
                    work = 'Bind the native wear-action conditions for this exact equipment form.'
        elif scope == 'activity:storage':
            residual = {'meaning': ('container acceptance/removal behavior' if axis == 'operation' else 'item admission and removal conditions'),
                        'required_input': 'container isItemAllowed/isRemoveItemAllowed interpretation and any exact AcceptItemFunction',
                        'reason': 'Transfer code proves conditional storage but delegates item admission/removal; the exact Capacity and acceptance fields above determine the unresolved question.'}
        elif scope == 'activity:combat':
            residual = {'meaning': ('attack outcome and affected state' if axis == 'operation' else 'target/hit and attack-effect conditions'),
                        'required_input': 'DoAttack/WeaponHit or IsoTrap interpretation for the exact weapon declaration',
                        'reason': 'Admitted firing/tree-use facts are bounded. Hit, damage and trap state changes are not defined by the attack dispatch calls.'}
        elif scope == 'activity:expenditure':
            residual = {'meaning': 'depletion/replacement outcome' if axis == 'operation' else 'conditions of depletion and replacement',
                        'required_input': 'InventoryItem.Use and the exact ReplaceOnDeplete dispatch',
                        'reason': 'Any accepted water effects remain supported; depletion and replacement are a separate engine handoff for the declared drainable form.'}
        else:
            refs, residual, work, failure, terminal_reason = activities_review.review(applied, attempt, axis, base, conflicts, facts, failure, fields, item, observations, payload, refs, residual, scope, terminal_reason, work)
        if scope == 'item:direct' and item in base.get('heat_control_sources', {}):
            heat = base['heat_control_sources'][item]
            applied['shared_heat_controls'] = {'functions': heat['functions'], 'predicates': heat['predicates']}
            refs = sorted(set(refs) | set(heat['observation_refs']))
            if residual is not None:
                residual['additional_heat_boundary'] = 'Native target binding, fire/heat state and delivery remain separate from the interpreted fuel, tinder or ignition action; explicit source arithmetic and inactive client branches remain attached.'
        if scope == 'item:direct' and item in base.get('equipment_control_sources', {}):
            equipment = base['equipment_control_sources'][item]
            applied['shared_equipment_controls'] = {'functions': equipment['functions'], 'predicates': equipment['predicates']}
            refs = sorted(set(refs) | set(equipment['observation_refs']))
            if residual is not None:
                residual['additional_equipment_boundary'] = 'Native object/part binding, world mutation and inventory delivery remain separate from the exact additional equipment actions; their source-specific continued-validity and interruption rules are retained.'
        if applied.get('shared_garment_patching') and residual is not None:
            residual['additional_examined_dependency'] = applied['shared_garment_patching']['native_boundary']
        row.update(attribution_status='attribution_failure' if failure else 'attributed',
                   attribution_rule_ref='question_scope/1/' + scope + '/' + axis,
                   applied_inputs=applied, direct_evidence_refs=refs,
                   accepted_partial_fact_refs=partial_refs, answered_scope=answered,
                   remaining_scope=[] if terminal_reason else [residual], remaining_work=work,
                   effective_blocker_refs=[])
        if terminal_reason:
            if result['state'] != 'evidence_backed_not_applicable':
                result.update(state='resolved', fact_refs=partial_refs)
                for binding in by_question[key]:
                    binding['contribution'] = 'whole_scope'
            result.update(question_coverage='whole_scope', coverage_justification=terminal_reason,
                          blockers=[], next_source_dependency=None, transition_reason=terminal_reason)
            row['whole_scope_reason'] = terminal_reason
        else:
            blocker = model.identity('residual', [list(key), residual])
            row['effective_blocker_refs'] = [{'ref': blocker, 'remaining_scope': residual,
                                              'evidence_refs': refs, 'reason': residual['reason']}]
            result.update(state='investigated_unresolved', fact_refs=[], question_coverage='partial',
                          blockers=[blocker], next_source_dependency=residual['required_input'],
                          transition_reason=residual['reason'])
        row['successor_result'] = deepcopy(result)
    return audit


def reconcile_direct_claims(base, payload, audit, inventory):
    """Finish only the predecessor comparison named by the direct local work.

    Use the actual migrated clauses and their source adjudications. No result is
    made terminal, and a route's empty unfinished list alone is insufficient.
    """
    claims = defaultdict(list)
    unsegmented = defaultdict(list)
    for claim in inventory['claims']:
        claims[claim['item_id']].append(claim)
    for clause in inventory['clauses']:
        if clause['classification'] == 'unsegmented':
            unsegmented[clause['item_id']].append({'locale': clause['locale'], 'span': clause['span']})
    conservation = {c['predecessor_claim_id']: c for c in inventory['conservation']}
    for row in audit:
        key = tuple(row['question_key'])
        if key[2] != 'item:direct' or row['attribution_status'] != 'attributed' or not row.get('remaining_work'):
            continue
        item_claims = claims[key[0]]
        compared = []
        for claim in item_claims:
            conserved = conservation.get(claim['predecessor_claim_id'], {})
            if (claim['migration_disposition'] != 'pending_investigation' and not claim.get('remaining_work')
                    and conserved.get('conservation_status') in {'conserved', 'responsibility_removed', 'bounded_unresolved'}):
                compared.append({'claim_ref': claim['predecessor_claim_id'], 'meaning': claim.get('meaning'),
                                 'disposition': claim['migration_disposition'],
                                 'fact_refs': claim['candidate_successor_fact_refs'],
                                 'source_refs': claim['verified_source_refs'],
                                 'remaining_uncertainty': claim['remaining_uncertainty']})
        row['applied_inputs']['predecessor_comparison'] = {
            'compared': compared, 'unsegmented_surfaces': unsegmented[key[0]],
            'pending_claim_refs': sorted(c['predecessor_claim_id'] for c in item_claims
                                        if c['predecessor_claim_id'] not in {v['claim_ref'] for v in compared})}
        records = base['declarations'].get(key[0], [])
        if len(records) != 1 or sources.stable_properties(records[0])[1]:
            continue
        attempt = payload['attempts'][row['applied_inputs']['route_observation_ref']]
        if (not item_claims or len(compared) != len(item_claims) or unsegmented[key[0]]
                or attempt['unfinished_semantic_paths']):
            continue
        row['applied_inputs']['predecessor_comparison']['completion'] = 'complete'
        row['remaining_work'] = ('Predecessor comparison is complete. Independently establish which additional exact '
                                 'operation or condition propositions remain unanswered and which source dependency '
                                 'actually blocks each; conditional behavior must not be blocked merely by unknown current state.')
