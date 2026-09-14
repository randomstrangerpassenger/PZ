"""Phrase vocabulary only. No r6 producer, selection, prose record or audit runs."""
from __future__ import annotations

from . import expression_rules as base
from . import recovery_expression as vocabulary
from . import recovery_sources as source
from . import acquisition_expression

FUNCTIONS = {**base.FUNCTIONS, **{k: v[1:] for k, v in source.FUNCTIONS.items()},
             **vocabulary.FUNCTION_VIEWS,
             "view_written_note_pages": ("저장된 메모를 열람할 수 있다", "Stored notes can be viewed"),
             "switch_declared_clothing_form": ("선택 가능한 다른 착용 형태로 바꿀 수 있다", "It can be changed into an available alternate wearable form")}
FUNCTIONS.update({
    'provide_vehicle_headlight': ('호환 차량의 전조등에 달아 빛을 낼 수 있다', 'It can provide light in a compatible vehicle headlight'),
    'install_vehicle_storage_part': ('호환 차량에 장착할 수 있다', 'It can be installed in a compatible vehicle'),
    'melee_attack': ('무기로 쓸 수 있다', 'It can be used as a weapon'),
    'request_physics_attack': ('던져서 사용할 수 있다', 'It can be thrown'),
    'unpick_garment_patch': ('의류의 패치를 제거할 수 있다', 'It can be used to remove a garment patch'),
    'use_pain_relief_medicine': ('통증 완화를 위해 복용할 수 있다', 'It can be taken for pain relief'),
    'use_unhappiness_medicine': ('시간을 두고 불행을 줄이는 데 복용할 수 있다', 'It can be taken to reduce unhappiness over time'),
    'use_panic_relief_medicine': ('공포를 줄이는 데 복용할 수 있다', 'It can be taken to reduce panic'),
    'use_sleep_aid_medicine': ('불안이나 통증으로 잠들기 어려울 때 복용할 수 있다', 'It can help with sleep when anxiety or pain makes falling asleep difficult'),
    'use_fatigue_relief_medicine': ('피로를 줄이는 데 복용할 수 있다', 'It can be taken to reduce fatigue'),
    'use_wound_infection_medicine': ('상처 감염을 치료하는 데 복용할 수 있다. 좀비화는 막지 못한다', 'It can be taken to fight wound infections. It cannot prevent zombification'),
    'apply_lip_makeup': ('입술 화장을 할 수 있다', 'It can be used to apply lip makeup'),
    'apply_eye_makeup': ('눈 화장을 할 수 있다', 'It can be used to apply eye makeup'),
    'apply_makeup': ('화장을 할 수 있다', 'It can be used to apply makeup'),
    'remove_registered_makeup': ('화장을 지울 수 있다', 'It can be used to remove makeup'),
    'install_vehicle_suspension': ('맞는 차량에 서스펜션으로 장착할 수 있다', 'It can be installed as suspension in a compatible vehicle'),
    'remove_vehicle_suspension': ('호환 차량의 서스펜션을 탈거할 수 있다', 'The compatible vehicle suspension can be removed'),
})

# Installation describes the component being fitted, not a servicing tool.
for _part, _ko_name, _en_name in (('brake', '브레이크', 'a brake'), ('muffler', '머플러', 'a muffler')):
    FUNCTIONS['install_vehicle_' + _part] = (
        '맞는 차량에 ' + _ko_name + '로 장착할 수 있다',
        'It can be installed as ' + _en_name + ' in a compatible vehicle')


def wearing(location, locale):
    """Realize admitted body locations without exposing equipment-slot terms."""
    name = pair(source.BODY_LABELS[location], locale)
    if location.startswith('MakeUp_'):
        return ('얼굴을 꾸미는 데 사용할 수 있다' if locale == 'ko' else 'It can be used to decorate the face')
    if location == 'Eyes':
        return ('얼굴에 걸쳐 쓸 수 있다' if locale == 'ko' else 'It can be worn over the eyes')
    if location in {'LeftEye', 'RightEye'}:
        return (name + ' 위에 착용할 수 있다' if locale == 'ko' else 'It can be worn over the ' + name)
    if location in {'Socks', 'Shoes'}:
        return ('발에 신을 수 있다' if locale == 'ko' else 'It can be worn on the feet')
    if location in {'Necklace', 'Necklace_Long'}:
        return ('목에 걸어 착용할 수 있다' if locale == 'ko' else 'It can be worn around the neck')
    if location == 'Scarf':
        return ('목에 두를 수 있다' if locale == 'ko' else 'It can be worn around the neck')
    if location == 'Hands':
        return ('손에 낄 수 있다' if locale == 'ko' else 'It can be worn on the hands')
    if location in {'Belt', 'BeltExtra'}:
        return ('허리에 착용할 수 있다' if locale == 'ko' else 'It can be worn at the waist')
    bodily = {'Hat', 'FullHat', 'Ears', 'EarTop', 'BellyButton', 'Nose', 'Shoes', 'Hands',
              'Neck', 'Mask', 'MaskEyes', 'MaskFull', 'LeftWrist', 'RightWrist',
              'Left_MiddleFinger', 'Right_MiddleFinger', 'Left_RingFinger', 'Right_RingFinger'}
    if location in bodily:
        return (name + '에 착용할 수 있다') if locale == 'ko' else 'It can be worn on the ' + name
    return ('착용할 수 있다' if locale == 'ko' else 'It can be worn')

EFFECTS = {**source.EFFECTS, **vocabulary.EFFECT_VIEWS,
    ("reload_speed_setting", "multiply_1_15"): ("장전 속도를 15% 높인다", "It increases reload speed by 15%"),
    ("forge_temperature", "increase"): ("화로의 열을 높인다", "It raises furnace heat"),
    ("fishing_rod_form", "replace_on_line_break"): ("낚싯줄이 끊어지면 원래 낚싯대와 미끼가 사라진다", "A broken line removes the original rod and lure")}
CONTEXTS = {**vocabulary.CONTEXTS,
            'food_preparation': ('요리', 'food preparation and cooking')}
ROLES = vocabulary.ROLES

# Short independently authored capability phrases. The predicates in detail
# still describe execution; these phrases do not promise an unconditional act.
COMPACT_FUNCTIONS = {
    'drink_food_contents': ('마실 수 있다', 'It can be drunk'),
    'take_food_medicine': ('약으로 복용할 수 있다', 'It can be taken as medicine'),
    "melee_attack": ("무기로 쓸 수 있다", "It can be used as a weapon"),
    "request_physics_attack": ("던져서 사용할 수 있다", "It can be thrown"),
    "apply_splint": ("골절 부위를 고정하는 데 쓸 수 있다", "It can be used to splint fractures outside the head and torso"),
    "record_written_notes": ("필기구가 있고 타인의 소유 잠금 없이 편집 잠금이 풀려 있으면 메모를 쓸 수 있다", "Notes can be written with a writing implement, no other-user ownership lock and editing unlocked"),
    "view_written_note_pages": ("필기구 없이 메모를 읽을 수 있다", "Notes can be read without a writing implement"),
    "wear_on_body": ("몸에 착용할 수 있다", "It can be worn"),
    "wear_configured_clothing": ("몸에 착용할 수 있다", "It can be worn"),
    "read_literature": ("읽기 조건에 맞으면 독서할 수 있다", "It can be read when the reading requirements are met"),
    "consume_edible_food": ("먹을 수 있다", "It can be eaten"),
    "eat_food": ("먹을 수 있다", "It can be eaten"),
    "supply_trap_bait": ("추가 재료가 없는 날음식을 받는 덫의 미끼로 쓸 수 있다", "It can bait a compatible trap as uncooked food without added ingredients"),
    "fish_with_spear": ("창낚시에 쓸 수 있다", "It can be used for spear fishing"),
    "write_note_pages": ("잠기지 않은 메모를 쓰는 필기구로 쓸 수 있다", "It can serve as a writing implement for unlocked notes"),
    "drink_stored_water": ("갈증이 있을 때 담긴 물을 마실 수 있다", "Its water can be drunk when thirsty"),
    "apply_fertilizer": ("파종된 살아 있는 작물의 비료로 쓸 수 있다", "It can fertilize living, seeded crops"),
    "consolidate_drainable_supplies": ("같은 종류의 덜 찬 물품에 잔량을 모을 수 있다", "Its remainder can be consolidated into a nonfull item of the same type"),
}

INLINE_CONDITIONS = {
    (source.CONSUMING, 'drink_food_contents'): ('포만 상태가 허용하면', 'when satiety permits'),
    (source.CONSUMING, 'take_food_medicine'): ('포만 상태가 허용하면', 'when satiety permits'),
    (source.FOOD_TRAP_BAIT, "supply_trap_bait"): ("추가 재료가 없는 날음식", "uncooked food without added ingredients"),
    (source.NOTE_EDIT, "record_written_notes"): ("필기구가 있고 타인의 소유 잠금 없이 편집 잠금이 풀려 있으면", "with a writing implement, no other-user ownership lock and editing unlocked"),
    (source.CONSUMING, "consume_edible_food"): ("포만 상태가 허용하면", "when satiety permits"),
    (source.CONSUMING, "eat_food"): ("포만 상태가 허용하면", "when satiety permits"),
    (source.MELEE, "melee_attack"): ("차량 밖에서", "outside a vehicle"),
    (source.PHYSICS_ATTACK, "request_physics_attack"): ("차량 밖에서", "outside a vehicle"),
    (source.WATER_DRINKING, "drink_stored_water"): ("갈증이 있을 때", "when thirsty"),
}

# These are explicit shared meanings, not a general equal-string filter.
# Each predicate keeps its own application/ref even when an overview says the
# shared condition once. Expanded uses the full, separately scoped predicates.
COMPACT_CONDITION_GROUPS = {
    source.ROD_FISHING: "rod_at_water",
    source.FISHING_EXECUTION: "rod_at_water",
    source.PAINTING: "painting_tools",
    source.PAINT_ACTIONS: "painting_tools",
    source.MAKEUP_USE: "makeup_access",
    source.MAKEUP_LIFECYCLE: "makeup_access",
}

COOKING_ELIGIBILITY = 'Only where the recipe accepts the ingredient, with its cooked/frozen and other eligibility requirements satisfied.'
PILL_INVENTORY = 'The selected pills remain in inventory while taking them.'
READING_ELIGIBILITY = 'The character can read, is awake, meets any book skill requirement, and the reading action remains valid for possession, page state and driving state.'
COMPACT_CONDITION_GROUPS.update({READING_ELIGIBILITY: 'reading_eligibility', source.READ_SELECTION: 'reading_eligibility'})


def qualifier_clauses(qualifiers, locale):
    """A predicate's existence never licenses an execution guide in L3."""
    return list(dict.fromkeys(use_qualifier(q, locale) for q in qualifiers if public_qualifier(q)))


def public_qualifier(q):
    """Only independently useful consumption consequences reach fallback prose.

    Target compatibility and required participants are stated by the use
    frames, from their scoped evidence. Full eligibility/calculation predicates
    remain available to those frames, but are not automatic extra sentences.
    """
    return q['payload']['predicate'] in {
        source.BANDAGE_INFECTION, source.POISONOUS_WILD_FOOD,
    }


