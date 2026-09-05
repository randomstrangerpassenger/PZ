"""Reviewed bilingual realization of accepted propositions, never fact admission.

Unknown payloads fail closed. English predicates below are semantic selectors,
not predecessor prose. Neither profile names nor item names imply a function.
"""
from __future__ import annotations

from .investigation import require

LOCALES = ('ko', 'en')


def phrase(pair, locale):
    require(locale in LOCALES, 'unsupported locale; no fallback')
    return pair[LOCALES.index(locale)]


FUNCTIONS = {
    'apply_bandage': ('상처 부위에 붕대 재료로 댈 수 있다', 'It can be applied as a bandage'),
    'drink_stored_water': ('담긴 물을 마실 수 있다', 'The stored water can be drunk'),
    'dry_the_body': ('몸의 물기를 닦을 수 있다', 'It can be used to dry the body'),
    'dye_hair_or_beard': ('머리카락이나 수염을 염색할 수 있다', 'It can dye hair or a beard'),
    'eat_food': ('먹을 수 있다', 'It can be eaten'),
    'read_literature': ('읽을 수 있다', 'It can be read'),
    'record_written_notes': ('글을 적어 기록할 수 있다', 'It can hold written notes'),
    'store_and_retrieve_items': ('물건을 넣고 꺼낼 수 있다', 'Items can be stored in it and retrieved'),
    'take_pills': ('알약을 복용할 수 있다', 'The pills can be taken'),
    'wear_on_body': ('몸에 착용할 수 있다', 'It can be worn on the body'),
}

