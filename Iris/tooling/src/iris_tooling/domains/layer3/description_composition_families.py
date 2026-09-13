"""Semantic sentence frames for functions with nested conditions and results.

Frames are selected by admitted payloads and actual result edges, never FullType.
They consume meaning units, not previously generated prose.
"""
from . import description_composition_lexicon as lex

READING = "The character can read, is awake, meets any book skill requirement, and the reading action remains valid for possession, page state and driving state."
LEARNING = "Reading progress yields a multiplier above the current one, and the reader is within this book's supported training level range."
DRINKING = "For water with remaining portions: manual drinking is offered above thirst 0.1; consumed portions require positive thirst and the container to remain in inventory."
TAINT = "The consumed water is tainted, current poison level is below 20, and current sickness is below 0.3."
WEARING = "The clothing is in the character inventory and is worn at its configured body location."
FRAME_PREDICATES = {
    "reading": {READING, LEARNING, lex.source.READ_SELECTION, lex.source.READ_MAXIMUM},
    "drinking": {DRINKING, TAINT, lex.source.WATER_DRINKING},
    "fertilizer": {lex.source.FERTILIZING, lex.source.FERTILIZER_GROWTH, lex.source.FERTILIZER_ROT},
    "smoking": {lex.source.SMOKING, lex.source.SMOKER_EFFECT, lex.source.NONSMOKER_EFFECT, lex.source.CONSUMING},
    "note": {lex.source.NOTE_EDIT, lex.source.NOTE_LIMITS},
    "wearing": {WEARING, lex.source.WEARING, lex.source.WEAR_ACTION},
    "wear": {lex.source.SPEAR_FISHING_WEAR},
}
FRAME_REQUIRED = {"reading": {READING, LEARNING}, "drinking": {DRINKING},
                  "fertilizer": FRAME_PREDICATES["fertilizer"], "smoking": FRAME_PREDICATES["smoking"],
                  "note": {lex.source.NOTE_EDIT}, "wearing": set(), "wear": {lex.source.SPEAR_FISHING_WEAR}}
FRAME_REQUIRED["smoking"] = FRAME_REQUIRED["smoking"] - {lex.source.CONSUMING}
FRAME_PREDICATES["vehicle_exchange"] = {lex.source.PANEL_INSTALL, lex.source.PANEL_REMOVE,
    *lex.source.VEHICLE_EXCHANGE_REQUIREMENTS.values(), *lex.source.RUNNING_EXCHANGE.values(),
    lex.source.VEHICLE_BATTERY_EXCHANGE, lex.source.VEHICLE_BULB_EXCHANGE}
FRAME_REQUIRED["vehicle_exchange"] = {lex.source.PANEL_INSTALL, lex.source.PANEL_REMOVE}
FRAME_PREDICATES["vehicle_fuel"] = {lex.source.VEHICLE_FUEL, lex.source.VEHICLE_FUEL_ENGINE}
FRAME_REQUIRED["vehicle_fuel"] = FRAME_PREDICATES["vehicle_fuel"]
GROUND_TASKS = {
    "clear_burnt_floor_ashes": (lex.source.ASH_CLEARING, ("탄 바닥의 재 치우기", "clearing ash from burnt floors")),
    "collect_ground_into_bag": (lex.source.GROUND_FILL, ("포대에 흙·모래·자갈 담기", "collecting dirt, sand or gravel into a bag")),
    "dig_furrow": (lex.source.FURROW_DIGGING, ("빈 자연 지면에 고랑 파기", "digging furrows on empty natural ground")),
    "dig_grave": (lex.source.GRAVE_DIGGING, ("적합한 자연 지면에 무덤 파기", "digging graves on suitable natural ground")),
    "fill_grave": (lex.source.GRAVE_FILLING, ("무덤 메우기", "filling graves")),
    "remove_farm_plant": (lex.source.PLANT_REMOVAL, ("수확 없이 작물·고랑 제거", "removing plants or furrows without harvesting")),
}
FRAME_PREDICATES["ground_work"] = {p for p, _ in GROUND_TASKS.values()}
FRAME_REQUIRED["ground_work"] = set()
FRAME_PREDICATES["bellows"] = {lex.source.BELLOWS_USE}
FRAME_REQUIRED["bellows"] = FRAME_PREDICATES["bellows"]
FRAME_PREDICATES["role_overview"] = set(lex.base.PREDICATES) | set(lex.vocabulary.QUALIFIER_VIEWS)
FRAME_REQUIRED["role_overview"] = set()

# An ignition implement is shared across target/method branches. Its compact
# purpose names targets; the exact method branches remain in expanded.
IGNITION = {
    "light_campfire_with_petrol": (lex.source.CAMP_PETROL_USE, ("campfire",), ("petrol",)),
    "ignite_hearth_with_petrol": (lex.source.HEARTH_PETROL, ("barbecue", "fireplace"), ("petrol",)),
    "ignite_hearth_with_tinder": (lex.source.HEARTH_TINDER, ("barbecue", "fireplace"), ("tinder",)),
    "ignite_industrial_fire_with_petrol": (lex.source.INDUSTRIAL_PETROL, ("furnace", "drum"), ("petrol",)),
    "ignite_industrial_tinder": (lex.source.INDUSTRIAL_TINDER, ("drum",), ("tinder",)),
    "light_campfire": (lex.source.CAMP_IGNITER, ("campfire",), ("petrol", "tinder")),
}
IGNITION_TARGETS = {"barbecue": ("바비큐", "barbecues"), "fireplace": ("벽난로", "fireplaces"),
    "furnace": ("연료가 있는 화로", "fueled furnaces"), "drum": ("통나무 드럼", "drums containing logs"),
    "campfire": ("모닥불", "campfires")}
WATER_USES = {
    "store_water": ({lex.source.WATER_STORAGE}, ("물 보관", "water storage")),
    "carry_water": ({lex.source.CARRYING, lex.source.WATER_STORAGE}, ("물 운반", "water carrying")),
    "pour_water_into_container": ({lex.source.WATER_TRANSFER}, ("다른 용기에 물 옮기기", "transferring water to other containers")),
    "receive_poured_water": ({lex.source.WATER_TRANSFER}, ("다른 용기에서 물 받기", "receiving water from other containers")),
    "supply_world_water_storage": ({lex.source.WORLD_WATER_TRANSFER}, ("물 저장 시설 보충", "refilling water-storage objects")),
    "water_seeded_crop": ({lex.source.CROP_WATERING}, ("작물 급수", "crop watering")),
    "wash_vehicle_blood": ({lex.source.VEHICLE_WASHING}, ("차량 혈흔 세척", "washing vehicle bloodstains")),
    "extinguish_fire": ({lex.source.EXTINGUISH_CONDITIONS}, ("소화", "fire extinguishing")),
}
FRAME_PREDICATES["ignition"] = {p for p, _, _ in IGNITION.values()}
FRAME_PREDICATES["ignition"].update({lex.source.CORPSE_IGNITION, lex.source.CANDLE_LIGHT_RECIPE})
FRAME_PREDICATES['ignition'].add(lex.source.LIGHT_CONTROL)
FRAME_PREDICATES['ignition'].update({lex.source.PUMP_CONTAINER, lex.source.GENERATOR_REFUEL, lex.source.VEHICLE_CONTAINER})
FRAME_PREDICATES["water_overview"] = set().union(*(p for p, _ in WATER_USES.values())) | FRAME_PREDICATES["drinking"]
FRAME_REQUIRED["ignition"] = FRAME_REQUIRED["water_overview"] = set()
FRAME_PREDICATES['water_overview'].add(lex.source.COOKING_BASE)
FRAME_PREDICATES['note'].update({lex.source.CAMP_TINDER_USE, lex.source.HEARTH_TINDER,
    lex.source.INDUSTRIAL_TINDER, lex.source.CAMP_FUEL_USE, lex.source.HEARTH_FUEL})