QUALIFIER_OVERRIDES = {
    # Public descriptions address ordinary survival play. The source predicate
    # remains the exact input/ref key; cheat-only exceptions are not public prose.
    'Only for a compatible previous construction stage, with required skills, tools and materials available; material consumption excludes construction cheat mode.':
        ('건축 단계를 이어 진행하려면 호환되는 이전 단계와 필요한 기술·도구·재료를 갖춰야 한다',
         'Continuing construction requires a compatible previous stage and the required skills, tools and materials'),
    'For the active wooden-cross or log-wall branch requiring this material; log-wall binding chooses sufficient sheets (clean/dirty), otherwise twine, otherwise rope. World placement and material availability must hold; cheat mode does not consume material.':
        ('이 재료가 필요한 나무 십자가 또는 통나무 벽 작업에 해당한다. 통나무 벽을 묶을 때 충분한 깨끗한 시트나 더러운 시트를 먼저 사용하고, 없으면 노끈, 그다음 밧줄을 사용한다. 배치와 재료 확보 조건을 충족해야 한다',
         'This applies to wooden-cross or log-wall construction requiring this material. Log-wall binding uses sufficient clean or dirty sheets first, otherwise twine, otherwise rope. Placement and material availability must hold'),
    source.STITCHING: ('유리가 없고 붕대를 감지 않은 깊은 상처를 봉합침 또는 바늘과 실로 봉합한다',
                       'Stitch a deep, unbandaged wound without glass using a suture needle or a needle and thread'),
    source.MAKEUP_LIFECYCLE: ('선택한 화장품과 소지한 거울 또는 같은 층에서 가로막히지 않은 가까운 거울이 필요하다. 차량에 타고 있거나 파운데이션을 소지·선택한 경우에는 거울 없이 가능하다. 화장품 사용량은 소모하지 않으며 미확정 미리보기는 창을 닫으면 취소된다',
                             'Use the selected cosmetic with a carried mirror or an unobstructed nearby mirror on the same floor. Being in a vehicle or carrying or selecting foundation permits use without a mirror. Cosmetic uses are not spent; closing the window cancels an uncommitted preview'),
    source.BODY_WASHING: ('같은 건물 맥락의 접근 가능한 물 공급원에서 피·때 묻은 몸을 씻으며 세탁기·건조기는 제외된다. 처리 부위당 물 1단위를 쓰고 피를 씻을 때 남은 세제 사용량을 소모한다. 물이 부족하면 일부 부위가 남고 화장도 제거된다. 세제가 부족해도 가능하지만 더 오래 걸리며 이동하면 중단된다',
                          'Wash a bloody or dirty body at a reachable water source in the same building context, excluding washers and dryers. Each processed part uses one water unit and blood cleaning spends available soap uses. Limited water can leave parts unwashed; makeup is removed too. Insufficient soap slows washing without preventing it; movement interrupts'),
    source.EQUIPMENT_WASHING: ('같은 건물 맥락의 접근 가능한 물 공급원에서 소지한 피·때 묻은 의류·용기나 피 묻은 무기를 씻으며 세탁기·건조기는 제외된다. 동작마다 물 10단위가 필요하다. 세제를 쓰는 의류 분기는 피 묻은 부위마다 사용량을 소모하고 때만 있으면 소모하지 않는다. 옷은 완전히 젖으며 세제 부족은 시간을 늘려도 세척을 막지 않는다. 이동하면 중단된다',
                               'Wash carried bloody or dirty clothing or containers, or bloody weapons, at a reachable water source in the same building context, excluding washers and dryers. Each action needs ten water units. The with-soap clothing branch spends a use per bloody part, none for dirt alone. Clothing becomes fully wet; insufficient soap slows washing without preventing it. Movement interrupts'),
    source.WASHING_OUTCOME: ('물로 처리한 신체·의류 부위의 피·때만 지운다. 물이 부족하면 몸의 일부만 씻길 수 있고 의류는 젖는다. 세제는 선택 사항이며 상처·감염 치료를 뜻하지 않는다',
                             'Water clears blood and dirt only from processed body or clothing parts. Limited water can leave the body partly unwashed, and clothing becomes wet. Soap is optional; this does not treat wounds or infection'),
    source.POULTICE_USE: ('다른 약초 찜질제가 없고 붕대가 없는 다친 부위에 소지한 찜질제를 소모해 바른다. 해당 약초 계수를 10에 의료 기술에 따른 임의값을 더한 값으로 설정하며 환자가 시술 범위에 있어야 한다',
                         'Consume the carried poultice on an injured, unbandaged part without another herbal poultice. Its corresponding factor is set to ten plus a medical-skill-dependent random value; the patient must remain within treatment reach'),
    **{predicate: tuple(text.rstrip('.') for text in source.QUALIFIERS[predicate]) for predicate in source.SPEAR_CONDITIONS.values()},
    source.RUNNING_EXCHANGE['tire']: ('잭과 주 손의 휠 렌치가 필요하며 정비 1을 성공 판정에 반영한다. 별도 제작 지식은 요구하지 않는다. 장착할 때는 대응 브레이크와 서스펜션이 있어야 한다', 'A jack and primary-hand lug wrench are required; Mechanics 1 feeds the success roll without a recipe requirement. Installation requires the matching brake and suspension'),

    source.VEHICLE_FUEL: ('엔진이 꺼진 차량의 장착 탱크에 접근하고 맞는 용기와 남은 연료 또는 빈 공간을 갖춰 넣거나 뺀다. 중단해도 일부 옮긴 연료는 남을 수 있다',
                         'Approach the installed tank with the engine stopped and a suitable container, available fuel or free space for adding or siphoning. Partial transfers may remain after interruption'),
    source.VEHICLE_FUEL_ENGINE: ('장착 탱크의 연료를 작동 중인 엔진이 소비하며 탱크 상태가 70 미만이면 추가 연료 손실이 생길 수 있다',
                                'A running engine consumes fuel from the installed tank; tank condition below 70 can cause additional fuel loss'),
    source.SPEAR_TOOL_WEAR: ("창 제작에 사용하면 도구의 내구도가 줄어든다", "Using the tool to craft a spear reduces its condition"),
    source.ROD_LINE_BREAK: ("제작 낚싯대에서는 나무 막대, 일반 낚싯대에서는 부러진 낚싯대를 얻는 경로가 있다", "A crafted rod can return a wooden stick; a manufactured rod can return a broken rod"),
    source.BELLOWS_USE: ("불이 붙고 열이 낮은 화로에서 사용하며 지구력을 소모한다. 이동하면 중단된다", "Use on a lit furnace below maximum heat; it consumes endurance. Movement interrupts"),
    source.TRAP_ASSEMBLY: ("선택한 덫 제작법의 재료와 학습 조건이 필요하다. 톱과 목공·덫 기술은 제작법에서 요구할 때 필요하며 운전 중에는 제작할 수 없다", "Use the materials and learned recipe for the selected trap. A saw and carpentry or trapping skill are needed when the recipe requires them; crafting is unavailable while driving"),
    source.CANDLE_EXTINGUISH_RECIPE: ("켜진 초를 대상으로 하며 걸으면서 가능하지만 운전 중에는 할 수 없다", "It applies to a lit candle; walking is allowed, but driving is not"),
    source.LIGHT_CONTROL: ("손에 들거나 장착한 상태에서 이용하며 실제 발광은 현재 상태에 달려 있다", "Use while held or attached; actual light emission depends on its current state"),
    source.PANEL_INSTALL: ("호환되는 빈 차량 부품 자리에 상태가 남은 물품을 설치하며 지정 도구·지식·선행 작업이 필요하다. 설치가 계속 허용되어야 하며 실패하면 물품이 손상될 수 있다", "Installation needs a compatible empty vehicle-part slot, an item with condition remaining, and the specified tools, knowledge and prerequisites. Installation must remain permitted; failure can damage the item"),
    source.PANEL_REMOVE: ("장착된 호환 부품의 탈거가 허용되어야 하며 지정 도구·지식·선행 제거와 내용물 비우기 조건을 따른다. 실패하면 장착 부품이 손상될 수 있다", "Removal must be permitted for the installed compatible part, with its tools, knowledge, prerequisite removals and empty-content conditions. Failure can damage the installed part"),
    source.STAGE_ACTION: ("단계별 건축에서 요구하는 제작 지식과 파손되지 않은 보존 도구·재료를 갖춰야 한다. 이동하면 중단되며 일반 완료 시 재료를 소모한다", "Staged construction requires its recipe knowledge, unbroken kept tools and materials. Movement interrupts; ordinary completion consumes the materials"),
    source.WEAR_ACTION: ("착용 중 물품이 소지품에 남아 있어야 하며 이동하면 착용 동작이 중단된다", "The item must remain in inventory during the wear action; movement interrupts wearing"),
    source.FIXING_ACTION: ("수리 재료를 소지해야 하며 장착된 차량 부품이 아닌 수리 대상도 소지해야 한다. 이동하면 수리가 중단된다", "Keep the repair supplies and, except for installed vehicle parts, the target in inventory. Movement interrupts repair"),
    source.NOTE_ACCESS: ("이 조작에 접근하려면 필기구가 있고 다른 사용자의 소유 잠금이 없어야 한다", "Access to these controls requires a writing implement and no ownership lock belonging to another user"),
    source.NOTE_EDIT: ("필기구가 있고 다른 사용자의 소유 잠금이 없으며 편집 잠금이 풀려 있어야 한다", "A writing implement is required, with no other-user ownership lock and with editing unlocked"),
    source.SPEAR_FISHING: ("파손되지 않은 창을 들고 물가에서 미끼 없이 낚시한다. 이동하면 중단되며 포획은 물고기 잔량·기술·시간·계절과 확률에 따라 달라진다", "Hold an unbroken spear at nearby water to fish without bait. Movement interrupts; catches depend on stock, skill, time, season and chance"),
    source.SPEAR_FISHING_WEAR: ("물품의 내구도가 감소할 수 있다", "The item can lose condition"),
    source.WASH_TARGET: ("접근 가능한 물 공급원과 세척당 물 10단위가 필요하다. 세제는 선택 사항이며 이동하면 중단된다", "An accessible water source and ten water units per wash are required. Soap is optional; movement interrupts"),
}

# A nominal coordination preserves each admitted operation while sharing its
# subject and predicate. It is not a Profile label or a per-item sentence DB.
CONTROL_NOUNS = {}
for _family, _rows in {
    "device": """
adjust_device_volume|음량|volume
control_device_headphones|헤드폰 연결|headphone connections
control_device_media|기록 매체 재생·교체|recorded-media playback and exchange
edit_radio_presets|주파수 저장|frequency presets
insert_device_battery|건전지 삽입|battery insertion
remove_device_battery|건전지 제거|battery removal
open_device_controls|조작 창|the control panel
toggle_device_power|전원|power
toggle_radio_microphone|마이크 음소거|microphone muting
tune_radio|주파수|radio tuning
select_tv_channel|채널|channels
""",
    "water": """
store_water|물 보관|water storage
carry_water|물 운반|water carrying
pour_water_into_container|물 따르기|water pouring
receive_poured_water|물 받기|receiving water
dump_water|물 버리기|water disposal
supply_world_water_storage|물 저장 시설 보충|refilling water-storage objects
water_seeded_crop|파종된 작물 급수|watering seeded crops
wash_vehicle_blood|차량 혈흔 세척|washing vehicle blood
""",
    "firearm": """
load_firearm_rounds|호환 탄약 장전|loading matching rounds
unload_firearm_rounds|잔탄 꺼내기|unloading remaining rounds
receive_firearm_magazine|호환 탄창 삽입|inserting matching magazines
eject_firearm_magazine|장착 탄창 배출|ejecting installed magazines
rack_firearm|가능한 약실·탄 걸림 조작|available chamber and jam controls
change_firearm_mode|발사 모드 변경|firing-mode changes
receive_weapon_upgrade|드라이버로 호환 부품 장착|fitting compatible parts with a screwdriver
detach_weapon_upgrade|드라이버로 장착 부품 제거|removing installed parts with a screwdriver
use_alternate_reload_controls|설정별 장전 조작|configured reloading controls
""",
    "ignition": """
ignite_hearth_with_petrol|휘발유로 바비큐·벽난로 점화|petrol lighting of barbecues and fireplaces
ignite_hearth_with_tinder|불쏘시개로 바비큐·벽난로 점화|tinder lighting of barbecues and fireplaces
ignite_industrial_fire_with_petrol|휘발유로 연료가 있는 화로·통나무 드럼 점화|petrol lighting of fueled furnaces and drums containing logs
ignite_industrial_tinder|불쏘시개로 통나무 드럼 점화|tinder lighting of drums containing logs
light_campfire|불쏘시개로 모닥불 점화|tinder lighting of campfires
request_corpse_burning|시신 점화|corpse ignition
""",
}.items():
    for _row in _rows.strip().splitlines():
        _function, _ko, _en = _row.split("|")
        CONTROL_NOUNS[_function] = (_family, (_ko, _en))

