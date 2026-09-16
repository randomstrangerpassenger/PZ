"""Meaning extraction from the bound predecessor, separate from fact admission.

Only reviewed prose forms receive atoms. Sentence boundaries merely delimit
review work: an unknown sentence remains unsegmented, even if its item already
has accepted facts. All spans use the original Unicode text, before trimming.
"""
import re
from collections import defaultdict

from . import semantic_model as model
from . import recovery_sources as sources
from . import semantic_results as semantic
from . import acquisition_expression


# Named learning claims retain each independent subject and the declaration
# entries it would require. This is prose decomposition, not proof of learning.
LEARNING_TOPICS = {
    'cake_dough': ('Make Cake Batter',), 'pie_dough': ('Make Pie Dough',),
    'cookie_dough': ('Make Chocolate Chip Cookie Dough', 'Make Chocolate Cookie Dough', 'Make Oatmeal Cookie Dough', 'Make Sugar Cookie Dough', 'Make Shortbread Cookie Dough'),
    'bread_dough': ('Make Bread Dough',), 'biscuits': ('Make Biscuits',), 'pizza': ('Make Pizza',),
    'remote_controllers': ('Make Remote Controller V1', 'Make Remote Controller V2', 'Make Remote Controller V3'),
    'make_timer': ('Make Timer',), 'attach_timer': ('Add Timer',),
    'motion_sensors': ('Add Motion Sensor V1', 'Add Motion Sensor V2', 'Add Motion Sensor V3'),
    'make_remote_trigger': ('Make Remote Trigger',), 'attach_remote_trigger': ('Add Crafted Trigger',),
    'noise_maker': ('Make Noise Maker',), 'smoke_bomb': ('Make Smoke Bomb',),
    'mildew_spray': ('Make Mildew Cure',), 'pest_spray': ('Make Flies Cure',),
    'make_fishing_rod': ('Make Fishing Rod',), 'repair_fishing_rod': ('Fix Fishing Rod',),
    'fishing_net': ('Make Fishing Net',), 'reclaim_net_wire': ('Get Wire Back',),
    'snare_trap': ('Make Snare Trap',), 'wooden_box_trap': ('Make Wooden Box Trap',),
    'stick_trap': ('Make Stick Trap',), 'box_trap': ('Make Trap Box',), 'cage_trap': ('Make Cage Trap',),
    'metal_walls': ('Make Metal Walls',), 'metal_roof': ('Make Metal Roof',),
    'metal_containers': ('Make Metal Containers',), 'metal_fences': ('Make Metal Fences',),
    'metal_sheets': ('Make Metal Sheet', 'Make Small Metal Sheet'),
    'metal_cutlery': ('Make Fork', 'Make Spoon'),
    'metal_cookware': ('Make Cooking Pot', 'Make Roasting Pan', 'Make Saucepan', 'Make Baking Tray', 'Make Baking Pan', 'Make Pan'),
    'nails': ('Make Nails',), 'hinges': ('Make Hinge',),
    'small_metal_tools': ('Make Letter Opener', 'Make Scissors', 'Make Butter Knife', 'Make Ball Peen Hammer'),
    'metal_tools': ('Make Tongs', 'Make Hammer', 'Make Suture Needle Holder', 'Make Tweezers', 'Make Suture Needle', 'Make Kitchen Knife', 'Make Saw', 'Make Hunting Knife', 'Make Shovel', 'Make Hand Shovel'),
    'smithing_containers': ('Make Metal Drum',),
    'ammunition': ('Make 9mm Bullets', 'Make Shotgun Shells', 'Make 308 Bullets', 'Make 223 Bullets'),
    'ammunition_molds': ('Make 9mm Bullets Mold', 'Make 308 Bullets Mold', 'Make 223 Bullets Mold', 'Make Shotgun Shells Mold'),
    'metal_weapons': ('Make Crowbar', 'Make Golfclub', 'Make Axe', 'Make Sledgehammer'),
}

