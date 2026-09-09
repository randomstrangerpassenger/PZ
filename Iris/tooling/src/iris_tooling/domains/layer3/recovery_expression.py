"""Bounded successor composition for source-confirmed recovery meanings.

Existing supported meanings use L3-05's pure composer. Closed new
function/state/effect/qualifier groups are composed here. No dictionaries are patched,
no adopted status is fabricated, and predecessor INPUTS never leave this module.
"""
from collections import defaultdict
from copy import deepcopy
import re

from . import acquisition_consumption as combined
from . import expression_results as expression
from . import expression_rules
from . import investigation as inv
from . import recovery
from . import recovery_sources
from . import description_projection as projection


# These are language views of the source-bound predicates, not new facts or
# validation authority. The complete predicate and provenance stay in facts.
# Compact does not inherit the expanded sentence: only an explicitly reviewed
# first-contact distinction is projected; ordinary execution stays in detail.
QUALIFIER_VIEWS = {}


def _views(rows, *, scope=False):
    for line in rows.strip().splitlines():
        names, ko, en = line.split('|')
        for name in names.split():
            predicate = getattr(recovery_sources, name)
            QUALIFIER_VIEWS[predicate] = {'expanded': (ko, en),
                                        'compact': (ko, en) if scope else None}


_views('''
CONSUMING|소지한 음식과 필요한 보조 물품이 있어야 하며, 포만 상태가 섭취를 허용해야 한다.|The food and any required companion item must be available, and satiety must permit consumption.
COOKING_ACTION COOKING_BASE|선택한 요리에서 허용하는 재료와 익힘·냉동 상태여야 한다.|The selected preparation must accept the ingredient and its cooked or frozen state.
FOOD_TRANSFER|음식을 옮긴 캐릭터의 이름이 조리자 정보에 남는다.|The character who transfers the food is recorded as its chef.
FIXING_ACTION|해당 수리법의 재료가 필요하며 수리 결과와 소모량은 수리법에 따라 달라진다.|The applicable repair supplies are required; the result and consumption depend on the repair method.
MELEE|차량 밖에서 공격 가능한 상태여야 한다.|Ordinary melee attacks require being outside a vehicle and able to attack.
STAGE_ACTION CARPENTRY_MATERIAL|선택한 건축 작업의 재료·도구·기술과 배치 조건을 충족해야 한다.|The selected construction requires its materials, tools, skills and suitable placement.
SHOVEL_SMITHING SMITHING_PARTS FORGE_PREPARATION|학습한 단조법에 맞는 재료·보존 도구·기술과 모루가 필요하다.|The learned forging recipe requires its materials, kept tools, skill and an anvil.
WELDED_PARTS|선택한 부품 용접법에 맞는 금속 재료·용접 도구·보호구와 기술이 필요하다.|The selected part-welding recipe requires its metal materials, welding equipment, protection and skill.
WELDING_CONSTRUCTION|선택한 용접 건축에 필요한 재료·장비·기술과 배치 조건을 갖춰야 한다.|The selected welded construction requires its materials, equipment, skills and suitable placement.
WASH_TARGET|접근 가능한 물 공급원에서 씻는다. 세제는 필수가 아니며 세척한 옷은 젖는다.|Wash at an accessible water source. Soap is optional, and washed clothing becomes wet.
NOTE_SAVE|쪽과 제목의 편집은 확인을 눌러야 저장된다.|Confirm the edits to save the pages and title.
NOTE_ACCESS NOTE_IMPLEMENT|메모 편집에는 필기구와 편집 권한이 필요하다.|Editing notes requires a writing implement and editing access.
NOTE_LIMITS|작성 가능한 쪽수와 입력 길이 안에서 기록한다.|Writing is limited by the available pages and entry length.
NOTE_LOCK|편집 잠금 변경은 즉시 적용되며 쪽 편집 취소로 되돌려지지 않는다.|Editing-lock changes apply immediately and survive cancellation of page edits.
READ_SELECTION|글을 읽을 수 있고 깨어 있으며 책의 기술 조건을 만족해야 한다. 이동하면 독서가 중단된다.|The reader must be literate, awake and meet the book's skill requirements. Movement interrupts reading.
READ_PROGRESS|독서 진행은 캐릭터별로 기록되며 기술 부족이나 문맹 상태에서는 초기화될 수 있다.|Reading progress is recorded per character and can reset for insufficient skill or illiteracy.
READ_MAXIMUM|완독해야 최대 배율에 도달하며, 지원 기술 수준에서 현재보다 높은 배율만 적용된다.|Full reading is needed for the maximum multiplier; it applies only within the supported skill levels and above the current multiplier.
WEARING WEAR_ACTION|해당 물품을 소지하고 지정된 신체 위치에 착용한다.|Keep the item in inventory and wear it at its designated body location.
CARRYING|용기와 내용물을 옮길 공간·접근·물품 허용 조건을 충족해야 한다.|Moving the container with its contents requires space, access and item admission.
BACK_CONTAINER|손에 든 물품을 내려 등 위치에 착용하며 기존 등 장비를 교체할 수 있다.|The bag is taken out of the hands and worn on the back, potentially replacing existing back equipment.
WEIGHT_EXERCISE|운동기구를 소지하고 차량 밖에서 운동 가능한 상태여야 한다. 이동하거나 지치면 운동이 끝난다.|Have the exercise equipment and be able to exercise outside a vehicle. Movement or exhaustion ends the exercise.
PLUMBING|파손되지 않은 파이프 렌치와 배관 가능한 실내 물체가 필요하다.|An unbroken pipe wrench and an indoor object that permits plumbing are required.
OPENING CAN_OPENING|해당 개봉법에서 요구하는 도구와 제작 조건을 갖춰야 한다.|The applicable opening method requires its tools and crafting conditions.
JAR_BOX_OPENING|개봉법은 빈 병과 병뚜껑을 꺼내는 용도다.|The opening recipe is for unpacking empty jars and lids.
BOX_PACKING SEED_PACKING|해당 포장법에 맞는 종류와 수량의 물품을 준비해야 한다.|Supply the item types and quantities required by the packing recipe.
BAKING MATERIAL_ASSEMBLY MATTRESS_PREPARATION|선택한 제조법의 재료·도구와 필요한 제작 지식을 갖춰야 한다.|The selected recipe requires its materials, tools and any required recipe knowledge.
FROG_PREPARATION|손질에 사용할 수 있는 칼을 갖춰야 한다.|A knife accepted for the preparation is required.
WIRE_RECOVERY|부서진 통발을 해당 회수 제조법에 제공한다.|Supply the broken net to the corresponding recovery recipe.
POULTICE_PREPARATION|대응하는 약초와 절구·공이가 필요하며 일반 제작 창에는 숨김 제조법이 나타나지 않는다.|The corresponding herb and mortar and pestle are required; hidden recipes are absent from the normal crafting window.
ROPE_MAKING|시트 로프 제작에 허용되는 직물이나 시트를 재료로 제공한다.|Supply fabric or a sheet accepted for sheet-rope crafting.
SPRAY_PREPARATION|해당 살포제 제조법을 익히고 빈 분무기와 지정 재료를 준비한다.|Learn the relevant spray recipe and supply an empty spray bottle and its specified ingredients.
CAMP_KIT_PREPARATION TENT_KIT_PREPARATION|해당 키트 제조법의 재료와 도구를 갖춰야 한다.|Supply the materials and tools required by the kit recipe.
MEDICAL_CONSOLIDATION|같은 유형의 덜 찬 물품에 남은 양을 옮기며 두 물품을 소지해야 한다.|Keep both items in inventory to transfer the remainder into a not-full item of the same type.
RENAME_ITEM FOOD_NAMING|허용된 길이의 비어 있지 않은 이름을 확인해야 한다.|Confirm a nonempty name within the permitted length.
ASH_CLEARING|불탄 바닥의 재와 파손되지 않은 해당 청소 도구가 필요하다.|Ash on a burnt floor and an unbroken tool accepted for clearing it are required.
MAP_READING|지도를 소지한 동안 열어 이동·확대·축소하며 볼 수 있다.|Keep the map in inventory to view it, pan and zoom.
MAP_ANNOTATION|필기구가 필요하며 기존 주석을 수정하거나 옮길 때는 지우개도 필요하다.|A writing implement is required; editing or moving existing annotations also requires an eraser.
MAP_ERASURE|지우개가 필요하며 주석을 수정하거나 옮길 때는 필기구도 필요하다.|An eraser is required; editing or moving annotations also requires a writing implement.
MAP_REVEAL|지도를 열면 표시된 범위가 월드맵의 알려진 지역에 추가된다.|Opening the map adds its displayed bounds to known areas of the world map.
ALARM_SETTING|시계를 소지하거나 놓인 시계에 접근해 알람 상태와 시각을 확인하여 저장한다.|Carry the clock or access its placed form, then confirm the alarm state and time.
ALARM_STOPPING|울리는 시계를 소지하거나 놓인 시계에 접근해야 한다.|Carry the ringing clock or reach its placed form.
CHOPPING|접근 가능한 나무와 주 손에 든 사용 가능한 도끼가 필요하다.|A reachable tree and a usable axe in the primary hand are required.
LOADING MAGAZINE_FILL|규격이 맞는 탄약과 남은 장전 공간이 필요하다. 달리면 중단되며 이미 넣은 탄은 남는다.|Matching ammunition and loading space are required. Running interrupts; rounds already loaded remain.
MAGAZINE_EMPTY|탄이 남은 탄창을 소지해야 한다. 달리면 중단되며 이미 꺼낸 탄은 남는다.|Carry a magazine with ammunition. Running interrupts; rounds already removed remain out.
MAGAZINE_LOADING|호환 총기를 주 손에 들고 탄창을 소지해야 하며 총기의 탄창 자리가 비어 있어야 한다.|Hold the compatible gun in the primary hand, carry the magazine and leave its magazine slot empty.
WEAPON_ATTACHMENT|호환 총기의 빈 장착 위치와 파손되지 않은 드라이버가 필요하다.|A compatible empty firearm attachment slot and an unbroken screwdriver are required.
WEAPON_PART_REMOVAL|부품이 장착된 총기와 파손되지 않은 드라이버를 소지해야 한다.|Carry the gun with its installed part and an unbroken screwdriver.
PICKUP PLACEMENT|해당 가구의 부품·도구·기술·공간·접근과 이용 권한 조건을 충족해야 한다.|Meet the furniture's part, tool, skill, space, access and permission requirements.
PAINTING PAINT_ACTIONS|도색 가능한 표면이나 벽 표식에 붓과 대응 페인트가 필요하다.|A brush and matching paint are needed for a paintable surface or wall sign.
CONTENTS_EMPTYING WATER_EMPTYING|버리는 동안 용기를 소지해야 하며 이미 버린 양은 취소해도 돌아오지 않는다.|Keep the container in inventory; cancelling does not restore contents already discarded.
GROUND_FILL|사용 가능한 흙 파기 도구와 내용물에 맞는 포대의 빈 공간이 필요하다.|A usable digging tool and space in a bag compatible with the ground material are required.
GROUND_POUR|소지한 포대의 내용물을 받을 수 있는 바닥에 접근해야 한다.|Reach a floor that can receive the carried bag's contents.
EXTINGUISH_CONDITIONS|사용량이 남은 소화 물품으로 불타는 대상에 접근해야 한다.|Reach the burning target with extinguishing supplies remaining.
TRAP_PLACEMENT|덫을 소지하고 장애물과 다른 덫이 없는 배치 가능한 바닥을 골라야 한다.|Carry the trap and choose suitable ground without obstacles or another trap.
REMOTE_LINK|대응 조종기와 장치를 함께 소지해 연결한다.|Carry the compatible controller and device together to link them.
REMOTE_RESET|선택한 물품의 연결만 해제하며 다른 물품의 연결은 그대로다.|Only the selected item's link is reset; other items retain theirs.
REMOTE_TRIGGER|연결된 장치가 조종 범위 안에 있어야 작동 대상이 될 수 있다.|A linked device must be within control range to be a trigger target.
FERTILIZING|살아 있고 씨를 심은 작물에 접근해 비료를 사용한다.|Reach a living, seeded crop to apply fertilizer.
CARPENTRY_MATERIAL|선택한 건축물의 재료·도구·기술과 배치 조건을 충족해야 한다.|Meet the selected construction's material, tool, skill and placement requirements.
SOWING|아직 씨를 심지 않은 고랑과 해당 작물의 낱알 씨앗이 필요하다.|An unseeded furrow and the crop's loose seeds are required.
UMBRELLA_CHANGE|대응하는 형태 변경법을 사용하며 이전 우산의 상태가 이어진다.|Use the matching form-change recipe; the umbrella's condition carries over.
DISINFECTION|붕대가 감기지 않은 치료 가능한 부위를 선택하고 소독제를 소지해야 한다.|Select an eligible unbandaged body part and keep the disinfectant in inventory.
DISINFECTION_USE|소독제를 사용할 때 남은 양의 일부를 소모한다.|Disinfection consumes some of the remaining disinfectant.
SPLINTING|머리·몸통 이외의 골절 부위에 완성 부목이나 찢어진 천과 적합한 지지대를 사용한다.|Use a finished splint or ripped sheets with a suitable support on a fracture outside the head and torso.
SPLINT_REMOVAL|부목이 적용된 부위에서 제거하며 남아 있는 골절을 치료하는 동작은 아니다.|Remove a splint from a splinted part; removal does not heal a remaining fracture.
BANDAGE_REMOVAL|붕대가 적용된 부위를 선택해 제거하며 반환 형태는 붕대 상태에 따라 달라진다.|Select a bandaged part to remove the bandage; its returned form depends on its state.
BANDAGE_APPLICATION DIRTY_BANDAGING|붕대를 사용할 수 있는 부위에 소지한 재료를 대며 적용한 재료를 소모한다.|Apply the carried material to a part that permits bandaging; application consumes it.
BANDAGE_LIFE|붕대의 유효 시간은 의료 기술과 재료의 강도에 따라 달라지며 더러운 붕대는 유효 시간이 없다.|Bandage life varies with medical skill and material strength; dirty bandages have no remaining bandage life.
BURN_CLEANING|세척이 필요한 화상에 충분한 강도의 붕대 재료를 사용하며 통증이 생길 수 있다.|Use sufficiently strong bandaging material on a burn that needs washing; the treatment can cause pain.
BANDAGE_WASHING BANDAGE_RECIPE_WASHING|해당 더러운 붕대나 천과 세척에 허용되는 물이 필요하다.|The specified dirty bandage or cloth and water permitted for washing are required.
PILL_TAKING|선택한 알약을 소지한 채 복용하며 달리면 중단된다.|Keep the selected pills in inventory while taking them; running interrupts.
BANDAGE_MATERIALS|해당 준비법의 천·솜·소독 재료와 수량·온도 조건을 갖춰야 한다.|The preparation requires its fabric, cotton and disinfecting supplies, quantities and temperature conditions.
BODY_DRYING|마른 수건의 사용량이 남아 있어야 하며 몸을 닦는 동안 수건을 소모한다.|A dry towel must have uses remaining; drying consumes towel uses.
BLOOD_CLEANING|혈흔이 있는 바닥에 표백제와 해당 청소 도구가 필요하다. 도구는 소모하지 않는다.|A bloodied floor requires bleach and an accepted cleaning tool. The tool is not consumed.
BODY_WASHING EQUIPMENT_WASHING WASHING_OUTCOME|물을 사용해 피·때를 씻는다. 세제는 선택 사항이며 물이 부족하면 세척이 일부만 진행될 수 있다.|Water washes away blood and dirt. Soap is optional; limited water can leave washing incomplete.
''')