def pair(value, locale):
    if locale not in ("ko", "en"):
        raise ValueError("unsupported locale")
    return value[0 if locale == "ko" else 1].strip().rstrip(".")


def context(activity, locale, compact=False):
    short = {"woodworking": ("목공", "woodworking"), "metal_forging": ("금속 가공", "metalworking"),
             "smithing_parts": ("문 부품 단조", "forging door fittings"),
             "shovel_smithing": ("삽류 단조", "forging shovels")}
    if compact and activity in short:
        return pair(short[activity], locale)
    if compact and activity in {"construction", "carpentry_menu_construction"}:
        return pair(("건축", "construction"), locale)
    return pair(CONTEXTS[activity], locale)


# This is a placement decision by predicate meaning, not historical compact
# inclusion. Inventory/access, action setup and delivery mechanics qualify the
# detailed execution, rather than change the stated capability/role.
DETAIL_CONDITIONS = {}
for _names, _reason in (
    ("WEARING WEAR_ACTION CARRYING CONTENTS_EMPTYING WATER_EMPTYING WATER_TRANSFER WORLD_WATER_TRANSFER WATER_STORAGE MEDICAL_CONSOLIDATION RENAME_ITEM FOOD_NAMING",
     "inventory, transfer capacity, naming limits and action lifetime are execution detail"),
    ("DEVICE_POWER DEVICE_PANEL DEVICE_VOLUME RADIO_WINDOW_LIFETIME RADIO_PRESETS RADIO_TUNING RADIO_HEADPHONE_CONTROL MIC_CONTROL RADIO_MEDIA_CONTROL BATTERY_INSERT BATTERY_REMOVE TV_TUNING",
     "control availability and per-control setup are detailed under the named supported control"),
    ("RADIO_WORLD_FORM RADIO_DISMANTLING ELECTRONIC_SALVAGE SCRAP_RECOVERY",
     "world placement and dismantling methods, tools and salvage amounts remain in expanded"),
    ("GUN_ROUND_LOADING GUN_ROUND_UNLOADING MAGAZINE_LOADING GUN_MAGAZINE_EJECTION GUN_RACKING GUN_FIRE_MODES WEAPON_ATTACHMENT WEAPON_PART_REMOVAL LEGACY_GUN_CONTROLS",
     "named firearm-control phrase preserves matching item, slot/state or setting; action lifetime and kept-tool detail are expanded"),
    ("CAMP_FUEL_USE HEARTH_FUEL FURNACE_FUEL CAMP_TINDER_USE HEARTH_TINDER INDUSTRIAL_TINDER",
     "fuel/tinder role retains its actual targets; per-target selection, igniter and consumption detail is expanded"),
    ("COOKING_ACTION COOKING_BASE FOOD_ASSEMBLY BAKING MATERIAL_ASSEMBLY CARPENTRY_MATERIAL STAGE_ACTION FORGE_PREPARATION SMITHING_PARTS SHOVEL_SMITHING CAMP_KIT_PREPARATION TRAP_ASSEMBLY SAWN_WOOD WOOD_SHAPING FIXING_ACTION",
     "named input role; recipe-specific resources, quantities, output and execution detail"),
    ("WATER_DRINKING CONSUMING MELEE PHYSICS_ATTACK NOTE_EDIT",
     "the short function explicitly states its distinguishing condition; remaining execution detail is expanded"),
    ("HEARTH_PETROL INDUSTRIAL_PETROL CORPSE_IGNITION CAMP_IGNITER",
     "named ignition role retains fuel/tinder method; target readiness and resource consumption are detailed"),
):
    for _name in _names.split():
        DETAIL_CONDITIONS[getattr(source, _name)] = _reason

COMPACT_QUALIFIERS = {}
for _names, _ko, _en in (
    ("READ_SELECTION", "글을 읽을 수 있고 깨어 있으며 책의 기술 조건에 맞아야 한다", "The reader must be literate, awake and meet the book's skill requirements"),
    ("READ_MAXIMUM", "지원 기술 범위에서 현재보다 높은 배율만 적용되며 완독해야 최대 배율에 이른다", "Only a higher multiplier applies within the supported skill levels; full reading reaches the maximum"),
    ("READ_PROGRESS", "독서 진도는 캐릭터별로 기록된다", "Reading progress is recorded per character"),
    ("FABRIC_ACTION", "데님·가죽을 찢을 때는 가위가 필요하다", "Ripping denim or leather requires scissors"),
    ("FOOD_TRAP_BAIT", "미끼는 추가 재료가 없는 날음식이어야 한다", "Bait must be uncooked food without added ingredients"),
    ("SPEAR_FISHING", "파손되지 않은 창으로 물가에서 미끼 없이 낚시하며 포획은 보장되지 않는다", "Use an unbroken spear at water without bait; catches are not guaranteed"),
    ("SPLINTING", "골절 부위에 완성 부목 또는 찢어진 천과 지지대를 사용한다", "For fractures outside the head and torso, use a finished splint or ripped sheets and a support"),
    ("POISONOUS_WILD_FOOD", "독성이 있는 야생 식품을 먹었을 때 적용된다", "This applies when poisonous wild food is eaten"),
    ("SMOKER_EFFECT", "흡연가 특성이 있을 때 적용된다", "This applies with the Smoker trait"),
    ("NONSMOKER_EFFECT", "흡연가 특성이 없을 때 적용된다", "This applies without the Smoker trait"),
    ("SMOKING", "성냥이나 라이터가 필요하다", "A match or lighter is required"),
    ("BANDAGE_INFECTION", "감염된 재료를 댄 경우에만 해당한다", "This applies only when the applied material is infected"),
    ("FERTILIZING", "살아 있고 파종된 작물에 사용한다", "Use on a living, seeded crop"),
    ("FERTILIZER_GROWTH", "과다 시비 전의 작물에만 적용된다", "This applies before over-fertilization"),
    ("FERTILIZER_ROT", "이미 네 번 이상 시비한 작물에 더 주면 해당한다", "This applies when fertilizing a crop already fertilized at least four times"),
    ("CROP_WATERING", "물을 더 받을 수 있는 파종된 작물에 사용한다", "Use on a seeded crop that can receive more water"),
    ("VEHICLE_WASHING", "접근 가능한 차량의 혈흔을 물로 씻는다", "Use water on accessible vehicle bloodstains"),
    ("ROD_FISHING FISHING_EXECUTION", "물가에서 낚싯대와 미끼를 들고 사용하며 포획은 보장되지 않는다", "Hold a rod and lure at water; catches are not guaranteed"),
    ("SLOT_USE", "착용 중 맞는 유형의 물품만 부착한다", "While worn, attach only matching item types"),
    ("FIRING", "탄약이 준비되고 탄 걸림이 없어야 한다", "Ammunition must be ready and the gun must not be jammed"),
    ("EXTINGUISH_CONDITIONS", "소화 물품의 잔량이 필요하다", "The extinguishing item must have uses remaining"),
):
    for _name in _names.split():
        COMPACT_QUALIFIERS[getattr(source, _name)] = (_ko, _en)
COMPACT_QUALIFIERS[READING_ELIGIBILITY] = COMPACT_QUALIFIERS[source.READ_SELECTION]

def compact_qualifier(q, locale, unit):
    p = q["payload"]["predicate"]
    kinds = {f["fact_kind"] for f in unit["facts"]}
    function = unit["facts"][0]["payload"].get("function")
    if p == source.READ_MOOD and all(f['payload'].get('direction') == 'cap_at_reading_start' for f in unit['facts']):
        return None, "the effect clause explicitly retains the reading-start cap; execution remains expanded"
    if p in {source.NOTE_EDIT, source.CONSUMING, source.MELEE, source.PHYSICS_ATTACK, source.WATER_DRINKING} and (p, function) not in INLINE_CONDITIONS:
        return qualifier(q, locale), "additional condition is not implied by this function's short wording"
    if p in COMPACT_QUALIFIERS:
        return pair(COMPACT_QUALIFIERS[p], locale), "short condition; complete execution scope in expanded"
    if "context_role" in kinds or "use_context" in kinds:
        return None, "input role and named activity; operation-specific eligibility and consequences in expanded"
    if p in DETAIL_CONDITIONS and not ("effect" in kinds and p in {
        source.NOTE_EDIT, source.WATER_DRINKING, source.CONSUMING, source.MELEE, source.PHYSICS_ATTACK,
    }):
        return None, DETAIL_CONDITIONS[p]
    if p == "The clothing is in the character inventory and is worn at its configured body location.":
        return None, "inventory and configured location are worn-state execution details"
    return qualifier(q, locale), "condition realized with its exact claim"


def qualifier(q, locale):
    return use_qualifier(q, locale)


def core(fact, locale, compact=False):
    kind, p = fact["fact_kind"], fact["payload"]
    if kind == "direct_function":
        fn = p["function"]
        return pair(COMPACT_FUNCTIONS[fn] if compact and fn in COMPACT_FUNCTIONS else FUNCTIONS[fn], locale)
    if kind == "acquisition":
        return acquisition_expression.realize(fact, locale).rstrip(".")
    if kind == "effect":
        key = p["property"], p["direction"]
        if key in EFFECTS:
            return pair(EFFECTS[key], locale)
        skill = p["property"].removesuffix("_experience_multiplier")
        if skill in base.SKILLS and p["direction"] == "increase":
            name = pair(base.SKILLS[skill], locale)
            return (f"{name} 경험치 배율을 높인다" if locale == "ko"
                    else f"It increases the {name} experience multiplier")
        raise ValueError(f"unimplemented effect: {key}")
    if kind == "state":
        state, value = p["state"], p["value"]
        if state == "worn_location":
            name = pair(source.BODY_LABELS[value], locale)
            return f"착용 위치는 {name} 자리다" if locale == "ko" else f"It occupies the {name} equipment slot"
        if type(value) is not int or value <= 0:
            raise ValueError("invalid reading parameter")
        return pair({
            "reading_page_count": (f"전체 {value}쪽이다", f"It has {value} pages"),
            "skill_book_max_multiplier": (f"경험치 배율은 최대 {value}배다", f"Its XP multiplier reaches up to {value}"),
            "skill_book_progress_step": (f"독서 진행 {value}%마다 경험치 배율을 계산한다", f"Its XP multiplier is calculated in {value}% reading-progress steps"),
        }[state], locale)
    raise ValueError(f"unimplemented lexical kind: {kind}")


