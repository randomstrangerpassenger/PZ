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
FRAME_PREDICATES["vehicle_exchange"] = {lex.source.PANEL_INSTALL, lex.source.PANEL_REMOVE,
    *lex.source.VEHICLE_EXCHANGE_REQUIREMENTS.values(), *lex.source.RUNNING_EXCHANGE.values(),
    lex.source.VEHICLE_BATTERY_EXCHANGE, lex.source.VEHICLE_BULB_EXCHANGE}
FRAME_REQUIRED["vehicle_exchange"] = {lex.source.PANEL_INSTALL, lex.source.PANEL_REMOVE}
FRAME_PREDICATES["vehicle_fuel"] = {lex.source.VEHICLE_FUEL, lex.source.VEHICLE_FUEL_ENGINE}
FRAME_REQUIRED["vehicle_fuel"] = FRAME_PREDICATES["vehicle_fuel"]
GROUND_TASKS = {
    "clear_burnt_floor_ashes": (lex.source.ASH_CLEARING, ("탄 바닥의 재 치우기", "clearing ash from burnt floors")),
    "collect_ground_into_bag": (lex.source.GROUND_FILL, ("여유가 있는 맞는 포대에 흙·모래·자갈 담기", "collecting dirt, sand or gravel into a compatible bag with space")),
    "dig_furrow": (lex.source.FURROW_DIGGING, ("빈 자연 지면에 고랑 파기", "digging furrows on empty natural ground")),
    "dig_grave": (lex.source.GRAVE_DIGGING, ("자연 지면 두 칸에 무덤 파기", "digging graves on two suitable natural-ground squares")),
    "fill_grave": (lex.source.GRAVE_FILLING, ("시신 유무와 무관하게 무덤 메우기", "filling unfilled graves with or without corpses")),
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
    "apply_splint": ("SPLINTING", ("머리·몸통 외 골절에 부목을 대는 데 쓸 수 있다", "It can help splint fractures outside the head and torso")),
    "control_portable_light": ("LIGHT_CONTROL", ("휴대 조명으로 쓸 수 있으며 발광 여부는 현재 상태에 달려 있다", "It can serve as a portable light when its current state permits emission")),
    "light_candle": ("CANDLE_LIGHT_RECIPE", ("운전 중이 아닐 때 발화 도구로 초에 불을 붙일 수 있다", "When not driving, a fire-starting item can be used to light the candle")),
    "extinguish_candle": ("CANDLE_EXTINGUISH_RECIPE", ("운전 중이 아닐 때 켜진 초를 끄는 제작법에 쓴다", "When not driving, it can be supplied to the lit-candle extinguishing recipe")),
    "extinguish_on_unequip": ("CANDLE_UNEQUIP", ("장착한 초를 손에서 빼거나 버리면 꺼진 초로 바뀐다", "Unequipping or dropping the equipped candle changes it to an unlit candle")),
    "build_wooden_barricade": ("WOOD_BARRICADE", ("판자를 받는 문·창문에 망치·판자·못으로 바리케이드를 추가할 수 있다", "An accepted hammer, planks and nails can add barricades to eligible doors or windows")),
    "remove_barricade": ("WOOD_UNBARRICADE", ("철거 도구로 바리케이드 판자를 하나씩 떼며 못은 돌려받지 못한다", "An accepted removal tool takes off barricade planks one at a time without returning nails")),
    "fish_with_spear": ("SPEAR_FISHING", ("파손되지 않은 창으로 물가에서 미끼 없이 낚시하며 포획은 보장되지 않는다", "An unbroken spear can fish at water without bait; catches are not guaranteed")),
    "water_seeded_crop": ("CROP_WATERING", ("물을 더 받을 수 있는 파종 작물에 물을 준다", "It waters seeded crops that can receive more water")),
    "wash_vehicle_blood": ("VEHICLE_WASHING", ("물로 접근 가능한 차량의 혈흔을 씻는다", "Its water washes accessible vehicle bloodstains")),
    "extinguish_fire": ("EXTINGUISH_CONDITIONS", ("잔량이 있으면 불타는 지면·캐릭터의 소화에 쓸 수 있다", "With uses remaining, it can help extinguish burning ground or characters")),
    "apply_garment_patch": ("GARMENT_PATCHING", ("실·바늘과 함께 패치 없는 의류 부위의 구멍을 덧대거나 패딩을 추가하는 데 쓴다", "With thread and a needle, it can patch holes or add padding to unpatched garment parts")),
    "clean_burn": ("BURN_CLEANING", ("세척이 필요한 화상에 충분한 강도의 붕대 재료로 쓰며 통증이 생길 수 있다", "Sufficiently strong bandaging material can clean burns needing washing; treatment can cause pain")),
    "apply_bandage": ("BANDAGE_APPLICATION", ("붕대를 댈 수 있는 부위에 붕대 재료로 사용해 소모한다", "It is consumed as bandaging material on a body part that permits bandaging")),
    "fire_ammunition": ("FIRING", ("탄약이 준비되고 탄 걸림이 없어야 사격할 수 있다. 낡은 총은 잔탄이 있을 때 걸릴 수 있다", "Firing requires ready ammunition and no jam. A worn gun with rounds remaining can jam")),
    "convert_lamp_to_battery": ("LAMP_CONVERSION", ("전기 기술 5에서 드라이버와 전자 스크랩으로 조명을 건전지형으로 개조한다. 건전지는 별도로 넣는다", "At Electricity 5, a screwdriver and electronic scrap convert a lamp to battery power; add the battery separately")),
    "dismantle_built_object": ("THUMPABLE_SCRAP", ("톱·드라이버로 분해 가능한 건축물을 해체하며 보호 구역 규칙을 따른다. 회수량은 정해져 있지 않다", "A saw and screwdriver can dismantle eligible built objects under safehouse rules; salvage amounts vary")),
    "manage_weapon_attachments": ("WEAPON_ATTACHMENT_TOOL", ("사용 가능한 드라이버로 호환 무기의 부착물을 장착·제거하며 드라이버는 소모하지 않는다", "A usable screwdriver installs or removes compatible weapon parts without being consumed")),
    "service_vehicle_parts": ("VEHICLE_TOOL_USE", ("차량 부품의 도구·제작법 조건에 맞춰 장착·탈거에 쓰며 실패나 부품 손상이 생길 수 있다", "It serves in vehicle-part installation or removal with the required tools and recipe; failure or part damage is possible")),
    "load_matching_ammunition": ("LOADING", ("빈 공간이 있는 호환 총기·탄창에 장전하는 탄약이다", "It is ammunition for compatible firearms or magazines with loading space")),
    "fill_magazine": ("MAGAZINE_FILL", ("탄창의 빈 공간에 호환 탄약을 넣을 수 있다", "Matching rounds can be loaded into the magazine's free capacity")),
    "empty_magazine": ("MAGAZINE_EMPTY", ("탄창의 잔탄을 꺼낼 수 있다", "Remaining rounds can be removed from the magazine")),
    "take_pills": ("PILL_TAKING", ("소지한 알약을 복용할 수 있다", "The carried pills can be taken")),
    "set_alarm": ("ALARM_SETTING", ("알람을 켜거나 끄고 시각을 설정할 수 있다", "Its alarm state and time can be set")),
    "stop_alarm": ("ALARM_STOPPING", ("울리는 알람을 끌 수 있다", "Its ringing alarm can be stopped")),
    "fill_petrol_container": ("PUMP_CONTAINER", ("전원이 공급되는 주유소에서 남은 연료를 용기의 빈 공간에 받을 수 있다", "It can receive available fuel from a powered pump into its free capacity")),
    "transfer_vehicle_fuel": ("VEHICLE_CONTAINER", ("엔진이 꺼진 차량과 호환 용기 사이의 연료 이동에 쓸 수 있다", "It can transfer fuel between a stopped-engine vehicle and a compatible container")),
    "refuel_generator": ("GENERATOR_REFUEL", ("꺼진 발전기의 빈 연료 공간에 휘발유를 보충할 수 있다", "It can add petrol to an inactive generator with fuel space")),
    "pitch_tent": ("CAMP_PLACEMENT", ("배치 가능한 빈 공간에 텐트를 설치할 수 있다", "It can pitch a tent in a suitable clear space")),
}
for _function, (_condition, _pair) in FUNCTION_FRAMES.items():
    FRAME_PREDICATES[_function] = {getattr(lex.source, _condition)}
    FRAME_REQUIRED[_function] = FRAME_PREDICATES[_function]