# Exact clauses with one proposition. The predicate names are migration audit
# vocabulary, not new fact kinds or a source interpretation authority.
CLAUSES = {
    '바벨 컬 운동에 사용하는 운동기구다': [('function', 'exercise_barbell_curl')],
    'Exercise equipment used for barbell curls': [('function', 'exercise_barbell_curl')],
    '덤벨 프레스와 바이셉스 컬 운동에 사용하는 운동기구다': [('function', 'exercise_dumbbell_press'), ('function', 'exercise_biceps_curl')],
    'Exercise equipment used for dumbbell presses and biceps curls': [('function', 'exercise_dumbbell_press'), ('function', 'exercise_biceps_curl')],
    '근접 전투에 쓰는 무기다': [('function', 'melee_attack')],
    'A weapon used in close combat': [('function', 'melee_attack')],
    'A tool that can be used for melee attacks': [('function', 'melee_attack')],
    '차량 제동에 쓰는 브레이크 부품이다': [('effect', 'vehicle_braking', 'affect')],
    'A brake component used for vehicle braking': [('effect', 'vehicle_braking', 'affect')],
    '차량 타이어의 공기압을 조절할 때 사용된다': [('function', 'adjust_vehicle_tire_pressure')],
    'Used to adjust the air pressure in vehicle tires': [('function', 'adjust_vehicle_tire_pressure')],
    '독성이 있다': [('hazard', 'food_poison')],
    '머리나 얼굴에 착용하는 의류다': [('wear', 'head_or_face')],
    '오른쪽 손목에 착용할 수 있다': [('wear', 'right_wrist')],
    '왼쪽 눈에 착용할 수 있다': [('wear', 'left_eye')],
    '오른쪽 눈에 착용할 수 있다': [('wear', 'right_eye')],
    '눈에 착용할 수 있다': [('wear', 'eyes')],
    '목에 착용할 수 있다': [('wear', 'neck_accessory')],
    '코에 착용할 수 있다': [('wear', 'nose')],
    'Equipment worn over the face and eyes': [('wear', 'face_and_eyes')],
    'Clothing worn over the whole body': [('wear', 'whole_body')],
    'Equipment worn at the waist': [('wear', 'waist_equipment')],
    'Long underwear worn on the upper and lower body': [('wear', 'whole_body')],
    'Long underwear worn on the lower body': [('wear', 'long_underwear_legs')],
    'Outerwear worn on the body': [('wear', 'outerwear')],
    'Socks worn on the feet': [('wear', 'socks')],
    'Clothing worn on or around the body': [('function', 'wear_body')],
    '군용품점과 캠핑, 사냥 장비 보관 장소, 생존 차량에서 발견된다': [('acquisition_place', 'military-surplus stores'), ('acquisition_place', 'camping areas'), ('acquisition_place', 'hunting-equipment storage'), ('acquisition_place', 'survival vehicles')],
    '군과 경찰 보관 장소, 총기점과 작업 현장에서 발견된다': [('acquisition_place', 'military areas'), ('acquisition_place', 'police storage'), ('acquisition_place', 'gun stores'), ('acquisition_place', 'work sites')],
    '군용과 소방 보관 장소, 실험 시설에서 발견된다': [('acquisition_place', 'military areas'), ('acquisition_place', 'fire-department storage'), ('acquisition_place', 'laboratories')],
    '겨울 의류와 생존 장비 보관 장소, 소방 차량에서 발견된다': [('acquisition_place', 'winter-clothing areas'), ('acquisition_place', 'survival-equipment storage'), ('acquisition_place', 'fire-department vehicles')],
    '겨울 의류와 생존 장비 보관 장소에서 발견된다': [('acquisition_place', 'winter-clothing areas'), ('acquisition_place', 'survival-equipment storage')],
    '경찰과 경비 보관 장소에서 발견된다': [('acquisition_place', 'police areas'), ('acquisition_place', 'security-guard storage')],
    '군용과 소방 보관 장소, 캠핑과 사냥 장비 보관 장소에서 발견된다': [('acquisition_place', 'military areas'), ('acquisition_place', 'fire-department storage'), ('acquisition_place', 'camping areas'), ('acquisition_place', 'hunting-equipment storage')],
    '겨울 의류와 캠핑 장비 보관 장소에서 발견된다': [('acquisition_place', 'winter-clothing areas'), ('acquisition_place', 'camping-equipment storage')],
    '불을 끄는 데 사용할 수 있는 흙 포대다': [('function', 'extinguish_fire'), ('material_form', 'bag_of_dirt')],
    'A bag of dirt that can be used to put out fires': [('function', 'extinguish_fire'), ('material_form', 'bag_of_dirt')],
    '흙을 담아 얻는다': [('acquisition_process', 'fill_ground_bag', 'dirt')],
    'Obtained by filling it with soil': [('acquisition_process', 'fill_ground_bag', 'dirt')],
    '자갈을 담아 얻는다': [('acquisition_process', 'fill_ground_bag', 'gravel')],
    'Obtained by filling it with gravel': [('acquisition_process', 'fill_ground_bag', 'gravel')],
    '모래를 담아 얻는다': [('acquisition_process', 'fill_ground_bag', 'sand')],
    'Obtained by filling it with sand': [('acquisition_process', 'fill_ground_bag', 'sand')],
    '사무용품과 학용품 보관 장소, 의료 작업 장소에서 발견된다': [('acquisition_place', 'office-supply storage'), ('acquisition_place', 'school-supply storage'), ('acquisition_place', 'medical work areas')],
    'Found with office supplies, school-supply storage, and medical work areas': [('acquisition_place', 'office-supply storage'), ('acquisition_place', 'school-supply storage'), ('acquisition_place', 'medical work areas')],
    '창문이나 난간 등에 설치해 오르내리는 데 쓰는 천 로프다': [('identity_label', '천 로프'), ('function', 'supply_escape_rope'), ('function', 'traverse_installed_rope')],
    'A sheet rope installed at suitable windows or railings for climbing': [('identity_label', '천 로프'), ('function', 'supply_escape_rope'), ('function', 'traverse_installed_rope')],
    '시트나 면 의류를 찢어 만든다': [('acquisition_process', 'craft_sheet_rope_from_sheet_or_cotton')],
    'Made by tearing sheets or cotton clothing': [('acquisition_process', 'craft_sheet_rope_from_sheet_or_cotton')],
    '철조망 울타리를 만드는 목공 작업 중 사용된다': [('role', 'barbed_fence_construction', 'material')],
    'Used in carpentry work to build barbed-wire fences': [('role', 'barbed_fence_construction', 'material')],
    '서랍 달린 작은 탁자를 만드는 데 쓰는 부품이다': [('role', 'drawer_table_construction', 'material')],
    'A component used to build a small table with a drawer': [('role', 'drawer_table_construction', 'material')],
    '문이나 서랍을 만드는 데 쓰는 손잡이 부품이다': [('identity_label', '손잡이 부품'), ('role', 'door_construction', 'material'), ('role', 'furniture_crafting', 'material')],
    'A handle component used to build doors or drawers': [('identity_label', '손잡이 부품'), ('role', 'door_construction', 'material'), ('role', 'furniture_crafting', 'material')],
    '문이나 게이트 등 경첩이 필요한 구조물을 만들 때 사용된다': [('role', 'hinged_structure_construction', 'material')],
    'Used to build structures that require hinges, such as doors or gates': [('role', 'hinged_structure_construction', 'material')],
    '돌망치를 만드는 재료로 쓰는 돌이다': [('identity_label', '돌'), ('role', 'stone_hammer_crafting', 'material')],
    'A stone used to make a stone hammer': [('identity_label', '돌'), ('role', 'stone_hammer_crafting', 'material')],
    '침대를 만드는 데 쓰는 재료다': [('role', 'bed_construction', 'material')],
    'A material used to build a bed': [('role', 'bed_construction', 'material')],
    '재봉에 쓰는 바늘이다': [('function', 'sew_fabric')],
    'A needle used for sewing': [('function', 'sew_fabric')],
    '의류를 수선하거나 가죽 패치를 덧대 보강할 때 사용된다': [('function', 'apply_garment_patch'), ('effect', 'garment_protection', 'increase'), ('material_form', 'leather_patch')],
    'Used to mend clothing or reinforce it with leather patches': [('function', 'apply_garment_patch'), ('effect', 'garment_protection', 'increase'), ('material_form', 'leather_patch')],
    '청소 도구와 함께 혈흔을 지우는 데 쓰는 유독성 표백제다': [('function', 'clean_world_blood'), ('condition', 'blood_cleaning', 'bleach_and_tool'), ('hazard', 'toxic_bleach')],
    'Toxic bleach used with cleaning tools to remove blood stains': [('function', 'clean_world_blood'), ('condition', 'blood_cleaning', 'bleach_and_tool'), ('hazard', 'toxic_bleach')],
    'Use on a blood-stained area with a mop, an unbroken broom, a dish towel or a bath towel': [('condition', 'blood_cleaning', 'bleach_and_tool')],
    'Cleaning consumes bleach': [('consumption_property', 'blood_cleaning', 'bleach_used')],
    '부러지지 않았다면 재를 쓸어낼 수 있고, 표백제와 함께 쓰면 혈흔도 지울 수 있다': [('function', 'clear_burnt_floor_ashes'), ('condition', 'ash_clearing', 'unbroken_broom'), ('function', 'clean_world_blood'), ('condition', 'blood_cleaning', 'bleach_and_tool')],
    "If it isn't broken, use it to sweep up ashes or, with bleach, clean blood stains": [('function', 'clear_burnt_floor_ashes'), ('condition', 'ash_clearing', 'unbroken_broom'), ('function', 'clean_world_blood'), ('condition', 'blood_cleaning', 'bleach_and_tool')],
    'Clearing ashes requires an unbroken broom': [('condition', 'ash_clearing', 'unbroken_broom')],
    'To remove blood stains, also carry bleach and use the cleaning option on a blood-stained area': [('condition', 'blood_cleaning', 'bleach_and_tool')],
    '표백제와 함께 쓰면 혈흔을 지울 수 있다': [('function', 'clean_world_blood'), ('condition', 'blood_cleaning', 'bleach_and_tool')],
    'With bleach, you can remove blood stains': [('function', 'clean_world_blood'), ('condition', 'blood_cleaning', 'bleach_and_tool')],
    'Carry bleach as well and use the cleaning option on a blood-stained area': [('condition', 'blood_cleaning', 'bleach_and_tool')],
    '섭취하면 허기와 갈증을 줄일 수 있고 요리 재료로도 사용할 수 있다': [('effect', 'hunger', 'decrease'), ('effect', 'thirst', 'decrease'), ('role', 'food_preparation', 'ingredient')],
    '샐러드·과일 샐러드는 그릇과 사과를 소지하고 그릇의 만들기 메뉴에서 사과를 넣는다': [('recipe_relation', 'Salad', 'ingredient'), ('recipe_relation', 'FruitSalad', 'ingredient'), ('recipe_requirement', 'Salad', 'Bowl_and_Apple_in_inventory'), ('recipe_requirement', 'FruitSalad', 'Bowl_and_Apple_in_inventory'), ('recipe_menu', 'Salad', 'bowl_preparation'), ('recipe_menu', 'FruitSalad', 'bowl_preparation')],
    "For salad or fruit salad, carry a bowl and an apple and add the apple through the bowl's preparation menu": [('recipe_relation', 'Salad', 'ingredient'), ('recipe_relation', 'FruitSalad', 'ingredient'), ('recipe_requirement', 'Salad', 'Bowl_and_Apple_in_inventory'), ('recipe_requirement', 'FruitSalad', 'Bowl_and_Apple_in_inventory'), ('recipe_menu', 'Salad', 'bowl_preparation'), ('recipe_menu', 'FruitSalad', 'bowl_preparation')],
    '케이크는 케이크 반죽을 베이킹 팬에 담아 만든 준비된 케이크에, 단 파이는 파이 반죽·베이킹 팬·밀대로 만든 준비된 파이에 넣는다': [('recipe_relation', 'Cake', 'ingredient'), ('recipe_relation', 'PieSweet', 'ingredient'), ('recipe_preparation', 'Cake', 'CakeBatter_BakingPan'), ('recipe_preparation', 'PieSweet', 'PieDough_BakingPan_RollingPin')],
    'For cake, add it to cake batter placed in a baking pan; for sweet pie, add it to pie dough prepared with a baking pan and rolling pin': [('recipe_relation', 'Cake', 'ingredient'), ('recipe_relation', 'PieSweet', 'ingredient'), ('recipe_preparation', 'Cake', 'CakeBatter_BakingPan'), ('recipe_preparation', 'PieSweet', 'PieDough_BakingPan_RollingPin')],
    '머핀은 반죽이 담긴 머핀 쟁반에 넣으며, 팬케이크·와플·오트밀은 해당 음식을 준비한 뒤 재료 추가 메뉴에서 넣는다': [('recipe_relation', 'Muffin', 'ingredient'), ('recipe_preparation', 'Muffin', 'batter_tray'), ('recipe_relation', 'Pancakes', 'ingredient'), ('recipe_relation', 'Waffles', 'ingredient'), ('recipe_relation', 'Oatmeal', 'ingredient'), ('recipe_menu', 'Pancakes', 'prepared_food_add_ingredient'), ('recipe_menu', 'Waffles', 'prepared_food_add_ingredient'), ('recipe_menu', 'Oatmeal', 'prepared_food_add_ingredient')],
    'For muffins, use a tray containing muffin batter': [('recipe_relation', 'Muffin', 'ingredient'), ('recipe_preparation', 'Muffin', 'batter_tray')],
    'For pancakes, waffles or oatmeal, prepare that food first and use its add-ingredient menu': [('recipe_relation', 'Pancakes', 'ingredient'), ('recipe_relation', 'Waffles', 'ingredient'), ('recipe_relation', 'Oatmeal', 'ingredient'), ('recipe_menu', 'Pancakes', 'prepared_food_add_ingredient'), ('recipe_menu', 'Waffles', 'prepared_food_add_ingredient'), ('recipe_menu', 'Oatmeal', 'prepared_food_add_ingredient')],
    '추가 재료 한도는 샐러드류 6개, 케이크·단 파이 4개, 팬케이크·와플·오트밀 3개, 머핀 1개다': [('recipe_limit', 'Salad', '6'), ('recipe_limit', 'FruitSalad', '6'), ('recipe_limit', 'Cake', '4'), ('recipe_limit', 'PieSweet', '4'), ('recipe_limit', 'Pancakes', '3'), ('recipe_limit', 'Waffles', '3'), ('recipe_limit', 'Oatmeal', '3'), ('recipe_limit', 'Muffin', '1')],
    'Ingredient limits are six for salads, four for cake or sweet pie, three for pancakes, waffles or oatmeal, and one for muffins': [('recipe_limit', 'Salad', '6'), ('recipe_limit', 'FruitSalad', '6'), ('recipe_limit', 'Cake', '4'), ('recipe_limit', 'PieSweet', '4'), ('recipe_limit', 'Pancakes', '3'), ('recipe_limit', 'Waffles', '3'), ('recipe_limit', 'Oatmeal', '3'), ('recipe_limit', 'Muffin', '1')],
    '케이크·단 파이·머핀은 재료를 넣은 뒤 굽는다': [('recipe_sequence', 'Cake', 'bake_after_addition'), ('recipe_sequence', 'PieSweet', 'bake_after_addition'), ('recipe_sequence', 'Muffin', 'bake_after_addition')],
    'Bake cake, sweet pie and muffins after adding ingredients': [('recipe_sequence', 'Cake', 'bake_after_addition'), ('recipe_sequence', 'PieSweet', 'bake_after_addition'), ('recipe_sequence', 'Muffin', 'bake_after_addition')],
    '이동 계획 작업에서 위치를 확인하려고 펼쳐 볼 때 참고한다': [('function', 'view_item_map'), ('intended_use', 'navigation_planning')],
    'Opened and referenced to check a location while planning travel': [('function', 'view_item_map'), ('intended_use', 'navigation_planning')],
    '미끼와 함께 설치해 토끼나 다람쥐를 잡는 데 쓰는 덫이다': [('function', 'place_animal_trap'), ('function', 'catch_trap_animal'), ('condition', 'animal_trapping', 'bait'), ('eligible_animal', 'rabbit'), ('eligible_animal', 'squirrel')],
    'A baited trap used to catch rabbits or squirrels': [('function', 'catch_trap_animal'), ('condition', 'animal_trapping', 'bait'), ('eligible_animal', 'rabbit'), ('eligible_animal', 'squirrel')],
    '사과나 옥수수 등 대상 동물이 먹는 미끼를 넣는다': [('condition', 'animal_trapping', 'accepted_bait'), ('bait_example', 'apple'), ('bait_example', 'corn')],
    'Add bait accepted by the target animal, such as an apple or corn': [('condition', 'animal_trapping', 'accepted_bait'), ('bait_example', 'apple'), ('bait_example', 'corn')],
    '토끼와 다람쥐는 야간에 포획 대상이 되며, 지역·미끼 신선도·플레이어 접근 여부에 따라 포획이 제한된다': [('animal_time', 'rabbit', 'night'), ('animal_time', 'squirrel', 'night'), ('condition', 'animal_trapping', 'zone'), ('condition', 'animal_trapping', 'bait_freshness'), ('condition', 'animal_trapping', 'player_proximity')],
    'Rabbits and squirrels are eligible at night; location, bait freshness and player proximity restrict catches': [('animal_time', 'rabbit', 'night'), ('animal_time', 'squirrel', 'night'), ('condition', 'animal_trapping', 'zone'), ('condition', 'animal_trapping', 'bait_freshness'), ('condition', 'animal_trapping', 'player_proximity')],
    '시간대 제한은 없지만 지역·미끼 신선도·플레이어 접근 여부에 따라 포획이 제한된다': [('condition', 'animal_trapping', 'no_time_limit'), ('condition', 'animal_trapping', 'zone'), ('condition', 'animal_trapping', 'bait_freshness'), ('condition', 'animal_trapping', 'player_proximity')],
    '호환되는 장치와 연결해 원격으로 작동시키는 조종기다': [('function', 'link_remote_device'), ('function', 'trigger_linked_device'), ('condition', 'remote_trigger', 'compatible_linked_device')],
    'A controller used to remotely trigger compatible linked devices': [('function', 'trigger_linked_device'), ('condition', 'remote_trigger', 'compatible_linked_device')],
    '묶음을 풀어 통나무를 꺼낼 수 있다': [('function', 'unbundle_logs'), ('output_identity', 'logs')],
    'A vehicle seat used for sitting or holding items': [('function', 'sit_in_vehicle'), ('function', 'store_vehicle_items')],
    '먹거나 그릇에 나누어 담을 수 있는 국물 요리다': [('function', 'eat_food'), ('function', 'portion_into_bowls'), ('identity_label', 'soup_or_stew')],
    'Obtained by processing electronic parts': [('acquisition_process', 'process_electronic_parts')],
    '왼손 약지에 착용할 수 있다': [('wear', 'left_ring_finger')],
    '오른손 약지에 착용할 수 있다': [('wear', 'right_ring_finger')],
    'Crafted from electronic scrap, radio parts, wire, and aluminum': [('acquisition_process', 'craft'), ('acquisition_material', 'electronic_scrap'), ('acquisition_material', 'radio_parts'), ('acquisition_material', 'wire'), ('acquisition_material', 'aluminum')],
    '읽으면 해당 임시 무선기기의 제작법을 배운다': [('function', 'read_literature'), ('effect', 'makeshift_radio_recipe_knowledge', 'gain')],
    'Reading it teaches the corresponding makeshift radio recipe': [('function', 'read_literature'), ('effect', 'makeshift_radio_recipe_knowledge', 'gain')],
    'A tray of batter used to bake muffins and remove them as portions': [('function', 'bake_muffins'), ('function', 'remove_portioned_muffins'), ('condition', 'remove_muffins', 'after_baking'), ('state_label', 'batter_filled_muffin_tray')],
    "If you're wet and it has uses remaining, you can dry off with it": [('function', 'dry_the_body'), ('condition', 'body_drying', 'wet_body'), ('condition', 'body_drying', 'uses_remaining')],
    'A wet towel that can be used to dry the body again once it has dried': [('function', 'dry_towel'), ('function', 'dry_the_body'), ('condition', 'body_drying', 'after_towel_dries'), ('state_label', 'wet_towel')],
    '맥주를 따라 얻는다': [('acquisition_process', 'pour_beer')],
    'Obtained by pouring beer': [('acquisition_process', 'pour_beer')],
    '재료를 섞어 얻는다': [('acquisition_process', 'mix_ingredients')],
    'Obtained by mixing ingredients': [('acquisition_process', 'mix_ingredients')],
    'Reading material that can reduce boredom, stress and unhappiness': [('function', 'read_literature'), ('conditional_effect', 'boredom', 'decrease', 'reading'), ('conditional_effect', 'stress', 'decrease', 'reading'), ('conditional_effect', 'unhappiness', 'decrease', 'reading')],
    'A cleanser used when washing blood and dirt from the body or clothing': [('function', 'wash_body'), ('function', 'wash_clothing'), ('effect', 'blood', 'remove'), ('effect', 'dirt', 'remove')],
    'Perfume used to add fragrance to the body': [('effect', 'body_scent', 'add')],
    'A material': [('role_unspecified_context', 'material')],
    'Cloth material used to bandage wounds or make some tools and splints': [('function', 'apply_bandage'), ('role', 'tool_crafting', 'material'), ('role', 'splint_crafting', 'material')],
    'Camping equipment': [('context_label', 'camping')],
    '물고기를 손질해 얻는다': [('acquisition_process', 'prepare_fish')],
    'Obtained by preparing a fish': [('acquisition_process', 'prepare_fish')],
    'An artificial lure used when fishing with a rod': [('state_label', 'artificial_lure'), ('function', 'bait_rod_fishing')],
    '포획은 보장되지 않고 루어가 파손될 수 있다': [('constraint', 'fishing_outcome', 'catch_not_guaranteed'), ('effect', 'fishing_lure', 'may_break')],
    'A catch is not guaranteed, and the lure can break': [('constraint', 'fishing_outcome', 'catch_not_guaranteed'), ('effect', 'fishing_lure', 'may_break')],
    '포대 장벽을 만들거나 불을 끄는 데 쓰는 재료다': [('role', 'bag_barrier_construction', 'material'), ('function', 'extinguish_fire')],
    'A material used to build bag barriers or put out fires': [('role', 'bag_barrier_construction', 'material'), ('function', 'extinguish_fire')],
    'Made by boiling pasta': [('acquisition_process', 'boil_pasta')],
    '쌀을 끓여 만든다': [('acquisition_process', 'boil_rice')],
    'Made by boiling rice': [('acquisition_process', 'boil_rice')],
    '구조물을 파괴하는 데 사용하는 도구다': [('function', 'destroy_structure')],
    '덫 및 어망 제작 작업에 들어가는 재료다': [('role', 'trap_crafting', 'material'), ('role', 'fishing_net_crafting', 'material')],
    'Material used to make traps and fishing nets': [('role', 'trap_crafting', 'material'), ('role', 'fishing_net_crafting', 'material')],
    'A television used to watch broadcasts or play recorded VHS tapes': [('function', 'watch_broadcasts'), ('function', 'play_vhs_recording')],
    '분무기를 조합해 얻는다': [('acquisition_process', 'assemble_gardening_spray')],
    'Obtained by assembling a gardening spray can': [('acquisition_process', 'assemble_gardening_spray')],
    '작물의 흰가루병 수준을 낮추는 데 쓰는 분무액이다': [('function', 'treat_crop_mildew'), ('effect', 'crop_mildew_level', 'decrease')],
    'A spray used to reduce mildew in crops': [('function', 'treat_crop_mildew'), ('effect', 'crop_mildew_level', 'decrease')],
    '작물의 해충 수준을 낮추는 데 쓰는 분무액이다': [('function', 'treat_crop_flies'), ('effect', 'crop_flies_level', 'decrease')],
    'A spray used to reduce flies affecting crops': [('function', 'treat_crop_flies'), ('effect', 'crop_flies_level', 'decrease')],
    '흰가루병이 있는 작물의 문제 처리 메뉴에서 사용량을 고른다': [('condition', 'crop_spray', 'mildew_menu_and_amount')],
    'Choose an amount in the treat-problem menu for a crop with mildew': [('condition', 'crop_spray', 'mildew_menu_and_amount')],
    '해충이 있는 작물의 문제 처리 메뉴에서 사용량을 고른다': [('condition', 'crop_spray', 'flies_menu_and_amount')],
    'Choose an amount in the treat-problem menu for a crop with flies': [('condition', 'crop_spray', 'flies_menu_and_amount')],
    '분무액의 남은 사용량이 필요하며, 다른 병을 함께 치료하는 분무액은 아니다': [('condition', 'crop_spray', 'remaining_uses'), ('constraint', 'crop_spray', 'specific_disease_only')],
    'The spray needs remaining uses; it is not a treatment for other crop diseases': [('condition', 'crop_spray', 'remaining_uses'), ('constraint', 'crop_spray', 'specific_disease_only')],
    '분무액의 남은 사용량이 필요하며, 흰가루병은 별도 분무액으로 처리한다': [('condition', 'crop_spray', 'remaining_uses'), ('constraint', 'crop_spray', 'mildew_uses_separate_spray')],
    'The spray needs remaining uses; mildew uses a separate spray': [('condition', 'crop_spray', 'remaining_uses'), ('constraint', 'crop_spray', 'mildew_uses_separate_spray')],
    '물을 담거나 작물용 치료 분무액을 만드는 데 쓰는 빈 용기다': [('function', 'store_water'), ('role', 'crop_spray_preparation', 'material')],
    'An empty container used to hold water or prepare crop-treatment sprays': [('function', 'store_water'), ('role', 'crop_spray_preparation', 'material')],
    '물을 담아 보관하고 공급하는 분무 용기다': [('function', 'store_water'), ('function', 'pour_water_into_container')],
    'A spray container used to store and supply water': [('function', 'store_water'), ('function', 'pour_water_into_container')],
    '분무기에 약품을 채워 얻는다': [('acquisition_process', 'fill_spray_with_chemicals')],
    'Obtained by filling a spray can with chemicals': [('acquisition_process', 'fill_spray_with_chemicals')],
    '양동이에 물을 담아 만든다': [('acquisition_process', 'fill_water'), ('condition', 'fill_water', 'empty_container')],
    'Made by filling a bucket with water': [('acquisition_process', 'fill_water'), ('condition', 'fill_water', 'empty_container')],
    '물 양동이를 비워 구한다': [('acquisition_process', 'empty_water_bucket')],
    'Obtained by emptying a bucket of water': [('acquisition_process', 'empty_water_bucket')],
    '불이 붙은 곳이나 캐릭터의 불을 끄는 데 쓰는 소화기다': [('function', 'extinguish_fire')],
    'An extinguisher used to put out fires on squares or characters': [('function', 'extinguish_fire')],
    '헤어스프레이와 불꽃놀이 재료를 조합해 만든다': [('acquisition_process', 'assemble'), ('acquisition_material', 'hairspray'), ('acquisition_material', 'fireworks_material')],
    'Made by combining hairspray and fireworks material': [('acquisition_process', 'assemble'), ('acquisition_material', 'hairspray'), ('acquisition_material', 'fireworks_material')],
    '작물의 다음 성장 단계까지 걸리는 시간을 줄이는 데 쓰는 비료다': [('function', 'apply_fertilizer'), ('effect', 'crop_growth_schedule', 'advance')],
    "Fertilizer used to shorten the time to a crop's next growth stage": [('function', 'apply_fertilizer'), ('effect', 'crop_growth_schedule', 'advance')],
    '살아 있는 작물의 비료 주기 메뉴에서 사용한다': [('condition', 'fertilizing', 'living_crop'), ('condition', 'fertilizing', 'farming_menu')],
    'Use the fertilize option on a living crop': [('condition', 'fertilizing', 'living_crop'), ('condition', 'fertilizing', 'farming_menu')],
    '이미 준 비료 횟수에 따라 결과가 달라지며, 지나치게 주면 작물이 썩는다': [('condition', 'fertilizing_outcome', 'previous_applications'), ('effect', 'crop_state', 'set_rotten'), ('condition', 'crop_rot', 'excess_fertilizer')],
    'The result depends on previous applications; excessive fertilizer rots the crop': [('condition', 'fertilizing_outcome', 'previous_applications'), ('effect', 'crop_state', 'set_rotten'), ('condition', 'crop_rot', 'excess_fertilizer')],
    'A container used to carry water': [('function', 'carry_water')],
    'An item that can be used for melee attacks': [('function', 'melee_attack')],
    'A part used to modify firearms': [('function', 'attach_weapon_part')],
    '찌르는 근접 공격에 쓰는 창이다': [('identity_label', 'spear'), ('function', 'melee_attack'), ('attack_form', 'thrust')],
    'A spear used for thrusting melee attacks': [('identity_label', 'spear'), ('function', 'melee_attack'), ('attack_form', 'thrust')],
    'A vehicle storage component used to hold items': [('function', 'store_vehicle_items')],
    '탄약 상자를 열어 얻는다': [('acquisition_process', 'open_ammunition_box')],
    '고기를 잘라 얻는다': [('acquisition_process', 'cut_meat')],
    'Obtained by cutting meat': [('acquisition_process', 'cut_meat')],
    'Obtained by processing herbs': [('acquisition_process', 'process_medicinal_plants')],
    'Made through metalworking': [('acquisition_process', 'metalworking')],
    '몸통에 덧입을 수 있다': [('wear', 'torso')],
    '점화 재료와 함께 모닥불에 불을 붙이는 데 쓴다': [('function', 'light_campfire'), ('condition', 'campfire_lighting', 'tinder')],
    '미끼를 달아 물고기를 잡는 데 쓰는 낚싯대다': [('identity_label', 'fishing_rod'), ('function', 'fish_with_rod'), ('condition', 'rod_fishing', 'bait_attached')],
    'A fishing rod used with bait to catch fish': [('identity_label', 'fishing_rod'), ('function', 'fish_with_rod'), ('condition', 'rod_fishing', 'bait_attached')],
    '부서지지 않은 낚싯대와 미끼를 소지하고 물가의 낚시 메뉴를 사용한다': [('condition', 'rod_fishing', 'unbroken_rod'), ('condition', 'rod_fishing', 'rod_and_bait_carried'), ('condition', 'rod_fishing', 'water_fishing_menu')],
    'Carry an unbroken rod and a lure, then use the fishing menu by the water': [('condition', 'rod_fishing', 'unbroken_rod'), ('condition', 'rod_fishing', 'rod_and_bait_carried'), ('condition', 'rod_fishing', 'water_fishing_menu')],
    '부서지지 않은 낚싯대와 함께 소지하고 물가의 낚시 메뉴에서 사용한다': [('condition', 'rod_fishing', 'unbroken_rod'), ('condition', 'rod_fishing', 'carried_with_rod'), ('condition', 'rod_fishing', 'water_fishing_menu')],
    'Carry it with an unbroken fishing rod and use the fishing menu by the water': [('condition', 'rod_fishing', 'unbroken_rod'), ('condition', 'rod_fishing', 'carried_with_rod'), ('condition', 'rod_fishing', 'water_fishing_menu')],
    '미끼 종류와 시간·계절에 따라 결과가 달라지며 포획은 보장되지 않는다': [('condition', 'fishing_outcome', 'lure_type'), ('condition', 'fishing_outcome', 'time'), ('condition', 'fishing_outcome', 'season'), ('constraint', 'fishing_outcome', 'catch_not_guaranteed')],
    'Lure type, time and season affect the result, and a catch is not guaranteed': [('condition', 'fishing_outcome', 'lure_type'), ('condition', 'fishing_outcome', 'time'), ('condition', 'fishing_outcome', 'season'), ('constraint', 'fishing_outcome', 'catch_not_guaranteed')],
    '깨진 유리 파편이므로 치우거나 접근할 때 주의가 필요하다': [('state_label', 'broken_glass'), ('caution', 'clearing_broken_glass'), ('caution', 'approaching_broken_glass')],
    'Broken glass that requires care when approached or cleared': [('state_label', 'broken_glass'), ('caution', 'clearing_broken_glass'), ('caution', 'approaching_broken_glass')],
    'Recorded media that can be played on a compatible device': [('identity_label', 'recorded_media'), ('function', 'play_recorded_media'), ('condition', 'recorded_media_playback', 'compatible_device')],
    '차량의 후드를 떼어내거나 다시 끼울 수 있다': [('function', 'remove_vehicle_hood'), ('function', 'refit_vehicle_hood')],
    "You can remove and refit the vehicle's hood": [('function', 'remove_vehicle_hood'), ('function', 'refit_vehicle_hood')],
    'A soup or stew that can be eaten or divided into bowls': [('function', 'eat_food'), ('function', 'portion_into_bowls'), ('identity_label', 'soup_or_stew')],
    'Made by tying logs together': [('acquisition_process', 'tie_logs')],
    '통나무를 묶어 만든다': [('acquisition_process', 'tie_logs')],
    'Untie the bundle to take out logs': [('function', 'unbundle_logs'), ('output_identity', 'logs')],
    '전자 부품을 가공해 얻는다': [('acquisition_process', 'process_electronic_parts')],
    '약초를 가공해 얻는다': [('acquisition_process', 'process_medicinal_plants')],
    '금속 가공으로 만든다': [('acquisition_process', 'metalworking')],
    '파스타를 끓여 만든다': [('acquisition_process', 'boil_pasta')],
    '전자 스크랩과 무선 부품, 전선과 알루미늄으로 제작한다': [('acquisition_process', 'craft'), ('acquisition_material', 'electronic_scrap'), ('acquisition_material', 'radio_parts'), ('acquisition_material', 'wire'), ('acquisition_material', 'aluminum')],
    'You can wear it over your torso': [('wear', 'torso')],
    'You can wear it on your left ring finger': [('wear', 'left_ring_finger')],
    'You can wear it on your right ring finger': [('wear', 'right_ring_finger')],
    'Used with tinder or fuel to light a campfire': [('function', 'light_campfire'), ('condition', 'campfire_lighting', 'tinder_or_fuel')],
    'A battery that supplies power for starting a vehicle and operating its electrical devices': [('function', 'supply_vehicle_starting_power'), ('function', 'supply_vehicle_electrical_power')],
    '상처에 감거나 일부 도구와 부목을 만드는 데 쓰는 천 재료다': [('function', 'apply_bandage'), ('role', 'tool_crafting', 'material'), ('role', 'splint_crafting', 'material')],
    '못을 사용하는 목공 구조물을 만드는 데 쓰는 도구다': [('role', 'carpentry_menu_construction', 'tool'), ('condition', 'carpentry_menu_construction', 'nailed_structure')],
    '몸이나 옷의 피와 때를 씻는 데 쓰는 세정제다': [('function', 'wash_body'), ('function', 'wash_clothing'), ('effect', 'blood', 'remove'), ('effect', 'dirt', 'remove')],
    '몸이 젖었고 사용량이 남아 있다면 물기를 닦을 수 있다': [('function', 'dry_the_body'), ('condition', 'body_drying', 'wet_body'), ('condition', 'body_drying', 'uses_remaining')],
    '몸에 향을 더할 때 쓰는 향수다': [('effect', 'body_scent', 'add')],
    '말린 뒤 몸의 물기를 닦는 데 다시 쓸 수 있는 젖은 수건이다': [('function', 'dry_towel'), ('function', 'dry_the_body'), ('condition', 'body_drying', 'after_towel_dries'), ('state_label', 'wet_towel')],
    '머핀을 구운 뒤 나누어 꺼내는 데 쓰는 반죽이 든 틀이다': [('function', 'bake_muffins'), ('function', 'remove_portioned_muffins'), ('condition', 'remove_muffins', 'after_baking'), ('state_label', 'batter_filled_muffin_tray')],
    'Obtained by opening an ammunition box or casting near an anvil': [('acquisition_process', 'open_ammunition_box'), ('acquisition_process', 'cast_ammunition'), ('condition', 'cast_ammunition', 'near_anvil')],
    'Obtained by opening an ammunition box': [('acquisition_process', 'open_ammunition_box')],
    '모루 근처에서 철괴와 망치, 집게로 제작한다': [('acquisition_process', 'craft'), ('acquisition_material', 'iron_ingot'), ('acquisition_tool', 'hammer'), ('acquisition_tool', 'tongs'), ('condition', 'craft', 'near_anvil')],
    'Crafted near an anvil from an iron ingot with a hammer and tongs': [('acquisition_process', 'craft'), ('acquisition_material', 'iron_ingot'), ('acquisition_tool', 'hammer'), ('acquisition_tool', 'tongs'), ('condition', 'craft', 'near_anvil')],
    '컵에 음료를 담아 만든다': [('acquisition_process', 'pour_drink_into_cup')],
    'Made by pouring a drink into a cup': [('acquisition_process', 'pour_drink_into_cup')],
    '컵에 물과 재료를 담아 끓여 만든다': [('acquisition_process', 'boil_in_cup'), ('acquisition_material', 'water'), ('acquisition_material', 'ingredients')],
    'Made by boiling water and ingredients in a cup': [('acquisition_process', 'boil_in_cup'), ('acquisition_material', 'water'), ('acquisition_material', 'ingredients')],
    '동물 사체를 손질해 얻는다': [('acquisition_process', 'butcher_animal_carcass')],
    'Obtained by butchering an animal carcass': [('acquisition_process', 'butcher_animal_carcass')],
    'Use it to strike or shove': [('function', 'melee_attack'), ('function', 'shove')],
    '휘둘러 공격하거나 밀어낼 수 있다': [('function', 'melee_attack'), ('function', 'shove')],
    'Can be dismantled to recover electronic scrap': [('function', 'dismantle_electronics'), ('output_identity', 'electronic_scrap')],
    '학습 작업에서 기술이나 제작법을 익히려고 읽거나 참고할 때 본다': [('function', 'read_or_consult'), ('effect', 'skill_knowledge', 'gain'), ('effect', 'recipe_knowledge', 'gain')],
    'Read or referenced to learn a skill or crafting recipe': [('function', 'read_or_consult'), ('effect', 'skill_knowledge', 'gain'), ('effect', 'recipe_knowledge', 'gain')],
    '하체에 입을 수 있다': [('wear', 'lower_body')],
    'You can wear it on your lower body': [('wear', 'lower_body')],
    'You can wear it on your left middle finger': [('wear', 'left_middle_finger')],
    'You can wear it on your right middle finger': [('wear', 'right_middle_finger')],
    '왼쪽 손목에 착용할 수 있다': [('wear', 'left_wrist')],
    'You can wear it on your left wrist': [('wear', 'left_wrist')],
    '소지품 정리 작업에서 현금과 카드, 지갑을 챙겨 들고 다닐 때 다룬다': [('function', 'carry_cash'), ('function', 'carry_cards'), ('function', 'carry_wallet')],
    '나무를 찍거나 자를 수 있다': [('function', 'chop_tree')],
    'Use it to chop or cut trees': [('function', 'chop_tree')],
    'Clothing worn around the neck': [('wear', 'neck_clothing')],
    '손에 들고 비를 막으며, 접어 둘 수 있는 우산이다': [('function', 'protect_from_rain'), ('condition', 'rain_protection', 'held'), ('function', 'fold_umbrella')],
    'An umbrella that protects from rain when held and can be folded': [('function', 'protect_from_rain'), ('condition', 'rain_protection', 'held'), ('function', 'fold_umbrella')],
    '펼쳐 손에 들면 비를 막는 우산으로 쓸 수 있다': [('function', 'unfold_umbrella'), ('function', 'protect_from_rain'), ('condition', 'rain_protection', 'open_and_held')],
    'Can be opened and held to provide protection from rain': [('function', 'unfold_umbrella'), ('function', 'protect_from_rain'), ('condition', 'rain_protection', 'open_and_held')],
    '기록물에 글을 쓰거나 지도에 주석을 남기는 필기구다': [('function', 'write_documents'), ('function', 'annotate_map')],
    'A writing tool used for documents or map annotations': [('function', 'write_documents'), ('function', 'annotate_map')],
    '문서를 작성·수정하거나 종이를 정리할 때 쓰는 문구류다': [('function', 'write_documents'), ('function', 'revise_documents'), ('function', 'organize_paper')],
    'Stationery used to write or revise documents or organize paper': [('function', 'write_documents'), ('function', 'revise_documents'), ('function', 'organize_paper')],
    '그릇에 나누어 담아 먹을 수 있는 조리 음식이다': [('function', 'portion_into_bowls'), ('function', 'eat_food'), ('state_label', 'prepared_food')],
    'Prepared food that can be divided into bowls for eating': [('function', 'portion_into_bowls'), ('function', 'eat_food'), ('state_label', 'prepared_food')],
    '쌀이나 파스타를 익혀 그릇에 나누어 담는 조리 준비물이다': [('function', 'cook_rice_or_pasta'), ('function', 'portion_into_bowls')],
    'Rice or pasta prepared for cooking and serving in bowls': [('function', 'cook_rice_or_pasta'), ('function', 'portion_into_bowls')],
    '상처에 감을 수 있는 오염된 붕대 재료다': [('function', 'apply_bandage'), ('state_label', 'dirty_bandaging_material')],
    'Dirty bandaging material that can be applied to wounds': [('function', 'apply_bandage'), ('state_label', 'dirty_bandaging_material')],
    '텐트 키트를 만드는 데 쓰는 재료다': [('role', 'tent_kit_making', 'material')],
    '건전지를 사용해 주변을 비추는 손전등이다': [('power_source', 'battery'), ('function', 'illuminate_surroundings')],
    'A battery-powered flashlight used to illuminate the surroundings': [('power_source', 'battery'), ('function', 'illuminate_surroundings')],
    'Obtained by placing seeds in a packet': [('acquisition_process', 'pack_seeds')],
    'Obtained by opening a seed packet': [('acquisition_process', 'open_seed_packet')],
    'Made by cooking dough or ingredients': [('acquisition_process', 'cook_dough_or_ingredients')],
    'Used to remove and plant seeds while preparing cultivation': [('function', 'unpack_seeds'), ('function', 'sow_seeds')],
    '땅을 파서 경작할 자리를 만드는 데 쓰는 도구다': [('function', 'dig_furrow')],
    '눈가에 색을 더하는 아이섀도다': [('visual_effect', 'eye_color')],
    '눈가에 무늬를 더하는 분장이다': [('visual_effect', 'eye_pattern')],
    'Face paint used to add a pattern around the eyes': [('visual_effect', 'eye_pattern')],
    'A material or component used to craft radios or two-way radios': [('role', 'radio_crafting', 'material_or_component')],
    '라디오나 무전기를 만드는 데 쓰는 재료·부품이다': [('role', 'radio_crafting', 'material_or_component')],
    'Clothing worn over the upper and lower body': [('wear', 'whole_body'), ('visual_coverage', 'upper_and_lower_body')],
    'Use it to carry gasoline or refuel a vehicle': [('function', 'carry_gasoline'), ('function', 'refuel_vehicle')],
    '휘발유를 담아 운반하거나 차량에 주유할 수 있다': [('function', 'carry_gasoline'), ('function', 'refuel_vehicle')],
    'A device that produces noise when triggered': [('conditional_effect', 'noise', 'produce', 'triggered')],
    'A device that produces smoke when triggered': [('conditional_effect', 'smoke', 'produce', 'triggered')],
    "A replacement component for a vehicle's suspension": [('function', 'replace_vehicle_suspension')],
    '분해해 전자 부품을 얻을 수 있다': [('function', 'dismantle_electronics'), ('output_identity', 'electronic_parts')],
    '불을 붙이는 재료나 연료로 태워 쓸 수 있다': [('role', 'fire_starting', 'tinder'), ('role', 'burning', 'fuel')],
    'Can be burned as tinder or fuel': [('role', 'fire_starting', 'tinder'), ('role', 'burning', 'fuel')],
    '오른손 중지에 착용할 수 있다': [('wear', 'right_middle_finger')],
    '왼손 중지에 착용할 수 있다': [('wear', 'left_middle_finger')],
    '열쇠가 맞는 문의 잠금을 조작하는 데 쓴다': [('function', 'operate_door_lock'), ('condition', 'door_lock', 'matching_key')],
    'Used to operate the lock of a matching door': [('function', 'operate_door_lock'), ('condition', 'door_lock', 'matching_key')],
    '자물쇠를 달 수 있는 구조물을 잠그는 데 쓴다': [('function', 'install_padlock')],
    'Used to lock structures that support padlocks': [('function', 'install_padlock')],
    '번호 자물쇠를 달 수 있는 구조물을 잠그는 데 쓴다': [('function', 'install_combination_padlock')],
    'Used to secure structures that support combination padlocks': [('function', 'install_combination_padlock')],
    '열쇠가 맞는 자물쇠를 푸는 데 쓴다': [('function', 'remove_matching_padlock'), ('condition', 'padlock', 'matching_key')],
    'Used to unlock a matching padlock': [('function', 'remove_matching_padlock'), ('condition', 'padlock', 'matching_key')],
    '열쇠가 맞는 차량을 사용하는 데 쓴다': [('function', 'request_matching_vehicle_start'), ('condition', 'vehicle', 'matching_key')],
    'Used to operate the matching vehicle': [('function', 'request_matching_vehicle_start'), ('condition', 'vehicle', 'matching_key')],
    'An alcoholic drink that can be consumed or used as a cooking ingredient': [('function', 'drink_food'), ('role', 'food_preparation', 'ingredient'), ('identity_label', 'alcoholic_drink')],
    'Handled when carrying cash, cards, and a wallet': [('function', 'carry_cash'), ('function', 'carry_cards'), ('function', 'carry_wallet')],
    'Handled during leisure when viewing or collecting photos, recordings, souvenirs, or toys': [('context_label', 'leisure'), ('function', 'view_leisure_objects'), ('function', 'collect_leisure_objects')],
    '여가 작업에서 사진이나 기록 매체, 기념품 장난감을 꺼내 보거나 모아둘 때 다룬다': [('context_label', 'leisure'), ('function', 'view_leisure_objects'), ('function', 'collect_leisure_objects')],
    '놀이 작업에서 판과 카드, 말, 작은 장난감을 꺼내 가볍게 즐길 때 다룬다': [('context_label', 'play'), ('function', 'play_with_game_objects')],
    'Handled during play with boards, cards, pieces, or small toys': [('context_label', 'play'), ('function', 'play_with_game_objects')],
    '교체 가능한 조명에 끼워 사용하는 전구다': [('function', 'install_light_bulb'), ('condition', 'lighting', 'replaceable_bulb')],
    'Clothing worn on the head or face': [('wear', 'head_or_face')],
    'Clothing worn over the torso': [('wear', 'torso')],
    'Underwear worn on the legs': [('wear', 'leg_underwear')],
    'An empty container that can be reused to carry water': [('function', 'store_water'), ('function', 'carry_water'), ('state_label', 'empty_reusable_container')],
    'Open the jar to take out its vegetables': [('function', 'unpack_jarred_food'), ('output_identity', 'vegetables')],
    'A two-way radio used to transmit and receive on a tuned frequency': [('function', 'transmit_radio_signal'), ('function', 'receive_radio_signal'), ('condition', 'radio', 'tuned_frequency')],
    'A tank fitted to a vehicle to store fuel': [('function', 'install_vehicle_part'), ('function', 'store_vehicle_fuel')],
    'A muffler component that affects vehicle engine noise': [('effect', 'vehicle_engine_noise', 'affect')],
    'A tire fitted to a vehicle wheel that affects traction': [('function', 'install_vehicle_tire'), ('effect', 'vehicle_traction', 'affect')],
    '그릇이나 냄비에 음식 또는 재료를 담아 준비한다': [('acquisition_process', 'put_food_or_ingredients_in_bowl_or_pot')],
    'Prepared by placing food or ingredients in a bowl or pot': [('acquisition_process', 'put_food_or_ingredients_in_bowl_or_pot')],
    'Made by cooking ingredients': [('acquisition_process', 'cook_ingredients')],
    '반죽이나 재료를 조리해 만든다': [('acquisition_process', 'cook_dough_or_ingredients')],
    'Obtained by placing ammunition in a box': [('acquisition_process', 'box_ammunition')],
    '얼굴 전체에 무늬를 더하는 분장이다': [('visual_effect', 'full_face_pattern')],
    'Face paint used to add a pattern across the face': [('visual_effect', 'full_face_pattern')],
    'Eye shadow used to add color around the eyes': [('visual_effect', 'eye_color')],
    'Sporting equipment used according to the rules of a game or activity': [('function', 'play_sport'), ('condition', 'sport', 'game_rules')],
    '경기나 놀이 규칙에 맞춰 사용하는 스포츠 용품이다': [('function', 'play_sport'), ('condition', 'sport', 'game_rules')],
    '주방 작업에서 식기와 상차림 소품을 꺼내 쓰거나 식사 준비에 곁들일 때 다룬다': [('context_label', 'table_setting'), ('function', 'use_tableware')],
    'Handled with tableware and place-setting items during kitchen work or meal preparation': [('context_label', 'table_setting'), ('function', 'use_tableware')],
    '빈 용기 정리 작업에서 남은 캔이나 용기를 비우고 따로 모아 다시 쓰거나 처리할 때 다룬다': [('function', 'empty_container'), ('function', 'sort_empty_containers'), ('function', 'reuse_container'), ('function', 'dispose_container')],
    'Handled when emptying, sorting, reusing, or disposing of leftover cans and containers': [('function', 'empty_container'), ('function', 'sort_empty_containers'), ('function', 'reuse_container'), ('function', 'dispose_container')],
    '재배를 준비하며 씨앗을 꺼내 심을 때 쓴다': [('function', 'unpack_seeds'), ('function', 'sow_seeds')],
    '눈 화장에 쓰는 화장품이다': [('function', 'apply_eye_makeup')],
    'Cosmetics used around the eyes': [('function', 'apply_eye_makeup')],
    '입술에 색을 더하는 데 쓰는 화장품이다': [('function', 'apply_lip_makeup'), ('visual_effect', 'lip_color')],
    'Cosmetics used to add color to the lips': [('function', 'apply_lip_makeup'), ('visual_effect', 'lip_color')],
    '기초 화장에 쓰는 화장품이다': [('function', 'apply_makeup'), ('cosmetic_role', 'base_layer')],
    'Cosmetics used as a base layer of makeup': [('function', 'apply_makeup'), ('cosmetic_role', 'base_layer')],
    '착용 작업에서 몸에 걸쳐 입고 활동 복장으로 갖출 때 입는다': [('function', 'wear_body')],
    '몸에 걸쳐 차림을 갖추거나 용도에 맞게 착용한다': [('function', 'wear_body')],
    '몸에 걸쳐 착용하는 액세서리다': [('function', 'wear_body')],
    '몸통 위에 걸쳐 입는 의류다': [('wear', 'torso')],
    '상하체를 함께 덮어 입는 의류다': [('wear', 'whole_body'), ('visual_coverage', 'upper_and_lower_body')],
    '목에 두르는 의류다': [('wear', 'neck_clothing')],
    '몸에 걸쳐 입는 겉옷이다': [('wear', 'outerwear')],
    '보관 작업에서 소지품이나 내용물을 담아 휴대하거나 나눠 옮길 때 다룬다': [('function', 'store_and_retrieve_items'), ('function', 'carry_stored_items'), ('function', 'redistribute_container_contents')],
    '물건을 담아 운반하는 자루다': [('function', 'store_and_retrieve_items'), ('function', 'carry_stored_items')],
    '실내 정리 작업에서 수납 가구나 보관함을 옮겨 배치할 때 다룬다': [('function', 'remove_placed_furniture'), ('function', 'place_moveable_furniture'), ('context_label', 'storage_furniture_layout')],
    'Handled when moving storage furniture or containers into position indoors': [('function', 'remove_placed_furniture'), ('function', 'place_moveable_furniture'), ('context_label', 'storage_furniture_layout')],
    '병을 열어 담긴 채소를 꺼낼 수 있다': [('function', 'unpack_jarred_food'), ('output_identity', 'jarred_contents', 'vegetables')],
    '물을 담아 휴대할 때 다시 쓸 수 있는 빈 용기다': [('function', 'store_water'), ('function', 'carry_water'), ('state', 'container_contents', 'empty'), ('function', 'reuse_container')],
    '주파수를 맞춰 무선 신호를 송수신하는 기기다': [('function', 'tune_radio'), ('function', 'receive_radio_signal'), ('function', 'transmit_radio_signal')],
    '주파수를 맞춰 라디오 방송을 듣는 기기다': [('function', 'tune_radio'), ('function', 'receive_radio_signal')],
    'TV 방송을 보거나 녹화된 VHS를 재생하는 기기다': [('function', 'receive_tv_signal'), ('function', 'play_vhs')],
    '호환되는 재생 장치에서 기록된 내용을 재생하는 매체다': [('function', 'play_recorded_media'), ('condition', 'media_playback', 'compatible_player')],
    '차량에 장착해 연료를 저장하는 탱크다': [('function', 'install_vehicle_part'), ('function', 'store_vehicle_fuel')],
    '차량 바퀴에 장착하며 접지력에 영향을 주는 타이어다': [('function', 'install_vehicle_tire'), ('effect', 'vehicle_traction', 'affect')],
    '차량의 엔진 소음에 영향을 주는 소음기 부품이다': [('effect', 'vehicle_engine_noise', 'affect')],
    '차량 서스펜션을 교체하는 데 쓰는 부품이다': [('function', 'replace_vehicle_suspension')],
    '차량의 시동과 전기 장치에 전원을 공급하는 배터리다': [('function', 'supply_vehicle_starting_power'), ('function', 'supply_vehicle_electrical_power')],
    '차량에 설치해 앉거나 물건을 놓는 좌석이다': [('function', 'install_vehicle_seat'), ('function', 'sit_on_vehicle_seat'), ('function', 'store_items_on_vehicle_seat')],
    '차량 정비 작업에서 차체 패널이나 유리를 떼어내거나 다시 끼울 때 다룬다': [('function', 'remove_vehicle_panel_or_glass'), ('function', 'install_vehicle_panel_or_glass')],
    '차량에서 물건을 보관하는 수납 부품이다': [('function', 'store_vehicle_items')],
    '작동하면 소리를 내는 장치다': [('conditional_effect', 'world_noise', 'emit', 'activation')],
    '작동하면 연기를 발생시키는 장치다': [('conditional_effect', 'world_smoke', 'emit', 'activation')],
    '불을 일으키는 데 쓰는 화염 무기다': [('effect', 'world_fire', 'ignite')],
    '조리 준비나 조리 과정에서 다룬다': [('context', 'food_preparation')],
    'Handled during food preparation or cooking': [('context', 'food_preparation')],
    '마시거나 요리 재료로 쓰는 알코올 음료다': [('function', 'drink_food_contents'), ('role', 'food_preparation', 'ingredient'), ('identity_label', 'alcoholic_drink')],
    '근접 전투 작업에서 휘둘러 공격하거나 밀어낼 때 쓴다': [('function', 'melee_attack'), ('function', 'shove')],
    '근접 공격에 사용할 수 있는 도구다': [('function', 'melee_attack')],
    '근접 공격에 쓸 수 있는 도구다': [('function', 'melee_attack')],
    '벌목 작업에서 나무를 찍거나 자를 때 쓴다': [('function', 'chop_tree')],
    '읽으면 지루함·스트레스·불행을 줄일 수 있는 읽을거리다': [('conditional_effect', 'boredom', 'decrease', 'reading'), ('conditional_effect', 'stress', 'decrease', 'reading'), ('conditional_effect', 'unhappiness', 'decrease', 'reading')],
    '재료다': [('identity_label', '재료')],
    '총기 개조 작업에 들어가는 부품이다': [('function', 'attach_weapon_part')],
    'A component used in firearm modification': [('function', 'attach_weapon_part')],
    'Handled when removing or reinstalling devices and fixed fixtures': [('function', 'remove_placed_furniture'), ('function', 'place_moveable_furniture'), ('context_label', 'equipment_layout')],
    'Handled when moving chairs, tables, or resting furniture into position indoors': [('function', 'remove_placed_furniture'), ('function', 'place_moveable_furniture'), ('context_label', 'indoor_furniture_layout')],
    'Handled when arranging a space by placing or removing decorations, exhibits, signs, or area markers': [('function', 'place_moveable_furniture'), ('function', 'remove_placed_furniture'), ('intended_use', 'area_marking'), ('context_label', 'decoration_layout')],
    'You can wear it on your upper body': [('wear', 'upper_body')],
    'Use it to store and carry items': [('function', 'store_and_retrieve_items'), ('function', 'carry_stored_items')],
    'Paint used for coating or leaving marks': [('function', 'paint_supported_surface'), ('function', 'paint_wall_sign')],
    'Obtained by placing harvested produce in a sack': [('acquisition_process', 'sack_produce')],
    'Prepared by mixing ingredients': [('acquisition_process', 'mix_ingredients')],
    'Made by combining ingredients': [('acquisition_process', 'combine_ingredients')],
    'Made by canning ingredients in a jar': [('acquisition_process', 'jar_food')],
    'Obtained by modifying an explosive': [('acquisition_process', 'modify_explosive')],
    '폭발물을 개조해 얻는다': [('acquisition_process', 'modify_explosive')],
    'Usable for melee attacks or as a spear attachment': [('function', 'melee_attack'), ('role', 'spear_upgrade', 'attachment')],
    '근접 공격이나 창 끝에 붙이는 용도로 쓸 수 있다': [('function', 'melee_attack'), ('role', 'spear_upgrade', 'attachment')],
    '읽으면 지루함과 스트레스를 줄일 수 있는 읽을거리다': [('conditional_effect', 'boredom', 'decrease', 'reading'), ('conditional_effect', 'stress', 'decrease', 'reading')],
    'Reading material that can reduce boredom and stress': [('conditional_effect', 'boredom', 'decrease', 'reading'), ('conditional_effect', 'stress', 'decrease', 'reading')],
    '장신구 취급 장소와 장신구 보관 장소, 채집으로 구할 수 있다': [('acquisition_place', 'jewelry areas'), ('acquisition_place', 'jewelry storage'), ('acquisition_method', 'foraging')],
    'Can be obtained from jewelry retailers, jewelry storage, foraging': [('acquisition_place', 'jewelry areas'), ('acquisition_place', 'jewelry storage'), ('acquisition_method', 'foraging')],
    '시가지와 트레일러파크, 초목 지대 채집으로 구할 수 있다': [('acquisition_zone', 'TownZone'), ('acquisition_zone', 'TrailerPark'), ('acquisition_zone', 'Vegitation')],
    'Can be obtained from urban areas, trailer parks, foraging in vegetation zones': [('acquisition_place', 'urban areas'), ('acquisition_place', 'trailer parks'), ('acquisition_zone', 'Vegitation')],
    '설비 배치 작업에서 기기나 고정 설비를 떼어내거나 다시 설치할 때 다룬다': [('function', 'remove_placed_furniture'), ('function', 'place_moveable_furniture'), ('context_label', 'equipment_layout')],
    '실내 배치 작업에서 의자나 탁자, 휴식 가구를 옮겨 자리를 잡을 때 다룬다': [('function', 'remove_placed_furniture'), ('function', 'place_moveable_furniture'), ('context_label', 'indoor_furniture_layout')],
    '공간 연출 작업에서 장식물, 전시물, 표지물을 세우거나 치우며 구역 표시를 정리할 때 다룬다': [('function', 'place_moveable_furniture'), ('function', 'remove_placed_furniture'), ('intended_use', 'area_marking'), ('context_label', 'decoration_layout')],
    '흡연가라면 스트레스와 불행을 줄일 수 있지만 비흡연가의 식중독 수치를 높인다': [('conditional_effect', 'stress', 'decrease', 'smoker'), ('conditional_effect', 'unhappiness', 'decrease', 'smoker'), ('conditional_effect', 'food_sickness', 'increase', 'nonsmoker')],
    '상처 감염을 치료하는 데 쓰는 약이다': [('effect', 'wound_infection', 'decrease')],
    '섭취하면 허기를 줄일 수 있다': [('effect', 'hunger', 'decrease')],
    'Consuming it can reduce hunger': [('effect', 'hunger', 'decrease')],
    '섭취하면 허기와 갈증을 줄일 수 있다': [('effect', 'hunger', 'decrease'), ('effect', 'thirst', 'decrease')],
    'Consuming it can reduce hunger and thirst': [('effect', 'hunger', 'decrease'), ('effect', 'thirst', 'decrease')],
    '섭취하면 허기를 줄일 수 있지만 갈증은 높인다': [('effect', 'hunger', 'decrease'), ('effect', 'thirst', 'increase')],
    '요리 재료로도 쓰인다': [('role', 'food_preparation', 'ingredient')],
    'It is also used as a cooking ingredient': [('role', 'food_preparation', 'ingredient')],
    '날것으로 먹으면 위험할 수 있다': [('condition', 'raw_ingestion', 'hazard')],
    '독성이 있으면 식중독 수치가 오른다': [('effect', 'food_sickness', 'increase_if_poisonous')],
    '자루를 열어 담긴 농산물을 꺼낼 수 있다': [('function', 'unpack_produce')],
    '칠하거나 표식을 남기는 작업에 쓰는 도료다': [('function', 'paint_supported_surface'), ('function', 'paint_wall_sign')],
    '탄약을 장전해 사격하는 데 쓰는 총기다': [('function', 'load_firearm'), ('function', 'fire_ammunition')],
    '해당 탄종을 사용하는 총기의 장전에 쓰는 탄약이다': [('role', 'firearm_loading', 'ammunition')],
    'Ammunition used to load guns that accept this ammunition type': [('role', 'firearm_loading', 'ammunition')],
    '물건을 담아 운반하는 휴대용 보관함이다': [('function', 'store_and_retrieve_items'), ('function', 'carry_stored_items')],
    '물을 담아 운반하는 데 쓰는 용기다': [('function', 'store_water'), ('function', 'carry_water')],
    '머리에 쓰는 의류나 장신구다': [('wear', 'head')],
    '상체에 입는 의류다': [('wear', 'upper_body')],
    '하체에 입는 의류다': [('wear', 'lower_body')],
    '상체에 걸쳐 입는 겉옷이다': [('wear', 'outerwear')],
    '하의로 착용하는 속옷이다': [('wear', 'lower_underwear')],
    '상의로 착용하는 속옷이다': [('wear', 'upper_underwear')],
    '귀에 착용하는 장신구다': [('wear', 'ears')],
    '발에 신는 신발류다': [('wear', 'feet')],
    '배꼽에 착용하는 장신구다': [('wear', 'belly_button')],
    '몸에 입는 원피스형 의류다': [('wear', 'dress')],
    '목에 착용하는 목걸이다': [('wear', 'necklace')],
    '목에 착용하는 장신구다': [('wear', 'neck')],
    '근접 공격에 사용할 수 있는 물건이다': [('function', 'melee_attack')],
    '기폭해 폭발을 일으키는 무기다': [('effect', 'explosion', 'triggered')],
    'A weapon that produces an explosion when triggered': [('effect', 'explosion', 'triggered')],
    '시간을 확인하거나 알람을 설정하는 데 쓰는 시계다': [('function', 'check_time'), ('function', 'set_alarm')],
    'A clock used to check the time or set an alarm': [('function', 'check_time'), ('function', 'set_alarm')],
    '설치한 뒤 일정 시간이 지나면 소리를 내는 재사용 장치다': [('function', 'place_noise_device'), ('effect', 'device_sound', 'after_delay'), ('condition', 'device_sound', 'after_placement'), ('function', 'reuse_activated_device')],
    'A reusable device that makes a sound after a set delay': [('effect', 'device_sound', 'after_delay'), ('function', 'reuse_activated_device')],
    '착용하면 산탄총 이외의 총기를 더 빨리 장전할 수 있다': [('effect', 'reload_speed', 'increase'), ('condition', 'reload_speed', 'worn'), ('condition', 'reload_speed', 'non_shotgun')],
    'Wear it to reload non-shotgun firearms faster': [('effect', 'reload_speed', 'increase'), ('condition', 'reload_speed', 'worn'), ('condition', 'reload_speed', 'non_shotgun')],
    '착용하면 산탄총을 더 빨리 장전할 수 있다': [('effect', 'reload_speed', 'increase'), ('condition', 'reload_speed', 'worn'), ('condition', 'reload_speed', 'shotgun')],
    'Wear it to reload shotguns faster': [('effect', 'reload_speed', 'increase'), ('condition', 'reload_speed', 'worn'), ('condition', 'reload_speed', 'shotgun')],
    '산탄이 아닌 탄약을 사용하는 총기의 장전 속도를 높이는 착용 장비다': [('effect', 'reload_speed', 'increase'), ('condition', 'reload_speed', 'worn'), ('condition', 'reload_speed', 'non_shotgun')],
    '산탄총 탄약을 사용하는 총기의 장전 속도를 높이는 착용 장비다': [('effect', 'reload_speed', 'increase'), ('condition', 'reload_speed', 'worn'), ('condition', 'reload_speed', 'shotgun')],
    '착용한 상태에서 산탄총 탄약이 아닌 탄약을 쓰는 총기를 장전할 때 적용된다': [('condition', 'reload_speed', 'worn'), ('condition', 'reload_speed', 'non_shotgun')],
    '착용한 상태에서 산탄총 탄약을 쓰는 총기를 장전할 때 적용된다': [('condition', 'reload_speed', 'worn'), ('condition', 'reload_speed', 'shotgun')],
    'Consuming it can reduce hunger but increases thirst': [('effect', 'hunger', 'decrease'), ('effect', 'thirst', 'increase')],
    'Eating it raw can be dangerous': [('condition', 'raw_ingestion', 'hazard')],
    'If poisonous, it increases food sickness': [('effect', 'food_sickness', 'increase_if_poisonous')],
    '섭취하면 허기와 갈증을 줄일 수 있으며, 요리 재료로도 쓰인다': [('effect', 'hunger', 'decrease'), ('effect', 'thirst', 'decrease'), ('role', 'food_preparation', 'ingredient')],
    'Eating it can reduce hunger and thirst; it can also be used as a cooking ingredient': [('effect', 'hunger', 'decrease'), ('effect', 'thirst', 'decrease'), ('role', 'food_preparation', 'ingredient')],
    '봉지를 열어 재배용 씨앗을 꺼낼 수 있다': [('function', 'unpack_seeds')],
    'Open the packet to obtain seeds for planting': [('function', 'unpack_seeds')],
    '총기 장전에 쓰는 탄창이다': [('function', 'insert_matching_magazine')],
    'A magazine used to load a firearm': [('function', 'insert_matching_magazine')],
    '필기구가 있으면 내용을 적어 보관할 수 있는 기록물이다': [('function', 'record_written_notes'), ('condition', 'note_writing', 'writing_implement')],
    'A document in which notes can be written and kept using a writing tool': [('function', 'record_written_notes'), ('condition', 'note_writing', 'writing_implement')],
    'Open the sack to take out its produce': [('function', 'unpack_produce')],
    '사격에 쓰는 총기다': [('function', 'fire_ammunition')],
    'A firearm used for shooting': [('function', 'fire_ammunition')],
    '위치 확인과 이동 계획에 참고하는 지도다': [('function', 'view_item_map'), ('intended_use', 'navigation_planning')],
    'A map referenced for navigation and route planning': [('function', 'view_item_map'), ('intended_use', 'navigation_planning')],
    'A portable container used to carry items': [('function', 'store_and_retrieve_items'), ('function', 'carry_stored_items')],
    '물건을 넣어 보관하거나 운반할 수 있다': [('function', 'store_and_retrieve_items'), ('function', 'carry_stored_items')],
    '상처에 감거나 붙이는 데 쓰는 붕대 재료다': [('function', 'apply_bandage')],
    'Bandaging material used to cover wounds': [('function', 'apply_bandage')],
    '머리색을 바꾸는 데 쓰는 염색약이다': [('function', 'dye_hair_or_beard')],
    'Hair dye used to change hair color': [('function', 'dye_hair_or_beard')],
    '머리 모양을 정돈하는 데 쓰는 헤어 젤이다': [('function', 'groom_hair')],
    'Hair gel used to style hair': [('function', 'groom_hair')],
    '소리를 내는 작은 종이다': [('identity_label', '종'), ('function', 'ring_bell')],
    'A small bell that makes sound': [('identity_label', '종'), ('function', 'ring_bell')],
    '허리에 착용하는 벨트다': [('function', 'wear_body')],
    'A belt worn around the waist': [('function', 'wear_body')],
    'An accessory worn on the body': [('function', 'wear_body')],
    '물을 담는 그릇이다': [('function', 'store_water')],
    'A vessel used to hold water': [('function', 'store_water')],
    '청취 작업에서 휴대용 라디오를 켜고 주파수를 맞춰 방송을 들을 때 다룬다': [('function', 'toggle_device_power'), ('function', 'tune_radio'), ('function', 'receive_radio_signal')],
    'Handled when tuning a portable radio to listen to broadcasts': [('function', 'tune_radio'), ('function', 'receive_radio_signal')],
    '야외 이동 작업에서 펼쳐 비를 막거나 접어 휴대할 때 쓴다': [('function', 'unfold_umbrella'), ('function', 'protect_from_rain'), ('function', 'fold_umbrella')],
    'Opened for rain protection or folded for carrying outdoors': [('function', 'unfold_umbrella'), ('function', 'protect_from_rain'), ('function', 'fold_umbrella')],
    '신호 확인이나 장비 운용에 쓰는 전자 기기다': [('function', 'check_signals'), ('function', 'operate_equipment')],
    'An electronic device used to check signals or operate equipment': [('function', 'check_signals'), ('function', 'operate_equipment')],
    '손질하면 개구리 고기를 얻을 수 있다': [('function', 'prepare_frog_meat'), ('output_identity', 'frog_meat')],
    'It can be cut up to obtain frog meat': [('function', 'prepare_frog_meat'), ('output_identity', 'frog_meat')],
    '철사를 회수할 수 있는 부서진 통발이다': [('identity_label', '망가진 그물 덫'), ('function', 'recover_wire')],
    'A broken fish trap from which wire can be recovered': [('identity_label', '망가진 그물 덫'), ('function', 'recover_wire')],
    '매트리스를 만드는 데 쓰는 재료다': [('role', 'mattress_preparation', 'material')],
    'A material used to make a mattress': [('role', 'mattress_preparation', 'material')],
    '탄약 주조에 쓰는 틀이다': [('role', 'metal_forging', 'tool')],
    'A mold used to cast ammunition': [('role', 'metal_forging', 'tool')],
    '금속 단조에 쓰는 도구다': [('role', 'metal_forging', 'tool')],
    'A tool used for metal forging': [('role', 'metal_forging', 'tool')],
    '금속 가공에서 작은 금속판을 만드는 재료로 쓰는 금속판이다': [('role', 'welded_parts', 'material')],
    'A metal sheet used as material for producing smaller metal sheets': [('role', 'welded_parts', 'material')],
    '금속 가공에서 금속판을 만드는 재료로 쓰는 작은 금속판이다': [('role', 'welded_parts', 'material')],
    'A small metal sheet used as material for producing metal sheets': [('role', 'welded_parts', 'material')],
    '채소를 병조림으로 담는 데 쓰는 빈 병이다': [('role', 'vegetable_jarring', 'material')],
    'An empty jar used to can vegetables': [('role', 'vegetable_jarring', 'material')],
    '채소 병조림을 만들 때 빈 병과 함께 쓰는 뚜껑이다': [('role', 'vegetable_jarring', 'material'), ('condition', 'vegetable_jarring', 'with_empty_jar')],
    'A lid used with an empty jar when canning vegetables': [('role', 'vegetable_jarring', 'material'), ('condition', 'vegetable_jarring', 'with_empty_jar')],
    '화장을 적용할 때 쓸 수 있는 거울이다': [('function', 'support_makeup_mirror')],
    'A mirror used when applying makeup': [('function', 'support_makeup_mirror')],
    '면도에 쓰는 도구다': [('function', 'groom_beard')],
    'A tool used for shaving': [('function', 'groom_beard')],
    '컴프리 습포를 만드는 데 쓰는 재료다': [('role', 'poultice_preparation', 'material')],
    'An ingredient used to make a comfrey poultice': [('role', 'poultice_preparation', 'material')],
    '질경이 습포를 만드는 데 쓰는 재료다': [('role', 'poultice_preparation', 'material')],
    'An ingredient used to make a plantain poultice': [('role', 'poultice_preparation', 'material')],
    '소독용 솜을 만드는 데 쓰는 재료다': [('role', 'bandaging_material_preparation', 'material')],
    'A material used to make alcohol-soaked cotton balls': [('role', 'bandaging_material_preparation', 'material')],
    'Thread used to craft fabric items or stitch wounds together with a needle': [('role', 'fabric_crafting', 'material'), ('function', 'stitch_wound')],
    '의료 처치 작업에서 소독하거나 약재로 써 상처를 돌볼 때 쓴다': [('function', 'disinfect_wound'), ('function', 'medicate_wound')],
    'Used to disinfect or medicate wounds during treatment': [('function', 'disinfect_wound'), ('function', 'medicate_wound')],
    '마시면 갈증을 줄일 수 있다': [('effect', 'thirst', 'decrease')],
    'Drinking it can reduce thirst': [('effect', 'thirst', 'decrease')],
    '상처를 소독하는 데 쓰는 소모품이다': [('function', 'disinfect_wound'), ('consumption_property', 'consumable')],
    '상처를 소독하는 데 쓰는 소독제다': [('function', 'disinfect_wound')],
    'A consumable used to disinfect wounds': [('function', 'disinfect_wound'), ('consumption_property', 'consumable')],
    'A disinfectant used to disinfect wounds': [('function', 'disinfect_wound')],
    '다친 부위에 바르는 약초 찜질제다': [('function', 'apply_poultice')],
    'An herbal poultice applied to an injured body part': [('function', 'apply_poultice')],
    '골절 부위를 고정하는 데 쓰는 부목이다': [('function', 'apply_splint')],
    'A splint used to immobilize a fracture': [('function', 'apply_splint')],
    '깊은 상처를 봉합하는 데 쓰는 바늘이다': [('function', 'stitch_wound')],
    'A needle used to stitch deep wounds': [('function', 'stitch_wound')],
    '몸에 박힌 깨진 유리나 총알을 꺼낼 때 쓰는 의료 도구다': [('function', 'remove_embedded_glass'), ('function', 'remove_embedded_bullet')],
    'A medical tool used to remove embedded glass or bullets': [('function', 'remove_embedded_glass'), ('function', 'remove_embedded_bullet')],
    '상처 봉합을 돕고, 박힌 유리나 탄환을 제거하는 데 쓰는 의료 도구다': [('function', 'assist_stitching'), ('function', 'remove_embedded_glass'), ('function', 'remove_embedded_bullet')],
    'A medical tool that assists with stitching wounds and removing embedded glass or bullets': [('function', 'assist_stitching'), ('function', 'remove_embedded_glass'), ('function', 'remove_embedded_bullet')],
    '천 물품을 제작하거나 바늘과 함께 상처를 봉합할 때 쓰는 실이다': [('role', 'fabric_crafting', 'material'), ('function', 'stitch_wound')],
    '건강 패널에서 붕대가 감겨 있지 않은 다친 부위를 선택하고 소독 메뉴의 사용 가능한 물품 중에서 고른다':
        [('condition', 'disinfection', 'unbandaged'), ('condition', 'disinfection', 'injured'), ('condition', 'disinfection', 'health_panel_selection')],
    '건강 패널에서 골절이 있고 아직 부목을 대거나 봉합하지 않은 부위를 선택한다':
        [('condition', 'splinting', 'fracture'), ('condition', 'splinting', 'not_splinted'), ('condition', 'splinting', 'not_stitched')],
    '머리와 위·아래 몸통은 부목 메뉴의 대상에서 제외된다': [('condition', 'splinting', 'head_torso_excluded')],
    '상체에 입을 수 있다': [('wear', 'upper_body')],
    'It can be worn on the upper body': [('wear', 'upper_body')],
    '탄약을 상자에 담아 얻는다': [('acquisition_process', 'box_ammunition')],
    'Obtained by packing ammunition into a box': [('acquisition_process', 'box_ammunition')],
    '탄약 상자를 열거나 모루 근처에서 주조해 얻는다': [('acquisition_process', 'open_ammunition_box'), ('acquisition_process', 'cast_ammunition'), ('condition', 'ammunition_casting', 'near_anvil')],
    '씨앗을 봉투에 담아 얻는다': [('acquisition_process', 'package_seeds')],
    '씨앗 봉투를 열어 얻는다': [('acquisition_process', 'open_seed_packet')],
    '수확물을 포대에 담아 얻는다': [('acquisition_process', 'sack_produce')],
    '빈 용기에 물을 담아 얻는다': [('acquisition_process', 'fill_water'), ('condition', 'fill_water', 'empty_container')],
    '빈 용기에 물을 채워 얻는다': [('acquisition_process', 'fill_water'), ('condition', 'fill_water', 'empty_container')],
    'Obtained by filling an empty container with water': [('acquisition_process', 'fill_water'), ('condition', 'fill_water', 'empty_container')],
    '재료를 병조림해 만든다': [('acquisition_process', 'jar_food')],
    '재료를 조리해 만든다': [('acquisition_process', 'cook_ingredients')],
    '재료를 섞어 준비한다': [('acquisition_process', 'mix_ingredients')],
    '재료를 조합해 만든다': [('acquisition_process', 'combine_ingredients')],
    '제작으로 얻는다': [('acquisition_process', 'craft')],
    'Obtained through crafting': [('acquisition_process', 'craft')],
}