# Player-use condition wording. These phrases are authored from the existing
# admitted predicates. They do not re-parse source or infer a new item effect.
# The full predicate remains in the item's qualifier record.
# Only these existing, use-relevant projections are adopted. New entries in
# the source vocabulary are not automatically made public by this composer.
_ADOPTED_USE_CONDITIONS = """
FOOD_TRAP_BAIT OPENED_FOOD EGG_CARTON_OPENING PRODUCE_SACK_OPENING JAR_PREPARATION
FERTILIZER_GROWTH FERTILIZER_ROT BATTERY_INSERTION BATTERY_INSERT PICKUP_LOSS
SMOKING SMOKER_EFFECT NONSMOKER_EFFECT POISONOUS_WILD_FOOD FIRING READ_MOOD
BANDAGE_INFECTION BANDAGE_PANIC BANDAGE_OR_BURN_PANIC SLOT_USE ROD_REPAIR_INPUT
FISHING_LURE_LOSS SCRAP_RECOVERY CAMPFIRE_PLACEMENT TENT_REST TRAP_CATCH
TRAP_RABBIT_SQUIRREL TRAP_BIRD TRAP_RODENTS FISHING_LURES FISHING_MATCHES
SPEAR_FISHING SPEAR_FISHING_WEAR SPEAR_TOOL_WEAR SPEAR_STONE_LOSS RADIO_CRAFTING
ACTIVATION WATER_STORAGE FLOOR_GLASS_INJURY TIRE_WEAR PADLOCK_KEY_USE
CANNED_COOKED FISH_CREATED RADIO_CODE_EFFECTS MEDICAL_PANIC LIGHT_CONTROL
CAMP_FRICTION LAMP_BULB LAMP_BATTERY LAMP_CONVERSION PILLAR_BATTERY
CHARGER_CONTROLS VEHICLE_BATTERY_EXCHANGE VEHICLE_BATTERY_CYCLE VEHICLE_BULB_EXCHANGE
GENERATOR_CONTROL GENERATOR_REPAIR GENERATOR_REFUEL THUMPABLE_SCRAP
NET_CHECKING STONE_TOOL_WEAR PUMP_CONTAINER VEHICLE_CONTAINER INDUSTRIAL_PETROL
HEAT_FRICTION PROPANE_BARBECUE BELLOWS_USE DRUM_LOGS CORPSE_IGNITION
TRAP_LIFECYCLE ROD_LINE_BREAK ENGINE_REPAIR ENGINE_SALVAGE VEHICLE_TOOL_USE
PLASTER_USE CURTAIN_USE BURNT_VEHICLE_USE
""".split()
USE_QUALIFIERS = {getattr(source, name): vocabulary.QUALIFIER_VIEWS[getattr(source, name)]['compact']
                  for name in _ADOPTED_USE_CONDITIONS}
RELOAD_SCOPES = {}
for _strap, _predicate in source.STRAP_SPEED.items():
    _shells = _strap.endswith('_Shells')
    RELOAD_SCOPES[_predicate] = (
        '산탄을 쓰는 총기' if _shells else '산탄 이외의 탄종을 사용하는 총기',
        'firearms using shotgun shells' if _shells else 'firearms using ammunition other than shotgun shells')
    USE_QUALIFIERS[_predicate] = (
        '착용 중 ' + RELOAD_SCOPES[_predicate][0] + '에 적용된다',
        'While worn, it applies to ' + RELOAD_SCOPES[_predicate][1])


def reload_effect(unit, plan, locale, compact):
    """Realize the admitted operation and its ammo scope, never item identity."""
    if [f['payload'] for f in unit['facts']] != [
            {'property': 'reload_speed_setting', 'direction': 'multiply_1_15'}]:
        return None
    predicates = {plan['qualifiers'][q]['payload']['predicate'] for q in unit['qualifier_refs']}
    if len(predicates) != 1 or not predicates <= RELOAD_SCOPES.keys():
        return None
    scope = pair(RELOAD_SCOPES[next(iter(predicates))], locale)
    if locale == 'ko':
        return '착용하면 ' + scope + '의 장전 속도를 15% 높인다'
    return ('+15% reload speed for ' + scope + ' while worn' if compact else
            'While worn, it increases reload speed by 15% for ' + scope)
for _names, _ko, _en in (
    ('WEARING WEAR_ACTION', '지정된 신체 위치에 착용한다', 'It is worn at its designated body location'),
    ('CARRYING', '담긴 물품과 함께 운반할 수 있다', 'It can be carried with its contents'),
    ('BACK_CONTAINER', '등에 메어 착용할 수 있다', 'It can be worn on the back'),
    ('COOKING_ACTION', '재료의 조리·냉동 상태 등 해당 요리의 재료 조건을 충족해야 한다', 'The ingredient must meet the preparation’s requirements, including cooked and frozen state'),
    ('COOKING_BASE', '이 용기가 받는 재료를 더해 요리를 만들 수 있다', 'Accepted ingredients can be added to this container to prepare food'),
    ('FOOD_ASSEMBLY BAKING', '선택한 요리가 요구하는 재료와 도구를 함께 사용한다', 'Use it with the ingredients and tools required by the selected preparation'),
    ('CONSUMING', '포만 상태가 허용할 때 먹거나 마실 수 있다', 'It can be eaten or drunk when satiety permits'),
    ('MELEE PHYSICS_ATTACK', '차량 밖에서 사용할 수 있다', 'It can be used outside a vehicle'),
    ('READ_SELECTION', '읽을 수 있고 깨어 있으며 책의 기술 조건을 충족해야 한다', 'The reader must be literate, awake and meet the book’s skill requirements'),
    ('READ_MAXIMUM', '지원 기술 범위에서 현재보다 높은 배율만 적용하며 완독해야 최대 배율에 이른다', 'Only a higher multiplier applies within the supported skill range; full reading reaches the maximum'),
    ('MAP_READING', '해당 지도를 열어 볼 수 있다', 'The corresponding map can be viewed'),
    ('MAP_ANNOTATION', '맞는 필기구로 지도에 글과 기호를 적으며 수정·이동에는 지우개도 필요하다', 'A matching writing implement adds map text and symbols; editing or moving them also requires an eraser'),
    ('MAP_ERASURE', '지도의 글·기호를 지우며 수정·이동에는 필기구도 필요하다', 'It erases map text and symbols; editing or moving them also needs a writing implement'),
    ('ALARM_SETTING ALARM_STOPPING', '알람 시각을 정하고 켜거나 끌 수 있다', 'The alarm time can be set and the alarm switched on or off'),
    ('BODY_DRYING', '젖은 몸을 닦을 때 사용량을 소모하며 완전히 마르지 않을 수 있다', 'Drying a wet body spends uses and may leave some wetness'),
    ('BODY_WASHING EQUIPMENT_WASHING', '물과 함께 몸 또는 의류·장비를 씻는 세척제로 쓴다', 'It serves as a cleaning supply with water for the body or clothing and equipment'),
    ('WATER_TRANSFER WORLD_WATER_TRANSFER', '남은 물을 빈 공간이 있는 호환 용기나 물 저장 시설에 옮길 수 있다', 'Remaining water can be transferred to a compatible container or water-storage object with free capacity'),
    ('WATER_DRINKING', '갈증이 있고 물이 남아 있을 때 마실 수 있다', 'Its remaining water can be drunk when thirsty'),
    ('CROP_WATERING', '물을 더 받을 수 있는 파종 작물에 사용한다', 'Use on seeded crops that can receive more water'),
    ('VEHICLE_WASHING', '물로 차량의 혈흔을 씻는다', 'Water washes bloodstains from a vehicle'),
    ('BLOOD_CLEANING', '표백제와 청소 도구를 함께 사용해 바닥 혈흔을 지운다', 'Bleach and a cleaning tool remove floor bloodstains'),
    ('EXTINGUISH_CONDITIONS', '사용량이 남아 있으면 불타는 지면이나 캐릭터의 소화에 쓴다', 'With uses remaining, it can help extinguish burning ground or characters'),
    ('OPENING', '포장을 열어 선언된 내용물을 꺼낼 수 있다', 'The package can be opened to retrieve its declared contents'),
    ('CAN_OPENING', '해당 통조림에 맞는 개봉 도구가 필요하다', 'An opener accepted by the canned-food recipe is required'),
    ('BOWL_PORTIONING', '음식을 해당 제작법이 받는 그릇에 나눈다', 'The food can be divided among bowls accepted by its recipe'),
    ('BOX_PACKING SEED_PACKING', '해당 포장 제작법이 정한 종류와 수량을 모아 포장한다', 'The corresponding packaging recipe requires its specified types and quantities'),
    ('MATERIAL_ASSEMBLY', '해당 제작법이 요구하는 다른 재료·도구와 함께 사용한다', 'Use it with the other materials and tools required by the corresponding recipe'),
    ('FIXING_ACTION', '호환되는 손상 물품의 수리에 쓴다', 'It is used to repair compatible damaged items'),
    ('FABRIC_ACTION', '데님·가죽에는 가위가 필요하며 실도 회수할 수 있다', 'Denim and leather require scissors; thread may also be recovered'),
    ('GARMENT_PATCHING', '실과 바늘을 함께 써서 의류의 구멍을 덧대거나 패딩을 더하는 데 쓴다', 'With thread and a needle, it patches garment holes or adds padding'),
    ('GARMENT_PATCH_REMOVAL', '제거한 패치 재료를 돌려받을 수도 있다', 'The removed patch material may be recovered'),
    ('BANDAGE_APPLICATION', '붕대를 댈 수 있는 부위에 붕대 재료로 소모한다', 'It is consumed as bandaging material on a body part that permits bandaging'),
    ('BANDAGE_LIFE', '붕대의 유지 수치는 재료와 치료자의 기술에 따라 달라진다', 'Bandage life depends on the material and caregiver’s skill'),
    ('BURN_CLEANING', '세척이 필요한 화상에는 강도가 충분한 붕대 재료를 사용하며 통증이 생길 수 있다', 'Burns needing washing require sufficiently strong bandaging material; treatment can cause pain'),
    ('DISINFECTION', '붕대가 없는 치료 가능한 상처에 사용한다', 'It is used on an eligible unbandaged wound'),
    ('DISINFECTION_USE', '소독에 재료의 일부를 소모한다', 'Disinfection consumes part of the material'),
    ('PILL_TAKING', '알약을 복용할 수 있다', 'The pills can be taken'),
    ('SUTURE_ASSISTANCE', '봉합·실밥 제거의 기본 시간을 줄이는 보조 도구이며 바늘과 실을 대신하지 않는다', 'It reduces the base time for stitching or stitch removal without replacing the needle and thread'),
    ('LOADING AMMUNITION_LOADING_PATHS', '호환 총기나 탄창의 빈 공간에 장전하는 탄약이다', 'It is ammunition for compatible firearms or magazines with loading space'),
    ('MAGAZINE_FILL GUN_ROUND_LOADING', '빈 공간에 호환 탄약을 장전할 수 있다', 'Matching rounds can be loaded into available capacity'),
    ('MAGAZINE_EMPTY GUN_ROUND_UNLOADING', '남은 탄약을 꺼낼 수 있다', 'Remaining rounds can be unloaded'),
    ('MAGAZINE_LOADING GUN_MAGAZINE_EJECTION', '호환 탄창을 넣거나 장착 탄창을 꺼낼 수 있다', 'A matching magazine can be inserted or an installed magazine ejected'),
    ('WEAPON_ATTACHMENT WEAPON_PART_REMOVAL WEAPON_ATTACHMENT_TOOL', '사용 가능한 드라이버로 호환 부착물을 장착·제거하며 드라이버는 소모하지 않는다', 'A usable screwdriver installs or removes compatible attachments without being consumed'),
    ('GUN_FIRE_MODES', '지원하는 발사 모드를 선택할 수 있다', 'A supported firing mode can be selected'),
    ('GUN_FIRING_CYCLE', '탄약이 준비되어 있고 탄 걸림이 없어야 하며 낡은 총기는 걸릴 수 있다', 'Firing needs ready ammunition and no jam; worn firearms can jam'),
    ('DEVICE_POWER', '지원 기기에 전력이 있어야 가동할 수 있다', 'A supported device needs power to operate'),
    ('RADIO_TUNING TV_TUNING', '기기가 지원하는 주파수나 채널을 선택한다. 수신 가능한 내용에 따라 시청·청취 결과가 달라진다', 'Select a frequency or channel supported by the device; viewing or listening depends on available content'),
    ('RADIO_MEDIA_CONTROL', '대응 기록 매체의 재생에는 전원이 필요하다', 'Playback of compatible recorded media requires power'),
    ('MEDIA_INSERT', '대응 기기의 빈 자리에 넣으며 재생에는 전원이 필요하다', 'It fits an empty compatible device slot; playback requires power'),
    ('MEDIA_LABEL', '배정된 기록의 내용 안내를 읽을 수 있다', 'The assigned recording’s description can be read'),
    ('HEADPHONE_CONNECTION', 'TV가 아닌 휴대 기기의 빈 헤드폰 자리에 연결한다', 'It can connect to an empty headphone slot on a portable non-TV device'),
    ('RADIO_WORLD_FORM', '기기에 대응하는 설치 형태로 놓을 수 있다', 'It can be placed in its corresponding world form'),
    ('CLOTHING_FORM', '지원하는 다른 착용 형태로 바꿀 수 있다', 'It can be changed to a supported alternate wearable form'),
    ('PLACEMENT', '가구에 맞는 배치 조건을 충족하는 곳에 설치한다', 'It can be placed where its furniture placement requirements hold'),
    ('PICKUP', '해당 가구에 필요한 도구·기술이 있어야 이동할 수 있다', 'Moving the furniture requires its applicable tools and skill'),
    ('PLANT_CUTTING', '사용 가능한 자르기 도구로 덤불·벽 덩굴을 제거하며 도구가 마모될 수 있다', 'A usable cutting tool removes bushes or wall vines and may wear'),
    ('STRUCTURE_DESTRUCTION', '파괴·보호 구역 규칙이 허용하는 구조물을 슬레지해머로 파괴하며 도구가 마모될 수 있다', 'A sledgehammer destroys structures permitted by destruction and safehouse rules and may wear'),
    ('FURROW_DIGGING', '파손되지 않은 경작 도구로 빈 자연 지면에 고랑을 판다', 'An unbroken digging tool creates furrows on empty natural ground'),
    ('PLANT_REMOVAL', '파손되지 않은 경작 도구로 수확 없이 작물·고랑을 제거한다', 'An unbroken digging tool removes plants or furrows without harvesting'),
    ('GRAVE_DIGGING', '사용 가능한 삽과 무덤을 배치할 자연 지면 두 칸이 필요하다', 'It requires a usable shovel and two natural-ground squares suitable for a grave'),
    ('GRAVE_FILLING', '사용 가능한 삽으로 무덤을 메우며 시신이 없어도 가능하다', 'A usable shovel fills an unfilled grave, with or without a corpse'),
    ('GROUND_FILL', '맞는 땅 파기 도구로 흙·모래·자갈을 호환 포대의 빈 공간에 담는다', 'An accepted digging tool collects dirt, sand or gravel into a compatible bag’s free capacity'),
    ('GROUND_POUR', '내용물을 받을 수 있는 바닥에 땅 재료를 붓는다', 'Its ground material can be poured onto a suitable floor'),
    ('CAMP_FUEL_USE HEARTH_FUEL FURNACE_FUEL', '연료로 쓰면 소모한다', 'Using it as fuel consumes it'),
    ('CAMP_TINDER_USE HEARTH_TINDER INDUSTRIAL_TINDER', '불이 꺼진 대상과 점화 도구가 필요하며 불쏘시개는 소모된다', 'An unlit target and an igniter are required; the tinder is consumed'),
    ('CAMP_PETROL_USE HEARTH_PETROL', '연료가 있고 꺼진 대상에 잔량이 있는 휘발유와 점화 도구를 함께 쓴다', 'Use petrol with remaining uses and an igniter on an unlit, fueled target'),
    ('TIRE_INFLATION', '타이어 펌프로 장착 타이어에 공기를 넣는다', 'A tire pump adds air to an installed tire'),
    ('TIRE_DEFLATION', '장착 타이어의 남은 공기를 펌프 없이 뺀다', 'Remaining air can be released from an installed tire without a pump'),
    ('COMPOST_TRANSFER', '퇴비와 여유 공간이 있는 통·포대 사이에서 옮기며 포대가 일부만 채워질 수 있다', 'Compost transfers between a bin and bag with supply and capacity; the bag may fill only partially'),
    ('WEAPON_ATTACHMENT_TOOL', '사용 가능한 드라이버로 호환 부착물을 장착·제거하며 도구는 보존된다', 'A usable screwdriver installs or removes compatible attachments and is kept'),
):
    for _name in _names.split():
        USE_QUALIFIERS[getattr(source, _name)] = (_ko, _en)