# All 21 accepted predicate branches are independently phrased in each locale.
PREDICATES = {
    'A body part is eligible for bandaging; the material remains in inventory and the patient does not move out of reach.':
        ('붕대를 댈 수 있는 신체 부위여야 하며, 재료가 소지품에 남아 있고 환자가 손이 닿는 범위를 벗어나지 않아야 한다', 'The body part must allow bandaging, the material must remain in inventory, and the patient must stay within reach'),
    'A compatible empty flashlight or duck device is supplied; transferred charge is the charge remaining in the battery selected by the recipe.':
        ('호환되는 빈 손전등이나 오리 모양 장치가 필요하며, 전달되는 충전량은 제작 과정에서 선택된 배터리의 남은 충전량이다', 'A compatible empty flashlight or duck device is needed; the charge transferred is the charge left in the battery selected during crafting'),
    'A supported woodworking transformation must have its inputs, tools, skill and recipe eligibility requirements satisfied.':
        ('해당 목공 작업의 재료·도구·기술과 제작 가능 조건을 충족해야 한다', 'The woodworking operation must meet its input, tool, skill and crafting eligibility requirements'),
    'An eligible fabric or named sheet is supplied to the recipe; recovered material and quantity depend on fabric, covered parts, dirt/blood and tailoring state.':
        ('사용 가능한 직물이나 지정된 시트가 필요하며, 회수되는 재료와 양은 직물·덮는 신체 부위·오염과 피·재봉 상태에 따라 달라진다', 'Eligible fabric or a specified sheet is needed; the recovered material and quantity depend on fabric, covered body parts, dirt, blood and tailoring state'),
    'Food is in inventory; any required companion item is present; satiety permits starting the eating action.':
        ('음식이 소지품에 있고 필요한 보조 물품을 갖추며, 포만 상태가 먹기 시작할 수 있는 상태여야 한다', 'The food must be in inventory, any required companion item must be present, and satiety must permit starting to eat'),
    'For a compatible damaged item and available repair materials; repair eligibility and outcome depend on the fixing rules.':
        ('호환되는 손상된 물품과 수리 재료가 필요하며, 수리 가능 여부와 결과는 해당 수리 규칙에 따라 달라진다', 'A compatible damaged item and available repair materials are needed; eligibility and results depend on the applicable repair rules'),
    'For the active wooden-cross branch, the hammer is not broken and world placement/material requirements hold.':
        ('나무 십자가를 만드는 해당 작업에서 망치가 부서지지 않았고 배치·재료 조건이 충족되어야 한다', 'For the applicable wooden-cross construction, the hammer must be unbroken and placement and material requirements must hold'),
    'For the active wooden-cross or log-wall branch requiring this material; log-wall binding chooses sufficient sheets (clean/dirty), otherwise twine, otherwise rope. World placement and material availability must hold; cheat mode does not consume material.':
        ('이 재료가 필요한 나무 십자가 또는 통나무 벽 작업에 해당한다. 통나무 벽을 묶을 때 충분한 깨끗한 시트나 더러운 시트를 먼저 사용하고, 없으면 노끈, 그다음 밧줄을 사용한다. 배치와 재료 확보 조건이 충족되어야 하며 치트 모드에서는 재료를 소모하지 않는다', 'This applies to wooden-cross or log-wall construction requiring this material. Log-wall binding uses sufficient clean or dirty sheets first, otherwise twine, otherwise rope. Placement and material availability must hold; cheat mode does not consume materials'),
    'For water with remaining portions: manual drinking is offered above thirst 0.1; consumed portions require positive thirst and the container to remain in inventory.':
        ('물이 남아 있어야 한다. 직접 마시기는 갈증 수치가 0.1을 넘을 때 가능하며, 실제 물을 마시려면 갈증이 0보다 크고 용기가 소지품에 남아 있어야 한다', 'Water must remain. Manual drinking is available above thirst 0.1; consuming water requires thirst above zero and the container to remain in inventory'),
    'Only for a compatible previous construction stage, with required skills, tools and materials available; material consumption excludes construction cheat mode.':
        ('건축 단계를 이어 진행할 때는 호환되는 이전 단계가 있고 필요한 기술·도구·재료를 갖추어야 하며, 건축 치트 모드에서는 재료를 소모하지 않는다', 'When continuing a construction stage, a compatible previous stage and the required skills, tools and materials are needed; construction cheat mode does not consume materials'),
    'Only where the recipe accepts the ingredient, with its cooked/frozen and other eligibility requirements satisfied.':
        ('해당 조리에서 받아들이는 재료여야 하며, 익힘·냉동 상태와 그 밖의 사용 조건을 충족해야 한다', 'The preparation must accept this ingredient, with cooked, frozen and other eligibility conditions satisfied'),
    "Reading progress yields a multiplier above the current one, and the reader is within this book's supported training level range.":
        ('독서 진도로 얻는 배율이 현재 배율보다 높고, 독자의 기술 수준이 이 책의 학습 범위 안에 있어야 한다', "Reading progress must yield a multiplier above the current one, and the reader must be within the book's supported training levels"),
    'Storage requires room and item admission; transfer requires accessible distinct source/destination, permitted removal and applicable multiplayer restrictions.':
        ('넣을 공간이 있고 해당 물건을 담을 수 있어야 한다. 옮길 때는 서로 다른 출발지와 목적지에 접근할 수 있고 꺼내기가 허용되며 멀티플레이 제한을 충족해야 한다', 'Storage needs room and item admission. Transfers need accessible, distinct source and destination containers, permitted removal and compliance with multiplayer restrictions'),
    'The body is wet, the towel has uses remaining, and the towel is in inventory.':
        ('몸이 젖어 있고 수건의 사용량이 남아 있으며 수건을 소지하고 있어야 한다', 'The body must be wet, and the towel must have uses remaining and be in inventory'),
    'The character can read, is awake, meets any book skill requirement, and the reading action remains valid for possession, page state and driving state.':
        ('글을 읽을 수 있고 깨어 있으며 책의 기술 요구를 충족해야 한다. 소지 여부·페이지 상태·운전 상태가 독서를 계속할 수 있는 조건이어야 한다', 'The reader must be literate, awake and meet any book skill requirement; possession, page state and driving state must allow reading to continue'),
    'The clothing is in the character inventory and is worn at its configured body location.':
        ('의류를 소지하고 해당 의류에 지정된 신체 부위에 착용해야 한다', 'The clothing must be in inventory and worn at its designated body location'),
    'The consumed water is tainted, current poison level is below 20, and current sickness is below 0.3.':
        ('마시는 물이 오염되어 있고 현재 중독 수치가 20 미만이며 질병 수치가 0.3 미만인 경우에 해당한다', 'This applies when the consumed water is tainted, current poison level is below 20 and sickness is below 0.3'),
    'The dye remains in inventory; hair exists and is not Bald, or the beard model exists and is nonempty.':
        ('염색약이 소지품에 남아 있고 대머리가 아닌 머리카락이 있거나 비어 있지 않은 수염이 있어야 한다', 'The dye must remain in inventory, with non-bald hair or an existing, nonempty beard'),
    'The object requests this tool; inventory, reachability, world object and multiplayer permission checks must hold.':
        ('해당 물체가 이 도구를 요구해야 하며, 소지 여부·접근 가능 여부·월드 물체 상태·멀티플레이 권한 조건을 충족해야 한다', 'The object must require this tool, and inventory, reachability, world-object and multiplayer permission checks must hold'),
    'The selected pills remain in inventory while taking them.':
        ('복용하는 동안 선택한 알약이 소지품에 남아 있어야 한다', 'The selected pills must remain in inventory while being taken'),
    'Editing needs an available writing implement and must not be locked by another user.':
        ('사용할 필기구가 필요하며 다른 사용자가 편집을 잠그지 않았어야 한다', 'Editing needs an available writing implement and must not be locked by another user'),
}