# Discovery-place meanings are prose atoms only. These names never grant loot
# facts or resolve raw distribution namespaces. A compound that does not fit
# this bounded grammar remains an independent unsegmented obligation.
PLACES = {
    '사물함': 'lockers', '골프 카트': 'golf carts', '극장': 'theaters', '작업 현장': 'work sites',
    '서점 가방 진열대': 'bookstore bag displays', '학교 물품 장소': 'school-supply areas',
    '제과 작업 장소': 'baking areas', '식기 보관 장소': 'tableware storage', '칼 제작 장소': 'knife-production areas',
    '식료품점': 'grocery stores', '애완용품 판매점': 'pet-supply stores', '시계 판매점': 'watch stores',
    '우편 작업장': 'postal workplaces', '숙박 시설': 'lodging', '욕실': 'bathrooms', '실험실': 'laboratories',
    '실험 시설': 'laboratories', '배관 자재 장소': 'plumbing-supply areas', '검시 작업 장소': 'autopsy areas',
    '음향 기기 판매점': 'audio-equipment stores', '전자용품 보관 장소': 'electronics storage',
    '정비 작업장': 'maintenance workshops', '공구 판매 장소': 'tool retailers',
    '무장 은신처': 'armed safehouses', '교도관 보관 장소': 'corrections-officer storage',
    '장난감 판매점': 'toy stores', '주거지': 'residences',
    '제과점': 'bakeries', '카페': 'cafes', '악기 상점': 'music stores', '전당포': 'pawnshops',
    '금속 작업장': 'metalworking workshops', '책상': 'desks', '발전기실': 'generator rooms',
    '캠핑과 사냥 장비 보관 장소': 'camping and hunting equipment storage',
    '군과 경찰 무기 보관 장소': 'military and police weapon storage',
    '군과 경찰 총기 보관 장소': 'military and police firearm storage',
    '경찰과 교도관 보관 장소': 'police and prison-guard storage',
    '축제 물품과 코스튬 보관 장소': 'festival-supply and costume storage',
    '학교': 'schools', '서점': 'bookstores', '도서관': 'libraries', '가정집 책장': 'home bookshelves',
    '책 상자': 'book crates', '우체국': 'post offices', '우편 차량': 'postal vehicles',
    '장신구 취급 장소': 'jewelry areas', '장신구 보관 장소': 'jewelry storage',
    '속옷 진열대': 'underwear displays', '의류 보관 장소': 'clothing storage',
    '공사 자재 보관 장소': 'construction-material storage', '작업장': 'workshops',
    '군용 보관 장소': 'military storage', '군용품점': 'military-surplus stores',
    '지도 진열대': 'map displays', '지도 상자': 'map crates', '차량 정비소 선반': 'vehicle-shop shelves', '차량': 'vehicles',
    '악기 상자': 'instrument cases', '음악 상점': 'music stores', '연습실 보관함': 'rehearsal-room storage',
    '작업 차량': 'work vehicles', '차고': 'garages', '공구 상자': 'toolboxes', '공구점': 'tool stores',
    '전자제품 매장': 'electronics stores', '전자 부품 보관 장소': 'electronic-parts storage',
    '재킷 매장': 'jacket stores', '사냥 장비 보관 장소': 'hunting-equipment storage',
    '가정 총기 보관 장소': 'home firearm storage', '가정집': 'homes', '의료 시설': 'medical facilities',
    '모자 매장': 'hat stores', '바지 매장': 'pants stores', '총기 취급 장소': 'firearm areas',
    '경찰 시설': 'police facilities', '총기 매장': 'gun stores', '차고 총기 보관 장소': 'garage firearm storage',
    '코스튬 보관 장소': 'costume storage', '수영복 진열대': 'swimwear displays',
    '드레스 매장': 'dress stores', '볼링장 보관 장소': 'bowling-alley storage', '셔츠 매장': 'shirt stores',
    '소방 보관 장소': 'fire-department storage', '란제리 매장': 'lingerie stores',
}


