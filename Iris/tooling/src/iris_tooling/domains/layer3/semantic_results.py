"""Offline semantic investigation producer. No composer or runtime writer.

The input snapshot limits every conclusion. Runtime eligibility and opaque
callbacks remain explicit dependencies, including when useful partial facts exist.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import argparse
import json
import os
import re

from . import investigation as inv
from . import source_reader as reader
from . import interpretations as meaning
from .semantic_model import SCHEMA, canonical, fact_identity, identity

ROOT = 'Iris/_docs/authority/dvf/layer3_semantic_results'
HUMAN = 'docs/iris_dvf_layer3_semantic_investigation_question_results_contract.md'
TEST_SOURCE = 'Iris/build/description/v2/tests/test_layer3_semantic_results.py'
TEST_ID = 'test_layer3_semantic_results.Layer3SemanticResultsTest.test_semantic_results_contract'
ENTRY = 'layer3_semantic_results'
MENU = 'lua/client/ISUI/ISInventoryPaneContextMenu.lua'
GROUPS = 'lua/server/recipecode.lua'
CLOTHING = 'lua/shared/Definitions/ClothingRecipesDefinitions.lua'
EAT = 'lua/client/TimedActions/ISEatFoodAction.lua'
CRAFT = 'lua/client/TimedActions/ISCraftAction.lua'
COOK = 'lua/client/TimedActions/ISAddItemInRecipe.lua'
FIX = 'lua/client/TimedActions/ISFixAction.lua'
MOVE = 'lua/client/Moveables/ISMoveableDefinitions.lua'
PROPS = 'lua/client/Moveables/ISMoveableSpriteProps.lua'
MOVE_ACTION = 'lua/client/Moveables/ISMoveablesAction.lua'
WEAR = 'lua/client/TimedActions/ISWearClothing.lua'
READ = 'lua/client/TimedActions/ISReadABook.lua'
DRY = 'lua/client/TimedActions/ISDryMyself.lua'
DRINK = 'lua/client/TimedActions/ISDrinkFromBottle.lua'
TRANSFER = 'lua/client/TimedActions/ISInventoryTransferAction.lua'
SKILLS = 'lua/server/XpSystem/XPSystem_SkillBook.lua'
BUILD = 'lua/client/BuildingObjects/ISUI/ISBuildMenu.lua'
STAGE = 'lua/client/BuildingObjects/TimedActions/ISMultiStageBuild.lua'
BUILD_ACTION = 'lua/client/BuildingObjects/TimedActions/ISBuildAction.lua'
BUILD_UTIL = 'lua/server/BuildingObjects/ISBuildUtil.lua'
BUILD_OBJECT = 'lua/server/BuildingObjects/ISBuildingObject.lua'
WALL = 'lua/server/BuildingObjects/ISWoodenWall.lua'
FURNITURE = 'lua/server/BuildingObjects/ISSimpleFurniture.lua'
SHOTGUN = 'lua/shared/Reloading/ISShotgunWeapon.lua'
BANDAGE = 'lua/client/TimedActions/ISApplyBandage.lua'
DYE = 'lua/client/TimedActions/ISDyeHair.lua'
PILLS = 'lua/client/TimedActions/ISTakePillAction.lua'

# Each rule was reviewed against its source consumers, not just extracted fields.
# This table is producer admission metadata, not a second validation registry.
RULES = {
    'construction': ('D', 'Raw multistage ItemsRequired joined to ISBuildMenu/canDoStage and ISMultiStageBuild.consumeMaterial; or reviewed active wooden-cross/log-wall construction branches.',
        'Construction material or tool, conditional on the specific stage/branch and world placement requirements.',
        'Not all declared callbacks are active. Log-wall binding alternatives and no-hammer branch are preserved; no health/strength claim.'),
    'bandaging': ('E', 'CanBandage=true -> damaged body-part menu -> inventory-valid ISApplyBandage.',
        'Apply a bandage; preserve patient/movement/inventory eligibility.',
        'No healing or infection prevention claim. Dirty/infected material and character traits can change the outcome.'),
    'hair_dye': ('E', 'HairDye=true -> existing hair/beard menu branch -> ISDyeHair.',
        'Dye hair or beard subject to an existing corresponding visual and possession.',
        'No claim of a particular color absent resolved visual data; no bald-hair applicability.'),
    'pill_taking': ('E', 'Exact case-sensitive Pills prefix -> onPillsItems -> ISTakePillAction.',
        'Take pills from inventory.',
        'BodyDamage.JustTookPill is an engine boundary; no drug effect inferred from a name.'),
    'fabric_recovery': ('B', 'Exact Recipe.OnCreate.RipClothing callback, structurally expanded fabric group, and non-keep input.',
        'Fabric recovery material, conditional on fabric definition and recipe eligibility.',
        'Not all clothing is eligible; dirty yields and recovered quantity/thread are runtime-dependent.'),
    'battery_supply': ('B', 'Exact Battery destroy-input in Recipe.OnCreate.TorchBatteryInsert and corresponding Torch/HandTorch/Rubberducky2 result.',
        'Power supply for a compatible portable device; transferred charge follows the battery used.',
        'No universal Drainable-to-fuel inference or arbitrary device compatibility.'),
    'drinking_water': ('E', 'Unique Drainable declaration with IsWaterSource=true, joined to isWaterSource -> doDrinkForThirstMenu -> onDrinkForThirst -> ISDrinkFromBottle.',
        'Drink stored water; thirst decreases while positive. Tainted water conditionally increases poison level under the explicit Lua thresholds.',
        'Empty water-storage containers, Food drinks and unknown declarations are not admitted. Water toxicity is conditional, never asserted for every water item.'),
    'reading': ('A', 'Unique non-writable Literature declaration, menu literacy/skill checks, and ISReadABook.',
        'Read literature; a bound SkillBook mapping additionally supports conditional skill experience multiplier increase.',
        'No claim that every book grants XP/recipes or improves mood; non-skill ReadLiterature engine effects remain unresolved.'),
    'storage': ('A', 'Unique Container declaration with positive Capacity and inventory-container transfer consumer.',
        'Store and retrieve items subject to capacity, admission, removal, accessibility and multiplayer restrictions.',
        'No weight-reduction arithmetic or assertion that arbitrary items fit.'),
    'native_eating': ('A', 'Unique Food declaration, CantEat not true, no custom menu, explicit negative HungerChange.',
        'Eating action, inventory/required item and satiety prerequisites; no inferred nutritional effect.',
        'CantEat, custom commands (including smoking), missing hunger and duplicate declarations are excluded.'),
    'native_block': ('A', 'Unique Food declaration with explicit CantEat=true and menu exclusion.',
        'Current form is excluded from native eating; processing/other actions remain open.',
        'No item-global absence and no inference about a transformed item.'),
    'wearing': ('A', 'Unique Clothing declaration with nonempty BodyLocation and wear consumer.',
        'Wearing on the body with possession prerequisite; no insulation or protection inference.',
        'BodyLocation absent, duplicate declaration and container equipment are not this rule.'),
    'writing': ('E', 'Unique Literature declaration with CanBeWrite=true and note editing consumer.',
        'Record written notes subject to writing implement and ownership lock.',
        'Not skill training or automatic knowledge acquisition.'),
    'drying': ('E', 'Exact BathTowel or DishCloth branch and ISDryMyself action.',
        'Dry the body, decreasing wetness while wet and towel has uses remaining.',
        'No numeric drying rate, clothing drying, or duration claim.'),
    'cooking_ingredient': ('C', 'Unique declaration with explicit EvolvedRecipe entry joined to raw evolvedrecipe definition.',
        'Food preparation ingredient conditional on recipe eligibility, cooking/frozen restrictions.',
        'No runtime eligibility guarantee, exact relation enumeration, or ingestion effect.'),
    'repair': ('D', 'Raw Require/Fixer clauses joined to repair menu and ISFixAction.',
        'Repair context with repair material or repair target role; engine validity remains conditional.',
        'No success probability, amount repaired, or first/last duplicate winner.'),
    'moving': ('D', 'Exact item/tag expansion of original moveable tool definitions consumed by hasTool.',
        'Tool for moving furniture when the object asks for that tool and world/action prerequisites hold.',
        'No universal construction, dismantling or furniture compatibility inference.'),
    'woodwork': ('B', 'Reviewed plank/nails/saw/hammer transformation recipes with raw input/keep/group clauses.',
        'Woodworking material/tool context; retained inputs are tools only in these reviewed transformations.',
        'No general keep-to-tool conversion; output relations stay observations.'),
    'investigation': ('ABCDE', 'Bound raw observations, searches and declared source consumers.',
        'Question attempt and residual dependency only; this rule never creates accepted facts.',
        'A literal hit, absence, parser limitation or profile label is not a semantic proposition.'),
}
WOOD_RECIPES = {'Make Stake', 'Make Mortar and Pestle', 'Build Spiked Baseball Bat', 'Build Spiked Plank'}


def rule_records() -> dict:
    return {key: {'revision': '1', 'route': row[0], 'preconditions': row[1], 'transformation': row[2],
                  'exceptions': row[3], 'review_state': 'reviewed', 'reviewed_on': '2026-09-04',
                  'review_scope': 'unique automatic rule and its explicit admission boundary; not every emitted fact'}
            for key, row in RULES.items()}


class Builder:
    def __init__(self, sources: dict[str, str]):
        self.sources = sources
        self.observations = {}
        self.provenance = {}
        self.facts = {}
        self.fact_scopes = defaultdict(set)

    def observe(self, path: str, locator: str, content) -> str:
        row = {'source_path': path, 'source_sha256': self.sources[path], 'locator': locator, 'content': content}
        oid = identity('obs', row)
        self.observations[oid] = row
        return oid

    def explain(self, item: str, rule: str, refs: list[str], proposition: str, fid: str | None = None) -> str:
        first = self.observations[refs[0]]
        row = {'item_id': item, 'source_path': first['source_path'], 'source_sha256': first['source_sha256'],
               'locator': first['locator'], 'observation_refs': sorted(set(refs)), 'rule_ref': rule,
               'rule_revision': '1', 'proposition': proposition, 'semantic_identity': fid}
        pid = identity('prov', row)
        self.provenance[pid] = row
        return pid

    def fact(self, item: str, kind: str, payload: dict, refs: list[str], rule: str, scopes: list[str], **relations) -> str:
        fact = {'item_id': item, 'fact_kind': kind, 'status': 'accepted', 'payload': payload, **relations}
        fid = fact_identity(fact)
        pid = self.explain(item, rule, refs, canonical({'kind': kind, 'payload': payload, **relations}), fid)
        if fid not in self.facts:
            self.facts[fid] = {**fact, 'fact_id': fid, 'provenance_refs': [],
                               'admission': {'rule_ref': rule, 'supported': True}}
        if pid not in self.facts[fid]['provenance_refs']:
            self.facts[fid]['provenance_refs'].append(pid)
        self.fact_scopes[fid].update(scopes)
        return fid

    def activity(self, item, activity, role, refs, rule, scopes, predicate):
        context = self.fact(item, 'use_context', {'activity': activity}, refs, rule, scopes)
        local_role = self.fact(item, 'context_role', {'role': role}, refs, rule, scopes, context_fact_ref=context)
        self.fact(item, 'condition', {'predicate': predicate}, refs, rule, scopes,
                  applies_to_fact_refs=[context, local_role])


def source_paths(root: Path, contract: dict) -> list[str]:
    paths = {s['path'] for s in contract['sources']}
    # The plan names repository scripts and inventory action dependencies as inputs.
    paths.update(p.relative_to(root).as_posix() for p in (root / 'scripts').rglob('*.txt'))
    paths.update({GROUPS, CLOTHING, EAT, CRAFT, COOK, FIX, MOVE, PROPS, MOVE_ACTION, WEAR, READ, DRY, DRINK, TRANSFER, SKILLS,
                  BUILD, STAGE, BUILD_ACTION, BUILD_UTIL, BUILD_OBJECT, WALL, FURNITURE, SHOTGUN})
    menu = (root / MENU).read_text(encoding='utf-8-sig')
    class_names = set(re.findall(r'\b(IS\w+):new\(', reader.mask(menu, lua=True)))
    # Locate only actions actually called from this source; do not scan user paths.
    paths.update(p.relative_to(root).as_posix() for p in (root / 'lua').rglob('*.lua') if p.stem in class_names)
    return sorted(paths)


def prepare(root: Path) -> dict:
    """One real corpus production. No resolver replay or test is run here."""
    contract = inv.read_json(root / inv.ROOT / 'contract.json')
    definition = inv.binding(root, inv.ROOT + '/manifest.json')
    predecessor = inv.bound_json(root, definition)
    for member in predecessor['members']:
        inv.require(inv.binding(root, member['path']) == member, 'predecessor member drift')
    inv.inherited_contract(root, contract['inherits'])
    for source in contract['sources']:
        inv.require(inv.binding(root, source['path']) == source, 'bound source drift')
    target_ids = inv.targets(root)
    inv.require(len(target_ids) == 2105 and inv.set_digest(target_ids) == predecessor['target_set_sha256'], 'target drift')
    baseline = inv.read_rows(root / inv.ROOT / 'applications.jsonl')
    prior_evidence = inv.exact_rows(inv.read_rows(root / inv.ROOT / 'evidence.jsonl'))
    paths = source_paths(root, contract)
    sources = [inv.binding(root, path) for path in paths]
    texts = {path: inv.local_path(root, path).read_text(encoding='utf-8-sig') for path in paths}
    b = Builder({s['path']: s['sha256'] for s in sources})
    records = [record for path in paths if path.startswith('scripts/')
               for record in reader.declarations(texts[path], path)]
    raw_items = defaultdict(list)
    record_refs = {}
    for record in records:
        ref = b.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{record['kind']}:{record['module']}.{record['name']}",
                        {'raw': record['raw'], 'clauses': record['clauses']})
        record_refs[id(record)] = ref
        if record['kind'] == 'item': raw_items[record['module'] + '.' + record['name']].append(record)
    fields = {item: reader.unique_properties(rows[0]) if len(rows) == 1 else None for item, rows in raw_items.items()}
    group_defs = reader.groups(texts[GROUPS])
    reader.expand_structural_groups(group_defs, fields, texts[CLOTHING])
    group_refs = {name: b.observe(GROUPS, f"L{group['line']}:{name}", group) for name, group in group_defs.items()}
    # Source inventories are shared observations; item attempts store exact matches.
    inventories = {}
    for route, selected in {
        'A': [p for p in paths if p.startswith('scripts/')] + [MENU, EAT, WEAR, READ, TRANSFER, SKILLS],
        'B': [p for p in paths if p.startswith('scripts/')] + [GROUPS, CLOTHING, CRAFT, SHOTGUN],
        'C': ['scripts/evolvedrecipes.txt', GROUPS, COOK, MENU],
        'D': ['scripts/fixing.txt', 'scripts/vehicles/vehiclesfixing.txt', MOVE, PROPS, MOVE_ACTION, FIX,
              BUILD, STAGE, BUILD_ACTION, BUILD_UTIL, BUILD_OBJECT, WALL, FURNITURE, 'scripts/multistagebuild.txt', MENU],
        'E': [p for p in paths if p.startswith('lua/')],
    }.items():
        selected = sorted(set(selected))
        inventories[route] = [b.observe(path, 'file:bounded-investigation', {
            'route': route, 'method': 'raw declaration/consumer inventory',
            'line_count': len(texts[path].splitlines()),
            'boundary': 'Static snapshot; runtime state, loader winner and engine implementations are not supplied.'}) for path in selected]
    consumer_refs = {p: b.observe(p, 'file:semantic-consumer', {'raw': texts[p]})
                     for p in (MENU, GROUPS, CLOTHING, EAT, CRAFT, COOK, FIX, MOVE, PROPS, MOVE_ACTION, WEAR, READ, DRY, DRINK, TRANSFER, SKILLS,
                               BUILD, STAGE, BUILD_ACTION, BUILD_UTIL, BUILD_OBJECT, WALL, FURNITURE, SHOTGUN, BANDAGE, DYE, PILLS)}
    callback_refs = defaultdict(list)
    for path in (GROUPS, SHOTGUN):
        clean = reader.mask(texts[path], lua=True)
        for name in re.findall(r'^function\s+([\w.]+)\s*\(', clean, re.M):
            callback_refs[name].append(consumer_refs[path])
    callback_defs = set(callback_refs)
    action_names = set(re.findall(r'\b(IS\w+):new\(', reader.mask(texts[MENU], lua=True)))
    for path in paths:
        if Path(path).stem in action_names and path not in consumer_refs:
            consumer_refs[path] = b.observe(path, 'file:semantic-consumer', {'raw': texts[path]})
    action_analysis = {name: {'state': 'investigated_unresolved' if name in meaning.ACTION_READINGS else 'not_investigated',
                             'finding': meaning.ACTION_READINGS.get(name, 'Source available; caller/action semantic investigation remains unfinished.'),
                             'source_paths': [p for p in paths if Path(p).stem == name],
                             'observation_refs': [consumer_refs[p] for p in paths if Path(p).stem == name] + [consumer_refs[MENU]]}
                       for name in sorted(action_names)}
    index = inv.read_json(root / 'Iris/input/recipes_index_full.json')['items']
    skill_names = set(re.findall(r'SkillBook\["([^"]+)"\]\.perk\s*=\s*Perks\.\w+', reader.mask(texts[SKILLS], lua=True)))
    recipes, recipe_opaque, recipe_findings = defaultdict(list), [], {}
    for record in records:
        if record['kind'] != 'recipe': continue
        participants, opaque = reader.recipe_participants(record, fields, group_defs)
        recipe_findings[record_refs[id(record)]] = meaning.recipe_analysis(record, participants, callback_defs, callback_refs)
        if opaque: recipe_opaque.append({'observation_ref': record_refs[id(record)], 'clauses': opaque})
        for participant in participants:
            if participant['item_id'] in target_ids:
                recipes[participant['item_id']].append({**participant, 'record': record,
                                                       'observation_ref': record_refs[id(record)]})
    evolved = defaultdict(list)
    for record in records:
        if record['kind'] == 'evolvedrecipe': evolved[record['name']].append(record)
    fixing = defaultdict(list)
    stages = defaultdict(list)
    building_candidates = defaultdict(list)
    function = None
    for line, text in enumerate(reader.mask(texts[BUILD], lua=True).splitlines(), 1):
        match = re.search(r'(ISBuildMenu\.\w+)\s*=\s*function', text)
        if match: function = match[1]
        for match in re.finditer(r'\["(?:need|use):([\w.]+)"\]\s*=\s*(.+)', text):
            if match[1] in target_ids:
                building_candidates[match[1]].append(b.observe(BUILD, f'L{line}:{function}',
                    {'raw': text.strip(), 'factory': function,
                     'interpretation': 'Declared construction requirement. Shared consumeMaterial removes required inventory/ground items or uses. Branch reachability and the specific object factory remain prerequisites, so this is not a universal material role.'}))
    for record in records:
        if record['kind'] != 'multistagebuild': continue
        values = reader.properties(record, ':')
        for role, key in (('material', 'ItemsRequired'), ('tool', 'ItemsToKeep')):
            for value in values.get(key, []):
                for token in value.split(';'):
                    item = reader.qualify(record['module'], token.split('=')[0].strip())
                    if item in target_ids:
                        stages[item].append({'role': role, 'observation_ref': record_refs[id(record)],
                                             'clause': value, 'previous_stages': values.get('PreviousStage', []),
                                             'skill': values.get('SkillRequired', [])})
    for record in records:
        if record['kind'] != 'fixing': continue
        values = reader.properties(record, ':')
        for role, key in (('repair_target', 'Require'), ('repair_material', 'Fixer')):
            for value in values.get(key, []):
                tokens = value.split(';') if role == 'repair_target' else [value.split(';')[0].split('=')[0]]
                for token in tokens:
                    item = reader.qualify(record['module'], token.strip())
                    if item in target_ids:
                        fixing[item].append({'role': role, 'observation_ref': record_refs[id(record)], 'clause': value})
    # Independently reverse-index every literal in the bound action source set.
    # Hits are attempts, never automatic facts or proof that an absent hit means N/A.
    token_items = defaultdict(set)
    for item in target_ids:
        for token in {item, item.split('.', 1)[1], *(fields.get(item) or {}).get('Tags', '').split(';')}:
            if token: token_items[token].add(item)
    lua_hits = defaultdict(list)
    for path in paths:
        if not path.startswith('lua/'): continue
        for hit in reader.literal_hits(texts[path], set(token_items)):
            ref = b.observe(path, f"L{hit['line']}:literal:{hit['token']}", hit)
            for item in token_items[hit['token']]: lua_hits[item].append(ref)
    attempts, application_inputs, pending, results, universe = {}, [], [], [], []
    aid = 'iris-layer3-semantic-results-1'
    axes = {a['axis_id']: a for a in contract['axes']}
    baseline_pending = sum(len(row['pending_scope_refs']) for row in baseline)
    baseline_keys = sum(sum(a['axis_id'] != 'acquisition' for a in row['required_axes']) for row in baseline)
    inv.require(baseline_keys == 8882 and len(baseline) == 2105, 'baseline universe drift')
    for prior in baseline:
        item = prior['item_id']
        raw = raw_items.get(item, [])
        f = fields.get(item) or {}
        native_refs = [record_refs[id(r)] for r in raw]
        links = recipes[item]
        cooking_refs = []
        for entry in f.get('EvolvedRecipe', '').split(';'):
            name = entry.split(':')[0].strip()
            cooking_refs.extend(record_refs[id(r)] for r in evolved.get(name, []))
        base_refs = [record_refs[id(r)] for rows in evolved.values() for r in rows
                     if any(reader.qualify(r['module'], value) == item
                            for key, vals in reader.properties(r, ':').items() if key in {'BaseItem', 'ResultItem'} for value in vals)]
        per_route = {}
        native_boundary = ('loader_or_declaration_identity' if len(raw) != 1 or fields.get(item) is None else {
            'Food': 'IsoGameCharacter.Eat_and_OnEat_dispatch',
            'Weapon': 'HandWeapon_attack_reload_and_character_state',
            'Clothing': 'Clothing_protection_insulation_and_body_state',
            'Literature': 'ISReadABook_SkillBook_and_ReadLiterature',
            'Container': 'ItemContainer_capacity_and_transfer_state',
            'Drainable': 'DrainableComboItem.Use_and_device_specific_consumers',
        }.get(f.get('Type'), 'engine_state_semantics'))
        for route, matching, finding, dependency in (
            ('A', native_refs, {'declarations': len(raw), 'fields': f, 'type_consumer': f.get('Type'),
                               'duplicate_properties': bool(raw and fields.get(item) is None),
                               'interpretation': {'Food': meaning.ACTION_READINGS['ISEatFoodAction'], 'Literature': meaning.ACTION_READINGS['ISReadABook'],
                                  'Clothing': meaning.ACTION_READINGS['ISWearClothing'], 'Container': meaning.ACTION_READINGS['ISInventoryTransferAction'],
                                  'Weapon': meaning.ACTION_READINGS['ISReloadWeaponAction'], 'Drainable': meaning.ACTION_READINGS['ISConsolidateDrainable']}.get(f.get('Type'),
                                  'No native engine consumer supplied for this declaration kind; the independent property/callback paths are examined under E. Identity conflicts preserve all candidates.')}, native_boundary),
            ('B', [r['observation_ref'] for r in links] + [group_refs[r['group']] for r in links if r['group'] in group_refs],
             {'participants': [{k: v for k, v in r.items() if k != 'record'} for r in links],
              'recipe_interpretation_refs': sorted({r['observation_ref'] for r in links}),
              'index_comparison': {
                  'seed_rows': index.get(item, []),
                  'raw_rows': sorted({(r['record']['path'], r['record']['name'], r['role']) for r in links}),
                  'raw_absent_from_seed': sorted({(Path(r['record']['path']).name, r['record']['name'], r['role']) for r in links}
                      - {(r['source'], r['recipe'], r['role']) for r in index.get(item, [])}),
                  'seed_without_raw_match': [r for r in index.get(item, []) if not any(Path(link['record']['path']).name == r['source'] and link['record']['name'] == r['recipe'] and link['role'] == r['role'] for link in links)],
                  'comparison_limit': 'Exact source basename/name/role seed comparison; repeated raw definitions and source clauses remain distinct observations.'},
              'opaque_group_inventory': 'parser_limits/recipe_opaque', 'index_is_search_seed_only': True}, 'RecipeManager_and_opaque_callbacks'),
            ('C', native_refs + cooking_refs + base_refs,
             {'declared_entries': f.get('EvolvedRecipe'), 'base_or_result_refs': base_refs,
              'consumer': 'getItemsCanBeUse / needToBeCooked / addItem; frozen and poison filters'}, 'EvolvedRecipe_runtime_eligibility'),
            ('D', [r['observation_ref'] for r in fixing[item] + stages[item]] + building_candidates[item] + native_refs,
             {'fixing': fixing[item], 'stages': stages[item], 'building_candidates': building_candidates[item], 'moveable_tools': prior_evidence[item]['moveable_tools'],
              'consumer': 'FixingManager repair; moveable hasTool/object predicates; stage doStage followed by consumption of required items/uses, subject to previous stage, tools and skill.'}, 'FixingManager_stage_engine_and_world_object_state'),
            ('E', lua_hits[item] + native_refs,
             {'literal_refs': sorted(set(lua_hits[item])), 'type': f.get('Type'), 'tags': f.get('Tags'),
              'predicate_evaluation': reader.selected_item_predicates(texts[MENU], item, fields.get(item)),
              'replacement_chain': meaning.replacement_chain(item, fields),
              'action_interpretation_refs': sorted(action_analysis),
              'menu_interpretation': meaning.MENU_READINGS,
              'consumer': 'inventory native/property branches and called actions; exact literal search is not complete dispatch'},
             'runtime_predicate_and_indirect_dispatch'),
        ):
            # Shared route inventory is referenced once by its route key.
            refs = sorted(set(matching + [inventories[route][0]]))
            unfinished = []
            if route == 'B':
                unfinished = sorted({name for link in links for name in recipe_findings[link['observation_ref']]['unfinished_callbacks']})
            elif route == 'E':
                unfinished = [name for name, row in action_analysis.items() if row['state'] == 'not_investigated']
            attempt_id = identity('attempt', [item, route, refs, finding])
            attempts[attempt_id] = {'item_id': item, 'route': route, 'observation_refs': refs,
                'method': 'reverse raw participation + source consumer boundary analysis', 'finding': finding,
                'coverage_ref': route,
                'dependency': dependency, 'state': 'not_investigated' if unfinished else 'investigated_unresolved',
                'unfinished_semantic_paths': unfinished,
                'limit': 'No execution of dynamic predicate; no global negative from static absence.'}
            per_route[route] = attempt_id
        routes = [dict(r) for route in prior['routing'] for r in route['observations']]
        profile_routes = {r['profile_id']: r for r in routes}
        # Existing definition, additional instances: group/result, fixing and base
        # participation open its questions without rewriting L3-02 routing rules.
        construction_material = item in {'Base.Plank', 'Base.Nails', 'Base.Log', 'Base.RippedSheets', 'Base.RippedSheetsDirty', 'Base.Twine', 'Base.Rope'}
        construction_tool = 'Hammer' in f.get('Tags', '').split(';')
        newly = {'crafting': bool(links), 'cooking': bool(cooking_refs or base_refs), 'world_work': bool(fixing[item] or stages[item] or construction_material or construction_tool)}
        for profile, applicable in newly.items():
            if applicable and profile_routes[profile]['state'] != 'confirmed_applicable':
                r = profile_routes[profile]
                r.update(state='confirmed_applicable', scope_refs=[next(p for p in contract['profiles'] if p['profile_id'] == profile)['routing']['scope']],
                         evidence_refs=[per_route[{'crafting': 'B', 'cooking': 'C', 'world_work': 'D'}[profile]]],
                         reason='Raw reverse participation confirms this existing question instance; semantic completion remains separate.')
        for old_pending in prior['pending_scope_refs']:
            profile = old_pending['profile_id']
            route = {'crafting': 'B', 'cooking': 'C', 'world_work': 'D', 'direct': 'E'}.get(profile, 'A')
            pending.append({'item_id': item, 'profile_id': profile,
                            'before': old_pending, 'attempt_refs': [per_route[route]],
                            'disposition': ('not_investigated' if attempts[per_route[route]]['state'] == 'not_investigated' else
                                            'applicable' if profile_routes[profile]['state'] == 'confirmed_applicable' else 'pending_with_blocker'),
                            'dependency': attempts[per_route[route]]['dependency']})
        refs = native_refs + [consumer_refs[MENU]]
        if len(raw) == 1 and fields.get(item) is not None:
            for flag, rule, action, function, predicate in (
                ('CanBandage', 'bandaging', BANDAGE, 'apply_bandage', 'A body part is eligible for bandaging; the material remains in inventory and the patient does not move out of reach.'),
                ('HairDye', 'hair_dye', DYE, 'dye_hair_or_beard', 'The dye remains in inventory; hair exists and is not Bald, or the beard model exists and is nonempty.'),
            ):
                if f.get(flag, '').lower() == 'true':
                    fid = b.fact(item, 'direct_function', {'function': function}, refs + [consumer_refs[action]], rule, ['item:direct'])
                    b.fact(item, 'condition', {'predicate': predicate}, refs + [consumer_refs[action]], rule, ['item:direct'], applies_to_fact_refs=[fid])
            if item.split('.', 1)[1].startswith('Pills'):
                fid = b.fact(item, 'direct_function', {'function': 'take_pills'}, refs + [consumer_refs[PILLS]], 'pill_taking', ['item:direct'])
                b.fact(item, 'condition', {'predicate': 'The selected pills remain in inventory while taking them.'}, refs + [consumer_refs[PILLS]], 'pill_taking', ['item:direct'], applies_to_fact_refs=[fid])
            if f.get('Type') == 'Drainable' and f.get('IsWaterSource', '').lower() == 'true':
                source_refs = refs + [consumer_refs[DRINK]]
                scopes = ['item:direct', 'activity:expenditure']
                function = b.fact(item, 'direct_function', {'function': 'drink_stored_water'}, source_refs, 'drinking_water', scopes)
                thirst = b.fact(item, 'effect', {'property': 'thirst', 'direction': 'decrease'}, source_refs, 'drinking_water', scopes)
                poison = b.fact(item, 'effect', {'property': 'poison_level', 'direction': 'increase'}, source_refs, 'drinking_water', scopes)
                b.fact(item, 'condition', {'predicate': 'For water with remaining portions: manual drinking is offered above thirst 0.1; consumed portions require positive thirst and the container to remain in inventory.'},
                       source_refs, 'drinking_water', scopes, applies_to_fact_refs=[function, thirst, poison])
                b.fact(item, 'condition', {'predicate': 'The consumed water is tainted, current poison level is below 20, and current sickness is below 0.3.'},
                       source_refs, 'drinking_water', scopes, applies_to_fact_refs=[poison])
            if f.get('Type') == 'Literature' and f.get('CanBeWrite', '').lower() != 'true':
                source_refs = refs + [consumer_refs[READ]]
                function = b.fact(item, 'direct_function', {'function': 'read_literature'}, source_refs, 'reading', ['activity:reading'])
                b.fact(item, 'condition', {'predicate': 'The character can read, is awake, meets any book skill requirement, and the reading action remains valid for possession, page state and driving state.'},
                       source_refs, 'reading', ['activity:reading'], applies_to_fact_refs=[function])
                if f.get('SkillTrained') in skill_names and f.get('NumberOfPages', '').isdigit() and int(f['NumberOfPages']) > 0:
                    source_refs += [consumer_refs[SKILLS]]
                    effect = b.fact(item, 'effect', {'property': f['SkillTrained'] + '_experience_multiplier', 'direction': 'increase'},
                                    source_refs, 'reading', ['activity:reading'])
                    b.fact(item, 'condition', {'predicate': 'Reading progress yields a multiplier above the current one, and the reader is within this book\'s supported training level range.'},
                           source_refs, 'reading', ['activity:reading'], applies_to_fact_refs=[effect])
                    b.fact(item, 'condition', {'predicate': 'The character can read, is awake, meets any book skill requirement, and the reading action remains valid for possession, page state and driving state.'},
                           source_refs, 'reading', ['activity:reading'], applies_to_fact_refs=[effect])
            if f.get('Type') == 'Container' and f.get('Capacity', '').isdigit() and int(f['Capacity']) > 0:
                source_refs = refs + [consumer_refs[TRANSFER]]
                function = b.fact(item, 'direct_function', {'function': 'store_and_retrieve_items'}, source_refs, 'storage', ['activity:storage'])
                b.fact(item, 'condition', {'predicate': 'Storage requires room and item admission; transfer requires accessible distinct source/destination, permitted removal and applicable multiplayer restrictions.'},
                       source_refs, 'storage', ['activity:storage'], applies_to_fact_refs=[function])
            if (f.get('Type') == 'Food' and f.get('CantEat', '').lower() != 'true'
                  and not f.get('CustomContextMenu') and not f.get('CustomMenuOption')
                  and re.fullmatch(r'-\d+(?:\.\d+)?', f.get('HungerChange', ''))):
                function = b.fact(item, 'direct_function', {'function': 'eat_food'}, refs + [consumer_refs[EAT]],
                                  'native_eating', ['activity:ingestion'])
                b.fact(item, 'condition', {'predicate': 'Food is in inventory; any required companion item is present; satiety permits starting the eating action.'},
                       refs + [consumer_refs[EAT]], 'native_eating', ['activity:ingestion'], applies_to_fact_refs=[function])
            if f.get('Type') == 'Clothing' and f.get('BodyLocation'):
                function = b.fact(item, 'direct_function', {'function': 'wear_on_body'}, refs + [consumer_refs[WEAR]],
                                  'wearing', ['activity:wearing'])
                b.fact(item, 'condition', {'predicate': 'The clothing is in the character inventory and is worn at its configured body location.'},
                       refs + [consumer_refs[WEAR]], 'wearing', ['activity:wearing'], applies_to_fact_refs=[function])
            if f.get('Type') == 'Literature' and f.get('CanBeWrite', '').lower() == 'true':
                function = b.fact(item, 'direct_function', {'function': 'record_written_notes'}, refs, 'writing', ['activity:reading', 'item:direct'])
                b.fact(item, 'constraint', {'predicate': 'Editing needs an available writing implement and must not be locked by another user.'},
                       refs, 'writing', ['activity:reading', 'item:direct'], applies_to_fact_refs=[function])
            if item in {'Base.BathTowel', 'Base.DishCloth'}:
                function = b.fact(item, 'direct_function', {'function': 'dry_the_body'}, refs + [consumer_refs[DRY]], 'drying', ['item:direct'])
                effect = b.fact(item, 'effect', {'property': 'body_wetness', 'direction': 'decrease'}, refs + [consumer_refs[DRY]], 'drying', ['item:direct'])
                b.fact(item, 'condition', {'predicate': 'The body is wet, the towel has uses remaining, and the towel is in inventory.'},
                       refs + [consumer_refs[DRY]], 'drying', ['item:direct'], applies_to_fact_refs=[function, effect])
            if cooking_refs:
                b.activity(item, 'food_preparation', 'ingredient', refs + cooking_refs + [consumer_refs[COOK]], 'cooking_ingredient',
                           ['activity:cooking'], 'Only where the recipe accepts the ingredient, with its cooked/frozen and other eligibility requirements satisfied.')
            if prior_evidence[item]['moveable_tools']:
                b.activity(item, 'moving_furniture', 'tool', refs + [consumer_refs[MOVE], consumer_refs[PROPS], consumer_refs[MOVE_ACTION]],
                           'moving', ['activity:world_work'], 'The object requests this tool; inventory, reachability, world object and multiplayer permission checks must hold.')
            for repair in fixing[item]:
                b.activity(item, 'repair', repair['role'], refs + [repair['observation_ref'], consumer_refs[FIX]], 'repair',
                           ['activity:world_work'], 'For a compatible damaged item and available repair materials; repair eligibility and outcome depend on the fixing rules.')
            for stage in stages[item]:
                b.activity(item, 'construction', stage['role'], refs + [stage['observation_ref'], consumer_refs[BUILD], consumer_refs[STAGE], consumer_refs[BUILD_UTIL]],
                           'construction', ['activity:world_work'], 'Only for a compatible previous construction stage, with required skills, tools and materials available; material consumption excludes construction cheat mode.')
            if construction_material or construction_tool:
                predicate = ('For the active wooden-cross branch, the hammer is not broken and world placement/material requirements hold.' if construction_tool else
                             'For the active wooden-cross or log-wall branch requiring this material; log-wall binding chooses sufficient sheets (clean/dirty), otherwise twine, otherwise rope. World placement and material availability must hold; cheat mode does not consume material.')
                b.activity(item, 'construction', 'tool' if construction_tool else 'material',
                           refs + [consumer_refs[p] for p in (BUILD, BUILD_ACTION, BUILD_UTIL, BUILD_OBJECT, WALL, FURNITURE)],
                           'construction', ['activity:world_work'], predicate)
            for link in links:
                record = link['record']
                callbacks = reader.properties(record, ':').get('OnCreate', [])
                if callbacks == ['Recipe.OnCreate.RipClothing'] and link['role'] == 'input':
                    b.activity(item, 'fabric_recovery', 'material', refs + [link['observation_ref'], consumer_refs[GROUPS], consumer_refs[CLOTHING], consumer_refs[CRAFT]],
                               'fabric_recovery', ['activity:crafting'], 'An eligible fabric or named sheet is supplied to the recipe; recovered material and quantity depend on fabric, covered parts, dirt/blood and tailoring state.')
                if (item == 'Base.Battery' and callbacks == ['Recipe.OnCreate.TorchBatteryInsert'] and link['role'] == 'destroy'
                        and reader.properties(record, ':').get('Result') in (['Torch'], ['HandTorch'], ['Rubberducky2'])):
                    b.activity(item, 'portable_device_power', 'power_supply', refs + [link['observation_ref'], consumer_refs[GROUPS], consumer_refs[CRAFT]],
                               'battery_supply', ['activity:crafting'], 'A compatible empty flashlight or duck device is supplied; transferred charge is the charge remaining in the battery selected by the recipe.')
                if record['name'] in WOOD_RECIPES and link['role'] in {'input', 'keep'}:
                    source_refs = refs + [link['observation_ref'], consumer_refs[CRAFT]]
                    if link['group']: source_refs.append(group_refs[link['group']])
                    b.activity(item, 'woodworking', 'tool' if link['role'] == 'keep' else 'material', source_refs, 'woodwork',
                               ['activity:crafting'], 'A supported woodworking transformation must have its inputs, tools, skill and recipe eligibility requirements satisfied.')
        gap = {**prior_evidence[item]['gap'], 'evidence_refs': list(per_route.values()),
               'missing': 'See per-route semantic findings and unfinished paths; dynamic dispatch, engine interpretation and runtime object/character state remain open.',
               'next': 'Resolve the named per-route dependencies before claiming exhaustive direct behavior or item completion.'}
        application_inputs.append({'item_id': item, 'routes': routes, 'gap': gap})
        required = defaultdict(set)
        for route in routes:
            profile = next(p for p in contract['profiles'] if p['profile_id'] == route['profile_id'])
            for scope in route['scope_refs']:
                for axis in profile['required_axes']:
                    if axis != 'acquisition': required[(item, axis, scope)].add(profile['profile_id'])
        old_keys = {(item, a['axis_id'], a['scope_ref']) for a in prior['required_axes'] if a['axis_id'] != 'acquisition'}
        for key, contributors in sorted(required.items()):
            route = {'activity:crafting': 'B', 'activity:cooking': 'C', 'activity:world_work': 'D', 'item:direct': 'E'}.get(key[2], 'A')
            attempt = attempts[per_route[route]]
            pid = b.explain(item, 'investigation', attempt['observation_refs'],
                            'Investigated bound static participation and consumer; ' + attempt['dependency'] + ' prevents whole-question closure.')
            result = {'item_id': item, 'axis_id': key[1], 'scope_ref': key[2], 'question_key': list(key),
                'authority_ref': aid, 'registry_revision': contract['revision'], 'state': attempt['state'],
                'attempt_refs': [per_route[route]], 'provenance_refs': [pid], 'fact_refs': [],
                'question_coverage': 'partial', 'blockers': [attempt['dependency']],
                'next_source_dependency': attempt['dependency'], 'transition_reason': 'Performed raw/source-consumer investigation; partial facts do not close scope.'}
            if attempt['state'] == 'not_investigated':
                result['not_investigated_reason'] = 'Available semantic paths still require interpretation: ' + ', '.join(attempt['unfinished_semantic_paths'])
            # CantEat excludes exactly the native eating channel in this form.
            # Transformation and residual direct questions are deliberately separate.
            if len(raw) == 1 and fields.get(item) and f.get('Type') == 'Food' and f.get('CantEat', '').lower() == 'true' and key[2] == 'activity:ingestion' and key[1] in {'operation', 'effects'}:
                result.update(state='evidence_backed_not_applicable', question_coverage='whole_scope',
                    coverage_justification='The explicit CantEat flag blocks entry to the native eating branch for this form; this closes only that channel.',
                    negative_scope=list(key), scope_complete=True, exclusion_predicate='unique Food declaration AND CantEat=true excludes native eating in current form',
                    closed_source_refs=[raw[0]['path'], MENU], blockers=[], next_source_dependency=None)
            results.append(result)
            universe.append({'question_key': list(key), 'relation': 'retained' if key in old_keys else 'newly_required',
                             'before_revision': contract['revision'], 'after_revision': contract['revision'],
                             'before_readpoint': definition, 'after_authority': aid, 'contributors': sorted(contributors),
                             'finding_refs': [per_route[route]]})
        inv.require(old_keys <= required.keys(), 'producer lost original question')
    bindings = []
    facts = sorted(b.facts.values(), key=lambda f: f['fact_id'])
    for fact in facts:
        fact['provenance_refs'].sort()
        for result in results:
            if (result['item_id'] == fact['item_id'] and result['scope_ref'] in b.fact_scopes[fact['fact_id']]
                    and fact['fact_kind'] in axes[result['axis_id']]['allowed_result_kinds']):
                bindings.append({'question_key': result['question_key'], 'fact_ref': fact['fact_id'],
                                 'authority_ref': aid, 'registry_revision': contract['revision'], 'contribution': 'partial'})
    anomaly_ids = ['Base.Bag_PistolCase', 'Base.Lemongrass', 'Base.NoiseMaker', 'Base.ShotgunCase1']
    anomaly_search = defaultdict(list)
    for item in anomaly_ids:
        token = item.split('.', 1)[1]
        for path in paths:
            if not path.startswith('scripts/'): continue
            for line, text in enumerate(texts[path].splitlines(), 1):
                if token.casefold() in text.casefold():
                    anomaly_search[item].append(b.observe(path, f'L{line}:near-name-search',
                        {'raw': text, 'search_token': token, 'alias_inferred': False}))
    anomalies = [{'item_id': item, 'raw_candidates': [record_refs[id(r)] for r in raw_items.get(item, [])],
                  'search_refs': sorted(set(lua_hits[item] + anomaly_search[item])), 'disposition': 'investigated_unresolved',
                  'reason': 'Duplicate declarations: no bound loader winner.' if len(raw_items.get(item, [])) > 1 else 'Exact declaration absent; similar spelling/model/display token is not an alias.',
                  'next': 'Obtain exact declaration and loader/build correspondence; preserve case-sensitive target.',
                  'affected_attempt_refs': [key for key, a in attempts.items() if a['item_id'] == item]}
                 for item in anomaly_ids]
    return {'schema_version': SCHEMA, 'status': 'candidate', 'authority_id': aid,
            'registry_revision': contract['revision'], 'definition_readpoint': definition, 'inherits': contract['inherits'],
            'target_ids': target_ids, 'target_set_sha256': inv.set_digest(target_ids),
            'baseline_key_count': baseline_keys, 'baseline_pending_count': baseline_pending,
            'source_bindings': sources, 'source_snapshot': contract['snapshot'],
            'source_capability': {route: {'source_observation_refs': refs, 'status': 'partial',
                'negative_limit': 'Only explicit native CantEat closure; absence never establishes global negative.',
                'available_membership': 'all attempts with this route, their item question keys and pending profiles',
                'missing_dependency': 'Engine implementation, runtime predicate state, complete indirect dispatch and exact upstream build.'}
                for route, refs in inventories.items()},
            'rules': rule_records(), 'observations': b.observations, 'provenance': b.provenance, 'facts': facts,
            'source_interpretations': {'recipes': recipe_findings, 'actions': action_analysis,
                                       'callback_readings': meaning.CALLBACK_READINGS},
            'attempts': attempts, 'results': results, 'fact_question_bindings': bindings,
            'application_inputs': application_inputs, 'pending': pending, 'universe': universe, 'anomalies': anomalies,
            'parser_limits': {'recipe_opaque': recipe_opaque, 'groups': group_defs,
                'strings_comments': 'Lexically masked; repeated clauses and all declarations retained.',
                'group_expansion': 'Straight-line tag/type unions plus six reviewed fabric/type/name predicates; live registry additions and loader effects remain unresolved.'},
            'review': {'state': 'pending_content_audit', 'rules': sorted(RULES), 'samples': [],
                       'claim_ceiling': 'Unique rules and named samples only; no full-corpus semantic accuracy claim.'}}


def output_directory(root: Path, output: Path) -> Path:
    # Reject lexical escapes before resolving any out-of-repository target.
    inv.require(Path(os.path.abspath(output)).is_relative_to(root.resolve()), 'semantic output must remain in repository')
    resolved = output.resolve()
    inv.require(resolved.is_relative_to(root.resolve()), 'semantic output must remain in repository')
    allowed = [(root / '.tmp/semantic').resolve(), (root / ROOT).resolve()]
    inv.require(any(resolved == p or resolved.is_relative_to(p) for p in allowed), 'not a semantic candidate output root')
    inv.require(not resolved.exists() or not any(resolved.iterdir()), 'candidate output must be empty; never overwrite authority')
    return resolved


def load_manifest(root: Path, ref: dict, *, mode: str) -> tuple[dict, dict]:
    """Explicit candidate/adopted boundaries over the same immutable subject.

    Corpus lifecycle is candidate. Adoption is owned by the current route and
    its successful closeout, never by mutating the verified corpus bytes.
    """
    inv.require(mode in {'candidate', 'adopted'}, 'unknown semantic loading mode')
    manifest = inv.bound_json(root, ref)
    inv.require(manifest.get('schema_version') == 'iris-layer3-semantic-manifest-v1'
                and manifest.get('status') == 'adoption_subject', 'not a semantic manifest')
    members = {m['path']: m for m in manifest['members']}
    inv.require(len(members) == len(manifest['members']) and manifest['corpus']['path'] in members,
                'missing/duplicate corpus member')
    for member in members.values():
        inv.require(inv.binding(root, member['path']) == member, 'semantic member drift')
    inv.require(manifest['corpus'] == members[manifest['corpus']['path']], 'corpus binding mismatch')
    payload = inv.bound_json(root, manifest['corpus'])
    inv.require(payload.get('status') == 'candidate' and payload['definition_readpoint'] == manifest['definition_readpoint'],
                'invalid immutable candidate/definition')
    definition = inv.bound_json(root, manifest['definition_readpoint'])
    for member in definition['members']:
        inv.require(inv.binding(root, member['path']) == member, 'definition member drift')
    for source in payload['source_bindings']:
        inv.require(inv.binding(root, source['path']) == source, 'semantic source drift')
    if mode == 'adopted':
        route = inv.read_json(root / 'Iris/_docs/authority/iris_current_route_index.json').get(ENTRY, {})
        inv.require(route.get('state') == 'adopted' and route.get('manifest_path') == ref['path']
                    and route.get('manifest_sha256') == ref['sha256'], 'unadopted semantic readpoint')
        closeout = inv.local_path(root, route['adoption_result']).read_text(encoding='utf-8')
        inv.require('G1_EXIT_CODE=0' in closeout and ref['sha256'] in closeout, 'missing exact successful adoption record')
        payload = {**payload, 'status': 'adopted'}
    return manifest, payload


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='iris-tooling build layer3 semantic-results')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    from iris_tooling.build.repository_context import require_repository_context
    root = require_repository_context().repository_root
    directory = output_directory(root, args.output)
    payload = prepare(root)
    directory.mkdir(parents=True, exist_ok=True)
    inv.write_json(directory / 'corpus.json', payload)
    print(json.dumps({'status': 'candidate', 'targets': len(payload['target_ids']),
                      'facts': len(payload['facts']), 'questions': len(payload['results']),
                      'pending': len(payload['pending']), 'output': str(directory)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
