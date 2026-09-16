"""Crafting, cooking and world-work question review."""
from .recovery_question_rules import CONSUMERS, deepcopy, sources


def review(applied, attempt, axis, base, conflicts, facts, failure, fields, item, observations, payload, refs, residual, scope, terminal_reason, work):
    finding = attempt['finding']
    if scope == 'activity:crafting':
        local = finding.get('participants', [])
        meaning = 'roles of the exact consumed/kept/result participants' if axis == 'role' else 'eligibility and callback conditions of those exact recipe participants'
        work = 'Lower the reviewed exact recipe participation to context-local roles/conditions where supported; keep is not automatically a tool.'
    elif scope == 'activity:cooking':
        local = {k: finding.get(k) for k in ('declared_entries', 'base_or_result_refs')}
        applied['previous_declared_entries'] = local['declared_entries']
        local['declared_entries'] = fields.get('EvolvedRecipe')
        applied['current_declared_entries'] = local['declared_entries']
        meaning = 'ingredient/base/result role' if axis == 'role' else 'accepted ingredient and food-state restrictions'
        work = 'Reconcile exact ingredient versus base/result membership and its caller filters before whole-scope closure.'
    else:
        local = {k: finding.get(k) for k in ('fixing', 'stages', 'building_candidates', 'moveable_tools')}
        meaning = 'context-local repair/construction/moveable roles' if axis == 'role' else 'conditions of those exact world-work participants'
        work = 'Reconcile each listed exact fixing/stage/tool relation with its already interpreted consumer and accepted facts.'
    residual = {'meaning': meaning, 'required_input': CONSUMERS[scope],
                'reason': 'The exact participation is evidence for this axis; remaining local interpretation is explicitly unfinished, not a generic route-wide engine blocker.',
                'exact_participation': local}
    if scope == 'activity:cooking':
        item_facts = [f for f in facts.values() if f['item_id'] == item]
        ingredient = any(f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'ingredient'}
                         and facts[f['context_fact_ref']]['payload'] == {'activity': 'food_preparation'}
                         for f in item_facts)
        conditions = any(f['payload'] == {'predicate': sources.COOKING_ACTION} for f in item_facts)
        ingredient_ok = (not local['declared_entries'] or (ingredient and conditions
                         and fields.get('EvolvedRecipe') == local['declared_entries']
                         and 'EvolvedRecipe' not in conflicts))
        base_relations = base.get('cooking_base_relations', {}).get(item, [])
        base_ok = all(any(r['path'] == observations[ref]['source_path']
                         and r['clauses'] == observations[ref]['content'].get('clauses')
                         for r in base_relations) for ref in local['base_or_result_refs'])
        if local['base_or_result_refs']:
            base_ok = base_ok and any(f['payload'] == {'predicate': sources.COOKING_BASE} for f in item_facts)
            applied['base_and_result_relations'] = base_relations
        if ingredient_ok and base_ok and (ingredient or base_relations):
            work = None
            residual.update(required_input='EvolvedRecipe.getEvolvedRecipe/getItemsCanBeUse/needToBeCooked/addItem for the exact declared roles',
                            reason='Ingredient entries and each BaseItem/ResultItem relation are separately reconciled to accepted context-local roles and caller/action conditions. The explicit isResultItem continuation branch supports adding to prepared food; output membership alone is not treated as a use. Runtime food eligibility and transformation remain at the named engine methods. Source inventory, poisoning-policy and frozen/cooked filters were examined.')
    elif scope == 'activity:world_work':
        item_facts = [f for f in facts.values() if f['item_id'] == item]
        repairs = [f for f in item_facts if f['fact_kind'] == 'context_role'
                   and facts[f['context_fact_ref']]['payload'] == {'activity': 'repair'}]
        interpreted = []
        for link in local['fixing']:
            original = observations[link['observation_ref']]
            matching = [f for f in repairs if f['payload'] == {'role': link['role']}
                        and any(o == link['observation_ref'] or (
                            observations[o]['source_path'] == original['source_path']
                            and observations[o]['source_sha256'] == original['source_sha256']
                            and original['content'].get('raw')
                            and observations[o]['content'].get('raw', '').replace('\r\n', '\n') == original['content']['raw'].replace('\r\n', '\n'))
                            for p in f['provenance_refs'] for o in payload['provenance'][p]['observation_refs'])]
            if matching:
                interpreted.append({'observation_ref': link['observation_ref'], 'role': link['role'],
                                    'role_fact_refs': sorted(f['fact_id'] for f in matching)})
        fixing_ok = len(interpreted) == len(local['fixing']) and (not local['fixing'] or
                    any(f['payload'] == {'predicate': sources.FIXING_ACTION} for f in item_facts))
        tool_relations = base.get('moveable_tool_relations', {}).get(item, [])
        tools_ok = all(any(all(r.get(k) == link.get(k) for k in ('definition', 'token', 'tag'))
                          for r in tool_relations) for link in local['moveable_tools'])
        if local['moveable_tools']:
            tools_ok = tools_ok and any(f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'tool'}
                                        and facts[f['context_fact_ref']]['payload'] == {'activity': 'moving_furniture'}
                                        for f in item_facts)
            applied['interpreted_moveable_tools'] = tool_relations
        construction_roles = [f for f in item_facts if f['fact_kind'] == 'context_role'
                              and facts[f['context_fact_ref']]['payload'] == {'activity': 'construction'}]
        interpreted_stages = []
        for link in local['stages']:
            matching = [f for f in construction_roles if f['payload'] == {'role': link['role']}
                        and link['observation_ref'] in {
                            o for p in f['provenance_refs'] for o in payload['provenance'][p]['observation_refs']}]
            if matching:
                interpreted_stages.append({'observation_ref': link['observation_ref'], 'role': link['role'],
                                           'role_fact_refs': sorted(f['fact_id'] for f in matching)})
        stages_ok = len(interpreted_stages) == len(local['stages']) and (not local['stages'] or
                    any(f['payload'] == {'predicate': sources.STAGE_ACTION} for f in item_facts))
        interpreted_building = []
        for ref in local['building_candidates']:
            factory = observations[ref]['content']['factory']
            relation = next((r for r in base.get('factory_relations', {}).get(item, [])
                             if r['observation_ref'] == ref), None)
            if relation is not None:
                role = facts.get(relation.get('role_fact_ref'))
                if (relation['status'] == 'active_welding' and role and role['payload'] == {'role': relation['role']}
                        and facts[role['context_fact_ref']]['payload'] == {'activity': 'metal_welding_construction'}
                        and any(f['payload'] == {'predicate': sources.WELDING_CONSTRUCTION} for f in item_facts)):
                    interpreted_building.append(deepcopy(relation))
                    continue
                if relation['status'] == 'no_active_menu_reference' or (
                        role and role['payload'] == {'role': 'material'}
                        and facts[role['context_fact_ref']]['payload'] == {'activity': 'carpentry_menu_construction'}
                        and any(f['payload'] == {'predicate': sources.CARPENTRY_MATERIAL} for f in item_facts)):
                    interpreted_building.append(deepcopy(relation))
                    continue
            if factory in {'ISBuildMenu.onLogWall', 'ISBuildMenu.onWoodenCross'}:
                matching = [f for f in construction_roles if f['payload'] == {'role': 'material'}
                            and any(payload['provenance'][p]['rule_ref'] == 'construction' for p in f['provenance_refs'])]
                if matching:
                    interpreted_building.append({'observation_ref': ref, 'factory': factory,
                                                 'role_fact_refs': sorted(f['fact_id'] for f in matching)})
        building_ok = len(interpreted_building) == len(local['building_candidates'])
        applied['interpreted_stage_relations'] = interpreted_stages
        applied['interpreted_building_relations'] = interpreted_building
        if fixing_ok and tools_ok and stages_ok and building_ok and any(local.values()):
            applied['interpreted_fixing_relations'] = interpreted
            work = None
            boundaries = []
            if local['fixing']:
                boundaries.append('FixingManager runtime selection, consumption and repair outcome')
            if local['moveable_tools']:
                boundaries.append('object-specific pickup/place properties and permission state')
            if local['stages']:
                boundaries.append('MultiStageBuilding selection and doStage outcome for the exact previous-stage/skill declarations')
            if local['building_candidates']:
                boundaries.append('world placement, availability and runtime object construction for the exact active factory branches')
            residual.update(required_input='; '.join(boundaries),
                            reason='Every listed fixing, tool, stage and active-factory relation is reconciled separately to its scoped role and conditions. Repair inventory/vehicle exceptions, actual moveable FullType/tag membership, stage start/interruption/consumption and log-wall binding alternatives are retained where applicable. The named runtime selection or object-result boundary remains; no listed local relation is hidden by that boundary.')
    elif scope == 'activity:crafting':
        group_context = {'Recipe.GetItemTypes.CraftSheetRope': 'sheet_rope_making',
                         'Recipe.GetItemTypes.RipSheets': 'fabric_recovery',
                         'Recipe.GetItemTypes.RipClothing_Cotton': 'fabric_recovery',
                         'Recipe.GetItemTypes.RipClothing_Denim': 'fabric_recovery',
                         'Recipe.GetItemTypes.RipClothing_Leather': 'fabric_recovery'}
        interpreted = []
        crafting_roles = [f for f in facts.values() if f['item_id'] == item and f['fact_kind'] == 'context_role']
        material_roles = [f for f in facts.values() if f['item_id'] == item and f['fact_kind'] == 'context_role'
                          and f['payload'] == {'role': 'material'}]
        opening_functions = [f for f in facts.values() if f['item_id'] == item
                             and f['fact_kind'] in {'direct_function', 'context_role'}
                             and any(payload['provenance'][p]['rule_ref'] in {'package_opening', 'umbrella_form', 'battery_receiver', 'electronic_salvage', 'radio_crafting', 'material_assembly'}
                                     for p in f['provenance_refs'])]
        for link in local:
            if link['role'] == 'result':
                interpreted.append({'observation_ref': link['observation_ref'], 'clause': link['clause'],
                                    'disposition': 'transformation output; not an intrinsic crafting-use role'})
                continue
            original = observations[link['observation_ref']]
            baking = [f for f in crafting_roles if any(
                payload['provenance'][p].get('contributor_rule_ref', payload['provenance'][p]['rule_ref']) in {'baking_preparation', 'bandage_materials', 'spear_crafting', 'fabric_conditions', 'smithing_parts', 'box_packing', 'bowl_portioning', 'seed_packing', 'jar_preparation', 'bandage_washing', 'crop_spray_preparation', 'camping_kit_preparation', 'shovel_smithing', 'poultice_preparation', 'metal_forging', 'welded_parts', 'log_binding', 'mattress_preparation', 'frog_preparation', 'wire_recovery', 'food_preparation_recipes', 'item_transformation_recipes'}
                and any(observations[o]['source_path'] == original['source_path']
                        and observations[o]['source_sha256'] == original['source_sha256']
                        and observations[o]['content'].get('clauses') == original['content'].get('clauses')
                        for o in payload['provenance'][p]['observation_refs'])
                for p in f['provenance_refs'])]
            if baking:
                interpreted.append({'observation_ref': link['observation_ref'], 'clause': link['clause'],
                                    'role_fact_refs': sorted(f['fact_id'] for f in baking),
                                    'disposition': 'Exact reviewed preparation role and conditions from its complete recipe clauses; raw numeric semantics remain native residual, without semicolon conversion.'})
                continue
            if link.get('numeric_suffix') or link.get('import_resolution'):
                continue  # Unreviewed identity admission alone never resolves a role.
            # These are already admitted, recipe-specific roles. Join
            # their own provenance rather than generalizing input/keep.
            established = []
            for fact in crafting_roles:
                activity = facts[fact['context_fact_ref']]['payload'].get('activity')
                expected = None
                if activity == 'woodworking' and link['role'] in {'input', 'keep'}:
                    expected = ('woodwork', 'tool' if link['role'] == 'keep' else 'material')
                elif activity == 'portable_device_power' and link['role'] == 'destroy':
                    expected = ('battery_supply', 'power_supply')
                if expected and fact['payload'] == {'role': expected[1]} and any(
                        payload['provenance'][p]['rule_ref'] == expected[0]
                        and link['observation_ref'] in payload['provenance'][p]['observation_refs']
                        for p in fact['provenance_refs']):
                    established.append(fact['fact_id'])
            if established:
                interpreted.append({'observation_ref': link['observation_ref'], 'clause': link['clause'],
                                    'role_fact_refs': sorted(established),
                                    'disposition': 'existing recipe-specific role with its bound eligibility condition'})
                continue
            opening = [f for f in opening_functions if any(
                observations[o]['source_path'] == original['source_path']
                and observations[o]['source_sha256'] == original['source_sha256']
                and original['content'].get('clauses')
                and observations[o]['content'].get('clauses') == original['content']['clauses']
                for p in f['provenance_refs'] for o in payload['provenance'][p]['observation_refs'])]
            if opening and (link['role'] in {'input', 'destroy'} or (
                    link['role'] == 'keep' and (link.get('group') in {'Recipe.GetItemTypes.CanOpener', 'Recipe.GetItemTypes.Screwdriver'}
                    or any(f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'tool'}
                           and any(payload['provenance'][p]['rule_ref'] == 'material_assembly' for p in f['provenance_refs'])
                           for f in opening)))):
                interpreted.append({'observation_ref': link['observation_ref'], 'clause': link['clause'],
                                    'transformation_fact_refs': sorted(f['fact_id'] for f in opening),
                                    'disposition': 'reviewed transformation participant with its accepted eligibility conditions'})
                continue
            context = group_context.get(link.get('group'))
            matching = [f for f in material_roles if facts[f['context_fact_ref']]['payload'] == {'activity': context}
                        and link['observation_ref'] in {
                            obs for p in f['provenance_refs'] for obs in payload['provenance'][p]['observation_refs']}]
            # Recovery uses a more precise locator and retains CRLF;
            # join the same bound source and complete parsed clauses.
            if context == 'sheet_rope_making' and not matching:
                original = observations[link['observation_ref']]
                clauses = original['content'].get('clauses')
                matching = [f for f in material_roles if facts[f['context_fact_ref']]['payload'] == {'activity': context}
                            and clauses and any(observations[o]['content'].get('clauses') == clauses
                                and observations[o]['source_path'] == original['source_path']
                                and observations[o]['source_sha256'] == original['source_sha256']
                                for p in f['provenance_refs'] for o in payload['provenance'][p]['observation_refs'])]
            if link['role'] == 'input' and matching:
                interpreted.append({'observation_ref': link['observation_ref'], 'clause': link['clause'], 'group': link['group'],
                                    'role_fact_refs': sorted(f['fact_id'] for f in matching)})
        # Preserve completed per-relation work even when another
        # recipe for the same item still needs local interpretation.
        applied['interpreted_material_relations'] = interpreted
        suffixes = [deepcopy(link) for link in local if link.get('numeric_suffix')]
        if suffixes:
            residual['uninterpreted_participation'] = suffixes
            residual['numeric_semantics'] = 'Raw numeric operands, including their separator and spacing, are preserved; participation recovery does not infer consumption amounts or translate semicolon semantics into equals semantics.'
        imports = [deepcopy(link) for link in local if link.get('import_resolution')]
        if imports:
            residual['imported_participation'] = imports
            residual['import_semantics'] = 'Explicit import headers bind unique absent-local source identities; native runtime module resolution and participant selection remain separate from this source participation admission.'
        if local and len(interpreted) == len(local) and any(link['role'] != 'result' for link in local):
            work = None
            residual.update(required_input='RecipeManager runtime eligibility/selection/consumption for the exact reconciled recipes',
                            reason='Every listed input, destroy or kept participant is reconciled to a source-bound material role or an explicitly reviewed transformation function and its conditions. Fabric recipes retain their fabric/state restrictions; package opening retains any CanOpener requirement; umbrella form changes and battery receivers retain their callback conditions. Result clauses are acquisition leads rather than intrinsic-use evidence. No arbitrary keep-to-tool inference is made. Runtime recipe eligibility and selected material state remain unresolved.')
        elif local and all(link['role'] == 'result' for link in local):
            applied['output_only_relations'] = [
                {'observation_ref': link['observation_ref'], 'clause': link['clause'],
                 'disposition': 'transformation output; not an intrinsic crafting-use role'} for link in local]
            work = None
            residual.update(required_input='Runtime recipe-group membership and RecipeManager participant selection beyond the exact output-only observations',
                            reason='Every exact known participation for this item is a result clause. These observations describe how the item is produced; they do not establish a material/tool use or its conditions. No output role is relabeled as an intrinsic function. The supplied partial group expansion does not prove that runtime groups add no further input participation, so whole-scope N/A is not claimed.',
                            parser_boundary='parser_limits/recipe_opaque and runtime group registration')
    return refs, residual, work, failure, terminal_reason