CLAUSES.update({
    '천이나 의류를 찢어 얻는다': [('acquisition_process', 'rip_named_cloth'), ('acquisition_process', 'rip_registered_clothing')],
    'Obtained by ripping cloth or clothing': [('acquisition_process', 'rip_named_cloth'), ('acquisition_process', 'rip_registered_clothing')],
    'Obtained by tearing fabric or clothing': [('acquisition_process', 'rip_named_cloth'), ('acquisition_process', 'rip_registered_clothing')],
    '데님 의류를 찢어 얻는다': [('acquisition_process', 'rip_denim_clothing')],
    'Obtained by tearing denim clothing': [('acquisition_process', 'rip_denim_clothing')],
    '가죽 의류를 찢어 얻는다': [('acquisition_process', 'rip_leather_clothing')],
    'Obtained by tearing leather clothing': [('acquisition_process', 'rip_leather_clothing')],
    '붕대를 소독하거나 끓여서 만든다': [('acquisition_process', 'disinfect_bandage'), ('acquisition_process', 'boil_bandage')],
    'Made by disinfecting or boiling a bandage': [('acquisition_process', 'disinfect_bandage'), ('acquisition_process', 'boil_bandage')],
    '헝겊을 소독하거나 끓여서 만든다': [('acquisition_process', 'disinfect_rag'), ('acquisition_process', 'boil_rag')],
    'Made by disinfecting or boiling a rag': [('acquisition_process', 'disinfect_rag'), ('acquisition_process', 'boil_rag')],
    '솜에 알코올을 묻혀 만든다': [('acquisition_process', 'wet_cotton_with_alcohol')],
    'Made by soaking cotton balls in alcohol': [('acquisition_process', 'wet_cotton_with_alcohol')],
    '상처에 감아 사용하는 붕대다': [('function', 'apply_bandage')],
    'A bandage applied to wounds': [('function', 'apply_bandage')],
    '건강 패널에서 붕대가 감겨 있지 않은 다친 부위의 붕대 메뉴로 적용한다': [('condition', 'bandaging', 'injured_unbandaged_health_menu')],
    'Apply it using the bandage menu for an injured, unbandaged body part in the Health panel': [('condition', 'bandaging', 'injured_unbandaged_health_menu')],
    '이미 감은 붕대는 같은 패널의 붕대 제거 메뉴에서 뺄 수 있다': [('function', 'remove_applied_bandage')],
    "An existing bandage can be removed through that panel's remove-bandage option": [('function', 'remove_applied_bandage')],
    '나무막대와 낚싯줄, 종이클립이나 못으로 제작한다': [('acquisition_process', 'craft'), ('acquisition_material', 'wooden_stick'), ('acquisition_material', 'fishing_line'), ('acquisition_alternative_materials', 'paperclip', 'nail')],
    'Crafted from a wooden stick, fishing line, and a paperclip or nail': [('acquisition_process', 'craft'), ('acquisition_material', 'wooden_stick'), ('acquisition_material', 'fishing_line'), ('acquisition_alternative_materials', 'paperclip', 'nail')],
    '나무막대와 끈, 종이클립이나 못으로 제작한다': [('acquisition_process', 'craft'), ('acquisition_material', 'wooden_stick'), ('acquisition_material', 'twine'), ('acquisition_alternative_materials', 'paperclip', 'nail')],
    'Crafted from a wooden stick, cord, and a paperclip or nail': [('acquisition_process', 'craft'), ('acquisition_material', 'wooden_stick'), ('acquisition_material', 'twine'), ('acquisition_alternative_materials', 'paperclip', 'nail')],
    '부러진 낚싯대를 끈과 종이클립이나 못으로 수리한다': [('acquisition_process', 'craft'), ('acquisition_material', 'broken_fishing_rod'), ('acquisition_material', 'twine'), ('acquisition_alternative_materials', 'paperclip', 'nail')],
    'Made by repairing a broken fishing rod with cord and a paperclip or nail': [('acquisition_process', 'craft'), ('acquisition_material', 'broken_fishing_rod'), ('acquisition_material', 'twine'), ('acquisition_alternative_materials', 'paperclip', 'nail')],
    '낚싯줄을 연결해 낚싯대로 수리할 수 있다': [('function', 'repair_fishing_rod_with_line')],
    'It can be repaired into a fishing rod by attaching line': [('function', 'repair_fishing_rod_with_line')],
    '낚싯대 낚시에 미끼로 쓰는 작은 물고기다': [('function', 'bait_rod_fishing'), ('identity_label', 'bait_fish')],
    'A small fish used as bait when fishing with a rod': [('function', 'bait_rod_fishing'), ('identity_label', 'bait_fish')],
    '이 미끼로는 파이크를 노릴 수 있다': [('condition', 'rod_fishing', 'baitfish_pike')],
    'Pike are eligible catches with this bait': [('condition', 'rod_fishing', 'baitfish_pike')],
    '미끼는 소모되거나 잃을 수 있고, 포획은 보장되지 않는다': [('consumption_property', 'fishing_lure', 'may_be_spent_or_lost'), ('constraint', 'fishing_outcome', 'catch_not_guaranteed')],
    'The bait can be consumed or lost, and a catch is not guaranteed': [('consumption_property', 'fishing_lure', 'may_be_spent_or_lost'), ('constraint', 'fishing_outcome', 'catch_not_guaranteed')],
    '낚싯대 낚시에 쓰는 인공 미끼다': [('function', 'bait_rod_fishing'), ('state_label', 'artificial_lure')],
    '몸의 물기를 닦거나 표백제와 함께 혈흔을 지우는 데 쓴다': [('function', 'dry_the_body'), ('function', 'clean_world_blood'), ('condition', 'blood_cleaning', 'bleach_and_tool')],
    '몸을 말리려면 몸이 젖어 있고 수건의 사용량이 남아 있어야 한다': [('condition', 'body_drying', 'wet_body'), ('condition', 'body_drying', 'uses_remaining')],
    '혈흔 청소에는 표백제도 필요하다': [('condition', 'blood_cleaning', 'bleach_and_tool')],
    '재를 치우거나 표백제와 함께 혈흔을 지우는 데 쓰는 도구다': [('function', 'clear_burnt_floor_ashes'), ('function', 'clean_world_blood'), ('condition', 'blood_cleaning', 'bleach_and_tool')],
    '재를 치울 때는 부서지지 않은 빗자루가 필요하다': [('condition', 'ash_clearing', 'unbroken_broom')],
    '혈흔을 지울 때는 표백제도 소지하고 혈흔이 있는 곳의 청소 메뉴를 사용한다': [('condition', 'blood_cleaning', 'bleach_and_tool')],
    '표백제와 함께 혈흔을 지우는 데 쓰는 도구다': [('function', 'clean_world_blood'), ('condition', 'blood_cleaning', 'bleach_and_tool')],
    '표백제를 함께 소지하고 혈흔이 있는 곳의 청소 메뉴에서 사용한다': [('condition', 'blood_cleaning', 'bleach_and_tool')],
    '혈흔이 있는 곳에서 대걸레, 부서지지 않은 빗자루, 행주 또는 수건과 함께 사용한다': [('condition', 'blood_cleaning', 'bleach_and_tool')],
    '청소할 때 표백제가 소모된다': [('consumption_property', 'blood_cleaning', 'bleach_used')],
    '표백제와 함께 쓰면 혈흔도 지울 수 있다': [('function', 'clean_world_blood'), ('condition', 'blood_cleaning', 'bleach_and_tool')],
    'With bleach, you can also remove blood stains': [('function', 'clean_world_blood'), ('condition', 'blood_cleaning', 'bleach_and_tool')],
    'Select an injured, unbandaged body part in the Health panel, then choose it from the available items in the disinfect menu': [('condition', 'disinfection', 'unbandaged'), ('condition', 'disinfection', 'injured'), ('condition', 'disinfection', 'health_panel_selection')],
    '호환되는 라디오 장치에 연결해 소리를 듣는 데 쓴다': [('function', 'connect_radio_headphones'), ('function', 'listen_through_radio_headphones')],
    'Used with compatible radio devices to listen through headphones': [('function', 'connect_radio_headphones'), ('function', 'listen_through_radio_headphones')],
    '미끼로는 지렁이·귀뚜라미·메뚜기·바퀴벌레, 미끼용 작은 물고기 또는 두 종류의 낚시 루어 등을 쓸 수 있다': [('condition', 'rod_fishing', 'lure_examples')],
    'Lures include worms, crickets, grasshoppers, cockroaches, bait fish and either type of fishing tackle': [('condition', 'rod_fishing', 'lure_examples')],
    '작은 물고기 미끼로는 파이크를, 인공 루어로는 송어·배스·메기 등을 잡을 수 있다': [('condition', 'rod_fishing', 'baitfish_pike'), ('condition', 'rod_fishing', 'artificial_species')],
    'Bait fish can attract pike; artificial tackle can attract trout, bass and catfish': [('condition', 'rod_fishing', 'baitfish_pike'), ('condition', 'rod_fishing', 'artificial_species')],
    '송어·배스·메기 등 이 인공 미끼에 반응하는 어종을 잡을 수 있으며, 파이크나 미끼용 작은 물고기는 이 미끼의 대상이 아니다': [('condition', 'rod_fishing', 'artificial_species'), ('constraint', 'rod_fishing', 'artificial_excludes_pike_baitfish')],
    'Eligible fish include trout, bass and catfish; pike and bait fish do not take this artificial lure': [('condition', 'rod_fishing', 'artificial_species'), ('constraint', 'rod_fishing', 'artificial_excludes_pike_baitfish')],
    '미끼와 함께 설치해 쥐를 잡는 데 쓰는 덫이다': [('function', 'place_animal_trap'), ('function', 'catch_trap_animal'), ('eligible_animal', 'mouse_or_rat'), ('condition', 'animal_trapping', 'bait')],
    'A baited trap used to catch mice and rats': [('function', 'place_animal_trap'), ('function', 'catch_trap_animal'), ('eligible_animal', 'mouse_or_rat'), ('condition', 'animal_trapping', 'bait')],
    '치즈·땅콩버터 등 쥐가 먹는 미끼를 넣는다': [('bait_example', 'cheese'), ('bait_example', 'peanut_butter'), ('condition', 'animal_trapping', 'accepted_bait')],
    'Add mouse or rat bait such as cheese or peanut butter': [('bait_example', 'cheese'), ('bait_example', 'peanut_butter'), ('condition', 'animal_trapping', 'accepted_bait')],
    '미끼와 함께 설치해 새를 잡는 데 쓰는 덫이다': [('function', 'place_animal_trap'), ('function', 'catch_trap_animal'), ('eligible_animal', 'bird'), ('condition', 'animal_trapping', 'bait')],
    '벌레·빵·옥수수 등 새가 먹는 미끼를 넣는다': [('bait_example', 'worm'), ('bait_example', 'bread'), ('bait_example', 'corn'), ('condition', 'animal_trapping', 'accepted_bait')],
    'Add bird bait such as worms, bread or corn': [('bait_example', 'worm'), ('bait_example', 'bread'), ('bait_example', 'corn'), ('condition', 'animal_trapping', 'accepted_bait')],
    'There is no time-of-day restriction, but location, bait freshness and player proximity restrict catches': [('condition', 'animal_trapping', 'no_time_limit'), ('condition', 'animal_trapping', 'zone'), ('condition', 'animal_trapping', 'bait_freshness'), ('condition', 'animal_trapping', 'player_proximity')],
    'Birds have no time-of-day restriction, but location, bait freshness and player proximity restrict catches': [('condition', 'animal_trapping', 'no_time_limit'), ('condition', 'animal_trapping', 'zone'), ('condition', 'animal_trapping', 'bait_freshness'), ('condition', 'animal_trapping', 'player_proximity')],
})