_views('''
FOOD_TRAP_BAIT|추가 재료가 없는 익히지 않은 음식만 미끼로 넣으며 동물에 따라 맞는 미끼가 다르다.|Only uncooked food without added ingredients can be supplied as bait; accepted bait depends on the animal.
NOTE_EDIT|필기구가 필요하며 메모의 편집 잠금이 풀려 있어야 한다.|A writing implement is required, and the note must be unlocked for editing.
OPENED_FOOD|먼저 개봉해야 하며 꺼낸 음식이 해당 요리에 허용되어야 한다.|Open it first; the extracted food must be accepted by the preparation.
EGG_CARTON_OPENING PRODUCE_SACK_OPENING|개봉해도 내용물의 신선도가 새것으로 돌아가지는 않는다.|Opening does not restore the contents to fresh condition.
JAR_PREPARATION|병에 담는 것만으로 보존 기간이 늘어나지는 않는다.|Jarring alone does not extend shelf life.
FERTILIZER_GROWTH|과다 시비 전의 살아 있는 작물에 적용되며 이미 도달한 성장 시점을 더 앞당기지는 않는다.|This applies to a living crop before over-fertilization and does not advance an already reached growth time.
FERTILIZER_ROT|이미 네 번 이상 비료를 받은 작물에 더 주면 부패한다.|A crop that has already received fertilizer at least four times rots if fertilized again.
BATTERY_INSERTION|충전량이 없는 대응 기기에 넣으며 건전지의 남은 충전량만 전달한다.|Insert it into a compatible empty device; only the battery's remaining charge is transferred.
BATTERY_INSERT|배터리형 기기의 빈 배터리 칸에 전력이 남은 배터리를 넣는다.|Insert a battery with charge remaining into an empty battery slot of a battery-powered device.
PICKUP_LOSS|떼어내다가 부서질 수 있다.|Removal can break the object.
SMOKING|성냥이나 라이터가 필요하다.|A match or lighter is required.
SMOKER_EFFECT|흡연가 특성이 있을 때 적용된다.|This applies with the Smoker trait.
NONSMOKER_EFFECT|흡연가 특성이 없을 때 적용된다.|This applies without the Smoker trait.
POISONOUS_WILD_FOOD|독성이 있는 야생 식품을 먹었을 때 적용된다.|This applies when poisonous wild food is eaten.
FIRING|탄약이 준비되어 있고 총기가 걸리지 않아야 한다.|Ammunition must be ready and the firearm must not be jammed.
READ_MOOD|읽는 동안 시작 시점보다 높아지는 것을 막는 효과다.|This prevents the value from rising above its level when reading began.
BANDAGE_INFECTION|적용한 재료 자체가 감염되어 있을 때만 해당한다.|This applies only when the applied material itself is infected.
BANDAGE_PANIC|혈액공포증이 있는 치료자가 출혈 부위의 붕대를 적용하거나 제거할 때 해당한다.|This applies to a Hemophobic caregiver bandaging or unbandaging a bleeding part.
BANDAGE_OR_BURN_PANIC|혈액공포증이 있는 치료자에게 적용되며 붕대 치료에서는 출혈이 있어야 한다.|This applies to a Hemophobic caregiver; bandage treatment also requires bleeding.
SLOT_USE|착용해야 생기는 장착 위치이며 맞는 유형의 물품만 부착할 수 있다.|The attachment slot is available while worn and accepts only matching item types.
ROD_REPAIR_INPUT|낚싯줄이 없는 형태로, 낚시에 쓰려면 해당 수리법이 필요하다.|This form lacks a fishing line and needs its corresponding repair before rod fishing.
FISHING_LURE_LOSS|미끼는 사용 중 소모되거나 낚싯줄 파손으로 잃을 수 있다.|Bait can be consumed during fishing or lost when the line breaks.
SCRAP_RECOVERY|분해로 전자 스크랩을 회수할 수 있지만 추가 부품은 보장되지 않는다.|Dismantling can recover electronic scrap, but additional parts are not guaranteed.
''', scope=True)


_views('''
VEHICLE_SEATING|장착된 빈 좌석과 접근 가능한 문·좌석 경로가 필요하다.|An installed empty seat and an accessible door or seat route are required.
VEHICLE_STORAGE|장착된 수납 부품의 접근·용량·물품 허용 조건을 충족해야 한다.|Meet the installed storage part's access, capacity and item-admission conditions.
VEHICLE_FUEL|장착된 탱크에 접근하고 주유·회수에 맞는 용기와 남은 연료 또는 빈 공간을 갖춰야 한다.|Reach the installed tank with a suitable container and remaining fuel or space for filling or siphoning.
VEHICLE_FUEL_ENGINE|장착된 탱크의 연료는 작동 중인 엔진에서 소비되며 탱크 상태가 나쁘면 더 잃을 수 있다.|The running engine consumes fuel from the installed tank; a damaged tank can lose additional fuel.
LOG_BINDING|통나무를 로프로 묶거나 대응 묶음을 풀 때 사용한다.|Use it when binding logs with rope or unstacking the corresponding bundle.
BOWL_PORTIONING|해당 냄비 음식과 그릇을 준비해 음식의 양과 영양을 나눈다.|Supply the matching pot of food and bowls to divide its portions and nutrition.
SEED_EXTRACTION|봉지의 씨앗을 먼저 꺼내야 한다.|Remove the seeds from their packet first.
BATTERY_REMOVE|배터리형 기기에 배터리가 들어 있어야 한다.|The battery-powered device must contain a battery.
MIC_CONTROL|전원이 켜진 양방향 기기의 마이크 음소거를 조작한다.|Control microphone muting on a powered two-way device.
DEVICE_PANEL RADIO_WINDOW_LIFETIME|휴대 기기는 손에 든 채 조작하며 설치·차량 기기는 접근 가능한 위치여야 한다.|Hold a portable device to use its controls; placed and vehicle devices must be accessible.
RADIO_TUNING TV_TUNING|전원이 켜진 기기에서 선택 가능한 채널을 맞춘다.|Tune an available channel on a powered device.
DEVICE_VOLUME|전원이 켜진 기기의 음량과 음소거 상태를 바꾼다.|Change the volume and mute state of a powered device.
MEDIA_LABEL|기록이 배정된 매체를 소지하면 제공되는 내용 안내를 볼 수 있다.|Carry media with assigned recorded content to view its available description.
MEDIA_INSERT RADIO_MEDIA_CONTROL|기기에 맞는 기록 매체와 빈 삽입 위치가 필요하며 재생에는 기기가 켜져 있어야 한다.|Insertion requires matching recorded media and an empty slot; playback requires the device to be on.
HEADPHONE_CONNECTION RADIO_HEADPHONE_CONTROL|휴대 가능한 TV 이외 기기의 빈 헤드폰 위치에 연결한다.|Connect to an empty headphone slot on a portable device other than a television.
RADIO_PRESETS|지원하는 무전기의 저장 채널을 편집하며 현재 채널을 바꾸려면 별도로 맞춰야 한다.|Edit presets on a supported radio; tune separately to change its current channel.
RADIO_WORLD_FORM|배치에 맞는 공간과 접근 조건을 갖춰야 하며 기기 정보는 설치된 형태에 이어진다.|Meet the placement space and access conditions; device data carries over to the placed form.
CLOTHING_FORM|지원하는 착용 형태를 선택하면 물품을 그 형태로 바꾸어 착용한다.|Selecting a supported clothing form changes the item into that form and wears it.
BATTER_TEST|해당 반죽에 쓰는 알은 익지 않아야 하며 신선도에 따른 남은 양 조건을 충족해야 한다.|Eggs used for the specified batter must be uncooked and meet the remaining-amount requirement for their freshness.
DEVICE_DELAY|타이머를 지원하는 장치에서 양수의 지연 시간을 확인하여 저장한다.|Confirm a positive delay on a device that supports a timer.
DEVICE_PLACEMENT|소지한 장치를 현재 위치에 설치하며 설치 후에는 손과 소지품에서 제거된다.|Place the carried device at the current location; it then leaves the hands and inventory.
DEVICE_RETRIEVAL|회수할 물품이 남은 설치 장치에 접근해야 한다.|Reach a placed device that still has an item available for retrieval.
PANEL_INSTALL PANEL_REMOVE|호환 차량의 해당 부품 위치에 접근해 필요한 도구·지식과 선행 작업을 갖춰야 한다. 실패하면 손상될 수 있다.|Reach the compatible vehicle-part position with its tools, knowledge and prerequisite work. Failure can cause damage.
PANEL_DOOR|멈춘 차량의 해당 문이나 덮개에서 조작하며 잠겼으면 해제가 필요하다.|Operate the corresponding door or cover on a stopped vehicle; unlock it if needed.
PANEL_LOCK|장착된 문의 잠금 장치가 작동해야 하며 접근 위치에 따라 열쇠 요구가 다르다.|The installed door lock must work; key requirements depend on the access position.
PANEL_WINDOW|파괴되지 않은 개폐식 창문에만 해당한다.|This applies only to an unbroken openable window.
TIRE_INFLATION|장착된 타이어와 펌프가 필요하며 이미 넣은 공기는 취소해도 남는다.|An installed tire and pump are required; cancelling leaves air already added.
TIRE_DEFLATION|장착된 타이어에 공기가 남아 있어야 하며 펌프 없이 뺄 수 있다.|The installed tire must contain air; no pump is required to release it.
ESCAPE_ROPE_INSTALL|지상층보다 높은 부착 지점과 못·충분한 한 종류의 로프가 필요하다.|An attachment point above ground level, a nail and enough rope of one type are required.
ESCAPE_ROPE_REMOVE|설치된 로프의 부착 지점에 접근해 제거한다.|Reach the attachment point of the installed rope to remove it.
ESCAPE_ROPE_CLIMB|설치된 로프에 접근하고 힘과 올라가기 조건을 충족해야 한다.|Reach the installed rope and meet its strength and climbing requirements.
FLOOR_GLASS_PICKUP|바닥 유리 옆으로 접근해 줍는다.|Reach a square beside the floor glass to pick it up.
FABRIC_ACTION|재료에 맞는 찢기 방법을 사용하며 데님·가죽에는 가위가 필요하다. 회수량은 직물과 재봉 기술에 따라 달라진다.|Use the ripping method for the fabric; denim and leather need scissors. Yield varies with fabric and tailoring skill.
GARMENT_PATCHING|패치가 없는 해당 의류 부위에 천 조각·실·바늘로 구멍을 덧대거나 패딩을 더한다.|Use fabric pieces, thread and a needle to patch a hole or add padding to an eligible unpatched garment part.
GARMENT_PATCH_REMOVAL|패치가 있는 의류와 바늘이 필요하며 천 회수 여부는 재봉 기술에 따라 달라진다.|A patched garment and a needle are required; cloth recovery depends on tailoring skill.
WATER_TRANSFER WORLD_WATER_TRANSFER|물을 받을 여유가 있는 대응 용기에 붓는다. 중간에 취소해도 옮긴 물은 남는다.|Pour into a compatible receiver with space. Water already transferred remains if cancelled.
CROP_WATERING|물을 더 받을 수 있는 파종된 작물에 소지한 물을 사용한다.|Use carried water on a seeded crop that can receive more water.
VEHICLE_WASHING|혈흔이 있는 차량 부위에 접근해 소지한 물로 씻는다.|Reach a bloodied vehicle part and wash it with carried water.
WATER_DRINKING|갈증이 있을 때 소지한 물을 마시며 중단하기 전 마신 양은 되돌아오지 않는다.|Drink carried water while thirsty; water consumed before interruption is not restored.
SPRAY_TREATMENT|해당 병충해가 있는 작물에 맞는 살포제를 사용한다.|Apply the matching spray to a crop with the corresponding disease or pest.
VEHICLE_KEY_USE|열쇠가 차량과 맞아야 하며 운전석에서 시동과 점화장치를 조작한다.|The key must match the vehicle; operate starting and ignition controls from the driver's seat.
KEY_ALARM|맞는 열쇠가 있으면 해당 차량의 첫 문 개방 경보를 피하지만 이미 울리는 경보를 끄지는 않는다.|A matching key avoids that vehicle's first door-opening alarm but does not stop an alarm already ringing.
KEY_MECHANICS|열쇠를 요구하는 해당 정비 작업에서 차량과 맞는 열쇠를 사용한다.|Use the matching vehicle key for a mechanics operation that requires one.
DOOR_KEY_USE|맞는 열쇠로 닫힌 문의 잠금을 조작하며 열쇠는 소모하지 않는다.|Operate the closed door's lock with a matching key; the key is not consumed.
PADLOCK_USE|기존 자물쇠나 번호가 없는 지원 구조물에 설치한다.|Install it on a supported structure without an existing padlock or code.
CODE_LOCK_USE|잠기지 않은 지원 구조물에 번호를 설정해 설치한다.|Set a code to install it on an unlocked supported structure.
CODE_UNLOCK|설치된 번호 자물쇠의 맞는 번호를 입력해야 한다.|Enter the matching code of the installed combination lock.
CAMP_PLACEMENT TENT_PLACEMENT|키트를 준비해 장애물이 없는 적합한 설치 위치를 골라야 한다.|Prepare the kit and choose a suitable unobstructed placement position.
DYE_APPLICATION|염색할 머리카락이나 수염이 있어야 하며 염색약을 소모한다.|Hair or a beard must exist to dye; applying dye consumes it.
HAIR_GROOMING|현재 머리 길이에서 가능한 스타일과 그 스타일에 맞는 가위·면도기 또는 헤어젤이 필요하다.|Choose a style available at the current hair length with its required scissors, razor or hair gel.
BEARD_GROOMING|수염이 있어야 하며 파손되지 않은 면도기나 가위가 필요하다.|A beard and an unbroken razor or scissors are required.
MAKEUP_USE MAKEUP_LIFECYCLE|대응하는 분장을 골라 적용한다. 메뉴에는 거울·차량 탑승 또는 파운데이션 조건 중 하나가 필요하다.|Choose and apply supported makeup. The menu requires a mirror, being in a vehicle, or the foundation condition.
STITCHING|유리가 없고 붕대를 감지 않은 깊은 상처에 봉합침이나 바늘과 실을 사용한다.|Use a suture needle or a needle and thread on a deep, unbandaged wound without glass.
GLASS_REMOVAL|붕대가 없는 상처의 유리를 제거하며 맨손으로 제거하면 통증이 더 생긴다.|Remove glass from an unbandaged wound; bare-hand removal adds pain.
BULLET_REMOVAL|붕대가 없는 상처에 박힌 탄환을 적합한 도구로 제거하며 통증이 생긴다.|Use a suitable tool to remove a bullet from an unbandaged wound; this causes pain.
POULTICE_USE|다른 약초 찜질제가 없는 미붕대 상처에 적용하며 찜질제를 소모한다.|Apply to an unbandaged injury without another herbal poultice; the poultice is consumed.
''')

