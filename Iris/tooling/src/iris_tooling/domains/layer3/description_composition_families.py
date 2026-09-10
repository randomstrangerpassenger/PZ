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
    *lex.source.VEHICLE_EXCHANGE_REQUIREMENTS.values(), *lex.source.RUNNING_EXCHANGE.values()}
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
FRAME_PREDICATES["water_overview"] = set().union(*(p for p, _ in WATER_USES.values())) | FRAME_PREDICATES["drinking"]
FRAME_REQUIRED["ignition"] = FRAME_REQUIRED["water_overview"] = set()

FUNCTION_FRAMES = {
    "apply_splint": ("SPLINTING", ("머리·몸통 외 골절에 부목을 대는 데 쓸 수 있다", "It can help splint fractures outside the head and torso")),
    "control_portable_light": ("LIGHT_CONTROL", ("손에 들거나 장착한 상태에서 휴대 조명을 조작할 수 있다", "It offers portable-light controls while held or attached")),
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
}
for _function, (_condition, _pair) in FUNCTION_FRAMES.items():
    FRAME_PREDICATES[_function] = {getattr(lex.source, _condition)}
    FRAME_REQUIRED[_function] = FRAME_PREDICATES[_function]
FRAME_PREDICATES["apply_bandage"] = {lex.source.BANDAGE_APPLICATION, lex.source.DIRTY_BANDAGING,
    "A body part is eligible for bandaging; the material remains in inventory and the patient does not move out of reach."}
FRAME_PREDICATES["fire_ammunition"] = {lex.source.FIRING, lex.source.GUN_FIRING_CYCLE}
FRAME_REQUIRED["fire_ammunition"] = FRAME_PREDICATES["fire_ammunition"]


def frames(plan, locale, links):
    units = [u for u in plan["units"] if not u["detail_reason"]]
    used, output = set(), []

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
                role_detail = frame == "role_overview" and predicate not in {lex.source.MELEE, lex.source.SPLINTING}
                detail = frame in {"wearing", "ignition"} or predicate == lex.source.NOTE_LIMITS or role_detail
                if frame == "water_overview":
                    detail = predicate not in FRAME_PREDICATES["drinking"]
                dispositions.append({"qualifier_ref": qref, "applies_to_fact_refs": u["fact_refs"],
                    "placement": "expanded" if detail else "compact_summary", "text": None if detail else text.removesuffix("."),
                    "reason": rule + "; operation lifetime, exact arithmetic and delivery remain in expanded"})
        output.append({"text": text, **linked, "expression": "conditional_frame",
                       "placement_reason": rule, "qualifier_dispositions": dispositions})
        used.update(r for u in members for r in u["fact_refs"])

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
        members = list(role_units)
        for name, condition, phrase in (
            ("melee_attack", lex.source.MELEE, ("차량 밖 근접 공격", "melee attacks outside a vehicle")),
            ("apply_splint", lex.source.SPLINTING, ("머리·몸통 외 골절의 부목 적용", "splinting fractures outside the head and torso")),
            ("build_wooden_barricade", lex.source.WOOD_BARRICADE, ("문·창문에 판자 바리케이드 추가", "adding plank barricades to doors or windows")),
            ("remove_barricade", lex.source.WOOD_UNBARRICADE, ("판자 바리케이드 철거", "removing plank barricades")),
        ):
            selected = [u for u in function(name) if
                        {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} == {condition}]
            if selected:
                members += selected
                purposes.append(phrase)
        fuel = [u for name, predicate in (("supply_campfire_fuel", lex.source.CAMP_FUEL_USE),
                 ("supply_hearth_fuel", lex.source.HEARTH_FUEL), ("supply_furnace_fuel", lex.source.FURNACE_FUEL))
                for u in function(name) if {plan["qualifiers"][q]["payload"]["predicate"] for q in u["qualifier_refs"]} == {predicate}]
        if purposes or fuel:
            members += fuel
            contexts = {f["payload"]["activity"] for u in role_units for f in u["facts"] if f["fact_kind"] == "use_context"}
            contexts.update(u["context"]["activity"] for u in role_units if u.get("context"))
            members += [u for u in units if len(u["facts"]) == 1 and u["facts"][0]["fact_kind"] == "use_context"
                        and u["facts"][0]["payload"]["activity"] in contexts]
            names = {loc: list(dict.fromkeys(lex.context(c, loc, True) for c in sorted(contexts))) for loc in ("ko", "en")}
            ko_text = "·".join(names["ko"]) + "에 쓰는 " + lex.ROLES[role_name][0] + "이며, "
            en_text = "It serves as " + lex.ROLES[role_name][1] + " for " + lex_join(names["en"])
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
        emit(ignition, ("·".join(p[0] for p in targets) + "의 점화에 쓰는 도구다",
                        "It is a tool for lighting " + lex_join([p[1] for p in targets])),
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
        tasks = [p for name, p in purposes if name not in {"store_water", "carry_water"}]
        carrying = any(name == "carry_water" for name, _ in purposes)
        ko_text = "물을 보관" + ("·운반" if carrying else "") + "할 수 있다"
        en_text = "It can store" + (" and carry" if carrying else "") + " water"
        if tasks:
            ko_text = ko_text.removesuffix("할 수 있다") + "하며, 담긴 물은 " + "·".join(p[0] for p in tasks) + "에 쓸 수 있다"
            en_text += " for " + lex_join([p[1] for p in tasks])
        if drinking and poison and related(drink, poison) and all(any(
                plan["qualifiers"][q]["payload"]["predicate"] == TAINT for q in u["qualifier_refs"]) for u in poison):
            members += poison
            ko_text += ". 오염된 물을 마시면 중독될 수 있다"
            en_text += ". Drinking tainted water can cause poisoning"
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
        emit(view + write,
             ("필기구 없이 메모를 읽을 수 있다. 쓰려면 필기구와 편집 권한이 있고 편집 잠금이 풀려 있어야 한다",
              "Notes can be read without a writing implement. Writing requires an implement, editing access and an unlocked note"),
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