# Standalone taxonomy only. These exact source categories do not establish a
# function, treatment effect, recipe role, or destination product presence.
DISPLAY_LABELS = {
    '탄약': {'Ammo'}, '폭발물': {'Explosives'}, '전자 기기': {'Electronics', 'Communications'},
    '의료 용품': {'FirstAid'}, '무기 부품': {'WeaponPart'}, '재료': {'Material'},
    '도구': {'Tool', 'ToolWeapon'}, '스포츠 용품': {'Sports'}, '가방': {'Bag'},
    '악기': {'Instrument'}, '무기': {'Weapon', 'WeaponCrafted', 'ToolWeapon'},
    '수원': {'Water'}, '서적': {'Literature'}, '문서': {'Literature'},
    '용기': {'Container'}, '잡동사니': {'Junk'}, '캠핑 용품': {'Camping'},
    '낚시 용품': {'Fishing'}, '도료': {'Paint'}, '덫 사냥 용품': {'Trapping'},
    '원예 용품': {'Gardening'}, '액세서리': {'Accessory'},
    '차량 정비 용품': {'VehicleMaintenance'}, '기술 서적': {'SkillBook'},
}


def discovery_places(clause):
    # The location predicate and noun-phrase grammar establish the predecessor
    # claim only. Unrecognized runtime place names remain literal source-
    # investigation obligations; they are never admission aliases.
    def place_name(part, locale):
        if locale == 'ko':
            if part in PLACES:
                return PLACES[part]
            if (re.fullmatch(r'[가-힣A-Za-z0-9 ·-]+', part)
                    and not re.search(r'에서|하면|거나|그리고|또는', part)
                    and re.search(r'(?:장소|매장|상점|상자|보관함|시설|창고|주방|부엌|선반|진열대|서랍|옷장|차량|차고|사무실|식당|음식점|병원|약국|학교|가정집|집|공장|구역|공원|공간|판매대|매대|용품점|철물점|골동품점|체육관|탈의실|구급차|은닉처)$', part)):
                return part
        else:
            if part in PLACES.values():
                return part
            if (re.fullmatch(r'[A-Za-z0-9 -]+', part)
                    and not re.search(r'\b(?:after|before|if|when|while|with|without|by|using|where|that)\b', part)
                    and re.search(r'\b(?:areas|stores|storage|shelves|displays|drawers|wardrobes|homes|houses|kitchens|restaurants|warehouses|crates|boxes|cabinets|facilities|shops|vehicles|garages|offices|schools|hospitals|pharmacies|parks|rooms|cases|retailers|counters|stashes|gyms|ambulances|safehouses|lockers|laboratories|desks)$', part)):
                return part
        return None

    match = re.fullmatch(r'(.+)에서 발견된다', clause)
    if match:
        text = match[1]
        protected = {f'__PLACE{i}__': phrase for i, phrase in enumerate(PLACES) if '과 ' in phrase}
        for token, phrase in protected.items():
            text = text.replace(phrase, token)
        parts = [protected.get(p, p) for p in re.split(r',\s*|(?:와|과|이나|나)\s+', text)]
        names = [place_name(p, 'ko') for p in parts]
        if all(names):
            return [('acquisition_place', name) for name in names]
    match = re.fullmatch(r'Found (?:in|at) (.+)', clause)
    if match:
        text = match[1]
        protected = {f'__PLACE{i}__': phrase for i, phrase in enumerate(PLACES.values()) if ' and ' in phrase}
        for token, phrase in protected.items():
            text = text.replace(phrase, token)
        parts = [protected.get(p, p) for p in re.split(r',\s*(?:and\s+)?|\s+(?:and|or)\s+', text)]
        parts = [re.sub(r'^(?:in|on|at) ', '', p) for p in parts]
        names = [place_name(p, 'en') for p in parts]
        if all(names):
            return [('acquisition_place', name) for name in names]
    for locale, pattern in (('ko', r'(.+?)(?:와|과|,) 채집으로 구할 수 있다'),
                            ('en', r'Can be obtained from (.+?)(?:,| and) foraging')):
        match = re.fullmatch(pattern, clause)
        if match:
            places = discovery_places(match[1].strip() + '에서 발견된다' if locale == 'ko'
                                      else 'Found in ' + match[1].strip())
            if places:
                return [*places, ('acquisition_method', 'foraging')]
    return None
SKILLS = {
    '목공': 'Carpentry', '요리': 'Cooking', '응급처치': 'FirstAid', '농사': 'Farming', '낚시': 'Fishing',
    '덫 사냥': 'Trapping', '채집': 'Foraging', '재봉술': 'Tailoring', '차량정비': 'Mechanics',
    '금속 용접': 'MetalWelding', '전기공학': 'Electricity',
    'Carpentry': 'Carpentry', 'Cooking': 'Cooking', 'First Aid': 'FirstAid', 'Farming': 'Farming',
    'Fishing': 'Fishing', 'Trapping': 'Trapping', 'Foraging': 'Foraging', 'Tailoring': 'Tailoring',
    'Mechanics': 'Mechanics', 'Metalworking': 'MetalWelding', 'Electrical': 'Electricity', 'Electricity': 'Electricity',
}

WEAR_PHRASES = {
    'head': ('머리에 쓰는 의류나 장신구다', '머리에 착용하는 장비다', 'Clothing or an accessory worn on the head', 'Equipment worn on the head'),
    'upper_body': ('상체에 입는 의류다', 'Clothing worn on the upper body'),
    'lower_body': ('하체에 입는 의류다', 'Clothing worn on the lower body'),
    'outerwear': ('상체에 걸쳐 입는 겉옷이다', 'Outerwear worn on the upper body'),
    'upper_underwear': ('상의로 착용하는 속옷이다', 'Underwear worn on the upper body'),
    'lower_underwear': ('하의로 착용하는 속옷이다', 'Underwear worn on the lower body'),
    'ears': ('귀에 착용하는 장신구다', 'An accessory worn on the ears'),
    'upper_ear': ('귀 윗부분에 착용하는 장신구다', 'An accessory worn on the upper ear'),
    'feet': ('발에 신는 신발류다', 'Footwear worn on the feet'),
    'hands': ('손에 끼는 의류다', 'Clothing worn on the hands'),
    'belly_button': ('배꼽에 착용하는 장신구다', 'An accessory worn at the navel'),
    'dress': ('몸에 입는 원피스형 의류다', 'A one-piece garment worn on the body'),
    'skirt': ('하체에 입는 치마다', 'A skirt worn on the lower body'),
    'necklace': ('목에 착용하는 목걸이다', 'A necklace worn around the neck'),
    'long_necklace': ('목에 착용하는 긴 목걸이다', 'A long necklace worn around the neck'),
    'neck': ('목에 착용하는 장신구다', 'An accessory worn around the neck'),
    'underwear': ('몸에 착용하는 속옷류다', 'Underwear worn on the body'),
    'vest': ('몸통에 걸쳐 입는 조끼류다', 'A vest worn over the torso'),
    'eyes': ('눈 부위에 착용하는 안경류다', 'Eyewear worn over the eyes'),
    'face': ('얼굴에 착용하는 의류나 장비다', 'Clothing or equipment worn on the face'),
}
for _location, _phrases in WEAR_PHRASES.items():
    for _phrase in _phrases:
        CLAUSES[_phrase] = [('wear', _location)]


for _ko, _en, _topics in (
    ('케이크·파이와 쿠키 반죽 제작법을 배우는 잡지다', 'A magazine that teaches recipes for cake, pie and cookie doughs', ('cake_dough', 'pie_dough', 'cookie_dough')),
    ('빵 반죽·비스킷과 피자 제작법을 배우는 잡지다', 'A magazine that teaches recipes for bread dough, biscuits and pizza', ('bread_dough', 'biscuits', 'pizza')),
    ('원격 조종기 제작법을 배우는 잡지다', 'A magazine that teaches how to craft remote controllers', ('remote_controllers',)),
    ('타이머 제작과 부착 방법을 배우는 잡지다', 'A magazine that teaches how to craft and attach timers', ('make_timer', 'attach_timer')),
    ('동작 감지기 부착 방법을 배우는 잡지다', 'A magazine that teaches how to attach motion sensors', ('motion_sensors',)),
    ('원격 격발 장치 제작과 부착 방법을 배우는 잡지다', 'A magazine that teaches how to craft and attach remote triggers', ('make_remote_trigger', 'attach_remote_trigger')),
    ('소음 발생 장치 제작법을 배우는 잡지다', 'A magazine that teaches how to craft a noise maker', ('noise_maker',)),
    ('연막탄 제작법을 배우는 잡지다', 'A magazine that teaches how to craft a smoke bomb', ('smoke_bomb',)),
    ('작물의 흰가루병과 해충을 처리하는 분무액 제작법을 배우는 잡지다', 'A magazine that teaches recipes for mildew and pest treatment sprays for crops', ('mildew_spray', 'pest_spray')),
    ('낚싯대 제작과 수리 방법을 배우는 잡지다', 'A magazine that teaches how to craft and repair fishing rods', ('make_fishing_rod', 'repair_fishing_rod')),
    ('통발 제작과 철사 회수 방법을 배우는 잡지다', 'A magazine that teaches how to craft a fishing net trap and reclaim its wire', ('fishing_net', 'reclaim_net_wire')),
    ('올가미 덫 제작법을 배우는 잡지다', 'A magazine that teaches how to craft a snare trap', ('snare_trap',)),
    ('나무 상자 덫과 막대 덫 제작법을 배우는 잡지다', 'A magazine that teaches how to craft wooden box and stick traps', ('wooden_box_trap', 'stick_trap')),
    ('상자 덫과 철창 덫 제작법을 배우는 잡지다', 'A magazine that teaches how to craft box and cage traps', ('box_trap', 'cage_trap')),
    ('금속 벽과 지붕 제작법을 배우는 잡지다', 'A magazine that teaches how to build metal walls and roofs', ('metal_walls', 'metal_roof')),
    ('금속 보관함 제작법을 배우는 잡지다', 'A magazine that teaches how to build metal containers', ('metal_containers',)),
    ('금속 울타리 제작법을 배우는 잡지다', 'A magazine that teaches how to build metal fences', ('metal_fences',)),
    ('금속판 가공법을 배우는 잡지다', 'A magazine that teaches recipes for making metal sheets', ('metal_sheets',)),
    ('금속 식기와 조리 용기 제작법을 배우는 잡지다', 'A magazine that teaches recipes for metal cutlery and cookware', ('metal_cutlery', 'metal_cookware')),
    ('못·경첩과 작은 금속 도구 제작법을 배우는 잡지다', 'A magazine that teaches recipes for nails, hinges and small metal tools', ('nails', 'hinges', 'small_metal_tools')),
    ('여러 금속 도구와 용기 제작법을 배우는 잡지다', 'A magazine that teaches recipes for metal tools and containers', ('metal_tools', 'smithing_containers')),
    ('탄약·주형과 일부 금속 무기 제작법을 배우는 잡지다', 'A magazine that teaches recipes for ammunition, molds and some metal weapons', ('ammunition', 'ammunition_molds', 'metal_weapons')),
):
    for _phrase in (_ko, _en):
        CLAUSES[_phrase] = [('effect', 'recipe_knowledge', 'gain', topic) for topic in _topics]


# Opening action, named contents and any explicit tool condition are independent
# predecessor propositions; output identity is adjudicated against its own recipe.
for _ko, _en, _output in (
    ('볼로네제', 'bolognese', 'Base.CannedBologneseOpen'),
    ('당근', 'carrots', 'Base.CannedCarrotsOpen'),
    ('칠리', 'chili', 'Base.CannedChiliOpen'),
    ('옥수수', 'corn', 'Base.CannedCornOpen'),
    ('과일 음료', 'fruit drink', 'Base.CannedFruitBeverageOpen'),
    ('과일 칵테일', 'mixed fruit', 'Base.CannedFruitCocktailOpen'),
    ('연유', 'condensed milk', 'Base.CannedMilkOpen'),
    ('복숭아', 'peaches', 'Base.CannedPeachesOpen'),
    ('완두콩', 'peas', 'Base.CannedPeasOpen'),
    ('파인애플', 'pineapple', 'Base.CannedPineappleOpen'),
    ('감자', 'potatoes', 'Base.CannedPotatoOpen'),
    ('토마토', 'tomatoes', 'Base.CannedTomatoOpen'),
):
    _object = _ko + ('를' if _ko in {'볼로네제', '칠리', '옥수수', '과일 음료', '연유', '복숭아', '감자', '토마토'} else '을')
    CLAUSES['개봉해 ' + (_ko + ' 내용물을' if _ko == '볼로네제' else _object) + ' 꺼낼 수 있는 통조림이다'] = [('function', 'unpack_canned_food'), ('output_identity', 'exact_opened_item', _output)]
    _contents = '혼합 과일을' if _ko == '과일 칵테일' else _object
    CLAUSES['통조림 따개로 열어 안에 든 ' + _contents + ' 꺼낼 수 있다'] = [('function', 'unpack_canned_food'), ('condition', 'package_opening', 'can_opener'), ('output_identity', 'exact_opened_item', _output)]
    CLAUSES['Open it with a can opener to get the ' + _en] = [('function', 'unpack_canned_food'), ('condition', 'package_opening', 'can_opener'), ('output_identity', 'exact_opened_item', _output)]
CLAUSES.update({
    '개봉해 콘비프를 꺼낼 수 있는 통조림이다': [('function', 'unpack_canned_food'), ('output_identity', 'exact_opened_item', 'Base.CannedCornedBeefOpen')],
    'A can opened to obtain its corned beef': [('function', 'unpack_canned_food'), ('output_identity', 'exact_opened_item', 'Base.CannedCornedBeefOpen')],
    '개봉해 정어리를 꺼낼 수 있는 통조림이다': [('function', 'unpack_canned_food'), ('output_identity', 'exact_opened_item', 'Base.CannedSardinesOpen')],
    'A can opened to obtain its sardines': [('function', 'unpack_canned_food'), ('output_identity', 'exact_opened_item', 'Base.CannedSardinesOpen')],
    '병을 열어 양배추를 꺼내는 식품이다': [('function', 'unpack_jarred_food'), ('output_identity', 'exact_opened_item', 'farming.Cabbage')],
    'A jar opened to obtain cabbage': [('function', 'unpack_jarred_food'), ('output_identity', 'exact_opened_item', 'farming.Cabbage')],
    '포장을 열어 달걀을 꺼낼 수 있다': [('function', 'unpack_eggs'), ('output_identity', 'exact_opened_item', 'Base.Egg')],
    'Open the carton to take out its eggs': [('function', 'unpack_eggs'), ('output_identity', 'exact_opened_item', 'Base.Egg')],
    '상자를 열어 못을 꺼낼 수 있다': [('function', 'unpack_box_contents'), ('output_identity', 'exact_opened_item', 'Base.Nails')],
    'Can be opened to remove nails': [('function', 'unpack_box_contents'), ('output_identity', 'exact_opened_item', 'Base.Nails')],
    '상자를 열어 나사못을 꺼낼 수 있다': [('function', 'unpack_box_contents'), ('output_identity', 'exact_opened_item', 'Base.Screws')],
    'Can be opened to remove screws': [('function', 'unpack_box_contents'), ('output_identity', 'exact_opened_item', 'Base.Screws')],
    '상자를 열어 종이 클립을 꺼낼 수 있다': [('function', 'unpack_box_contents'), ('output_identity', 'exact_opened_item', 'Base.Paperclip')],
    'Open the box to take out paperclips': [('function', 'unpack_box_contents'), ('output_identity', 'exact_opened_item', 'Base.Paperclip')],
    '상자를 열어 빈 병 여러 개를 꺼낼 수 있다': [('function', 'unpack_box_contents'), ('output_identity', 'exact_opened_item', 'Base.EmptyJar'), ('output_quantity', 'multiple_empty_jars')],
    'Can be opened to remove several empty bottles': [('function', 'unpack_box_contents'), ('output_identity', 'exact_opened_item', 'Base.EmptyJar'), ('output_quantity', 'multiple_empty_jars')],
    '지도에 남긴 주석을 지우는 데 쓰는 도구다': [('function', 'erase_item_map_annotations')],
    '몸에 입거나 걸쳐 착용하는 의류다': [('function', 'wear_body')],
    '상하체에 함께 입는 내의다': [('wear', 'whole_body')],
    '몸에 걸쳐 입는 가운이다': [('wear', 'outerwear')],
    '열쇠를 담아 휴대하는 보관함이다': [('function', 'carry_stored_items'), ('storage_acceptance', 'keys')],
})

