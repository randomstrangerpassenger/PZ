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
EFFECTS = {**source.EFFECTS, **vocabulary.EFFECT_VIEWS,
    ("forge_temperature", "increase"): ("화로의 열을 높인다", "It raises furnace heat"),
    ("fishing_rod_form", "replace_on_line_break"): ("낚싯줄이 끊어지면 원래 낚싯대와 미끼가 사라진다", "A broken line removes the original rod and lure")}
CONTEXTS = vocabulary.CONTEXTS
ROLES = vocabulary.ROLES

# Short independently authored capability phrases. The predicates in detail
# still describe execution; these phrases do not promise an unconditional act.
COMPACT_FUNCTIONS = {
    "melee_attack": ("차량 밖에서 근접 공격에 쓸 수 있다", "It can be used for melee attacks outside a vehicle"),
    "request_physics_attack": ("차량 밖에서 투척 공격에 쓸 수 있다", "It can be used for throwing attacks outside a vehicle"),
    "apply_splint": ("머리·몸통 외 골절에 부목을 대는 데 쓸 수 있다", "It can be used to splint fractures outside the head and torso"),
    "record_written_notes": ("필기구가 있고 타인의 소유 잠금 없이 편집 잠금이 풀려 있으면 메모를 쓸 수 있다", "Notes can be written with a writing implement, no other-user ownership lock and editing unlocked"),
    "view_written_note_pages": ("필기구 없이 메모를 읽을 수 있다", "Notes can be read without a writing implement"),
    "wear_on_body": ("몸에 착용할 수 있다", "It can be worn"),
    "wear_configured_clothing": ("몸에 착용할 수 있다", "It can be worn"),
    "read_literature": ("읽기 조건에 맞으면 독서할 수 있다", "It can be read when the reading requirements are met"),
    "consume_edible_food": ("포만 상태가 허용하면 먹을 수 있다", "It can be eaten when satiety permits"),
    "eat_food": ("포만 상태가 허용하면 먹을 수 있다", "It can be eaten when satiety permits"),
    "supply_trap_bait": ("추가 재료가 없는 날음식을 받는 덫의 미끼로 쓸 수 있다", "It can bait a compatible trap as uncooked food without added ingredients"),
    "fish_with_spear": ("창낚시에 쓸 수 있다", "It can be used for spear fishing"),
    "write_note_pages": ("잠기지 않은 메모를 쓰는 필기구로 쓸 수 있다", "It can serve as a writing implement for unlocked notes"),
    "drink_stored_water": ("갈증이 있을 때 담긴 물을 마실 수 있다", "Its water can be drunk when thirsty"),
    "apply_fertilizer": ("파종된 살아 있는 작물의 비료로 쓸 수 있다", "It can fertilize living, seeded crops"),
    "consolidate_drainable_supplies": ("같은 종류의 덜 찬 물품에 잔량을 모을 수 있다", "Its remainder can be consolidated into a nonfull item of the same type"),
}

INLINE_CONDITIONS = {
    (source.NOTE_EDIT, "record_written_notes"): ("필기구가 있고 타인의 소유 잠금 없이 편집 잠금이 풀려 있으면", "with a writing implement, no other-user ownership lock and editing unlocked"),
    (source.CONSUMING, "consume_edible_food"): ("포만 상태가 허용하면", "when satiety permits"),
    (source.CONSUMING, "eat_food"): ("포만 상태가 허용하면", "when satiety permits"),
    (source.MELEE, "melee_attack"): ("차량 밖에서", "outside a vehicle"),
    (source.PHYSICS_ATTACK, "request_physics_attack"): ("차량 밖에서", "outside a vehicle"),
    (source.WATER_DRINKING, "drink_stored_water"): ("갈증이 있을 때", "when thirsty"),
}

# Distinct predicates that old vocabulary projected to one sentence must not
# disappear just because those strings happened to match.
QUALIFIER_OVERRIDES = {
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
load_firearm_rounds|빈 공간에 호환 탄약 장전|loading matching rounds into free capacity
unload_firearm_rounds|탄창식이 아닌 총의 잔탄 꺼내기|unloading rounds from a firearm that does not use a detachable magazine
receive_firearm_magazine|빈 칸에 호환 탄창 삽입|matching magazine insertion into an empty slot
eject_firearm_magazine|장착된 탄창 배출|installed magazine ejection
rack_firearm|상태에 맞는 약실·탄 걸림 조작|chamber and jam handling as its state permits
change_firearm_mode|지원하는 발사 모드 변경|offered firing-mode changes
receive_weapon_upgrade|사용 가능한 드라이버로 빈 자리에 호환 부품 장착|compatible upgrade installation in an empty slot with a usable screwdriver
detach_weapon_upgrade|사용 가능한 드라이버로 장착 부품 제거|installed upgrade removal with a usable screwdriver
use_alternate_reload_controls|설정별 장전 조작|the selected reloading controls
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
    ("SPLINTING", "머리·몸통 외 골절에 완성 부목 또는 찢어진 천과 지지대를 사용한다", "For fractures outside the head and torso, use a finished splint or ripped sheets and a support"),
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

def compact_qualifier(q, locale, unit):
    p = q["payload"]["predicate"]
    kinds = {f["fact_kind"] for f in unit["facts"]}
    function = unit["facts"][0]["payload"].get("function")
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
    predicate = q["payload"]["predicate"]
    if predicate in QUALIFIER_OVERRIDES:
        return pair(QUALIFIER_OVERRIDES[predicate], locale)
    if predicate in base.PREDICATES:
        return pair(base.PREDICATES[predicate], locale)
    if predicate in vocabulary.QUALIFIER_VIEWS:
        return pair(vocabulary.QUALIFIER_VIEWS[predicate]["expanded"], locale)
    return pair(base.PREDICATES[predicate], locale)


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