FRAME_PREDICATES["apply_bandage"] = {lex.source.BANDAGE_APPLICATION, lex.source.DIRTY_BANDAGING,
    "A body part is eligible for bandaging; the material remains in inventory and the patient does not move out of reach."}
FRAME_PREDICATES["fire_ammunition"] = {lex.source.FIRING, lex.source.GUN_FIRING_CYCLE}
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
    'support_makeup_mirror': ({lex.source.MAKEUP_LIFECYCLE},
        ('선택한 화장품의 화장창을 열 때 소지하거나 근처에 두는 거울로 쓴다', 'It serves as a carried or nearby mirror for opening the selected cosmetic’s makeup window')),
    'place_fishing_net': ({lex.source.NET_PLACEMENT},
        ('물에 설치하는 어망이며 설치 성공은 조건에 달려 있다', 'It is a fishing net for placement in water when placement conditions hold')),
    'check_fishing_net': ({lex.source.NET_CHECKING},
        ('설치 후 한 시간 이상 지나면 미끼 물고기 포획을 확인하며 포획 실패나 어망 파손이 생길 수 있다', 'After at least one hour, the placed net can be checked for bait fish; catches are not guaranteed and the net can break')),
    'remove_fishing_net': ({lex.source.NET_REMOVAL},
        ('설치한 어망을 회수할 수 있으나 원래 물품 상태는 보존하지 않는다', 'The placed net can be retrieved without preserving its original item state')),
    'supply_drum_logs': ({lex.source.DRUM_LOGS},
        ('빈 금속 드럼에 통나무 다섯 개를 공급하며 점화·숯 회수는 별도다', 'It supplies five logs to an empty metal drum; lighting and charcoal retrieval are separate')),
    'groom_beard': ({lex.source.BEARD_GROOMING},
        ('파손되지 않은 도구로 기존 수염을 다듬거나 면도한다', 'An unbroken tool can trim or shave an existing beard')),
    'send_remote_trigger': ({lex.source.REMOTE_TRIGGER},
        ('연결 ID가 맞고 조종 범위 안에 있는 장치에 원격 작동을 요청한다', 'It requests remote activation of a device with a matching link ID within range')),
    'inflate_vehicle_tire': ({lex.source.TIRE_INFLATION},
        ('펌프로 장착 타이어에 공기를 넣으며 취소해도 넣은 공기는 남는다', 'A pump adds air to an installed tire; air already added remains after cancellation')),
    'deflate_vehicle_tire': ({lex.source.TIRE_DEFLATION},
        ('공기가 남은 장착 타이어에서 펌프 없이 공기를 뺀다', 'It releases remaining air from an installed tire without a pump')),
    'light_campfire_by_friction': ({lex.source.CAMP_FRICTION},
        ('연료가 든 꺼진 모닥불에 나무 마찰로 점화를 시도한다. 지구력을 소모하며 막대가 부러질 수 있다', 'It attempts wood-friction ignition of an unlit, fueled campfire, spending endurance with a risk of breaking the stick')),
    'operate_vehicle_battery_charger': ({lex.source.CHARGER_CONTROLS},
        ('설치한 충전기에 배터리를 연결·분리하며 전력이 있으면 충전을 조작한다', 'It connects or removes batteries and controls charging when powered')),
    'place_vehicle_battery_charger': ({lex.source.CHARGER_PLACEMENT},
        ('한 칸에 하나씩 설치하며 배터리가 없을 때 회수하는 차량 배터리 충전기다', 'The charger can be placed one per square and retrieved without a battery')),
    'avoid_first_door_alarm_trigger': ({lex.source.KEY_ALARM},
        ('맞는 차량의 첫 문 개방 경보를 피하지만 이미 울리는 경보는 끄지 않는다', 'It avoids the matching vehicle’s first door-opening alarm, but does not stop a ringing alarm')),
    'operate_door_lock': ({lex.source.DOOR_KEY_USE},
        ('맞는 닫힌 문의 잠금을 조작하며 소모되지 않는다', 'It operates a matching closed door’s lock without being consumed')),
    'remove_matching_padlock': ({lex.source.PADLOCK_KEY_USE},
        ('맞는 구조물 자물쇠를 제거할 때 소모하는 열쇠다', 'It is consumed when removing a matching structure padlock')),
    'request_matching_vehicle_start': ({lex.source.VEHICLE_KEY_USE},
        ('운전석에서 맞는 차량의 시동·점화장치를 조작하는 열쇠다', 'It operates a matching vehicle’s start and ignition controls from the driver’s seat')),
    'satisfy_vehicle_mechanics_key': ({lex.source.KEY_MECHANICS},
        ('맞는 차량의 정비 작업에서 열쇠 요구를 충족한다', 'It meets the key requirement of a matching vehicle mechanics operation')),
    'install_combination_padlock': ({lex.source.CODE_LOCK_USE},
        ('잠기지 않은 지원 구조물에 번호를 정해 설치하는 자물쇠다', 'It installs on an unlocked supported structure with a chosen code')),
    'remove_combination_padlock': ({lex.source.CODE_UNLOCK},
        ('맞는 번호로 설치된 번호 자물쇠를 제거한다', 'Its matching code removes an installed combination lock')),
    'transfer_compost': ({lex.source.COMPOST_TRANSFER},
        ('퇴비와 여유 공간이 있는 통·포대 사이에서 퇴비를 옮긴다', 'It transfers compost between a bin and bag with supply and free capacity')),
    'receive_compost': ({lex.source.COMPOST_TRANSFER},
        ('여유 공간에 퇴비통의 퇴비를 담는 자루다', 'It receives compost from a bin into its available capacity')),
    'fill_ground_bag': ({lex.source.GROUND_FILL},
        ('흙 파기 도구로 대응하는 지면의 흙·자갈·모래를 빈 공간에 담는 포대다', 'It receives compatible ground material into free space with a digging tool')),
    'pour_ground_cover': ({lex.source.GROUND_POUR},
        ('내용물을 받을 수 있는 바닥에 붓는 포대다', 'Its contents can be poured onto a suitable floor')),
    'read_recorded_media_label': ({lex.source.MEDIA_LABEL},
        ('기록이 배정된 매체를 소지하면 내용 안내를 읽을 수 있다', 'Its assigned recording’s description can be read while carried')),
    'insert_recorded_media': ({lex.source.MEDIA_INSERT},
        ('전원이 켜진 대응 기기의 빈 자리에 넣어 재생하는 기록 매체다', 'It is recorded media for an empty compatible slot; playback needs the device on')),
    'connect_radio_headphones': ({lex.source.HEADPHONE_CONNECTION},
        ('TV가 아닌 휴대 기기의 빈 헤드폰 자리에 연결한다', 'It connects to an empty headphone slot on a portable non-TV device')),
    'operate_installed_vehicle_door': ({lex.source.PANEL_DOOR},
        ('정지한 차량의 장착 문·덮개를 필요시 잠금 해제해 여닫는다', 'It opens or closes an installed door or cover on a stopped vehicle after unlocking if needed')),
    'operate_installed_vehicle_lock': ({lex.source.PANEL_LOCK},
        ('작동하는 장착 문 잠금 장치를 접근 위치별 열쇠 조건에 따라 조작한다', 'It controls a working installed door lock under the access position’s key requirements')),
    'operate_installed_vehicle_window': ({lex.source.PANEL_WINDOW},
        ('파손되지 않은 장착 개폐식 차량 창문을 여닫는다', 'It opens or closes an unbroken installed openable vehicle window')),
    'repair_vehicle_engine': ({lex.source.ENGINE_REPAIR},
        ('예비 부품·렌치와 정비 기술·접근 조건을 갖춘 손상 엔진 수리에 쓴다', 'It serves in damaged-engine repair with spare parts, a wrench and the required skill and access')),
    'erase_map_annotations': ({lex.source.MAP_ERASURE},
        ('지도의 글·기호 주석을 지우며 수정·이동에는 필기구도 필요하다', 'It erases map annotations; editing or moving them also needs a writing implement')),
    'groom_hair': ({lex.source.HAIR_GROOMING},
        ('현재 머리 길이에서 허용하는 스타일에 맞춰 머리를 손질하는 데 쓴다', 'It supports grooming styles allowed by the current hair length')),
    'serve_as_eating_utensil': ({lex.source.MEAL_UTENSIL},
        ('식사에 필수는 아닌 도구이며 지원 동작에서는 숟가락이 포크보다 우선한다', 'It is an optional eating utensil; supported animations prefer a spoon over a fork')),

    'plaster_supported_structure': ({lex.source.PLASTER_USE},
        ('목공 4와 석고 양동이로 지원하는 구조물에 석고를 발라 칠할 수 있게 한다', 'With Woodwork four and a plaster bucket, it plasters eligible structures to make them paintable')),
    'prepare_opened_food_ingredient': ({lex.source.OPENED_FOOD, lex.source.OPENING, lex.source.CAN_OPENING, lex.source.COOKING_ACTION},
        ('개봉한 내용물을 허용하는 요리의 재료로 쓸 수 있다', 'Its opened contents can be ingredients in preparations that accept them')),

    'build_metal_barricade': ({lex.source.METAL_BARRICADE},
        ('토치와 금속판 또는 막대로 문·창문에 금속 바리케이드를 설치하며 용접 마스크는 필요하지 않다', 'A torch and metal sheet or bars can barricade doors or windows without a welding mask')),
    'remove_metal_barricade': ({lex.source.METAL_UNBARRICADE},
        ('토치 사용량을 소모해 금속 바리케이드를 제거하며 무손상 회수는 보장되지 않는다', 'It spends torch uses to remove metal barricades; full-condition salvage is not guaranteed')),
    'dismantle_burnt_vehicle': ({lex.source.BURNT_VEHICLE_USE},
        ('용접 마스크와 토치로 불타거나 파손된 차량을 분해하며 회수 재료는 확률에 따른다', 'A welding mask and torch can dismantle burnt or smashed vehicles; salvage varies by chance')),
    'store_vehicle_items': ({lex.source.VEHICLE_STORAGE},
        ('차량에 장착된 대응 수납 부품에서 허용된 물품을 보관한다', 'It stores admitted items in its corresponding installed vehicle storage part')),
    'store_and_retrieve_items': ({'Storage requires room and item admission; transfer requires accessible distinct source/destination, permitted removal and applicable multiplayer restrictions.'},
        ('빈 공간에 허용된 물건을 넣고 꺼내는 수납 용기다', 'It stores and retrieves admitted items within its available capacity')),
    'wear_container_on_back': ({lex.source.BACK_CONTAINER},
        ('등에 메어 착용할 수 있다', 'It can be worn on the back')),
    'switch_declared_clothing_form': ({lex.source.CLOTHING_FORM},
        ('지원하는 다른 형태로 바꾸어 착용할 수 있다', 'It can be changed into and worn in a supported alternate form')),
    'chop_tree': ({lex.source.CHOPPING},
        ('사용 가능한 도끼로 접근 가능한 나무를 벨 수 있다', 'A usable axe can chop reachable trees')),
    'cut_bushes_and_vines': ({lex.source.PLANT_CUTTING},
        ('사용 가능한 자르기 도구로 덤불·벽 덩굴을 제거하며 도구가 마모될 수 있다', 'A usable cutting tool can remove bushes and wall vines and may wear')),
    'link_remote_device': ({lex.source.REMOTE_LINK},
        ('함께 소지한 대응 조종기·장치의 원격 연결을 설정한다', 'It links a compatible controller and device carried together')),
    'reset_remote_id': ({lex.source.REMOTE_RESET},
        ('선택한 물품의 원격 연결만 해제한다', 'It resets only the selected item\'s remote link')),
    'place_trigger_device': ({lex.source.DEVICE_WORLD_PLACEMENT},
        ('설치 가능한 장치를 소지한 채 현재 칸에 놓을 수 있다', 'A carried, placement-enabled device can be placed on the current square')),
    'place_noise_device': ({lex.source.DEVICE_PLACEMENT},
        ('소지한 장치를 현재 칸에 설치할 수 있다', 'The carried device can be placed on the current square')),
    'retrieve_placed_device': ({lex.source.DEVICE_RETRIEVAL},
        ('회수 가능한 설치 장치를 소지품으로 가져올 수 있다', 'A recoverable placed device can be returned to inventory')),
    'set_device_timer': ({lex.source.DEVICE_TIMER_CONTROL, lex.source.DEVICE_DELAY},
        ('타이머를 지원하는 장치에 양수의 지연 시간을 설정할 수 있다', 'A positive delay can be set on a device that supports a timer')),
    'fish_with_rod': ({lex.source.ROD_FISHING, lex.source.FISHING_EXECUTION, lex.source.FISHING_LURES, lex.source.FISHING_MATCHES},
        ('물가에서 맞는 미끼와 함께 쓰는 낚싯대이며 포획은 보장되지 않는다', 'It is a rod for fishing at water with matching bait; catches are not guaranteed')),
    'bait_rod_fishing': ({lex.source.ROD_FISHING, lex.source.FISHING_EXECUTION, lex.source.FISHING_MATCHES, lex.source.FISHING_LURE_LOSS},
        ('물가의 낚싯대 낚시에 쓰는 미끼이며 포획은 보장되지 않는다', 'It is bait for rod fishing at water; catches are not guaranteed')),
    'control_installed_generator': ({lex.source.GENERATOR_CONTROL},
        ('지식·연료·상태 조건에 따라 설치한 발전기를 연결하고 가동할 수 있다', 'The installed generator can be connected and operated subject to knowledge, fuel and condition requirements')),
    'handle_generator': ({lex.source.GENERATOR_HANDLING},
        ('발전기를 양손으로 들거나 연결을 해제한 뒤 회수할 수 있다', 'The generator can be carried in both hands or retrieved after disconnection')),
    'inspect_generator': ({lex.source.GENERATOR_INSPECTION},
        ('설치한 발전기의 연료·상태·전력 사용 정보를 확인할 수 있다', 'Its installed generator fuel, condition and power use can be inspected')),
    'repair_generator': ({lex.source.GENERATOR_REPAIR},
        ('발전기 지식과 전자 스크랩으로 꺼진 손상 발전기를 수리할 수 있다', 'Generator knowledge and electronic scrap allow repair of an inactive damaged generator')),
    'connect_to_vehicle_battery_charger': ({lex.source.CHARGER_CONTROLS},
        ('덜 충전된 차량 배터리를 전원이 있는 충전기에 연결해 충전할 수 있다', 'A vehicle battery below full charge can be connected to a powered charger for charging')),
    'install_light_bulb': ({lex.source.LAMP_BULB},
        ('교체 가능한 조명의 빈 자리에 넣는 전구이며 전력은 별도로 필요하다', 'It fits an empty bulb slot in a modifiable lamp; power is required separately')),
    'clean_world_blood': ({lex.source.BLOOD_CLEANING},
        ('표백제와 청소 도구로 바닥 혈흔을 지우는 데 쓴다', 'It serves in cleaning floor bloodstains with bleach and a cleaning tool')),
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