for _ko, _en, _property, _direction in (
    ('통증 완화를 위해 복용하는 약이다', 'Medicine taken to relieve pain', 'pain', 'decrease'),
    ('공포를 줄이기 위해 복용하는 약이다', 'Medicine taken to reduce panic', 'panic', 'decrease'),
    ('잠드는 것을 돕기 위해 복용하는 약이다', 'Medicine taken to help with falling asleep', 'sleep_onset', 'facilitate'),
    ('피로를 줄이기 위해 복용한다', 'Taken to reduce fatigue', 'fatigue', 'decrease')):
    for _phrase in (_ko, _en):
        CLAUSES[_phrase] = [('function', 'take_pills'), ('effect', _property, _direction)]
for _phrase in ('시간을 두고 불행감을 줄이는 데 쓰는 약이다', 'Medicine used to reduce unhappiness over time'):
    CLAUSES[_phrase] = [('function', 'take_pills'), ('effect', 'unhappiness', 'decrease'), ('effect_timing', 'unhappiness', 'delayed')]

for _ko, _en, _atoms in (
    ('옷이나 천 제품에 다는 단추다', 'A button attached to clothing or fabric goods', [('function', 'attach_button_to_clothing_or_fabric')]),
    ('머리를 빗고 정돈할 때 쓰는 빗이다', 'A comb used to arrange and groom hair', [('function', 'comb_hair'), ('function', 'groom_hair')]),
    ('개가 씹는 장난감이다', 'A chew toy for dogs', [('function', 'dog_chew_toy')]),
    ('사진이나 그림을 넣어 두는 액자다', 'A frame used to hold a photograph or picture', [('function', 'frame_photograph'), ('function', 'frame_picture')]),
    ('반려견에게 매는 목줄이다', 'A collar worn by a pet dog', [('function', 'equip_pet_dog_collar')]),
    ('고무 오리 모양의 장난감이다', 'A toy shaped like a rubber duck', [('identity_label', '고무 오리')]),
    ('이를 닦을 때 쓰는 칫솔이다', 'A toothbrush used to brush teeth', [('function', 'brush_teeth')]),
    ('이를 닦을 때 쓰는 치약이다', 'Toothpaste used to brush teeth', [('function', 'brush_teeth')]),
    ('끈 형태의 재료다', 'A cord-like material', [('identity_label', '끈'), ('role_unspecified_context', 'material')]),
    ('Build 41에서는 특별한 제작 용도가 없는 잡동사니이다', 'Junk with no specific crafting use in Build 41', [('identity_label', '잡동사니'), ('negative_scope', 'crafting_use', 'Build 41')]),
    ('생활 관리 작업에서 몸과 주변을 닦고 정리하거나 실내에 필요한 소모품을 챙길 때 다룬다',
     'Handled while cleaning the body or surroundings and gathering household consumables',
     [('function', 'clean_body'), ('function', 'clean_surroundings'), ('function', 'organize_household_items'), ('function', 'gather_household_supplies')]),
):
    for _phrase in (_ko, _en):
        CLAUSES[_phrase] = _atoms

CLAUSES['Handled while cleaning the body or surroundings and gathering household consumables'] = [('function', 'clean_body'), ('function', 'clean_surroundings'), ('function', 'gather_household_supplies')]

def spans(text):
    """Independent surface boundaries; decimal ammunition IDs stay intact."""
    start = 0
    for match in re.finditer(r'(?:[.!?](?=\s|$)|\n+)', text):
        end = match.end()
        if end > start:
            yield start, end, text[start:end]
        start = end
    if start < len(text):
        yield start, len(text), text[start:]


IDENTITY_MEANINGS = {
    '젖은 목욕 수건': [('identity_label', '목욕 수건'), ('state_label', 'wet_towel')],
    '젖은 행주': [('identity_label', '행주'), ('state_label', 'wet_towel')],
    '무기 겸용 도구': [('identity_label', '도구'), ('function', 'attack_as_weapon')],
    '제작 무기': [('identity_label', '무기'), ('acquisition_process', 'craft')],
    '조리 재료': [('role', 'food_preparation', 'ingredient')],
    '소모성 재료': [('role_unspecified_context', 'material'), ('consumption_property', 'consumable')],
    '조리 도구': [('role', 'food_preparation', 'tool')],
    '원예 도구': [('role', 'gardening', 'tool')],
    '원예 소모품': [('context_label', 'gardening'), ('consumption_property', 'consumable')],
    '의료 소모품': [('context_label', 'medical_use'), ('consumption_property', 'consumable')],
    '차량 정비 소모품': [('context_label', 'vehicle_maintenance'), ('consumption_property', 'consumable')],
    '접이식 우산': [('identity_label', '우산'), ('function', 'fold_umbrella')],
    '빈 병': [('identity_label', '병'), ('state_label', 'empty_container')],
    '기념품 인형': [('identity_label', '인형'), ('context_label', 'souvenir')],
}

for _color in ('검은', '금발', '파란', '초록', '연갈색', '분홍', '빨간', '흰색', '노란'):
    IDENTITY_MEANINGS[_color + ' 염색약'] = [('identity_label', '염색약'), ('visual_effect', 'dye_color', _color)]

for _first, _second in (
    ('흰가루병이 있는 작물의 문제 처리 메뉴에서 사용량을 고른다', '분무액의 남은 사용량이 필요하며, 다른 병을 함께 치료하는 분무액은 아니다'),
    ('해충이 있는 작물의 문제 처리 메뉴에서 사용량을 고른다', '분무액의 남은 사용량이 필요하며, 흰가루병은 별도 분무액으로 처리한다'),
):
    CLAUSES[_first + '. ' + _second] = CLAUSES[_first] + CLAUSES[_second]


CLAUSES.update({
    '모닥불 자리를 설치하는 데 쓰는 키트다': [('function', 'place_campfire')],
    'A kit used to place a campfire': [('function', 'place_campfire')],
    '텐트를 설치하는 데 쓰는 키트다': [('function', 'pitch_tent')],
    'A kit used to pitch a tent': [('function', 'pitch_tent')],
    'A material used to make a tent kit': [('role', 'tent_kit_making', 'material')],
    '불씨를 만들 때 쓰는 부싯돌이다': [('function', 'make_spark')],
    'Flint used to make a spark': [('function', 'make_spark')],
    '도구다': [('identity_label', '도구')],
    '녹음된 CD를 재생해 듣는 기기다': [('function', 'play_cd_recording')],
    'A device used to play recorded CDs': [('function', 'play_cd_recording')],
    '라디오 방송을 듣거나 녹음된 CD를 재생하는 기기다': [('function', 'receive_radio_signal'), ('function', 'play_cd_recording')],
    'A radio used to tune in to broadcasts': [('function', 'tune_radio'), ('function', 'receive_radio_signal')],
    'TV 방송을 시청하는 기기다': [('function', 'receive_tv_signal')],
    'A television used to watch broadcasts': [('function', 'receive_tv_signal')],
    'A television used to watch broadcasts or play recorded VHS tapes': [('function', 'receive_tv_signal'), ('function', 'play_vhs')],
})


# Remaining predecessor surfaces are decomposed independently of whether their
# claims have a source answer. Coordination retains each role/function; these
# pairs do not admit facts or certify the named crafting output.
for _ko, _en, _atoms in (
    ('휴대 작업에서 메거나 들고 다니며 물건을 담아 옮길 때 쓴다', 'Used to carry items by wearing or holding it', [('function', 'carry_stored_items'), ('condition', 'carrying', 'worn_or_held')]),
    ('케이크나 파이 반죽을 담아 굽기 준비를 하는 틀이다', 'A pan used to prepare cake or pie dough for baking', [('role', 'cake_preparation', 'container'), ('role', 'pie_preparation', 'container')]),
    ('일부 반죽과 튀김 요리에 넣는 재료다', 'An ingredient used in some doughs and fried dishes', [('role', 'dough_preparation', 'ingredient'), ('role', 'fried_food_preparation', 'ingredient')]),
    ('쿠키 반죽을 준비할 때 쓰는 베이킹 트레이다', 'A baking tray used to prepare cookie dough', [('role', 'cookie_preparation', 'container')]),
    ('못을 사용하는 목공 구조물을 만드는 데 쓸 수 있는 망치다', 'A hammer usable for building wooden structures with nails', [('role', 'construction', 'tool'), ('condition', 'construction', 'wooden_structure_with_nails')]),
    ('손전등 등 건전지를 사용하는 기기에 전원을 공급한다', 'Supplies power to battery-operated devices such as flashlights', [('role', 'portable_device_power', 'power_supply'), ('example_target', 'portable_device_power', 'flashlight')]),
    ('텀블러에 따라 마시는 맥주다', 'Beer poured into a tumbler for drinking', [('function', 'drink_food_contents'), ('preparation_form', 'beer_in_tumbler')]),
    ('컵에 따라 마시는 맥주다', 'Beer poured into a cup for drinking', [('function', 'drink_food_contents'), ('preparation_form', 'beer_in_cup')]),
    ('화로에 바람을 불어넣어 온도를 높일 때 쓰는 풀무다', "Bellows used to raise a forge's temperature by forcing in air", [('function', 'blow_forge_air'), ('effect', 'forge_temperature', 'increase')]),
    ('텀블러에 재료를 섞어 만들어 마시는 음료다', 'A drink mixed from ingredients in a tumbler', [('function', 'drink_food_contents'), ('preparation_form', 'mixed_drink_in_tumbler')]),
    ('컵에 재료를 섞어 만들어 마시는 음료다', 'A drink mixed from ingredients in a cup', [('function', 'drink_food_contents'), ('preparation_form', 'mixed_drink_in_cup')]),
    ('조리에 넣는 재료다', 'An ingredient used in cooking', [('role', 'food_preparation', 'ingredient')]),
    ('음식을 담거나 반죽을 섞는 데 쓰는 그릇이다', 'A bowl used to hold food or mix dough', [('role', 'food_preparation', 'container'), ('role', 'dough_preparation', 'container')]),
    ('석고 마감이 가능한 구조물에 바르는 반죽이다', 'Plaster used to finish structures that support plastering', [('function', 'plaster_supported_structure')]),
    ('틀에 담아 케이크를 준비하는 반죽이다', 'Batter placed in a baking pan to prepare a cake', [('role', 'cake_preparation', 'ingredient'), ('condition', 'cake_preparation', 'baking_pan')]),
    ('불을 붙여 빛을 내는 양초다', 'A candle that provides light when lit', [('function', 'light_candle'), ('effect', 'illumination', 'provide'), ('condition', 'illumination', 'lit')]),
    ('포장을 열어 사탕을 꺼내는 식품이다', 'A package opened to obtain candy', [('function', 'unpack_food'), ('output_identity', 'food', 'candy')]),
    ('개봉하거나 냄비에 담아 수프를 준비하는 데 쓰는 버섯 수프 통조림이다', 'Canned mushroom soup opened or put in a pot to prepare soup', [('function', 'unpack_canned_food'), ('role', 'soup_preparation', 'ingredient'), ('condition', 'soup_preparation', 'cooking_pot')]),
    ('차량에서 분리한 배터리의 충전량을 회복할 때 사용된다', 'Used to recharge a battery removed from a vehicle', [('function', 'charge_vehicle_battery'), ('condition', 'battery_charging', 'removed_from_vehicle')]),
    ('모닥불이나 숯불 바비큐에 보충하는 연료다', 'Fuel added to campfires or charcoal barbecues', [('function', 'supply_campfire_fuel'), ('function', 'supply_charcoal_barbecue_fuel')]),
    ('용광로에 연료로 넣어 쓰는 석탄이다', 'Coal used as furnace fuel', [('role', 'furnace_fueling', 'fuel')]),
    ('커피 음료를 만드는 데 넣는 재료다', 'An ingredient used to make coffee drinks', [('role', 'coffee_preparation', 'ingredient')]),
    ('물이 든 머그잔이나 찻잔에서 음료 준비 메뉴를 사용해 커피를 넣는다', 'Use the beverage preparation menu on a water-filled mug or teacup to add coffee', [('recipe_menu', 'coffee_preparation', 'water_filled_mug_or_teacup'), ('recipe_relation', 'coffee_preparation', 'add_coffee')]),
    ('이미 준비한 호환 음료에도 해당 메뉴가 허용하는 재료를 추가할 수 있다', 'Compatible prepared drinks can also receive ingredients allowed by that menu', [('function', 'add_food_ingredients'), ('condition', 'beverage_preparation', 'compatible_prepared_drink')]),
    ('연막탄 제작에 들어가는 재료다', 'Material used to make a smoke bomb', [('role', 'smoke_bomb_crafting', 'material')]),
    ('케이크나 파이 등의 반죽을 만드는 데 쓰는 가루 재료다', 'A flour ingredient used to make dough or batter for foods such as cakes and pies', [('role', 'cake_preparation', 'ingredient'), ('role', 'pie_preparation', 'ingredient')]),
    ('바리케이드를 제거하는 데 쓸 수 있는 도구다', 'A tool usable for removing barricades', [('function', 'remove_barricade')]),
    ('개봉해 내용물을 꺼낼 수 있는 사료 통조림이다', 'Canned pet food that can be opened to obtain its contents', [('function', 'unpack_canned_food'), ('identity_label', '사료 통조림')]),
    ('장치를 조립하거나 도구를 창에 붙일 때 쓰는 접착 재료다', 'An adhesive material used to assemble devices or attach tools to spears', [('role', 'device_assembly', 'material'), ('role', 'spear_upgrade', 'material')]),
    ('발전기 연결과 수리에 필요한 지식을 배우는 잡지다', 'A magazine that teaches knowledge needed to connect and repair generators', [('learning', 'generator_connection'), ('learning', 'generator_repair')]),
    ('연료를 담아 운반하는 데 쓰는 빈 용기다', 'An empty container used to hold and carry fuel', [('function', 'store_fuel'), ('function', 'carry_fuel'), ('state_label', 'empty_container')]),
    ('차량 엔진의 상태를 수리하는 데 쓰는 부품이다', 'Parts used to repair the condition of a vehicle engine', [('function', 'repair_vehicle_engine')]),
    ('낚싯대 제작과 수리에 들어가는 낚싯줄 재료다', 'Fishing line used to make or repair fishing rods', [('role', 'fishing_rod_crafting', 'material'), ('role', 'fishing_rod_repair', 'material')]),
    ('물에 설치해 미끼용 작은 물고기를 잡는 데 쓰는 통발이다', 'A fishing net trap placed in water to catch bait fish', [('function', 'place_fishing_net'), ('function', 'catch_bait_fish'), ('condition', 'net_fishing', 'water')]),
    ('가까운 물 타일에 설치한 뒤 시간이 지나면 확인한다', 'Place it on a nearby water tile and check it after time has passed', [('function', 'place_fishing_net'), ('function', 'check_fishing_net'), ('condition', 'net_fishing', 'near_water'), ('condition', 'net_fishing', 'elapsed_time')]),
    ('미끼 물고기를 얻을 수 있지만 포획은 확정되지 않으며, 오래 둔 통발은 확인할 때 부서질 수 있다', 'It may yield bait fish, but a catch is not guaranteed and a net left out for a long time may break when checked', [('output_identity', 'net_fishing', 'bait_fish'), ('condition', 'net_fishing', 'catch_not_guaranteed'), ('hazard', 'net_breakage_after_time')]),
    ('반죽과 일부 튀김 요리에 들어가는 재료다', 'An ingredient used in doughs and some fried dishes', [('role', 'dough_preparation', 'ingredient'), ('role', 'fried_food_preparation', 'ingredient')]),
    ('던져 사용하는 공이다', 'A ball used by throwing it', [('function', 'throw_item'), ('identity_label', '공')]),
    ('통나무를 판자로 켜는 데 쓰는 톱이다', 'A saw used to turn logs into planks', [('role', 'log_sawing', 'tool')]),
    ('설치하면 주변 기기에 전기를 공급한다', 'Once installed, it can supply electricity to nearby devices', [('function', 'supply_generator_power'), ('condition', 'generator_power', 'installed'), ('target_scope', 'generator_power', 'nearby_devices')]),
    ('원격 조종기나 타이머 같은 장치를 조립할 때 쓰는 접착제다', 'An adhesive used to assemble devices such as remote controllers and timers', [('role', 'remote_controller_crafting', 'material'), ('role', 'timer_crafting', 'material')]),
    ('물과 섞어 그레이비를 만드는 데 쓰는 재료다', 'An ingredient mixed with water to make gravy', [('role', 'gravy_preparation', 'ingredient'), ('condition', 'gravy_preparation', 'water')]),
    ('재료를 넣어 볶음 요리를 준비하는 팬이다', 'A pan used to prepare stir-fried dishes by adding ingredients', [('role', 'stir_fry_preparation', 'base')]),
    ('파이프 폭탄을 만드는 데 쓰는 재료다', 'Material used to make a pipe bomb', [('role', 'pipe_bomb_crafting', 'material')]),
    ('에어로졸 폭탄을 만드는 데 쓰는 재료다', 'Material used to make an aerosol bomb', [('role', 'aerosol_bomb_crafting', 'material')]),
    ('에어로졸 폭탄 제작에 들어가는 재료다', 'Material used to make an aerosol bomb', [('role', 'aerosol_bomb_crafting', 'material')]),
    ('건설이나 제작 준비 작업에서 자재를 깎거나 맞춰 다른 도구 부품으로 만들 때 쓴다', 'Used to shape or fit material into other tool parts during construction or crafting preparation', [('function', 'shape_tool_parts'), ('function', 'fit_tool_parts'), ('context', 'construction_or_crafting')]),
    ('야생 열매와 버섯의 독성을 구별하는 지식을 배우는 잡지다', 'A magazine that teaches how to identify poisonous wild berries and mushrooms', [('learning', 'identify_poisonous_berries'), ('learning', 'identify_poisonous_mushrooms')]),
    ('분해해 동작 감지 부품을 회수하는 데 쓸 수 있다', 'Can be dismantled to recover a motion sensor', [('function', 'dismantle_electronics'), ('output_identity', 'electronic_salvage', 'motion_sensor')]),
    ('금속 제작 작업에서 녹이거나 두드려 다른 부품으로 만들 때 쓴다', 'Used in metal crafting to melt or hammer material into other parts', [('role', 'metal_melting', 'material'), ('role', 'metal_forging', 'material')]),
    ('타이어·브레이크 등 일부 차량 부품을 탈착할 때 사용된다', 'Used to install or remove certain vehicle parts, such as tires and brakes', [('role', 'vehicle_tire_exchange', 'tool'), ('role', 'vehicle_brake_exchange', 'tool')]),
    ('조리나 식사 준비 작업에서 먹거나 나눠 먹을 때 쓴다', 'Food used while preparing or eating a meal', [('function', 'eat_food'), ('role', 'food_preparation', 'ingredient')]),
    ('톱으로 판자를 만들거나 모닥불 키트를 만드는 데 쓰는 통나무다', 'A log used to make planks with a saw or to craft a campfire kit', [('role', 'log_sawing', 'material'), ('role', 'campfire_kit_preparation', 'material'), ('condition', 'log_sawing', 'saw')]),
    ('차량 타이어를 탈착할 때 사용된다', 'Used to install or remove vehicle tires', [('role', 'vehicle_tire_exchange', 'tool')]),
    ('식재료를 자르거나 작은 동물을 손질하며, 근접 무기로도 쓸 수 있다', 'Used to cut ingredients or butcher small animals, and can also serve as a melee weapon', [('function', 'cut_food'), ('function', 'butcher_small_animals'), ('function', 'melee_attack')]),
    ('일반 차량의 정비 작업에 필요한 지식을 배우는 잡지다', 'A magazine that teaches knowledge required for work on standard vehicles', [('learning', 'standard_vehicle_mechanics')]),
    ('상용 차량의 정비 작업에 필요한 지식을 배우는 잡지다', 'A magazine that teaches knowledge required for work on commercial vehicles', [('learning', 'commercial_vehicle_mechanics')]),
    ('고성능 차량의 정비 작업에 필요한 지식을 배우는 잡지다', 'A magazine that teaches knowledge required for work on performance vehicles', [('learning', 'performance_vehicle_mechanics')]),
    ('금속 바리케이드를 만드는 데 쓰는 금속봉이다', 'A metal bar used to make metal barricades', [('role', 'metal_barricading', 'material')]),
    ('물을 받거나 장작을 태워 숯을 만드는 데 쓰는 금속 드럼통이다', 'A metal drum used to collect water or burn wood into charcoal', [('function', 'collect_water'), ('function', 'burn_logs_to_charcoal')]),
    ('금속 가공 작업에서 재료로 쓰이는 금속 파이프다', 'A metal pipe used as material in metalworking', [('role', 'metalworking', 'material')]),
    ('약초를 찧어 찜질제를 만드는 데 쓰는 도구다', 'A tool used to grind herbs into poultices', [('role', 'poultice_preparation', 'tool')]),
    ('호환되는 장치에 동작 감지 기능을 붙이는 부품이다', 'A component used to add motion sensing to compatible devices', [('role', 'motion_sensor_attachment', 'material')]),
    ('머핀 반죽을 준비하는 데 쓰는 틀이다', 'A tray used to prepare muffin batter', [('role', 'muffin_preparation', 'container')]),
    ('비스킷을 구운 뒤 나누어 꺼내는 데 쓰는 반죽이 든 틀이다', 'A tray of dough used to bake biscuits and remove them as portions', [('role', 'biscuit_preparation', 'base'), ('function', 'portion_biscuits')]),
    ('교란 작업에서 소리를 내는 장치를 설치하거나 던질 때 다룬다', 'Handled when placing or throwing a noise-making device as a distraction', [('function', 'place_noise_device'), ('function', 'throw_noise_device'), ('effect', 'noise', 'distraction')]),
    ('페인트를 사용해 미장한 벽이나 도색 가능한 표면을 칠할 때 사용된다', 'Used with paint to color plastered walls or other paintable surfaces', [('function', 'paint_supported_surface'), ('condition', 'surface_painting', 'paint_and_compatible_surface')]),
    ('물과 섞어 팬케이크를 만드는 데 쓰는 재료다', 'An ingredient mixed with water to make pancakes', [('role', 'pancake_preparation', 'ingredient'), ('condition', 'pancake_preparation', 'water')]),
    ('나뭇가지나 막대와 함께 모닥불에 불을 붙이는 데 쓴다', 'Used with a branch or stick to kindle a campfire', [('function', 'light_campfire'), ('condition', 'campfire_lighting', 'branch_or_stick')]),
    ('틀에 담아 파이를 준비하는 반죽이다', 'Dough placed in a baking pan to prepare a pie', [('role', 'pie_preparation', 'ingredient'), ('condition', 'pie_preparation', 'baking_pan')]),
    ('모닥불 등에 보충하는 연료로 쓴다', 'Used as fuel for fires such as campfires', [('function', 'supply_campfire_fuel'), ('role', 'other_fire_fueling', 'fuel')]),
    ('목공과 여러 제작 작업에 들어가는 판자 재료다', 'Plank material used in carpentry and other crafting', [('role', 'woodworking', 'material'), ('role_unspecified_context', 'crafting_material')]),
    ('물과 섞어 석고 반죽이 든 양동이를 만드는 재료다', 'A material mixed with water to make a bucket of plaster', [('role', 'plaster_preparation', 'material'), ('condition', 'plaster_preparation', 'water')]),
    ('허기를 줄일 수 있지만 갈증을 늘릴 수 있는 식품이다', 'A food that can reduce hunger but may increase thirst', [('effect', 'hunger', 'decrease'), ('effect', 'thirst', 'increase')]),
    ('수프를 만들거나 담는 데 쓰는 냄비다', 'A pot used to prepare or hold soup', [('role', 'soup_preparation', 'container')]),
    ('용접용 토치를 충전할 때 쓰는 프로판 통이다', 'A propane tank used to refill a welding torch', [('role', 'torch_refilling', 'fuel_supply')]),
    ('원격 방아쇠 장치를 만드는 전자 부품이다', 'An electronic component used to make a remote trigger', [('role', 'remote_trigger_crafting', 'material')]),
    ('원격 조종기를 만드는 데 쓰는 전자 부품이다', 'An electronic component used to make a remote controller', [('role', 'remote_controller_crafting', 'material')]),
    ('재료를 넣어 구울 요리를 준비하는 팬이다', 'A pan used to prepare roasting dishes by adding ingredients', [('role', 'roasting_preparation', 'base')]),
    ('반죽을 펴서 파이·피자·빵 등을 준비할 때 쓰는 도구다', 'A tool used to roll dough when preparing foods such as pies, pizzas and bread', [('role', 'pie_preparation', 'tool'), ('role', 'pizza_preparation', 'tool'), ('role', 'bread_preparation', 'tool')]),
    ('묶거나 연결이 필요한 제작 작업에 쓰는 로프 재료다', 'Rope material used in crafting that requires tying or connecting', [('role', 'binding_crafting', 'material'), ('role', 'connecting_crafting', 'material')]),
    ('건전지를 넣거나 뺄 수 있는 고무 오리다', 'A rubber duck whose battery can be inserted or removed', [('function', 'insert_device_battery'), ('function', 'remove_device_battery')]),
    ('톱질에 쓰며 산탄총 총열 절단 작업에도 쓰는 도구다', 'A tool used for sawing and cutting down shotgun barrels', [('role', 'sawing', 'tool'), ('role', 'shotgun_sawing', 'tool')]),
    ('일부 손상된 무기나 도구를 수리할 때 사용된다', 'Used to repair certain damaged weapons or tools', [('role', 'repair', 'repair_material')]),
    ('금속 구조물이나 일부 금속 제작물을 만드는 재료로 사용된다', 'Used as material for metal structures and certain metal items', [('role', 'metal_welding_construction', 'material'), ('role', 'metalworking', 'material')]),
    ('석기 도구를 만들거나 창을 깎는 데 쓰는 돌이다', 'A stone used to make stone tools or carve a spear', [('role', 'tool_crafting', 'material'), ('role', 'spear_crafting', 'tool')]),
    ('매트리스나 모닥불 키트를 만드는 데 쓰는 천이다', 'Fabric used to make a mattress or campfire kit', [('role', 'mattress_preparation', 'material'), ('role', 'campfire_kit_preparation', 'material')]),
    ('반죽이나 오믈렛 등을 준비할 때 쓰는 조리 도구다', 'A cooking utensil used to prepare foods such as dough and omelettes', [('role', 'dough_preparation', 'tool'), ('role', 'omelette_preparation', 'tool')]),
    ('분해해 증폭기 부품을 회수하는 데 쓸 수 있다', 'Can be dismantled to recover an amplifier component', [('function', 'dismantle_electronics'), ('output_identity', 'electronic_salvage', 'amplifier')]),
    ('차를 우릴 때 쓰는 재료다', 'Material used to brew tea', [('role', 'tea_preparation', 'ingredient')]),
    ('타이머 장치를 만드는 전자 부품이다', 'An electronic component used to make a timer', [('role', 'timer_crafting', 'material')]),
    ('호환되는 폭발물 등에 타이머를 붙이는 데 쓰는 부품이다', 'A component used to attach a timer to compatible explosives', [('role', 'timer_attachment', 'material')]),
    ('통조림을 여는 데 쓰는 도구다', 'A tool used to open cans', [('role', 'package_opening', 'tool')]),
    ('개봉하거나 그릇에 담아 콩 요리를 준비하는 데 쓰는 통조림이다', 'Canned beans opened or put in a bowl to prepare a bean dish', [('function', 'unpack_canned_food'), ('role', 'bean_preparation', 'ingredient'), ('condition', 'bean_preparation', 'bowl')]),
    ('개봉하거나 냄비에 담아 수프를 준비하는 데 쓰는 통조림이다', 'Canned soup opened or put in a pot to prepare soup', [('function', 'unpack_canned_food'), ('role', 'soup_preparation', 'ingredient'), ('condition', 'soup_preparation', 'cooking_pot')]),
    ('도구나 기타 물건을 넣어 운반하는 휴대용 보관함이다', 'A portable container for carrying tools or other items', [('function', 'store_and_retrieve_items'), ('function', 'carry_stored_items')]),
    ('즉석 도구와 창 또는 부목을 만드는 데 쓰는 나뭇가지다', 'A branch used to make improvised tools, spears or splints', [('role', 'tool_crafting', 'material'), ('role', 'spear_crafting', 'material'), ('role', 'splint_crafting', 'material')]),
    ('호환되는 장치를 원격 조종할 수 있게 개조하는 부품이다', 'A component used to make compatible devices remotely controllable', [('role', 'remote_trigger_attachment', 'material')]),
    ('개봉해 참치를 꺼낼 수 있는 통조림이다', 'A can opened to obtain its tuna', [('function', 'unpack_canned_food'), ('output_identity', 'food', 'tuna')]),
    ('모닥불 재료를 만드는 데 쓰는 잔가지다', 'Twigs used to make campfire materials', [('role', 'campfire_kit_preparation', 'material')]),
    ('금속 해체 작업에서 남는, 재료로 쓸 수 없는 금속 조각이다', 'Scrap left by metal dismantling that cannot be used as material', [('acquisition_process', 'metal_dismantling'), ('negative_role', 'crafting', 'material')]),
    ('모닥불 연료로 쓸 수 있는 나무 조각이다', 'A piece of wood usable as campfire fuel', [('function', 'supply_campfire_fuel')]),
    ('채소 병조림을 만드는 데 들어가는 재료다', 'An ingredient used to prepare jars of vegetables', [('role', 'vegetable_jarring', 'material')]),
    ('물을 담아 운반하는 데 쓰는 빈 병이다', 'An empty bottle used to hold and carry water', [('function', 'store_water'), ('function', 'carry_water'), ('state_label', 'empty_container')]),
    ('쌀이나 파스타 요리를 준비하는 데 쓰는 물이 든 냄비다', 'A water-filled cooking pot used to prepare rice or pasta dishes', [('role', 'rice_preparation', 'container'), ('role', 'pasta_preparation', 'container'), ('state_label', 'water_filled_container')]),
    ('쌀이나 파스타 요리를 준비하는 데 쓰는 물이 든 소스팬이다', 'A water-filled saucepan used to prepare rice or pasta dishes', [('role', 'rice_preparation', 'container'), ('role', 'pasta_preparation', 'container'), ('state_label', 'water_filled_container')]),
    ('잘라내거나 쪼개서 먹을 부분을 준비하는 과일이다', 'A fruit that is sliced or smashed into portions for eating', [('function', 'slice_fruit'), ('function', 'smash_fruit'), ('output_purpose', 'portions_for_eating')]),
    ('온몸에 걸쳐 입을 수 있다', 'You can wear it over your whole body', [('wear', 'whole_body')]),
    ('일부 금속 작업에 필요한 용접 마스크다', 'A welding mask required for some metalworking tasks', [('role', 'metalworking', 'tool')]),
    ('와인잔에 따라 마시는 와인이다', 'Wine poured into a wine glass for drinking', [('function', 'drink_food_contents'), ('preparation_form', 'wine_in_glass')]),
    ('거리를 둔 채 찌르거나 밀어낼 수 있다', 'Use it to thrust or shove from a distance', [('function', 'thrust_attack'), ('function', 'shove_attack'), ('combat_property', 'reach')]),
    ('호환되는 도구나 무기를 수리하는 데 쓰는 접착제다', 'An adhesive used to repair compatible tools or weapons', [('role', 'repair', 'repair_material')]),
    ('빵 등의 반죽을 만드는 데 들어가는 재료다', 'An ingredient used to make dough such as bread dough', [('role', 'bread_preparation', 'ingredient')]),
):
    CLAUSES[_ko] = CLAUSES[_en] = _atoms