def use_qualifier(q, locale):
    predicate = q['payload']['predicate']
    if predicate in USE_QUALIFIERS:
        return pair(USE_QUALIFIERS[predicate], locale)
    # No automatic execution-prose fallback. Missing expression is a defect,
    # never an evidence gap or accepted absence.
    raise ValueError('unimplemented public qualifier: ' + predicate)


for _names, _ko, _en in (
    ('ROPE_MAKING', '시트 로프 제작이 허용된 직물·시트를 재료로 쓴다', 'Eligible fabric or sheets serve as material for making sheet rope'),
    ('MAP_REVEAL', '지도에 지정된 구역을 알려진 구역으로 표시한다. 방문 기록이나 안전한 경로를 뜻하지 않는다', 'It marks the map’s designated area as known; this is not a record of visiting or a safe route'),
    ('BATTER_TEST', '케이크·머핀에는 익히지 않은 재료를 쓴다. 달걀 재료는 신선하면 원래 분량, 그 외에는 원래 분량의 4분의 3 이상이 필요하다', 'Cake and muffin preparation rejects cooked participants. Egg ingredients need their original portion when fresh, or at least three quarters otherwise'),
    ('PAINTING PAINT_ACTIONS', '붓과 해당 색 페인트가 필요하며 페인트는 소모한다', 'It requires a brush and paint in the corresponding color; paint is consumed'),
    ('UMBRELLA_CHANGE', '열린 형태와 닫힌 형태 사이에서 상태를 보존해 바꿀 수 있다. 개방만으로 비를 막는 효과는 확인되지 않았다', 'It can change between open and closed forms while retaining condition; opening alone does not establish rain protection'),
    ('SIMPLE_TRANSFORMATION', '해당 제작법의 재료로 선언된 결과물을 만든다', 'It supplies material for the result declared by the corresponding recipe'),
    ('CARPENTRY_MATERIAL STAGE_ACTION', '선택한 건축물에 맞는 재료·목공 기술·도구와 배치 조건이 필요하다. 단계식 건축에는 호환되는 이전 단계가 필요하다', 'Construction requires the selected object’s materials, carpentry skill, tools and placement conditions; staged building also needs a compatible previous stage'),
    ('FORGE_PREPARATION', '배운 금속 단조 제작법의 재료·보존 도구와 대장장이 기술이 필요하다. 완성 무기의 상태는 해당 제작법과 기술·확률에 따라 달라진다', 'The learned forging recipe requires its materials, kept tools and Blacksmith skill; weapon condition depends on the applicable recipe, skill and chance'),
    ('NOTE_EDIT', '쓰기에는 맞는 필기구가 필요하고 타인의 소유 잠금과 편집 잠금이 없어야 한다', 'Writing needs a matching implement, no other-user ownership lock and editing unlocked'),
    ('FLOOR_GLASS_PICKUP', '바닥의 깨진 유리를 치울 수 있다', 'It can clear broken glass from the floor'),
    ('BANDAGE_MATERIALS', '해당 붕대 재료 제작법이 받는 천·솜과 소독제·술 또는 물 든 조리 용기를 함께 쓴다', 'Use the cloth or cotton accepted by the bandaging-material recipe with disinfectant, liquor or a water-filled cooking vessel'),
    ('CAMP_KIT_PREPARATION', '판자 3개 또는 통나무 2개를 쓰는 모닥불 키트 제작법에서 허용된 천·시트·종이류·잔가지 중 하나를 함께 쓴다', 'Campfire-kit recipes use three planks or two logs with an accepted cloth, sheet, paper item or twigs'),
    ('POULTICE_USE', '붕대가 없고 다른 찜질제가 적용되지 않은 치료 가능 부위에 소모해 해당 찜질제 수치를 설정한다. 수치는 응급처치 기술과 확률에 따라 달라진다', 'It is consumed on an eligible unbandaged part without another poultice to set its corresponding poultice factor, depending on First Aid skill and chance'),
    ('LOG_BINDING', '통나무 2·3·4개를 밧줄류 두 개로 묶는다. 풀면 해당 통나무와 저장된 묶기 재료를 반환하며 이전 재료 기록이 없으면 밧줄 두 개를 반환한다', 'Two, three or four logs are bundled with two rope-tagged supplies. Unstacking returns the corresponding logs and recorded binding types, or two ropes if no binding record exists'),
    ('WELDING_CONSTRUCTION', '배운 금속 건축물의 용접 기술·재료와 토치·용접 마스크가 필요하다. 용접봉 필요량은 작업의 토치 사용량에 따라 달라진다', 'The learned metal construction requires its welding skill, materials, torch and welding mask; welding-rod requirements depend on torch uses'),
    ('STITCHING', '깊은 상처를 봉합할 수 있다', 'It can stitch a deep wound'),
    ('GLASS_REMOVAL', '상처에 박힌 유리를 제거할 수 있다', 'It can be used to remove glass embedded in a wound'),
    ('BULLET_REMOVAL', '몸에 박힌 총알을 제거할 수 있다', 'It can be used to remove an embedded bullet'),
    ('WEIGHT_EXERCISE', '해당 웨이트 운동에 쓰며 지구력 조건을 충족해야 한다', 'It serves in its corresponding weight exercise, subject to endurance requirements'),
    ('POULTICE_PREPARATION', '해당 식물 다섯 개와 보존하는 절구·공이로 찜질제를 만든다. 야생마늘 제작법은 일반 제작 목록에서 숨겨져 있다', 'The recipe uses five of its named plant with a kept mortar and pestle to prepare poultice. Wild-garlic recipes are hidden from the ordinary crafting list'),
    ('TENT_KIT_PREPARATION', '방수포와 나무 막대 2개, 텐트 말뚝 4개 또는 말뚝 4개로 텐트 키트를 만든다', 'A tarp, two wooden sticks and either four tent pegs or four stakes supply a tent kit'),
    ('JAR_BOX_OPENING', '상자를 열어 빈 병 6개와 병뚜껑 6개를 꺼낸다', 'Opening the box provides six empty jars and six lids'),
    ('WIRE_RECOVERY', '철사 회수 제작법의 재료이나 결과 표기의 해석이 미확정이어서 회수량은 확인되지 않았다', 'It is material for the wire-recovery recipe; the unresolved result notation leaves the yield unconfirmed'),
    ('SPRAY_PREPARATION', '빈 원예 분무기에 우유류를 넣어 흰가루병 약을, 물과 담배를 넣어 해충 약을 만든다. 해당 농사 제작법 지식과 재료 분량 조건이 필요하다', 'An empty gardening spray can takes milk for mildew cure or water and cigarettes for flies cure, under the Farming recipe’s knowledge and portion requirements'),
    ('PADLOCK_USE', '문이 아닌 잠기지 않은 구조물 중 자물쇠를 지원하는 곳에 설치하며 대응 열쇠를 얻는다', 'It locks an eligible unlocked non-door structure and supplies matching keys'),
    ('ESCAPE_ROPE_REMOVE', '로프가 달린 대응 창문·문 등의 로프를 제거한다. 같은 상태의 로프 회수는 보장되지 않는다', 'It removes an escape rope from a supported attachment; recovery of the same item condition is not guaranteed'),
    ('ESCAPE_ROPE_INSTALL', '지상층보다 높은 지원 창문·틀·넘을 수 있는 구조물에 못과 충분한 한 종류의 로프를 사용한다. 로프와 시트 로프의 수량은 합치지 않는다', 'Use nails and enough of one rope type on a supported window, frame or hoppable attachment above ground level; rope and sheet-rope counts are not combined'),
    ('CAMP_PLACEMENT', '키트에 맞는 빈 공간에 설치하며 별도 망치는 필요하지 않다', 'The kit needs suitable clear space and no separate hammer'),
    ('TENT_PLACEMENT', '텐트는 인접한 빈 두 칸을 사용한다', 'A tent needs two adjacent clear squares'),
    ('MATTRESS_PREPARATION', '보존하는 바늘과 실 5, 시트 5개, 베개 5개를 매트리스 제작에 쓴다', 'A kept needle, five thread units, five sheets and five pillows supply mattress crafting'),
    ('PLUMBING', '사용 가능한 파이프렌치로 외부 물 공급이 허용된 실내 설비를 연결한다. 연결 자체로 정수 효과는 확인되지 않는다', 'A usable pipe wrench connects eligible indoor fixtures to external water; the connection does not establish purification'),
    ('SPLINTING', '골절 부위에 완성 부목 또는 찢어진 천과 판자·나뭇가지·나무 막대 중 하나를 소모한다', 'For fractures outside the head and torso, consume a finished splint or ripped sheets with a plank, tree branch or wooden stick'),
):
    for _name in _names.split():
        USE_QUALIFIERS[getattr(source, _name)] = (_ko, _en)
