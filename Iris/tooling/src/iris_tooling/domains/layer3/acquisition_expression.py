"""User-facing acquisition propositions; raw execution detail stays in the fact."""
from __future__ import annotations
import re
from .expression_rules import phrase
from .investigation import require

ZONES = {
    'DeepForest': ('깊은 숲', 'deep forests'), 'Forest': ('숲', 'forests'),
    'Vegitation': ('초목 지대', 'vegetated areas'), 'FarmLand': ('농경지', 'farmland'),
    'Farm': ('농장', 'farms'), 'TrailerPark': ('트레일러 주거지', 'trailer parks'),
    'TownZone': ('도시 지역', 'towns'), 'Nav': ('도로 지역', 'road areas'),
}
RECOVERY = {
    'world_generator_recovery': (
        '월드에 놓인 발전기를 연결 해제한 상태에서 회수해 얻을 수 있다. 기존 상태와 남은 연료가 이어진다.',
        'It can be obtained by picking up an existing, disconnected world generator, retaining its condition and remaining fuel.'),
    'world_drum_recovery': (
        '월드에 놓인 금속 드럼통을 회수해 얻을 수 있다.',
        'It can be obtained by recovering an existing metal drum from the world.'),
    'incidental_plowing': (
        '자연 지면에 밭을 갈다가 발견할 수 있다.',
        'It may be found while plowing a plot on natural ground.'),
    'incidental_ground_digging': (
        '자루에 흙을 퍼 담다가 발견할 수 있다.',
        'It may be found while shoveling ground into a bag.'),
    'clothing_material_recovery': (
        '재료를 회수할 수 있는 의류를 찢다가 실을 얻을 수 있다. 회수 여부와 양은 재봉 수준과 의류에 따라 달라진다.',
        'Thread may be recovered by ripping eligible clothing; recovery and the amount depend on tailoring skill and the clothing.'),
    'compost_collection': (
        '퇴비통에 퇴비가 충분히 있을 때 빈 모래주머니에 담아 얻을 수 있다.',
        'It can be obtained by filling an empty sandbag from a composter containing enough compost.'),
    'crafted_rod_breakage': (
        '제작한 낚싯대가 낚시 중 부러질 때 나무 막대를 얻는 경로가 있다.',
        'A wooden stick can be recovered when a crafted fishing rod breaks during fishing.'),
    'manufactured_rod_breakage': (
        '일반 낚싯대가 낚시 중 부러질 때 얻을 수 있다.',
        'It can be obtained when a manufactured fishing rod breaks during fishing.'),
    'curtain_material_recovery': (
        '커튼이 달린 창문이나 커튼을 파괴하는 과정에서 시트를 회수할 수 있다.',
        'A sheet can be recovered when destroying a curtain or a window with curtains.'),
    'padlock_key_issue': (
        '열쇠를 발급할 수 있는 자물쇠를 채울 때 얻을 수 있다. 열쇠 수는 사용한 자물쇠에 따라 달라진다.',
        'Keys can be obtained when fitting a padlock that can still issue keys; the count depends on that padlock.'),
    'padlock_recovery': (
        '맞는 열쇠로 자물쇠를 풀어 회수할 수 있다. 이 과정에서 열쇠는 소모된다.',
        'It can be recovered by unlocking a padlock with its matching key, which is consumed in the process.'),
    'placed_lit_candle_replacement': (
        '켜진 양초를 바닥에 놓으면 꺼진 양초로 바뀌며, 남은 사용량과 상태가 이어진다.',
        'Placing a lit candle on the floor yields an unlit candle with its remaining uses and condition retained.'),
    'transferred_lit_candle_replacement': (
        '켜진 양초를 용기 사이에서 옮기는 과정에서 꺼진 양초로 바뀌며, 남은 사용량과 상태가 이어진다. 바닥에 놓거나 월드에서 줍는 경로와는 구별된다.',
        'Transferring a lit candle between containers can yield an unlit candle with its remaining uses and condition retained. This is distinct from floor placement or world-item pickup.'),
    'splint_material_recovery': (
        '재료로 만든 부목을 제거하면 찢어진 시트와 부목 재료를 돌려받을 수 있다. 완성 부목 자체를 사용한 경우는 이 경로에 포함되지 않는다.',
        'Removing a splint made from materials can return ripped sheets and the splint material. This route excludes a splint made using a finished splint item.'),
}