# Acquisition clauses retain process, input alternatives and tools separately.
# These are predecessor assertions only; adjudication must bind their evidence.
for _ko, _en, _atoms in (
    ('스피커를 분해해 구한다', 'Obtained by dismantling a speaker', [('acquisition_process', 'dismantle_speaker')]),
    ('나뭇가지와 깎인 돌, 천 조각으로 제작한다', 'Crafted from a branch, chipped stone, and a ripped sheet', [('acquisition_process', 'craft'), ('acquisition_material', 'TreeBranch'), ('acquisition_material', 'SharpedStone'), ('acquisition_material', 'RippedSheets')]),
    ('야구 방망이와 못, 망치로 제작한다', 'Crafted from a baseball bat and nails with a hammer', [('acquisition_process', 'craft'), ('acquisition_material', 'BaseballBat'), ('acquisition_material', 'Nails'), ('acquisition_tool', 'Hammer')]),
    ('유리컵에 음료를 따라 만든다', 'Made by pouring a drink into a glass', [('acquisition_process', 'pour_drink'), ('acquisition_container', 'glass')]),
    ('플라스틱 컵에 음료를 따라 만든다', 'Made by pouring a drink into a plastic cup', [('acquisition_process', 'pour_drink'), ('acquisition_container', 'plastic_cup')]),
    ('빵을 잘라 얻는다', 'Obtained by slicing bread', [('acquisition_process', 'slice_bread')]),
    ('양초에 불을 붙여 얻는다', 'Obtained by lighting a candle', [('acquisition_process', 'light_candle')]),
    ('퇴비를 담아 얻는다', 'Obtained by filling it with compost', [('acquisition_process', 'fill_ground_bag', 'compost')]),
    ('쌍열 산탄총과 톱으로 절단해 만든다', 'Made by cutting down a double-barrel shotgun with a saw', [('acquisition_process', 'saw_off_shotgun'), ('acquisition_material', 'DoubleBarrelShotgun'), ('acquisition_tool', 'saw')]),
    ('전자기기를 분해해 구한다', 'Obtained by dismantling electronic devices', [('acquisition_process', 'dismantle_electronics')]),
    ('휘발유와 천 조각과 빈 병을 조합해 만든다', 'Made by combining gasoline, a ripped sheet, and an empty bottle', [('acquisition_process', 'craft'), ('acquisition_material', 'gasoline'), ('acquisition_material', 'RippedSheets'), ('acquisition_material', 'empty_bottle')]),
    ('나뭇가지와 깎인 돌, 천 조각이나 끈으로 제작한다', 'Crafted from a branch, chipped stone, and a ripped sheet or cord', [('acquisition_process', 'craft'), ('acquisition_material', 'TreeBranch'), ('acquisition_material', 'SharpedStone'), ('acquisition_alternative_materials', 'RippedSheets', 'cord')]),
    ('탄약을 분해해 구한다', 'Obtained by dismantling ammunition', [('acquisition_process', 'dismantle_ammunition')]),
    ('호박을 가공해 만든다', 'Made by processing a pumpkin', [('acquisition_process', 'process_pumpkin')]),
    ('나뭇가지와 돌, 천 조각으로 제작한다', 'Crafted from a branch, stone, and a ripped sheet', [('acquisition_process', 'craft'), ('acquisition_material', 'TreeBranch'), ('acquisition_material', 'Stone'), ('acquisition_material', 'RippedSheets')]),
    ('신문으로 제작한다', 'Crafted from newspaper', [('acquisition_process', 'craft'), ('acquisition_material', 'Newspaper')]),
    ('알루미늄으로 제작한다', 'Crafted from aluminum', [('acquisition_process', 'craft'), ('acquisition_material', 'Aluminum')]),
    ('술병이나 빈 병, 천 조각과 휘발유로 제작한다', 'Crafted from a liquor or empty bottle, a ripped sheet, and gasoline', [('acquisition_process', 'craft'), ('acquisition_alternative_materials', 'liquor_bottle', 'empty_bottle'), ('acquisition_material', 'RippedSheets'), ('acquisition_material', 'gasoline')]),
    ('못 상자를 열어 구한다', 'Obtained by opening a box of nails', [('acquisition_process', 'open_nails_box')]),
    ('전자 부품과 증폭기를 조합해 만든다', 'Made by combining electronic parts and an amplifier', [('acquisition_process', 'craft'), ('acquisition_material', 'ElectronicsScrap'), ('acquisition_material', 'Amplifier')]),
    ('나무 판재를 가공해 얻는다', 'Obtained by processing lumber', [('acquisition_process', 'process_lumber')]),
    ('빈 표백제 병에 휘발유를 담아 만든다', 'Made by filling an empty bleach bottle with gasoline', [('acquisition_process', 'fill_gasoline'), ('acquisition_container', 'BleachEmpty')]),
    ('빈 연료통에 휘발유를 담아 만든다', 'Made by filling an empty gas can with gasoline', [('acquisition_process', 'fill_gasoline'), ('acquisition_container', 'EmptyPetrolCan')]),
    ('빈 음료수 병에 휘발유를 담아 만든다', 'Made by filling an empty pop bottle with gasoline', [('acquisition_process', 'fill_gasoline'), ('acquisition_container', 'PopBottleEmpty')]),
    ('전자 부품과 금속 파이프, 화약과 끈으로 제작한다', 'Crafted from electronic parts, a metal pipe, gunpowder, and cord', [('acquisition_process', 'craft'), ('acquisition_material', 'ElectronicsScrap'), ('acquisition_material', 'MetalPipe'), ('acquisition_material', 'GunPowder'), ('acquisition_material', 'cord')]),
    ('통나무를 톱으로 가공해 얻는다', 'Obtained by sawing a log', [('acquisition_process', 'saw_log'), ('acquisition_tool', 'saw')]),
    ('판자와 못, 망치로 제작한다', 'Crafted from planks and nails with a hammer', [('acquisition_process', 'craft'), ('acquisition_material', 'Plank'), ('acquisition_material', 'Nails'), ('acquisition_tool', 'Hammer')]),
    ('TV 리모컨을 분해해 구한다', 'Obtained by dismantling a TV remote', [('acquisition_process', 'dismantle_tv_remote')]),
    ('산탄총과 톱으로 절단해 만든다', 'Made by cutting down a shotgun with a saw', [('acquisition_process', 'saw_off_shotgun'), ('acquisition_material', 'Shotgun'), ('acquisition_tool', 'saw')]),
    ('빈 술병이나 빈 맥주병을 깨뜨려 만든다', 'Made by breaking an empty liquor or beer bottle', [('acquisition_process', 'break_bottle'), ('acquisition_alternative_materials', 'empty_liquor_bottle', 'empty_beer_bottle')]),
    ('냉찜질팩과 천 조각, 신문으로 제작한다', 'Crafted from a cold pack, ripped sheets, and newspaper', [('acquisition_process', 'craft'), ('acquisition_material', 'Coldpack'), ('acquisition_material', 'RippedSheets'), ('acquisition_material', 'Newspaper')]),
    ('천 조각과 막대 재료로 제작한다', 'Crafted from ripped sheets and stick material', [('acquisition_process', 'craft'), ('acquisition_material', 'RippedSheets'), ('acquisition_material', 'stick_material')]),
    ('나뭇가지를 칼날 도구로 깎아 만든다', 'Made by shaping a branch with a bladed tool', [('acquisition_process', 'shape_branch'), ('acquisition_tool', 'bladed_tool')]),
    ('타이머나 알람시계를 개조해 만든다', 'Made by modifying a timer or alarm clock', [('acquisition_process', 'modify_timer'), ('acquisition_alternative_materials', 'Timer', 'alarm_clock')]),
    ('모루 근처에서 철괴와 망치로 제작한다', 'Crafted near an anvil from an iron ingot with a hammer', [('acquisition_process', 'metalworking'), ('acquisition_material', 'IronIngot'), ('acquisition_tool', 'Hammer'), ('condition', 'acquisition', 'near_anvil')]),
    ('수신기와 전자 부품으로 만든다', 'Made from a receiver and electronic parts', [('acquisition_process', 'craft'), ('acquisition_material', 'Receiver'), ('acquisition_material', 'ElectronicsScrap')]),
    ('빈 물병에 휘발유를 담아 만든다', 'Made by filling an empty water bottle with gasoline', [('acquisition_process', 'fill_gasoline'), ('acquisition_container', 'WaterBottleEmpty')]),
    ('수박을 잘라 얻는다', 'Obtained by slicing a watermelon', [('acquisition_process', 'slice_watermelon')]),
    ('수박을 으깨 얻는다', 'Obtained by crushing a watermelon', [('acquisition_process', 'smash_watermelon')]),
    ('빈 위스키 병에 휘발유를 담아 만든다', 'Made by filling an empty whiskey bottle with gasoline', [('acquisition_process', 'fill_gasoline'), ('acquisition_container', 'WhiskeyEmpty')]),
    ('와인잔에 와인을 따라 만든다', 'Made by pouring wine into a wine glass', [('acquisition_process', 'pour_wine'), ('acquisition_container', 'wine_glass')]),
    ('빈 와인 병에 휘발유를 담아 만든다', 'Made by filling an empty wine bottle with gasoline', [('acquisition_process', 'fill_gasoline'), ('acquisition_container', 'WineEmpty')]),
    ('판자를 톱질해 만든다', 'Made by sawing planks', [('acquisition_process', 'saw_planks')]),
    ('베이컨을 잘게 손질해 얻는다', 'Obtained by cutting bacon into pieces', [('acquisition_process', 'cut_bacon_into_bits')]),
    ('베이컨을 손질해 얻는다', 'Obtained by preparing bacon', [('acquisition_process', 'prepare_bacon')]),
    ('재료를 그릇에 담아 만든다', 'Made by placing ingredients in a bowl', [('acquisition_process', 'put_food_or_ingredients_in_bowl_or_pot'), ('acquisition_container', 'bowl')]),
):
    CLAUSES[_ko] = CLAUSES[_en] = _atoms


# Locale counterparts share atoms only where the actual clauses say the same thing.
for _en, _ko in (
    ('Medicine used to treat wound infections', '상처 감염을 치료하는 데 쓰는 약이다'),
    ('You can wear it on your right wrist', '오른쪽 손목에 착용할 수 있다'),
    ('You can wear it over your left eye', '왼쪽 눈에 착용할 수 있다'),
    ('You can wear it over your right eye', '오른쪽 눈에 착용할 수 있다'),
    ('You can wear it over your eyes', '눈에 착용할 수 있다'),
    ('You can wear it around your neck', '목에 착용할 수 있다'),
    ('You can wear it on your nose', '코에 착용할 수 있다'),
    ('It is poisonous', '독성이 있다'),
    ('A full-body garment', 'Clothing worn over the whole body'),
    ('A tool', '도구다'),
    ('For smokers, it can reduce stress and unhappiness; for non-smokers, it increases food sickness', '흡연가라면 스트레스와 불행을 줄일 수 있지만 비흡연가의 식중독 수치를 높인다'),
    ('In the Health panel, select a fractured part that is not already splinted or stitched', '건강 패널에서 골절이 있고 아직 부목을 대거나 봉합하지 않은 부위를 선택한다'),
    ('The head and upper and lower torso are excluded from the splint menu', '머리와 위·아래 몸통은 부목 메뉴의 대상에서 제외된다'),
    ('A radio used to listen to broadcasts or play recorded CDs', '라디오 방송을 듣거나 녹음된 CD를 재생하는 기기다'),
):
    CLAUSES[_en] = CLAUSES[_ko]

CLAUSES.update({
    'Consumable material used in crafting or repair': [('role', 'crafting', 'material'), ('role', 'repair', 'material'), ('consumption_property', 'consumable')],
    'A nail used in construction or crafting': [('identity_label', 'nail'), ('role', 'construction', 'material'), ('role', 'crafting', 'material')],
    'A screw used in assembly or repair': [('identity_label', 'screw'), ('role', 'assembly', 'material'), ('role', 'repair', 'material')],
    'A material used to make and repair fishing rods': [('role', 'fishing_rod_crafting', 'material'), ('role', 'fishing_rod_repair', 'material')],
    'Open the box to take out shotgun shells': [('function', 'unpack_box_contents'), ('output_identity', 'exact_opened_item', 'Base.ShotgunShells')],
    'A consumable material used when welding structures such as metal fences and doors': [('role', 'welding_construction', 'material'), ('consumption_property', 'consumable'), ('context_example', 'welding_construction', 'metal_fences'), ('context_example', 'welding_construction', 'metal_doors')],
})
for _ko, _en, _atoms in (
    ('판자 2개와 못 2개, 망치로 나무 십자가를 만들 수 있다', 'A wooden cross requires two planks, two nails and a hammer', [('recipe_relation', 'WoodenCross', 'construction'), ('recipe_requirement', 'WoodenCross', 'Plank', 2), ('recipe_requirement', 'WoodenCross', 'Nails', 2), ('recipe_requirement', 'WoodenCross', 'Hammer')]),
    ('게임의 지면 우클릭 → 목공 → 기타 메뉴에서 나무 십자가를 선택하고 놓을 위치를 고른다', "In the game's ground right-click menu, choose Carpentry, then Miscellaneous and Wooden Cross, and select a placement location", [('recipe_menu', 'WoodenCross', 'ground_carpentry_miscellaneous'), ('recipe_sequence', 'WoodenCross', 'select_placement')]),
    ('이 예시는 해당 구조물의 재료 조건이며, 다른 목공 구조물까지 같은 재료나 기술 조건으로 만들 수 있다는 뜻은 아니다', 'These material requirements apply to this structure; other carpentry structures do not necessarily share its materials or skill requirements', [('recipe_limit', 'WoodenCross', 'structure_specific_materials_and_skills')]),
):
    CLAUSES[_ko] = CLAUSES[_en] = _atoms