FUNCTION_FRAMES = {
    "apply_splint": ("SPLINTING", ("머리와 몸통을 제외한 골절 부위를 고정하는 데 쓸 수 있다", "It can help splint fractures outside the head and torso")),
    "control_portable_light": ("LIGHT_CONTROL", ("휴대 조명으로 쓸 수 있으며 발광 여부는 현재 상태에 달려 있다", "It can serve as a portable light when its current state permits emission")),
    "light_candle": ("CANDLE_LIGHT_RECIPE", ("발화 도구로 초에 불을 붙일 수 있다", "A fire-starting item can be used to light the candle")),
    "extinguish_candle": ("CANDLE_EXTINGUISH_RECIPE", ("켜진 초를 끄는 제작법에 사용할 수 있다", "It can be supplied to the lit-candle extinguishing recipe")),
    "extinguish_on_unequip": ("CANDLE_UNEQUIP", ("장착한 초를 손에서 빼거나 버리면 꺼진 초로 바뀐다", "Unequipping or dropping the equipped candle changes it to an unlit candle")),
    "build_wooden_barricade": ("WOOD_BARRICADE", ("판자를 받는 문과 창문에 망치·판자·못으로 바리케이드를 추가할 수 있다", "An accepted hammer, planks and nails can add barricades to eligible doors or windows")),
    "remove_barricade": ("WOOD_UNBARRICADE", ("나무 바리케이드 철거에 쓸 수 있다", "It can be used to remove wooden barricades")),
    "fish_with_spear": ("SPEAR_FISHING", ("물가에서 미끼 없이 창낚시에 쓸 수 있다", "It can be used for spear fishing at water without bait")),
    "water_seeded_crop": ("CROP_WATERING", ("파종한 작물에 물을 줄 수 있다", "It can water seeded crops")),
    "wash_vehicle_blood": ("VEHICLE_WASHING", ("물로 차량의 혈흔을 씻을 수 있다", "Its water can wash vehicle bloodstains")),
    "extinguish_fire": ("EXTINGUISH_CONDITIONS", ("바닥이나 몸에 붙은 불을 끌 수 있다", "It can extinguish fires on the ground or on characters")),
    "apply_garment_patch": ("GARMENT_PATCHING", ("의류의 구멍을 덧대거나 패딩을 추가할 수 있다", "It can be used to patch garment holes or add padding")),
    "clean_burn": ("BURN_CLEANING", ("세척이 필요한 화상에 충분한 강도의 붕대 재료로 쓰며 통증이 생길 수 있다", "Sufficiently strong bandaging material can clean burns needing washing; treatment can cause pain")),
    "apply_bandage": ("BANDAGE_APPLICATION", ("붕대를 댈 수 있는 부위의 붕대 재료로 사용할 수 있다", "It can be used as bandaging material for body parts that permit bandaging")),
    "wash_bandaging_material": ("BANDAGE_WASHING", ("물을 사용해 대응하는 깨끗한 붕대·직물 형태로 바꿀 수 있다", "Water can turn it into the corresponding clean bandage or fabric form")),
    "destroy_structure": ("STRUCTURE_DESTRUCTION", ("구조물을 철거하는 데 사용할 수 있다", "It can be used to demolish structures")),
    "assist_stitching": ("SUTURE_ASSISTANCE", ("봉합이나 실밥 제거에 보조 도구로 사용할 수 있으며 기본 시간을 줄인다", "It can assist stitching or stitch removal and reduces their base time")),
    "disinfect_wound": ("DISINFECTION", ("붕대가 없는 부위의 상처를 소독할 수 있다", "It can be used to disinfect an unbandaged wound")),
    "fire_ammunition": ("FIRING", ("사격에 사용할 수 있다. 탄약이 준비되고 탄 걸림이 없어야 하며 낡은 총은 잔탄이 있을 때 걸릴 수 있다", "It can be used for shooting. Firing needs ready ammunition and no jam; a worn gun with rounds remaining can jam")),
    "convert_lamp_to_battery": ("LAMP_CONVERSION", ("조명을 건전지로 작동하도록 개조할 수 있다", "It can be used to convert lamps to battery power")),
    "dismantle_built_object": ("THUMPABLE_SCRAP", ("분해 가능한 건축물을 해체하고 재료를 회수할 수 있다", "It can be used to dismantle eligible built objects and recover materials")),
    "manage_weapon_attachments": ("WEAPON_ATTACHMENT_TOOL", ("호환 무기의 부착물을 장착하거나 제거할 수 있다", "It can be used to install or remove compatible weapon parts")),
    "service_vehicle_parts": ("VEHICLE_TOOL_USE", ("차량 부품을 장착하거나 탈거하는 데 사용할 수 있다", "It can be used to install or remove vehicle parts")),
    "load_matching_ammunition": ("LOADING", ("빈 공간이 있는 호환 총기나 탄창에 장전할 수 있다", "It can be loaded into compatible firearms or magazines with loading space")),
    "fill_magazine": ("MAGAZINE_FILL", ("탄창의 빈 공간에 호환 탄약을 넣을 수 있다", "Matching rounds can be loaded into the magazine's free capacity")),
    "empty_magazine": ("MAGAZINE_EMPTY", ("탄창의 잔탄을 꺼낼 수 있다", "Remaining rounds can be removed from the magazine")),
    "take_pills": ("PILL_TAKING", ("소지한 알약을 복용할 수 있다", "The carried pills can be taken")),
    "set_alarm": ("ALARM_SETTING", ("알람을 켜거나 끄고 시각을 설정할 수 있다", "Its alarm state and time can be set")),
    "stop_alarm": ("ALARM_STOPPING", ("울리는 알람을 끌 수 있다", "Its ringing alarm can be stopped")),
    "fill_petrol_container": ("PUMP_CONTAINER", ("전원이 공급되는 주유기에서 연료를 받을 수 있다", "It can receive fuel from a powered pump")),
    "transfer_vehicle_fuel": ("VEHICLE_CONTAINER", ("엔진이 꺼진 차량과 호환 용기 사이의 연료 이동에 쓸 수 있다", "It can transfer fuel between a stopped-engine vehicle and a compatible container")),
    "refuel_generator": ("GENERATOR_REFUEL", ("꺼진 발전기에 휘발유를 보충할 수 있다", "It can add petrol to an inactive generator")),
    "pitch_tent": ("CAMP_PLACEMENT", ("텐트를 설치할 수 있다", "It can be used to pitch a tent")),
}
for _function, (_condition, _pair) in FUNCTION_FRAMES.items():
    FRAME_PREDICATES[_function] = {getattr(lex.source, _condition)}
    FRAME_REQUIRED[_function] = FRAME_PREDICATES[_function]
FRAME_PREDICATES["apply_bandage"] = {lex.source.BANDAGE_APPLICATION, lex.source.DIRTY_BANDAGING,
    "A body part is eligible for bandaging; the material remains in inventory and the patient does not move out of reach."}
FRAME_PREDICATES["fire_ammunition"] = {lex.source.FIRING, lex.source.GUN_FIRING_CYCLE}
FRAME_PREDICATES['disinfect_wound'] = {lex.source.DISINFECTION, lex.source.DISINFECTION_USE}
FRAME_REQUIRED["fire_ammunition"] = FRAME_PREDICATES["fire_ammunition"]
FRAME_PREDICATES["load_matching_ammunition"].add(lex.source.AMMUNITION_LOADING_PATHS)
FRAME_PREDICATES["take_pills"].add(lex.PILL_INVENTORY)
FRAME_PREDICATES["pitch_tent"].add(lex.source.TENT_PLACEMENT)
FRAME_PREDICATES['tool_wear'] = {lex.source.SPEAR_TOOL_WEAR}
FRAME_REQUIRED['tool_wear'] = FRAME_PREDICATES['tool_wear']
FRAME_PREDICATES['washing'] = {lex.source.BODY_WASHING, lex.source.EQUIPMENT_WASHING, lex.source.WASHING_OUTCOME}
FRAME_REQUIRED['washing'] = {lex.source.BODY_WASHING, lex.source.WASHING_OUTCOME}
FRAME_PREDICATES['sowing'] = {lex.source.SOWING, lex.source.SEED_EXTRACTION, lex.source.OPENING, *lex.source.SOW_COUNTS.values()}
FRAME_REQUIRED['sowing'] = {lex.source.SOWING}