def array(raw):
    require(isinstance(raw, str) and raw.strip().startswith('{') and raw.strip().endswith('}'), 'unsupported list')
    values = [x.strip().strip('"') for x in raw.strip()[1:-1].split(',') if x.strip()]
    require(all(re.fullmatch(r'[A-Za-z0-9_.]+', x) for x in values), 'unsupported list token')
    return values


def weights(raw):
    require(isinstance(raw, str) and raw.strip().startswith('{') and raw.strip().endswith('}'), 'unsupported zones')
    pairs = []
    for entry in raw.strip()[1:-1].split(','):
        if not entry.strip():
            continue
        m = re.fullmatch(r'\s*(\w+)\s*=\s*(\d+(?:\.\d+)?)\s*', entry)
        require(m is not None and m[1] in ZONES, 'unknown zone')
        pairs.append((m[1], m[2]))
    require(len(pairs) == len(dict(pairs)), 'duplicate zone')
    return sorted(pairs)


def locations(payload, locale):
    p = payload['conditions']
    category_zones = {z for c in p['category_conditions'].values() for z, w in weights(c['zoneChance']) if float(w) > 0}
    allowed = [z for z, w in weights(p['zones']) if float(w) > 0 and z in category_zones]
    require(allowed, 'expression_gap: no supported foraging place')
    return ', '.join(phrase(ZONES[z], locale) for z in allowed)


def foraging(payload, locale):
    p, route = payload['conditions'], payload['route']
    place = locations(payload, locale)
    text = [phrase((f'{place}에서 채집 중 발견할 수 있다.', f'It may be found by foraging in {place}.'), locale)]
    months = sorted(map(int, array(p['months'])))
    if months != list(range(1, 13)):
        # Month membership is a genuine availability scope, not a spawn weight.
        intervals = []
        for m in months:
            if intervals and intervals[-1][-1] == m - 1:
                intervals[-1].append(m)
            else:
                intervals.append([m])
        ko = ', '.join(f'{xs[0]}~{xs[-1]}월' if len(xs) > 1 else f'{xs[0]}월' for xs in intervals)
        names = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
        en = ', '.join(f'{names[xs[0]-1]}–{names[xs[-1]-1]}' if len(xs) > 1 else names[xs[0]-1] for xs in intervals)
        text.append(phrase((f'발견 가능한 시기는 {ko}이다.', f'It is available during {en}.'), locale))
    if int(p['skill']) > 0:
        text.append(phrase((f"채집 {p['skill']}레벨이 필요하다.", f"It requires foraging level {p['skill']}."), locale))
    if p['forceOutside'] == 'true':
        text.append(phrase(('실외에서 발견되는 경로다.', 'This route requires an outdoor location.'), locale))
    if array(p['recipes']):
        require(array(p['recipes']) == ['Herbalist'], 'unreviewed knowledge')
        text.append(phrase(('약초 지식이 필요하다.', 'Herbalist knowledge is required.'), locale))
    natural = all(array(c['validFloors']) != ['ANY'] for c in p['category_conditions'].values())
    if natural:
        text.append(phrase(('자연 지면에서 찾을 수 있다.', 'It can be found on natural ground.'), locale))
    if route['method'] == 'foraging_crop_seed':
        crops = {'farming.Potato': ('감자', 'potatoes'), 'farming.Tomato': ('토마토', 'tomatoes'),
                 'farming.Carrot': ('당근', 'carrots'), 'farming.Cabbage': ('양배추', 'cabbages'),
                 'Base.Carrots': ('당근', 'carrots'), 'Base.Broccoli': ('브로콜리', 'broccoli'),
                 'farming.RedRadish': ('래디시', 'radishes')}
        crop = phrase(crops[route['crop_item']], locale)
        text.append(phrase((f'야생 {crop} 채집 시 씨앗이 함께 나오는 경로이며 매번 나오지는 않는다.', f'This seed route accompanies foraging wild {crop}; seeds are not obtained every time.'), locale))
    return ' '.join(text)