# Exact locale variants retain the same typed propositions as their paired text.
for _texts, _atoms in (
    (['A rifle used for shooting', '사격에 쓰는 소총이다', 'A shotgun used for shooting', '사격에 쓰는 산탄총이다', 'A double-barrel shotgun used for shooting', '사격에 쓰는 더블 배럴 산탄총이다'], [('function', 'fire_ammunition')]),
    (['A ring worn on the left ring finger', '왼손 약지에 착용하는 반지다'], [('wear', 'left_ring_finger')]),
    (['A ring worn on the right ring finger', '오른손 약지에 착용하는 반지다'], [('wear', 'right_ring_finger')]),
    (['An accessory worn on the left wrist', '왼쪽 손목에 착용하는 장신구다'], [('wear', 'left_wrist')]),
    (['An accessory worn on the right wrist', '오른쪽 손목에 착용하는 장신구다'], [('wear', 'right_wrist')]),
    (['An accessory worn on the nose', '코에 착용하는 장신구다'], [('wear', 'nose')]),
    (['An underwear accessory worn on the leg', '다리에 착용하는 속옷 장식이다'], [('wear', 'leg_underwear')]),
    (['발에 신는 양말류다'], [('wear', 'socks')]),
    (['하체에 입는 내의다'], [('wear', 'long_underwear_legs')]),
    (['전신에 착용하는 의류다', '몸에 입는 일체형 의류다'], [('wear', 'whole_body')]),
    (['상체에 착용하는 의류다'], [('wear', 'upper_body')]),
    (['허리에 착용하는 장비다'], [('wear', 'waist_equipment')]),
    (['얼굴과 눈 부위에 착용하는 장비다'], [('wear', 'face_and_eyes')]),
    (['A decorative tail worn on the body', '몸에 착용하는 꼬리 장식이다'], [('function', 'wear_body')]),
    (['A robe worn on the body'], [('function', 'wear_body')]),
    (['다리에 착용하는 속옷류다'], [('wear', 'leg_hosiery')]),
    (['A container used to carry keys'], [('function', 'carry_stored_items'), ('storage_acceptance', 'keys')]),
    (['A sack used to carry items'], [('function', 'carry_stored_items')]),
    (['An empty bottle used to carry water'], [('function', 'carry_water'), ('state_label', 'empty_container')]),
    (['An empty container used to carry fuel'], [('function', 'carry_fuel'), ('state_label', 'empty_container')]),
    (['A bulb used in lights that accept replacement bulbs'], [('function', 'install_light_bulb'), ('condition', 'lighting', 'replaceable_bulb')]),
    (['A component used to add a timer to compatible devices such as explosives'], [('role', 'timer_attachment', 'material')]),
    (['A component used to modify compatible devices for remote triggering'], [('role', 'remote_trigger_attachment', 'material')]),
    (['A material used to make an aerosol bomb'], [('role', 'aerosol_bomb_crafting', 'material')]),
    (['A material used to make pipe bombs'], [('role', 'pipe_bomb_crafting', 'material')]),
    (['A pan used to prepare ingredients for roasting'], [('role', 'roasting_preparation', 'base')]),
    (['A pan used to prepare stir-fries by adding ingredients'], [('role', 'stir_fry_preparation', 'base')]),
    (['A saw used to cut logs into planks'], [('role', 'log_sawing', 'tool')]),
    (['A sawing tool also used to shorten shotgun barrels'], [('role', 'sawing', 'tool'), ('role', 'shotgun_sawing', 'tool')]),
    (['A tool used for joining metal', '금속 접합에 쓰는 도구다'], [('role', 'metalworking', 'tool')]),
    (['A tool used to build wooden structures with nails'], [('role', 'carpentry_menu_construction', 'tool'), ('condition', 'carpentry_menu_construction', 'nailed_structure')]),
    (['A tool used to destroy structures'], [('function', 'destroy_structure')]),
    (['A tool used to dig soil for cultivation'], [('function', 'dig_furrow')]),
    (['A tool used to erase map annotations'], [('function', 'erase_item_map_annotations')]),
    (['A tool used to open cans of food'], [('role', 'package_opening', 'tool')]),
    (['A twig used to prepare campfire material'], [('role', 'campfire_kit_preparation', 'material')]),
    (['An incendiary weapon used to start fires'], [('effect', 'world_fire', 'ignite')]),
    (['An ingredient used to can vegetables'], [('role', 'vegetable_jarring', 'material')]),
    (['An ingredient used to make doughs such as bread dough'], [('role', 'bread_preparation', 'ingredient')]),
    (['An ingredient used to prepare coffee drinks'], [('role', 'coffee_preparation', 'ingredient')]),
    (['건축이나 제작에 쓰는 못이다'], [('role', 'construction', 'material'), ('role', 'crafting', 'material')]),
    (['조립이나 수리에 쓰는 나사못이다'], [('role', 'assembly', 'material'), ('role', 'repair', 'material')]),
    (['낚싯대 제작과 수리에 쓰는 재료다'], [('role', 'fishing_rod_crafting', 'material'), ('role', 'fishing_rod_repair', 'material')]),
    (['금속 울타리·문 등 용접 제작에 쓰는 소모 재료다'], [('role', 'welding_construction', 'material'), ('consumption_property', 'consumable'), ('context_example', 'welding_construction', 'metal_fences'), ('context_example', 'welding_construction', 'metal_doors')]),
    (['A ball used for throwing'], [('function', 'throw_item')]),
    (['A baited trap used to catch birds'], [('function', 'catch_animals'), ('condition', 'trapping', 'bait'), ('target_scope', 'trapping', 'birds')]),
):
    for _text in _texts:
        CLAUSES[_text] = _atoms


CLAUSES.update({
    '제작이나 수리 작업에 들어가는 소모성 재료다': [('role', 'crafting', 'material'), ('role', 'repair', 'material'), ('consumption_property', 'consumable')],
    '전력 작업에서 설치해 주변 기기에 전기를 공급할 때 쓴다': [('function', 'supply_generator_power'), ('condition', 'generator_power', 'installed'), ('target_scope', 'generator_power', 'nearby_devices')],
    '연료 취급 작업에서 연료를 옮기거나 넣을 때 쓴다': [('function', 'transfer_fuel'), ('function', 'supply_fuel')],
    '근접 전투 작업에서 거리를 두고 찌르거나 밀어낼 때 쓴다': [('combat_property', 'reach'), ('function', 'thrust_attack'), ('function', 'shove_attack')],
})

def interpret(text, field=None):
    clause = text.strip().rstrip('.!?').strip()
    if not clause:
        # Only whitespace and sentence punctuation can reach this rule. It
        # cannot discard words, labels, numbers, conditions or conjunctions.
        return [] if re.fullmatch(r'[\s.!?]*', text) else None
    if field == 'identity_hint':
        # A class label is an explicit predecessor meaning, not non-semantic
        # filler. Its admissibility/owner disposition is assessed separately.
        return IDENTITY_MEANINGS.get(clause, [('identity_label', clause)])
    if clause in CLAUSES:
        return CLAUSES[clause]
    match = re.fullmatch(r'글을 읽을 수 있고 (.+) 레벨이 (\d+)~(\d+)이라면, 이 책을 읽어 (.+) (\d+)~(\d+)레벨의 경험치 획득 배율을 높일 수 있다', clause)
    if match and match[1] in SKILLS and match[4] in SKILLS:
        return [('condition', 'skill_reading', 'literate'),
                ('skill_current_range', SKILLS[match[1]], int(match[2]), int(match[3])),
                ('skill_effect_range', SKILLS[match[4]], int(match[5]), int(match[6])),
                ('effect', SKILLS[match[4]] + '_experience_multiplier', 'increase')]
    match = re.fullmatch(r'If you can read and are at (.+) level (\d+)[–-](\d+), this book boosts the XP multiplier for levels (\d+)[–-](\d+)', clause)
    if match and match[1] in SKILLS:
        return [('condition', 'skill_reading', 'literate'),
                ('skill_current_range', SKILLS[match[1]], int(match[2]), int(match[3])),
                ('skill_effect_range', SKILLS[match[1]], int(match[4]), int(match[5])),
                ('effect', SKILLS[match[1]] + '_experience_multiplier', 'increase')]
    spear_names = {'식빵칼': 'BreadKnife', '버터칼': 'ButterKnife', '포크': 'Fork', '편지칼': 'LetterOpener',
                   '메스': 'Scalpel', '숟가락': 'Spoon', '가위': 'Scissors', '손갈퀴': 'HandFork',
                   '드라이버': 'Screwdriver', '식칼': 'KitchenKnife', '사냥칼': 'HuntingKnife', '마체테': 'Machete', '얼음송곳': 'IcePick'}
    spear_names.update({name.lower(): attachment for name, attachment, _ in sources.SPEAR_ATTACHMENTS})
    match = re.fullmatch(r'제작한 창과 (.+), 덕트 테이프로 제작한다', clause)
    match = match or re.fullmatch(r'Crafted from a crafted spear, (.+), and duct tape', clause)
    if match and match[1] in spear_names:
        return [('acquisition_process', 'craft'), ('acquisition_material', 'SpearCrafted'),
                ('acquisition_material', spear_names[match[1]]), ('acquisition_material', 'DuctTape')]
    if clause in {'판자나 나뭇가지와 칼날 도구로 제작한다', 'Crafted from a plank or branch with a bladed tool'}:
        return [('acquisition_process', 'craft'), ('acquisition_alternative_materials', 'Plank', 'TreeBranch'),
                ('acquisition_tool', 'spear_cutting_alternative')]
    vehicle_parts = {'후드': 'hood', '앞문': 'front door', '앞문 유리': 'front window', '뒷문': 'rear door',
                     '양문형 뒷문': 'double rear door', '뒷문 유리': 'rear window', '뒤 유리': 'rear windshield',
                     '트렁크 덮개': 'trunk lid', '앞유리': 'windshield'}
    match = re.fullmatch(r'차량의 (.+)(?:을|를) 떼어내거나 다시 끼울 수 있다', clause)
    if match and match[1] in vehicle_parts:
        part = vehicle_parts[match[1]].replace(' ', '_')
        return [('function', 'remove_vehicle_' + part), ('function', 'refit_vehicle_' + part)]
    match = re.fullmatch(r"You can remove and refit the vehicle's (.+)", clause)
    if match and match[1] in vehicle_parts.values():
        part = match[1].replace(' ', '_')
        return [('function', 'remove_vehicle_' + part), ('function', 'refit_vehicle_' + part)]
    discovery = discovery_places(re.sub(r'^(?:획득 방법|Acquisition):\s*', '', clause))
    if discovery is not None:
        return discovery
    if clause.startswith(('획득 방법: ', 'Acquisition: ')):
        return interpret(clause.split(':', 1)[1].strip(), 'acquisition_hint')
    match = re.fullmatch(r'적용 수준에서 읽으면 (.+) 경험치 획득 배율을 높이는 기술서다', clause)
    match = match or re.fullmatch(r'A skill book that increases (.+) XP gain when read at the applicable level', clause)
    if match and match[1] in SKILLS:
        return [('effect', SKILLS[match[1]] + '_experience_multiplier', 'increase')]
    match = re.fullmatch(r'총 (\d+)쪽이며, (\d+)%씩 읽을 때마다 현재보다 높은 배율만 적용된다', clause)
    if match:
        return [('state', 'reading_page_count', int(match[1])), ('state', 'skill_book_progress_step', int(match[2])),
                ('condition', 'skill_multiplier', 'higher_than_current')]
    match = re.fullmatch(r'The book has (\d+) pages', clause)
    if match:
        return [('state', 'reading_page_count', int(match[1]))]
    match = re.fullmatch(r'끝까지 읽으면 최대 (\d+)배가 된다', clause)
    if match:
        return [('state', 'skill_book_max_multiplier', int(match[1])), ('condition', 'skill_multiplier', 'full_reading_progress')]
    match = re.fullmatch(r'Every (\d+)% read applies the new multiplier only if it is higher, up to (\d+) times when finished', clause)
    if match:
        return [('state', 'skill_book_progress_step', int(match[1])), ('condition', 'skill_multiplier', 'higher_than_current'),
                ('state', 'skill_book_max_multiplier', int(match[2])), ('condition', 'skill_multiplier', 'full_reading_progress')]
    match = re.fullmatch(r'상자를 열어 (.+) 탄약을 꺼낼 수 있다', clause)
    if match:
        return [('function', 'unpack_ammunition'), ('output_identity', 'ammunition', match[1])]
    # A single predicate can be extracted without deciding its truth. Reject
    # coordination/condition markers here; those require explicit multi-atom
    # rules above. This is intentionally narrower than sentence splitting.
    if (not re.search(r'[,;]|\b(?:and|or|but|if|when|once|while)\b|거나|하며|하면|있으면|으며|고 |또는|및 ', clause)
            and (re.fullmatch(r'(?:A|An) [^.!?]+ (?:used to|used for|worn on|worn around|used in) [^.!?]+', clause)
                 or re.fullmatch(r'[^.!?]+(?:에 쓰는|에 사용하는|에 착용하는|에 입는|에 신는|에 끼는) [^.!?]+다', clause))):
        return [('single_proposition', clause)]
    match = re.fullmatch(r'Open the box to take out (.+) ammunition', clause)
    if match:
        return [('function', 'unpack_ammunition'), ('output_identity', 'ammunition', match[1])]
    return None


def extract(inventory):
    """Decompose fields and independently bind rendered clauses to meanings.

    Unknown fields remain pending. Unknown rendered spans retain their own
    obligation even when the structured field has been recognized.
    """
    claims = []
    by_item = {row['item_id']: row for row in inventory['items']}
    for row in by_item.values():
        row['claim_ids'] = []
    for original in inventory['claims']:
        field = original['predecessor_field_or_surface']
        text = original['predecessor_text_ref']['text']
        for start, end, piece in spans(text):
            meanings = interpret(piece, field)
            if meanings == []:
                continue
            for meaning in meanings if meanings else [None]:
                claim = {**original, 'predecessor_text_ref': {**original['predecessor_text_ref'], 'span': [start, end]},
                         'meaning': list(meaning) if meaning else None,
                         'decomposition_state': 'decomposed' if meaning else 'unsegmented',
                         'extraction_rule_ref': 'predecessor_clauses/1' if meaning else None}
                claim['predecessor_claim_id'] = model.identity('claim', [original['predecessor_claim_id'], start, end, meaning])
                claims.append(claim)
                by_item[claim['item_id']]['claim_ids'].append(claim['predecessor_claim_id'])
    index = {}
    for claim in claims:
        if claim['meaning']:
            index.setdefault((claim['item_id'], tuple(claim['meaning'])), []).append(claim['predecessor_claim_id'])
    clauses = []
    for surface in inventory['clauses']:
        for start, end, piece in spans(surface['text']):
            meanings = interpret(piece)
            for meaning in meanings or []:
                lookup = (surface['item_id'], tuple(meaning))
                if lookup in index:
                    continue
                # Rendered-only meanings are real predecessor obligations.
                # They are never silently discarded for lacking a field match.
                ref = model.identity('claim', [surface['item_id'], surface['locale'], surface['text'], start, end, meaning])
                claims.append({'item_id': surface['item_id'], 'predecessor_claim_id': ref,
                               'predecessor_field_or_surface': surface['locale'],
                               'predecessor_text_ref': {'locale': surface['locale'], 'text': surface['text'], 'span': [start, end]},
                               'meaning': list(meaning), 'decomposition_state': 'decomposed',
                               'extraction_rule_ref': 'predecessor_clauses/1', 'predecessor_source_leads': [],
                               'candidate_successor_fact_refs': [], 'verified_source_refs': [],
                               'migration_disposition': 'pending_investigation', 'reason': 'Independent rendered proposition requires source adjudication.',
                               'remaining_uncertainty': None, 'remaining_work': 'source adjudication',
                               'source_binding': 'predecessor_only', 'source_strength': 'not_admitted',
                               'review_state': 'pending', 'owner_adoption_evidence': None, 'owner_presence_evidence': None})
                by_item[surface['item_id']]['claim_ids'].append(ref)
                index[lookup] = [ref]
            linked = [ref for meaning in meanings or [] for ref in index.get((surface['item_id'], tuple(meaning)), [])]
            accounted = meanings is not None and all((surface['item_id'], tuple(m)) in index for m in meanings)
            clauses.append({**surface, 'span': [start, end], 'text': piece, 'claim_ids': linked,
                            'classification': ('non_semantic' if meanings == [] else 'claim_ids') if accounted else 'unsegmented',
                            'classification_rule_ref': ('whitespace_punctuation/1' if meanings == [] else 'predecessor_clauses/1') if accounted else None,
                            'classification_reason': ('Exact whitespace/sentence punctuation contains no proposition.' if meanings == []
                                                      else 'Each recognized semantic atom is joined to an independently recorded predecessor claim.') if accounted else None})
    return {**inventory, 'claims': claims, 'clauses': clauses}


WEAR_LOCATIONS = {
    'head_or_face': {'Hat', 'FullHat', 'FullHelmet', 'Mask', 'MaskEyes', 'MaskFull'},
    'face_and_eyes': {'MaskEyes'}, 'waist_equipment': {'BeltExtra'},
    'left_eye': {'LeftEye'}, 'right_eye': {'RightEye'}, 'nose': {'Nose'},
    'neck_accessory': {'Neck', 'Necklace', 'Necklace_Long'}, 'socks': {'Socks'},
    'leg_hosiery': {'UnderwearBottom', 'UnderwearExtra1', 'Stockings'},
    'leg_underwear': {'UnderwearExtra1'}, 'long_underwear_legs': {'Legs1'},
    'right_ring_finger': {'Right_RingFinger'}, 'left_ring_finger': {'Left_RingFinger'},
    'right_middle_finger': {'Right_MiddleFinger'}, 'left_middle_finger': {'Left_MiddleFinger'},
    'left_wrist': {'LeftWrist'}, 'right_wrist': {'RightWrist'},
    'torso': {'TorsoExtra', 'TorsoExtraVest'},
    'whole_body': {'FullSuit', 'FullSuitHead', 'Boilersuit', 'BodyCostume', 'Torso1Legs1'},
    'neck_clothing': {'Scarf', 'Neck'},
    'head': {'Hat', 'FullHat', 'FullHelmet'}, 'upper_body': {'Shirt', 'Tshirt', 'ShortSleeveShirt', 'TankTop', 'Sweater', 'SweaterHat', 'FullTop', 'TorsoExtra', 'TorsoExtraVest', 'Jacket', 'Jacket_Bulky', 'JacketHat', 'JacketHat_Bulky', 'JacketSuit', 'Jacket_Down'},
    'lower_body': {'Pants'}, 'outerwear': {'Jacket', 'Jacket_Bulky', 'JacketHat', 'JacketHat_Bulky', 'JacketSuit', 'Jacket_Down'},
    'upper_underwear': {'UnderwearTop'}, 'lower_underwear': {'UnderwearBottom'},
    'ears': {'Ears'}, 'upper_ear': {'EarTop'}, 'feet': {'Shoes'}, 'hands': {'Hands'},
    'belly_button': {'BellyButton'}, 'dress': {'Dress'}, 'skirt': {'Skirt'}, 'necklace': {'Necklace'},
    'long_necklace': {'Necklace_Long'}, 'neck': {'Neck'}, 'underwear': {'Underwear'},
    'vest': {'TorsoExtraVest'}, 'eyes': {'Eyes'}, 'face': {'Mask', 'MaskEyes', 'MaskFull'},
}

# Reviewed standalone clothing taxonomy labels. The separate wear/use claims
# remain Layer 3 obligations; modifiers such as protection or color are not
# covered by this owner-bound removal rule.
CLOTHING_LABEL_LOCATIONS = {
    '상의': WEAR_LOCATIONS['upper_body'], '하의': WEAR_LOCATIONS['lower_body'],
    '머리 착용품': WEAR_LOCATIONS['head'], '얼굴 착용품': WEAR_LOCATIONS['face'],
    '안경류': WEAR_LOCATIONS['eyes'], '전신 복장': WEAR_LOCATIONS['whole_body'],
    '반지': set().union(*(WEAR_LOCATIONS[k] for k in ('right_ring_finger', 'left_ring_finger', 'right_middle_finger', 'left_middle_finger'))),
    '목걸이': WEAR_LOCATIONS['necklace'] | WEAR_LOCATIONS['long_necklace'],
    '팔찌': WEAR_LOCATIONS['left_wrist'] | WEAR_LOCATIONS['right_wrist'],
}


# These source-reviewed role specializations require the named recipe in the
# contributing provenance. A broad parent context alone cannot prove a child.
PREPARATION_ROLES = {
    'aerosol_bomb_crafting': ('explosive_assembly', {'Make Aerosol bomb'}),
    'pipe_bomb_crafting': ('explosive_assembly', {'Make Pipe bomb'}),
    'smoke_bomb_crafting': ('explosive_assembly', {'Make Smoke Bomb'}),
    'timer_attachment': ('explosive_modification', {'Add Timer'}),
    'motion_sensor_attachment': ('explosive_modification', {'Add Motion Sensor V1', 'Add Motion Sensor V2', 'Add Motion Sensor V3'}),
    'remote_trigger_attachment': ('explosive_modification', {'Add Crafted Trigger'}),
    'remote_controller_crafting': ('electronic_assembly', {'Make Remote Controller V1', 'Make Remote Controller V2', 'Make Remote Controller V3'}),
    'remote_trigger_crafting': ('electronic_assembly', {'Make Remote Trigger'}),
    'timer_crafting': ('electronic_assembly', {'Make Timer'}),
    'log_sawing': ('woodworking', {'Saw Logs'}),
    'shotgun_sawing': ('shotgun_modification', {'Saw Off Shotgun', 'Saw Off Double Barrel Shotgun'}),
    'bread_preparation': ('dough_preparation', {'Make Bread Dough'}),
    'pizza_preparation': ('dough_preparation', {'Make Pizza'}),
    'cake_preparation': (None, {'Make Cake Batter', 'Place Cake in Baking Pan'}),
    'pie_preparation': (None, {'Make Pie Dough', 'Place Pie in Baking Pan'}),
    'muffin_preparation': ('batter_preparation', {'Prepare Muffins'}),
    'bean_preparation': ('food_preparation', {'Make Bowl of Beans'}),
    'gravy_preparation': ('food_preparation', {'Make Gravy'}),
    'pancake_preparation': ('food_preparation', {'Make Pancake'}),
    'omelette_preparation': ('food_preparation', {'Prepare Omelette'}),
    'fried_food_preparation': ('food_preparation', {'Make Fried Shrimp', 'Make Fried Onion Rings'}),
    'rice_preparation': ('grain_preparation', {'Place Rice in Cooking Pot', 'Place Rice in Saucepan'}),
    'pasta_preparation': ('grain_preparation', {'Place Pasta in Cooking Pot', 'Place Pasta in Saucepan'}),
    'torch_refilling': ('blowtorch_refilling', {'Refill Blow Torch'}),
}