_views('''
CAMP_FUEL_USE|즐겨찾기한 물품은 제외하며 옷은 벗고 용기는 비워야 한다. 연료로 사용하면 소모한다.|Favorites are excluded; clothing must be unequipped and containers empty. Fuel use consumes the item.
CAMP_TINDER_USE|발화 도구가 필요하며 불쏘시개는 소모된다. 즐겨찾기한 물품·착용 중인 옷·내용물이 있는 용기는 제외된다.|A fire-starting item is required and the tinder is consumed. Favorites, worn clothing and nonempty containers are excluded.
CAMPFIRE_PLACEMENT|설치한 모닥불은 불이 꺼져 있으며 연료와 점화가 별도로 필요하다.|A newly placed campfire is unlit and needs fuel and lighting separately.
TENT_REST|먼저 설치해야 하며 서버가 수면을 허용하고 캐릭터의 휴식·수면 조건을 충족해야 한다.|Place the tent first; server sleep permission and the character's rest or sleep conditions must hold.
TRAP_CATCH|맞는 신선한 미끼와 동물별 시간·지역 조건이 필요하며 포획은 확률에 따른다.|Suitable fresh bait and the animal's time and area conditions are required; capture is probabilistic.
TRAP_RABBIT_SQUIRREL|토끼·다람쥐에 대응한다.|It supports rabbits and squirrels.
TRAP_BIRD|새에 대응한다.|It supports birds.
TRAP_RODENTS|생쥐·쥐에 대응한다.|It supports mice and rats.
ROD_FISHING FISHING_LURES|낚싯대와 맞는 미끼를 함께 사용하며 물고기·장소·기술에 따라 결과가 달라진다.|Use a rod with matching bait; results vary with fish, location and skill.
FISHING_MATCHES|물고기에 따라 받는 미끼가 다르며 인공 루어로 모든 물고기를 낚을 수는 없다.|Accepted bait differs by fish; artificial lures do not support every fish.
SPEAR_FISHING|미끼 없이 물가에서 사용하며 포획은 보장되지 않고 창이 마모될 수 있다.|Use at the water without bait; catches are not guaranteed and the spear can wear.
SPEAR_FISHING_WEAR SPEAR_TOOL_WEAR|이 작업에 사용하면 도구의 상태가 감소할 수 있다.|This use can reduce the tool's condition.
SPEAR_STONE_LOSS|창 제작에 사용한 깎인 돌은 잃을 수 있다.|A chipped stone used in spear crafting can be lost.
RADIO_DISMANTLING ELECTRONIC_SALVAGE|맞는 드라이버가 필요하며 즐겨찾기한 분해 대상은 제외된다. 회수 부품은 기기와 기술에 따라 달라진다.|A matching screwdriver is required and favorite targets are excluded. Recovered parts vary with device and skill.
RADIO_CRAFTING|해당 제작 지식과 전기 기술이 필요하며 완성품에 전원이 들어 있는 것은 아니다.|The recipe knowledge and electrical skill are required; a crafted device is not supplied with power.
ACTIVATION DEVICE_POWER|손에 들거나 장착한 지원 기기에 전력을 공급할 수 있어야 한다.|A supported held or equipped device must have an available power supply.
WATER_STORAGE|오염된 수원의 물을 담으면 용기의 물도 오염될 수 있으며 채우기로 정수되지 않는다.|Filling from a tainted source can taint the stored water; filling does not purify it.
FLOOR_GLASS_INJURY|손에 착용한 보호 물품 없이 유리를 주우면 손이 긁히거나 유리가 박힐 수 있다.|Picking up glass without an item worn on the hands can scratch a hand or leave glass embedded.
RUNNING_WEAR BRAKE_WEAR|장착된 부품은 주행이나 제동 중 마모될 수 있다.|The installed part can wear during driving or braking.
TIRE_WEAR|주행 중 공기와 상태가 줄 수 있으며 공기나 상태가 나쁘면 타이어를 잃을 수 있다.|Driving can reduce tire air and condition; poor air or condition can cause tire loss.
PADLOCK_KEY_USE|맞는 열쇠로 자물쇠를 제거하며 그 열쇠 하나를 소모한다.|Remove the padlock with a matching key; one such key is consumed.
CANNED_COOKED|가열 때 보존 기준을 바꾸지만 이미 지난 신선도 경과를 없애지는 않는다.|Cooking changes preservation thresholds without erasing freshness age already elapsed.
FISH_CREATED|생선의 크기에 따라 무게와 영양이 달라진다.|Fish weight and nutrition vary with size.
RADIO_CODE_EFFECTS|실제로 전달된 기록·방송 내용과 캐릭터의 시청 조건에 따라 적용된다.|This depends on content actually delivered and the character's viewing or listening conditions.
DISINFECTION_ADMIN_PAIN|이 통증 변화는 관리자 권한의 치료 동작에만 해당한다.|This pain change applies only to treatment performed with administrative access.
SUTURE_ASSISTANCE|봉합·실밥 제거 시간을 줄이는 보조 도구이며 바늘과 실을 대신하지 않는다.|It assists stitching and stitch removal by reducing their base time; it does not replace the needle and thread.
MEDICAL_PANIC|혈액공포증이 있는 시술자에게 적용되며 찜질제는 출혈 부위에서만 해당한다.|This applies to a Hemophobic caregiver; poultice treatment also requires bleeding.
''', scope=True)

for _n, _predicate in recovery_sources.SOW_COUNTS.items():
    QUALIFIER_VIEWS[_predicate] = {'expanded': recovery_sources.QUALIFIERS[_predicate], 'compact': None}
for _kind, _predicate in recovery_sources.VEHICLE_EXCHANGE_REQUIREMENTS.items():
    _pair = (('기초 차량 정비 지식과 드라이버가 필요하며 탈거할 때 수납 공간을 비워야 한다.',
              'Basic Mechanics knowledge and a screwdriver are needed; empty the storage before removal.') if _kind == 'seat' else
             ('기초 차량 정비 지식·드라이버·렌치가 필요하며 탈거할 때 탱크를 비워야 한다.',
              'Basic Mechanics knowledge, a screwdriver and a wrench are needed; empty the tank before removal.'))
    QUALIFIER_VIEWS[_predicate] = {'expanded': _pair, 'compact': None}
for _kind, _predicate in recovery_sources.RUNNING_EXCHANGE.items():
    _pair = {'tire': ('잭과 휠 렌치가 필요하며 장착 위치에 브레이크와 서스펜션이 있어야 한다.',
                      'A jack and lug wrench are required; the matching brake and suspension must be installed.'),
             'brake': ('기초 차량 정비 지식·잭·렌치가 필요하며 탈거 전에 대응 타이어를 제거한다.',
                       'Basic Mechanics knowledge, a jack and a wrench are needed; remove the matching tire before removal.'),
             'suspension': ('기초 차량 정비 지식·잭·렌치가 필요하며 탈거 전에 대응 타이어를 제거한다.',
                            'Basic Mechanics knowledge, a jack and a wrench are needed; remove the matching tire before removal.'),
             'muffler': ('기초 차량 정비 지식과 렌치를 갖추고 적재함 작업 위치에 접근한다.',
                         'Have Basic Mechanics knowledge and a wrench, and reach the trunk work area.')}[_kind]
    QUALIFIER_VIEWS[_predicate] = {'expanded': _pair, 'compact': None}
for _item, _predicate in recovery_sources.STRAP_SPEED.items():
    _shell = _item == 'Base.AmmoStrap_Shells'
    _pair = (('착용 중이며 주 손 총기가 산탄을 사용할 때 적용된다.',
              'This applies while worn when the primary-hand weapon uses shotgun shells.') if _shell else
             ('착용 중이며 주 손 총기가 산탄 이외의 탄종을 사용할 때 적용된다.',
              'This applies while worn when the primary-hand weapon uses ammunition other than shotgun shells.'))
    QUALIFIER_VIEWS[_predicate] = {'expanded': _pair, 'compact': _pair}
for _activity, _predicate in recovery_sources.SPEAR_CONDITIONS.items():
    _pair = {'spear_crafting': ('판자나 나뭇가지와 절삭 도구가 필요하며 창 상태는 목공 기술에 따라 달라진다.',
                               'A plank or branch and a cutting tool are needed; spear condition varies with carpentry skill.'),
             'spear_upgrade': ('제작한 창과 해당 부착물·덕트 테이프가 필요하며 재료 상태가 결과에 영향을 준다.',
                               'A crafted spear, matching attachment and duct tape are needed; input condition affects the result.'),
             'spear_reclaim': ('부서진 창도 해당 회수법에 사용할 수 있다.',
                               'A broken spear can also be used in the matching reclaim recipe.')}[_activity]
    QUALIFIER_VIEWS[_predicate] = {'expanded': _pair, 'compact': _pair if _activity == 'spear_reclaim' else None}

# Older and more complete source predicates can describe the same player-facing
# condition. They retain distinct fact identities even when their prose agrees.
for _old, _new in {
    'For a compatible damaged item and available repair materials; repair eligibility and outcome depend on the fixing rules.': 'FIXING_ACTION',
    'Only where the recipe accepts the ingredient, with its cooked/frozen and other eligibility requirements satisfied.': 'COOKING_ACTION',
    'For the active wooden-cross branch, the hammer is not broken and world placement/material requirements hold.': 'STAGE_ACTION',
    'Only for a compatible previous construction stage, with required skills, tools and materials available; material consumption excludes construction cheat mode.': 'STAGE_ACTION',
    'For the active wooden-cross or log-wall branch requiring this material; log-wall binding chooses sufficient sheets (clean/dirty), otherwise twine, otherwise rope. World placement and material availability must hold; cheat mode does not consume material.': 'STAGE_ACTION',
}.items():
    QUALIFIER_VIEWS[_old] = QUALIFIER_VIEWS[getattr(recovery_sources, _new)]

QUALIFIER_VIEWS[recovery_sources.DEVICE_POWER] = {
    'expanded': ('접근 가능한 기기에 배터리나 현재 위치의 전원이 있어야 한다.',
                 'An accessible device needs battery power or power available at its location.'), 'compact': None}
QUALIFIER_VIEWS[recovery_sources.CAMP_FUEL_USE]['compact'] = (
    '연료로 사용하면 소모한다.', 'Using it as fuel consumes it.')
QUALIFIER_VIEWS[recovery_sources.CAMP_TINDER_USE]['compact'] = (
    '발화 도구가 필요하며 불쏘시개는 소모된다.', 'A fire-starting item is needed and the tinder is consumed.')

EFFECT_VIEWS = {
    ('food_chef_attribution', 'set_transferring_character'): ('소지품 옮기기 동작으로 음식 이동을 완료하면 옮긴 캐릭터가 조리자로 기록된다.',
                                                           'Completing the inventory transfer action for food records the transferring character as its chef.'),
    ('food_preservation_age', 'rebase_on_cooking'): ('가열하면 식품의 보존 기준과 경과 나이를 조정한다.',
                                                   'Cooking adjusts the food preservation thresholds and relative age.'),
    ('fish_size_nutrition', 'initialize_from_registered_size'): ('생선의 크기에 따라 무게·영양·허기 값을 정한다.',
                                                               'Fish size determines its weight, nutrition and hunger values.'),
    ('delivered_media_code_outcome', 'apply_configured_code'): ('전달된 방송·기록 내용에 따라 능력치·경험치·제작법 학습 효과가 적용될 수 있다.',
                                                              'Delivered broadcast or recorded content can affect stats, XP or recipe knowledge.'),
    ('splint_factor', 'set_doctor_half'): ('의료 기술에 따라 부목의 치료 계수가 정해진다.',
                                         'Medical skill determines the splint treatment factor.'),
    ('poultice_factor', 'set_doctor_random'): ('의료 기술에 따라 약초 찜질제의 치료 계수가 달라진다.',
                                            'The herbal-poultice treatment factor varies with medical skill.'),
}
FUNCTION_VIEWS = {
    'supply_vehicle_engine_fuel': ('장착된 탱크에서 작동 중인 엔진에 연료를 공급한다.',
                                  'The installed tank supplies fuel to the running engine.'),
    'send_remote_trigger': ('연결된 장치를 범위 안에서 원격으로 작동시키는 데 쓸 수 있다.',
                            'It can be used to trigger a linked device within range.'),
    'request_matching_vehicle_start': ('맞는 차량의 시동과 점화장치를 조작하는 데 쓸 수 있다.',
                                       'It can operate starting and ignition controls in a matching vehicle.'),
    'avoid_first_door_alarm_trigger': ('맞는 차량의 첫 문 개방 때 경보를 피할 수 있다.',
                                       'It can avoid a matching vehicle alarm on first door opening.'),
}


_views('''
FOOD_ASSEMBLY|선택한 음식 준비법에서 허용하는 재료와 용기·도구가 필요하다. 학습을 요구하는 준비법은 먼저 익혀야 하며 운전 중에는 제작할 수 없다.|Use the ingredients, vessels and tools accepted by the selected preparation; learn it where required. Crafting is unavailable while driving.
FOOD_SLICING|선택한 손질법에 맞는 음식과 보존 도구가 필요하며 운전 중에는 할 수 없다.|Use the food and kept tool accepted by the selected preparation; it is unavailable while driving.
COOKED_SLICING|선택한 파이·케이크 손질법의 도구가 필요하며 음식은 익었거나 탄 상태여야 한다. 운전 중에는 할 수 없다.|Use the specified tool on cooked or burnt pie or cake; preparation is unavailable while driving.
DOUGH_SLICING|빵 반죽을 자를 때는 익힌 반죽과 지정된 칼이 필요하며 운전 중에는 할 수 없다.|Use the specified knife on cooked bread dough; preparation is unavailable while driving.
PIZZA_SLICING|피자 손질 도구가 필요하다. 완성 피자 형식 이외에는 익었거나 탄 피자를 선택해야 하며 운전 중에는 할 수 없다.|Use the specified pizza-cutting tool. Forms other than ready-made pizza must be cooked or burnt; preparation is unavailable while driving.
FISH_PREPARATION|생선 손질 도구가 필요하고 생선의 실제 무게가 0.6보다 커야 하며 운전 중에는 할 수 없다.|Use a permitted fish-cutting tool on fish weighing more than 0.6; preparation is unavailable while driving.
ANIMAL_PREPARATION|선택한 작은 동물 손질법에서 허용하는 사체와 칼이 필요하며 운전 중에는 할 수 없다.|Use the carcass and knife accepted by the selected small-animal preparation; it is unavailable while driving.
SANDWICH_PREPARATION|치즈 샌드위치를 만들 때는 허용하는 빵과 치즈가 필요하며 빵 조각은 신선도에 따른 남은 양 조건을 만족해야 한다. 운전 중에는 할 수 없다.|For cheese sandwiches, use accepted bread and cheese; bread slices must retain the amount required for their freshness. Preparation is unavailable while driving.
GRAIN_VESSEL_PREPARATION|허용하는 쌀 또는 파스타와 물이 든 냄비·소스팬이 필요하며 운전 중에는 할 수 없다.|Supply accepted rice or pasta and a water-filled pot or saucepan; preparation is unavailable while driving.
OATMEAL_PREPARATION|그릇과 귀리·물이 필요하며 운전 중에는 준비할 수 없다.|Supply a bowl, oats and water; preparation is unavailable while driving.
WOOD_SHAPING|선택한 목재 가공법에서 허용하는 목재와 보존 도구가 필요하며 운전 중에는 할 수 없다.|Use the wood and kept tool accepted by the selected shaping operation; it is unavailable while driving.
''', scope=True)


_views('''
GUN_ROUND_LOADING|총을 주 손에 들고 호환 탄약과 남은 장전 공간이 있어야 한다. 자동 재장전은 걸린 총에 탄을 넣지 않으며 달리면 중단된다.|Hold the firearm in the primary hand with matching ammunition and free capacity. Automatic reload refuses a jammed gun; running interrupts.
GUN_ROUND_UNLOADING|탄창을 쓰지 않는 총에 남은 탄약이 있을 때 탄약을 꺼낼 수 있다. 달리면 중단되며 약실의 탄은 별도로 다룬다.|Unload remaining rounds from a firearm without a detachable magazine. Running interrupts; its chamber is handled separately.
GUN_MAGAZINE_EJECTION|총을 주 손에 들고 탄창이 끼워져 있어야 한다. 달리면 중단되며 약실의 탄은 남는다.|Hold the firearm in the primary hand with a magazine installed. Running interrupts; a chambered round remains.
GUN_RACKING|총의 탄 걸림·약실·잔탄 상태가 조작을 허용해야 한다. 걸림을 풀거나 약실에 탄을 넣고 뺄 수 있으며 달리면 중단된다.|The current jam, chamber and ammunition state must permit cycling. Running interrupts.
GUN_FIRING_CYCLE|사격하면 총의 방식에 따라 탄약·약실·탄피 상태가 바뀐다. 상태가 나쁜 총은 남은 탄약이 있을 때 걸릴 수 있다.|Firing changes ammunition, chamber and spent-round state according to the gun. A worn gun with remaining ammunition may jam.
LEGACY_GUN_CONTROLS|구형 장전 방식 설정에서는 등록된 탄약·탄창과 난이도별 규칙을 따른다. 장전은 달리면 중단되지만 약실 조작은 이동으로 중단되지 않는다.|Under the legacy reloading setting, use the registered ammunition or magazine and the difficulty-specific rules. Running interrupts loading, while movement does not interrupt cycling.
GUN_FIRE_MODES|이 총에 제공되는 현재 모드 이외의 발사 모드를 선택할 수 있다.|Choose a different firing mode offered by this firearm.
''', scope=True)