def frames(plan, locale, links):
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
    for fn, target in (('apply_eye_makeup', ('눈 분장', 'eye makeup')),
                       ('apply_lip_makeup', ('입술 분장', 'lip makeup')),
                       ('apply_makeup', ('분장', 'makeup'))):
        application, removal = function(fn), function('remove_registered_makeup')
        if application and removal:
            emit(application + removal,
                 (target[0] + '을 하거나 등록된 착용 분장을 지우는 데 쓴다',
                  'It is used to apply ' + target[1] + ' or remove registered worn makeup'),
                 'makeup', 'coordinate makeup application and removal; consumption and preview lifetime remain expanded')
    washing = function('wash_body')
    washed = [u for u in units if len(u['facts']) == 1 and u['facts'][0]['payload'] in (
        {'property': 'washed_surface_blood', 'direction': 'remove'},
        {'property': 'washed_surface_dirt', 'direction': 'remove'})]
    if washing and len(washed) == 2:
        emit(washing + washed,
             ('물을 쓰는 몸 세척의 세척제다. 처리한 신체·의류 부위의 피·때를 지우며 세제 없이도 씻을 수 있고 물이 부족하면 일부만 씻긴다',
              'It is a supply for washing the body with water. Washing clears blood and dirt from processed body or clothing parts; soap is optional and limited water can leave washing incomplete'),
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
                 (ko_start + f'이 작물의 낱알 씨앗 {count}개를 아직 씨가 없는 경작 고랑 하나에 심는다. 성장·수확은 보장하지 않는다',
                  en_start + f'{count} loose seeds of this crop per unseeded plowed furrow; growth and harvest are not guaranteed'),
                 'sowing', 'seed packet opening is distinct from consumption of the configured loose-seed count')
    for fn, prop, direction, frame, wording in (
        ('dry_the_body', 'body_wetness', 'decrease', 'drying',
         ('사용량이 남은 수건을 소지해 젖은 몸을 닦으며 사용량을 소모한다. 완전히 마르는 것은 보장되지 않는다',
          'A carried towel with uses remaining reduces body wetness while spending uses; complete dryness is not guaranteed')),
        ('disinfect_wound', 'wound_alcohol_level', 'increase', 'disinfection',
         ('소지한 소독제를 소모해 붕대가 없는 치료 가능 부위의 알코올 수치를 높인다',
          'It spends carried disinfectant to raise the alcohol level of an eligible unbandaged body part')),
        ('treat_crop_mildew', 'crop_mildew_level', 'decrease', 'crop_treatment',
         ('흰가루병이 있는 작물에 살포해 사용당 수치를 5씩 최소 0까지 낮춘다',
          'It treats crops with mildew, reducing the level by five per use to a minimum of zero')),
        ('treat_crop_flies', 'crop_flies_level', 'decrease', 'crop_treatment',
         ('해충이 있는 작물에 살포해 사용당 수치를 5씩 최소 0까지 낮춘다',
          'It treats crops with flies, reducing the level by five per use to a minimum of zero')),
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
             ('소지한 염색약을 소모해 존재하는 머리카락이나 수염을 염색약 색으로 바꾼다',
              'It consumes carried dye to set existing hair or beard to the dye color'),
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
    curtains = function('install_sheet_curtain') + function('control_sheet_curtain')
    if len(curtains) == 2:
        emit(curtains,
             ('커튼이 없는 대응 창문·문에 설치하는 커튼 재료이며 설치 후 열고 닫거나 떼어낼 수 있다',
              'It supplies a curtain for an eligible window or door without one; the installed curtain can be opened, closed or removed'),
             'curtain', 'installation target and installed-object controls retain their distinct states')
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
             ('남은 충전량을 호환되는 ' + '·'.join(t[0] for t in targets) + '의 전원으로 공급할 수 있다',
              'It can supply its remaining charge to compatible ' + lex_join([t[1] for t in targets])),
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
                 (names[0] + '용 설치 덫으로 미끼·포획물·덫을 회수할 수 있다. 포획에는 신선한 대응 미끼와 시간·지역 조건이 필요하며 성공은 보장되지 않는다',
                  'It is a placeable trap for ' + names[1] + ', with bait, catch and trap retrieval. Catches require matching fresh bait and time/area conditions and are not guaranteed'),
                 'trap', 'trap placement, handling and conditional capture overview; exact targets, losses and controls remain expanded')

    # A first-contact overview uses role noun phrases plus locally modified
    # purpose phrases, rather than appending complete fact sentences. The
    # crafting targets and operation procedures remain independently expanded.
    activities_allowed = {"construction", "carpentry_menu_construction", "woodworking", "metal_forging",
                          "smithing_parts", "shovel_smithing", "moving_furniture"}
    role_units = [u for u in units if (any(f["payload"].get("activity") in activities_allowed for f in u["facts"])
                  or (u.get("context") or {}).get("activity") in activities_allowed)
                  and any(f["payload"].get("role") in {"material", "tool"} for f in u["facts"])]
    roles = {f["payload"]["role"] for u in role_units for f in u["facts"] if f["fact_kind"] == "context_role"}
    if role_units and len(roles) == 1:
        role_name = next(iter(roles))
        purposes = []
        purpose_names = []
        members = list(role_units)
        for name, condition, phrase in (
            ("melee_attack", lex.source.MELEE, ("근접 공격", "melee attacks")),
            ("apply_splint", lex.source.SPLINTING, ("부목 적용", "applying splints")),
            ("build_wooden_barricade", lex.source.WOOD_BARRICADE, ("판자 바리케이드 설치", "adding plank barricades")),
            ("remove_barricade", lex.source.WOOD_UNBARRICADE, ("판자 바리케이드 철거", "removing plank barricades")),
        ):
            selected = [u for u in function(name) if
                        {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} == {condition}]
            if selected:
                members += selected
                purposes.append(phrase)
                purpose_names.append(name)
        if {'build_wooden_barricade', 'remove_barricade'} <= set(purpose_names):
            purposes = [phrase for name, phrase in zip(purpose_names, purposes)
                        if name not in {'build_wooden_barricade', 'remove_barricade'}]
            purposes.append(('판자 바리케이드 설치·철거', 'adding or removing plank barricades'))
        fuel = [u for name, predicate in (("supply_campfire_fuel", lex.source.CAMP_FUEL_USE),
                 ("supply_hearth_fuel", lex.source.HEARTH_FUEL), ("supply_furnace_fuel", lex.source.FURNACE_FUEL))
                for u in function(name) if {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} == {predicate}]
        if purposes or fuel:
            members += fuel
            contexts = {f["payload"]["activity"] for u in role_units for f in u["facts"] if f["fact_kind"] == "use_context"}
            contexts.update(u["context"]["activity"] for u in role_units if u.get("context"))
            members += [u for u in units if len(u["facts"]) == 1 and u["facts"][0]["fact_kind"] == "use_context"
                        and u["facts"][0]["payload"]["activity"] in contexts]
            # Only these admitted construction/crafting children share a parent
            # purpose. Furniture moving is independent, never a crafting subtype.
            labels = []
            if contexts & {'construction', 'carpentry_menu_construction'}:
                labels.append(('건축', 'construction'))
            if contexts & {'woodworking', 'metal_forging', 'smithing_parts', 'shovel_smithing'}:
                labels.append(('제작', 'crafting'))
            if 'moving_furniture' in contexts:
                labels.append(('가구 이동', 'moving furniture'))
            names = {loc: [lex.pair(label, loc) for label in labels] for loc in ('ko', 'en')}
            ko_text = '일부 ' + "·".join(names["ko"]) + " 작업의 " + lex.ROLES[role_name][0] + "이며, "
            en_text = "It serves as " + lex.ROLES[role_name][1] + " for certain " + lex_join(names["en"]) + ' tasks'
            ko_tail = ", ".join(p[0] for p in purposes) + "에 쓸 수 있다" if purposes else ""
            en_tail = (", can be used for " + lex_join([p[1] for p in purposes])) if purposes else ""
            if fuel:
                ko_tail = (", ".join(p[0] for p in purposes) + "에 쓰거나 " if purposes else "") + "연료로 소모할 수 있다"
                en_tail += (", and " if en_tail else " and ") + "can be consumed as fuel"
            elif en_tail:
                en_tail = en_tail.replace(", can be used for ", " and can be used for ", 1)
            emit(members, (ko_text + ko_tail, en_text + en_tail), "role_overview",
                 "role overview with distinct purpose modifiers; recipe targets, operation prerequisites and results are expanded")

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
        emit(read + learning + maximum,
             (f"글을 읽을 수 있고 깨어 있으며 책의 기술 범위에 맞으면 {name[0]} 경험치 배율을 높인다. 현재보다 높은 배율만 적용된다.{ko_max}",
              f"Literate, awake readers within the book's skill range can raise their {name[1]} XP multiplier above its current value.{en_max}"),
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
            ko_ignition = '점화와 꺼진 ' + '·'.join(t[0] for t in supply_targets) + '의 급유에 쓰는 연료 용기다'
            en_ignition = 'It is a fuel container for lighting fires and refueling inactive ' + lex_join([t[1] for t in supply_targets])
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
    if any(name == "store_water" for name, _ in purposes):
        members = list(water)
        drinking = drink and related(drink, thirst) and all(
            {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} <= FRAME_PREDICATES["drinking"]
            for u in drink + thirst + poison)
        if drinking:
            members += drink + thirst
            purposes.append(("drink_stored_water", ("갈증 해소", "quenching thirst")))
        task_names = {'water_seeded_crop': ('작물 급수', 'watering crops'),
                      'wash_vehicle_blood': ('차량 세척', 'washing vehicles'),
                      'extinguish_fire': ('소화', 'extinguishing fires'),
                      'drink_stored_water': ('음용', 'drinking'),
                      'supply_world_water_storage': ('저장 시설 급수', 'refilling water storage')}
        tasks = [task_names[name] for name, p in purposes if name not in {"store_water", "carry_water"}]
        cooking = [u for u in units if not set(u['fact_refs']) & used
                   and {tuple(sorted(f['payload'].items())) for f in u['facts']} ==
                       {(('activity', 'food_ingredient_addition'),), (('role', 'base'),)}
                   and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {lex.source.COOKING_BASE}]
        if cooking:
            members += cooking
        carrying = any(name == "carry_water" for name, _ in purposes)
        ko_text = "물을 보관" + ("·운반" if carrying else "") + "할 수 있다"
        en_text = "It can store" + (" and carry" if carrying else "") + " water"
        if tasks:
            ko_text = ko_text.removesuffix("할 수 있다") + "하며, 담긴 물은 " + "·".join(p[0] for p in tasks) + "에 쓸 수 있다"
            en_text += " for " + lex_join([p[1] for p in tasks])
        if cooking:
            ko_text = ko_text.removesuffix('할 수 있다').removesuffix('쓸 수 있다').rstrip() + ' 쓰고, 재료를 더해 요리를 만들 수도 있다' if tasks else '물을 보관·운반하거나 재료를 더해 요리를 만들 수 있다'
            en_text += '; ingredients can also be added to prepare food'
        if drinking and poison and related(drink, poison) and all(any(
                plan["qualifiers"][q]["payload"]["predicate"] == TAINT for q in u["qualifier_refs"]) for u in poison):
            members += poison
            ko_text += ' (오염수 음용은 중독 위험)'
            en_text += '; drinking tainted water risks poisoning'
        emit(members, (ko_text, en_text), "water_overview",
             "water storage/use purposes with conditional taint risk; exact quantities and bodily thresholds are expanded")
        drink, thirst, poison = function("drink_stored_water"), effect("thirst"), effect("poison_level")
    if drink and related(drink, thirst):
        members = drink + thirst
        ko_text = "갈증이 있을 때 담긴 물을 마셔 갈증을 줄일 수 있다"
        en_text = "Its water can be drunk to reduce thirst when thirsty"
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
             ("불이 붙고 열이 낮은 화로에서 풀무로 열을 높이며 지구력을 소모한다",
              "Bellows raise the heat of a lit furnace below maximum heat and consume endurance"),
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
             ("성냥이나 라이터로 흡연한다. 포만 상태가 허용할 때 흡연가의 스트레스·불행 수치를 줄이며 비흡연가의 식중독 수치를 높인다",
              "It can be smoked with a match or lighter. When satiety permits, smoking reduces a Smoker's stress and unhappiness but increases a non-Smoker's food sickness"),
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
        emit(wear + location, (f"{name[0]} 자리에 착용한다", f"It is worn in the {name[1]} slot"),
             "wearing", "wearing frame: the explicit equipment location qualifies the wearing capability")

    # The unresolved pair is deliberately NOT joined to its fishing function.
    for u in effect("item_condition"):
        if any(plan["qualifiers"][q]["payload"]["predicate"] == lex.source.SPEAR_FISHING_WEAR for q in u["qualifier_refs"]):
            emit([u], ("내구도가 감소할 수 있다", "It can lose condition"),
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
            'clear_burnt_floor_ashes': ('바닥 재 치우기', 'clearing floor ash'),
            'collect_ground_into_bag': ('흙·모래·자갈 포대 담기', 'bagging dirt, sand or gravel'),
            'dig_furrow': ('고랑 파기', 'digging furrows'),
            'dig_grave': ('무덤 파기', 'digging graves'),
            'fill_grave': ('무덤 메우기', 'filling graves'),
            'remove_farm_plant': ('수확 없이 작물·고랑 제거', 'removing plants or furrows without harvesting'),
        }
        tasks = [short[u['facts'][0]['payload']['function']] for u in ground]
        emit(ground,
             ("사용 가능한 상태에서 " + "·".join(t[0] for t in tasks) + " 작업에 쓸 수 있다",
              "When usable, it can be used for " + (", ".join(t[1] for t in tasks[:-1]) + ", and " if len(tasks) > 1 else "") + tasks[-1][1]),
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
        core = lex.core(action['facts'][0], locale)
        conditions = lex.qualifier_clauses([plan['qualifiers'][q] for q in action['qualifier_refs']], locale)
        text = core + '. ' + '. '.join(conditions) + '. ' + lex.pair(
            ('화장품 사용량은 소모하지 않으며 창을 닫으면 미확정 미리보기를 취소한다',
             'Cosmetic uses are not spent; closing the window cancels an uncommitted preview'), locale) + '.'
        output.append({'text': text, **links([action], plan), 'expression': 'exact_scope'})
        output.append({'text': lex.pair(('같은 접근 조건에서 등록된 착용 분장도 지울 수 있다',
                                        'Under the same access conditions, registered worn makeup can also be removed'), locale) + '.',
                       **links([remove], plan), 'expression': 'exact_scope'})
        used.update(action['fact_refs'] + remove['fact_refs'])
    return output, used


def packaging_frames(plan, locale, links, compact=False):
    output, used = condition_frames(plan, locale, links, compact)
    for fn, activity, predicate, wording in (
        ('portion_into_bowls', 'food_portioning', lex.source.BOWL_PORTIONING,
         ('음식을 그릇에 나눌 수 있다', 'The food can be divided into bowls')),
        ('unpack_box_contents', 'package_opening', lex.source.OPENING,
         ('내용물을 꺼낼 수 있는 포장 재료다', 'It is packaged material that can be opened to retrieve its contents')),
        ('unpack_canned_food', 'package_opening', lex.source.OPENING,
         ('개봉해 내용물을 꺼낼 수 있는 통조림이다', 'It is canned food that can be opened to retrieve its contents')),
        ('unpack_canned_food', 'package_opening', lex.source.CAN_OPENING,
         ('맞는 개봉 도구로 내용물을 꺼내는 통조림이다', 'It is canned food opened with an accepted opener to retrieve its contents')),
        ('unpack_jarred_food', 'package_opening', lex.source.OPENING,
         ('병을 열어 내용물을 꺼내는 식품이다', 'It is jarred food that can be opened to retrieve its contents')),
        ('unpack_produce', 'package_opening', lex.source.PRODUCE_SACK_OPENING,
         ('농산물을 꺼내는 자루이며 개봉해도 신선도가 회복되지는 않는다', 'It is a sack opened to retrieve produce; opening does not restore freshness')),
        ('unbundle_logs', 'log_binding', lex.source.LOG_BINDING,
         ('대응 제조법으로 풀 수 있는 통나무 묶음 재료다', 'It is material for unstacking the corresponding log bundle')),
        ('prepare_frog_meat', 'frog_preparation', lex.source.FROG_PREPARATION,
         ('허용된 칼로 손질해 고기를 꺼내는 개구리 재료다', 'It is a frog that can be prepared for meat with an accepted knife')),
        ('unpack_eggs', 'package_opening', lex.source.EGG_CARTON_OPENING,
         ('달걀을 꺼내는 포장이며 개봉해도 신선도가 회복되지는 않는다', 'It is a carton opened to retrieve eggs; opening does not restore freshness')),
        ('unpack_box_contents', 'package_opening', lex.source.JAR_BOX_OPENING,
         ('빈 병과 병뚜껑이 든 상자이며 개봉해 꺼낼 수 있다', 'It is a box that can be opened to retrieve empty jars and lids')),
        ('process_broken_fish_net', 'wire_recovery', lex.source.WIRE_RECOVERY,
         ('철사 회수 제조법에 쓰는 부서진 어망이다', 'It is a broken net used as material for wire recovery')),
        ('unpack_ammunition', 'package_opening', lex.source.OPENING,
         ('탄약이 든 상자이며 개봉해 탄약을 꺼낼 수 있다', 'It is boxed ammunition that can be unpacked')),
        ('pack_into_box', 'item_packaging', lex.source.BOX_PACKING,
         ('지정 수량을 모아 상자로 포장하는 재료다', 'It is material packed into a box in the specified quantity')),
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