# These frames describe admitted functions, with operation details left in
# their public expanded clauses. Unknown conditions still take the fallback.
OVERVIEWS = {
    'apply_poultice': ({lex.source.POULTICE_USE},
        ('다친 부위에 약초 찜질제로 바를 수 있다', 'It can be applied to an injured body part as an herbal poultice')),
    'install_padlock': ({lex.source.PADLOCK_USE},
        ('자물쇠를 달 수 있는 구조물을 잠글 수 있다. 문에는 쓸 수 없으며, 설치하면 열쇠를 얻는다', 'It can lock structures that accept padlocks, except doors. Installation provides matching keys')),
    'provide_belt_slots': ({lex.source.SLOT_USE},
        ('착용하면 허리 양쪽에 도구나 무전기를 걸어 휴대할 수 있다', 'When worn, it can carry compatible tools or walkie-talkies on either side of the waist')),
    'provide_right_holster_slot': ({lex.source.SLOT_USE},
        ('착용하면 오른쪽에 홀스터에 맞는 총기를 넣어 휴대할 수 있다', 'When worn, it can carry a compatible firearm on the right side')),
    'provide_paired_holster_slots': ({lex.source.SLOT_USE},
        ('허리 양쪽 홀스터에 맞는 총기를 넣어 휴대할 수 있다', 'It can carry compatible firearms in holsters on both sides of the waist')),
    'paint_supported_surface': ({lex.source.PAINTING, lex.source.PAINT_ACTIONS},
        ('도색 가능한 표면을 칠할 수 있다', 'It can be used to paint compatible surfaces')),
    'paint_wall_sign': ({lex.source.PAINTING, lex.source.PAINT_ACTIONS},
        ('벽에 표식을 그릴 수 있다', 'It can be used to paint signs on walls')),
    'use_vehicle_seat': ({lex.source.VEHICLE_SEATING},
        ('차량에 장착해 앉는 좌석으로 사용할 수 있다', 'Once installed on a vehicle, it can be used as a seat')),
    'power_exterior_fuel_pumps': ({lex.source.GENERATOR_EXTERIOR_USE},
        ('야외 주유기에 전원을 공급할 수 있다', 'It can supply power to exterior fuel pumps')),
    'rest_at_placed_tent': ({lex.source.TENT_REST},
        ('설치한 텐트에서 쉬거나 잘 수 있다', 'The placed tent can be used for resting or sleeping')),
    'place_campfire': ({lex.source.CAMP_PLACEMENT, lex.source.CAMPFIRE_PLACEMENT},
        ('모닥불을 설치할 수 있다', 'It can be used to place a campfire')),
    'supply_propane_barbecue': ({lex.source.PROPANE_BARBECUE},
        ('프로판 바비큐에 설치해 연료를 공급할 수 있다', 'It can be installed on a propane barbecue to supply fuel')),
    'support_makeup_mirror': ({lex.source.MAKEUP_LIFECYCLE},
        ('분장할 때 모습을 비춰 볼 수 있다', 'It can show your reflection when applying makeup')),
    'place_fishing_net': ({lex.source.NET_PLACEMENT},
        ('설치 조건을 충족하면 물에 어망을 설치할 수 있다', 'It can be placed in water as a fishing net when placement conditions hold')),
    'check_fishing_net': ({lex.source.NET_CHECKING},
        ('설치 후 한 시간 이상 지나면 미끼 물고기 포획을 확인하며 포획 실패나 어망 파손이 생길 수 있다', 'After at least one hour, the placed net can be checked for bait fish; catches are not guaranteed and the net can break')),
    'remove_fishing_net': ({lex.source.NET_REMOVAL},
        ('설치한 어망을 회수할 수 있으나 원래 물품 상태는 보존하지 않는다', 'The placed net can be retrieved without preserving its original item state')),
    'supply_drum_logs': ({lex.source.DRUM_LOGS},
        ('빈 금속 드럼의 숯 제작 재료로 쓸 수 있다', 'It can be made into charcoal in an empty metal drum')),
    'groom_beard': ({lex.source.BEARD_GROOMING},
        ('수염을 다듬거나 면도할 수 있다', 'It can be used to trim or shave a beard')),
    'send_remote_trigger': ({lex.source.REMOTE_TRIGGER},
        ('조종 범위 안의 연결된 장치를 원격으로 작동시킬 수 있다', 'It can remotely activate a linked device within range')),
    'inflate_vehicle_tire': ({lex.source.TIRE_INFLATION},
        ('차량에 장착된 타이어에 공기를 넣을 수 있다', 'It can be used to inflate a tire installed on a vehicle')),
    'deflate_vehicle_tire': ({lex.source.TIRE_DEFLATION},
        ('공기가 남은 장착 타이어에서 펌프 없이 공기를 뺀다', 'It releases remaining air from an installed tire without a pump')),
    'light_campfire_by_friction': ({lex.source.CAMP_FRICTION},
        ('연료가 든 꺼진 모닥불에 나무 마찰로 점화를 시도한다. 지구력을 소모하며 막대가 부러질 수 있다', 'It attempts wood-friction ignition of an unlit, fueled campfire, spending endurance with a risk of breaking the stick')),
    'operate_vehicle_battery_charger': ({lex.source.CHARGER_CONTROLS},
        ('전력을 공급해 차량 배터리를 충전하는 데 쓸 수 있다', 'It can be used to charge vehicle batteries when powered')),
    'place_vehicle_battery_charger': ({lex.source.CHARGER_PLACEMENT},
        ('한 칸에 하나씩 설치하며 배터리가 없을 때 회수하는 차량 배터리 충전기다', 'The charger can be placed one per square and retrieved without a battery')),
    'avoid_first_door_alarm_trigger': ({lex.source.KEY_ALARM},
        ('열쇠가 맞는 차량의 문을 처음 열 때 경보가 울리지 않게 한다. 이미 울리는 경보는 끄지 못한다', 'It prevents the alarm from being triggered when first opening the matching vehicle. It cannot silence an alarm already ringing')),
    'operate_door_lock': ({lex.source.DOOR_KEY_USE},
        ('열쇠가 맞는 문을 잠그거나 열 수 있다', 'It can lock or unlock a door with a matching lock')),
    'remove_matching_padlock': ({lex.source.PADLOCK_KEY_USE},
        ('맞는 구조물 자물쇠를 제거할 수 있으며 이때 소모된다', 'It can remove a matching structure padlock and is consumed in the process')),
    'request_matching_vehicle_start': ({lex.source.VEHICLE_KEY_USE},
        ('열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다', 'It can be used to start the matching vehicle')),
    'satisfy_vehicle_mechanics_key': ({lex.source.KEY_MECHANICS},
        ('맞는 차량의 정비 작업에서 열쇠 요구를 충족한다', 'It meets the key requirement of a matching vehicle mechanics operation')),
    'install_combination_padlock': ({lex.source.CODE_LOCK_USE},
        ('자물쇠를 달 수 있는 구조물에 비밀번호 잠금을 설정할 수 있다. 문이나 이미 잠긴 구조물에는 쓸 수 없다', 'It can secure a structure that accepts padlocks with a chosen code, except doors and already locked structures')),
    'remove_combination_padlock': ({lex.source.CODE_UNLOCK},
        ('설치 후 맞는 번호로 제거할 수 있다', 'Once installed, it can be removed with its matching code')),
    'transfer_compost': ({lex.source.COMPOST_TRANSFER},
        ('퇴비통과 포대 사이에서 퇴비를 옮길 수 있다', 'It can transfer compost between a bin and a bag')),
    'receive_compost': ({lex.source.COMPOST_TRANSFER},
        ('퇴비통의 퇴비를 담을 수 있다', 'It can receive compost from a bin')),
    'fill_ground_bag': ({lex.source.GROUND_FILL},
        ('흙이나 자갈, 모래를 담을 수 있다', 'It can hold dirt, gravel or sand')),
    'pour_ground_cover': ({lex.source.GROUND_POUR},
        ('담긴 재료를 바닥에 깔 수 있다', 'Its ground material can be spread on the floor')),
    'read_recorded_media_label': ({lex.source.MEDIA_LABEL},
        ('기록이 배정된 매체를 소지하면 내용 안내를 읽을 수 있다', 'Its assigned recording’s description can be read while carried')),
    'insert_recorded_media': ({lex.source.MEDIA_INSERT},
        ('다른 매체가 들어 있지 않은 호환 기기에서 전원을 켜고 재생할 수 있다', 'It can be played in a powered compatible player with no other media inserted')),
    'connect_radio_headphones': ({lex.source.HEADPHONE_CONNECTION},
        ('다른 헤드폰이 연결되지 않은 호환 휴대 기기에 꽂아 쓸 수 있다. TV에는 연결할 수 없다', 'It can be plugged into a portable device with an available headphone connection, excluding TVs')),
    'operate_installed_vehicle_door': ({lex.source.PANEL_DOOR},
        ('차량에 장착된 문·덮개를 여닫을 수 있다', 'It can open or close an installed vehicle door or cover')),
    'operate_installed_vehicle_lock': ({lex.source.PANEL_LOCK},
        ('차량에 장착된 문의 잠금을 조작할 수 있다', 'It can operate the lock of an installed vehicle door')),
    'operate_installed_vehicle_window': ({lex.source.PANEL_WINDOW},
        ('차량에 장착된 개폐식 창문을 여닫을 수 있다', 'It can open or close an installed openable vehicle window')),
    'repair_vehicle_engine': ({lex.source.ENGINE_REPAIR},
        ('손상된 차량 엔진을 수리하는 데 사용할 수 있다', 'It can be used to repair damaged vehicle engines')),
    'erase_map_annotations': ({lex.source.MAP_ERASURE},
        ('지도의 글·기호 주석을 지울 수 있다', 'It can erase map text or symbols')),
    'groom_hair': ({lex.source.HAIR_GROOMING},
        ('머리를 손질할 수 있다', 'It can be used to groom hair')),
    'serve_as_eating_utensil': ({lex.source.MEAL_UTENSIL},
        ('식사에 선택적으로 사용할 수 있다', 'It can be used as an optional eating utensil')),

    'plaster_supported_structure': ({lex.source.PLASTER_USE},
        ('구조물에 석고를 발라 도색을 준비할 수 있다', 'It can be used to plaster supported structures to prepare them for painting')),
    'prepare_opened_food_ingredient': ({lex.source.OPENED_FOOD, lex.source.OPENING, lex.source.CAN_OPENING, lex.source.COOKING_ACTION},
        ('개봉한 내용물을 허용하는 요리의 재료로 쓸 수 있다', 'Its opened contents can be ingredients in preparations that accept them')),

    'build_metal_barricade': ({lex.source.METAL_BARRICADE},
        ('문과 창문에 금속 바리케이드를 설치하는 데 사용할 수 있다', 'It can be used to install metal barricades on doors and windows')),
    'remove_metal_barricade': ({lex.source.METAL_UNBARRICADE},
        ('금속 바리케이드를 철거하는 데 사용할 수 있다', 'It can be used to remove metal barricades')),
    'dismantle_burnt_vehicle': ({lex.source.BURNT_VEHICLE_USE},
        ('불타거나 파손된 차량을 분해해 재료를 회수할 수 있다', 'It can be used to dismantle burnt or smashed vehicles and recover materials')),
    'store_vehicle_items': ({lex.source.VEHICLE_STORAGE},
        ('차량에 장착해 물품을 보관할 수 있다', 'Once installed on a vehicle, it can store items')),
    'store_and_retrieve_items': ({'Storage requires room and item admission; transfer requires accessible distinct source/destination, permitted removal and applicable multiplayer restrictions.'},
        ('빈 공간에 허용된 물건을 넣고 꺼내는 수납 용기다', 'It stores and retrieves admitted items within its available capacity')),
    'wear_container_on_back': ({lex.source.BACK_CONTAINER},
        ('등에 메어 착용할 수 있다', 'It can be worn on the back')),
    'switch_declared_clothing_form': ({lex.source.CLOTHING_FORM},
        ('착용 모양을 바꿀 수 있다', 'It can be worn in an alternate form')),
    'chop_tree': ({lex.source.CHOPPING},
        ('나무를 베는 데 사용할 수 있다', 'It can be used to chop trees')),
    'cut_bushes_and_vines': ({lex.source.PLANT_CUTTING},
        ('덤불이나 벽 덩굴을 제거할 수 있다', 'It can be used to remove bushes and wall vines')),
    'link_remote_device': ({lex.source.REMOTE_LINK},
        ('함께 가지고 있는 호환 장치를 연결해 원격으로 작동시키도록 설정할 수 있다', 'It can pair a compatible controller and device carried together for remote activation')),
    'reset_remote_id': ({lex.source.REMOTE_RESET},
        ('선택한 물품의 원격 연결만 해제한다', 'It resets only the selected item\'s remote link')),
    'place_trigger_device': ({lex.source.DEVICE_WORLD_PLACEMENT},
        ('바닥에 설치할 수 있다', 'It can be placed on the ground')),
    'place_noise_device': ({lex.source.DEVICE_PLACEMENT},
        ('바닥에 설치할 수 있다', 'It can be placed on the ground')),
    'retrieve_placed_device': ({lex.source.DEVICE_RETRIEVAL},
        ('설치 후 회수할 수 있다', 'It can be picked up after placement')),
    'set_device_timer': ({lex.source.DEVICE_TIMER_CONTROL, lex.source.DEVICE_DELAY},
        ('타이머의 지연 시간을 설정할 수 있다', 'Its timer delay can be set')),
    'fish_with_rod': ({lex.source.ROD_FISHING, lex.source.FISHING_EXECUTION, lex.source.FISHING_LURES, lex.source.FISHING_MATCHES},
        ('물가에서 맞는 미끼와 함께 낚시할 수 있다', 'It can be used for rod fishing at water with matching bait')),
    'bait_rod_fishing': ({lex.source.ROD_FISHING, lex.source.FISHING_EXECUTION, lex.source.FISHING_MATCHES, lex.source.FISHING_LURE_LOSS},
        ('물가에서 낚싯대 낚시의 미끼로 사용할 수 있다', 'It can be used as bait for rod fishing at water')),
    'control_installed_generator': ({lex.source.GENERATOR_CONTROL},
        ('지식·연료·상태 조건에 따라 설치한 발전기를 연결하고 가동할 수 있다', 'The installed generator can be connected and operated subject to knowledge, fuel and condition requirements')),
    'handle_generator': ({lex.source.GENERATOR_HANDLING},
        ('발전기를 양손으로 들거나 연결을 해제한 뒤 회수할 수 있다', 'The generator can be carried in both hands or retrieved after disconnection')),
    'inspect_generator': ({lex.source.GENERATOR_INSPECTION},
        ('설치한 발전기의 연료·상태·전력 사용 정보를 확인할 수 있다', 'Its installed generator fuel, condition and power use can be inspected')),
    'repair_generator': ({lex.source.GENERATOR_REPAIR},
        ('손상된 발전기를 수리하는 데 사용할 수 있다', 'It can be used to repair damaged generators')),
    'connect_to_vehicle_battery_charger': ({lex.source.CHARGER_CONTROLS},
        ('덜 충전된 차량 배터리를 전원이 있는 충전기에 연결해 충전할 수 있다', 'A vehicle battery below full charge can be connected to a powered charger for charging')),
    'install_light_bulb': ({lex.source.LAMP_BULB},
        ('전구를 교체할 수 있는 조명에 장착할 수 있다', 'It can be fitted to lamps with replaceable bulbs')),
    'clean_world_blood': ({lex.source.BLOOD_CLEANING},
        ('바닥 혈흔을 지울 수 있다', 'It can be used to clean floor bloodstains')),
}
for _name, (_predicates, _) in OVERVIEWS.items():
    FRAME_PREDICATES[_name] = _predicates
    FRAME_REQUIRED[_name] = {lex.source.ROD_FISHING} if _name in {'fish_with_rod', 'bait_rod_fishing'} else _predicates