_views('''
DEVICE_ASSEMBLY|선택한 장치 제작법의 재료·도구와 학습·전기 기술 조건이 필요하며 운전 중에는 제작할 수 없다.|Use the materials and tools of the selected device recipe and meet its learning and electrical-skill requirements; crafting is unavailable while driving.
MOLOTOV_ASSEMBLY|화염병 제작법마다 허용하는 병·천·연료가 다르다. 잔량을 검사하는 제작법에서는 연료 태그 물품이 가득 차 있어야 하며 운전 중에는 제작할 수 없다.|Molotov recipes accept different bottles, cloth and fuel. Where the recipe tests fullness, Petrol-tagged items must be full; crafting is unavailable while driving.
TRAP_ASSEMBLY|선택한 덫 제작법의 재료와 학습 조건이 필요하다. 톱과 목공·덫 기술 조건은 해당 제작법에서 요구할 때 적용되며 운전 중에는 제작할 수 없다.|Use the materials and learned recipe for the selected trap. Saw and carpentry/trapping requirements apply where declared; crafting is unavailable while driving.
SAWN_WOOD|통나무·판자를 해당 목재 가공법에 제공하고 허용하는 톱을 사용한다. 운전 중에는 제작할 수 없다.|Supply the log or plank accepted by the selected woodworking recipe and use a permitted saw; crafting is unavailable while driving.
SIMPLE_TRANSFORMATION|선택한 가공법에서 지정한 재료가 필요하며 운전 중에는 제작할 수 없다.|Supply the material specified by the selected transformation; crafting is unavailable while driving.
PLASTER_MIXING|석고 혼합에는 허용하는 양동이와 석고 가루·물이 필요하며 운전 중에는 제작할 수 없다.|Mixing plaster requires an accepted bucket, plaster powder and water; crafting is unavailable while driving.
CAKE_PAN_PREPARATION|케이크 반죽을 베이킹 팬에 옮기는 준비법에 사용하며 운전 중에는 할 수 없다.|Use it to transfer cake batter into a baking pan; preparation is unavailable while driving.
EGG_PACKING|달걀 포장은 익거나 타지 않은 달걀을 받으며 냉동 달걀도 허용한다. 운전 중에는 포장할 수 없다.|Egg packing accepts eggs that are neither cooked nor burnt, including frozen eggs; packing is unavailable while driving.
OMELETTE_PREPARATION|오믈렛 준비에는 프라이팬·허용하는 도구와 익히지 않은 달걀이 필요하며 달걀은 신선도별 남은 양 조건을 만족해야 한다. 운전 중에는 할 수 없다.|Omelette preparation requires a frying pan, accepted utensil and uncooked eggs retaining the amount required for their freshness; it is unavailable while driving.
TRAY_EMPTYING|해당 팬·트레이의 음식을 비울 수 있으며 상한 음식도 허용한다. 재료를 돌려받는 동작은 아니고 운전 중에는 할 수 없다.|Empty the specified food from its pan or tray, including rotten food. Ingredients are not recovered; emptying is unavailable while driving.
MUFFIN_PORTIONING|머핀을 꺼내려면 익힌 머핀 트레이가 필요하며 운전 중에는 할 수 없다.|Removing muffins requires a cooked muffin tray; it is unavailable while driving.
BISCUIT_PORTIONING|비스킷·쿠키를 꺼내려면 익었거나 탄 해당 트레이가 필요하며 운전 중에는 할 수 없다.|Removing biscuits or cookies requires their cooked or burnt tray; it is unavailable while driving.
BEAN_PREPARATION|콩을 그릇에 옮길 때 그릇과 열린 콩 통조림 또는 캔 따개가 필요한 닫힌 통조림을 사용한다. 운전 중에는 할 수 없다.|To prepare a bowl of beans, use a bowl and opened beans, or a closed can with an accepted can opener; preparation is unavailable while driving.
CANDY_OPENING|사탕 포장을 여는 데 사용할 수 있으며 운전 중에는 개봉할 수 없다.|It can be supplied to the candy-package opening recipe; opening is unavailable while driving.
SHOTGUN_SHORTENING|해당 산탄총과 지정된 톱으로 총신 단축 제작법에 참여한다. 호환 부착물은 옮기고 다른 부착물은 돌려주도록 처리하며 운전 중에는 할 수 없다.|Use the corresponding shotgun and specified saw for barrel shortening. Compatible attachments transfer and others are returned; crafting is unavailable while driving.
TORCH_REFILL_RECIPE|토치 재충전에는 가득 차지 않은 토치와 연료가 남은 프로판 탱크가 필요하며 운전 중에는 할 수 없다.|Refilling requires a blowtorch that is not full and a propane tank with fuel remaining; it is unavailable while driving.
BATTERY_REMOVAL_RECIPE|건전지를 꺼내려면 해당 기기에 남은 전력이 있어야 한다. 이동 중에는 가능하지만 운전 중에는 할 수 없다.|Removing a battery requires remaining charge in the supported device. Walking is allowed, but driving is not.
CANDLE_LIGHT_RECIPE|초에 불을 붙이는 제작법에는 초와 허용하는 발화 도구가 필요하다. 걸으면서는 가능하지만 운전 중에는 할 수 없다.|The candle-lighting recipe requires a candle and an accepted fire-starting item. Walking is allowed, but driving is not.
CANDLE_EXTINGUISH_RECIPE|켜진 초를 끄는 제작법에 사용할 수 있다. 걸으면서는 가능하지만 운전 중에는 할 수 없다.|It can be supplied to the lit-candle extinguishing recipe. Walking is allowed, but driving is not.
''', scope=True)

_views('''
AMMUNITION_LOADING_PATHS|해당 탄종을 받는 총기나 탄창과 남은 장전 공간이 필요하다. 달리면 장전이 중단된다.|Use a firearm or magazine that accepts this ammunition and has free capacity; running interrupts loading.
PHYSICS_ATTACK|공격할 수 있는 상태에서 차량 밖에 있어야 하며 밀치기에는 차량 예외가 있다.|Be able to attack and outside a vehicle, with a vehicle exception for shoving.
DEVICE_TIMER_CONTROL|타이머 설정을 지원하는 장치에서 양수의 지연 값을 확인해야 한다.|Confirm a positive delay on a device that offers timer settings.
DEVICE_WORLD_PLACEMENT|설치를 허용하는 장치를 소지한 채 현재 칸에 놓으며 걷거나 달리면 중단된다.|Keep a placement-enabled device in inventory to place it on the current square; walking or running interrupts.
''', scope=True)

_views('''
LIGHT_CONTROL|손에 들거나 장착한 지원 조명의 조작 기능을 쓴다. 발광 가능 여부는 현재 상태에 달려 있다.|Use the controls offered for a supported held or attached light; light emission depends on its current state.
CANDLE_UNEQUIP|켜진 초를 손에서 빼거나 장착한 채 버리면 꺼진 초로 바뀐다.|Unequipping or dropping an equipped lit candle changes it to an unlit candle.
CAMP_IGNITER|꺼진 모닥불에 불쏘시개를 함께 쓰거나, 연료가 든 모닥불에 휘발유를 함께 써 점화를 시도한다. 걷거나 달리면 중단된다.|Use tinder with an unlit campfire, or petrol with an already fueled campfire. Walking or running interrupts the lighting action.
CAMP_FRICTION|연료가 든 꺼진 모닥불에 구멍 낸 나무와 가지·막대를 사용한다. 지구력이 줄고 막대가 부러질 수 있으며 점화는 확률적이다. 이동하면 중단된다.|Use drilled wood and a branch or stick with an unlit fueled campfire. Endurance decreases, the stick may break, and ignition is random. Movement interrupts.
''', scope=True)

for _name in ('FOOD_ASSEMBLY', 'WOOD_SHAPING', 'SAWN_WOOD', 'SIMPLE_TRANSFORMATION'):
    QUALIFIER_VIEWS[getattr(recovery_sources, _name)]['compact'] = None

_views('''
PLANT_CUTTING|대상 덤불·덩굴과 사용 가능한 자르기 도구가 필요하다. 도구가 마모될 수 있으며 이동하면 중단된다.|Use a valid cutting tool on a target bush or vine; the tool may wear and movement interrupts.
WOOD_BARRICADE|판자를 받을 수 있는 문·창문과 허용하는 망치·판자·못 두 개가 필요하다. 작업 중 문을 닫아 두며 이동하면 중단된다.|Use an eligible door or window, an accepted hammer, a plank and two nails. Keep the door closed during work; movement interrupts.
WOOD_UNBARRICADE|판자가 있는 바리케이드와 허용하는 철거 도구가 필요하다. 판자를 하나씩 제거하며 못은 돌려주지 않는다.|Use an accepted removal tool on a barricade with planks. Planks are removed one at a time; nails are not returned.
METAL_BARRICADE|기존 바리케이드가 없는 호환 문·창문에 토치 사용량 한 번과 금속판 또는 막대 세 개가 필요하다. 용접 마스크는 필요하지 않다.|Use a compatible unbarricaded door or window, one torch use and a metal sheet or three bars. A welding mask is not required.
METAL_UNBARRICADE|금속 바리케이드에 사용량이 남은 토치를 사용한다. 토치를 한 번 사용하며 무손상 회수를 보장하지 않는다.|Use a torch with remaining fuel on a metal barricade. One torch use is consumed; full-condition salvage is not guaranteed.
MEAL_UTENSIL|지원하는 음식의 식사 동작에서 숟가락이 포크보다 우선 선택되며 없어도 식사할 수 있다.|For supported eating animations, a spoon takes priority over a fork; neither is required for eating.
STRUCTURE_DESTRUCTION|파괴·보호 구역 규칙이 허용하는 대상에 접근해 사용 가능한 슬레지해머를 장착한다. 이동하면 중단되며 도구가 마모될 수 있다.|Approach an eligible target permitted by destruction and safehouse rules and equip a usable sledgehammer. Movement interrupts and the tool may wear.
''', scope=True)

_views('''
LAMP_BULB|교체 가능한 조명에 빈 전구 자리가 있어야 한다. 전구 설치만으로 전력이나 발광을 보장하지 않는다.|Use an empty bulb slot in a modifiable lamp. Inserting a bulb alone does not supply power or guarantee illumination.
LAMP_BATTERY|건전지용으로 개조한 조명의 빈 칸에 충전량이 남은 건전지를 넣는다.|Use a battery with remaining charge in an empty slot of a lamp converted to battery power.
LAMP_CONVERSION|전기 기술 5와 사용 가능한 드라이버·전자 스크랩이 필요하다. 스크랩 하나를 소비하며 건전지는 별도로 넣어야 한다.|Electricity five, a usable screwdriver and electronic scrap are required. One scrap is consumed; a battery must be added separately.
PILLAR_BATTERY|건전지를 연료로 받는 기둥 조명과 남은 충전량이 있는 건전지가 필요하다.|Use a battery with remaining charge in a pillar lamp that accepts it as fuel.
CHARGER_PLACEMENT|한 칸에 충전기 하나만 설치할 수 있고 배터리가 없는 충전기만 회수할 수 있다.|Only one charger can be placed on a square, and it must have no battery to be retrieved.
CHARGER_CONTROLS|설치된 충전기와 완충되지 않은 차량 배터리가 필요하다. 켜기에는 전력 조건을 충족해야 하며 실제 충전은 별도 처리다.|Use a placed charger and a vehicle battery below full charge. Switching it on requires power; actual charging is handled separately.
VEHICLE_BATTERY_EXCHANGE|호환 차량 배터리 자리와 드라이버·정비 접근 조건이 필요하다. 제거할 때는 엔진이 시동·운전 중이면 안 된다.|Use a compatible battery slot, a screwdriver and mechanics access. The engine must not be started or running for removal.
VEHICLE_BATTERY_CYCLE|호환 차량에 장착한 배터리의 충전량은 엔진 상태·경과 시간과 별도 장치 소비 계산을 따른다. 시동 성공은 보장하지 않는다.|Installed battery charge follows engine state, elapsed time and separate device consumption calculations. Engine start is not guaranteed.
VEHICLE_BULB_EXCHANGE|기본 전구를 받는 호환 차량 자리와 드라이버가 필요하다. 색 전구까지 호환된다고 일반화하지 않는다.|Use a compatible vehicle slot accepting the standard bulb and a screwdriver. Compatibility is not generalized to colored bulbs.
GENERATOR_CONTROL|설치한 발전기에 접근해야 한다. 연결에는 발전기 지식이 필요하며 켜려면 연결·연료·상태 조건을 만족해야 한다. 상태가 낮으면 시동에 실패할 수 있다.|Approach an installed generator. Connecting requires generator knowledge; starting requires connection, fuel and condition, and can fail at low condition.
GENERATOR_REPAIR|꺼진 손상 발전기와 발전기 지식·전자 스크랩이 필요하다. 스크랩을 하나씩 사용하며 한 번으로 완전 수리되지는 않을 수 있다.|Use generator knowledge and electronic scrap on an inactive damaged generator. Scrap is consumed one at a time; one repair may not restore full condition.
GENERATOR_REFUEL|작동하지 않고 가득 차지 않은 발전기에 사용 가능한 휘발유 용기를 장착해 접근한다.|Approach an inactive generator below full fuel with an accepted petrol container equipped.
GENERATOR_HANDLING|접근 가능한 원래 용기에서 양손으로 들거나 연결을 해제한 설치 발전기를 회수한다.|Take it in both hands from an accessible source container, or retrieve a disconnected installed generator.
GENERATOR_INSPECTION|접근 가능한 설치 발전기의 정보를 읽는다. 표시된 정보나 실내 경고는 실제 효과 구현과 구분된다.|Read information from an accessible installed generator. Displayed readings and the indoor warning do not implement the effects themselves.
''', scope=True)

_views('''
FURROW_DIGGING|망가지지 않은 경작 도구로 빈 자연 지면에 접근한다. 이동하면 중단되며 고랑 파기가 파종이나 수확을 뜻하지 않는다.|Approach empty natural ground with an unbroken digging tool. Movement interrupts; digging is separate from sowing or harvesting.
PLANT_REMOVAL|망가지지 않은 경작 도구로 작물·고랑에 접근한다. 수확물을 얻는 동작은 아니며 이동하면 중단된다.|Approach the plant or furrow with an unbroken digging tool. This is not harvesting, and movement interrupts.
GRAVE_DIGGING|사용 가능한 삽과 배치 가능한 자연 지면 두 칸이 필요하다. 접근·양손 장착 후 작업하며 이동하면 중단된다.|Use an unbroken grave-digging shovel and two eligible natural-ground squares. Approach and equip both hands; movement interrupts.
GRAVE_FILLING|아직 메우지 않은 무덤에 사용 가능한 삽을 들고 접근한다. 시신이 없어도 메울 수 있고 이동하면 중단된다.|Approach an unfilled grave with an unbroken shovel. Filling needs no corpse and is interrupted by movement.
THUMPABLE_SCRAP|분해 가능한 건축물에 사용 가능한 톱과 드라이버를 갖추고 접근한다. 보호 구역 규칙을 따르며 고정 수량 회수를 보장하지 않는다.|Approach an eligible built object with an unbroken saw and screwdriver. Safehouse rules apply and salvage amounts are not fixed.
NET_PLACEMENT|어망을 소지하고 가까운 물을 지정한다. 설치와 소지품 제거의 동시 성공은 보장하지 않는다.|Carry the net and select nearby water. Placement and inventory removal are not guaranteed to succeed together.
NET_CHECKING|설치 뒤 한 시간 이상 지난 가까운 어망을 확인한다. 물고기는 확률적으로 나오며 15시간을 넘기면 어망이 부서질 수도 있다.|Check a nearby net after at least one hour. Catches are random; after more than 15 hours the net may break.
NET_REMOVAL|가까운 설치 어망을 회수한다. 새 어망이 반환되며 원래 물품 상태를 보존하지 않는다.|Retrieve a nearby placed net. A new net is returned rather than the original item state.
STONE_TOOL_WEAR|건축 행동 완료 시 주 손의 돌망치가 확률적으로 마모될 수 있다.|A stone hammer in the primary hand may wear when a build action completes.
''', scope=True)