CONTEXTS = {
    'construction': ('건축 작업', 'construction'),
    'fabric_recovery': ('직물 회수', 'fabric recovery'),
    'food_preparation': ('음식 준비와 조리', 'food preparation'),
    'moving_furniture': ('가구 이동', 'moving furniture'),
    'portable_device_power': ('휴대 장치의 전원 공급', 'powering portable devices'),
    'repair': ('물품 수리', 'item repair'),
    'woodworking': ('목공 작업', 'woodworking'),
}
ROLES = {
    'ingredient': ('재료', 'an ingredient'), 'material': ('재료', 'a material'),
    'power_supply': ('전원', 'a power supply'), 'repair_material': ('수리 재료', 'a repair material'),
    'repair_target': ('수리 대상', 'an item to be repaired'), 'tool': ('도구', 'a tool'),
}
SKILLS = {
    'Blacksmith': ('대장장이', 'blacksmithing'), 'Carpentry': ('목공', 'carpentry'),
    'Cooking': ('요리', 'cooking'), 'Electricity': ('전기공학', 'electrical'),
    'Farming': ('농사', 'farming'), 'FirstAid': ('응급처치', 'first aid'),
    'Fishing': ('낚시', 'fishing'), 'Foraging': ('채집', 'foraging'),
    'Mechanics': ('차량 정비', 'mechanics'), 'MetalWelding': ('금속 용접', 'metalworking'),
    'Tailoring': ('재봉', 'tailoring'), 'Trapping': ('덫 사냥', 'trapping'),
}

# Grammars operate on bound question scopes, never select a primary profile.
# Empty contribution is meaningful: native Weapon/Drainable do not imply facts.
PROFILE_GRAMMARS = {
    'direct': 'qualified_function_and_effect',
    'ingestion': 'ingestion_and_qualified_effect',
    'combat': 'qualified_combat_operation',
    'wearing': 'body_function_with_wear_condition',
    'storage': 'storage_and_transfer_conditions',
    'reading': 'reading_and_separately_qualified_learning',
    'expenditure': 'qualified_consumption_without_inferred_fuel',
    'crafting': 'context_local_role_and_eligibility',
    'cooking': 'preparation_role_and_food_state',
    'world_work': 'world_context_role_and_permissions',
}


def composition_scope(profile_id, fact):
    """Profile-specific admissible block grouping, with no fact selection.

    The key controls only which already realized clauses may share a block.
    The caller unions the keys from every contributing profile.
    """
    require(profile_id in PROFILE_GRAMMARS, 'unreviewed composition profile')
    qualifiers = tuple(fact['qualifier_refs'])
    context = fact['context_ref'] or (fact['ref'] if fact['fact_kind'] == 'use_context' else None)
    if profile_id in {'crafting', 'cooking', 'world_work'}:
        # A role is always grouped with its own activity, never a global role.
        return ('activity_role', context or fact['ref'], qualifiers)
    if profile_id == 'reading':
        # Reading eligibility and XP eligibility are separate claims.
        return ('reading' if fact['fact_kind'] == 'direct_function' else 'learning', qualifiers)
    if profile_id == 'ingestion':
        # Equal food-state predicates can share an ingestion/effect block.
        return ('ingestion_state', qualifiers)
    if profile_id == 'wearing':
        return ('body_location', qualifiers)
    if profile_id == 'storage':
        return ('storage_transfer', qualifiers)
    if profile_id == 'combat':
        return ('combat_operation', qualifiers)
    if profile_id == 'expenditure':
        return ('use_state', context, qualifiers)
    # Residual direct questions must not combine unrelated operations merely
    # because the item is in the always-applicable direct profile.
    return ('direct_claim', fact['ref'], qualifiers)