FRAME_REQUIRED['set_device_timer'] = set()
FRAME_PREDICATES['makeup'] = {lex.source.MAKEUP_USE, lex.source.MAKEUP_LIFECYCLE}
FRAME_REQUIRED['makeup'] = FRAME_PREDICATES['makeup']
FRAME_REQUIRED['prepare_opened_food_ingredient'] = {lex.source.OPENED_FOOD}

DRY_BODY = 'The body is wet, the towel has uses remaining, and the towel is in inventory.'
DYE_ACCESS = 'The dye remains in inventory; hair exists and is not Bald, or the beard model exists and is nonempty.'
FRAME_PREDICATES.update({
    'drying': {lex.source.BODY_DRYING, DRY_BODY},
    'disinfection': {lex.source.DISINFECTION, lex.source.DISINFECTION_USE},
    'crop_treatment': {lex.source.SPRAY_TREATMENT},
    'dye': {lex.source.DYE_APPLICATION, DYE_ACCESS},
    'reading_mood': {READING, lex.source.READ_SELECTION, lex.source.READ_MOOD},
    'curtain': {lex.source.CURTAIN_USE},
    'trap': {lex.source.TRAP_CATCH, lex.source.TRAP_PLACEMENT, lex.source.TRAP_CONTROLS,
             lex.source.TRAP_LIFECYCLE, lex.source.TRAP_RABBIT_SQUIRREL, lex.source.TRAP_BIRD, lex.source.TRAP_RODENTS},
})
FRAME_REQUIRED['trap'] = {lex.source.TRAP_CATCH, lex.source.TRAP_PLACEMENT, lex.source.TRAP_CONTROLS, lex.source.TRAP_LIFECYCLE}
BATTERY_TARGETS = {
    'supply_lamp_battery': (lex.source.LAMP_BATTERY, ('건전지형 조명', 'battery-powered lamps')),
    'supply_pillar_light_battery': (lex.source.PILLAR_BATTERY, ('기둥 조명', 'pillar lamps')),
    'supply_portable_device_charge': (lex.source.BATTERY_INSERTION, ('휴대 기기', 'portable devices')),
    'use_as_radio_battery': (lex.source.BATTERY_INSERT, ('배터리형 기기', 'battery-powered devices')),
}
BATTERY_RECIPE = 'A compatible empty flashlight or duck device is supplied; transferred charge is the charge remaining in the battery selected by the recipe.'
FRAME_PREDICATES['battery_supply'] = {p for p, _ in BATTERY_TARGETS.values()} | {BATTERY_RECIPE}
FRAME_REQUIRED['battery_supply'] = set()
for _name in ('drying', 'disinfection', 'crop_treatment', 'dye', 'reading_mood', 'curtain'):
    FRAME_REQUIRED[_name] = FRAME_PREDICATES[_name]