USE_QUALIFIERS.update({
    COOKING_ELIGIBILITY: USE_QUALIFIERS[source.COOKING_ACTION],
    READING_ELIGIBILITY: USE_QUALIFIERS[source.READ_SELECTION],
    'A supported woodworking transformation must have its inputs, tools, skill and recipe eligibility requirements satisfied.':
        ('해당 목재 가공에 맞는 재료·도구·기술·제작법이 필요하다', 'The woodworking transformation requires its corresponding inputs, tools, skill and recipe'),
    'For a compatible damaged item and available repair materials; repair eligibility and outcome depend on the fixing rules.': USE_QUALIFIERS[source.FIXING_ACTION],
    'The object requests this tool; inventory, reachability, world object and multiplayer permission checks must hold.':
        ('해당 가구가 요구하는 도구이며 멀티플레이 권한 제한을 따른다', 'It is the tool required by the furniture, subject to multiplayer permissions'),
    'Only for a compatible previous construction stage, with required skills, tools and materials available; material consumption excludes construction cheat mode.': USE_QUALIFIERS[source.STAGE_ACTION],
    'For the active wooden-cross branch, the hammer is not broken and world placement/material requirements hold.':
        ('나무 십자가 제작에는 파손되지 않은 망치와 해당 재료·배치 조건이 필요하다', 'A wooden cross requires an unbroken hammer and its materials and placement conditions'),
    'For the active wooden-cross or log-wall branch requiring this material; log-wall binding chooses sufficient sheets (clean/dirty), otherwise twine, otherwise rope. World placement and material availability must hold; cheat mode does not consume material.':
        ('나무 십자가·통나무 벽의 해당 재료로 쓴다. 벽을 묶을 때는 충분한 시트류, 노끈, 밧줄 순서로 가능한 재료를 사용한다', 'It supplies the corresponding wooden-cross or log-wall material. Wall binding uses sufficient sheets, otherwise twine, otherwise rope'),
})

for _activity, _wording in {
    'spear_crafting': ('판자 또는 나뭇가지와 허용된 절삭 도구로 창을 만든다. 결과 상태는 목공 기술과 확률에 따라 달라지며 보존 도구도 마모되거나 사라질 수 있다', 'A plank or tree branch and an accepted cutting tool supply a crafted spear. Its condition depends on carpentry skill and chance; kept tools can wear or be lost'),
    'spear_upgrade': ('제작한 창·해당 부착물·덕트 테이프를 사용한다. 결과 상태는 창과 부착 무기의 상태에 따라 달라진다', 'Use a crafted spear, its corresponding attachment and duct tape; result condition depends on the spear and participating weapon condition'),
    'spear_reclaim': ('창에서 부착물을 떼어 회수할 수 있다', 'The attachment can be recovered from the spear'),
}.items():
    USE_QUALIFIERS[source.SPEAR_CONDITIONS[_activity]] = _wording
USE_QUALIFIERS.update({
    'The clothing is in the character inventory and is worn at its configured body location.': USE_QUALIFIERS[source.WEARING],
    'The body is wet, the towel has uses remaining, and the towel is in inventory.': USE_QUALIFIERS[source.BODY_DRYING],
    'For water with remaining portions: manual drinking is offered above thirst 0.1; consumed portions require positive thirst and the container to remain in inventory.': USE_QUALIFIERS[source.WATER_DRINKING],
    'A body part is eligible for bandaging; the material remains in inventory and the patient does not move out of reach.': USE_QUALIFIERS[source.BANDAGE_APPLICATION],
    'Reading progress yields a multiplier above the current one, and the reader is within this book\'s supported training level range.': USE_QUALIFIERS[source.READ_MAXIMUM],
    'Storage requires room and item admission; transfer requires accessible distinct source/destination, permitted removal and applicable multiplayer restrictions.': ('용량 안에서 허용된 물품을 넣고 꺼내며 접근·멀티플레이 제한을 따른다', 'Admitted items can be stored and retrieved within capacity, subject to access and multiplayer restrictions'),
})

for _names, _ko, _en in (
    ('NOTE_IMPLEMENT', '쓰기에는 필기구가 필요하며 타인의 소유 잠금과 편집 잠금이 없어야 한다', 'Writing needs an implement, no other-user ownership lock and editing unlocked'),
    ('SHOVEL_SMITHING', '대장장이 기술 6과 배운 제작법·모루·망치·집게로 삽류를 단조한다. 삽에는 철 주괴 90과 손잡이, 손삽에는 철 주괴 50을 사용하며 도구는 보존한다', 'Forging shovels requires Blacksmith 6, the learned recipe, an anvil, hammer and tongs. A shovel uses 90 iron-ingot units and a handle; a hand shovel uses 50 iron-ingot units. Tools are kept'),
    ('VEHICLE_SEATING', '차량에 장착한 비어 있는 좌석에 앉거나 자리를 옮길 수 있다. 차량에서 내리려면 정지해야 한다', 'An installed unoccupied vehicle seat permits sitting or seat switching; exiting requires the vehicle to stop'),
    ('WELDED_PARTS', '배운 금속 부품 제작법과 금속 재료·토치·보존하는 용접 마스크가 필요하다. 금속 막대에는 용접 2, 판 전환에는 용접 4가 필요하며 큰 판과 작은 판의 전환은 손실 없는 역변환이 아니다', 'The learned metal-part recipe requires metal inputs, a torch and a kept welding mask. Bars need MetalWelding 2 and sheet conversions need 4; conversions between small and large sheets are not lossless reverses'),
    ('WOOD_SHAPING', '말뚝 제작은 나뭇가지와 허용된 칼을, 구멍 뚫은 판자 제작은 판자·통나무와 허용된 드라이버·깎인 돌 대안을 사용하며 도구는 보존한다', 'Stake crafting uses a branch and an accepted knife; drilled-plank crafting uses its plank or log input and accepted screwdriver or chipped-stone alternative. Tools are kept'),
    ('FROG_PREPARATION', '허용된 날카로운 칼 또는 중식도로 개구리를 손질해 개구리 고기를 얻으며 도구는 보존한다', 'An accepted sharp knife or meat cleaver prepares the frog into frog meat; the tool is kept'),
    ('BANDAGE_RECIPE_WASHING', '해당 더러운 붕대·천·직물 조각을 오염되지 않은 물로 씻어 대응하는 깨끗한 형태로 만든다', 'The corresponding dirty bandage, rag or fabric strips can be washed with untainted water into their clean form'),
    ('DIRTY_BANDAGING', '붕대를 댈 수 있는 부위에 적용하면 재료를 소모한다. 더러운 재료라는 이름만으로 감염 상태가 확정되지는 않는다', 'Applying it to an eligible body part consumes the material; a dirty type name alone does not establish infection'),
    ('SAWN_WOOD', '톱으로 통나무를 판자 3개로, 판자를 튼튼한 막대 8개로 가공하는 해당 제작법에 쓴다. 톱은 보존한다', 'It serves in the applicable recipe for sawing a log into three planks or a plank into eight sturdy sticks; the saw is kept'),
    ('ESCAPE_ROPE_CLIMB', '설치된 로프와 힘 조건이 맞으면 올라가는 데 쓸 수 있다. 안전한 도착이 보장되지는 않는다', 'It can be used for ascent when the installed rope and strength requirements allow it; safe arrival is not guaranteed'),
):
    for _name in _names.split():
        USE_QUALIFIERS[getattr(source, _name)] = (_ko, _en)
USE_QUALIFIERS['An eligible fabric or named sheet is supplied to the recipe; recovered material and quantity depend on fabric, covered parts, dirt/blood and tailoring state.'] = USE_QUALIFIERS[source.FABRIC_ACTION]

USE_QUALIFIERS[source.BANDAGE_WASHING] = ('물 공급원에서 씻어 대응하는 깨끗한 붕대·직물 형태로 바꿀 수 있다', 'Washing at a water source produces the corresponding clean bandage or fabric form')
USE_QUALIFIERS[source.SMITHING_PARTS] = ('배운 문손잡이·경첩 제작법과 대장장이 기술 3, 철 주괴 15, 모루·볼핀 해머·집게가 필요하며 도구는 보존한다', 'The learned doorknob or hinge recipe requires Blacksmith 3, 15 iron-ingot units, an anvil, ball-peen hammer and tongs; tools are kept')