def predicate(fact, locale):
    require(set(fact['payload']) == {'predicate'}, 'unknown qualifier payload')
    value = fact['payload']['predicate']
    require(value in PREDICATES, 'expression_gap: unreviewed predicate')
    return phrase(PREDICATES[value], locale)


def core(fact, facts, locale):
    """Return a clause and its actually mentioned context refs."""
    kind, p = fact['fact_kind'], fact['payload']
    if kind == 'direct_function':
        require(set(p) == {'function'} and p['function'] in FUNCTIONS, 'expression_gap: function')
        return phrase(FUNCTIONS[p['function']], locale), []
    if kind == 'effect':
        require(set(p) == {'property', 'direction'}, 'expression_gap: effect shape')
        prop, direction = p['property'], p['direction']
        special = {
            ('body_wetness', 'decrease'): ('몸의 젖은 정도를 줄인다', 'It reduces body wetness'),
            ('thirst', 'decrease'): ('물을 마시면 갈증을 줄인다', 'Drinking the water reduces thirst'),
            ('poison_level', 'increase'): ('물을 마시면 중독 수치가 증가한다', 'Drinking the water increases poison level'),
        }
        if (prop, direction) in special:
            return phrase(special[prop, direction], locale), []
        skill = prop.removesuffix('_experience_multiplier')
        require(prop == skill + '_experience_multiplier' and skill in SKILLS and direction == 'increase', 'expression_gap: effect')
        name = phrase(SKILLS[skill], locale)
        return phrase((f'독서로 {name} 경험치 배율을 높인다', f'Reading increases the {name} experience multiplier'), locale), []
    if kind == 'use_context':
        require(set(p) == {'activity'} and p['activity'] in CONTEXTS, 'expression_gap: activity')
        name = phrase(CONTEXTS[p['activity']], locale)
        return phrase((f'{name}에 사용할 수 있다', f'It can be used for {name}'), locale), []
    if kind == 'context_role':
        require(set(p) == {'role'} and p['role'] in ROLES, 'expression_gap: role')
        context = facts[fact['context_ref']]
        require(context['fact_kind'] == 'use_context', 'non-local role')
        require(set(context['payload']) == {'activity'} and context['payload']['activity'] in CONTEXTS, 'expression_gap: role context')
        activity = phrase(CONTEXTS[context['payload']['activity']], locale)
        role = phrase(ROLES[p['role']], locale)
        if p['role'] == 'power_supply' and context['payload']['activity'] == 'portable_device_power':
            return phrase(('휴대 장치에 전원을 공급한다', 'It supplies power to portable devices'), locale), [context['ref']]
        if p['role'] == 'repair_target' and context['payload']['activity'] == 'repair':
            return phrase(('물품 수리의 대상이다', 'It is a target of item repair'), locale), [context['ref']]
        return phrase((f'{activity}에서 {role}로 쓰인다', f'It serves as {role} in {activity}'), locale), [context['ref']]
    raise ValueError('expression_gap: unknown semantic kind')


def qualified(fact, facts, locale):
    text, contexts = core(fact, facts, locale)
    qualifiers = sorted(set(fact['qualifier_refs']) | {q for c in contexts for q in facts[c]['qualifier_refs']})
    # Qualifiers stay adjacent to exactly this claim. No paragraph-wide scope.
    if qualifiers:
        clauses = list(dict.fromkeys(predicate(facts[q], locale) for q in qualifiers))
        context = facts[fact['context_ref']] if fact['context_ref'] else fact
        construction = context['fact_kind'] == 'use_context' and context['payload'].get('activity') == 'construction'
        label = (' — 해당 건축 경로별 조건: ', ' — conditions within each applicable construction path: ') if construction else (' — 조건: ', ' — conditions: ')
        text += phrase(label, locale) + '; '.join(clauses)
    return text + '.', sorted({fact['ref'], *contexts, *qualifiers})