_views('''
PUMP_CONTAINER|전원과 연료가 있는 접근 가능한 주유소와 비어 있거나 덜 찬 허용 용기가 필요하다. 중단해도 일부 이동량이 남으며 완료 시 연료 계산은 진행 중 계산과 다르다.|Use an accessible powered pump with fuel and an eligible empty or nonfull container. Partial transfers can remain after interruption; completion fuel arithmetic differs from progress updates.
VEHICLE_CONTAINER|엔진을 시동하지 않은 차량의 연료 탱크에 맞는 용기로 접근한다. 넣기·빼기 중 일부만 옮겨진 상태로 끝날 수 있다.|Approach a gasoline tank with the engine not started and a compatible container. Addition or siphoning can leave partial transfers.
HEARTH_FUEL|사용 가능한 연료를 대상까지 옮겨 넣는다. 배수형 물품은 한 번 사용하고 다른 물품은 통째로 소비하며 이동하면 중단된다.|Bring eligible fuel to the object. A drainable is used once; other items are consumed whole. Movement interrupts.
HEARTH_TINDER|불이 꺼진 대상에 불쏘시개와 점화 도구를 가져간다. 불쏘시개는 통째로 소비되며 벽난로에 더해지는 연료량은 선택한 불쏘시개와 맞지 않을 수 있다.|Bring tinder and an igniter to an unlit object. Tinder is consumed whole; the fuel amount added to a fireplace may not match the selected tinder.
HEARTH_PETROL|연료가 있고 불이 꺼진 대상과 잔량이 있는 휘발유·점화 도구가 필요하다. 완료 시 양쪽을 한 번 사용한다.|The unlit object needs fuel and both petrol and igniter need charge. Completion uses each once.
INDUSTRIAL_PETROL|연료가 있는 화로 또는 통나무가 든 드럼에 접근한다. 이 점화 동작은 휘발유와 점화 도구를 소비하지 않으며 실제 점화를 보장하지 않는다.|Approach a fueled furnace or logged drum. This action consumes neither petrol nor igniter and does not guarantee ignition.
INDUSTRIAL_TINDER|기존 화로·드럼에 불쏘시개와 점화 도구를 가져간다. 불쏘시개를 소비하지만 화로의 클라이언트 점화 코드는 비활성 상태다.|Bring tinder and an igniter to an existing furnace or drum. Tinder is consumed, but client furnace ignition is inactive in the source.
HEAT_FRICTION|구멍 낸 판자와 나무 막대 또는 나뭇가지, 지구력이 필요하다. 점화는 확률적이며 막대가 부서질 수 있다. 화로의 클라이언트 점화 코드는 비활성 상태다.|Use notched wood, a wooden stick or branch, and endurance. Ignition is random and the stick may break. Client furnace ignition is inactive in the source.
PROPANE_BARBECUE|잔량이 있는 탱크를 프로판 바비큐까지 가져간다. 기존 탱크는 바닥에 반환되며 설치·연료 이전의 동시 성공을 보장하지 않는다.|Bring a tank with fuel to a propane barbecue. An existing tank is dropped on the ground; installation and fuel transfer are not guaranteed to succeed together.
FURNACE_FUEL|연료가 부족한 기존 화로에 접근한다. 원본 동작의 반복 횟수와 소진 처리는 정확한 정량 보충을 보장하지 않는다.|Approach an existing furnace with space for fuel. The source loop and depletion handling do not guarantee an exact refill amount.
BELLOWS_USE|불이 붙고 열이 낮은 기존 화로에 접근한다. 동작 중 열과 지구력을 바꾸며 이동하면 중단된다. 제련 결과는 보장하지 않는다.|Approach an existing lit furnace below maximum heat. The action changes heat and endurance and stops with movement; it does not guarantee smelting.
DRUM_LOGS|비어 있는 가까운 금속 드럼과 통나무 다섯 개가 필요하다. 점화·시간 경과·숯 회수는 별도 단계이며 물품 전달 성공을 보장하지 않는다.|Use five logs at a nearby empty metal drum. Ignition, elapsed updates and charcoal retrieval are separate steps; item delivery is not guaranteed.
CORPSE_IGNITION|접근 가능한 시신, 휘발유와 점화 도구가 필요하다. 완료 시 두 물품을 사용하지만 실제 시신 소각 결과는 별도다.|Use petrol and an igniter at an accessible corpse. Completion uses both items; the actual corpse-burning result remains separate.
''', scope=True)

_views('''
CAMP_PETROL_USE|연료가 있고 꺼진 모닥불에 사용량이 충분한 휘발유와 점화 도구를 가져간다. 양쪽을 한 번 사용하며 걷기·달리기로 중단된다.|Bring sufficient petrol and an igniter to an unlit fueled campfire. Each is used once; walking or running interrupts.
TRAP_CONTROLS|설치한 덫에 접근해 현재 미끼·포획물 상태에 맞는 동작을 선택한다. 회수 물품은 새로 생성되며 미끼 반환과 명령 전달의 동시 성공을 보장하지 않는다.|Approach a placed trap and choose an action matching its bait/catch state. Returned items are newly created; bait return and command delivery may not succeed together.
TRAP_LIFECYCLE|포획에는 신선한 대응 미끼와 동물별 시간·지역·확률 조건이 필요하다. 미끼를 잃거나 덫이 파괴될 수 있고 포획한 동물은 소리를 낼 수 있다.|Catches require accepted fresh bait and animal-specific time, zone and random conditions. Bait can be lost, traps destroyed, and captured animals can make noise.
ROD_LINE_BREAK|낚싯줄 파손 시 제작 낚싯대는 나무 막대, 완제품 낚싯대는 부러진 낚싯대를 반환하도록 하고 원래 낚싯대와 미끼를 제거한다.|A broken line requests a wooden stick for a crafted rod or a broken rod for a modern rod, and removes the original rod and lure.
FISHING_EXECUTION|허용된 높이의 가까운 물에서 낚싯대·미끼를 계속 들고 있어야 한다. 이동하면 중단되며 물고기 잔량·확률·반복 선택과 물품 생성에 따라 포획 결과가 달라진다.|Keep the rod and lure held at nearby water on an allowed level. Movement interrupts; stock, random/repeated selection and item creation determine the catch result.
ENGINE_REPAIR|열화된 엔진, 예비 부품·렌치와 차량별 수리 기술·접근 권한이 필요하다. 부품별 조건 회복과 소모를 요청하지만 정상 엔진 작동을 보장하지 않는다.|A damaged engine needs spare parts, a wrench, its repair skill and access. The action requests condition recovery and part consumption, without guaranteeing engine operation.
ENGINE_SALVAGE|상태가 10을 넘는 엔진과 렌치·수리 기술·접근 권한이 필요하다. 부품 회수량은 확률에 달려 있고 엔진 상태는 0으로 설정된다.|An engine above condition ten requires a wrench, repair skill and access. Salvage is random and engine condition is set to zero.
VEHICLE_TOOL_USE|해당 차량 부품의 도구·제작법·접근 조건을 충족해야 한다. 도구는 보존되며 기술에 따른 설치·분리 실패와 부품 손상이 가능하다.|Meet the part's tool, recipe and access requirements. Tools are kept; skill-dependent installation/removal failure and part damage are possible.
WEAPON_ATTACHMENT_TOOL|사용 가능한 드라이버와 호환 무기·부착물이 필요하다. 걷거나 달리면 중단되며 드라이버를 소비하지 않는다.|Use an unbroken screwdriver with a compatible weapon and part. Walking or running interrupts; the screwdriver is kept.
PLASTER_USE|목공 4와 석고 양동이로 석고 처리가 가능한 대상에 접근한다. 한 번 사용해 외형·칠하기 상태 변경을 요청하며 구조물 강화를 뜻하지 않는다.|Approach a plasterable object with Woodwork four and a plaster bucket. One use requests its plaster appearance and paintable state; this is not structural reinforcement.
COMPOST_TRANSFER|퇴비와 여유 공간이 있는 통·포대를 사용한다. 빈 자루는 퇴비 포대로 교체되며 일부만 채워질 수 있다. 이동하면 중단된다.|Use a bin and bag with available compost and capacity. An empty sack is replaced by a compost bag and may fill only partially. Movement interrupts.
CURTAIN_USE|커튼이 없는 대응 창문·문에 시트를 가져가 설치한다. 설치한 커튼은 열기·닫기·제거를 지원하며 시야 차단과 제거 후 반환되는 물품은 확인되지 않았다.|Bring a sheet to an eligible window or door without curtains. The installed curtain supports opening, closing and removal; blocked visibility and the item returned after removal remain unconfirmed.
BURNT_VEHICLE_USE|불타거나 파손된 차량에 용접 마스크와 10회 사용량의 토치를 갖추고 접근한다. 재료 회수는 확률적이며 완료 시 토치를 10회 사용하고 차량 제거를 요청한다.|Approach a burnt or smashed vehicle with a welding mask and ten torch uses. Salvage is random; completion spends ten uses and requests vehicle removal.
''', scope=True)

# Public projections are authored independently at each resolution. The source
# predicate remains canonical and is referenced in the existing audit member;
# an implementation branch is not a player condition or a promised outcome.
PROJECTION_NOTES = {}


def _public_view(name, *, expanded=None, compact=None, note):
    predicate = getattr(recovery_sources, name)
    if expanded is not None:
        QUALIFIER_VIEWS[predicate]['expanded'] = expanded
    QUALIFIER_VIEWS[predicate]['compact'] = compact
    PROJECTION_NOTES[predicate] = note


for _name in ('WOOD_BARRICADE', 'WOOD_UNBARRICADE', 'METAL_BARRICADE', 'METAL_UNBARRICADE'):
    _public_view(_name, note='The function identifies the applicable barricade operation. Materials, quantities, tool eligibility and operation details remain in expanded; they are not repeated in first-contact prose.')

_public_view('PHYSICS_ATTACK',
    expanded=('투척 공격은 차량 밖에서 할 수 있다.', 'Throwing attacks require being outside a vehicle.'),
    compact=('투척 공격은 차량 밖에서 할 수 있다.', 'Throwing attacks require being outside a vehicle.'),
    note='SwingAnim=Throw and PhysicsObject declarations establish throwing-weapon use with the admitted attack input path. The common hook shoving exception does not apply to throwing. Native projectile creation, collision, damage, ignition and companion consumption are not admitted effects. No request/attempt wording is used as a substitute for those effects.')
_public_view('HEARTH_FUEL',
    expanded=('사용 가능한 연료를 대상에 넣어 소모한다. 이동하면 작업이 중단된다.', 'Eligible fuel is consumed when added to the object. Movement interrupts the action.'),
    note='Expanded consumption uses only this item’s unambiguous Type from existing exact declaration observations: one Drainable use or whole-item removal. Unknown/conflicting Type uses a quantity-neutral statement. The complete branches remain in the predicate. Native heat and combustion remain outside the admitted function.')
_public_view('HEARTH_TINDER',
    expanded=('불이 꺼진 대상에 불쏘시개와 점화 도구가 필요하다. 불쏘시개는 통째로 소모하고 점화 도구도 사용한다.', 'An unlit object needs tinder and a fire-starting item. The tinder is consumed whole and the fire-starting item is used.'),
    compact=('불이 꺼진 대상과 점화 도구가 필요하며 불쏘시개는 소모된다.', 'An unlit object and a fire-starting item are needed; the tinder is consumed.'),
    note='Fireplace fuel amount/list alignment and unbound lookup limitations remain source-analysis notes in the predicate. Public prose promises neither a specific burn duration nor unconditional command delivery.')
_public_view('HEARTH_PETROL',
    compact=('연료가 있고 불이 꺼진 대상과 잔량이 있는 휘발유·점화 도구가 필요하다.', 'The object must be fueled and unlit, with usable petrol and a fire-starting item.'),
    note='Per-action consumption remains expanded. Fireplace lookup and native execution limits remain in the source predicate; no guaranteed ignition result is added.')
_public_view('INDUSTRIAL_TINDER',
    expanded=('통나무가 있고 불이 꺼진 드럼에 불쏘시개와 점화 도구를 사용한다. 불쏘시개는 통째로 소모된다.', 'Use tinder and a fire-starting item at an unlit drum containing logs. The tinder is consumed whole.'),
    compact=('통나무가 있고 불이 꺼진 드럼과 점화 도구가 필요하며 불쏘시개는 소모된다.', 'An unlit drum containing logs and a fire-starting item are needed; the tinder is consumed.'),
    note='Public function scope is the independently supported drum path. The furnace branch has inactive client lighting and a nonclient state change; neither single-player availability nor general furnace ignition is inferred. The full accepted fact/predicate and source limitation are retained, including unused fuel amount and native delivery limits.')
_public_view('HEAT_FRICTION',
    expanded=('연료가 있고 불이 꺼진 대상에서 구멍 낸 판자와 나무 막대 또는 나뭇가지, 지구력이 필요하다. 점화는 확률적이며 막대가 부서질 수 있다.', 'At a fueled, unlit object, use notched wood, a wooden stick or branch, and endurance. Ignition is random and the stick may break.'),
    compact=('구멍 낸 판자와 나무 막대 또는 나뭇가지, 지구력이 필요하다. 점화는 확률적이며 막대가 부서질 수 있다.', 'Notched wood, a wooden stick or branch, and endurance are needed. Ignition is random and the stick may break.'),
    note='Public target scope is the independently supported non-propane barbecue, fireplace and logged drum. The inactive client furnace branch is not translated to a play mode or promised furnace function. Attempt timing, exact chances, stick preference and native delivery remain in the predicate.')
_public_view('INDUSTRIAL_PETROL',
    expanded=('연료가 있고 불이 꺼진 화로 또는 통나무가 있고 불이 꺼진 드럼에 휘발유와 점화 도구를 사용한다. 이 동작에서는 두 물품을 소모하지 않는다.', 'Use petrol and a fire-starting item at an unlit fueled furnace or unlit drum containing logs. This action does not consume either item.'),
    compact=('연료가 있고 불이 꺼진 화로 또는 통나무가 있고 불이 꺼진 드럼과 점화 도구가 필요하다.', 'An unlit fueled furnace or unlit drum containing logs and a fire-starting item are needed.'),
    note='The petrol path differs from the inactive client tinder/friction furnace branches. Retain the confirmed use and consumption detail without guaranteeing native ignition or command delivery.')
_public_view('PROPANE_BARBECUE',
    expanded=('잔량이 있는 탱크를 프로판 바비큐에 넣는다. 기존 탱크가 있으면 바닥에 놓인다.', 'Insert a tank with fuel into a propane barbecue. An existing tank is placed on the ground.'),
    compact=('프로판 바비큐와 연료가 남은 탱크가 필요하다.', 'A propane barbecue and a tank with fuel remaining are needed.'),
    note='Non-atomic installation/fuel transfer and native heating are source boundaries, not additional public functions.')
_public_view('FURNACE_FUEL',
    expanded=('연료가 부족한 기존 화로에 넣어 소모한다.', 'It is consumed to add fuel to an existing furnace with fuel capacity remaining.'),
    note='The source loop, depletion handling, native clamping and obsolete item availability do not establish an exact refill amount. The independently confirmed fuel role is retained.')
_public_view('BELLOWS_USE',
    expanded=('불이 붙고 열이 낮은 화로의 열을 높이며 지구력을 쓴다. 이동하면 중단된다.', 'It raises heat in a lit furnace below maximum heat and uses endurance. Movement interrupts.'),
    compact=('불이 붙고 열이 낮은 화로에 사용하며 지구력을 쓴다.', 'Use it on a lit furnace below maximum heat; it costs endurance.'),
    note='Per-update heat/endurance arithmetic and native smelting remain in the predicate. Raising heat does not establish a smelting output.')
_public_view('DRUM_LOGS',
    expanded=('비어 있는 금속 드럼에 통나무 다섯 개를 넣는다. 숯을 얻으려면 점화하고 시간이 지난 뒤 회수해야 한다.', 'Put five logs into an empty metal drum. Obtaining charcoal also requires lighting, elapsed time and retrieval.'),
    compact=('비어 있는 금속 드럼이 필요하다. 숯을 얻으려면 점화와 시간 경과·회수가 필요하다.', 'An empty metal drum is needed. Charcoal also requires lighting, elapsed time and retrieval.'),
    note='Exact timer/output quantities and non-atomic delivery remain in the predicate. Carried logs alone do not guarantee charcoal.')