for _names, _ko, _en in (
    ('PANEL_INSTALL', '호환 차량의 빈 부품 자리에 장착하며 해당 도구·제작 지식이 필요하다. 기술과 부품 상태에 따라 실패하거나 손상될 수 있다', 'It installs in a compatible empty vehicle slot with the applicable tools and knowledge; skill and part condition affect failure and damage'),
    ('PANEL_REMOVE', '호환 차량에 장착된 부품을 해당 도구·제작 지식으로 탈거하며 실패하거나 부품이 손상될 수 있다', 'The installed compatible vehicle part can be removed with its required tools and knowledge; failure or part damage is possible'),
    ('DEVICE_RETRIEVAL', '회수를 허용하는 설치 장치를 다시 가져올 수 있다', 'A placed device that permits retrieval can be recovered'),
    ('DEVICE_PLACEMENT DEVICE_WORLD_PLACEMENT', '설치를 허용하는 장치를 현재 칸에 놓을 수 있다', 'A placement-enabled device can be placed on the current square'),
    ('VEHICLE_STORAGE', '차량에 장착된 대응 수납 부품에서 허용된 물품을 보관한다', 'It stores admitted items in the corresponding installed vehicle storage part'),
    ('DYE_APPLICATION', '존재하는 머리카락이나 수염을 염색약 색으로 바꾸며 염색약을 소모한다', 'It consumes dye to color existing hair or beard in the dye’s color'),
    ('REMOTE_LINK', '대응하는 조종기와 장치를 함께 소지해 연결하며 연결 ID가 맞아야 원격으로 작동시킬 수 있다', 'A compatible controller and device carried together can be linked; remote triggering requires their matching link ID'),
    ('KEY_ALARM', '맞는 차량의 첫 문 개방 경보를 피하지만 이미 울리는 경보는 끄지 않는다', 'It avoids the matching vehicle’s first door-opening alarm but does not stop a ringing alarm'),
    ('TRAP_PLACEMENT', '배치 가능한 곳에 해당 덫을 설치한다. 설치 자체로 포획하지는 않는다', 'The trap can be placed at an eligible location; placement alone does not catch an animal'),
    ('ASH_CLEARING', '삽이나 빗자루로 탄 바닥의 재를 치운다', 'A shovel or broom clears ash from burnt floors'),
    ('CHOPPING', '사용 가능한 도끼로 나무를 벨 수 있다', 'A usable axe can chop trees'),
    ('WOOD_BARRICADE', '바리케이드를 받는 문과 창문에 망치·판자·못을 사용한다', 'Use an accepted hammer, planks and nails on a door or window that permits barricading'),
    ('WOOD_UNBARRICADE', '해당 철거 도구로 바리케이드 판자를 떼어내며 못은 돌려받지 못한다', 'An accepted removal tool takes off barricade planks without returning nails'),
    ('METAL_BARRICADE', '문과 창문에 토치와 금속판 또는 금속 막대로 바리케이드를 설치하며 용접 마스크는 필요하지 않다', 'A torch and metal sheet or bars barricade doors or windows without requiring a welding mask'),
    ('METAL_UNBARRICADE', '토치를 소모해 금속 바리케이드를 제거하며 온전한 재료 회수는 보장되지 않는다', 'Torch uses remove metal barricades; full-condition material recovery is not guaranteed'),
    ('NOTE_LIMITS', '메모는 지정된 쪽 수와 페이지의 글자 제한 안에서 작성한다', 'Notes are written within the declared page count and page text limits'),
    ('SEED_EXTRACTION', '씨앗 봉지를 열어 낱알 씨앗을 꺼내며 봉지 자체를 파종하지는 않는다', 'Open the packet to obtain loose seeds; the packet itself is not sown'),
    ('SOWING', '아직 씨가 없는 경작 고랑에 해당 작물의 낱알 씨앗을 심는다', 'The crop’s loose seeds are sown in an unseeded plowed furrow'),
    ('FERTILIZING', '살아 있는 파종 작물에 비료를 주며 과다 시비하면 썩을 수 있다', 'It fertilizes living seeded crops; over-fertilization can cause rot'),
    ('MAKEUP_USE MAKEUP_LIFECYCLE', '화장품과 손에 들거나 근처에 있는 거울이 필요하다. 화장품 사용량은 소모하지 않는다', 'It requires the cosmetic and a held or nearby mirror; cosmetic uses are not spent'),
    ('BEARD_GROOMING', '사용 가능한 도구로 기존 수염을 다듬거나 면도한다', 'A usable tool trims or shaves existing beard'),
    ('HAIR_GROOMING', '현재 머리 길이가 허용하는 스타일로 손질한다', 'It supports grooming styles allowed by current hair length'),
    ('SPRAY_TREATMENT', '해당 병해충이 있는 작물에 뿌려 해당 수치를 사용당 5씩 최소 0까지 낮춘다', 'It treats a crop with the corresponding infestation, reducing that level by five per use to a minimum of zero'),
    ('CODE_LOCK_USE', '잠기지 않은 지원 구조물에 번호를 정해 설치한다', 'It installs on an eligible unlocked structure with a chosen code'),
    ('NET_REMOVAL', '설치된 어망을 회수하되 원래 물품 상태가 보존되지는 않는다', 'The placed fishing net can be recovered without retaining its original item state'),
):
    for _name in _names.split():
        USE_QUALIFIERS[getattr(source, _name)] = (_ko, _en)
USE_QUALIFIERS.update({
    'The consumed water is tainted, current poison level is below 20, and current sickness is below 0.3.':
        ('오염수를 마셨을 때 중독 수치가 20 미만이고 질병 수치가 0.3 미만이면 해당한다', 'This applies when drinking tainted water with poison below 20 and sickness below 0.3'),
    'The dye remains in inventory; hair exists and is not Bald, or the beard model exists and is nonempty.': USE_QUALIFIERS[source.DYE_APPLICATION],
    PILL_INVENTORY: USE_QUALIFIERS[source.PILL_TAKING],
    'A compatible empty flashlight or duck device is supplied; transferred charge is the charge remaining in the battery selected by the recipe.':
        ('대응하는 빈 손전등·오리 기기에 선택된 건전지의 남은 충전량을 전달한다', 'It transfers the selected battery’s remaining charge to a compatible empty flashlight or duck device'),
})
for _count, _predicate in source.SOW_COUNTS.items():
    USE_QUALIFIERS[_predicate] = (f'고랑 하나에 낱알 씨앗 {_count}개를 쓴다', f'Use {_count} loose seeds per furrow')
for _kind, _wording in {
    'gastank': ('렌치·드라이버와 기본 정비 지식이 필요하며 탈거하려면 탱크가 비어 있어야 한다', 'It requires a wrench, screwdriver and Basic Mechanics knowledge; the tank must be empty for removal'),
    'seat': ('드라이버와 기본 정비 지식이 필요하며 탈거하려면 좌석 수납 공간이 비어 있어야 한다', 'It requires a screwdriver and Basic Mechanics knowledge; seat storage must be empty for removal'),
}.items():
    USE_QUALIFIERS[source.VEHICLE_EXCHANGE_REQUIREMENTS[_kind]] = _wording
for _kind, _wording in {
    'brake': ('잭·렌치와 기본 정비 지식이 필요하다. 탈거하려면 대응 타이어를 먼저 제거해야 한다', 'It requires a jack, wrench and Basic Mechanics knowledge. Removal requires the matching tire to be removed first'),
    'suspension': ('잭·렌치와 기본 정비 지식이 필요하다. 탈거하려면 대응 타이어를 먼저 제거해야 한다', 'It requires a jack, wrench and Basic Mechanics knowledge. Removal requires the matching tire to be removed first'),
    'muffler': ('렌치와 기본 정비 지식으로 교체한다', 'It can be exchanged with a wrench and Basic Mechanics knowledge'),
    'tire': ('잭과 십자 렌치를 사용하며 도구는 보존한다. 장착하려면 대응 브레이크·서스펜션이 있어야 한다', 'Use a jack and lug wrench, keeping both tools. Installation requires the matching brake and suspension'),
}.items():
    USE_QUALIFIERS[source.RUNNING_EXCHANGE[_kind]] = _wording

for _names, _ko, _en in (
    ('PANEL_DOOR', '정지한 차량의 장착 문·덮개를 잠금 해제한 뒤 여닫을 수 있다', 'An installed door or cover on a stopped vehicle can be opened or closed after unlocking'),
    ('PANEL_LOCK', '장착 문 잠금 장치를 접근 위치에 따른 열쇠 조건으로 조작한다', 'It controls an installed door lock under the access position’s key requirements'),
    ('PANEL_WINDOW', '파손되지 않은 장착 개폐식 창문을 여닫을 수 있다', 'An unbroken installed openable window can be opened or closed'),
    ('VEHICLE_FUEL', '차량에 장착해 연료를 보관하며 엔진이 꺼져 있으면 호환 용기로 넣거나 뺄 수 있다', 'Once installed, it stores vehicle fuel; a compatible container can add or siphon fuel with the engine stopped'),
    ('VEHICLE_FUEL_ENGINE', '작동 중인 엔진에 연료를 공급하며 탱크 상태가 70 미만이면 연료가 추가로 줄어들 수 있다', 'It supplies fuel to a running engine; tank condition below 70 can cause additional fuel loss'),
    ('DOOR_KEY_USE', '맞는 닫힌 문의 잠금을 조작하며 열쇠는 소모하지 않는다', 'It operates a matching closed door’s lock without consuming the key'),
    ('REMOTE_TRIGGER', '연결 ID가 맞고 조종 범위 안에 있는 장치에 원격 작동을 요청한다', 'It requests remote activation of a device with a matching link ID within range'),
    ('DEVICE_DELAY DEVICE_TIMER_CONTROL', '타이머를 지원하는 장치에 양수의 지연 시간을 설정한다', 'A positive delay can be set on a device supporting a timer'),
    ('CODE_UNLOCK', '맞는 번호를 사용해 설치된 번호 자물쇠를 제거한다', 'The matching code removes an installed combination lock'),
):
    for _name in _names.split():
        USE_QUALIFIERS[getattr(source, _name)] = (_ko, _en)

USE_QUALIFIERS[source.VEHICLE_KEY_USE] = ('운전석에서 맞는 차량의 시동·점화장치를 조작한다', 'It operates a matching vehicle’s start and ignition controls from the driver’s seat')

USE_QUALIFIERS[source.KEY_MECHANICS] = ('맞는 차량의 정비 작업에서 열쇠 요구를 충족한다', 'It meets the key requirement for a matching vehicle’s mechanics operation')

# General ignition prerequisites belong to the action, not to the tinder item.
for _name in ('CAMP_TINDER_USE', 'HEARTH_TINDER', 'INDUSTRIAL_TINDER'):
    USE_QUALIFIERS[getattr(source, _name)] = ('불쏘시개로 쓰면 소모한다', 'Using it as tinder consumes it')

# Conditions state the restriction, not a second copy of the action. In
# particular a consumption predicate never turns an edible into a drink.
USE_QUALIFIERS[source.CONSUMING] = ('포만 상태가 허용해야 한다', 'Satiety must permit consumption')
USE_QUALIFIERS[source.DEVICE_ASSEMBLY] = ('해당 장치 제작법의 학습·전기 기술 조건이 필요하다', 'The corresponding device recipe’s knowledge and electrical-skill requirements apply')
USE_QUALIFIERS[source.FISHING_EXECUTION] = ('포획은 물고기 잔량과 확률에 따라 달라진다', 'Catches depend on remaining fish stock and chance')
USE_QUALIFIERS[source.ROD_FISHING] = ('물고기 종류·장소·기술에 따라 맞는 미끼와 포획 결과가 달라진다', 'Accepted bait and catches depend on fish type, location and skill')
USE_QUALIFIERS[source.ELECTRONIC_SALVAGE] = ('맞는 드라이버로 분해해 전자 부품을 회수한다', 'Dismantling with a matching screwdriver recovers electronic parts')
USE_QUALIFIERS[source.RADIO_DISMANTLING] = USE_QUALIFIERS[source.ELECTRONIC_SALVAGE]
USE_QUALIFIERS[source.TRAP_ASSEMBLY] = ('선택한 덫 제작법의 학습·재료 조건과 해당 제작법에서 요구하는 톱·목공·덫 기술 조건이 필요하다', 'The selected trap recipe’s knowledge, materials and applicable saw, carpentry and trapping requirements apply')
USE_QUALIFIERS[source.FORGE_PREPARATION] = ('해당 금속 단조 제작법의 학습·대장장이 기술과 모루·보존 도구가 필요하다', 'The forging recipe requires its knowledge, Blacksmith skill, anvil and kept tools')
EFFECTS.update({
    ('splint_factor', 'set_doctor_half'): ('부목의 치료 계수는 응급처치 기술에 따라 달라진다', 'The splint treatment factor depends on First Aid skill'),
    ('poultice_factor', 'set_doctor_random'): ('찜질제 수치는 응급처치 기술과 확률에 따라 달라진다', 'The poultice factor depends on First Aid skill and chance'),
    ('treatment_panic', 'add_50'): ('치료자가 공포를 느낄 수 있다', 'The caregiver can panic'),
    ('bandage_patient_infection', 'set_true'): ('상처를 감염시킬 수 있다', 'It can infect the treated wound'),
    ('burn_wash_requirement', 'clear'): ('화상을 씻는 데 쓴다', 'It is used to clean a burn'),
    ('additional_pain', 'add_60_minus_doctor_level'): ('치료 시 통증이 생기며 응급처치 기술에 따라 달라진다', 'Treatment causes pain depending on First Aid skill'),
    ('applied_bandage_life', 'set_skill_random_plus_power'): ('붕대의 유지 수치는 재료와 응급처치 기술에 따라 달라진다', 'Bandage life depends on the material and First Aid skill'),
})