def frames(plan, locale, links, *, expanded=False):
    units = [u for u in plan["units"] if not u["detail_reason"]]
    output, used = packaging_frames(plan, locale, links, compact=True)

    def select(kind, key, value):
        return [u for u in units if len(u["facts"]) == 1 and u["facts"][0]["fact_kind"] == kind
                and u["facts"][0]["payload"].get(key) == value and not (set(u["fact_refs"]) & used)]

    def function(name):
        return select("direct_function", "function", name)

    def effect(name):
        expected = {"thirst": "decrease", "poison_level": "increase", "crop_growth_schedule": "advance",
                    "crop_state": "set_rotten", "stress": "decrease", "unhappiness": "decrease",
                    "food_sickness": "increase", "item_condition": "decrease"}[name]
        return [u for u in select("effect", "property", name) if u["facts"][0]["payload"].get("direction") == expected]

    def related(left, right):
        a = {r for u in left for r in u["fact_refs"]}
        b = {r for u in right for r in u["fact_refs"]}
        return bool(a and b) and all(any(r["kind"] == "result" and
            a & set(r.get("fact_refs", [])) and ref in r.get("fact_refs", [])
            for r in plan["relations"]) for ref in b)

    def emit(members, pair, frame, rule):
        if not members:
            return
        predicates = {plan["qualifiers"][q]["payload"]["predicate"] for u in members for q in u["qualifier_refs"]}
        if not predicates <= FRAME_PREDICATES[frame] or not FRAME_REQUIRED[frame] <= predicates:
            return  # An extra condition needs the general exact-scope path.
        text = lex.pair(pair, locale) + "."
        if frame == 'makeup':
            # Describe the two supplied uses; menu eligibility and preview
            # lifetime remain internal evidence, not an execution guide.
            output.append({'text': text, **links([dict(u, qualifier_refs=[]) for u in members], plan),
                           'expression': 'public_use', 'placement_reason': rule,
                           'qualifier_dispositions': []})
            used.update(r for u in members for r in u['fact_refs'])
            return
        linked = links(members, plan)
        dispositions = []
        for u in members:
            for qref in u["qualifier_refs"]:
                predicate = plan["qualifiers"][qref]["payload"]["predicate"]
                role_detail = frame == "role_overview"
                detail = frame in {"wearing", "ignition", "note", "makeup"} or predicate == lex.source.NOTE_LIMITS or role_detail
                if frame == "water_overview":
                    detail = predicate not in FRAME_PREDICATES["drinking"]
                dispositions.append({"qualifier_ref": qref, "applies_to_fact_refs": u["fact_refs"],
                    "placement": "expanded" if detail else "compact_summary", "text": None if detail else text.removesuffix("."),
                    "reason": rule + "; operation lifetime, exact arithmetic and delivery remain in expanded"})
        output.append({"text": text, **linked, "expression": "conditional_frame",
                       "placement_reason": rule, "qualifier_dispositions": dispositions})
        used.update(r for u in members for r in u["fact_refs"])

    # Function/result pairs require an actual result edge. The independently
    # admitted dye and reading effects below are coordinated without inventing
    # a causal edge; each original condition application remains linked.
    for fn, target in (('apply_eye_makeup', ('눈 화장', 'eye makeup')),
                       ('apply_lip_makeup', ('입술 화장', 'lip makeup')),
                       ('apply_makeup', ('화장', 'makeup'))):
        application, removal = function(fn), function('remove_registered_makeup')
        if application and removal:
            emit(application + removal,
                 (target[0] + '을 하거나 화장을 지울 수 있다',
                  'It can be used to apply ' + target[1] + ' or remove makeup'),
                 'makeup', 'makeup application and menu-selected removal; execution conditions retained internally')
    washing = function('wash_body')
    washed = [u for u in units if len(u['facts']) == 1 and u['facts'][0]['payload'] in (
        {'property': 'washed_surface_blood', 'direction': 'remove'},
        {'property': 'washed_surface_dirt', 'direction': 'remove'})]
    if washing and len(washed) == 2:
        emit(washing + washed,
             ('물로 몸을 씻을 때 세척제로 사용할 수 있다. 처리한 신체·의류 부위의 피·때를 지우며 세제 없이도 씻을 수 있고 물이 부족하면 일부만 씻긴다',
              'It can be used as a supply for washing the body with water. Washing clears blood and dirt from processed body or clothing parts; soap is optional and limited water can leave washing incomplete'),
             'washing', 'coordinate the named washing supply and scoped blood/dirt outcomes; equipment operations remain expanded')
    for fn in ('sow_seeds', 'sow_extracted_seeds'):
        for seed in function(fn):
            predicates = {plan['qualifiers'][q]['payload']['predicate'] for q in seed['qualifier_refs']}
            counts = [n for n, predicate in lex.source.SOW_COUNTS.items() if predicate in predicates]
            if len(counts) != 1:
                continue
            count = counts[0]
            members = [seed]
            if fn == 'sow_extracted_seeds':
                members += function('unpack_seeds')
                members += [u for u in units if not set(u['fact_refs']) & used
                            and any(f['payload'] == {'activity': 'package_opening'} for f in u['facts'])
                            and any(f['payload'] == {'role': 'material'} for f in u['facts'])]
            ko_start = '봉지를 개봉해 꺼낸 ' if fn == 'sow_extracted_seeds' else ''
            en_start = 'After opening the packet, sow ' if fn == 'sow_extracted_seeds' else 'Sow '
            emit(members,
                 (ko_start + '씨앗을 아직 씨가 없는 경작 고랑에 심을 수 있다',
                  ('The packet can be opened to obtain seeds for sowing in an unseeded plowed furrow' if fn == 'sow_extracted_seeds' else 'The seeds can be sown in an unseeded plowed furrow')),
                 'sowing', 'seed packet opening is distinct from consumption of the configured loose-seed count')
    for fn, prop, direction, frame, wording in (
        ('dry_the_body', 'body_wetness', 'decrease', 'drying',
         ('물기를 닦을 수 있다',
          'It can be used to dry yourself')),
        ('disinfect_wound', 'wound_alcohol_level', 'increase', 'disinfection',
         ('붕대가 없는 부위의 상처를 소독할 수 있다',
          'It can be used to disinfect an unbandaged wound')),
        ('treat_crop_mildew', 'crop_mildew_level', 'decrease', 'crop_treatment',
         ('흰가루병이 있는 작물에 살포해 병의 정도를 줄일 수 있다',
          'It can be sprayed on crops to reduce mildew')),
        ('treat_crop_flies', 'crop_flies_level', 'decrease', 'crop_treatment',
         ('해충이 있는 작물에 살포해 해충을 줄일 수 있다',
          'It can be sprayed on crops to reduce flies')),
    ):
        action = function(fn)
        outcome = [u for u in select('effect', 'property', prop) if u['facts'][0]['payload']['direction'] == direction]
        if action and outcome and related(action, outcome):
            emit(action + outcome, wording, frame, 'explicit function/result overview; exact execution and result conditions remain expanded')
    dye = function('dye_hair_or_beard')
    colors = [u for u in select('effect', 'property', 'hair_or_beard_color')
              if u['facts'][0]['payload']['direction'] == 'set_dye_color']
    if dye and colors:
        emit(dye + colors,
             ('머리카락이나 수염을 염색할 수 있다',
              'It can dye hair or a beard'),
             'dye', 'coordinate the admitted color-setting capability and state; no causal relation is inferred')
    reading = function('read_literature')
    moods = [u for u in units if not (set(u['fact_refs']) & used) and len(u['facts']) == 1
             and u['facts'][0]['fact_kind'] == 'effect'
             and u['facts'][0]['payload'].get('direction') == 'cap_at_reading_start'
             and u['facts'][0]['payload'].get('property') in {'boredom', 'stress', 'unhappiness'}]
    if reading and moods:
        labels = {'boredom': ('지루함', 'boredom'), 'stress': ('스트레스', 'stress'), 'unhappiness': ('불행', 'unhappiness')}
        names = [labels[u['facts'][0]['payload']['property']] for u in moods]
        emit(reading + moods,
             ('글을 읽을 수 있고 깨어 있으며 책의 기술 조건에 맞으면 독서할 수 있다. 독서 중 ' + '·'.join(n[0] for n in names) + ' 수치는 읽기 시작 때보다 높아지지 않는다',
              'Literate, awake readers meeting the book\'s skill requirements can read it; ' + lex_join([n[1] for n in names]) + ' stay at or below their reading-start levels while reading'),
             'reading_mood', 'coordinate reading and independently admitted mood caps under their shared reader eligibility')
    curtains = function('install_sheet_curtain')
    if curtains:
        emit(curtains,
             ('커튼이 없는 창문이나 문에 커튼으로 달아 쓸 수 있다',
              'It can be used as a curtain on an eligible window or door without one'),
             'curtain', 'carried material supplies a curtain; subsequent placed-object controls are internal')
    for name, (_, wording) in OVERVIEWS.items():
        for u in function(name):
            emit([u], wording, name, 'function overview; target compatibility, losses and operation details remain expanded')
    batteries, targets = [], []
    for name, (predicate, labels) in BATTERY_TARGETS.items():
        selected = [u for u in function(name) if {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {predicate}]
        if selected:
            batteries += selected
            targets.append(labels)
    if batteries:
        power_roles = [u for u in units if not (set(u['fact_refs']) & used)
            and any(f['payload'] == {'activity': 'portable_device_power'} for f in u['facts'])
            and any(f['payload'] == {'role': 'power_supply'} for f in u['facts'])
            and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {BATTERY_RECIPE}]
        if power_roles and any(u['facts'][0]['payload'].get('function') == 'supply_portable_device_charge' for u in batteries):
            batteries += power_roles
        emit(batteries,
             ('남은 충전량으로 호환되는 조명과 휴대 기기 등을 작동시킬 수 있다',
              'Its remaining charge can power compatible lights and portable or other battery-powered devices'),
             'battery_supply', 'battery supply targets remain distinct; empty-slot, recipe and charge-transfer details remain expanded')
    trapping = function('catch_trap_animal') + function('place_animal_trap') + function('manage_animal_trap')
    if len(trapping) == 3:
        predicates = {plan['qualifiers'][q]['payload']['predicate'] for u in trapping for q in u['qualifier_refs']}
        animals = [(p, names) for p, names in (
            (lex.source.TRAP_RABBIT_SQUIRREL, ('토끼·다람쥐', 'rabbits and squirrels')),
            (lex.source.TRAP_BIRD, ('새', 'birds')),
            (lex.source.TRAP_RODENTS, ('생쥐·쥐', 'mice and rats')),
        ) if p in predicates]
        if len(animals) == 1:
            names = animals[0][1]
            emit(trapping,
                 (names[0] + ' 포획을 위해 신선한 대응 미끼와 함께 설치할 수 있다. 미끼·포획물·덫을 회수할 수 있다',
                  'It can be placed with matching fresh bait to catch ' + names[1] + '. Bait, catches and the trap can be retrieved'),
                 'trap', 'trap placement, handling and conditional capture overview; exact targets, losses and controls remain expanded')

    read = function("read_literature")
    learning = [u for u in units if u["facts"][0]["fact_kind"] == "effect" and
                u["facts"][0]["payload"].get("property", "").endswith("_experience_multiplier")
                and u["facts"][0]["payload"].get("direction") == "increase"]
    maximum = select("state", "state", "skill_book_max_multiplier")
    if read and len(learning) == 1 and related(read, learning):
        skill = learning[0]["facts"][0]["payload"]["property"].removesuffix("_experience_multiplier")
        name = lex.base.SKILLS[skill]
        ko_max = en_max = ""
        if len(maximum) == 1:
            value = maximum[0]["facts"][0]["payload"]["value"]
            ko_max, en_max = f" 완독 시 최대 {value}배다.", f" Full reading reaches up to {value}×."
        wording = (f"자신의 기술 수준에 맞을 때 읽으면 {name[0]} 경험치 배율을 높일 수 있다.{ko_max}",
                   f"Reading it at the appropriate skill levels can raise the {name[1]} XP multiplier.{en_max}")
        if not expanded:
            wording = (f"자신의 기술 수준에 맞을 때 읽으면 {name[0]} 경험치 배율을 높일 수 있다.{ko_max}",
                       f"Reading it at the appropriate skill levels can raise the {name[1]} XP multiplier.{en_max}")
        emit(read + learning + maximum, wording,
             "reading", "reading/learning frame: reader eligibility precedes learning; maximum requires full reading")

    ignition, target_methods = [], {}
    for name, (predicate, targets, methods) in IGNITION.items():
        selected = [u for u in function(name) if
                    {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} == {predicate}]
        if selected:
            ignition += selected
            for target in targets:
                target_methods.setdefault(target, set()).update(methods)
    if ignition:
        # The implement's purpose does not promise every method for every
        # target. Fuel/tinder alternatives stay in actual exact-scope detail.
        targets = [IGNITION_TARGETS[t] for t in sorted(target_methods)]
        corpses = [u for u in function("request_corpse_burning") if
                   {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} == {lex.source.CORPSE_IGNITION}]
        if corpses:
            ignition += corpses
            targets.append(("시신", "corpses"))
        candle_tools = [u for u in units if not (set(u["fact_refs"]) & used)
            and any(f["payload"].get("role") == "tool" for f in u["facts"])
            and (any(f["payload"].get("activity") == "candle_lighting" for f in u["facts"])
                 or (u.get("context") or {}).get("activity") == "candle_lighting")
            and {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} <= {lex.source.CANDLE_LIGHT_RECIPE}]
        if candle_tools:
            ignition += candle_tools
            ignition += [u for u in units if len(u["facts"]) == 1 and u["facts"][0]["payload"] == {"activity": "candle_lighting"}
                         and {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} <= {lex.source.CANDLE_LIGHT_RECIPE}]
            targets.append(("초", "candles"))
        supplies, supply_targets = [], []
        for fn, predicate, label in (
            ('refuel_generator', lex.source.GENERATOR_REFUEL, ('발전기', 'generators')),
            ('transfer_vehicle_fuel', lex.source.VEHICLE_CONTAINER, ('차량', 'vehicles'))):
            selected = [u for u in function(fn) if {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {predicate}]
            if selected:
                supplies += selected
                supply_targets.append(label)
        if supplies:
            supplies += [u for u in function('fill_petrol_container') if {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {lex.source.PUMP_CONTAINER}]
        portable = [u for u in function('control_portable_light') if
                    {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {lex.source.LIGHT_CONTROL}]
        ignition += portable + supplies
        ko_ignition, en_ignition = '불을 붙이는 데 쓸 수 있다', 'It can be used for lighting fires'
        if supplies:
            ko_ignition = '점화와 꺼진 ' + '·'.join(t[0] for t in supply_targets) + '의 급유에 사용할 수 있다'
            en_ignition = 'It can be used for lighting fires and refueling inactive ' + lex_join([t[1] for t in supply_targets])
        if portable:
            ko_ignition = ko_ignition.removesuffix('쓸 수 있다') + '쓰거나 현재 상태가 허용하면 휴대 조명으로 쓸 수 있다'
            en_ignition += ' or as a portable light when its current state permits emission'
        emit(ignition, (ko_ignition, en_ignition),
             "ignition", "factor common ignition purpose; exact target/method alternatives and readiness remain expanded")

    drink, thirst, poison = function("drink_stored_water"), effect("thirst"), effect("poison_level")
    water, purposes = [], []
    for name, (allowed, phrase) in WATER_USES.items():
        selected = [u for u in function(name) if
                    {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} <= allowed]
        if selected:
            water += selected
            purposes.append((name, phrase))
    # Storage/carrying anchors this as a water-container overview, rather than
    # treating an extinguisher or unrelated tool as a water container.
    if not expanded and any(name == "store_water" for name, _ in purposes):
        members = list(water)
        drinking = drink and related(drink, thirst) and all(
            {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} <= FRAME_PREDICATES["drinking"]
            for u in drink + thirst + poison)
        if drinking:
            members += drink + thirst
            purposes.append(("drink_stored_water", ("갈증 해소", "quenching thirst")))
        task_names = {'water_seeded_crop': ('작물 급수', 'watering crops'),
                      'pour_water_into_container': ('다른 용기로 물 옮기기', 'transferring water to other containers'),
                      'receive_poured_water': ('다른 용기에서 물 받기', 'receiving water from other containers'),
                      'wash_vehicle_blood': ('차량 혈흔 세척', 'washing vehicle bloodstains'),
                      'extinguish_fire': ('소화', 'extinguishing fires'),
                      'drink_stored_water': ('음용', 'drinking'),
                      'supply_world_water_storage': ('저장 시설 급수', 'refilling water storage')}
        tasks = [task_names[name] for name, p in purposes if name not in {
            "store_water", "carry_water", "pour_water_into_container", "receive_poured_water"}
            and not (name == 'supply_world_water_storage' and any(n == 'pour_water_into_container' for n, _ in purposes))]
        cooking = [u for u in units if not set(u['fact_refs']) & used
                   and {tuple(sorted(f['payload'].items())) for f in u['facts']} ==
                       {(('activity', 'food_ingredient_addition'),), (('role', 'base'),)}
                   and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} <= {lex.source.COOKING_BASE}]
        if cooking:
            members += cooking
        carrying = any(name == "carry_water" for name, _ in purposes)
        receiving = any(name == 'receive_poured_water' for name, _ in purposes)
        pouring = any(name == 'pour_water_into_container' for name, _ in purposes)
        ko_text = "물을 담아 보관" + ("하거나 운반" if carrying else "") + "할 수 있다"
        en_text = "It can hold water for storage" + (" or carrying" if carrying else "")
        if pouring:
            storage = any(name == 'supply_world_water_storage' for name, _ in purposes)
            ko_text = '물을 보관·운반하거나 용기' + ('·저장 시설' if storage else '') + '에 부을 수 있다' if carrying else ko_text + '. 다른 용기에 물을 부을 수 있다'
            en_text = 'It can store, carry and pour water into containers' + (' or storage fixtures' if storage else '') if carrying else en_text + '. It can pour water into other containers'
        if tasks:
            ko_text += '. 담긴 물은 ' + "·".join(p[0] for p in tasks) + '에 쓸 수 있다'
            en_text += "; its water serves for " + lex_join([p[1] for p in tasks])
        if drinking and poison and related(drink, poison) and all(any(
                plan["qualifiers"][q]["payload"]["predicate"] == TAINT for q in u["qualifier_refs"]) for u in poison):
            members += poison
            ko_text += ' (오염수 음용은 중독 위험)'
            en_text += '; drinking tainted water risks poisoning'
        if cooking:
            ko_text += '. 재료를 더해 요리를 만들 수도 있다'
            en_text += '. Ingredients can also be added to prepare food'
        emit(members, (ko_text, en_text), "water_overview",
             "water storage/use purposes with conditional taint risk; exact quantities and bodily thresholds are expanded")
        drink, thirst, poison = function("drink_stored_water"), effect("thirst"), effect("poison_level")
    if drink and related(drink, thirst):
        members = drink + thirst
        ko_text = "담긴 물을 마셔 갈증을 줄일 수 있다"
        en_text = "Its water can be drunk to reduce thirst"
        if poison and related(drink, poison) and all(any(plan["qualifiers"][q]["payload"]["predicate"] == TAINT
                                                       for q in u["qualifier_refs"]) for u in poison):
            members += poison
            ko_text += ". 오염된 물을 마시면 중독될 수 있다"
            en_text += ". Drinking tainted water can cause poisoning"
        emit(members, (ko_text, en_text), "drinking", "drinking frame: thirst and taint effects retain different conditions")

    bellows = function("use_furnace_bellows")
    heat = [u for u in select("effect", "property", "forge_temperature") if u["facts"][0]["payload"]["direction"] == "increase"]
    if bellows and related(bellows, heat):
        emit(bellows + heat,
             ("불이 붙은 화로의 열을 높일 수 있다",
              "It can be used to raise the heat of a lit furnace"),
             "bellows", "bellows function/result frame: lit state, heat bound and endurance cost stay together")

    fertilize, growth, rot = function("apply_fertilizer"), effect("crop_growth_schedule"), effect("crop_state")
    if fertilize and related(fertilize, growth + rot) and growth and rot:
        emit(fertilize + growth + rot,
             ("살아 있는 파종 작물에 시비해 다음 성장 시점을 앞당길 수 있다. 이미 네 번 이상 시비한 작물에 더 주면 부패한다",
              "It can advance a living, seeded crop's next growth time. Fertilizing again after at least four applications rots the crop"),
             "fertilizer", "fertilizer frame: growth before over-fertilization and subsequent rot are conditional alternatives")

    smoke = function("smoke_cigarette")
    mood, sickness = effect("stress") + effect("unhappiness"), effect("food_sickness")
    if smoke and related(smoke, mood + sickness) and mood and sickness:
        emit(smoke + mood + sickness,
             ("성냥이나 라이터로 흡연할 수 있다. 흡연가의 스트레스·불행 수치를 줄이며 비흡연가의 식중독 수치를 높인다",
              "It can be smoked with a match or lighter. Smoking reduces a Smoker's stress and unhappiness but increases a non-Smoker's food sickness"),
             "smoking", "smoking frame: shared prerequisites do not merge opposite trait-dependent effects")

    view, write = function("view_written_note_pages"), function("record_written_notes")
    if view and write and all(any(plan["qualifiers"][q]["payload"]["predicate"] == lex.source.NOTE_EDIT
                                 for q in u["qualifier_refs"]) for u in write):
        fuel, tinder = [], []
        for fn, predicate, destination in (
            ('supply_campfire_fuel', lex.source.CAMP_FUEL_USE, fuel),
            ('supply_hearth_fuel', lex.source.HEARTH_FUEL, fuel),
            ('provide_campfire_tinder', lex.source.CAMP_TINDER_USE, tinder),
            ('provide_hearth_tinder', lex.source.HEARTH_TINDER, tinder),
            ('provide_industrial_tinder', lex.source.INDUSTRIAL_TINDER, tinder)):
            destination.extend(u for u in function(fn) if
                               {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {predicate})
        ko_extra = '거나 ' + '·'.join(word for members, word in ((fuel, '연료'), (tinder, '불쏘시개')) if members) + '로 소모' if fuel or tinder else ''
        en_extra = ' or consumed as ' + ' or '.join(word for members, word in ((fuel, 'fuel'), (tinder, 'tinder')) if members) if fuel or tinder else ''
        emit(view + write + fuel + tinder,
             ('메모를 읽고 적는 데 쓰' + ko_extra + '할 수 있다' if ko_extra else '메모를 읽고 적는 데 쓸 수 있다', 'It can be used for reading and writing notes' + en_extra),
             "note", "note frame: implement/access/unlocked requirements attach only to writing; page limits stay in detail")

    wear = function("wear_on_body") + function("wear_configured_clothing")
    location = select("state", "state", "worn_location")
    if wear and len(location) == 1:
        name = lex.source.BODY_LABELS[location[0]["facts"][0]["payload"]["value"]]
        emit(wear + location, (f"{name[0]} 자리에 착용할 수 있다", f"It can be worn in the {name[1]} slot"),
             "wearing", "wearing frame: the explicit equipment location qualifies the wearing capability")

    # The unresolved pair is deliberately NOT joined to its fishing function.
    for u in effect("item_condition"):
        if any(plan["qualifiers"][q]["payload"]["predicate"] == lex.source.SPEAR_FISHING_WEAR for q in u["qualifier_refs"]):
            emit([u], ("이 아이템의 내구도가 감소할 수 있다", "This item can lose condition"),
                 "wear", "independent wear statement; no causal attachment to the unresolved fishing relation")
        elif any(plan['qualifiers'][q]['payload']['predicate'] == lex.source.SPEAR_TOOL_WEAR for q in u['qualifier_refs']):
            emit([u], lex.QUALIFIER_OVERRIDES[lex.source.SPEAR_TOOL_WEAR],
                 'tool_wear', 'spear-crafting wear retains the actual use and kept-tool distinction')
    installing = [u for u in units if u["facts"][0]["payload"].get("function", "").startswith("install_vehicle_")]
    removing = [u for u in units if u["facts"][0]["payload"].get("function", "").startswith("remove_vehicle_")]
    if installing and removing:
        members = installing + removing
        predicates = {plan["qualifiers"][q]["payload"]["predicate"] for u in members for q in u["qualifier_refs"]}
        ko_extra = en_extra = ""
        if lex.source.VEHICLE_EXCHANGE_REQUIREMENTS["gastank"] in predicates:
            ko_extra, en_extra = " 탈거 전 탱크를 비운다.", " Empty the tank before removal."
        elif lex.source.VEHICLE_EXCHANGE_REQUIREMENTS["seat"] in predicates:
            ko_extra, en_extra = " 탈거 전 좌석 수납 공간을 비운다.", " Empty seat storage before removal."
        elif lex.source.VEHICLE_BATTERY_EXCHANGE in predicates:
            ko_extra, en_extra = " 배터리 탈거 시 엔진은 정지 상태여야 한다.", " Battery removal requires the engine to be stopped."
        emit(members,
             ("호환 차량의 빈 자리에 장착하거나 장착된 부품을 떼어낼 수 있다. 지정 도구·지식·선행 작업이 필요하며 실패하면 손상될 수 있다." + ko_extra,
              "It can be installed in a compatible empty vehicle slot or removed once installed. The specified tools, knowledge and prerequisites are needed; failure can cause damage." + en_extra),
             "vehicle_exchange", "vehicle exchange: empty-slot installation and installed-part removal keep their separate applicability")
    tank = function("store_vehicle_fuel") + function("transfer_vehicle_fuel") + function("supply_vehicle_engine_fuel")
    if len(tank) == 3:
        emit(tank,
             ("차량에 장착해 연료를 보관한다. 엔진을 멈추면 맞는 용기로 연료를 넣거나 뺄 수 있고 작동 중에는 엔진에 공급한다. 탱크 상태가 70 미만이면 추가로 연료를 잃을 수 있다",
              "Once installed, it stores fuel. With the engine stopped, a compatible container can add or siphon fuel; a running engine draws fuel from it. Below tank condition 70, additional fuel loss is possible"),
             "vehicle_fuel", "tank frame: installed storage, stopped-engine transfer and running-engine supply are distinct operations")
    ground, tasks = [], []
    for name, (predicate, phrase) in GROUND_TASKS.items():
        for u in function(name):
            if {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} == {predicate}:
                ground.append(u)
                tasks.append(phrase)
    if ground:
        # Target geometry and capacity are operation detail, not another use.
        short = {
            'clear_burnt_floor_ashes': ('재 청소', 'ash cleanup'),
            'collect_ground_into_bag': ('흙이나 모래, 자갈 담기', 'bagging dirt, sand or gravel'),
            'dig_furrow': ('고랑 파기', 'digging furrows'),
            'dig_grave': ('무덤 파기', 'digging graves'),
            'fill_grave': ('무덤 메우기', 'filling graves'),
            'remove_farm_plant': ('수확 없이 작물·고랑 제거', 'removing plants or furrows without harvesting'),
        }
        if expanded:
            by_name = {u['facts'][0]['payload']['function']: u for u in ground}
            grouped = set()
            for pair, wording in (
                (('dig_grave', 'fill_grave'), ('적합한 자연 지면에 무덤을 파거나 기존 무덤을 메울 수 있다', 'It can dig graves on suitable natural ground or fill existing graves')),
                (('dig_furrow', 'remove_farm_plant'), ('비어 있는 자연 지면에 고랑을 파거나 밭의 작물과 고랑을 정리할 수 있다. 작물 제거는 수확으로 처리되지 않는다', 'It can dig furrows on empty natural ground or clear plants and furrows. Removing plants does not harvest them')),
            ):
                if all(name in by_name for name in pair):
                    emit([by_name[name] for name in pair], wording, 'ground_work', 'same ground-work purpose, with target and non-harvest limits retained')
                    grouped.update(pair)
            for u in ground:
                if u['facts'][0]['payload']['function'] in grouped:
                    continue
                phrase = GROUND_TASKS[u['facts'][0]['payload']['function']][1]
                verbs = {'dig_furrow': '비어 있는 자연 지면에 고랑을 팔 수 있다', 'remove_farm_plant': '작물을 수확하지 않고 제거하거나 고랑을 없앨 수 있다', 'dig_grave': '적합한 자연 지면에 무덤을 팔 수 있다', 'fill_grave': '무덤을 메울 수 있다', 'collect_ground_into_bag': '흙이나 모래, 자갈을 포대에 담을 수 있다', 'clear_burnt_floor_ashes': '바닥의 재를 치울 수 있다'}
                emit([u], (verbs[u['facts'][0]['payload']['function']], 'It can be used for ' + phrase[1]),
                     'ground_work', 'independent ground operation with its actual target scope')
        else:
            functions = {u['facts'][0]['payload']['function'] for u in ground}
            tasks = []
            if {'dig_grave', 'fill_grave'} <= functions:
                tasks.append(('무덤 파기와 메우기', 'digging and filling graves'))
                functions -= {'dig_grave', 'fill_grave'}
            if {'dig_furrow', 'remove_farm_plant'} <= functions:
                tasks.append(('밭 만들기와 정리(수확 제외)', 'preparing and clearing planting beds without harvesting'))
                functions -= {'dig_furrow', 'remove_farm_plant'}
            tasks += [short[u['facts'][0]['payload']['function']] for u in ground if u['facts'][0]['payload']['function'] in functions]
            shaping = [task for task in tasks if task[0] in {'무덤 파기와 메우기', '밭 만들기와 정리(수확 제외)'}]
            handling = [task for task in tasks if task not in shaping]
            groups = [group for group in (shaping, handling) if group]
            emit(ground,
                 ('. '.join('·'.join(t[0] for t in group) + '에 쓸 수 있다' for group in groups),
                  '. '.join('It can be used for ' + lex_join([t[1] for t in group]) for group in groups)),
                 "ground_work", "ground-work frame: share tool readiness while keeping each operation's target constraints")
    for name, (_, pair) in FUNCTION_FRAMES.items():
        for u in function(name):
            members = [u]
            activity = {"light_candle": "candle_lighting", "extinguish_candle": "candle_extinguishing"}.get(name)
            if activity:
                members += [other for other in units if not (set(other["fact_refs"]) & used)
                    and {f["payload"].get("role") for f in other["facts"] if f["fact_kind"] == "context_role"} == {"transformation_target"}
                    and any(f["payload"].get("activity") == activity for f in other["facts"])
                    and other["qualifier_refs"] == u["qualifier_refs"]]
            emit(members, pair, name, "function-local condition integrated into its verb phrase")
    return output, used


def lex_join(values):
    return values[0] if len(values) == 1 else (" and ".join(values) if len(values) == 2
                                            else ", ".join(values[:-1]) + ", and " + values[-1])


def detail_frames(plan, locale, links):
    """Only identical application scopes may share an expanded segment."""
    output, used = packaging_frames(plan, locale, links)
    applications = [u for u in plan['units'] if len(u['facts']) == 1 and
                    u['facts'][0]['payload'].get('function') in {'apply_makeup', 'apply_eye_makeup', 'apply_lip_makeup'}
                    and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {lex.source.MAKEUP_USE, lex.source.MAKEUP_LIFECYCLE}]
    removal = [u for u in plan['units'] if len(u['facts']) == 1 and u['facts'][0]['payload'] == {'function': 'remove_registered_makeup'}
               and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {lex.source.MAKEUP_LIFECYCLE}]
    if len(applications) == len(removal) == 1:
        action, remove = applications[0], removal[0]
        for unit in (action, remove):
            output.append({'text': lex.core(unit['facts'][0], locale).rstrip('.') + '.',
                           **links([dict(unit, qualifier_refs=[])], plan), 'expression': 'public_use',
                           'placement_reason': 'independent makeup use; menu conditions retained internally',
                           'qualifier_dispositions': []})
        used.update(action['fact_refs'] + remove['fact_refs'])
    return output, used


def packaging_frames(plan, locale, links, compact=False):
    output, used = condition_frames(plan, locale, links, compact)
    for fn, activity, predicate, wording in (
        ('portion_into_bowls', 'food_portioning', lex.source.BOWL_PORTIONING,
         ('음식을 그릇에 나눌 수 있다', 'The food can be divided into bowls')),
        ('unpack_box_contents', 'package_opening', lex.source.OPENING,
         ('개봉해 내용물을 꺼낼 수 있다', 'It can be opened to retrieve its contents')),
        ('unpack_canned_food', 'package_opening', lex.source.OPENING,
         ('개봉해 내용물을 꺼낼 수 있다', 'It can be opened to retrieve its contents')),
        ('unpack_canned_food', 'package_opening', lex.source.CAN_OPENING,
         ('맞는 개봉 도구로 열어 내용물을 꺼낼 수 있다', 'It can be opened with an accepted opener to retrieve its contents')),
        ('unpack_jarred_food', 'package_opening', lex.source.OPENING,
         ('병을 열어 내용물을 꺼낼 수 있다', 'It can be opened to retrieve its contents')),
        ('unpack_produce', 'package_opening', lex.source.PRODUCE_SACK_OPENING,
         ('개봉해 농산물을 꺼낼 수 있다. 개봉해도 신선도가 회복되지는 않는다', 'It can be opened to retrieve produce; opening does not restore freshness')),
        ('unbundle_logs', 'log_binding', lex.source.LOG_BINDING,
         ('대응 제조법으로 통나무 묶음을 풀 수 있다', 'It can be unstacked using the corresponding log-bundle recipe')),
        ('prepare_frog_meat', 'frog_preparation', lex.source.FROG_PREPARATION,
         ('허용된 칼로 손질해 개구리 고기를 꺼낼 수 있다', 'It can be prepared for frog meat with an accepted knife')),
        ('unpack_eggs', 'package_opening', lex.source.EGG_CARTON_OPENING,
         ('개봉해 달걀을 꺼낼 수 있다. 개봉해도 신선도가 회복되지는 않는다', 'It can be opened to retrieve eggs; opening does not restore freshness')),
        ('unpack_box_contents', 'package_opening', lex.source.JAR_BOX_OPENING,
         ('개봉해 빈 병과 병뚜껑을 꺼낼 수 있다', 'It can be opened to retrieve empty jars and lids')),
        ('process_broken_fish_net', 'wire_recovery', lex.source.WIRE_RECOVERY,
         ('철사를 회수할 수 있다', 'It can be taken apart to recover wire')),
        ('unpack_ammunition', 'package_opening', lex.source.OPENING,
         ('개봉해 탄약을 꺼낼 수 있다', 'It can be unpacked to retrieve ammunition')),
        ('pack_into_box', 'item_packaging', lex.source.BOX_PACKING,
         ('지정 수량을 모아 상자로 포장할 수 있다', 'It can be packed into a box in the specified quantity')),
    ):
        action = [u for u in plan['units'] if len(u['facts']) == 1 and u['facts'][0]['payload'] == {'function': fn}]
        roles = [u for u in plan['units'] if {f['fact_kind'] for f in u['facts']} == {'use_context', 'context_role'}
                 and any(f['payload'] == {'activity': activity} for f in u['facts'])
                 and all(f['payload'] == {'role': 'material'} for f in u['facts'] if f['fact_kind'] == 'context_role')]
        if len(action) != 1 or len(roles) != 1 or action[0]['qualifier_refs'] != roles[0]['qualifier_refs']:
            continue
        members = action + roles
        if {plan['qualifiers'][q]['payload']['predicate'] for q in action[0]['qualifier_refs']} != {predicate}:
            continue
        condition = lex.qualifier(plan['qualifiers'][action[0]['qualifier_refs'][0]], locale)
        complete = predicate in {lex.source.JAR_BOX_OPENING, lex.source.FROG_PREPARATION,
                                lex.source.EGG_CARTON_OPENING, lex.source.PRODUCE_SACK_OPENING,
                                lex.source.WIRE_RECOVERY}
        text = lex.pair(wording, locale) + '.' + ((' 이때 ' if locale == 'ko' else ' ') + condition + '.' if not compact and not complete else '')
        segment = {'text': text, **links(members, plan), 'expression': 'exact_scope'}
        if compact:
            segment.update(placement_reason='named packaging function and material role with identical scope; method requirements in expanded',
                qualifier_dispositions=[{'qualifier_ref': q, 'applies_to_fact_refs': u['fact_refs'], 'placement': 'compact_core' if complete else 'expanded',
                                        'text': text.removesuffix('.') if complete else None, 'reason': 'named wording includes the complete condition' if complete else 'opening/packing method requirements remain expanded'}
                                       for u in members for q in u['qualifier_refs']])
        output.append(segment)
        used.update(r for u in members for r in u['fact_refs'])
    return output, used


def condition_frames(plan, locale, links, compact):
    """Known predicates already state the complete admitted action/effect.

    Sharing is permitted only for an exact qualifier scope and a closed set
    of payloads. This does not assert a new result relation.
    """
    output, used = [], set()
    cases = (
        ((lex.source.FLOOR_GLASS_PICKUP, lex.source.FLOOR_GLASS_INJURY), (
            {'function': 'pickup_floor_glass'},
            {'property': 'hand_scratch', 'direction': 'apply_during_glass_pickup'},
            {'property': 'hand_embedded_glass', 'direction': 'apply_during_glass_pickup'})),
        (lex.source.POULTICE_USE, ({'function': 'apply_poultice'}, {'property': 'poultice_factor', 'direction': 'set_doctor_random'})),
        (lex.source.WASHING_OUTCOME, ({'property': 'washed_surface_blood', 'direction': 'remove'}, {'property': 'washed_surface_dirt', 'direction': 'remove'})),
        (lex.source.STITCHING, ({'function': 'stitch_wound'}, {'property': 'stitched_state', 'direction': 'set_true'})),
        (lex.source.BULLET_REMOVAL, ({'function': 'remove_embedded_bullet'}, {'property': 'embedded_bullet', 'direction': 'remove'})),
        (lex.source.GLASS_REMOVAL, ({'function': 'remove_embedded_glass'}, {'property': 'embedded_glass', 'direction': 'remove'})),
        (lex.source.STONE_TOOL_WEAR, ({'property': 'held_stone_hammer_condition', 'direction': 'may_decrease_on_build'},)),
        (lex.source.SPEAR_STONE_LOSS, ({'property': 'inventory_presence', 'direction': 'remove'},)),
        (lex.source.MAP_REVEAL, ({'function': 'reveal_item_map_area'},)),
    )
    for predicate, payloads in cases:
        if compact and predicate == lex.source.WASHING_OUTCOME:
            continue  # The body-washing overview owns the compact combination.
        expected = set(predicate) if isinstance(predicate, tuple) else {predicate}
        candidates = [u for u in plan['units'] if len(u['facts']) == 1 and u['facts'][0]['payload'] in payloads
                      and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == expected
                      and (not compact or not u['detail_reason'])]
        if len(candidates) != len(payloads) or not all(any(u['facts'][0]['payload'] == p for u in candidates) for p in payloads):
            continue
        if len({tuple(u['qualifier_refs']) for u in candidates}) != 1:
            continue
        wording = '. '.join(lex.qualifier_clauses([plan['qualifiers'][q] for q in candidates[0]['qualifier_refs']], locale))
        segment = {'text': wording + '.', **links(candidates, plan), 'expression': 'exact_scope'}
        if compact:
            segment.update(placement_reason='complete conditional action/effect wording in one exact scope',
                qualifier_dispositions=[{'qualifier_ref': q, 'applies_to_fact_refs': u['fact_refs'],
                    'placement': 'compact_core', 'text': wording,
                    'reason': 'the full conditional statement expresses the admitted payload without repetition'}
                    for u in candidates for q in u['qualifier_refs']])
        output.append(segment)
        used.update(r for u in candidates for r in u['fact_refs'])
    return output, used