# The following controls shared the expanded-to-compact copy rule. Keep their
# confirmed purpose and meaningful prerequisites; procedural and source notes
# must not become repeated first-contact qualifications.
for _name, _ko, _en in (
    ('GENERATOR_INSPECTION', '접근 가능한 설치 발전기의 정보를 읽는다.', 'Read information from an accessible installed generator.'),
    ('NET_PLACEMENT', '어망을 소지하고 가까운 물에 설치한다.', 'Carry the net and place it in nearby water.'),
    ('PUMP_CONTAINER', '전원과 연료가 있는 주유소와 비어 있거나 덜 찬 허용 용기가 필요하다. 중단해도 일부 옮긴 연료는 남을 수 있다.', 'Use a powered pump with fuel and an eligible empty or nonfull container. Partial transfers can remain after interruption.'),
    ('TRAP_CONTROLS', '설치한 덫의 미끼·포획물 상태에 맞게 미끼 넣기·회수·덫 회수 동작을 선택한다.', 'Use bait placement, retrieval or trap removal as allowed by the placed trap’s bait and catch state.'),
    ('FISHING_EXECUTION', '가까운 물에서 낚싯대와 미끼를 들고 낚시한다. 이동하면 중단되며 물고기 잔량과 확률에 따라 포획 결과가 달라진다.', 'Fish in nearby water while holding a rod and lure. Movement interrupts; catches depend on remaining stock and chance.'),
    ('CURTAIN_USE', '커튼이 없는 대응 창문·문에 시트를 설치한다. 설치한 커튼은 열고 닫거나 제거할 수 있다.', 'Install a sheet on an eligible window or door without curtains. The installed curtain can be opened, closed or removed.'),
    ('CHARGER_CONTROLS', '설치된 충전기와 완충되지 않은 차량 배터리가 필요하다. 켜려면 전력이 있어야 한다.', 'Use a placed charger and a vehicle battery below full charge. Switching it on requires power.'),
    ('VEHICLE_BULB_EXCHANGE', '기본 전구를 받는 호환 차량 자리와 드라이버가 필요하다.', 'Use a compatible vehicle slot accepting the standard bulb and a screwdriver.'),
):
    _public_view(_name, expanded=(_ko, _en), compact=(_ko, _en),
        note='The referenced predicate retains exact execution, factory/native and delivery boundaries. Public text expresses the admitted control and applicable prerequisite, without treating internal uncertainty as a play condition or adding an unconfirmed downstream effect.')

FUNCTION_VIEWS.update({
    'request_physics_attack': ('투척 공격용 무기다.', 'It is a weapon for throwing attacks.'),
    'provide_industrial_tinder': ('통나무가 든 드럼에 불을 붙이는 불쏘시개로 쓸 수 있다.', 'It can serve as tinder for lighting a drum containing logs.'),
    'ignite_industrial_tinder': ('불쏘시개로 통나무가 든 드럼에 불을 붙이는 데 쓸 수 있다.', 'It can light tinder at a drum containing logs.'),
    'kindle_heat_sources': ('프로판을 쓰지 않는 바비큐·벽난로·통나무가 든 드럼의 마찰 점화에 쓸 수 있다.', 'It can be used for friction lighting of a non-propane barbecue, fireplace or drum containing logs.'),
    'provide_hearth_tinder': ('프로판을 쓰지 않는 바비큐·벽난로의 불쏘시개로 쓸 수 있다.', 'It can serve as tinder for a non-propane barbecue or fireplace.'),
})

for _name in ('CAMP_FUEL_USE', 'CAMP_TINDER_USE'):
    _public_view(_name, compact=QUALIFIER_VIEWS[getattr(recovery_sources, _name)]['compact'],
        note='Expanded projects clothing/container eligibility only for this item’s unambiguous Type in existing exact declaration observations. Favorite status and consumption apply generally; tinder also requires a fire-starting item. Ambiguous Type retains the general conditional view, without a declaration winner. All source filters remain in the referenced predicate.')
_public_view('CURTAIN_USE', compact=('커튼이 없는 대응 창문·문이 필요하다.', 'An eligible window or door without curtains is needed.'),
    note='The direct functions already state installation and opening/closing/removal. The qualifier only adds the absence-of-curtains prerequisite. Unconfirmed visibility and return-item behavior remain in the source predicate; neither is an admitted public effect.')
_public_view('CAMP_FRICTION',
    compact=('연료가 있고 불이 꺼진 모닥불과 구멍 낸 판자·막대가 필요하다. 지구력을 쓰며 점화는 확률적이고 막대가 부서질 수 있다.', 'An unlit fueled campfire, notched wood and a stick are needed. It costs endurance; ignition is random and the stick may break.'),
    note='Movement interruption and exact attempt timing remain expanded or in the predicate. The first-contact distinction is friction lighting with endurance, uncertain ignition and possible stick loss, not a procedural transcript.')

for _name, _expanded, _compact, _note in (
    ('NET_REMOVAL',
     ('가까운 설치 어망을 회수한다. 회수한 어망은 설치 전 물품의 상태를 이어받지 않는다.', 'Retrieve a nearby placed net. The retrieved net does not retain the pre-placement item state.'), None,
     'Returned-item state is an expanded detail. Factory identity and delivery remain in the source predicate.'),
    ('ENGINE_REPAIR',
     ('열화된 엔진에 예비 부품과 렌치를 사용한다. 차량별 수리 기술과 정비 접근 조건이 필요하다.', 'Use spare parts and a wrench on a damaged engine, with the required repair skill and mechanics access.'),
     ('차량에 맞는 수리 기술과 예비 부품·렌치가 필요하다.', 'The vehicle requires the appropriate repair skill, spare parts and a wrench.'),
     'The admitted repair use does not establish successful engine operation. Exact part consumption, condition-update requests and native completion remain in the predicate.'),
    ('PLASTER_USE',
     ('목공 4와 석고 양동이로 석고 처리가 가능한 대상에 석고를 바른다. 한 번 사용하며 칠할 수 있는 외형으로 바꾼다.', 'With Woodwork four and a plaster bucket, apply plaster to an eligible object. It uses one charge and changes the object to a paintable appearance.'),
     ('석고를 바를 수 있는 대상과 목공 기술이 필요하다.', 'A plasterable object and carpentry skill are needed.'),
     'The admitted appearance/paintable state change does not establish structural reinforcement. Exact skill/consumption details remain expanded and native delivery remains in the predicate.'),
    ('CORPSE_IGNITION',
     ('접근 가능한 시신의 소각 동작에 휘발유와 점화 도구를 사용한다. 두 물품을 각각 한 번 소모한다.', 'Use petrol and a fire-starting item for a corpse-burning action at an accessible corpse. Each item is used once.'),
     ('시신과 사용 가능한 휘발유·점화 도구가 필요하다.', 'A corpse, usable petrol and a fire-starting item are needed.'),
     'This is an admitted use with consumption, not a confirmed native corpse destruction result. Native burnCorpse outcome remains outside the accepted effects.'),
    ('BURNT_VEHICLE_USE',
     ('불타거나 파손된 차량에 용접 마스크와 10회 사용량의 토치를 사용한다. 회수 재료는 확률에 따라 달라진다.', 'Use a welding mask and ten torch uses on a burnt or smashed vehicle. Salvaged materials vary by chance.'),
     ('불타거나 파손된 차량과 용접 마스크·연료가 있는 토치가 필요하다. 회수 재료는 확률에 따라 달라진다.', 'A burnt or smashed vehicle, welding mask and fueled torch are needed. Salvaged materials vary by chance.'),
     'The action requests native vehicle removal; successful delivery is not a separate admitted effect. Exact torch consumption remains expanded.'),
):
    _public_view(_name, expanded=_expanded, compact=_compact, note=_note)


def projection_audit(descriptions):
    """Source remainders belong to the existing audit, not the user surface."""
    refs = defaultdict(list)
    for fact in descriptions['facts']:
        predicate = fact['payload'].get('predicate')
        if predicate in PROJECTION_NOTES:
            refs[predicate].append(fact['ref'])
    return [{'fact_refs': sorted(refs[predicate]), 'boundary': PROJECTION_NOTES[predicate],
             'expanded': list(QUALIFIER_VIEWS[predicate]['expanded']),
             'compact': list(QUALIFIER_VIEWS[predicate]['compact']) if QUALIFIER_VIEWS[predicate]['compact'] else None}
            for predicate in sorted(refs)]


def _subject_types(semantic):
    """Read existing exact declarations; repeated observations are not items.

    Physical declaration identity retains path, source hash and line span.
    Distinct declarations or conflicting Type values never select a winner.
    No additional source files are read for expression projection.
    """
    wanted = {f['item_id'] for f in semantic['facts'] if f['payload'].get('predicate') in
              {recovery_sources.CAMP_FUEL_USE, recovery_sources.CAMP_TINDER_USE, recovery_sources.HEARTH_FUEL}}
    records = defaultdict(dict)
    for observation in semantic['observations'].values():
        locator = observation.get('locator', '')
        item_id = locator.rsplit(':', 1)[-1]
        content = observation['content']
        if item_id not in wanted or not content.get('clauses'):
            continue
        header = re.match(r'\s*item\s+([\w.]+)\s*\{', content.get('raw', ''))
        if not header or header[1] not in {item_id, item_id.split('.', 1)[1]}:
            continue
        key = (observation['source_path'], observation['source_sha256'], locator.split(':', 1)[0],
               tuple(content['clauses']))
        records[item_id][key] = content
    result = {}
    for item_id, declarations in records.items():
        if len(declarations) == 1:
            fields, _ = recovery_sources.stable_properties(next(iter(declarations.values())))
            if fields.get('Type'):
                result[item_id] = fields['Type']
    return result


CONTEXTS = {**expression_rules.CONTEXTS,
    'curtain_handling': ('커튼 조작', 'curtain handling'),
    'surface_preparation': ('표면 준비', 'surface preparation'),
    'compost_handling': ('퇴비 취급', 'compost handling'),
    'weapon_modification': ('무기 개조', 'weapon modification'),
    'fuel_handling': ('연료 취급', 'fuel handling'),
    'metalworking': ('금속 작업', 'metalworking'),
    'charcoal_preparation': ('숯 준비', 'charcoal preparation'),
    'watermelon_breaking': ('수박 쪼개기', 'breaking a watermelon'),
    'metal_welding_construction': ('금속 용접 건축', 'welded construction'),
    'dough_preparation': ('반죽 준비', 'dough preparation'),
    'batter_preparation': ('묽은 반죽 준비', 'batter preparation'),
    'item_packaging': ('물품 포장', 'item packing'), 'food_portioning': ('음식 나누기', 'food portioning'),
    'seed_packaging': ('씨앗 포장', 'seed packing'), 'vegetable_jarring': ('채소 병조림', 'vegetable jarring'),
    'crop_spray_preparation': ('작물 치료제 준비', 'crop-treatment spray preparation'),
    'campfire_kit_preparation': ('모닥불 키트 제작', 'campfire-kit crafting'),
    'tent_kit_making': ('텐트 키트 제작', 'tent-kit crafting'),
    'metal_forging': ('금속 단조', 'metal forging'), 'welded_parts': ('금속 부품 용접', 'metal-part welding'),
    'log_binding': ('통나무 묶음 제작·해체', 'log bundling and unstacking'),
    'mattress_preparation': ('매트리스 제작', 'mattress crafting'),
    'frog_preparation': ('개구리 고기 손질', 'frog-meat preparation'),
    'wire_recovery': ('부서진 통발의 철사 회수', 'wire recovery from a broken net'),
    'poultice_preparation': ('약초 찜질제 준비', 'herbal-poultice preparation'),
    'smithing_parts': ('문손잡이·경첩 단조', 'door-knob and hinge forging'),
    'shovel_smithing': ('삽·손삽 단조', 'shovel and hand-shovel forging'),
    'tool_crafting': ('석제 도구 제작', 'stone-tool crafting'), 'splint_crafting': ('부목 제작', 'splint crafting'),
    'fishing_gear_crafting': ('낚시 장비 제작', 'fishing-gear crafting'),
    'bandaging_material_preparation': ('붕대·소독솜 준비', 'bandaging-supply preparation'),
    'furniture_crafting': ('가구 부품 제작', 'furniture-part crafting'),
    'spear_crafting': ('창 제작', 'spear crafting'), 'spear_upgrade': ('창 부착물 장착', 'spear attachment'),
    'spear_reclaim': ('창 부착물 회수', 'spear-attachment recovery'),
    'radio_crafting': ('간이 무전기 제작', 'makeshift-radio crafting'),
    'radio_salvage': ('라디오·TV 분해', 'radio and television dismantling'),
    'electronic_salvage': ('전자 기기 분해', 'electronic-device dismantling'),
    'carpentry_menu_construction': ('목공 건축', 'carpentry construction'),
    'battery_insertion': ('건전지 삽입', 'battery insertion'), 'package_opening': ('포장 개봉', 'package opening'),
    'umbrella_form_change': ('우산 접기·펼치기', 'umbrella folding and opening'),
    'sheet_rope_making': ('시트 로프 제작', 'sheet-rope crafting'),
    'food_ingredient_addition': ('조리 재료 추가', 'adding cooking ingredients')}
ROLES = {**expression_rules.ROLES, 'fuel': ('연료', 'fuel'), 'container': ('용기', 'a container'),
    'attachment': ('부착물', 'an attachment'), 'transformation_target': ('가공 대상', 'the item being transformed'),
    'power_receiver': ('전력을 받는 기기', 'the device receiving power'), 'base': ('바탕 재료', 'a preparation base')}
CONTEXTS.update({'grain_preparation': ('쌀·파스타 준비', 'rice and pasta preparation'), 'animal_butchery': ('작은 동물 손질', 'small-animal butchery'), 'fish_preparation': ('생선 손질', 'fish preparation'), 'cookie_preparation': ('쿠키 반죽 준비', 'cookie dough preparation'), 'pumpkin_carving': ('호박 조각', 'pumpkin carving')})

CONTEXTS.update({'ammunition_disassembly': ('탄약 분해', 'ammunition dismantling'), 'explosive_assembly': ('폭발·발화·신호 장치 제작', 'explosive, incendiary and signaling device assembly'), 'explosive_modification': ('장치 작동 부품 장착', 'device triggering-component installation'), 'electronic_assembly': ('타이머·원격 조작 부품 제작', 'timer and remote-control component assembly'), 'trap_crafting': ('덫 제작', 'trap crafting'), 'bottle_breaking': ('병 깨기', 'bottle breaking'), 'plaster_preparation': ('석고 혼합', 'plaster mixing'), 'food_container_emptying': ('음식 용기 비우기', 'emptying food containers'), 'shotgun_modification': ('산탄총 총신 단축', 'shotgun barrel shortening'), 'blowtorch_refilling': ('토치 재충전', 'blowtorch refilling'), 'battery_removal': ('건전지 꺼내기', 'battery removal'), 'candle_lighting': ('초에 불 붙이기', 'candle lighting'), 'candle_extinguishing': ('초 끄기', 'candle extinguishing'), 'hat_crafting': ('모자 제작', 'hat crafting')})

COMPACT_CONTEXTS = {**CONTEXTS, **{child: CONTEXTS['metal_forging']
    for child in ('smithing_parts', 'shovel_smithing')}}
DETAIL_FACTS = {
    ('effect', (('direction', 'set_transferring_character'), ('property', 'food_chef_attribution'))):
        'Chef attribution is metadata recorded by the examined inventory-transfer action. It does not change the food functions, ingredient role, bait eligibility, nutrition or preparation effect needed for first contact. The accepted effect and its exact transfer scope remain accessible in expanded.'}


