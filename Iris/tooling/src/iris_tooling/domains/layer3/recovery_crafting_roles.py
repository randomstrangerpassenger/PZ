"""Crafting-family fact recovery over the shared source indexes."""
from collections import defaultdict
import re
from . import source_reader as reader
from . import semantic_results as semantic
from . import investigation as inv
from .recovery_vocabulary import BAKING, BATTER_TEST, BUILD_CLASSES, SPEAR_ATTACHMENTS, SPEAR_CONDITIONS, SPEAR_STONE_LOSS, SPEAR_TOOL_WEAR, WELDING_CONSTRUCTION, WELDING_MENU
from .recovery_source_index import recipe_participants


def baking_roles(builder, recipes, fields, groups, targets, declaration, refs):
    mixing = 'keep Spatula/[Recipe.GetItemTypes.Spoon]/[Recipe.GetItemTypes.Fork]'
    cooking = ['Time:50.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking10']
    entries = [
        ('Make Cake Batter', 'batter_preparation', [mixing, 'Bowl', '[Recipe.GetItemTypes.Flour]=2', '[Recipe.GetItemTypes.BakingFat];15', '[Recipe.GetItemTypes.Sugar];10', '[Recipe.GetItemTypes.Egg]=2', 'Yeast', '[Recipe.GetItemTypes.Milk];5', 'Result:CakeBatter', 'NeedToBeLearn:true', *cooking, 'OnTest:Recipe.OnTest.WholeEgg']),
        ('Make Pie Dough', 'dough_preparation', [mixing, 'keep Bowl', 'Water=2', '[Recipe.GetItemTypes.Flour]=2', 'Butter/Lard/Margarine;15', 'Salt;2', 'Result:PieDough', 'NeedToBeLearn:true', *cooking]),
        ('Make Pizza', 'dough_preparation', [mixing, 'keep Bowl', 'keep RollingPin', 'Water=3', '[Recipe.GetItemTypes.Flour]=2', 'Salt;2', 'Yeast', '[Recipe.GetItemTypes.Oil];3', 'Cheese;15', '[Recipe.GetItemTypes.PizzaSauce];15', 'Result:PizzaRecipe', 'NeedToBeLearn:true', *cooking]),
        ('Make Biscuits', 'dough_preparation', ['destroy MuffinTray', mixing, 'keep Bowl', 'Water=1', 'Flour=1', 'Salt;1', 'BakingSoda=1', '[Recipe.GetItemTypes.BakingFat];1', 'Result: Muffintray_Biscuit', 'NeedToBeLearn:true', 'Category:Cooking', 'Time:50']),
        ('Prepare Muffins', 'batter_preparation', [mixing, 'keep Bowl', 'destroy MuffinTray', '[Recipe.GetItemTypes.Egg]=2', '[Recipe.GetItemTypes.BakingFat];2', '[Recipe.GetItemTypes.Milk];5', '[Recipe.GetItemTypes.Sugar];5', '[Recipe.GetItemTypes.Flour]=2', 'Result:BakingTray_Muffin', 'Category:Cooking', 'Time:60', 'OnTest:Recipe.OnTest.WholeEgg']),
    ]
    for flour, result in (('[Recipe.GetItemTypes.Flour]=1', 'BreadDough'), ('Flour=1', 'BaguetteDough')):
        entries.append(('Make Bread Dough', 'dough_preparation', [mixing, 'keep Bowl', 'keep RollingPin', 'Water=1', flour, 'Salt;1', 'Yeast', 'Result:' + result, 'NeedToBeLearn:true', *cooking]))
    for name, activity, clauses in entries:
        matches = [r for r in recipes if r['path'] == 'scripts/recipes.txt' and r['module'] == 'Base'
                   and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        observation = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}",
                                      {'raw': record['raw'], 'clauses': record['clauses']})
        participants, _ = recipe_participants(record, fields, groups)
        for participant in participants:
            item, source_role = participant['item_id'], participant['role']
            if item not in targets or item not in fields or source_role == 'result':
                continue
            if item in {'Base.Bowl', 'Base.MuffinTray'}:
                role = 'container'
            elif source_role == 'keep' and (participant['clause'] == mixing or item == 'Base.RollingPin'):
                role = 'tool'
            elif source_role == 'input':
                role = 'ingredient'
            else:
                continue
            evidence = [declaration(item), observation, refs[semantic.GROUPS], refs[semantic.CRAFT]]
            builder.activity(item, activity, role, evidence, 'baking_preparation', ['activity:crafting'], BAKING)
            if activity == 'batter_preparation':
                context = next(f['fact_id'] for f in builder.facts.values()
                               if f['item_id'] == item and f['payload'] == {'activity': activity})
                builder.fact(item, 'condition', {'predicate': BATTER_TEST}, evidence, 'baking_preparation',
                             ['activity:crafting'], applies_to_fact_refs=[context])