# Recipe quantities and general action validity belong to the recipe/action
# view. These clauses retain only distinctions relevant to the supplied use.
USE_QUALIFIERS[source.CAMP_KIT_PREPARATION] = ('판자 또는 통나무와 함께 모닥불 키트 제작에 쓴다', 'It supplies campfire-kit crafting with planks or logs')
USE_QUALIFIERS[source.CANDLE_LIGHT_RECIPE] = ('초와 허용하는 발화 도구를 함께 쓴다', 'A candle and an accepted fire-starting tool are used together')
USE_QUALIFIERS[source.CANDLE_EXTINGUISH_RECIPE] = ('켜진 초를 대상으로 한다', 'It applies to a lit candle')
USE_QUALIFIERS['The object requests this tool; inventory, reachability, world object and multiplayer permission checks must hold.'] = ('해당 가구가 요구하는 도구로 쓴다', 'It serves as the tool required by the furniture')

USE_QUALIFIERS[source.SHOVEL_SMITHING] = ('대장장이 기술 6과 배운 단조 제작법이 필요하다', 'It requires Blacksmith 6 and the learned forging recipe')

for _name, _ko, _en in (
    ('FOOD_SLICING', '해당 음식 손질에 맞는 도구를 사용한다', 'Use the tool accepted for preparing that food'),
    ('COOKED_SLICING', '익었거나 탄 파이·케이크와 지정된 손질 도구를 사용한다', 'Use cooked or burnt pie or cake and its accepted cutting tool'),
    ('DOUGH_SLICING', '익힌 빵 반죽과 지정된 칼을 사용한다', 'Use cooked bread dough and its accepted knife'),
    ('PIZZA_SLICING', '피자 손질 도구를 사용하며, 완성 피자 형식 외에는 익었거나 탄 피자가 필요하다', 'Use a pizza-cutting tool; forms other than ready-made pizza must be cooked or burnt'),
    ('FISH_PREPARATION', '손질 도구가 필요하며 생선 무게가 0.6보다 커야 한다', 'A cutting tool is required and the fish must weigh more than 0.6'),
    ('ANIMAL_PREPARATION', '해당 작은 동물 사체에 맞는 칼을 사용한다', 'Use a knife accepted for that small-animal carcass'),
    ('SANDWICH_PREPARATION', '빵 조각은 신선도에 따른 남은 양 조건을 충족해야 한다', 'Bread slices must retain the portion required for their freshness'),
    ('GRAIN_VESSEL_PREPARATION', '물 든 냄비·소스팬과 함께 쓴다', 'Use it with a water-filled pot or saucepan'),
    ('OATMEAL_PREPARATION', '오트밀을 만들 때는 그릇과 귀리·물을 함께 쓴다', 'For oatmeal, a bowl, oats and water are used together'),
    ('MOLOTOV_ASSEMBLY', '제작법에 맞는 병·천·연료를 쓰며 잔량을 검사하는 제작법에서는 연료가 가득 차 있어야 한다', 'Use the recipe’s accepted bottle, cloth and fuel; fuel must be full where the recipe checks fullness'),
    ('PLASTER_MIXING', '양동이에 석고 가루와 물을 혼합한다', 'Plaster powder and water are mixed in an accepted bucket'),
    ('CAKE_PAN_PREPARATION', '케이크 반죽을 팬에 담는 데 쓴다', 'It is used to put cake batter into a pan'),
    ('EGG_PACKING', '익거나 타지 않은 달걀을 받으며 냉동 달걀도 허용한다', 'It accepts eggs that are neither cooked nor burnt, including frozen eggs'),
    ('OMELETTE_PREPARATION', '오믈렛에는 익히지 않은 달걀을 쓰며 신선도별 남은 양 조건을 충족해야 한다', 'For omelettes, eggs must be uncooked and retain the portion required for their freshness'),
    ('MUFFIN_PORTIONING', '익힌 머핀 트레이에서 꺼낸다', 'Muffins are removed from a cooked tray'),
    ('BISCUIT_PORTIONING', '익었거나 탄 트레이에서 꺼낸다', 'Biscuits or cookies are removed from a cooked or burnt tray'),
    ('BEAN_PREPARATION', '닫힌 통조림에는 캔 따개가 필요하다', 'A closed can requires a can opener'),
    ('CANDY_OPENING', '포장을 열어 사탕을 꺼낸다', 'The package is opened to obtain candy'),
    ('SHOTGUN_SHORTENING', '대응하는 산탄총과 지정된 톱을 사용한다', 'Use the corresponding shotgun and specified saw'),
    ('TORCH_REFILL_RECIPE', '토치의 빈 연료 공간에 프로판을 채운다', 'Propane refills a blowtorch’s available fuel capacity'),
    ('SMITHING_PARTS', '배운 문손잡이·경첩 제작법과 대장장이 기술 3이 필요하다', 'It requires the learned door-fitting recipe and Blacksmith 3'),
    ('WEIGHT_EXERCISE', '운동의 지구력 조건을 충족해야 한다', 'The exercise’s endurance requirements apply'),
):
    USE_QUALIFIERS[getattr(source, _name)] = (_ko, _en)

for _name, _ko, _en in (
    ('CAMP_IGNITER', '모닥불 점화에 불쏘시개 또는 휘발유와 함께 쓴다', 'It is used with tinder or petrol to light a campfire'),
    ('NET_PLACEMENT', '물에 설치해 사용한다', 'It is used placed in water'),
    ('MEAL_UTENSIL', '식사에 필수인 도구는 아니다', 'The utensil is optional for eating'),
    ('TRAP_CONTROLS', '설치한 덫에서 미끼·포획물을 회수할 수 있다', 'Bait and catches can be retrieved from the placed trap'),
):
    USE_QUALIFIERS[getattr(source, _name)] = (_ko, _en)

USE_QUALIFIERS[source.WOOD_SHAPING] = ('해당 가공에 쓰는 도구는 소모하지 않는다', 'The tool used for the corresponding woodworking recipe is kept')
USE_QUALIFIERS[source.COOKED_SLICING] = ('대상 파이·케이크는 익었거나 탄 상태여야 한다', 'The target pie or cake must be cooked or burnt')
USE_QUALIFIERS[source.DOUGH_SLICING] = ('대상 빵 반죽은 익힌 상태여야 한다', 'The target bread dough must be cooked')
USE_QUALIFIERS[source.FISH_PREPARATION] = ('손질할 생선의 무게가 0.6보다 커야 한다', 'The fish being prepared must weigh more than 0.6')
USE_QUALIFIERS[source.SPEAR_FISHING] = ('물가에서 미끼 없이 쓸 수 있으며 포획은 보장되지 않는다', 'It can be used at water without bait; catches are not guaranteed')
USE_QUALIFIERS[source.SPEAR_FISHING_WEAR] = ('이 아이템의 내구도가 감소할 수 있다', 'This item can lose condition')

USE_QUALIFIERS[source.SPRAY_PREPARATION] = ('해당 작물 치료제 제작법 지식이 필요하다', 'The corresponding crop-treatment recipe must be learned')

USE_QUALIFIERS[source.POULTICE_PREPARATION] = ('절구와 공이를 사용한다', 'It uses a mortar and pestle')
USE_QUALIFIERS[source.POULTICE_USE] = ('붕대나 다른 찜질제가 없는 치료 가능 부위에 적용한다', 'It applies to an eligible body part without a bandage or another poultice')

EFFECTS[('fishing_rod_form', 'replace_on_line_break')] = ('낚싯줄이 끊어지면 파손되고 미끼를 잃는다', 'If the line breaks, it breaks and the bait is lost')
INLINE_CONDITIONS[(source.ROD_LINE_BREAK, None)] = EFFECTS[('fishing_rod_form', 'replace_on_line_break')]
USE_QUALIFIERS[source.ROD_LINE_BREAK] = (
    '낚싯줄이 끊어지면 파손되고 미끼를 잃는다',
    'If the line breaks, it breaks and the bait is lost')
USE_QUALIFIERS[source.STONE_TOOL_WEAR] = (
    '건축에 사용하면 마모될 수 있다', 'It may wear when used in construction')
EFFECTS[('held_stone_hammer_condition', 'may_decrease_on_build')] = USE_QUALIFIERS[source.STONE_TOOL_WEAR]

FUNCTIONS.update({
    'provide_equipped_rain_protection': ('손에 들면 비를 가리는 데 쓸 수 있다', 'It can provide rain protection while held'),
    'reduce_foraging_rain_effect': ('비가 야외 채집에 주는 불이익을 줄이는 데 쓸 수 있다', 'It can reduce the rain contribution to outdoor foraging penalties'),
})
USE_QUALIFIERS[source.EQUIPPED_RAIN_USE] = ('어느 손이든 들고 있어야 한다', 'It must be held in either hand')

USE_QUALIFIERS[source.GENERATOR_EXTERIOR_USE] = (
    '야외에서 발전기를 사용할 수 있도록 설정되어 있어야 한다',
    'The setting allowing generator operation outdoors must be enabled')

USE_QUALIFIERS[source.WELDED_PARTS] = ("큰 금속판과 작은 금속판의 전환에는 재료 손실이 있다", "Converting between large and small metal sheets loses material")

USE_QUALIFIERS[source.PLUMBING] = ('외부 수원 연결이 가능한 실내 설비에 쓴다', 'It is used with indoor fixtures that accept an external water connection')
USE_QUALIFIERS[source.FROG_PREPARATION] = ('개구리를 손질해 개구리 고기를 얻는다', 'The frog is prepared into frog meat')
USE_QUALIFIERS[source.SPEAR_CONDITIONS['spear_crafting']] = ('완성된 창의 상태는 목공 기술과 확률에 따라 달라지며, 사용한 도구는 마모되거나 사라질 수 있다', 'The crafted spear condition depends on carpentry skill and chance; the tool can wear or be lost')
USE_QUALIFIERS[source.SPEAR_CONDITIONS['spear_upgrade']] = ('부착 후 상태는 창과 부착 무기의 상태에 따라 달라진다', 'The resulting condition depends on the spear and attached weapon condition')

USE_QUALIFIERS[source.ENGINE_SALVAGE] = ("부품을 회수하면 엔진을 사용할 수 없게 된다", "Salvaging the parts leaves the engine unusable")
USE_QUALIFIERS[source.THUMPABLE_SCRAP] = ('분해 가능한 건축물에 파손되지 않은 톱과 드라이버로 사용한다. 보호 구역 규칙을 따른다', 'Use an unbroken saw and screwdriver on an eligible structure, subject to safehouse rules')
USE_QUALIFIERS[source.BURNT_VEHICLE_USE] = ('불타거나 파손된 차량에 용접 마스크와 연료가 있는 토치를 사용한다', 'Use a welding mask and a fueled torch on a burnt or smashed vehicle')

# The current tool is the subject; preserve the admitted loss consequence.
USE_QUALIFIERS[source.SPEAR_STONE_LOSS] = ('창을 만들 때 소모될 수 있다', 'It may be consumed when used to craft a spear')

FUNCTIONS['install_vehicle_tire'] = ('호환 차량에 타이어로 장착할 수 있다', 'It can be installed as a tire on a compatible vehicle')