def _context_core(fact, facts, locale):
    context = facts[fact['context_ref']] if fact['context_ref'] else fact
    activity = context['payload']['activity']
    inv.require(activity in CONTEXTS, 'unreviewed recovery context: ' + activity)
    name = CONTEXTS[activity][0 if locale == 'ko' else 1]
    if fact['fact_kind'] == 'use_context':
        return name + '에 쓰인다.' if locale == 'ko' else 'It is used for ' + name + '.'
    role = fact['payload']['role']
    inv.require(role in ROLES, 'unreviewed recovery role: ' + role)
    return _role_text([name], role, locale)


def _role_text(names, role, locale):
    if role == 'repair_target':
        return '수리할 수 있는 물품이다.' if locale == 'ko' else 'It can be repaired.'
    noun = ROLES[role][0 if locale == 'ko' else 1]
    if locale == 'ko':
        ending = (ord(noun[-1]) - ord('가')) % 28
        return '·'.join(names) + '에서 ' + noun + ('로' if ending in {0, 8} else '으로') + ' 쓰인다.'
    joined = names[0] if len(names) == 1 else (' and '.join(names) if len(names) == 2 else ', '.join(names[:-1]) + ', and ' + names[-1])
    return 'It serves as ' + noun + ' for ' + joined + '.'


def _qualifier_view(fact, locale, resolution, subject_types):
    predicate = fact['payload']['predicate']
    item_type = subject_types.get(fact['item_id'])
    if resolution == 'expanded' and item_type:
        if predicate in {recovery_sources.CAMP_FUEL_USE, recovery_sources.CAMP_TINDER_USE}:
            ko = '즐겨찾기에서 해제해야 하며 사용하면 소모한다.'
            en = 'It must not be a favorite and is consumed when used.'
            if item_type == 'Clothing':
                ko += ' 착용 중이라면 벗어야 한다.'
                en += ' It must be unequipped if worn.'
            elif item_type == 'Container':
                ko += ' 안에 든 물품을 비워야 한다.'
                en += ' Its contents must be emptied.'
            if predicate == recovery_sources.CAMP_TINDER_USE:
                ko += ' 점화 도구가 필요하다.'
                en += ' A fire-starting item is needed.'
            return ko if locale == 'ko' else en
        if predicate == recovery_sources.HEARTH_FUEL:
            pair = (('연료로 한 번 사용하며 이동하면 작업이 중단된다.', 'One use is consumed as fuel; movement interrupts the action.')
                    if item_type == 'Drainable' else
                    ('연료로 물품 전체를 소모하며 이동하면 작업이 중단된다.', 'The whole item is consumed as fuel; movement interrupts the action.'))
            return pair[0 if locale == 'ko' else 1]
    if predicate in QUALIFIER_VIEWS:
        pair = QUALIFIER_VIEWS[predicate][resolution]
        return pair[0 if locale == 'ko' else 1] if pair else None
    if predicate in expression_rules.PREDICATES:
        if resolution == 'compact' and projection.qualifier_tag(fact) is None:
            return None
        return expression_rules.predicate(fact, locale)
    inv.require(False, 'unreviewed recovery qualifier view: ' + predicate)


def _coalesce_expanded(rows, cores, facts, locale, review_ref, subject_types):
    # These conjunctions realize all matched propositions, including effects.
    # No item name or profile winner controls them.
    combined_rows = []

    def combine(wanted, pair):
        matches = [row for row in rows if (facts[row['claim_ref']]['fact_kind'],
                   tuple(sorted(facts[row['claim_ref']]['payload'].items()))) in wanted]
        if len(matches) != len(wanted):
            return
        refs = {r for row in matches for r in row['represented_fact_refs']}
        row = {'locale': locale, 'resolution': 'expanded', 'text': pair[0 if locale == 'ko' else 1],
               'claim_ref': min(r['claim_ref'] for r in matches), 'claim_refs': sorted(r['claim_ref'] for r in matches),
               'represented_fact_refs': sorted(refs),
               'dependency_refs': sorted({expression.canonical(d): d for e in matches for d in e['dependency_refs']}.values(), key=expression.canonical),
               'rule_ref': 'recovered_expanded/2/combined/' + locale, 'review_ref': review_ref}
        combined_rows.append({'expression_id': expression.identity(row), **row})
        rows[:] = [r for r in rows if r not in matches]

    note_claims = {('direct_function', (('function', f),)) for f in ('view_written_note_pages', 'record_written_notes')}
    note_claims.update(('effect', (('direction', 'update'), ('property', p))) for p in
                       ('written_note_pages', 'written_note_title', 'written_note_lock'))
    combine(note_claims, (
        '저장된 메모는 필기구 없이 읽을 수 있다. 내용과 제목을 작성하려면 필기구가 있고 다른 사용자가 잠그지 않은 상태에서 자신의 편집 잠금도 풀어야 한다. 쪽수와 입력 길이 제한 안에서 편집하고 확인하면 저장한다. 편집 잠금은 설정·해제 즉시 적용되며 쪽 편집을 취소해도 되돌려지지 않는다.',
        'Stored notes can be read without a writing implement. Writing pages and titles requires a writing implement, no lock held by another user and an unlocked editing state. Edit within the page and entry limits and confirm to save. Setting or removing the editing lock applies immediately and survives cancellation of page edits.'))
    combine({('direct_function', (('function', 'wash_carried_equipment'),)),
             ('effect', (('direction', 'remove_by_washing'), ('property', 'item_surface_blood')))}, (
        '접근 가능한 물 공급원에서 소지한 물품을 씻어 피를 지울 수 있다. 세제는 필수가 아니다.',
        'The carried item can be washed at an accessible water source to remove blood. Soap is optional.'))
    covered = set()
    for row in rows:
        claim = facts[row['claim_ref']]
        context = claim['context_ref']
        if context:
            role_scope = {_qualifier_view(facts[q], locale, 'expanded', subject_types) for q in claim['qualifier_refs']}
            context_scope = {_qualifier_view(facts[q], locale, 'expanded', subject_types) for q in facts[context]['qualifier_refs']}
            if role_scope <= context_scope:
                covered.add(context)
    groups = defaultdict(list)
    for row in rows:
        if row['claim_ref'] not in covered:
            implied = {recovery_sources.FOOD_TRANSFER} if facts[row['claim_ref']]['payload'] == {
                'property': 'food_chef_attribution', 'direction': 'set_transferring_character'} else set()
            qualifiers = tuple(sorted({_qualifier_view(facts[q], locale, 'expanded', subject_types)
                for q in row['represented_fact_refs'] if facts[q]['fact_kind'] in {'condition', 'constraint'}
                and facts[q]['payload']['predicate'] not in implied}))
            groups[qualifiers].append(row)
    result = []
    for qualifiers, group in sorted(groups.items()):
        claims = sorted(row['claim_ref'] for row in group)
        texts = list(dict.fromkeys(cores[r] for r in claims))
        row = {'locale': locale, 'resolution': 'expanded', 'text': ' '.join([*texts, *qualifiers]),
               'claim_ref': claims[0], 'claim_refs': claims,
               'represented_fact_refs': sorted({r for e in group for r in e['represented_fact_refs']}),
               'dependency_refs': sorted({expression.canonical(d): d for e in group for d in e['dependency_refs']}.values(), key=expression.canonical),
               'rule_ref': 'recovered_expanded/2/' + locale, 'review_ref': review_ref}
        result.append({'expression_id': expression.identity(row), **row})
    return [*combined_rows, *result]


def _compact_recovery(selected, facts, cores, locale, review_ref, subject_types):
    remaining = expression._expand_qualifiers(selected, facts) & set(cores)
    details = {r: DETAIL_FACTS[(facts[r]['fact_kind'], tuple(sorted(facts[r]['payload'].items())))]
               for r in remaining if (facts[r]['fact_kind'], tuple(sorted(facts[r]['payload'].items()))) in DETAIL_FACTS}
    remaining.difference_update(details)
    rows = []

    def related(refs):
        mentioned = set(refs) | {facts[r]['context_ref'] for r in refs if facts[r]['context_ref']}
        qualifiers = {q for r in mentioned for q in facts[r]['qualifier_refs']}
        return mentioned, qualifiers

    def scopes(refs):
        return tuple(sorted({view for q in related(refs)[1]
                             if (view := _qualifier_view(facts[q], locale, 'compact', subject_types))}))

    def emit(refs, text, grammar, *, phrased=(), covered_contexts=()):
        mentioned, qualifiers = related(refs)
        meaningful = {q for q in qualifiers if _qualifier_view(facts[q], locale, 'compact', subject_types)}
        additions = sorted({_qualifier_view(facts[q], locale, 'compact', subject_types) for q in meaningful} - set(phrased))
        mentioned.update(meaningful)
        row = {'locale': locale, 'resolution': 'compact', 'text': ' '.join([text, *additions]),
               'claim_refs': sorted(refs), 'represented_fact_refs': sorted(mentioned),
               'dependency_refs': [{'fact_ref': q, 'kind': facts[q]['fact_kind'],
                                    'projection': 'first_contact_scope' if q in meaningful else 'context'}
                                   for q in sorted(mentioned - refs)],
               'rule_ref': 'recovered_compact/2/' + grammar + '/' + locale, 'review_ref': review_ref}
        rows.append({'expression_id': expression.identity(row), **row})
        removable = set(refs) | meaningful | set(covered_contexts)
        for r in mentioned - removable:
            if facts[r]['fact_kind'] != 'use_context' or scopes({r}) == scopes(refs):
                removable.add(r)
        remaining.difference_update(removable)

    def find(kind, key, value):
        return {r for r in remaining if facts[r]['fact_kind'] == kind and facts[r]['payload'].get(key) == value}

    # Reading without a pen and writing with a pen are distinct contributions.
    viewing = find('direct_function', 'function', 'view_written_note_pages')
    writing = find('direct_function', 'function', 'record_written_notes')
    pages = find('effect', 'property', 'written_note_pages')
    titles = find('effect', 'property', 'written_note_title')
    locks = find('effect', 'property', 'written_note_lock')
    if viewing and writing and pages and titles and locks:
        refs = viewing | writing | pages | titles | locks
        note_scope = _qualifier_view(next(facts[q] for q in related(refs)[1]
                                         if facts[q]['payload']['predicate'] == recovery.NOTE_EDIT), locale, 'compact', subject_types)
        emit(refs, ('저장된 메모는 필기구 없이 읽을 수 있다. 다른 사용자의 잠금이 없고 자신의 편집 잠금도 풀면 필기구로 내용과 제목을 작성·저장할 수 있다. 편집 잠금을 설정하거나 해제할 수도 있다.' if locale == 'ko' else
                    'Stored notes can be read without a writing implement. With no other user holding the lock and its editing lock unlocked, pages and titles can be written and saved with a writing implement. The editing lock can also be set or removed.'),
             'note_read_write_lock', phrased=(note_scope,))

    eating = find('direct_function', 'function', 'eat_food') | find('direct_function', 'function', 'consume_edible_food')
    ingredients = {r for r in find('context_role', 'role', 'ingredient')
                   if facts[facts[r]['context_ref']]['payload'] == {'activity': 'food_preparation'}}
    if eating and ingredients and not scopes(eating | ingredients):
        emit(eating | ingredients, ('먹거나 요리 재료로 쓸 수 있다.' if locale == 'ko' else
                                    'It can be eaten or used as a cooking ingredient.'), 'food_and_ingredient')

    bait = find('direct_function', 'function', 'supply_trap_bait')
    bait_predicates = {facts[q]['payload']['predicate'] for q in related(bait)[1]}
    if bait and bait_predicates == {recovery_sources.FOOD_TRAP_BAIT}:
        emit(bait, ('추가 재료가 없는 익히지 않은 음식은 동물에 맞는 경우 설치된 덫의 미끼로 넣을 수 있다.' if locale == 'ko' else
                    'Uncooked food without added ingredients can bait a placed trap when accepted by the target animal.'),
             'eligible_trap_bait', phrased=scopes(bait))

    washing = find('direct_function', 'function', 'wash_carried_equipment')
    blood = {r for r in find('effect', 'property', 'item_surface_blood')
             if facts[r]['payload']['direction'] == 'remove_by_washing'}
    if washing and blood and scopes(washing) == scopes(blood):
        emit(washing | blood, ('물로 씻어 묻은 피를 지울 수 있다.' if locale == 'ko' else
                               'It can be washed with water to remove blood.'), 'washing_blood')

    # One proposition per function, with every supported target retained.
    # Only qualifiers authored into the combined sentence are discharged;
    # an additional/changed condition still accompanies its contributors.
    camp = [('모닥불', 'campfires')]
    hearth = [('프로판을 쓰지 않는 바비큐', 'non-propane barbecues'), ('벽난로', 'fireplaces')]
    drum = [('통나무가 든 드럼', 'drums containing logs')]

    def target_group(definitions):
        refs, labels, predicates = set(), [], set()
        for function, targets, predicate in definitions:
            matched = find('direct_function', 'function', function)
            if matched:
                refs.update(matched)
                labels.extend(targets)
                predicates.add(predicate)
        names = list(dict.fromkeys(pair[0 if locale == 'ko' else 1] for pair in labels))
        joined = ('' if not names else '·'.join(names) if locale == 'ko' else
                  names[0] if len(names) == 1 else
                  ' and '.join(names) if len(names) == 2 else ', '.join(names[:-1]) + ', and ' + names[-1])
        phrased = {_qualifier_view(facts[q], locale, 'compact', subject_types)
                   for q in related(refs)[1] if facts[q]['payload']['predicate'] in predicates}
        return refs, joined, phrased

    fuel, targets, phrased = target_group((
        ('supply_campfire_fuel', camp, recovery_sources.CAMP_FUEL_USE),
        ('supply_hearth_fuel', hearth, recovery_sources.HEARTH_FUEL),
        ('supply_furnace_fuel', [('연료가 부족한 화로', 'furnaces with fuel capacity remaining')], recovery_sources.FURNACE_FUEL),
    ))
    if fuel:
        emit(fuel, (targets + '의 연료로 소모할 수 있다.' if locale == 'ko' else
                    'It can be consumed as fuel for ' + targets + '.'), 'fuel_targets', phrased=phrased)

    tinder, targets, phrased = target_group((
        ('provide_campfire_tinder', camp, recovery_sources.CAMP_TINDER_USE),
        ('provide_hearth_tinder', hearth, recovery_sources.HEARTH_TINDER),
        ('provide_industrial_tinder', drum, recovery_sources.INDUSTRIAL_TINDER),
    ))
    if tinder:
        emit(tinder, ('점화 도구와 함께 불이 꺼진 ' + targets + '의 불쏘시개로 소모할 수 있다.' if locale == 'ko' else
                      'With a fire-starting item, it can be consumed as tinder for unlit ' + targets + '.'),
             'tinder_targets', phrased=phrased)

    friction, targets, phrased = target_group((
        ('light_campfire_by_friction', camp, recovery_sources.CAMP_FRICTION),
        ('kindle_heat_sources', [*hearth, *drum], recovery_sources.HEAT_FRICTION),
    ))
    if friction:
        emit(friction, ('연료가 있고 불이 꺼진 ' + targets + '의 마찰 점화에 쓸 수 있다. 구멍 낸 판자와 막대 또는 나뭇가지, 지구력이 필요하며 점화는 확률적이고 막대가 부서질 수 있다.' if locale == 'ko' else
                        'It can be used for friction lighting of fueled, unlit ' + targets + '. Notched wood, a stick or branch, and endurance are needed; ignition is random and the stick may break.'),
             'friction_targets', phrased=phrased)

    throwing = find('direct_function', 'function', 'request_physics_attack')
    if throwing:
        phrased = {_qualifier_view(facts[q], locale, 'compact', subject_types)
                   for q in related(throwing)[1] if facts[q]['payload']['predicate'] == recovery_sources.PHYSICS_ATTACK}
        emit(throwing, ('차량 밖에서 투척 공격에 사용할 수 있다.' if locale == 'ko' else
                        'It can be used for throwing attacks outside a vehicle.'), 'throwing_use', phrased=phrased)

    # These direct functions already say both the activity and this item's
    # role. Preserve all contributors while stating the proposition once.
    for activity, role, name in (
            ('battery_insertion', 'power_receiver', 'accept_battery_charge'),
            ('battery_removal', 'power_receiver', 'remove_device_battery'),
            ('electronic_salvage', 'transformation_target', 'dismantle_electronics')):
        direct = find('direct_function', 'function', name)
        roles = {r for r in find('context_role', 'role', role)
                 if facts[facts[r]['context_ref']]['payload'] == {'activity': activity}}
        for d in sorted(direct):
            same = {r for r in roles if scopes({r}) == scopes({d})}
            if activity == 'electronic_salvage':
                # SCRAP_RECOVERY states a result boundary, not an extra entry
                # prerequisite. It can accompany the shared operation once.
                result_view = QUALIFIER_VIEWS[recovery_sources.SCRAP_RECOVERY]['compact'][0 if locale == 'ko' else 1]
                same |= {r for r in roles if set(scopes({r})) <= set(scopes({d}))
                         and set(scopes({d})) - set(scopes({r})) == {result_view}}
            if same:
                emit({d} | same, cores[d], 'function_with_equivalent_context_role',
                     covered_contexts={facts[r]['context_ref'] for r in same})

    # Role clauses name their own context once. Equal projected conditions can
    # share a role sentence; a more restricted role cannot hide a broader use.
    groups = defaultdict(set)
    for r in sorted(remaining):
        f = facts[r]
        if f['fact_kind'] == 'context_role':
            groups[f['payload']['role'], scopes({r})].add(r)
    for (role, _), refs in sorted(groups.items()):
        activities = sorted({facts[facts[r]['context_ref']]['payload']['activity'] for r in refs})
        labels = list(dict.fromkeys(COMPACT_CONTEXTS[a][0 if locale == 'ko' else 1] for a in activities))
        text = _role_text(labels, role, locale)
        emit(refs, text, 'context_roles')
    specific_groups = defaultdict(set)
    for r in sorted(remaining):
        specific_groups[scopes({r})].add(r)
    for _, refs in sorted(specific_groups.items()):
        refs &= remaining
        if refs:
            emit(refs, ' '.join(dict.fromkeys(cores[r] for r in sorted(refs))), 'equal_scope_claims')
    represented = {r for row in rows for r in row['represented_fact_refs']}
    detail = selected - represented
    inv.require(all(r in details or facts[r]['fact_kind'] in {'condition', 'constraint'}
                    and _qualifier_view(facts[r], locale, 'compact', subject_types) is None for r in detail),
                'recovery compact contributor loss')
    return rows, sorted(detail - details.keys()), [{'fact_ref': r, 'reason': details[r]} for r in sorted(details)]