def welding_roles(base, builder, fields, targets, declaration, refs, texts):
    entries = [
        ('onMetalShelves', 'ISSimpleFurniture', 'Containers', (2,1,0,0,1,2,2)),
        ('onMetalCrate', 'ISWoodenContainer', 'Containers', (2,2,2,0,1,2,4)),
        ('onMetalCounter', 'ISWoodenContainer', 'Containers', (2,4,0,2,0,2,5)),
        ('onMetalCounterCorner', 'ISWoodenContainer', 'Containers', (2,4,0,2,0,2,5)),
        ('onSmallLocker', 'ISWoodenContainer', 'Containers', (3,4,0,2,0,2,6)),
        ('onBigLocker', 'ISWoodenContainer', 'Containers', (8,4,0,2,0,3,9)),
        ('onMetalWallFrame', 'ISWoodenWall', 'Walls', (0,0,0,0,0,2,3,3)),
        ('onMetalFence', 'ISWoodenWall', 'Fences', (1,2,0,0,3,1,3)),
        ('onMetalPoleFence', 'ISWoodenWall', 'Fences', (3,0,0,0,0,1,3)),
        ('onWiredFence', 'ISWoodenWall', 'Fences', (2,0,0,0,1,1,4,0,1)),
        ('onBigWiredFence', 'ISWoodenWall', 'Fences', (3,0,0,0,4,1,5,0,3)),
        ('onBigMetalFence', 'ISWoodenWall', 'Fences', (5,0,0,0,2,2,7)),
        ('onFenceGate', 'ISWoodenDoor', 'Fences', (3,0,0,2,2,1,4)),
        ('onBigMetalFenceGate', 'ISWoodenDoor', 'Fences', (5,0,0,2,4,2,7)),
        ('onDoublePoleDoor', 'ISDoubleDoor', 'Fences', (10,0,0,2,4,2,8)),
        ('onDoubleMetalDoor', 'ISDoubleDoor', 'Fences', (8,0,0,2,2,2,7,0,4)),
        ('onMetalFloor', 'ISWoodenFloor', 'Roof', (0,1,0,0,1,1,0)),
    ]
    text = reader.mask(texts[WELDING_MENU], lua=True)
    inv.require('Events.OnFillWorldObjectContextMenu.Add(ISBlacksmithMenu.doBuildMenu)' in text
                and 'local disableFurnaceAnvil = true' in text
                and 'return math.floor((torchUses + 0.1) / 2)' in text, 'welding entry or use calculation changed')
    bodies = {m[1]: m[0] for m in re.finditer(r'^ISBlacksmithMenu\.(on\w+)\s*=\s*function\b.*?(?=^ISBlacksmithMenu\.|\Z)', text, re.M | re.S)}
    recovered = defaultdict(list)
    masks = {item for item, f in fields.items() if item == 'Base.WeldingMask' or 'WeldingMask' in f.get('Tags', '').split(';')}
    for name, constructor, group, params in entries:
        section = text.split('if playerObj:isRecipeKnown("Make Metal ' + group + '") or ISBuildMenu.cheat then', 1)[1]
        section = section.split('if playerObj:isRecipeKnown(', 1)[0]
        selection = re.search(r'ISBlacksmithMenu\.' + name + r',\s*player,\s*"(\d+)"', section)
        inv.require(selection is not None and int(selection[1]) == params[5], 'welding callback selection changed')
        menu = section[selection.start():].split(':addOption(', 1)[0]
        expected = ','.join(map(str, params[:7])) + ',playerObj,toolTip' + (',' + ','.join(map(str, params[7:])) if len(params) > 7 else '')
        inv.require('ISBlacksmithMenu.checkMetalWeldingFurnitures(' + expected + ')' in re.sub(r'\s+', '', menu), 'welding menu requirements changed')
        body = bodies[name]
        required = {token: int(n) for token, n in re.findall(r'\["need:(Base\.\w+)"\]\s*=\s*"(\d+)"', body)}
        supplied = dict(zip(('Base.MetalPipe','Base.SmallSheetMetal','Base.SheetMetal','Base.Hinge','Base.ScrapMetal'), params[:5]))
        if len(params) > 7:
            supplied['Base.MetalBar'] = params[7]
        inv.require(required == {k: v for k, v in supplied.items() if v} and constructor + ':new(' in body
                    and 'buildUtil.consumeMaterial(self)' in texts[BUILD_CLASSES[constructor]], 'welding material/constructor changed')
        inv.require(re.search(r'\["use:Base.BlowTorch"\]\s*=\s*torchUse', body) is not None
                    and re.search(r'\["use:Base.WeldingRods"\]\s*=\s*ISBlacksmithMenu.weldingRodUses\(torchUse\)', body) is not None
                    and re.search(r'\.firstItem\s*=\s*"BlowTorch"', body) is not None
                    and re.search(r'\.secondItem\s*=\s*"WeldingMask"', body) is not None, 'welding supplies/equipment changed')
        literal_uses = {token: int(n) for token, n in re.findall(r'\["use:(Base\.\w+)"\]\s*=\s*"(\d+)"', body)}
        inv.require(literal_uses == ({'Base.Wire': params[8]} if len(params) > 8 and params[8] else {}), 'welding wire requirement changed')
        participants = [(item, 'material', count, 'need') for item, count in required.items()]
        participants.extend((item, 'material', count, 'use') for item, count in literal_uses.items())
        participants.append(('Base.BlowTorch', 'tool', params[5], 'use'))
        rods = int((params[5] + 0.1) // 2)
        if rods:
            participants.append(('Base.WeldingRods', 'material', rods, 'use'))
        participants.extend((item, 'tool', 1, 'equipment') for item in masks)
        for item, role_name, count, operand in participants:
            if item not in targets or item not in fields:
                continue
            ref = builder.observe(WELDING_MENU, 'active factory:' + name + ':' + item,
                {'factory': 'ISBlacksmithMenu.' + name, 'body': body, 'menu': menu, 'learned_group': 'Make Metal ' + group,
                 'required_item': item, 'role': role_name, 'operand': operand, 'count': count,
                 'menu_parameters': list(params), 'constructor': constructor, 'consumer': BUILD_CLASSES[constructor]})
            evidence = [declaration(item), ref, refs[WELDING_MENU], refs[BUILD_CLASSES[constructor]],
                        refs[semantic.BUILD_OBJECT], refs[semantic.BUILD_ACTION], refs[semantic.BUILD_UTIL]]
            context = builder.fact(item, 'use_context', {'activity': 'metal_welding_construction'}, evidence, 'welding_construction', ['activity:world_work'])
            role = builder.fact(item, 'context_role', {'role': role_name}, evidence, 'welding_construction', ['activity:world_work'], context_fact_ref=context)
            builder.fact(item, 'condition', {'predicate': WELDING_CONSTRUCTION}, evidence, 'welding_construction', ['activity:world_work'], applies_to_fact_refs=[context, role])
            relation = {'item_id': item, 'factory': 'ISBlacksmithMenu.' + name, 'role': role_name, 'count': count,
                        'operand': operand, 'observation_ref': ref, 'role_fact_ref': role, 'evidence_refs': sorted(set(evidence)),
                        'omission_reason': 'The historical route D factory scan covered ISBuildMenu only; this active metal-welding menu was not included.',
                        'source_instance_kind': 'active_welding_participant'}
            recovered[item].append(relation)
            base['factory_relations'][item].append({**relation, 'status': 'active_welding', 'constructor': constructor,
                                                   'source_ref': base['reader'].bindings[WELDING_MENU]})
    return recovered


def spear_roles(base, builder, recipes, fields, groups, targets, declaration, refs):
    entries = [('Create Spear', 'spear_crafting', ['Plank/TreeBranch', 'keep [Recipe.GetItemTypes.SharpKnife]/SharpedStone/MeatCleaver',
        'Result:SpearCrafted', 'Time:100.0', 'OnCreate:Recipe.OnCreate.CreateSpear', 'Category:Survivalist', 'OnGiveXP:Recipe.OnGiveXP.WoodWork5'], None)]
    for name, attachment, result in SPEAR_ATTACHMENTS:
        entries.append(('Attach ' + name + ' to Spear', 'spear_upgrade', ['SpearCrafted', attachment, 'DuctTape=2',
            'Result:' + result, 'Time:100.0', 'OnCreate:Recipe.OnCreate.UpgradeSpear', 'Category:Survivalist'], attachment))
        entries.append(('Reclaim ' + name + ' from Spear', 'spear_reclaim', [result, 'Result:' + attachment,
            'OnCreate:Recipe.OnCreate.DismantleSpear', 'Time:60.0', 'Category:Survivalist', 'AllowDestroyedItem:true'], attachment))
    for name, activity, clauses, attachment in entries:
        matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        participants, opaque = reader.recipe_participants(record, fields, groups)
        if opaque:
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}",
            {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses})
        for participant in participants:
            item = participant['item_id']
            if item not in targets or item not in fields or participant['role'] not in {'input', 'keep'}:
                continue
            role = ('tool' if participant['role'] == 'keep' else 'material')
            if activity == 'spear_upgrade' and item == 'Base.' + attachment:
                role = 'attachment'
            elif activity == 'spear_reclaim':
                role = 'transformation_target'
            evidence = [declaration(item), ref, refs[semantic.GROUPS], refs[semantic.CRAFT]]
            builder.activity(item, activity, role, evidence, 'spear_crafting', ['activity:crafting'], SPEAR_CONDITIONS[activity])
            base.setdefault('spear_recipe_sources', {}).setdefault(item, []).append({'name': name, 'activity': activity, 'role': role, 'observation_ref': ref})
            if activity == 'spear_crafting' and role == 'tool':
                if fields[item].get('Type') == 'Weapon' and {'SmallBlade', 'LongBlade', 'Axe'} & set(fields[item].get('Categories', '').split(';')):
                    effect = builder.fact(item, 'effect', {'property': 'item_condition', 'direction': 'decrease'}, evidence,
                                          'spear_crafting', ['item:direct'])
                    builder.fact(item, 'condition', {'predicate': SPEAR_TOOL_WEAR}, evidence, 'spear_crafting',
                                 ['item:direct', 'activity:crafting'], applies_to_fact_refs=[effect])
                elif item == 'Base.SharpedStone':
                    effect = builder.fact(item, 'effect', {'property': 'inventory_presence', 'direction': 'remove'}, evidence,
                                          'spear_crafting', ['item:direct'])
                    builder.fact(item, 'condition', {'predicate': SPEAR_STONE_LOSS}, evidence, 'spear_crafting',
                                 ['item:direct', 'activity:crafting'], applies_to_fact_refs=[effect])