def new_game(payload, locale):
    p = payload['conditions']
    clauses = []
    if 'difficulty' in p:
        names = {'Easy': ('쉬움', 'Easy'), 'Normal': ('보통', 'Normal'), 'Hard': ('어려움', 'Hard')}
        name = phrase(names[p['difficulty']], locale)
        clauses.append(phrase((f'{name} 난이도', f'{name} difficulty'), locale))
    if 'sandbox' in p:
        clauses.append(phrase(('시작 장비 설정을 켠 경우', 'the Starter Kit setting enabled'), locale))
    condition = ', '.join(clauses)
    lead = phrase((f'새 캐릭터 시작 시 {condition}에 지급되는 경로가 있다.' if condition else '새 캐릭터를 시작할 때 지급되는 경로가 있다.',
                   f'It has a new-character starting-item route with {condition}.' if condition else 'It has a new-character starting-item route.'), locale)
    if 'bag_guard' in p:
        lead += ' ' + phrase(('해당 지급 시점에 책가방이 없어야 한다.', 'A schoolbag must be absent at that point in the starting-item grant.'), locale)
    if 'initial_condition' in p:
        lead += ' ' + phrase((f"지급되는 물품의 상태 값은 {p['initial_condition']}이다.", f"The granted item has condition {p['initial_condition']}."), locale)
    return lead


def catch(payload, locale):
    p = payload['conditions']
    if payload['route']['method'] == 'fishing':
        return phrase(('물고기가 남아 있는 물가에서 알맞은 미끼나 창으로 낚시하다 얻을 수 있다. 물고기를 잡는 경우 줄이 끊어지지 않아야 한다.',
                       'It may be obtained by fishing at stocked water with a suitable lure or spear; catching a fish requires the line to remain intact.'), locale)
    d = p['definition']
    zones = sorted(re.search(r'\["(.+)"\]', k)[1] for k, v in d.items() if k.startswith('.zone[') and float(v) > 0)
    place = ', '.join(phrase(ZONES[z], locale) for z in zones)
    text = phrase((f'{place}에서 신선한 미끼를 넣은 알맞은 덫으로 잡을 수 있다. 플레이어가 가까이 있지 않은 동안 잡힌 동물이 덫을 확인할 때까지 남아 있어야 한다.',
                   f'It may be caught in {place} using a suitable trap with fresh bait, away from nearby players. The animal must remain in the trap until it is checked.'), locale)
    if d['.minHour'] != d['.maxHour']:
        text += ' ' + phrase((f"포획 시간대는 {d['.minHour']}시부터 다음 날 {d['.maxHour']}시까지다.", f"Capture hours run from {d['.minHour']}:00 through {d['.maxHour']}:00 the next day."), locale)
    return text


def realize(fact, locale):
    payload = fact['payload']
    require(set(payload) == {'route', 'conditions'}, 'expression_gap: acquisition shape')
    method = payload['route']['method']
    if method in {'foraging', 'foraging_crop_seed'}:
        return foraging(payload, locale)
    if method == 'new_game':
        return new_game(payload, locale)
    if method in {'fishing', 'trapping'}:
        return catch(payload, locale)
    require(method in RECOVERY, 'expression_gap: unreviewed route')
    return phrase(RECOVERY[method], locale)


def dependency_paths(fact):
    """Sources of the user-facing proposition, not claims to verbalize each field."""
    p = fact['payload']['conditions']
    method = fact['payload']['route']['method']
    paths = {'/conditions/eligibility'}
    if method in {'foraging', 'foraging_crop_seed'}:
        paths.update('/conditions/' + k for k in ('zones', 'months', 'skill', 'forceOutside', 'recipes'))
        for cat in p['category_conditions']:
            paths.update('/conditions/category_conditions/' + cat + '/' + k for k in ('zoneChance', 'validFloors'))
        if method == 'foraging_crop_seed':
            paths.add('/conditions/seed_branch')
    elif method == 'new_game':
        paths.update('/conditions/' + k for k in p if k != 'delivery')
    elif method == 'trapping':
        paths.update('/conditions/definition/' + k for k in p['definition'] if k in {'.minHour', '.maxHour'} or k.startswith('.zone['))
    return sorted(paths)