def normalize(semantic, acquisition, applications, contract):
    inv.require(semantic['status'] == acquisition['status'] == 'candidate', 'mixed candidate/adopted')
    inv.require(semantic['target_ids'] == acquisition['target_ids'], 'candidate target mismatch')
    facts, provenance = {}, {}
    for payload in (semantic, acquisition):
        aid = payload['authority_id']
        for fact in payload['facts']:
            ref = expression.qualify(aid, fact['fact_id'])
            inv.require(ref not in facts, 'duplicate qualified fact')
            facts[ref] = {'ref': ref, 'authority_ref': aid, 'fact_id': fact['fact_id'],
                          'item_id': fact['item_id'], 'fact_kind': fact['fact_kind'],
                          'payload': deepcopy(fact['payload']),
                          'provenance_refs': sorted(expression.qualify(aid, p) for p in fact['provenance_refs']),
                          'context_ref': expression.qualify(aid, fact['context_fact_ref']) if 'context_fact_ref' in fact else None,
                          'applies_to_refs': sorted(expression.qualify(aid, p) for p in fact.get('applies_to_fact_refs', [])),
                          'qualifier_refs': []}
            for p in fact['provenance_refs']:
                inv.require(p in payload['provenance'], 'missing provenance')
                provenance[expression.qualify(aid, p)] = deepcopy(payload['provenance'][p])
    for fact in facts.values():
        refs = fact['applies_to_refs'] + ([fact['context_ref']] if fact['context_ref'] else [])
        for ref in refs:
            inv.require(ref in facts and facts[ref]['item_id'] == fact['item_id']
                        and facts[ref]['authority_ref'] == fact['authority_ref'], 'broken correction reference')
        for ref in fact['applies_to_refs']:
            inv.require(facts[ref]['fact_kind'] not in {'condition', 'constraint'}, 'qualifier cycle')
            facts[ref]['qualifier_refs'].append(fact['ref'])
    for fact in facts.values():
        fact['qualifier_refs'].sort()
    return {'targets': semantic['target_ids'], 'facts': dict(sorted(facts.items())), 'subject_types': _subject_types(semantic),
            'provenance': dict(sorted(provenance.items())),
            'profiles': {p['profile_id']: p for p in contract['profiles']},
            'applications': inv.exact_rows(applications)}


def produce(inputs, bindings):
    facts = inputs['facts']
    subject_types = inputs['subject_types']
    island = {r for r, f in facts.items() if f['payload'] in
              ({'function': 'view_written_note_pages'}, {'predicate': recovery.NOTE_EDIT})
              or f['payload'].get('function') in recovery_sources.FUNCTIONS
              or (f['payload'].get('property'), f['payload'].get('direction')) in recovery_sources.EFFECTS
              or f['payload'].get('state') in {'worn_location', 'reading_page_count', 'skill_book_max_multiplier', 'skill_book_progress_step'}
              or f['payload'].get('predicate') in QUALIFIER_VIEWS}
    edges = defaultdict(set)
    for ref, fact in facts.items():
        for other in fact['applies_to_refs'] + ([fact['context_ref']] if fact['context_ref'] else []):
            edges[ref].add(other)
            edges[other].add(ref)
    pending = list(island)
    while pending:
        additions = edges[pending.pop()] - island
        pending.extend(additions)
        island.update(additions)
    inv.require(all(set(facts[r]['qualifier_refs']) <= island for r in island), 'note island has external qualifier')
    inv.require(all(not facts[r]['context_ref'] or facts[r]['context_ref'] in island for r in island), 'note island has external context')
    regular = deepcopy(inputs)
    regular['facts'] = {r: f for r, f in regular['facts'].items() if r not in island}
    regular['provenance'] = {r: p for r, p in regular['provenance'].items()
                             if any(r in f['provenance_refs'] for f in regular['facts'].values())}
    for app in regular['applications'].values():
        app['fact_question_bindings'] = [b for b in app['fact_question_bindings']
            if expression.qualify(b['authority_ref'], b['fact_ref']) not in island]
        # The pure composer reads resolved result contributors separately.
        for axis in app['required_axes']:
            result = axis.get('result')
            if result:
                result['fact_refs'] = [f for f in result.get('fact_refs', [])
                    if expression.qualify(result['authority_ref'], f) not in island]
    review = {'payload_domain_sha256': expression.selector_domain(regular),
              'locales': {loc: {'state': 'approved'} for loc in ('ko', 'en')},
              'review_boundary': 'Existing supported L3-05 rules; recovery groups use explicit source-reviewed bilingual rules.'}
    body = expression.produce(regular, review)
    # Pure composition's fixed envelope is an internal intermediate only.
    body['inputs'] = deepcopy(bindings)
    body['schema'] = 'iris-layer3-recovery-expression-v1'
    body['facts'] = [facts[r] for r in sorted(facts)]
    body['provenance'] = inputs['provenance']
    body['denominators']['facts'] = len(facts)
    body['denominators']['fact_locale_pairs'] = 2 * len(facts)
    body['completion'] = 'partial'
    regular_expressions = {e['expression_id']: e for e in body['expressions']}
    replaced_compact_ids = set()
    body['review_ref'] = expression.identity({'inputs': bindings, 'rule': 'recovered_meanings/1',
        'functions': recovery_sources.FUNCTIONS, 'function_views': FUNCTION_VIEWS,
        'qualifiers': QUALIFIER_VIEWS, 'projection_notes': PROJECTION_NOTES, 'contexts': CONTEXTS, 'roles': ROLES,
        'compact_contexts': COMPACT_CONTEXTS, 'detail_facts': sorted((list(k), v) for k, v in DETAIL_FACTS.items()),
        'effects': sorted((list(k), v) for k, v in {**recovery_sources.EFFECTS, **EFFECT_VIEWS}.items()),
        'body_locations': recovery_sources.BODY_LABELS})
    by_item = defaultdict(set)
    for ref in island:
        by_item[facts[ref]['item_id']].add(ref)
    for item in body['items']:
        item_id = item['item_id']
        app = inputs['applications'][item_id]
        profiles = expression._profiles(app, inputs)
        selected, obligations = expression._selection(app, facts)
        item['profiles'], item['first_contact_obligations'] = profiles, obligations
        for locale in ('ko', 'en'):
            rendered = item['locales'][locale]
            note_expressions = []
            cores = {}
            for ref in sorted(by_item[item_id]):
                fact = facts[ref]
                if fact['fact_kind'] in {'condition', 'constraint'}:
                    continue
                function = fact['payload'].get('function')
                contexts = [fact['context_ref']] if fact['context_ref'] else []
                qualifier_refs = sorted(set(fact['qualifier_refs']) |
                                        {q for c in contexts for q in facts[c]['qualifier_refs']})
                represented = sorted({ref, *contexts, *qualifier_refs})
                if function == 'view_written_note_pages':
                    text = ('저장된 메모 페이지를 열어 볼 수 있다. 필기구가 없어도 열람할 수 있다.' if locale == 'ko'
                            else 'Stored note pages can be viewed without a writing implement.')
                elif function == 'record_written_notes':
                    inv.require(function == 'record_written_notes', 'unsupported note function')
                    inv.require(any(facts[q]['payload'] == {'predicate': recovery.NOTE_EDIT}
                                    for q in fact['qualifier_refs']),
                                'missing note editing qualifier')
                    text = ('글을 적어 기록할 수 있다.' if locale == 'ko' else 'Written notes can be recorded.')
                else:
                    if fact['fact_kind'] == 'state':
                        state, value = fact['payload']['state'], fact['payload']['value']
                        if state == 'worn_location':
                            location = recovery_sources.BODY_LABELS[value][0 if locale == 'ko' else 1]
                            text = ('착용 위치는 ' + location + ' 자리다.' if locale == 'ko' else
                                    'It uses the ' + location + ' equipment slot.')
                        else:
                            inv.require(type(value) is int and value > 0, 'invalid reading parameter')
                            texts = {
                                'reading_page_count': (f'전체 쪽수는 {value}쪽이다.', f'The book has {value} pages.'),
                                'skill_book_max_multiplier': (f'이 책의 경험치 획득 배율은 최대 {value}배다.', f'This book provides an XP gain multiplier of up to {value}.'),
                                'skill_book_progress_step': (f'독서 진행 {value}% 단위로 경험치 배율을 계산한다.', f'The XP multiplier is calculated in {value}% reading-progress steps.'),
                            }
                            inv.require(state in texts, 'unsupported recovered state')
                            text = texts[state][0 if locale == 'ko' else 1]
                    elif fact['fact_kind'] == 'effect':
                        effect = (fact['payload']['property'], fact['payload']['direction'])
                        inv.require(effect in recovery_sources.EFFECTS, 'unsupported recovered effect')
                        pair = EFFECT_VIEWS.get(effect, recovery_sources.EFFECTS[effect])
                        inv.require(len(pair) == 2, 'recovery effect must have exactly two locales')
                        text = pair[0 if locale == 'ko' else 1]
                    else:
                        if function in recovery_sources.FUNCTIONS:
                            pair = FUNCTION_VIEWS.get(function, recovery_sources.FUNCTIONS[function][1:])
                            text = pair[0 if locale == 'ko' else 1]
                        elif fact['fact_kind'] in {'use_context', 'context_role'}:
                            text = _context_core(fact, facts, locale)
                        else:
                            text, core_contexts = expression_rules.core(fact, facts, locale)
                            inv.require(core_contexts == contexts, 'inconsistent role context')
                cores[ref] = text.rstrip('.') + '.'
                qualifier_texts = []
                for qualifier in qualifier_refs:
                    predicate = facts[qualifier]['payload']['predicate']
                    if function == 'record_written_notes' and predicate == recovery.NOTE_EDIT:
                        continue
                    view = _qualifier_view(facts[qualifier], locale, 'expanded', subject_types)
                    if view and view not in qualifier_texts:
                        qualifier_texts.append(view)
                text = ' '.join([cores[ref], *qualifier_texts])
                deps = [{'fact_ref': q, 'kind': facts[q]['fact_kind']} for q in [*contexts, *qualifier_refs]]
                row = {'locale': locale, 'resolution': 'expanded', 'text': text, 'claim_ref': ref,
                       'represented_fact_refs': represented, 'dependency_refs': deps,
                       'rule_ref': 'recovered_meanings/1/' + locale, 'review_ref': body['review_ref'] + '/' + locale}
                expanded = {'expression_id': expression.identity(row), **row}
                note_expressions.append(expanded)
            note_expressions = _coalesce_expanded(note_expressions, cores, facts, locale, body['review_ref'] + '/' + locale, subject_types)
            for expanded in note_expressions:
                for represented_ref in expanded['represented_fact_refs']:
                    rendered['fact_expressions'].setdefault(represented_ref, []).append(expanded['expression_id'])
            rendered['expanded'].extend(expression._blocks(note_expressions, profiles, facts))
            actual_refs = {r for e in note_expressions for r in e['represented_fact_refs']}
            inv.require(actual_refs == by_item[item_id], 'unsupported recovered expression group')
            rendered['expanded_represented_fact_refs'] = sorted(set(rendered['expanded_represented_fact_refs']) | actual_refs)
            s2 = rendered['s2']
            compact_expressions = []
            if by_item[item_id]:
                # Mixed old/new contributors share one first-contact grammar.
                # Supported cores still come from the historical pure rules;
                # unchanged acquisition units retain their existing realization.
                semantic_selected = {r for r in selected if facts[r]['fact_kind'] != 'acquisition'}
                for ref in expression._expand_qualifiers(semantic_selected, facts) - cores.keys():
                    f = facts[ref]
                    if f['fact_kind'] in {'condition', 'constraint'}:
                        continue
                    if f['fact_kind'] in {'context_role', 'use_context'}:
                        cores[ref] = _context_core(f, facts, locale)
                    else:
                        cores[ref] = expression_rules.core(f, facts, locale)[0].rstrip('.') + '.'
                compact_expressions, detail_qualifiers, detail_facts = _compact_recovery(
                    semantic_selected, facts, cores, locale, body['review_ref'] + '/' + locale, subject_types)
                retained = []
                for ref in s2['expression_refs']:
                    row = regular_expressions[ref]
                    if all(facts[r]['fact_kind'] == 'acquisition' for r in row['claim_refs']):
                        retained.append(row)
                    else:
                        replaced_compact_ids.add(ref)
                all_compact = [*retained, *compact_expressions]
                s2.update(text=' '.join(e['text'] for e in all_compact), logical_rows=int(bool(all_compact)),
                    expression_refs=[e['expression_id'] for e in all_compact],
                    represented_fact_refs=sorted({r for e in all_compact for r in e['represented_fact_refs']}),
                    dependency_refs=sorted({expression.canonical(d): d for e in all_compact for d in e['dependency_refs']}.values(), key=expression.canonical),
                    detail_qualifier_refs=detail_qualifiers, detail_fact_omissions=detail_facts,
                    state='expressed' if all_compact else ('upstream_gap' if any(o['state'] == 'upstream_gap' for o in obligations) else 'no_first_contact'))
            rendered['tooltip_detail_omission_refs'] = sorted(set(rendered['expanded_represented_fact_refs']) - set(s2['represented_fact_refs']))
            body['expressions'].extend([*note_expressions, *compact_expressions])
    body['expressions'] = [e for e in body['expressions'] if e['expression_id'] not in replaced_compact_ids]
    body['expressions'].sort(key=lambda e: e['expression_id'])
    return body


def prepare(base, semantic, bindings):
    acquisition = deepcopy(base['acquisition'])
    applications = combined.consume_payloads(semantic, acquisition, base['contract'], base['inherited'],
                                             bindings['semantic'], bindings['acquisition'])
    inputs = normalize(semantic, acquisition, applications, base['contract'])
    return produce(inputs, bindings), applications
