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


def adjudicate(base, inventory, descriptions, semantic_payload):
    """Join reviewed atoms to source-admitted facts, never to similar prose.

    Unsupported atoms stay pending unless an actual bounded source boundary
    has been investigated. No item-level fallback can classify all its claims.
    """
    facts = {f['ref']: f for f in descriptions['facts']}
    per_item = defaultdict(list)
    for fact in facts.values():
        per_item[fact['item_id']].append(fact)
    previous = {(f['item_id'], f['fact_id']) for f in base['expression']['facts']}
    items = {i['item_id']: i for i in descriptions['items']}
    conservation = []
    source_assessments = {}
    # Reuse the actual reviewed transformation evidence. Output clauses stay
    # acquisition leads; source-confirmed input use cannot prove native output
    # identity. Each selected route retains its own local work; unrelated
    # alternatives do not block an existential claim about this route.
    reviewed_results = defaultdict(dict)
    result_recipes = defaultdict(set)
    recipe_outputs = {}
    for trace in base['acquisition']['traces'].values():
        if trace['family'] != 'transformation':
            continue
        clauses = trace.get('conditions', [])
        results = [c.split(':', 1)[1].strip().split('=')[0] for c in clauses if c.startswith('Result:')]
        if len(results) == 1:
            output = results[0] if '.' in results[0] else trace['module'] + '.' + results[0]
            key = (trace['source_path'], tuple(clauses))
            result_recipes[output].add(key)
            recipe_outputs.setdefault(key, set()).add(output)
    observations = semantic_payload['observations']
    semantic_facts = {f['fact_id']: f for f in semantic_payload['facts']}

    def has_recipe(fact, names):
        source = semantic_facts.get(fact['fact_id'])
        return bool(source and any(
            observations[o]['content'].get('recipe_name') in names
            or observations[o]['locator'].rsplit(':', 1)[-1].removeprefix('Base.') in names
            for p in source['provenance_refs']
            for o in semantic_payload['provenance'][p]['observation_refs']
            if observations[o]['content'].get('clauses')))

    for fact in semantic_payload['facts']:
        if fact['fact_kind'] not in {'direct_function', 'context_role'}:
            continue
        for pref in fact['provenance_refs']:
            provenance = semantic_payload['provenance'][pref]
            rule = provenance.get('contributor_rule_ref', provenance['rule_ref'])
            processes = set()
            if rule in {'radio_crafting', 'material_assembly', 'spear_crafting', 'woodwork'}:
                processes.add('craft')
            if rule in {'food_preparation_recipes', 'baking_preparation', 'frog_preparation'}:
                processes.add('prepare_food')
            if rule == 'item_transformation_recipes':
                processes.add('reviewed_transformation')
            if rule == 'seed_packing':
                processes.update({'pack_seeds', 'package_seeds'})
            if rule == 'log_binding':
                processes.add('tie_logs')
            if rule == 'bandage_materials':
                processes.add('prepare_bandaging_material')
            if rule == 'fabric_recovery':
                processes.add('recover_registered_fabric')
            if rule == 'sheet_rope':
                processes.add('craft_sheet_rope_from_sheet_or_cotton')
            if rule in {'smithing_parts', 'shovel_smithing', 'metal_forging', 'welded_parts'}:
                processes.add('metalworking')
            if rule == 'camping_kit_preparation':
                processes.add('craft')
            if rule == 'poultice_preparation':
                processes.add('process_medicinal_plants')
            if rule == 'jar_preparation':
                processes.add('jar_food')
            if rule == 'crop_spray_preparation':
                processes.add('assemble_gardening_spray')
            if rule == 'box_packing':
                processes.add('box_ammunition')
            if rule == 'bowl_portioning':
                processes.add('put_food_or_ingredients_in_bowl_or_pot')
            if rule in {'radio_crafting', 'electronic_salvage'}:
                processes.add('process_electronic_parts')
            if rule == 'package_opening':
                processes.add('reviewed_transformation')
                method = fact['payload'].get('function')
                process = {'unpack_ammunition': 'open_ammunition_box', 'unpack_seeds': 'open_seed_packet',
                           'unpack_canned_food': 'open_canned_food', 'unpack_eggs': 'open_egg_carton'}.get(method)
                if process:
                    processes.add(process)
            if not processes:
                continue
            for oid in provenance['observation_refs']:
                observation = observations[oid]
                clauses = observation['content'].get('clauses', [])
                result = [c.split(':', 1)[1].strip().split('=')[0] for c in clauses if c.startswith('Result:')]
                if len(result) != 1:
                    continue
                key = (observation['source_path'], tuple(clauses))
                outputs = recipe_outputs.get(key, set())
                if len(outputs) != 1:
                    continue
                output = next(iter(outputs))
                entry = reviewed_results[output].setdefault(key, {'observation_ref': oid, 'processes': set(), 'source_paths': set()})
                entry['processes'].update(processes)
                if rule == 'metal_forging' and output in {'Base.Bullets9mm', 'Base.ShotgunShells', 'Base.308Bullets', 'Base.223Bullets'}:
                    entry['processes'].add('cast_ammunition')
                if rule == 'food_preparation_recipes':
                    name = observation['content'].get('recipe_name')
                    process = {'Slice Bread': 'slice_bread', 'Slice Watermelon': 'slice_watermelon',
                        'Get Bacon Bits': 'cut_bacon_into_bits', 'Get Bacon Rashers': 'prepare_bacon',
                        'Make Halloween Pumpkin': 'process_pumpkin', 'Make Stake': 'shape_branch',
                        'Drill Plank': 'process_lumber', 'Slice Ham': 'cut_meat', 'Slice Salami': 'cut_meat',
                        'Butcher Small Animal': 'butcher_animal_carcass', 'Butcher Rabbit': 'butcher_animal_carcass',
                        'Butcher Bird': 'butcher_animal_carcass', 'Cut Fish': 'prepare_fish',
                        'Make Bowl of Cereal': 'put_food_or_ingredients_in_bowl_or_pot',
                        'Make Bowl of Oatmeal': 'put_food_or_ingredients_in_bowl_or_pot'}.get(name)
                    if process:
                        entry['processes'].add(process)
                if rule == 'item_transformation_recipes':
                    name = observation['content'].get('recipe_name')
                    process = {
                        'Gather Gunpowder': 'dismantle_ammunition', 'Smash Bottle': 'break_bottle',
                        'Saw Logs': 'saw_log', 'Make Sturdy Stick': 'saw_planks',
                        'Saw Off Shotgun': 'saw_off_shotgun', 'Saw Off Double Barrel Shotgun': 'saw_off_shotgun',
                        'Smash Watermelon': 'smash_watermelon', 'Light Candle': 'light_candle',
                        'Make Timer': 'modify_timer', 'Make Bowl of Beans': 'put_food_or_ingredients_in_bowl_or_pot',
                        'Make Bucket of Plaster': 'mix_ingredients', 'Place Cake in Baking Pan': 'mix_ingredients',
                        'Make Remote Controller V1': 'process_electronic_parts',
                        'Make Remote Controller V2': 'process_electronic_parts',
                        'Make Remote Controller V3': 'process_electronic_parts',
                        'Make Aerosol bomb': 'assemble',
                    }.get(name)
                    if process:
                        entry['processes'].add(process)
                    if name in {'Add Timer', 'Add Motion Sensor V1', 'Add Motion Sensor V2', 'Add Motion Sensor V3', 'Add Crafted Trigger'}:
                        entry['processes'].add('modify_explosive')
                    if name in {'Make Aerosol bomb', 'Make Flame bomb', 'Make Smoke Bomb', 'Make Noise Maker', 'Make Pipe bomb',
                                'Make Molotov Cocktail', 'Make Remote Trigger', 'Make Remote Controller V1',
                                'Make Remote Controller V2', 'Make Remote Controller V3', 'Make Newspaper Hat', 'Make Tin Foil Hat',
                                'Make Wooden Box Trap', 'Make Snare Trap', 'Make Trap Box', 'Make Stick Trap', 'Make Cage Trap'}:
                        entry['processes'].add('craft')
                recipe_name = observation['content'].get('recipe_name') or observation['locator'].rsplit(':', 1)[-1].removeprefix('Base.')
                process_names = {
                    'Slice Baloney': 'cut_meat', 'Slice Fillet': 'prepare_fish', 'Slice Frog': 'butcher_animal_carcass',
                    'Dismantle Speaker': 'dismantle_speaker', 'Dismantle TV Remote': 'dismantle_tv_remote',
                    'Open Box of Nails': 'open_nails_box',
                    'Make Bread Dough': 'mix_ingredients', 'Make Chocolate Chip Cookie Dough': 'mix_ingredients',
                    'Make Chocolate Cookie Dough': 'mix_ingredients', 'Make Oatmeal Cookie Dough': 'mix_ingredients',
                    'Make Shortbread Cookie Dough': 'mix_ingredients', 'Make Sugar Cookie Dough': 'mix_ingredients',
                    'Prepare Omelette': 'mix_ingredients', 'Place Pie in Baking Pan': 'mix_ingredients',
                    'Place Pasta in Cooking Pot': 'put_food_or_ingredients_in_bowl_or_pot',
                    'Place Pasta in Saucepan': 'put_food_or_ingredients_in_bowl_or_pot',
                    'Place Rice in Cooking Pot': 'put_food_or_ingredients_in_bowl_or_pot',
                    'Place Rice in Saucepan': 'put_food_or_ingredients_in_bowl_or_pot',
                }
                if recipe_name in process_names:
                    entry['processes'].add(process_names[recipe_name])
                if recipe_name in {'Make 223 Bullets Mold', 'Make 308 Bullets Mold', 'Make 9mm Bullets Mold',
                        'Make Shotgun Shells Mold', 'Build Spiked Baseball Bat', 'Build Spiked Plank', 'Smash Bottle', 'Make Stake'}:
                    entry['processes'].add('craft')
                if rule == 'electronic_salvage':
                    entry['processes'].add('dismantle_electronics')
                if rule == 'bandage_materials':
                    name = observation['content'].get('recipe_name')
                    process = {'Disinfect Bandage': 'disinfect_bandage', 'Disinfect Rag': 'disinfect_rag',
                               'Douse Cotton in Alcohol': 'wet_cotton_with_alcohol', 'Put Alcohol on Cotton': 'wet_cotton_with_alcohol'}.get(name)
                    if process:
                        entry['processes'].add(process)
                        if any(c.startswith('Heat:') for c in clauses) and process.startswith('disinfect_'):
                            entry['processes'].add(process.replace('disinfect_', 'boil_'))
                if rule == 'fabric_recovery':
                    if '[Recipe.GetItemTypes.RipSheets]' in clauses:
                        entry['processes'].add('rip_named_cloth')
                    elif '[Recipe.GetItemTypes.RipClothing_Cotton]' in clauses:
                        entry['processes'].add('rip_registered_clothing')
                    elif '[Recipe.GetItemTypes.RipClothing_Denim]' in clauses:
                        entry['processes'].add('rip_denim_clothing')
                    elif '[Recipe.GetItemTypes.RipClothing_Leather]' in clauses:
                        entry['processes'].add('rip_leather_clothing')
                entry['source_paths'].update(observations[o]['source_path'] for o in provenance['observation_refs'])
    base['reader'].read('docs/ARCHITECTURE.md')
    picker = 'lua/server/Items/ItemPicker.lua'
    picker_text = base['reader'].read(picker).decode('utf-8-sig')
    if not re.search(r'^ItemPicker\s*=\s*ItemPickerJava\s*$', picker_text, re.M):
        raise ValueError('loot consumer handoff changed')
    loot_traces = defaultdict(list)
    for trace_ref, trace in base['acquisition']['traces'].items():
        if trace['family'] in {'loot', 'vehicle'}:
            for token in set(trace.get('tokens', [])):
                loot_traces[token].append((trace_ref, trace))
    def retain_boundary(claim, paths, examined, dependency, reason, partial=()):
        uncertainty = {'meaning': claim['meaning'], 'examined': examined,
            'required_input': dependency, 'reason': reason}
        claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=list(partial),
            verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
            remaining_work=None, remaining_uncertainty=uncertainty, reason=reason,
            source_binding='source_bound', source_strength='reviewed_exact_consumer_boundary', review_state='reviewed')
        conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
            'successor_fact_refs': list(partial), 'locales': {}, 'residual': uncertainty,
            'conservation_status': 'bounded_unresolved'})

    for claim in inventory['claims']:
        meaning = claim.get('meaning')
        if not meaning:
            continue
        item = claim['item_id']
        if meaning in (['function', 'sort_empty_containers'], ['function', 'dispose_container']):
            records = base['declarations'].get(item, [])
            if len(records) == 1:
                reason = 'Remove generic sorting/disposal from Layer 3 under the adopted general inventory-management exclusion. This atom describes organizing or discarding carried objects; it does not state an item-specific transformation. Emptying contents, refilling and crafting reuse remain independent claims. No destination surface or relocation is claimed.'
                claim.update(migration_disposition='responsibility_removed', reason=reason,
                    verified_source_refs=[base['reader'].bindings[records[0]['path']], base['reader'].bindings['docs/ARCHITECTURE.md']],
                    remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound',
                    source_strength='responsibility_boundary', review_state='reviewed',
                    owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': 'adopted P4 general inventory-management scope clarification', 'destination_presence': 'not_claimed'})
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'responsibility_removed',
                    'successor_fact_refs': [], 'locales': {}, 'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
                continue
        if item in sources.PLAIN_OBJECT_LABELS or item in sources.MATERIAL_OBJECT_ITEMS:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            plain = fields.get('Type') == 'Normal' and not conflicts and set(fields) <= (
                sources.MATERIAL_OBJECT_FIELDS if item in sources.MATERIAL_OBJECT_ITEMS else sources.PLAIN_OBJECT_FIELDS)
            management = meaning[0] == 'function' and meaning[1] in {
                'carry_cash', 'carry_cards', 'carry_wallet', 'organize_paper', 'organize_household_items',
                'gather_household_supplies', 'use_tableware'}
            labels = (meaning in (['context_label', 'table_setting'], ['context_label', 'play'])
                      or (item in {'Base.String', 'Base.Yarn', 'Base.Pipe'} and meaning == ['role_unspecified_context', 'material']))
            if plain and (management or labels):
                reason = ('Remove this exact general carrying, organizing, supply-gathering or table-setting gloss under the adopted inventory-management exclusion; it asserts no item-specific transformation. Dedicated gameplay, storage and cleaning claims remain independent.' if management else
                          'Remove this standalone play/table-setting or unspecified-material label from Layer 3. It supplies only a general context/category, with no independently described operation; actual function and recipe claims remain separately adjudicated.')
                evidence = [base['reader'].bindings[p] for p in (records[0]['path'], semantic.MENU, 'docs/ARCHITECTURE.md')]
                claim.update(migration_disposition='responsibility_removed', reason=reason, verified_source_refs=evidence,
                    remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound',
                    source_strength='responsibility_boundary', review_state='reviewed',
                    owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': 'P4 general inventory-management exclusion and Layer 2 category responsibility', 'destination_presence': 'not_claimed'})
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'responsibility_removed',
                    'successor_fact_refs': [], 'locales': {}, 'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
                continue
            absent_functions = {'play_sport', 'play_with_game_objects', 'attach_button_to_clothing_or_fabric',
                'comb_hair', 'groom_hair', 'dog_chew_toy', 'frame_photograph', 'frame_picture', 'equip_pet_dog_collar',
                'brush_teeth', 'write_documents', 'revise_documents', 'clean_body', 'clean_surroundings',
                'empty_container', 'reuse_container', 'wear_body', 'ring_bell', 'store_water',
                'toggle_device_power', 'tune_radio', 'receive_radio_signal', 'unfold_umbrella',
                'protect_from_rain', 'fold_umbrella', 'check_signals', 'operate_equipment'}
            absent = ((meaning[0] == 'function' and meaning[1] in absent_functions)
                      or meaning in (['condition', 'sport', 'game_rules'], ['effect', 'body_scent', 'add'], ['context', 'food_preparation']))
            supported_meaning = any((meaning[0] == 'function' and f['payload'] == {'function': meaning[1]})
                                    or (meaning == ['context', 'food_preparation'] and f['payload'].get('activity') in {'food_preparation', 'dough_preparation', 'batter_preparation'})
                                    for f in per_item[item])
            if plain and absent and not supported_meaning:
                paths = {records[0]['path'], semantic.MENU, semantic.CLOTHING, semantic.CRAFT, semantic.GROUPS,
                         sources.WORLD_MENU, sources.WASH_BODY, sources.WASH_CLOTHING, sources.CLEAN_BLOOD,
                         sources.CONTEXT_MANAGER, sources.CONTEXT_INVENTORY, sources.CONTEXT_LOADER,
                         sources.CONTEXT_ELEMENT, sources.CONTEXT_RADIO, sources.CONTEXT_MOVABLE, sources.CONTEXT_MEDIA,
                         sources.HOTBAR, sources.HOTBAR_SLOTS, sources.PLACE_OBJECT, sources.DROP_OBJECT,
                         sources.CAMP_FUEL, sources.CAMP_MENU, sources.LEGACY_RELOAD, sources.TUTORIAL_MENU}
                evidence = [base['reader'].bindings[p] for p in sorted(paths)]
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                    'selection': 'No exact named-item or capability-field predicate selects this claimed action in the bound inventory/registered dispatch. The normal model-placement and transfer routes are general management; a label is not an action implementation.',
                    'specific_exclusions': 'Sports/game items have no Weapon or game-control dispatch; toiletries have no dye/makeup/medical or actual Soap2/CleaningLiquid2/Bleach cleaning selection; plain tableware has no Food/capacity/water-replacement capability; stationery lacks writer tags and writable pages; pet/frame objects have no corresponding action selection. Any exact crafting relation remains separately attributed.'},
                    'required_input': 'An authoritative item-specific consumer implementing the claimed ' + '/'.join(map(str, meaning)) + ' for ' + item,
                    'reason': 'The available exact declaration and selected consumers do not establish the claimed dedicated operation, effect or rules. This is a bounded source gap for that proposition, not a claim that the object has no purpose anywhere or that a hypothetical extension blocks the answered dispatch question.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='examined_exact_dispatch_gap', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item in sources.OBJECT_LABELS and meaning in (
                ['identity_label', sources.OBJECT_LABELS[item]], ['context_label', 'leisure'], ['context_label', 'souvenir'],
                ['function', 'view_leisure_objects'], ['function', 'collect_leisure_objects']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Normal' and not conflicts and set(fields) <= sources.PLAIN_OBJECT_FIELDS:
                taxonomy = meaning[0] == 'identity_label' or meaning == ['context_label', 'souvenir']
                paths = {records[0]['path'], 'docs/ARCHITECTURE.md', semantic.MENU,
                         sources.CONTEXT_MEDIA, sources.RADIO_MEDIA, sources.LEGACY_MEDIA_MENU}
                for path in paths:
                    base['reader'].read(path)
                reason = ('Remove the standalone object taxonomy from Layer 3 under the existing Layer 2 classification responsibility. '
                          if taxonomy else
                          'Remove the generic leisure handling gloss: taking out, looking at ordinary objects and collecting them describe general inventory management within the adopted exclusion. '
                          'The sentence does not establish a dedicated photo viewer, a play-with-toy action, a mood effect or media playback. ')
                reason += 'This does not claim relocation or destination preservation; exact recorded-media functionality and every other direct question remain independently adjudicated.'
                claim.update(migration_disposition='responsibility_removed', reason=reason,
                    verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound',
                    source_strength='responsibility_boundary', review_state='reviewed',
                    owner_presence_evidence={'path': 'docs/ARCHITECTURE.md',
                        'section': '정보 계층 / 2계층' if taxonomy else 'adopted P4 general inventory-management scope clarification',
                        'destination_presence': 'not_claimed', 'declaration': fields,
                        'media_distinction': 'The obsolete disks/tapes world-menu body is commented out. Active RWMMedia uses isRecordedMedia/getMediaType; joypad selection names Disc_Retail/VHS_Retail/VHS_Home, not these generic Disc/VHS declarations.'})
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                    'migration_disposition': 'responsibility_removed', 'successor_fact_refs': [], 'locales': {},
                    'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
                continue
        if (item == 'Base.Apple' and meaning[0] in {'recipe_relation', 'recipe_requirement', 'recipe_menu',
                                                  'recipe_preparation', 'recipe_limit', 'recipe_sequence'}
                and meaning[1] in base.get('apple_recipe_relations', {})):
            relation = base['apple_recipe_relations'][meaning[1]]
            paths = {'docs/ARCHITECTURE.md', 'scripts/items_food.txt', relation['path'],
                     'scripts/recipes.txt', semantic.MENU, semantic.COOK, semantic.GROUPS}
            for path in paths:
                base['reader'].read(path)
            reason = ('Remove this concrete recipe relation, requirement, menu, preparation, limit or sequence from the Layer 3 description. '
                      'ARCHITECTURE assigns those exact interaction relationships to Layer 4. The independent Apple ingredient role and ingestion claims remain accounted. '
                      'This is responsibility removal, not verified relocation, a claim of destination presence, or certification of a native recipe limit/baking result.')
            claim.update(migration_disposition='responsibility_removed', reason=reason,
                verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound',
                source_strength='responsibility_boundary', review_state='reviewed',
                owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': '정보 계층 / 4계층 - 상호작용 정보 계층',
                    'destination_presence': 'not_claimed', 'source_relation': relation,
                    'retained_layer3_scope': 'The independent food-preparation ingredient fact retains recipe acceptance for the selected base, current cooked/frozen eligibility, inventory transfer/retention, poisoning policy and interruption qualifiers. No unconditional addition or finished cooked-food outcome is asserted. Numeric per-recipe capacity and exact preparation/menu sequence are the removed relation detail; removal does not strip those truth-changing Layer 3 eligibility predicates.',
                    'examined': 'Apple names eight exact evolved recipes. Bowl/CakePrep/PiePrep/BakingTray_Muffin and the prepared Pancakes/Waffles/Oatmeal forms match their BaseItem declarations. Cake/pie/muffin preparation recipes retain actual inputs and callbacks. The menu transfers base/ingredient and ISAddItemInRecipe delegates getItemsCanBeUse/addItem; MaxItems and Cookable are raw source properties, not independently verified native limits or baking outcomes.'})
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                'migration_disposition': 'responsibility_removed', 'successor_fact_refs': [], 'locales': {},
                'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
            continue
        if (item == 'Base.Hammer' and meaning[0] in {'recipe_relation', 'recipe_requirement', 'recipe_menu', 'recipe_limit', 'recipe_sequence'}
                and meaning[1] == 'WoodenCross'):
            paths = {'docs/ARCHITECTURE.md', semantic.BUILD, semantic.BUILD_OBJECT, semantic.BUILD_ACTION, semantic.BUILD_UTIL}
            for path in paths:
                base['reader'].read(path)
            retained = [f['ref'] for f in per_item[item] if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'tool'}]
            if retained:
                reason = ('Remove the exact Wooden Cross recipe requirements and menu/placement walkthrough under the existing Layer 4 interaction responsibility. '
                          'The active miscellaneous menu calls canBuild(2,2,0,0,0,0), requires a hammer and selects onWoodenCross; that factory declares two Base.Plank, two Base.Nails and starts the placement cursor. '
                          'These are structure-specific relations, not universal carpentry requirements. The independently admitted construction tool role and its eligibility/placement qualifiers remain Layer 3. '
                          'This is responsibility removal, not verified destination presence or guaranteed world-object creation.')
                claim.update(migration_disposition='responsibility_removed', reason=reason,
                    verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound',
                    source_strength='responsibility_boundary', review_state='reviewed',
                    owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': '정보 계층 / 4계층 - 상호작용 정보 계층',
                        'destination_presence': 'not_claimed', 'retained_layer3_fact_refs': retained,
                        'source_relation': 'ISBuildMenu.buildMiscMenu and ISBuildMenu.onWoodenCross'})
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                    'migration_disposition': 'responsibility_removed', 'successor_fact_refs': [], 'locales': {},
                    'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
                continue
        if meaning[0] == 'condition' and meaning[-1] == 'near_anvil':
            selected = [entry for (_, clauses), entry in reviewed_results[item].items() if 'NearItem:Anvil' in clauses]
            if selected:
                retain_boundary(claim, {semantic.CRAFT, *(p for entry in selected for p in entry['source_paths'])},
                    {'recipe_observation_refs': [e['observation_ref'] for e in selected], 'field': 'NearItem:Anvil'},
                    'Native NearItem object recognition, recipe validity and exact result binding',
                    'The declared anvil condition belongs to the exact recipe creating this item, not an intrinsic action of the resulting ammunition/mold/tool. Its raw requirement and interpreted input path are retained; native matching and result delivery remain separate.')
                continue
        if item == 'Base.Molotov' and meaning == ['acquisition_alternative_materials', 'liquor_bottle', 'empty_bottle']:
            selected = [entry for (_, clauses), entry in reviewed_results[item].items()
                if 'destroy [Recipe.GetItemTypes.Liquor]' in clauses or 'WineEmpty/WineEmpty2/WhiskeyEmpty/BeerEmpty' in clauses]
            if len(selected) >= 2:
                retain_boundary(claim, {semantic.CRAFT, semantic.GROUPS, *(p for entry in selected for p in entry['source_paths'])},
                    {'recipe_observation_refs': [e['observation_ref'] for e in selected]},
                    'Native full-liquor classification, separate recipe input selection and result delivery',
                    'Full liquor and an empty bottle with a petrol use are different complete recipes, each requiring cloth. Their alternatives cannot be treated as interchangeable bottles without the different fullness and fuel requirements.')
                continue
        if meaning[0] in {'acquisition_material', 'acquisition_tool', 'acquisition_alternative_materials'}:
            token_aliases = {
                'iron_ingot': {'IronIngot'}, 'Hammer': {'[Recipe.GetItemTypes.Hammer]', 'BallPeenHammer'},
                'hammer': {'[Recipe.GetItemTypes.Hammer]', 'BallPeenHammer'}, 'tongs': {'Tongs'},
                'saw': {'[Recipe.GetItemTypes.Saw]', 'Saw', 'GardenSaw'},
                'bladed_tool': {'[Recipe.GetItemTypes.SharpKnife]', 'MeatCleaver'},
                'cord': {'Twine'}, 'gasoline': {'PetrolCan', '[Recipe.GetItemTypes.Petrol]'},
                'hairspray': {'Hairspray'}, 'fireworks_material': {'Sparklers'},
                'stick_material': {'TreeBranch', 'WoodenStick', 'Plank'},
                'empty_bottle': {'WineEmpty', 'WineEmpty2', 'WhiskeyEmpty', 'BeerEmpty', 'WaterBottleEmpty'},
                'empty_liquor_bottle': {'WhiskeyEmpty'}, 'empty_beer_bottle': {'BeerEmpty'},
                'liquor_bottle': {'WhiskeyFull'}, 'alarm_clock': {'AlarmClock', 'AlarmClock2'},
            }
            selected = []
            for (_, clauses), entry in reviewed_results[item].items():
                inputs = [c for c in clauses if ':' not in c]
                if meaning[0] == 'acquisition_tool':
                    inputs = [c for c in inputs if c.startswith('keep ')]
                else:
                    inputs = [c for c in inputs if not c.startswith('keep ')]
                alternatives = [set(re.sub(r'[=;][0-9.]+$', '', c.removeprefix('keep ').removeprefix('destroy ')).split('/')) for c in inputs]
                expected = [token_aliases.get(t, {t}) for t in meaning[1:]]
                if (meaning[0] == 'acquisition_alternative_materials' and any(all(tokens & values for tokens in expected) for values in alternatives)
                        or meaning[0] != 'acquisition_alternative_materials' and any(expected[0] & values for values in alternatives)):
                    selected.append(entry)
            if selected:
                paths = {semantic.CRAFT, semantic.GROUPS, *(p for entry in selected for p in entry['source_paths'])}
                retain_boundary(claim, paths, {'recipe_observation_refs': [e['observation_ref'] for e in selected],
                    'input_role': meaning[0], 'result_fulltype': item},
                    'Native RecipeManager selected-input quantities, exact result identity and delivery',
                    'The claimed input/tool alternative matches an independently interpreted recipe for this exact result. Its retained clauses and callback preserve the actual other requirements; the input-use fact does not establish successful native acquisition or universal interchangeability.')
                continue
        rod_outputs = {'Base.CraftedFishingRod', 'Base.CraftedFishingRodTwineLine', 'Base.FishingRod', 'Base.FishingRodTwineLine'}
        rod_material = item in rod_outputs and meaning[0] in {'acquisition_material', 'acquisition_alternative_materials'}
        spear_outputs = {'Base.SpearCrafted', *('Base.' + result for _, _, result in sources.SPEAR_ATTACHMENTS)}
        spear_material = item in spear_outputs and meaning[0] in {'acquisition_material', 'acquisition_alternative_materials', 'acquisition_tool'}
        rod_repair = item == 'Base.FishingRodBreak' and meaning == ['function', 'repair_fishing_rod_with_line']
        radio_material = (item in {'Radio.RadioMakeShift', 'Radio.HamRadioMakeShift', 'Radio.WalkieTalkieMakeShift'}
                          and meaning[0] == 'acquisition_material' and meaning[1] in {'electronic_scrap', 'radio_parts', 'wire', 'aluminum'})
        if rod_material or rod_repair or spear_material or radio_material:
            output = 'Base.FishingRod' if rod_repair else item
            reviewed = reviewed_results[output]
            tokens = {'wooden_stick': 'WoodenStick', 'fishing_line': 'FishingLine', 'twine': 'Twine',
                      'broken_fishing_rod': 'FishingRodBreak', 'paperclip': 'Paperclip', 'nail': 'Nails'}
            tokens.update({token: token for token in ('SpearCrafted', 'DuctTape', 'Plank', 'TreeBranch',
                          *(attachment for _, attachment, _ in sources.SPEAR_ATTACHMENTS))})
            if radio_material:
                tokens.update(electronic_scrap='ElectronicsScrap', wire='Radio.ElectricWire', aluminum='Aluminum')
            selected = []
            for (_, clauses), entry in reviewed.items():
                inputs = [c for c in clauses if ':' not in c and not c.startswith(('keep ', 'destroy '))]
                bare = [re.sub(r'=\d+(?:\.\d+)?$', '', c) for c in inputs]
                if radio_material and meaning[1] == 'radio_parts':
                    matches = 'Radio.RadioReceiver' in bare and 'Amplifier' in bare
                elif meaning == ['acquisition_tool', 'spear_cutting_alternative']:
                    matches = 'keep [Recipe.GetItemTypes.SharpKnife]/SharpedStone/MeatCleaver' in clauses
                elif rod_repair:
                    matches = {'FishingRodBreak', 'FishingLine'} <= set(bare)
                elif meaning[0] == 'acquisition_alternative_materials':
                    matches = all(t in tokens for t in meaning[1:]) and any(set(c.split('/')) == {tokens[t] for t in meaning[1:]} for c in bare)
                else:
                    matches = meaning[1] in tokens and tokens[meaning[1]] in bare
                if matches:
                    selected.append(entry)
            if result_recipes[output] and selected:
                paths = {semantic.CRAFT, *(p for entry in selected for p in entry['source_paths'])}
                partial = [f['ref'] for f in per_item[item] if f['payload'] == {'role': 'material'}] if rod_repair else []
                uncertainty = {'meaning': meaning,
                    'examined': {'result_item': output, 'recipe_observation_refs': [e['observation_ref'] for e in selected],
                                 'input_interpretation': 'Exact input clauses and the paperclip/nail alternative are retained; crafting requires the learned recipe. The repair sentence omits that alternative and the full declared conditions.' if rod_repair else 'The stated material or alternative matches a source-reviewed input clause; amounts and other recipe requirements remain in that source observation.'},
                    'required_input': 'RecipeManager.PerformMakeItem result identity and delivery for the selected creation recipe',
                    'reason': 'The actual recipe inputs and Lua crafting consumer have been reconciled. Their source-bound material or tool role does not by itself establish the created result identity delivered by the native recipe manager.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)], remaining_work=None,
                    remaining_uncertainty=uncertainty, reason=uncertainty['reason'], source_binding='source_bound',
                    source_strength='reviewed_transformation_native_result_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if (meaning[:2] == ['acquisition_process', 'fill_ground_bag'] and item in base.get('ground_bag_relations', {})
                and {'Base.Dirtbag': 'dirt', 'Base.Gravelbag': 'gravel', 'Base.Sandbag': 'sand'}.get(item) == meaning[2]):
            relation = base['ground_bag_relations'][item]
            uncertainty = {'meaning': meaning, 'examined': relation,
                'required_input': 'Inventory.AddItem result identity for the specified Base bag and native used-delta/capacity state, plus the independent shovelGround server terrain operation',
                'reason': 'The registered menu, exact ground sprite selection, TakeDirt tool, empty HoldDirt replacement and matching partial-bag refill have been interpreted through their Lua consumers. A new bag starts at one use; this is not a guaranteed full bag. The local inventory transformation and server ground command are independent, and the native item creation/result remains bounded separately.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in relation['source_paths']],
                remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                source_binding='source_bound', source_strength='exact_ground_collection_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        if item == 'camping.Flint' and meaning == ['function', 'make_spark']:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if not conflicts and fields.get('Type') == 'Normal' and set(fields) <= sources.PLAIN_OBJECT_FIELDS:
                paths = {records[0]['path'], semantic.MENU, sources.CAMP_MENU, sources.CAMP_LIGHT,
                         sources.CAMP_FUEL, sources.CAMP_COMMANDS}
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                    'dispatch': 'The exact Normal Flint is not the selected active igniter, FlintKnife or SteelAndFlint. The camping light action consumes its selected fuel/igniter, not a display-name synonym.'},
                    'required_input': 'An authoritative active spark-making consumer selecting exact camping.Flint',
                    'reason': 'The declared name identifies flint but the bound active ignition dispatch does not corroborate its claimed spark-making use. This finite source comparison does not assert universal game-wide absence.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='exact_camping_dispatch_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if ((item == 'Base.BucketEmpty' and meaning == ['acquisition_process', 'empty_water_bucket'])
                or (item == 'farming.GardeningSprayFull' and meaning == ['acquisition_process', 'fill_spray_with_chemicals'])):
            filled = 'Base.BucketWaterFull' if item == 'Base.BucketEmpty' else item
            source = base.get('water_container_sources', {}).get(filled)
            records = base['declarations'].get(filled, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if source and not conflicts:
                paths = {records[0]['path'], semantic.MENU, sources.WORLD_MENU, sources.TAKE_WATER, sources.DUMP_WATER}
                uncertainty = {'meaning': meaning, 'examined': {'filled_declaration': fields, 'water_binding': source,
                    'emptying': sources.WATER_EMPTYING if item == 'Base.BucketEmpty' else None},
                    'required_input': ('Native Use interpretation of Base.BucketWaterFull ReplaceOnDeplete=BucketEmpty and exact returned inventory identity'
                        if item == 'Base.BucketEmpty' else 'An authoritative chemical-filling producer for exact farming.GardeningSprayFull, distinct from its demonstrated water-source replacement and the two treatment-spray recipe results'),
                    'reason': ('The actual dump action reduces water and calls Use after depletion; the declaration names BucketEmpty. The local action does not itself create that exact returned item, so acquisition identity remains native.'
                        if item == 'Base.BucketEmpty' else 'This exact full spray is declared as a water source and is reached by the empty spray WaterSource replacement. Milk and Cigarettes treatments have different exact results. The predecessor chemical-filling claim is not corroborated by the bound water route and is not silently rewritten as one of those treatments.')}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='exact_water_form_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if (meaning in (['acquisition_process', 'fill_water'], ['condition', 'fill_water', 'empty_container'])
                and item in base.get('water_filling_relations', {})):
            routes = base['water_filling_relations'][item]
            paths = {observations[r]['source_path'] for route in routes for r in route['observation_refs']}
            uncertainty = {'meaning': meaning, 'examined': routes,
                'required_input': 'Native getReplaceType(WaterSource) mapping and InventoryItemFactory result identity for the exact declared filled form; runtime water availability and delivery',
                'reason': 'The exact empty-form declarations, unbroken/same-building menu selection, transfer, start-time item replacement and progressive filling consumer are reconciled. The native replacement lookup/factory owns output identity. Partial fills and taint persistence remain explicit; filling is not assumed to create a full or purified container.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                         remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                         source_binding='source_bound', source_strength='exact_water_replacement_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        fuel_boundary = (item == 'Base.MetalDrum' and meaning in (
            ['function', 'collect_water'], ['function', 'burn_logs_to_charcoal']))
        fuel_acquisition = item in sources.PETROL_ITEMS and meaning[0] in {'acquisition_process', 'acquisition_container'}
        empty_fuel_state = item in sources.EMPTY_PETROL_ITEMS and (meaning in (
            ['state', 'container_contents', 'empty'], ['state_label', 'empty_container'], ['state_label', 'empty_reusable_container']))
        if fuel_boundary or fuel_acquisition or empty_fuel_state:
            records = base['declarations'].get(item, [])
            paths = {r['path'] for r in records}
            paths.update((sources.BLACKSMITH_MENU, semantic.PROPS, *sources.DRUM_SOURCES)
                if fuel_boundary else (sources.WORLD_MENU, sources.TAKE_FUEL, sources.VEHICLE_MENU, *sources.VEHICLE_FUEL_ACTIONS))
            uncertainty = {'meaning': meaning,
                'required_input': ('An active exact Base.MetalDrum-to-installed-object binding' if fuel_boundary else
                    'Native PetrolSource item creation, initial/depleted container state and actual source-to-result delivery'),
                'reason': ('The existing world drum rain/charcoal code is interpreted, but the carried Normal declaration has no WorldObjectSprite. The construction menu is disabled and its Base.MetalDrum requirement is commented out; moveables use another identity. Installed behavior therefore does not establish this carried-item claim.' if fuel_boundary else
                    'Actual pump and siphon actions replace an empty source using PetrolSource with a fallback, and subsequent transfer can be partial. The pump menu temporary replacement is not the action replacement. These control paths are represented, but native factory state/delivery and the acquisition outcome are not guaranteed from the item name. Acquisition facts remain under their existing authority.')}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                source_binding='source_bound', source_strength='examined_fuel_binding_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        electrical = base.get('electrical_control_sources', {}).get(item)
        electrical_outcome = (electrical and (
            item == 'Base.CarBatteryCharger' and meaning == ['function', 'charge_vehicle_battery']
            or item in {'Base.CarBattery1', 'Base.CarBattery2', 'Base.CarBattery3'} and meaning in (
                ['function', 'supply_vehicle_starting_power'], ['function', 'supply_vehicle_electrical_power'])
            or item == 'Base.Generator' and meaning in (
                ['function', 'supply_generator_power'], ['target_scope', 'generator_power', 'nearby_devices'])))
        if electrical_outcome:
            paths = {observations[r]['source_path'] for r in electrical['observation_refs']}
            uncertainty = {'meaning': meaning, 'examined': electrical,
                'required_input': ('IsoCarBatteryCharger charge progression for the connected battery and actual power state'
                    if item == 'Base.CarBatteryCharger' else
                    'IsoGenerator electricity propagation, coverage and connected consumers'
                    if item == 'Base.Generator' else
                    'Native vehicle engine-start and electrical-consumer execution for the installed battery'),
                'reason': 'The actual installation, connection and control paths are interpreted separately from the claimed native result. Vehicle Lua charge adjustments are represented, including the helper applying its delta twice. Charger activation and generator state setters do not themselves implement successful charging, electrical supply or a guaranteed coverage area. The unused legacy recharge action is not treated as a live charging route.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                source_binding='source_bound', source_strength='examined_electrical_execution_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        physics_outcome = (item in sources.THROWN_DEVICE_ITEMS and (
            meaning[0] == 'effect' and meaning[1] in {'world_fire', 'explosion'}
            or meaning[0] == 'conditional_effect' and meaning[1] in {'noise', 'smoke', 'world_noise', 'world_smoke'}
            or meaning == ['function', 'throw_item']))
        illumination = (item in sources.LIGHT_ITEMS and meaning in (
            ['function', 'illuminate_surroundings'], ['effect', 'illumination', 'provide'], ['condition', 'illumination', 'lit']))
        available_control = any(f['payload'].get('function') == ('request_physics_attack' if physics_outcome else 'control_portable_light') for f in per_item[item])
        if (physics_outcome or illumination) and available_control:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            paths = {records[0]['path'], semantic.MENU}
            paths.update({sources.FIREARM, sources.DEVICE_PLACE, sources.DEVICE_TIMER, sources.DEVICE_TAKE, sources.OBJECT_COMMANDS}
                         if physics_outcome else {sources.LIGHT_RADIAL, sources.LIGHT_BINDING, semantic.GROUPS, semantic.CRAFT})
            uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                'dispatch': sources.PHYSICS_ATTACK if physics_outcome else sources.LIGHT_CONTROL},
                'required_input': 'DoAttack/PhysicsObject and IsoTrap interpretation of the exact effect and activation fields' if physics_outcome else 'canEmitLight/light-strength geometry, charge drain and actual native emission for this exact light form',
                'reason': 'The applicable local controls and actual callbacks have been interpreted. Their declared native effect inputs and operation requests do not themselves establish this separate claimed outcome. No positive effect or negative immunity is inferred from names or zero-valued damage fields.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                source_binding='source_bound', source_strength='examined_device_execution_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        if meaning[0] == 'acquisition_process' and result_recipes[item]:
            reviewed = reviewed_results[item]
            # A claim that an item can be obtained through this route is
            # existential. Unrelated result recipes are separate obligations,
            # not a reason to postpone an already interpreted exact route.
            if any(meaning[1] in r['processes'] for r in reviewed.values()):
                selected = [r for r in reviewed.values() if meaning[1] in r['processes']]
                paths = {semantic.CRAFT, *(p for r in selected for p in r['source_paths'])}
                evidence = [base['reader'].bindings[p] for p in sorted(paths)]
                uncertainty = {'meaning': meaning, 'examined': {
                    'result_observation_refs': sorted(r['observation_ref'] for r in selected),
                    'consumer': semantic.CRAFT,
                    'local_reconciliation': 'The selected exact recipes match this claimed process and have source-reviewed input/callback conditions. Other result recipes are separate route obligations.'},
                    'required_input': 'RecipeManager.PerformMakeItem result identity, module resolution and delivery for these exact recipes',
                    'reason': 'The source supports the specified transformation route as a concrete acquisition lead. Its input roles and called Lua behavior have been interpreted, but ISCraftAction receives the created item from RecipeManager before delivery; input-use facts do not establish that native result identity. No output is relabeled as an intrinsic material role.'}
                if meaning[1] in {'rip_named_cloth', 'rip_registered_clothing', 'rip_denim_clothing', 'rip_leather_clothing'}:
                    fabric = {'rip_named_cloth': 'Sheet', 'rip_registered_clothing': 'Cotton', 'rip_denim_clothing': 'Denim', 'rip_leather_clothing': 'Leather'}[meaning[1]]
                    uncertainty['examined']['callback'] = 'Recipe.OnCreate.RipClothing uses items:get(0), the exact named Sheet or fabric definition, covered parts/tailoring, and dirt/blood selection. The nominal recipe result is removed; the callback creates and adds the selected material itself.'
                    uncertainty['examined']['material_identity'] = {'definition': fabric, 'full_type': item, 'dirty_branch': 'A dirty suffix is requested only when the script manager finds that form; otherwise the same full material type is created.'}
                    uncertainty['examined']['eligibility'] = 'Registered Clothing type and exact fabric membership exclude named-definition items. Separate IsWorn and IsNotWorn recipes preserve both states. Denim/Leather recipes additionally keep a Recipe.GetItemTypes.Scissors tool; these are recipe inputs, not the commented definition tools field.' if fabric != 'Sheet' else 'The RipSheets group admits non-Clothing items with a named material definition.'
                    uncertainty['required_input'] = 'RecipeManager callback dispatch and participant ordering for these recipes; runtime material/dirt selection and callback output delivery'
                    uncertainty['reason'] = 'The selected named-cloth or exact fabric route, its actual callback and full material name have been traced. The retained boundary is native callback invocation/selected participant delivery and conditional output. Separate worn/unworn selection and any scissors requirement remain on the exact recipes.'
                if meaning[1] in {'boil_bandage', 'boil_rag'}:
                    uncertainty['examined']['heat_requirement'] = 'The selected water-pot/saucepan recipes declare Heat:-0.22; raw semicolon water amounts are preserved.'
                    uncertainty['required_input'] += '; native interpretation of Heat:-0.22 relative to the claimed boiling temperature'
                    uncertainty['reason'] = 'The complete heated-water preparation recipes and their inputs have been interpreted. Their negative Heat field alone does not establish boiling temperature, and the created sterilized form is delivered by RecipeManager. Both exact limits are retained rather than calling the boiling claim recovered.'
                if meaning[1] == 'craft_sheet_rope_from_sheet_or_cotton':
                    uncertainty['examined']['input_group'] = 'CraftSheetRope admits Clothing with a registered fabric without noSheetRope, or a named ClothingRecipesDefinitions entry. Cotton and Sheet are admitted; Denim/Leather are excluded by noSheetRope. The exact recipe consumes that group and declares Result:SheetRope without a ripping callback.'
                    uncertainty['reason'] = 'The specified sheet/cotton material route is traced through its actual group, recipe and crafting consumer. The predecessor tearing wording is not substituted for Recipe.OnCreate.RipClothing, which is a different fabric-recovery recipe. Native RecipeManager still owns this exact result creation and delivery.'
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='reviewed_transformation_native_result_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if meaning[0] == 'wear' and meaning[1] in WEAR_LOCATIONS:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if (fields.get('Type') == 'Clothing' and conflicts.get('BodyLocation')
                    and set(conflicts['BodyLocation']) <= WEAR_LOCATIONS[meaning[1]]):
                paths = {records[0]['path'], semantic.WEAR, sources.BODY_LOCATIONS}
                uncertainty = {'meaning': meaning, 'examined': {'BodyLocation': conflicts['BodyLocation'], 'consumer': semantic.WEAR},
                    'required_input': 'Native load precedence and worn-location binding for these repeated BodyLocation declarations',
                    'reason': 'The raw declaration contains competing location values. Both belong to the claimed body region, but the exact getter value passed to setWornItem is not selected from declaration order by this recovery. Independent washing and other clothing uses remain represented.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='repeated_location_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if meaning == ['hazard', 'food_poison']:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Food' and (fields.get('PoisonPower') or fields.get('Poison')):
                paths = {records[0]['path'], semantic.MENU, semantic.EAT}
                uncertainty = {'meaning': meaning, 'examined': {k: fields.get(k) for k in ('Poison', 'PoisonPower', 'PoisonDetectionLevel', 'OnEat', 'OBSOLETE')},
                    'required_input': 'Native Food poison getters and IsoGameCharacter.Eat interpretation of this exact declared poison input',
                    'reason': 'The declared poison input and actual eating delegation are retained, but they do not establish a contact hazard, fixed poisoning outcome or dose. The independent hunger and any Lua callback effects remain separate.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='exact_native_food_poison_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        records = base['declarations'].get(item, [])
        exact_fields, exact_conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
        native_form = None
        native_paths = {semantic.MENU}
        if ((item.startswith('Base.Umbrella') or item.startswith('Base.ClosedUmbrella'))
                and (meaning == ['function', 'protect_from_rain'] or meaning[:2] == ['condition', 'rain_protection'])):
            native_form = ('ProtectFromRainWhenEquipped and EquippedNoSprint native consumers and held/open-form mapping',
                'The exact open form declares native rain/sprint fields; opening/closing recipes represent form changes. Neither a held-item getter nor the recipe callback implements weather protection. The native field result remains distinct from the recovered form operation.')
            native_paths.update({semantic.GROUPS, semantic.CRAFT})
        elif item.startswith('Base.MakeUp_') and meaning[0] == 'visual_effect' and exact_fields.get('Type') == 'Clothing':
            native_form = ('Exact ClothingItem asset and native worn-slot rendering for ' + item,
                'The registered makeup result is a Clothing item with a makeup body location. The actual makeup UI previews and replaces that item; its name and slot do not prove the claimed visible color or pattern.')
            native_paths.update({sources.MAKEUP_UI, sources.MAKEUP_DEFINITIONS})
        elif item == 'Base.FertilizerEmpty' and meaning in (['function', 'empty_container'], ['function', 'reuse_container']):
            native_form = ('An exact consumer selecting Base.FertilizerEmpty as an emptying or reusable container input',
                'The Normal declaration has no capacity, CanStoreWater, replacement chain or drainable charge. The fertilizer action removes this exact empty item after using fertilizer; it does not provide a reuse or emptying action for the empty form.')
            native_paths.add(sources.FERTILIZE_ACTION)
        elif item == 'Base.WoodenLance' and meaning in (['function', 'thrust_attack'], ['function', 'shove_attack'], ['combat_property', 'reach']):
            native_form = ('Native HandWeapon animation/attack mode and MinRange/MaxRange/PushBackMod execution',
                'The Weapon declaration selects represented melee use and supplies Spear animation/range/pushback inputs. The Lua equip/control path does not determine the claimed thrust, shove or practical reach result.')
        elif item.startswith('farming.') and item.endswith('Seed') and meaning == ['function', 'unpack_seeds']:
            native_form = ('An exact opening consumer for this loose Seed form, distinct from its SeedBag counterpart',
                'The Normal loose-seed declaration and sowing action consume seeds. The independently reviewed packet-opening recipe consumes SeedBag and produces this form; its output must not be recast as an opening input.')
            native_paths.update({semantic.CRAFT, semantic.GROUPS, sources.FARM_MENU})
        if native_form and exact_fields and not exact_conflicts:
            native_paths.add(records[0]['path'])
            uncertainty = {'meaning': meaning, 'examined': {'declaration': exact_fields},
                'required_input': native_form[0], 'reason': native_form[1]}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(native_paths)],
                remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                source_binding='source_bound', source_strength='exact_form_consumer_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        if item in base.get('unsupported_wear', {}) and (meaning[0] == 'wear' or meaning == ['function', 'wear_body']):
            boundary = base['unsupported_wear'][item]
            uncertainty = {'meaning': meaning, 'examined': boundary,
                           'required_input': 'verified runtime handling of the declared ' + boundary['location'] + ' body location',
                           'reason': boundary['reason']}
            claim.update(migration_disposition='unresolved', verified_source_refs=boundary['source_refs'],
                         reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                         source_binding='source_bound', source_strength='missing_registry_binding', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                 'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                 'conservation_status': 'bounded_unresolved'})
            continue
        if meaning[0] in {'skill_current_range', 'skill_effect_range'}:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if (fields.get('Type') == 'Literature' and fields.get('SkillTrained') == meaning[1]
                    and not {'Type', 'SkillTrained', 'LvlSkillTrained', 'NumLevelsTrained'} & conflicts.keys()):
                partial = [f['ref'] for f in per_item[item]
                           if f['payload'] == {'property': meaning[1] + '_experience_multiplier', 'direction': 'increase'}]
                paths = [records[0]['path'], semantic.READ, semantic.SKILLS]
                uncertainty = {'meaning': meaning,
                    'examined': {'declaration': {k: fields.get(k) for k in ('SkillTrained', 'LvlSkillTrained', 'NumLevelsTrained')},
                        'current_level_comparison': 'ISReadABook.update permits the multiplier branch when getLvlSkillTrained <= perkLevel + 1 <= getMaxLevelTrained and the reader is not Illiterate.',
                        'effect_range': 'checkMultiplier passes getLvlSkillTrained and getMaxLevelTrained to addXpMultiplier.',
                        'claimed_lower': meaning[2], 'claimed_upper': meaning[3]},
                    'required_input': 'The native Literature.getMaxLevelTrained mapping of LvlSkillTrained and NumLevelsTrained for the claimed numeric endpoints',
                    'reason': 'The conditional multiplier and its supported-level restriction are represented. The supplied Lua consumes the maximum-level getter but does not calculate that endpoint from the declared level count. The exact numeric interval is therefore retained separately rather than replaced by a generic level condition.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in paths], remaining_work=None,
                    remaining_uncertainty=uncertainty, reason=uncertainty['reason'], source_binding='source_bound',
                    source_strength='exact_numeric_getter_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item == 'Base.DigitalWatch2' and meaning[0] in {'acquisition_place', 'acquisition_method'}:
            paths = [r['path'] for r in base['acquisition']['source_bindings']
                     if 'Foraging/' in r['path'] or r['path'].endswith(('Distributions.lua', 'ItemPicker.lua'))]
            for path in paths:
                base['reader'].read(path)
            uncertainty = {'meaning': meaning,
                'examined': 'The bound foraging clothing table registers exact left/right WristWatch forms, not Base.DigitalWatch2. The bound distribution sources provide wristwatch leads but no DigitalWatch2 token. The exact DigitalWatch2 declaration is marked Obsolete.',
                'required_input': 'An exact Base.DigitalWatch2 acquisition producer or documented alias/availability mapping supporting the claimed route',
                'reason': 'The supplied route sources do not corroborate this obsolete FullType claim. Similar wristwatch names cannot be joined to it. This is an unconfirmed predecessor acquisition claim, not a claim that runtime acquisition is impossible.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in paths],
                reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                source_binding='source_bound', source_strength='exact_route_not_corroborated', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        if item == 'Base.Hinge' and meaning[0] == 'acquisition_place' and meaning[1] in {'construction-material storage', 'workshops'}:
            forage_path = 'lua/shared/Foraging/forageDefinitions.lua'
            paths = {forage_path, semantic.MOVE, semantic.PROPS}
            texts = {p: base['reader'].read(p).decode('utf-8-sig') for p in paths}
            forage = sources.reader.mask(texts[forage_path], lua=True)
            definitions = sources.reader.mask(texts[semantic.MOVE], lua=True)
            if (re.search(r'Hinge\s*=\s*"Base.Hinge"', forage)
                    and 'generateJunkDefs();' in forage and 'for _, spawnTable in pairs(junkItems) do' in forage
                    and 'type = itemFullName' in forage and 'spawnFuncs = { doGenericItemSpawn }' in forage
                    and re.search(r'addScrapItem\(\s*"Door",\s*"Base.Hinge",\s*2,\s*80,\s*true\s*\)', definitions)):
                traced = {ref: t for token in (item, 'Hinge') for ref, t in loot_traces[token]}
                if not traced:
                    uncertainty = {'meaning': meaning, 'examined': {
                        'foraging': 'generateJunkDefs is called and registers common junk Hinge as Base.Hinge with Junk category and eight general zones, including TownZone. doGenericItemSpawn adjusts supplied-item uses/condition; it does not bind a workshop or construction-supply container.',
                        'disassembly': 'The active Door scrap definition lists two static-size Hinge rolls with base chance 80; the earlier WoodenDoor/100 definition is inside a block comment and is excluded. getScrapItemsList selects actual object materials; addScrapItemToList applies the skill modifier and random roll. This is a disassembly lead, not a discovery-place definition.',
                        'loot_vehicle': 'The bound acquisition trace set has no exact full or short Hinge loot/vehicle producer connection.'},
                        'required_input': 'An exact Hinge producer-to-room/container or zone-to-place connection supporting the claimed construction-material storage or workshop location',
                        'reason': 'The supplied exact-item leads establish general foraging registration and door disassembly alternatives but do not corroborate the predecessor discovery place. Neither TownZone nor an object material is silently equated with that place. This does not assert that Hinge acquisition is impossible.'}
                    claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                        remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                        source_binding='source_bound', source_strength='exact_route_not_corroborated', review_state='reviewed')
                    conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                        'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                    continue
        if meaning[0] == 'acquisition_place' and meaning[1] not in {'urban areas', 'trailer parks'}:
            # Short tokens are explicitly retained as leads, not silently
            # qualified to Base or joined case-insensitively to a fact.
            traced = {ref: t for token in (item, item.split('.', 1)[1]) for ref, t in loot_traces[token]}
            if traced and all(t.get('assessment') == 'assessed' for t in traced.values()):
                connections = [{'trace_ref': ref, 'source_path': t['source_path'], 'locator': t['locator'],
                                'address': t.get('address'),
                                'identity_match': 'exact_fulltype' if item in t.get('tokens', []) else 'unqualified_lead',
                                'selection_conditions': t.get('conditions'),
                                'consumer_connections': t.get('consumer_connections', [])}
                               for ref, t in sorted(traced.items())]
                paths = {picker, *(t['source_path'] for t in traced.values()),
                         *(c['source_path'] for t in traced.values() for c in t.get('consumer_connections', []))}
                source_hashes = {r['path']: r['sha256'] for r in base['acquisition']['source_bindings']}
                for path in paths:
                    if path not in base['reader'].bindings:
                        base['reader'].read(path, source_hashes[path])
                evidence = [base['reader'].bindings[p] for p in sorted(paths)]
                uncertainty = {'meaning': meaning, 'examined': connections,
                               'required_input': 'ItemPickerJava namespace/selection semantics and mapping of the exact raw room/container/vehicle tokens to the claimed place',
                               'reason': 'The raw producer lists and their room/container or vehicle references are retained for this exact item query. Lua aliases the consumer to ItemPickerJava. These declarations alone do not establish the claimed human-readable discovery place; an unrelated accepted foraging route does not conserve it.'}
                assessment_ref = model.identity('assessment', [item, 'loot_vehicle', sorted(traced)])
                source_assessments.setdefault(assessment_ref, {'item_id': item, 'producer_connections': connections,
                                                             'source_refs': evidence})
                uncertainty['examined'] = {'source_assessment_ref': assessment_ref}
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='namespace_and_engine_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                                     'migration_disposition': 'unresolved', 'successor_fact_refs': [], 'locales': {},
                                     'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if meaning == ['acquisition_process', 'sack_produce'] and item in base.get('produce_sack_sources', {}):
            source = base['produce_sack_sources'][item]
            if not source['declared_result_leads']:
                records = base['declarations'][item]
                evidence = [base['reader'].bindings[p] for p in (records[0]['path'], source['opening_path'], semantic.MENU, semantic.GROUPS, semantic.CRAFT)]
                uncertainty = {'meaning': meaning, 'examined': source,
                    'consumer_boundary': 'The exact non-writable Food declaration uses the examined Food menu. OpenSackProduce consumes the existing sack, returns EmptySandbag and adjusts produce age; it is not a reverse packing operation. The bound recipe Result clauses supply no producer for this exact sack. Loot routes do not establish a packaging process.',
                    'required_input': 'An authoritative packing recipe or item-specific packing consumer that creates this exact SackProduce form from produce and a sack',
                    'reason': 'The claimed reverse process is not corroborated by the exact declaration, complete bound recipe-result leads and actual opening callback. This does not claim that the item is unobtainable or that every possible producer is absent.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='opening_not_reverse_packing', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        pill_meanings = {'Base.Pills': ['effect', 'pain', 'decrease'],
                         'Base.PillsBeta': ['effect', 'panic', 'decrease'],
                         'Base.PillsSleepingTablets': ['effect', 'sleep_onset', 'facilitate'],
                         'Base.PillsVitamins': ['effect', 'fatigue', 'decrease'],
                         'Base.PillsAntiDep': ['effect', 'unhappiness', 'decrease']}
        if (meaning == pill_meanings.get(item) or (item == 'Base.PillsAntiDep' and meaning == ['effect_timing', 'unhappiness', 'delayed'])):
            partial = [f['ref'] for f in per_item[item] if f['payload'] == {'function': 'take_pills'}]
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if partial and fields.get('Type') == 'Drainable' and not conflicts:
                evidence = [base['reader'].bindings[p] for p in (records[0]['path'], semantic.MENU, semantic.PILLS)]
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields, 'action': sources.PILL_TAKING},
                    'required_input': 'BodyDamage.JustTookPill interpretation for ' + item + ', including effect and onset timing',
                    'reason': 'The exact pill selection and timed consumer call are represented. The active Lua calls JustTookPill without assigning the claimed medicinal effect or delay. Display names and vitamin FatigueChange do not establish those native outcomes.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=evidence, remaining_work=None, remaining_uncertainty=uncertainty,
                    reason=uncertainty['reason'], source_binding='source_bound', source_strength='exact_medication_native_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if meaning[:2] == ['output_identity', 'exact_opened_item'] or (item == 'Base.BoxOfJars' and meaning == ['output_quantity', 'multiple_empty_jars']):
            routes = [r for r in base.get('package_opening_results', {}).get(item, [])
                      if (r['result_item'] == meaning[2] if meaning[0] == 'output_identity' else r['result_clause'] == 'EmptyJar=6')]
            if routes:
                paths = {semantic.CRAFT, semantic.GROUPS, *(r['path'] for r in routes)}
                uncertainty = {'meaning': meaning, 'examined': routes,
                    'required_input': 'RecipeManager.PerformMakeItem exact result identity/count and callback argument delivery',
                    'reason': 'The named contents match an independently bound opening Result clause. The admitted opening function and its tool/eligibility conditions do not alone prove the native result item delivered. Callback age/returned-vessel behavior remains attached to the exact recipe.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='exact_opening_result_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        pill_labels = {'Base.Pills': ('진통제', 'Painkillers'), 'Base.PillsAntiDep': ('항우울제', 'Antidepressants'),
                       'Base.PillsBeta': ('긴장완화제', 'Beta Blockers'), 'Base.PillsSleepingTablets': ('수면제', 'Sleeping Tablets'),
                       'Base.PillsVitamins': ('비타민', 'Vitamins')}
        key_labels = {**{item: ('열쇠', 'Key') for item in sources.KEY_ITEMS if item != 'Base.KeyPadlock'},
                      'Base.KeyPadlock': ('자물쇠 열쇠', 'Key'), 'Base.CarKey': ('차량 열쇠', 'Car Key'),
                      'Base.Padlock': ('통자물쇠', 'Padlock'), 'Base.CombinationPadlock': ('번호 자물쇠', 'Combination Padlock')}
        key_category = item in key_labels and meaning == ['identity_label', key_labels[item][0]]
        garden_category = meaning == ['context_label', 'gardening'] and item in {
            'farming.GardeningSprayMilk', 'farming.GardeningSprayCigarettes', 'farming.GardeningSprayFull'}
        vessel_category = (item in base.get('water_container_sources', {}) and meaning[0] == 'identity_label'
                           and meaning[1] in {'물통', '물 용기', '조리 용기', '빈 분무기'})
        pill_category = item in pill_labels and meaning == ['identity_label', pill_labels[item][0]]
        fishing_category = meaning[0] == 'identity_label' and meaning[1] in {'낚싯대', 'fishing_rod', 'bait_fish'}
        artificial_category = meaning == ['state_label', 'artificial_lure']
        household_category = meaning == ['identity_label', '생활용품']
        scissors_category = (item == 'Base.Scissors' and meaning == ['identity_label', '생활 도구']
                             and any(f['payload'] == {'function': 'melee_attack'} for f in per_item[item]))
        alarm_category = meaning == ['identity_label', '알람 시계'] and item in {'Base.AlarmClock', 'Base.AlarmClock2'}
        household_clock_category = meaning == ['identity_label', '전자 기기'] and item == 'Base.AlarmClock2'
        obsolete_clock_category = meaning == ['identity_label', '전자 시계'] and item == 'Base.DigitalWatch2'
        panel_source = base.get('vehicle_panel_sources', {}).get(item)
        panel_category = (panel_source and meaning == ['identity_label', sources.PANEL_FORMS[panel_source['family']][2]])
        storage_source = base.get('vehicle_storage_sources', {}).get(item)
        storage_category = (storage_source and meaning[0] == 'identity_label' and meaning[1] in
                            {'트렁크 모듈', '소형 트렁크', '글러브 박스', '좌석 모듈', '연료 탱크'})
        running_source = base.get('vehicle_running_sources', {}).get(item)
        storage_category = storage_category or (running_source and meaning == ['identity_label', {
            'tire': '타이어', 'brake': '브레이크 부품', 'suspension': '서스펜션', 'muffler': '머플러'}[running_source['kind']]])
        map_category = meaning == ['identity_label', '지도'] and item in base.get('item_map_sources', {})
        construction_part_labels = {'Base.Stone': ('돌', 'Stone'), 'Base.Drawer': ('서랍', 'Drawer'),
                                    'Base.Doorknob': ('손잡이 부품', 'Doorknob'), 'Base.SheetRope': ('천 로프', 'Sheet Rope')}
        construction_part_category = (item in construction_part_labels and meaning == ['identity_label', construction_part_labels[item][0]])
        furniture_labels = {'서랍', '매트리스', '에어컨', '앤티크 스토브', '오락 기기', '의자', '휴지통', '정원 장식', '탁자',
                            '약품 수납장', '공구 수납장', '상자', '싱크대', '커피 머신', '믹서 설비', '게시판', '액자 증서',
                            '데스크톱 컴퓨터', '개집', '변기', '운동 기구', '깃발 장식', '냉장고', '묘비', '오븐', '조리 기기',
                            '벽 장식', '조명 기구', '우편함', '마네킹', '벽걸이 지도', '락커', '스툴', '마이크', '전자레인지',
                            '거울', '수혈 장비', '디스펜서', '푸톤', '액자 장식', '팔레트', '팝콘 기기', '포스터', '프로젝터',
                            '바비큐 그릴', '도로 차단물', '안전 콘', '위성 안테나', '체중계', '바구니', '표지판', '음료 기기',
                            '카메라 장비', '토스터', '소변기', '벽시계', '정수기', '깨진 유리'}
        furniture_category = ((meaning[0] == 'identity_label' and meaning[1] in furniture_labels
                               or (item in sources.BROKEN_GLASS_ITEMS and meaning == ['state_label', 'broken_glass']))
                              and any(f['payload'] == {'function': 'place_moveable_furniture'} for f in per_item[item]))
        cleaning_labels = {'Base.Soap2': '비누', 'Base.CleaningLiquid2': '세정액', 'Base.Bleach': '생활 소모품',
                           'Base.Broom': '생활 도구', 'Base.Mop': '대걸레', 'Base.DishCloth': '행주', 'Base.BathTowel': '목욕 수건'}
        cleaning_category = (meaning == ['identity_label', cleaning_labels.get(item)] and
                             any(f['payload'] in ({'function': 'wash_body'}, {'function': 'clean_world_blood'}) for f in per_item[item]))
        weapon_category = (meaning in (['identity_label', 'spear'], ['identity_label', '근접 무기'])
                           and any(f['payload'] == {'function': 'melee_attack'} for f in per_item[item]))
        wrist_labels = {
            'ClassicBlack': {'손목시계', '클래식 손목시계 (검은색)'},
            'ClassicBrown': {'손목시계', '클래식 손목시계 (갈색)'},
            'ClassicGold': {'금색 손목시계', '손목시계 (금)'},
            'ClassicMilitary': {'군용 손목시계'},
            'DigitalBlack': {'디지털 손목시계', '디지털 손목시계 (검은색)'},
            'DigitalRed': {'디지털 손목시계', '디지털 손목시계 (빨간색)'},
            'DigitalDress': {'디지털 손목시계', '디지털 손목시계 (메탈릭 드레스 스타일)'},
        }
        wrist_category = (meaning[0] == 'identity_label' and item.startswith(('Base.WristWatch_Left_', 'Base.WristWatch_Right_'))
                          and meaning[1] in wrist_labels.get(item.rsplit('_', 1)[-1], set()))
        disinfectant_category = (meaning == ['identity_label', '소독약'] and
                                 any(f['payload'] == {'function': 'disinfect_wound'} for f in per_item[item]))
        camping_category = ((item == 'camping.Flint' and meaning == ['identity_label', '부싯돌'])
                            or (item == 'camping.SteelAndFlint' and meaning == ['identity_label', '도구'])
                            or (item == 'camping.CampingTent' and meaning == ['context_label', 'camping']))
        media_category = (item in {'Base.Disc_Retail', 'Base.VHS_Retail', 'Base.VHS_Home'}
                          and meaning[0] == 'identity_label' and meaning[1] in {'CD', '비디오테이프', 'recorded_media'})
        radio_category = item.startswith('Radio.') and meaning == ['identity_label', '무전기']
        appearance_labels = {'Base.Hairgel': '헤어젤', 'Base.Razor': '면도기', 'Base.Mirror': '거울',
            'Base.MakeupEyeshadow': '아이 메이크업', 'Base.MakeupFoundation': '파운데이션', 'Base.Lipstick': '립스틱',
            'Base.BathTowelWet': '목욕 수건', 'Base.DishClothWet': '행주', 'Base.WildGarlic': '약재'}
        appearance_labels.update({'Base.' + name: label for name, label in {
            'Bell': '종', 'Belt': '허리띠', 'CleaningLiquid': '세정액', 'Soap': '비누', 'Dart': '다트',
            'CarvingFork': '고기 포크', 'GrillBrush': '그릴 브러시', 'Handle': '건설 재료',
            'EmptyJar': '조리 용기', 'JarLid': '조리 용기', 'MuffinTray': '머핀 쟁반', 'RoastingPan': '로스팅 팬',
            'Amplifier': '증폭기', 'MotionSensor': '동작 감지 센서', 'Radio': '휴대용 라디오',
            'Teabag': '티백', 'Umbrella': '우산', 'WaterDish': '물그릇'}.items()})
        appearance_labels.update({'Radio.ElectricWire': '전선', 'Radio.RadioReceiver': '무전 수신기',
                                  'Radio.RadioTransmitter': '무전 송신기'})
        appearance_category = (meaning == ['identity_label', appearance_labels.get(item)] or
                               item.startswith('Base.HairDye') and meaning == ['identity_label', '염색약'])
        # Reviewed standalone names/categories only. State-bearing names and
        # claims about material roles, powered operation or consumption stay out.
        reviewed_names = set('''건전지|전력 장치|전기 회로 부속|차량 배터리|전구|풀무|석탄|금속 드럼|솔방울|잔가지|.223 탄창|.308 탄창|.44 매그넘 탄창|.45 자동 탄창|5.56mm 탄창|9mm 탄창|D-E 권총|JS-2000 산탄총|M14 단발 자동소총|M16 자동소총|M1911 권총|M36 리볼버|M625 리볼버|M9 권총|nail|screw|soup_or_stew|가정용 소모품|고무 오리|공|공구 가방|광대 분장|눈가 분장|더블 배럴 산탄총|더플백|도시락통|라임|런치백|레몬|매그넘|번철 팬|병|볼링 가방|부용 큐브|비닐봉지|빨간 펜|사냥용 소총|사료 통조림|생활 도구|손잡이 냄비|수렵총|수박|식재료|아이섀도|안경류|양초|엔진 부품|연필|옥수수 가루|옥수수 분말|용기|우산|의료 가방|의료 도구|의료 보호구|의약품|인스턴트 팝콘|입술 화장|자루|잡동사니|장비 가방|전면 분장|전면 위장 분장|절구와 공이|조명 기구|종이봉투|종이클립|종이클립 상자|주전자|지갑 가방|지우개|총기 케이스|코르크 따개|토트백|톱|티백|티슈|파란 펜|펜|풋볼|프라이팬|플라스틱 컵|해골 분장|핸드백|허리 가방|화장지|휴대 가방|휴대 케이스'''.split('|'))
        reviewed_names.update({'건설 재료', '금속 재료', '목재 재료', '로프 재료', '기호품', '재료', '즉석 둔기', '창류 무기', '착용형 도구', 'alcoholic_drink', '음료'})
        reviewed_name = meaning[0] == 'identity_label' and meaning[1] in reviewed_names
        if ((meaning[0] == 'identity_label' and meaning[1] in {'식품', '의류', '액세서리', '기술 서적'} | CLOTHING_LABEL_LOCATIONS.keys() | DISPLAY_LABELS.keys())
                or reviewed_name or appearance_category or radio_category or media_category or camping_category or garden_category or vessel_category or key_category or pill_category or fishing_category or artificial_category or disinfectant_category or household_category or alarm_category or household_clock_category or wrist_category or obsolete_clock_category or panel_category or storage_category or weapon_category or map_category or cleaning_category or furniture_category or construction_part_category or scissors_category):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            expected_type = {'식품': 'Food', '기술 서적': 'Literature'}.get(meaning[1], 'Clothing')
            skill_label = meaning[1] != '기술 서적' or (fields.get('SkillTrained') and 'SkillTrained' not in conflicts)
            clothing_label = meaning[1] not in CLOTHING_LABEL_LOCATIONS or (
                fields.get('BodyLocation') in CLOTHING_LABEL_LOCATIONS[meaning[1]] and 'BodyLocation' not in conflicts
                and any(f['payload'] == {'state': 'worn_location', 'value': fields['BodyLocation']} for f in per_item[item]))
            display_label = fields.get('DisplayCategory') in DISPLAY_LABELS.get(meaning[1], set()) and 'DisplayCategory' not in conflicts
            native_label = meaning[1] in {'식품', '의류', '액세서리', '기술 서적'} | CLOTHING_LABEL_LOCATIONS.keys()
            fishing_label = ((meaning[1] in {'낚싯대', 'fishing_rod'} and 'FishingRod' in fields.get('Tags', '').split(';') and 'Tags' not in conflicts)
                             or (meaning[1] == 'bait_fish' and item == 'Base.BaitFish' and fields.get('Type') == 'Food' and 'Type' not in conflicts)
                             or (artificial_category and base.get('fishing_lure_properties', {}).get(item, {}).get('plastic') is True))
            household_label = household_category and fields.get('DisplayCategory') and 'DisplayCategory' not in conflicts
            alarm_label = ((alarm_category or household_clock_category) and fields.get('DisplayName') == 'Alarm Clock'
                           and not {'DisplayName', 'Type'} & conflicts.keys())
            alarm_label = alarm_label or (obsolete_clock_category and fields.get('Type') == 'AlarmClock'
                                         and fields.get('DisplayName') == 'Digital Watch' and not conflicts)
            wrist_label = (wrist_category and fields.get('Type') == 'AlarmClockClothing'
                           and fields.get('ClothingItem') == item.split('.', 1)[1] and not conflicts)
            weapon_label = weapon_category and (meaning[1] != 'spear' or 'Spear' in fields.get('Categories', '').split(';')) and 'Categories' not in conflicts
            furniture_label = furniture_category and fields.get('Type') == 'Moveable' and fields.get('WorldObjectSprite') and not conflicts
            construction_part_label = (construction_part_category and fields.get('Type') == 'Normal' and not conflicts
                                       and fields.get('DisplayName') == construction_part_labels[item][1])
            pill_label = (pill_category and fields.get('Type') == 'Drainable' and fields.get('DisplayCategory') == 'FirstAid'
                          and fields.get('DisplayName') == pill_labels[item][1] and not conflicts)
            key_label = key_category and fields.get('Type') == 'Key' and fields.get('DisplayName') == key_labels[item][1] and not conflicts
            key_label = key_label or (garden_category and fields.get('DisplayCategory') == 'Gardening' and not conflicts) or (vessel_category and fields.get('CanStoreWater', '').lower() == 'true' and not conflicts)
            key_label = key_label or (camping_category and fields.get('Type') == 'Normal' and not conflicts
                and fields.get('DisplayName') == {'camping.Flint': 'Flint', 'camping.SteelAndFlint': 'Flint and Steel',
                                                 'camping.CampingTent': 'Tent'}[item])
            key_label = key_label or (radio_category and fields.get('Type') == 'Radio' and not conflicts)
            key_label = key_label or (appearance_category and fields.get('Type') in {'Normal', 'Drainable'} and not conflicts
                and (item in appearance_labels or fields.get('HairDye', '').lower() == 'true'))
            key_label = key_label or (media_category and fields.get('Type') == 'Normal' and fields.get('MediaCategory')
                                      and not conflicts and any(f['payload'] == {'function': 'insert_recorded_media'} for f in per_item[item]))
            electrical_label = (item in base.get('electrical_control_sources', {}) and not conflicts and meaning[1] == {
                'Base.Battery': '건전지', 'Base.Generator': '전력 장치', 'Base.ElectronicsScrap': '전기 회로 부속',
                **{i: '차량 배터리' for i in ('Base.CarBattery1', 'Base.CarBattery2', 'Base.CarBattery3')},
                **{i: '전구' for i in sources.LIGHT_BULBS}}.get(item))
            electrical_label = electrical_label or (not conflicts and meaning[1] == {
                'Base.Bellows': '풀무', 'Base.Coal': '석탄', 'Base.Log': '건설 재료', 'Base.MetalDrum': '금속 드럼',
                'Base.Pinecone': '솔방울', 'Base.TreeBranch': '목재 재료', 'Base.Twigs': '잔가지',
                'Base.UnusableWood': '쓸모없는 목재', 'Base.PopBottleEmpty': '병', 'Base.WhiskeyEmpty': '병',
                'Base.WineEmpty': '병', 'Base.WineEmpty2': '병'}.get(item)
                and fields.get('Type') in {'Normal', 'Drainable'})
            reviewed_name_bound = reviewed_name and bool(fields.get('Type')) and not {'Type', 'DisplayName', 'DisplayCategory'} & conflicts.keys()
            if reviewed_name_bound or electrical_label or key_label or pill_label or display_label or fishing_label or disinfectant_category or household_label or alarm_label or wrist_label or panel_category or storage_category or weapon_label or cleaning_category or furniture_label or construction_part_label or (scissors_category and fields.get('Type') == 'Weapon' and fields.get('DisplayCategory') == 'Household' and not conflicts) or (map_category and fields.get('Type') == 'Map' and 'Type' not in conflicts) or (native_label and fields.get('Type') == expected_type and 'Type' not in conflicts and skill_label and clothing_label):
                reason = ('Remove the standalone taxonomy label from Layer 3: this exact label supplies only a category, '
                          'which ARCHITECTURE assigns to Layer 2 navigation. This is responsibility removal, not a '
                          'claim that a replacement classification surface was inspected or that function/state meanings '
                          'were relocated. Independent use, effect, location, and acquisition claims remain accounted separately.')
                evidence = [base['reader'].bindings[records[0]['path']], base['reader'].bindings['docs/ARCHITECTURE.md']]
                if artificial_category:
                    evidence.append(base['reader'].bindings[sources.FISHING_PROPERTIES])
                if disinfectant_category:
                    evidence.extend(base['reader'].bindings[p] for p in (sources.HEALTH, sources.DISINFECT))
                claim.update(migration_disposition='responsibility_removed', reason=reason,
                             verified_source_refs=evidence, remaining_work=None, remaining_uncertainty=None,
                             source_binding='source_and_owner_bound', source_strength='responsibility_boundary', review_state='reviewed',
                             owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': '정보 계층 / 2계층 and 3계층',
                                                      'destination_presence': 'not_claimed', 'declaration_type': fields.get('Type'),
                                                      'declared_display_category': fields.get('DisplayCategory'),
                                                      'declared_body_location': fields.get('BodyLocation')})
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                                     'migration_disposition': 'responsibility_removed', 'successor_fact_refs': [],
                                     'locales': {}, 'residual': None, 'removal_reason': reason,
                                     'conservation_status': 'responsibility_removed'})
                continue
        candidates = per_item[item]
        if ((item.startswith('Base.LogStacks') and meaning == ['output_identity', 'logs'])
                or (item == 'Base.Frog' and meaning == ['output_identity', 'frog_meat'])
                or (item == 'Base.BrokenFishingNet' and meaning == ['function', 'recover_wire'])):
            selected = {'Base.Frog': 'prepare_frog_meat', 'Base.BrokenFishingNet': 'process_broken_fish_net'}.get(item, 'unbundle_logs')
            partial = [f for f in candidates if f['payload'] == {'function': selected}]
            if partial:
                evidence = sorted({o['source_path'] for f in partial for p in f['provenance_refs']
                                   for o in [semantic_payload['observations'][r] for r in semantic_payload['provenance'][p.split('/', 1)[-1]]['observation_refs']]})
                uncertainty = {'meaning': meaning,
                    'examined': sources.WIRE_RECOVERY if item == 'Base.BrokenFishingNet' else
                                sources.FROG_PREPARATION if item == 'Base.Frog' else sources.LOG_BINDING,
                    'required_input': 'Native RecipeManager exact result identity/count and inventory delivery' +
                                      (' including the unnormalized Result:Wire;3 parser behavior' if item == 'Base.BrokenFishingNet' else ''),
                    'reason': 'The source-confirmed transformation input and actual callback are represented, while the claimed returned item depends on the exact native result creation/delivery boundary. No returned item or numeric yield is invented from the display text.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=[f['ref'] for f in partial],
                    verified_source_refs=[base['reader'].bindings[p] for p in evidence], remaining_work=None,
                    remaining_uncertainty=uncertainty, reason=uncertainty['reason'], source_binding='source_bound',
                    source_strength='exact_recipe_result_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [f['ref'] for f in partial], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item == 'Base.WildGarlic' and meaning in (['function', 'disinfect_wound'], ['function', 'medicate_wound']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Normal' and not conflicts:
                paths = {records[0]['path'], semantic.MENU, sources.HEALTH, sources.DISINFECT, *sources.POULTICES.values()}
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                    'dispatch': 'Disinfection selects actual alcoholic/disinfectant supply, and poultice application selects WildGarlicCataplasm. The exact Normal WildGarlic raw plant matches neither, and Food WildGarlic2 is not an alias.'},
                    'required_input': 'An exact consumer selecting raw Base.WildGarlic for the claimed direct wound treatment',
                    'reason': 'The available health consumers do not establish direct disinfection or medication with the raw plant. Its hidden recipe input role is represented independently and cannot substitute for direct treatment.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='examined_exact_dispatch_gap', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if (item.startswith('Base.HairDye') and meaning[:2] == ['visual_effect', 'dye_color'] or
                item in {'Base.Lipstick', 'Base.MakeupEyeshadow'} and meaning[0] == 'visual_effect'):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if not conflicts and (fields.get('HairDye', '').lower() == 'true' or fields.get('MakeUpType') in {'Lips', 'Eyes'}):
                dye = fields.get('HairDye', '').lower() == 'true'
                paths = {records[0]['path'], semantic.MENU, semantic.DYE} if dye else {
                    records[0]['path'], semantic.MENU, sources.MAKEUP_UI, sources.MAKEUP_DEFINITIONS}
                partial = [f['ref'] for f in candidates if f['payload'].get('function') in {
                    'dye_hair_or_beard', 'apply_lip_makeup', 'apply_eye_makeup'}]
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                    'consumer': sources.DYE_APPLICATION if dye else sources.MAKEUP_LIFECYCLE},
                    'required_input': ('Native binding of declared RGB values to dye getters and visual color rendering; especially Ginger declares Strawberry Blonde, independently from Blonde' if dye else
                                       'Exact registered makeup item visual/texture binding and native worn-slot rendering'),
                    'reason': 'The actual color setter or cosmetic item replacement is represented. The predecessor named visible color is separate from its label and cannot be proved by a registry/item name without the exact native visual binding.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)], remaining_work=None,
                    remaining_uncertainty=uncertainty, reason=uncertainty['reason'], source_binding='source_bound',
                    source_strength='exact_visual_binding_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item in {'Base.BathTowelWet', 'Base.DishClothWet'} and meaning in (
                ['function', 'dry_towel'], ['function', 'dry_the_body'],
                ['condition', 'body_drying', 'after_towel_dries'], ['state_label', 'wet_towel']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Wet', '').lower() == 'true' and fields.get('ItemWhenDry') == item[:-3] and not conflicts:
                paths = {records[0]['path'], semantic.MENU, sources.DRY_BODY, sources.WORLD_MENU, sources.CLEAN_BLOOD}
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                    'dispatch': 'Exact dry BathTowel/DishCloth are selected for body drying and world blood cleaning. Wet siblings are not selected and have no Lua drying action. Wet, WetCooldown and ItemWhenDry are native item fields.'},
                    'required_input': 'Exact native Wet/WetCooldown/ItemWhenDry executor, returned item identity and remaining-use state before the represented dry-form body action',
                    'reason': 'The source declares a dry-form target but supplies no executor proving when the wet form dries or returns with usable supply. The predecessor automatic-drying/reuse implication remains bounded to that native transition; the dry-form action is independently represented.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                    remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                    source_binding='source_bound', source_strength='exact_wet_item_executor_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if meaning == ['effect', 'garment_protection', 'increase'] and item == 'Base.LeatherStrips':
            partial = [f['ref'] for f in candidates if f['payload'] == {'function': 'apply_garment_patch'}]
            if partial:
                uncertainty = {'meaning': meaning, 'partial_fact_refs': partial,
                    'examined': 'ISGarmentUI offers the selected LeatherStrips to repairClothing. Its tooltip calls native canFullyRestore/getScratchDefenseFromItem/getBiteDefenseFromItem; ISRepairClothing calls clothing:addPatch with the actual selected fabric.',
                    'required_input': 'Clothing.addPatch/canFullyRestore and fabric-to-scratch/bite-defense calculations for LeatherStrips and the selected garment part',
                    'reason': 'Patching/padding use and its material, thread, needle, part and interruption conditions are represented. The native garment/fabric calculation decides restoration versus protection and the resulting values; a leather label does not establish an unconditional defense increase.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in (sources.GARMENT_UI, sources.PATCH_GARMENT, semantic.MENU)],
                    reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                    source_binding='source_bound', source_strength='exact_native_patch_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item == 'Base.Bleach' and meaning == ['hazard', 'toxic_bleach']:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Poison', '').lower() == 'true' and not {'Poison', 'PoisonPower', 'UseForPoison'} & conflicts.keys():
                uncertainty = {'meaning': meaning,
                    'examined': {k: fields.get(k) for k in ('Type', 'CustomContextMenu', 'Poison', 'PoisonPower', 'PoisonDetectionLevel', 'UseForPoison', 'ReplaceOnUse')},
                    'required_input': 'IsoGameCharacter.Eat and native evolved-recipe poisoning interpretation of this exact Bleach declaration',
                    'reason': 'The script declares Poison=true/PoisonPower=120 and the consumption action delegates to character:Eat. Evolved-recipe selection applies the explicit EnablePoisoning/Bleach policy. Those declarations and guards do not establish a contact hazard or quantify the resulting toxicity; native poisoning execution remains. The independent world-blood cleaning function is represented.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in (records[0]['path'], semantic.MENU, semantic.EAT)],
                    reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                    source_binding='source_bound', source_strength='exact_native_poisoning_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if meaning == ['attack_form', 'thrust']:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Weapon' and fields.get('SwingAnim') == 'Spear' and not {'Type', 'SwingAnim', 'Categories'} & conflicts.keys():
                partial = [f['ref'] for f in candidates if f['payload'] == {'function': 'melee_attack'}]
                uncertainty = {'meaning': meaning,
                    'examined': {'SwingAnim': fields['SwingAnim'], 'Categories': fields.get('Categories'), 'DamageCategory': fields.get('DamageCategory'),
                                 'consumer': 'attackHook dispatches DoAttack through the non-ranged branch without interpreting the Spear animation token.'},
                    'required_input': 'DoAttack/Spear animation selection defining the actual thrust motion for this exact weapon',
                    'reason': 'Conditional melee use is represented. The Spear animation and sound labels are source leads, not the motion consumer; they do not independently identify the claimed thrust motion.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in (records[0]['path'], sources.FIREARM)],
                    reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                    source_binding='source_bound', source_strength='exact_attack_animation_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item == 'Base.AlarmClock' and meaning in (
                ['effect', 'device_sound', 'after_delay'], ['condition', 'device_sound', 'after_placement'],
                ['function', 'reuse_activated_device']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('PhysicsObject') == 'NoiseGenerator' and not conflicts:
                partial = [f['ref'] for f in candidates if f['payload'].get('function') in {
                    'set_device_timer', 'place_noise_device', 'retrieve_placed_device'}]
                paths = [records[0]['path'], semantic.MENU, sources.DEVICE_TIMER, sources.DEVICE_PLACE,
                         sources.WORLD_MENU, sources.DEVICE_TAKE]
                reuse = meaning == ['function', 'reuse_activated_device']
                uncertainty = {'meaning': meaning, 'examined': {
                    'declaration': {k: fields.get(k) for k in ('Type', 'PhysicsObject', 'NoiseRange', 'ExplosionTimer', 'CanBePlaced', 'CanBeReused', 'OBSOLETE')},
                    'consumer': 'The positive timer dialog saves a numeric setting; placement constructs IsoTrap. Retrieval returns trap:getItem only while an object and item remain. None of these Lua paths defines the sound event or post-activation item retention.'},
                    'required_input': ('IsoTrap activation/item retention and CanBeReused interpretation' if reuse else
                                       'IsoTrap countdown/NoiseGenerator sound execution after placement') + '; runtime availability of this OBSOLETE declaration',
                    'reason': ('Conditional retrieval is represented, but it does not establish survival through activation or repeat use. CanBeReused is a source lead whose native consumer is missing.' if reuse else
                               'The delay setter and placement are represented independently. The native IsoTrap executor determines when and whether the declared sound is emitted; timer and sound field names alone do not establish that effect.')}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                    verified_source_refs=[base['reader'].bindings[p] for p in paths], reason=uncertainty['reason'],
                    remaining_uncertainty=uncertainty, remaining_work=None, source_binding='source_bound',
                    source_strength='exact_device_executor_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                    'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
                continue
        if item in {'Base.SheetRope', 'Base.Rope'} and meaning == ['function', 'traverse_installed_rope']:
            records = base['declarations'].get(item, [])
            paths = {records[0]['path'], sources.WORLD_MENU, sources.ADD_ROPE, sources.REMOVE_ROPE,
                     sources.CLIMB_ROPE, sources.OBJECT_COMMANDS}
            partial = [f['ref'] for f in candidates if f['payload'] == {'function': 'start_escape_rope_ascent'}]
            uncertainty = {'meaning': meaning,
                'examined': 'The active installed-rope menu passes down=false, walks to the rope square and queues the guarded native ascent call. ISClimbSheetRopeAction also contains a down=true branch, but this local menu does not select it. Add/remove actions and server attachment-type dispatch are independently interpreted.',
                'required_input': 'Native installed-rope traversal and descent entry, including current rope continuity, attachment, character eligibility and completion',
                'reason': 'Conditional ascent control is represented, but the broader up/down climbing statement includes native traversal and descent. Merely defining a down branch does not establish its active local selection or successful travel. The exact remainder is retained independently of the installation material role.'}
            claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                         verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                         remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                         source_binding='source_bound', source_strength='exact_installed_rope_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        if item in sources.BROKEN_GLASS_ITEMS and meaning == ['caution', 'approaching_broken_glass']:
            records = base['declarations'].get(item, [])
            paths = {records[0]['path'], sources.WORLD_MENU, sources.PICKUP_GLASS, sources.WINDOW_GLASS,
                     sources.MOVE_TOOLS, semantic.PROPS}
            uncertainty = {'meaning': meaning,
                'examined': {'sprite': sources.stable_properties(records[0])[0].get('WorldObjectSprite'),
                    'pickup': 'The active pickup action and IsoBrokenGlass branch explicitly scratch/embed glass in an ungloved hand under random checks. These are pickup effects, not an approach or foot-contact trigger.',
                    'placement': 'Moveable placement constructs IsoBrokenGlass from native sprite IsoType; the Lua constructor caller does not execute contact/foot injury.',
                    'window': 'The separate window-frame removal action calls removeBrokenGlass on a smashed window and does not consume this shard item.'},
                'required_input': 'Native contact/foot-injury handling for the exact placed IsoBrokenGlass sprite, including actual triggering contact and footwear conditions',
                'reason': 'The predecessor approach warning is independent of the source-confirmed pickup hazard. Available placement and pickup Lua have been interpreted; they do not establish this contact effect or an approach radius. That specific engine behavior remains unresolved.'}
            claim.update(migration_disposition='unresolved', verified_source_refs=[base['reader'].bindings[p] for p in sorted(paths)],
                         remaining_work=None, remaining_uncertainty=uncertainty, reason=uncertainty['reason'],
                         source_binding='source_bound', source_strength='exact_glass_contact_boundary', review_state='reviewed')
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty, 'conservation_status': 'bounded_unresolved'})
            continue
        matched = []
        furniture_gloss = (meaning in (['context_label', 'equipment_layout'], ['context_label', 'decoration_layout'],
                                      ['context_label', 'indoor_furniture_layout'], ['context_label', 'storage_furniture_layout'],
                                      ['intended_use', 'area_marking'])
                           and any(f['payload'] == {'function': 'place_moveable_furniture'} for f in per_item[item]))
        construction_meanings = {'bed_construction': {'onBed'}, 'drawer_table_construction': {'onSmallWoodTableWithDrawer'},
            'door_construction': {'onWoodenDoor', 'onDoubleWoodenDoor'}, 'hinged_structure_construction': {'onWoodenDoor', 'onDoubleWoodenDoor'},
            'barbed_fence_construction': {'onBarbedFence'}, 'bag_barrier_construction': {'onSangBagWall', 'onGravelBagWall'}}
        construction_claim = (meaning[0] == 'role' and meaning[1] in construction_meanings and meaning[2] == 'material'
                              and any(r['factory'] in construction_meanings[meaning[1]] and r['status'] == 'active_material'
                                      for r in base.get('factory_relations', {}).get(item, [])))
        if item in sources.BROKEN_GLASS_ITEMS and meaning == ['caution', 'clearing_broken_glass']:
            matched = [f for f in candidates if f['payload'].get('direction') == 'apply_during_glass_pickup']
        elif construction_claim:
            matched = [f for f in candidates if f['payload'] == {'role': 'material'} and f['context_ref']
                       and (facts[f['context_ref']]['payload'] == {'activity': 'carpentry_menu_construction'}
                            or (meaning[1] == 'hinged_structure_construction'
                                and facts[f['context_ref']]['payload'] == {'activity': 'metal_welding_construction'}))]
        elif meaning == ['role', 'stone_hammer_crafting', 'material'] and item == 'Base.Stone':
            matched = [f for f in candidates if f['payload'] == {'role': 'material'} and f['context_ref']
                       and facts[f['context_ref']]['payload'] == {'activity': 'tool_crafting'}]
        elif item in {'Base.Plantain', 'Base.Comfrey'} and meaning == ['identity_label', '식품']:
            matched = [f for f in candidates if f['payload'] == {'role': 'material'} and f['context_ref']
                       and facts[f['context_ref']]['payload'] == {'activity': 'poultice_preparation'}]
        elif item == 'Base.MakeupFoundation' and meaning == ['cosmetic_role', 'base_layer']:
            matched = [f for f in candidates if f['payload'] == {'function': 'apply_makeup'}]
        elif furniture_gloss:
            matched = [f for f in candidates if f['payload'] in ({'function': 'place_moveable_furniture'}, {'function': 'remove_placed_furniture'})]
        elif ((item == 'Base.Thread' and meaning in (['role_unspecified_context', 'material'], ['role', 'fabric_crafting', 'material'], ['consumption_property', 'consumable']))
                or (item == 'Base.LeatherStrips' and meaning == ['material_form', 'leather_patch'])):
            matched = [f for f in candidates if f['payload'] == {'function': 'apply_garment_patch'}]
        elif meaning == ['intended_use', 'navigation_planning'] and item in base.get('item_map_sources', {}):
            # Correct the human-use gloss to the actual viewer operation. It does
            # not establish an automatic route planner or safe/accurate route.
            matched = [f for f in candidates if f['payload'] == {'function': 'view_item_map'}]
        elif item in sources.STRAP_SPEED and meaning in (
                ['effect', 'reload_speed', 'increase'], ['condition', 'reload_speed', 'worn'],
                ['condition', 'reload_speed', 'shotgun' if item.endswith('_Shells') else 'non_shotgun']):
            matched = [f for f in candidates if f['payload'] == (
                {'property': 'reload_speed_setting', 'direction': 'multiply_1_15'} if meaning[0] == 'effect' else
                {'predicate': sources.STRAP_SPEED[item]})]
        elif meaning == ['identity_label', '손상 낚싯대'] and item == 'Base.FishingRodBreak':
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.ROD_REPAIR_INPUT}]
        elif meaning[0] in {'acquisition_zone', 'acquisition_method'} or meaning in [['acquisition_place', 'urban areas'], ['acquisition_place', 'trailer parks']]:
            zone = (meaning[1] if meaning[0] == 'acquisition_zone' else
                    {'urban areas': 'TownZone', 'trailer parks': 'TrailerPark'}.get(meaning[1]))
            for fact in candidates:
                if fact['fact_kind'] != 'acquisition' or fact['payload']['route']['method'] not in {'foraging', 'foraging_crop_seed'}:
                    continue
                conditions = fact['payload']['conditions']
                item_zones = {z for z, w in acquisition_expression.weights(conditions['zones']) if float(w) > 0}
                category_zones = {z for c in conditions['category_conditions'].values()
                                  for z, w in acquisition_expression.weights(c['zoneChance']) if float(w) > 0}
                if (zone is None and meaning == ['acquisition_method', 'foraging']) or zone in item_zones & category_zones:
                    matched.append(fact)
        elif item in base.get('vehicle_storage_sources', {}) and meaning in (
                ['function', 'sit_on_vehicle_seat'], ['function', 'sit_in_vehicle']):
            matched = [f for f in candidates if f['payload'] == {'function': 'use_vehicle_seat'}]
        elif item in base.get('vehicle_storage_sources', {}) and meaning in (
                ['function', 'install_vehicle_part'], ['function', 'install_vehicle_seat']):
            matched = [f for f in candidates if f['payload'] == {'function': 'install_vehicle_storage_part'}]
        elif item in base.get('vehicle_storage_sources', {}) and meaning == ['function', 'store_items_on_vehicle_seat']:
            matched = [f for f in candidates if f['payload'] == {'function': 'store_vehicle_items'}]
        elif meaning == ['function', 'reuse_container']:
            matched = [f for f in candidates if f['payload'] == {'function': 'store_water'}]
        elif meaning[0] == 'function':
            matched = [f for f in candidates if f['payload'] == {'function': meaning[1]}]
            if meaning[1] in {'eat_food', 'drink_food'}:
                matched = [f for f in candidates if f['payload'].get('function') in
                    ({'eat_food', 'consume_edible_food', 'drink_food_contents'} if meaning[1] == 'eat_food'
                     else {'drink_food_contents'})]
            if meaning[1] == 'light_campfire' and item in sources.PETROL_ITEMS:
                matched = [f for f in candidates if f['payload'] == {'function': 'light_campfire_with_petrol'}]
            if meaning[1] == 'catch_animals' and item == 'Base.TrapStick':
                matched = [f for f in candidates if f['payload'] == {'function': 'catch_trap_animal'}]
            if meaning[1] == 'erase_item_map_annotations':
                matched = [f for f in candidates if f['payload'] == {'function': 'erase_map_annotations'}]
            if meaning[1] == 'insert_device_battery' and item == 'Base.Rubberducky2':
                matched = [f for f in candidates if f['payload'] == {'function': 'accept_battery_charge'}]
            if meaning[1] == 'light_campfire' and item == 'Base.PercedWood':
                matched = [f for f in candidates if f['payload'] == {'function': 'light_campfire_by_friction'}]
            if meaning[1] == 'fold_umbrella' and item.startswith('Base.ClosedUmbrella'):
                matched = [f for f in candidates if f['payload'] == {'function': 'unfold_umbrella'}]
            if item == 'Base.FishingNet' and meaning[1] == 'catch_bait_fish':
                matched = [f for f in candidates if f['payload'] == {'function': 'check_fishing_net'}]
            fuel_function = ({'blow_forge_air': 'use_furnace_bellows'} if item == 'Base.Bellows' else
                {'supply_charcoal_barbecue_fuel': 'supply_hearth_fuel'} if item == 'Base.Charcoal' else
                {'transfer_fuel': 'transfer_vehicle_fuel', 'refuel_vehicle': 'transfer_vehicle_fuel',
                 'supply_fuel': 'refuel_generator', 'carry_gasoline': 'transfer_vehicle_fuel'} if item in sources.PETROL_ITEMS else
                {'store_fuel': 'fill_petrol_container', 'carry_fuel': 'transfer_vehicle_fuel'} if item in sources.EMPTY_PETROL_ITEMS else {})
            if meaning[1] in fuel_function:
                matched = [f for f in candidates if f['payload'] == {'function': fuel_function[meaning[1]]}]
            if meaning[1] == 'wash_clothing' and item in {'Base.Soap2', 'Base.CleaningLiquid2'}:
                matched = [f for f in candidates if f['payload'] == {'function': 'wash_equipment'}]
            if meaning[1] == 'sew_fabric' and item == 'Base.Needle':
                matched = [f for f in candidates if f['payload'] == {'function': 'apply_garment_patch'}]
            panel = base.get('vehicle_panel_sources', {}).get(item)
            if panel and meaning[1] in {'remove_vehicle_panel_or_glass', 'install_vehicle_panel_or_glass',
                                        'refit_vehicle_' + panel['part_meaning']}:
                operation = 'remove' if meaning[1] == 'remove_vehicle_panel_or_glass' else 'install'
                matched = [f for f in candidates if f['payload'] == {'function': operation + '_vehicle_' + panel['part_meaning']}]
            if meaning[1] == 'read_or_consult':
                matched = [f for f in candidates if f['payload'] == {'function': 'read_literature'}]
            if meaning[1] in {'write_documents', 'revise_documents'}:
                matched = [f for f in candidates if f['payload'] == {'function': 'write_note_pages'}]
            elif meaning[1] == 'attack_as_weapon':
                matched = [f for f in candidates if f['payload'].get('function') in {'melee_attack', 'fire_ammunition'}]
            if meaning[1] == 'wear_body':
                matched = [f for f in candidates if f['payload'].get('function') in {'wear_on_body', 'wear_configured_clothing'}]
            elif meaning[1] == 'redistribute_container_contents':
                matched = [f for f in candidates if f['payload'] == {'function': 'store_and_retrieve_items'}]
            elif meaning[1] == 'replace_vehicle_suspension' and item in base.get('vehicle_running_sources', {}):
                matched = [f for f in candidates if f['payload'].get('function') in {'install_vehicle_suspension', 'remove_vehicle_suspension'}]
            elif meaning[1] == 'adjust_vehicle_tire_pressure' and item == 'Base.TirePump':
                matched = [f for f in candidates if f['payload'] == {'function': 'inflate_vehicle_tire'}]
            elif meaning[1] == 'sow_seeds':
                matched = [f for f in candidates if f['payload'].get('function') in {'sow_seeds', 'sow_extracted_seeds'}]
        elif item in sources.DRAINABLE_MATERIALS and meaning in (
                ['role_unspecified_context', 'material'], ['consumption_property', 'consumable']):
            matched = [f for f in candidates if f['fact_kind'] == 'context_role'
                       and f['payload'].get('role') in {'material', 'repair_material', 'ingredient'}]
        elif item in {'Base.Twine', 'Base.Wire'} and meaning == ['role', 'fishing_net_crafting', 'material']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'fishing_gear_crafting'} and has_recipe(f, {'Make Fishing Net'})]
        elif item == 'Base.DuctTape' and meaning in (['role', 'device_assembly', 'material'], ['role', 'spear_upgrade', 'material']):
            context = 'explosive_modification' if meaning[1] == 'device_assembly' else 'spear_upgrade'
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': context}]
        elif item == 'Base.Woodglue' and meaning == ['role', 'repair', 'repair_material']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'repair_material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'repair'}]
        elif item == 'Base.WeldingRods' and (meaning == ['role', 'welding_construction', 'material']
                or meaning in (['context_example', 'welding_construction', 'metal_fences'], ['context_example', 'welding_construction', 'metal_doors'])):
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'metal_welding_construction'}]
        elif item == 'Base.Vinegar' and meaning == ['role', 'food_preparation', 'ingredient']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'vegetable_jarring'}]
        elif item in {'Base.GravyMix', 'Base.PancakeMix'} and meaning in (
                ['condition', 'gravy_preparation', 'water'], ['condition', 'pancake_preparation', 'water']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FOOD_ASSEMBLY}
                       and has_recipe(f, {'Make Gravy' if item == 'Base.GravyMix' else 'Make Pancake'})]
        elif item == 'Base.Battery' and meaning in (
                ['role', 'portable_device_power', 'power_supply'], ['example_target', 'portable_device_power', 'flashlight']):
            matched = [f for f in candidates if f['payload'] == {'function': 'supply_portable_device_charge'}]
        elif meaning == ['condition', 'lighting', 'replaceable_bulb']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.LAMP_BULB}]
        elif item == 'Base.CarBatteryCharger' and meaning == ['condition', 'battery_charging', 'removed_from_vehicle']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.CHARGER_CONTROLS}]
        elif item == 'Base.Generator' and meaning == ['condition', 'generator_power', 'installed']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.GENERATOR_CONTROL}]
        elif meaning == ['power_source', 'battery']:
            matched = [f for f in candidates if f['payload'] == {'function': 'accept_battery_charge'}]
        elif meaning[0] == 'output_identity' and meaning[1] in {'electronic_scrap', 'electronic_parts'}:
            matched = [f for f in candidates if f['payload'] == {'function': 'dismantle_electronics'}
                       and any(facts[q]['payload'] == {'predicate': sources.SCRAP_RECOVERY} for q in f['qualifier_refs'])]
        elif meaning[0] == 'effect':
            matched = [f for f in candidates if f['payload'] == {'property': meaning[1], 'direction': meaning[2]}]
            if item in {'Base.Soap2', 'Base.CleaningLiquid2'} and meaning[1:] in (['blood', 'remove'], ['dirt', 'remove']):
                matched = [f for f in candidates if f['payload'] == {'property': 'washed_surface_' + meaning[1], 'direction': 'remove'}]
            if meaning[1:] == ['fishing_lure', 'may_break']:
                matched = [f for f in candidates if f['payload'] == {'predicate': sources.FISHING_LURE_LOSS}]
            if meaning[1:] in (['skill_knowledge', 'gain'], ['recipe_knowledge', 'gain']):
                records = base['declarations'].get(item, [])
                fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
                if fields.get('SkillTrained') and not fields.get('TeachedRecipes') and not {'SkillTrained', 'TeachedRecipes'} & conflicts.keys():
                    matched = [f for f in candidates if f['payload'] == {'property': fields['SkillTrained'] + '_experience_multiplier', 'direction': 'increase'}]
            if meaning[1:] == ['food_sickness', 'increase_if_poisonous']:
                matched = [f for f in candidates if f['payload'] == {'property': 'food_sickness', 'direction': 'increase'}
                           and any(facts[q]['payload'] == {'predicate': sources.POISONOUS_WILD_FOOD} for q in f['qualifier_refs'])]
        elif meaning[0] == 'conditional_effect':
            predicate = {'smoker': sources.SMOKER_EFFECT, 'nonsmoker': sources.NONSMOKER_EFFECT}.get(meaning[3])
            matched = [f for f in candidates if f['payload'] == {'property': meaning[1], 'direction': meaning[2]}
                       and any(facts[q]['payload'] == {'predicate': predicate} for q in f['qualifier_refs'])]
        elif meaning == ['role', 'spear_upgrade', 'attachment']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'attachment'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'spear_upgrade'}]
        elif meaning[0] == 'role' and meaning[1] in {'tool_crafting', 'splint_crafting', 'fishing_gear_crafting', 'furniture_crafting', 'tent_kit_making', 'campfire_kit_preparation', 'poultice_preparation', 'bandaging_material_preparation', 'metal_forging', 'welded_parts', 'mattress_preparation', 'vegetable_jarring'} and meaning[2] in {'material', 'tool'}:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': meaning[2]}
                       and facts[f['context_ref']]['payload'] == {'activity': meaning[1]}]
        elif meaning == ['condition', 'vegetable_jarring', 'with_empty_jar']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.JAR_PREPARATION}]
        elif meaning[0] == 'role' and meaning[1:] in (['radio_crafting', 'material_or_component'], ['radio_crafting', 'material']):
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'radio_crafting'}]
        elif meaning[0] == 'role' and meaning[1] in PREPARATION_ROLES:
            context, names = PREPARATION_ROLES[meaning[1]]
            role = 'fuel' if meaning[2] == 'fuel_supply' else meaning[2]
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': role}
                       and (context is None or facts[f['context_ref']]['payload'] == {'activity': context})
                       and has_recipe(f, names)]
        elif meaning[0] == 'role' and meaning[1] in {'dough_preparation', 'batter_preparation', 'cookie_preparation', 'plaster_preparation', 'trap_crafting', 'woodworking'}:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': meaning[2]}
                       and facts[f['context_ref']]['payload'] == {'activity': meaning[1]}]
        elif meaning[0] == 'role' and meaning[1:] in (['food_preparation', 'tool'], ['food_preparation', 'container']):
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': meaning[2]}
                       and facts[f['context_ref']]['payload'].get('activity') in {'food_preparation', 'dough_preparation', 'batter_preparation', 'cookie_preparation', 'food_portioning', 'fish_preparation', 'animal_butchery', 'grain_preparation'}]
        elif meaning == ['role', 'sawing', 'tool']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'tool'}
                       and facts[f['context_ref']]['payload'].get('activity') in {'woodworking', 'shotgun_modification'}]
        elif meaning[0] == 'role' and meaning[1:] == ['food_preparation', 'ingredient']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'ingredient'}
                       and facts[f['context_ref']]['payload'].get('activity') in {'food_preparation', 'dough_preparation', 'batter_preparation'}]
            if not matched:
                matched = [f for f in candidates if f['payload'] == {'function': 'prepare_opened_food_ingredient'}]
        elif meaning[0] == 'role' and meaning[1:] in (['fire_starting', 'tinder'], ['burning', 'fuel']):
            function = 'provide_campfire_tinder' if meaning[2] == 'tinder' else 'supply_campfire_fuel'
            matched = [f for f in candidates if f['payload'] == {'function': function}]
        elif meaning == ['context', 'food_preparation']:
            matched = [f for f in candidates if f['payload'].get('activity') in {'food_preparation', 'dough_preparation', 'batter_preparation'}]
        elif meaning == ['context_label', 'medical_use']:
            matched = [f for f in candidates if f['payload'].get('function') in {'apply_bandage', 'disinfect_wound'}]
        elif item in sources.PETROL_ITEMS and meaning == ['context_label', 'vehicle_maintenance']:
            matched = [f for f in candidates if f['payload'] == {'function': 'transfer_vehicle_fuel'}]
        elif (item == 'Base.Coal' and meaning == ['role', 'furnace_fueling', 'fuel']
              or item == 'Base.Pinecone' and meaning == ['role', 'other_fire_fueling', 'fuel']):
            matched = [f for f in candidates if f['payload'] == {'function':
                'supply_furnace_fuel' if item == 'Base.Coal' else 'supply_hearth_fuel'}]
        elif meaning[0] == 'role' and meaning[1:] == ['firearm_loading', 'ammunition']:
            matched = [f for f in candidates if f['payload'] == {'function': 'load_matching_ammunition'}]
        elif meaning[0] == 'wear':
            matched = [f for f in candidates if f['payload'].get('state') == 'worn_location'
                       and f['payload']['value'] in WEAR_LOCATIONS.get(meaning[1], set())]
        elif meaning[0] == 'state':
            matched = [f for f in candidates if f['payload'] == {'state': meaning[1], 'value': meaning[2]}]
        elif meaning == ['condition', 'package_opening', 'can_opener']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.CAN_OPENING}]
        elif meaning[:2] == ['condition', 'campfire_lighting']:
            predicate = (sources.CAMP_FRICTION if meaning[2] == 'branch_or_stick' and item == 'Base.PercedWood'
                         else sources.CAMP_IGNITER if meaning[2] in {'tinder', 'tinder_or_fuel'} else None)
            matched = [f for f in candidates if f['payload'] == {'predicate': predicate}]
        elif meaning == ['condition', 'radio', 'tuned_frequency']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.RADIO_TUNING}]
        elif meaning in (['condition', 'door_lock', 'matching_key'], ['condition', 'padlock', 'matching_key']):
            predicate = sources.DOOR_KEY_USE if meaning[1] == 'door_lock' else sources.PADLOCK_KEY_USE
            matched = [f for f in candidates if f['payload'] == {'predicate': predicate}]
        elif meaning == ['condition', 'vehicle', 'matching_key']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.VEHICLE_KEY_USE}]
        elif meaning == ['condition', 'skill_reading', 'literate']:
            matched = [f for f in candidates if f['payload'] == {'predicate': 'The character can read, is awake, meets any book skill requirement, and the reading action remains valid for possession, page state and driving state.'}]
        elif meaning[:2] == ['condition', 'skill_multiplier']:
            predicate = (sources.READ_MAXIMUM if meaning[2] == 'full_reading_progress' else
                         'Reading progress yields a multiplier above the current one, and the reader is within this book\'s supported training level range.')
            matched = [f for f in candidates if f['payload'] == {'predicate': predicate}]
        elif meaning == ['condition', 'blood_cleaning', 'bleach_and_tool']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.BLOOD_CLEANING}]
        elif meaning == ['consumption_property', 'blood_cleaning', 'bleach_used']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.BLOOD_CLEANING}]
        elif meaning[:2] == ['condition', 'body_drying'] and meaning[2] in {'wet_body', 'uses_remaining'}:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.BODY_DRYING}]
        elif meaning == ['condition', 'ash_clearing', 'unbroken_broom'] and item == 'Base.Broom':
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.ASH_CLEARING}]
        elif item in {'Base.Dirtbag', 'Base.Gravelbag', 'Base.Sandbag'} and meaning in (
                ['role_unspecified_context', 'material'], ['consumption_property', 'consumable'], ['material_form', 'bag_of_dirt']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.GROUND_POUR}]
        elif (item in sources.PETROL_ITEMS | {'Base.Charcoal', 'Base.PropaneTank'} and meaning in (
                ['role_unspecified_context', 'material'], ['consumption_property', 'consumable'])):
            predicates = ({sources.VEHICLE_CONTAINER, sources.GENERATOR_REFUEL, sources.HEARTH_PETROL, sources.INDUSTRIAL_PETROL}
                if item in sources.PETROL_ITEMS else {sources.HEARTH_FUEL, sources.FURNACE_FUEL} if item == 'Base.Charcoal'
                else {sources.PROPANE_BARBECUE})
            matched = [f for f in candidates if f['payload'].get('predicate') in predicates]
        elif item == 'Base.FishingNet' and (meaning[:2] == ['condition', 'net_fishing']
                or meaning == ['hazard', 'net_breakage_after_time']):
            predicate = sources.NET_PLACEMENT if meaning[-1] in {'water', 'near_water'} else sources.NET_CHECKING
            matched = [f for f in candidates if f['payload'] == {'predicate': predicate}]
        elif item == 'Base.TrapStick' and meaning in (['condition', 'trapping', 'bait'], ['target_scope', 'trapping', 'birds']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.TRAP_BIRD}]
        elif item in {'Base.Jack', 'Base.LugWrench'} and meaning[0] == 'role' and meaning[1] in {'vehicle_tire_exchange', 'vehicle_brake_exchange'}:
            matched = [f for f in candidates if f['payload'] == {'function': 'service_vehicle_parts'}]
        elif item in {'Base.BucketPlasterFull', 'Base.CompostBag', 'Base.Fertilizer'} and meaning == ['consumption_property', 'consumable']:
            predicates = {sources.PLASTER_USE} if item == 'Base.BucketPlasterFull' else {sources.FERTILIZING}
            matched = [f for f in candidates if f['payload'].get('predicate') in predicates]
        elif meaning == ['consumption_property', 'consumable']:
            matched = [f for f in candidates if f['payload'].get('predicate') in {sources.DISINFECTION_USE, sources.BANDAGE_APPLICATION, sources.DIRTY_BANDAGING, sources.SPRAY_TREATMENT, sources.WATER_DRINKING}]
        elif meaning[:2] in (['condition', 'crop_spray'], ['constraint', 'crop_spray']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.SPRAY_TREATMENT}]
        elif meaning == ['role', 'crop_spray_preparation', 'material']:
            matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'material'}
                       and facts[f['context_ref']]['payload'] == {'activity': 'crop_spray_preparation'}]
        elif meaning == ['condition', 'bandaging', 'injured_unbandaged_health_menu']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.BANDAGE_APPLICATION}]
        elif meaning == ['state_label', 'dirty_bandaging_material']:
            matched = [f for f in candidates if f['payload'] == {'property': 'applied_bandage_life', 'direction': 'set_zero'}]
        elif meaning[:2] == ['condition', 'disinfection'] and meaning[2] in {'unbandaged', 'injured', 'health_panel_selection'}:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.DISINFECTION}]
        elif meaning[:2] == ['condition', 'splinting'] and meaning[2] in {'fracture', 'not_splinted', 'not_stitched', 'head_torso_excluded'}:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.SPLINTING}]
        elif meaning[0] in {'eligible_animal', 'bait_example', 'animal_time'}:
            predicates = set()
            if meaning[0] == 'eligible_animal':
                predicates = {'rabbit': {sources.TRAP_RABBIT_SQUIRREL}, 'squirrel': {sources.TRAP_RABBIT_SQUIRREL},
                              'bird': {sources.TRAP_BIRD}, 'mouse_or_rat': {sources.TRAP_RODENTS}}.get(meaning[1], set())
            elif meaning[0] == 'bait_example':
                predicates = {'apple': {sources.TRAP_RABBIT_SQUIRREL}, 'corn': {sources.TRAP_RABBIT_SQUIRREL, sources.TRAP_BIRD},
                              'worm': {sources.TRAP_BIRD}, 'bread': {sources.TRAP_BIRD},
                              'cheese': {sources.TRAP_RODENTS}, 'peanut_butter': {sources.TRAP_RODENTS}}.get(meaning[1], set())
            elif meaning[1] in {'rabbit', 'squirrel'} and meaning[2] == 'night':
                predicates = {sources.TRAP_RABBIT_SQUIRREL}
            matched = [f for f in candidates if f['payload'].get('predicate') in predicates]
        elif meaning == ['condition', 'animal_trapping', 'no_time_limit']:
            matched = [f for f in candidates if f['payload'].get('predicate') in {sources.TRAP_BIRD, sources.TRAP_RODENTS}]
        elif meaning[:2] == ['condition', 'animal_trapping'] and meaning[2] in {'bait', 'accepted_bait', 'zone', 'bait_freshness', 'player_proximity'}:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.TRAP_CATCH}]
        elif meaning[:2] == ['condition', 'fertilizing'] and meaning[2] in {'living_crop', 'farming_menu'}:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FERTILIZING}]
        elif meaning == ['condition', 'crop_rot', 'excess_fertilizer']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FERTILIZER_ROT}]
        elif meaning == ['condition', 'fertilizing_outcome', 'previous_applications']:
            matched = [f for f in candidates if f['payload'].get('predicate') in {sources.FERTILIZER_GROWTH, sources.FERTILIZER_ROT}]
        elif meaning == ['condition', 'rod_fishing', 'lure_examples']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FISHING_LURES}]
        elif meaning in (['condition', 'rod_fishing', 'baitfish_pike'], ['condition', 'rod_fishing', 'artificial_species'],
                         ['constraint', 'rod_fishing', 'artificial_excludes_pike_baitfish']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FISHING_MATCHES}]
        elif ((meaning[:2] == ['condition', 'rod_fishing'] and meaning[2] in {
                'unbroken_rod', 'rod_and_bait_carried', 'carried_with_rod', 'water_fishing_menu', 'bait_attached'})
              or (meaning[:2] == ['condition', 'fishing_outcome'] and meaning[2] in {'lure_type', 'time', 'season'})
              or meaning == ['constraint', 'fishing_outcome', 'catch_not_guaranteed']):
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.ROD_FISHING}]
        elif meaning == ['consumption_property', 'fishing_lure', 'may_be_spent_or_lost']:
            matched = [f for f in candidates if f['payload'] == {'predicate': sources.FISHING_LURE_LOSS}]
        elif meaning == ['condition', 'note_writing', 'writing_implement']:
            from . import recovery
            matched = [f for f in candidates if f['payload'] == {'predicate': recovery.NOTE_EDIT}]
        alias_note = None
        if not matched:
            role_aliases = {
                ('Base.CandyPackage', ('function', 'unpack_food')): {('package_opening', 'material')},
                ('Base.MeatCleaver', ('function', 'cut_food')): {('food_portioning', 'tool'), ('fish_preparation', 'tool')},
                ('Base.MeatCleaver', ('function', 'butcher_small_animals')): {('animal_butchery', 'tool')},
                ('Base.Watermelon', ('function', 'slice_fruit')): {('food_portioning', 'ingredient')},
                ('Base.Watermelon', ('function', 'smash_fruit')): {('watermelon_breaking', 'ingredient')},
                ('Base.Watermelon', ('output_purpose', 'portions_for_eating')): {('food_portioning', 'ingredient')},
                ('Base.Muffintray_Biscuit', ('function', 'portion_biscuits')): {('food_portioning', 'ingredient')},
                ('Base.Muffintray_Biscuit', ('role', 'biscuit_preparation', 'base')): {('food_portioning', 'ingredient')},
                ('Base.Handle', ('function', 'fit_tool_parts')): {('metal_forging', 'material'), ('shovel_smithing', 'material')},
                ('Base.Handle', ('function', 'shape_tool_parts')): {('metal_forging', 'material'), ('shovel_smithing', 'material')},
                ('Base.Handle', ('context', 'construction_or_crafting')): {('metal_forging', 'material'), ('shovel_smithing', 'material')},
                ('Base.Frog', ('role', 'food_preparation', 'ingredient')): {('frog_preparation', 'material')},
                ('Base.BakingPan', ('role', 'food_preparation', 'tool')): {('food_preparation', 'container')},
                ('Base.BakingTray', ('role', 'food_preparation', 'tool')): {('cookie_preparation', 'container')},
                ('Base.Coffee2', ('function', 'add_food_ingredients')): {('food_preparation', 'ingredient')},
                ('Base.Coffee2', ('role', 'coffee_preparation', 'ingredient')): {('food_preparation', 'ingredient')},
                ('Base.Teabag2', ('role', 'tea_preparation', 'ingredient')): {('food_preparation', 'ingredient')},
                ('Base.RoastingPan', ('role', 'roasting_preparation', 'base')): {('food_ingredient_addition', 'base')},
                ('Base.GridlePan', ('role', 'stir_fry_preparation', 'base')): {('food_ingredient_addition', 'base')},
                ('Base.Pan', ('role', 'stir_fry_preparation', 'base')): {('food_ingredient_addition', 'base')},
                ('Base.TinOpener', ('role', 'package_opening', 'tool')): {('package_opening', 'tool')},
                ('Base.TreeBranch', ('role', 'spear_crafting', 'material')): {('spear_crafting', 'material')},
                ('Base.SharpedStone', ('role', 'spear_crafting', 'tool')): {('spear_crafting', 'tool')},
                ('Base.Scotchtape', ('role', 'repair', 'repair_material')): {('repair', 'repair_material')},
                ('Base.ScrapMetal', ('role', 'metal_welding_construction', 'material')): {('metal_welding_construction', 'material')},
                ('Base.ScrapMetal', ('role', 'metalworking', 'material')): {('metal_welding_construction', 'material')},
                ('Base.MetalPipe', ('role', 'metalworking', 'material')): {('welded_parts', 'material'), ('metal_welding_construction', 'material')},
                ('Base.Nails', ('role', 'construction', 'material')): {('carpentry_menu_construction', 'material')},
                ('Base.Nails', ('role', 'crafting', 'material')): {('woodworking', 'material'), ('furniture_crafting', 'material'), ('trap_crafting', 'material')},
                ('Base.Rope', ('role', 'binding_crafting', 'material')): {('log_binding', 'material')},
                ('Base.Rope', ('role', 'connecting_crafting', 'material')): {('carpentry_menu_construction', 'material')},
                ('Base.Plank', ('role_unspecified_context', 'crafting_material')): {('woodworking', 'material'), ('construction', 'material')},
            }
            role_aliases.update({
                ('Base.FishingLine', ('identity_label', '낚시 소모품')): {('fishing_gear_crafting', 'material')},
                ('Base.Hairspray', ('identity_label', '폭발물 재료')): {('explosive_assembly', 'material')},
                ('Base.WaterBottleEmpty', ('identity_label', '폭발물 재료')): {('explosive_assembly', 'material')},
                ('Base.SharpedStone', ('identity_label', '석기 제작 도구')): {('tool_crafting', 'material')},
            })
            for trap_item in ('Base.BakingTray_Muffin', 'Base.BakingTray_Muffin_Recipe'):
                role_aliases[trap_item, ('function', 'remove_portioned_muffins')] = {('food_portioning', 'ingredient')}
            for tool_item in ('Base.Hammer', 'Base.HammerStone', 'Base.BallPeenHammer'):
                role_aliases[tool_item, ('condition', 'carpentry_menu_construction' if tool_item != 'Base.BallPeenHammer' else 'construction', 'nailed_structure' if tool_item != 'Base.BallPeenHammer' else 'wooden_structure_with_nails')] = {('construction', 'tool')}
                role_aliases[tool_item, ('role', 'carpentry_menu_construction' if tool_item != 'Base.BallPeenHammer' else 'construction', 'tool')] = {('construction', 'tool')}
            for tool_item in ('Base.BlowTorch', 'Base.WeldingMask'):
                role_aliases[tool_item, ('role', 'metalworking', 'tool')] = {('metal_welding_construction', 'tool')}
            for line_item in ('Base.FishingLine', 'Base.Paperclip'):
                for operation in ('fishing_rod_crafting', 'fishing_rod_repair'):
                    role_aliases[line_item, ('role', operation, 'material')] = {('fishing_gear_crafting', 'material')}
            selected_roles = role_aliases.get((item, tuple(meaning)), set())
            if selected_roles:
                matched = [f for f in candidates if f['fact_kind'] == 'context_role' and f['context_ref']
                    and (facts[f['context_ref']]['payload']['activity'], f['payload']['role']) in selected_roles]
                if item in {'Base.FishingLine', 'Base.Paperclip'}:
                    matched = [f for f in matched if has_recipe(f, {'Fix Fishing Rod'} if meaning[1] == 'fishing_rod_repair' else {'Make Fishing Rod'})]
                if matched:
                    alias_note = 'Reconcile the broad predecessor wording with this exact source-reviewed participation and its full attached eligibility/consumption conditions. A supplied ingredient/material, kept tool, vessel or transformation target retains that role; this does not infer a generic action, interchangeable role or guaranteed native result.'
            if not matched and item == 'Base.MetalBar' and meaning == ['role', 'metal_barricading', 'material']:
                matched = [f for f in candidates if f['payload'] == {'function': 'build_metal_barricade'}]
                alias_note = 'Metal-bar barricading consumes three bars and one torch use through its actual door/window path. It is distinct from welding-menu construction and does not require the welding-menu mask or learned recipes.'
            if not matched and item == 'Base.BucketPlasterFull' and meaning == ['role_unspecified_context', 'material']:
                matched = [f for f in candidates if f['payload'] == {'function': 'plaster_supported_structure'}]
                alias_note = 'Replace the unspecified material label with the exact plasterable-structure operation, its carpentry and approach conditions and one selected bucket use. This does not imply arbitrary construction, repair, painting or structural strengthening.'
            predicate_aliases = {
                ('Base.TinnedBeans', ('condition', 'bean_preparation', 'bowl')): sources.BEAN_PREPARATION,
                ('Base.Log', ('condition', 'log_sawing', 'saw')): sources.SAWN_WOOD,
                ('Base.Coffee2', ('condition', 'beverage_preparation', 'compatible_prepared_drink')): sources.COOKING_ACTION,
                ('Base.Paintbrush', ('condition', 'surface_painting', 'paint_and_compatible_surface')): sources.PAINT_ACTIONS,
                ('Base.BakingTray_Muffin', ('condition', 'remove_muffins', 'after_baking')): sources.MUFFIN_PORTIONING,
                ('Base.BakingTray_Muffin_Recipe', ('condition', 'remove_muffins', 'after_baking')): sources.MUFFIN_PORTIONING,
                ('Base.PlasterPowder', ('condition', 'plaster_preparation', 'water')): sources.PLASTER_MIXING,
                ('Base.CakeBatter', ('condition', 'cake_preparation', 'baking_pan')): sources.CAKE_PAN_PREPARATION,
                ('Base.PieDough', ('condition', 'pie_preparation', 'baking_pan')): sources.FOOD_ASSEMBLY,
            }
            predicate = predicate_aliases.get((item, tuple(meaning)))
            if not matched and predicate:
                matched = [f for f in candidates if f['payload'] == {'predicate': predicate}]
            if not matched and meaning == ['role', 'gardening', 'tool'] and item in {
                    'Base.GardenFork', 'Base.GardenHoe', 'Base.Shovel', 'Base.Shovel2', 'farming.HandShovel'}:
                matched = [f for f in candidates if f['payload'].get('function') in {'dig_furrow', 'remove_farm_plant'}]
                alias_note = 'Narrow gardening to the actual furrow/plant-removal operation and its target, tool, access and interruption predicates; the tool does not provide arbitrary gardening effects.'
            if not matched and item in {'Base.Bag_JanitorToolbox', 'Base.Bag_SurvivorBag'} and meaning == ['condition', 'carrying', 'worn_or_held']:
                matched = [f for f in candidates if f['payload'] == {'function': 'carry_stored_items'}]
                alias_note = 'Carrying requires inventory transfer/admission, not necessarily wearing or holding the container. Only the separately declared Back form supports back equipment. Preserve those distinct conditions instead of the predecessor universal worn-or-held restriction.'
            if not matched and item == 'Base.BlowTorch' and meaning == ['identity_label', '소모성 도구']:
                matched = [f for f in candidates if f['payload'] == {'predicate': sources.METAL_BARRICADE}]
                alias_note = 'The welding action spends torch uses; KeepOnDeplete retains the depleted tool. Replace an unscoped consumable-tool label with this actual consumption condition, not a claim that the entire torch disappears.'
            if not matched and item == 'Base.ShotgunShellsBox' and meaning == ['function', 'unpack_box_contents']:
                matched = [f for f in candidates if f['payload'] == {'function': 'unpack_ammunition'}]
            if not matched and item.startswith('Base.MakeUp_Lips') and meaning == ['function', 'apply_lip_makeup']:
                matched = [f for f in candidates if f['payload'] == {'function': 'wear_on_body'}]
                alias_note = 'This exact item is the registered Clothing makeup result, not the MakeUpType cosmetic supply that opens the makeup-selection UI. Retain its actual worn-slot behavior instead of claiming it applies another cosmetic; visible color remains separately unresolved.'
        if matched:
            refs = {f['ref'] for f in matched}
            for fact in matched:
                refs.update(fact['qualifier_refs'])
                if fact['context_ref']:
                    refs.add(fact['context_ref'])
            # Qualifier claims retain their actual parent behavior too.
            refs.update(r for f in matched for r in f['applies_to_refs'])
            pending = list(refs)
            while pending:
                fact = facts[pending.pop()]
                dependencies = set(fact['qualifier_refs']) | ({fact['context_ref']} if fact['context_ref'] else set())
                pending.extend(dependencies - refs)
                refs.update(dependencies)
            source_refs = sorted({p for r in refs for p in facts[r]['provenance_refs']})
            core_was_present = all((f['item_id'], f['fact_id']) in previous for f in matched)
            was_present = all((facts[r]['item_id'], facts[r]['fact_id']) in previous for r in refs)
            disposition = 'already_represented' if was_present else 'corrected' if core_was_present else 'recovered'
            narrowing = alias_note
            if alias_note:
                disposition = 'corrected'
            if item in sources.PETROL_ITEMS | sources.EMPTY_PETROL_ITEMS | {'Base.Charcoal', 'Base.PropaneTank', 'Base.Bellows'} and meaning[0] in {'function', 'role_unspecified_context', 'consumption_property'}:
                disposition = 'corrected'
                narrowing = 'Replace the broad fuel/material/carrying gloss with the exact represented target and operation. Vehicle transfer, pump replacement, generator refill, hearth fuel and industrial ignition have different guards and consumption rules; industrial petrol ignition does not consume either input. Native results and delivery remain separate.'
            if item in sources.DRAINABLE_MATERIALS and meaning in (
                    ['role_unspecified_context', 'material'], ['consumption_property', 'consumable']):
                disposition = 'corrected'
                narrowing = 'Replace the unscoped material/consumable assertion with its actual recipe, fixing or construction participation. Exact role conditions retain consumption and result boundaries; this is not an unconditional assertion that the carried item is used up or has a generic material effect.'
            if item == 'Base.Vinegar' and meaning == ['role', 'food_preparation', 'ingredient']:
                disposition = 'corrected'
                narrowing = 'Narrow the broad food-ingredient wording to the reviewed vegetable-jarring material role, with the exact recipe inputs and conditions. This does not make the Drainable vinegar a directly edible food or an arbitrary evolved-recipe ingredient.'
            if item == 'Base.DuctTape' and meaning == ['role', 'device_assembly', 'material']:
                disposition = 'corrected'
                narrowing = 'The specific role is attaching timer, sensor or trigger modifications to the reviewed explosive devices, not arbitrary electronic device assembly. Exact modification recipes and callbacks remain attached.'
            if item == 'Base.FishingNet' and meaning == ['function', 'catch_bait_fish']:
                disposition = 'corrected'
                narrowing = 'The checking action can return BaitFish through hourly random rolls. More than fifteen elapsed hours first permits net breakage; neither a catch nor survival of the net is guaranteed.'
            if meaning == ['function', 'fold_umbrella'] and item.startswith('Base.ClosedUmbrella'):
                disposition = 'corrected'
                narrowing = 'This exact closed umbrella is the input to opening, not folding. Replace the generic folding capability with its supported closed-to-open recipe, preserving condition copying and hand-placement constraints. Folding belongs to the distinct open form; rain protection remains independently unresolved.'
            if meaning == ['function', 'adjust_vehicle_tire_pressure'] and item == 'Base.TirePump':
                disposition = 'corrected'
                narrowing = 'The pump participates in inflation only. The deflation menu needs no pump. The retained inflation target, equipment, action validity and partial server requests do not promise arbitrary chosen pressure or rollback on cancellation.'
            if construction_claim and meaning[1] == 'hinged_structure_construction':
                disposition = 'corrected'
                narrowing = 'The open-ended hinged-structure wording is bounded to the active wooden-door and metal gate/locker/counter factories that declare this exact hinge material. Their carpentry or learned metal-welding requirements and consumption conditions remain attached; arbitrary hinged structures are not inferred from their names.'
            if item in sources.BROKEN_GLASS_ITEMS and meaning == ['caution', 'clearing_broken_glass']:
                disposition = 'corrected'
                narrowing = 'The general clearing warning is narrowed to the actual floor-glass pickup hand scratch and nested embedded-glass branches, with missing hands-slot clothing and random checks. Gloves do not gate menu admission, and neither window-frame removal nor approach/foot contact is substituted for pickup.'
            if furniture_gloss:
                disposition = 'corrected'
                narrowing = 'The layout/area-marking gloss is narrowed to the exact Moveable sprite placement and conditional pickup actions with their full space, parts, contents, tool/skill, reach, permission and breakage conditions. These actions do not establish an automatic marked area, an indoor-only restriction, or the installed appliance/storage/resting function; those require the actual placed-object properties. No unrelated world operation is completed by this comparison.'
            if item in {'Base.Plantain', 'Base.Comfrey'} and meaning == ['identity_label', '식품']:
                disposition = 'corrected'
                narrowing = 'The exact raw plant is declared Normal, not Food, and the inventory eating predicate does not select it. Replace the unsupported food label with its source-confirmed poultice ingredient role; consumption of a similarly named Food form is not inferred.'
            if item == 'Base.MakeupFoundation' and meaning == ['cosmetic_role', 'base_layer']:
                disposition = 'corrected'
                narrowing = 'Replace the unsupported base-layer claim with selection of the exact registered Foundation designs and its mirror exemption. Apply replaces the worn cosmetic and does not implement a base layer under other makeup or consume the foundation supply.'
            if meaning == ['function', 'reuse_container']:
                disposition = 'corrected'
                narrowing = 'The reuse claim is narrowed to the exact declared water-filling replacement and its admitted source/transfer/capacity conditions. It does not establish arbitrary reuse, guaranteed full filling or preservation of the old inventory identity.'
            if item in {'Base.Dirtbag', 'Base.Gravelbag', 'Base.Sandbag'} and meaning in (['role_unspecified_context', 'material'], ['consumption_property', 'consumable'], ['material_form', 'bag_of_dirt']):
                disposition = 'corrected'
                narrowing = 'The unspecified material/consumable or dirt-bag wording is narrowed to the exact bag selected for ground pouring, which calls Use after adding its matching floor and retains restoration metadata. Other construction and extinguishing roles remain separately represented; no generic ingredient role or guaranteed empty-form replacement is inferred.'
            if item == 'Base.Thread' and meaning in (['role_unspecified_context', 'material'], ['role', 'fabric_crafting', 'material'], ['consumption_property', 'consumable']):
                disposition = 'corrected'
                narrowing = 'The unspecified material/fabric-making/consumable wording is narrowed to the actual garment patching action, which requires Thread in inventory and calls its Use on completion. This does not establish arbitrary fabric manufacture or guaranteed empty-form removal; other crafting and wound-stitching scopes remain independent.'
            if item == 'Base.LeatherStrips' and meaning == ['material_form', 'leather_patch']:
                disposition = 'corrected'
                narrowing = 'The leather-patch phrase is represented by this exact LeatherStrips input selected for the guarded patching action. Native patch type/protection and full restoration are not inferred from its material name.'
            if meaning == ['function', 'sew_fabric'] and item == 'Base.Needle':
                disposition = 'corrected'
                narrowing = 'The generic sewing claim is narrowed to actual garment patching/padding with a fabric, thread and the represented garment/part prerequisites. Arbitrary fabric construction is not inferred from the needle name.'
            if item in {'Base.Soap2', 'Base.CleaningLiquid2'} and meaning[0] in {'function', 'effect'}:
                disposition = 'corrected'
                narrowing = 'The cleanser claim is expressed as participation in actual water-based body/equipment washing. Soap is used for blood, not dirt alone, and insufficient soap changes calculated time rather than preventing washing. Partial body coverage, clothing wetness and makeup removal remain explicit; this does not claim wound treatment or that soap alone causes the cleaning.'
            if meaning == ['intended_use', 'navigation_planning']:
                disposition = 'corrected'
                narrowing = 'The human navigation-planning gloss is narrowed to the actual map viewer with pan/zoom/reset and its inventory/initialization conditions. The source supplies no automatic route planner, route safety or content-accuracy guarantee; these are not implied by viewing the map.'
            if meaning == ['context_label', 'medical_use']:
                disposition = 'corrected'
                narrowing = 'The broad medical-use category is represented by the exact admitted bandage application or wound-disinfection action and its conditions; other medical uses are not inferred.'
            if meaning == ['state_label', 'dirty_bandaging_material']:
                disposition = 'corrected'
                narrowing = 'The exact Dirty type-name branch applies a bandage with zero bandage life. This is the supported dirty-bandage meaning; the separate infected-item flag and wound infection are not inferred from the label.'
            if meaning == ['identity_label', '손상 낚싯대']:
                disposition = 'corrected'
                narrowing = 'The exact declaration names a rod without line, and the two source-reviewed repairs use it as that input form. Replace the ambiguous damaged-rod label with this line-repair meaning; weapon ConditionMax=3 is not a declaration of zero current condition.'
            if meaning == ['effect', 'fishing_lure', 'may_break']:
                disposition = 'corrected'
                narrowing = 'Replace physical breakage wording with the observed lure Use/hand clearing and line-break inventory removal paths. Artificial tackle is not immune to loss, but these paths do not establish a decrease in its durability condition.'
            if meaning == ['function', 'read_or_consult']:
                disposition = 'corrected'
                narrowing = 'The broad read-or-consult statement is narrowed to the supplied literature reading action and its accepted conditions; no independent consultation function is inferred.'
            if meaning[0] == 'effect' and meaning[1:] in (['skill_knowledge', 'gain'], ['recipe_knowledge', 'gain']):
                disposition = 'corrected'
                narrowing = 'This exact registered skill book has no declared taught recipes. ISReadABook updates a conditional skill XP multiplier and skips the non-skill ReadLiterature call. Replace the generic skill/recipe-knowledge wording with that multiplier effect; direct skill-level gain and recipe learning are not represented.'
            if meaning[0] == 'function' and meaning[1] in {'write_documents', 'revise_documents'}:
                disposition = 'corrected'
                narrowing = 'The broad predecessor document-writing/editing use is narrowed to writable-note pages and titles. The exact implement-tag predicate and journal setters support this scope; arbitrary documents and paper organization are not admitted.'
            elif item in sources.STRAP_SPEED and meaning[0] in {'effect', 'condition'} and meaning[1] == 'reload_speed':
                disposition = 'corrected'
                narrowing = 'The consumer matches the primary-hand ammo type against Base.ShotgunShells, not a firearm model class. Replace the broad faster-reload wording with the represented conditional 1.15 multiplication of ReloadSpeed. Exact action duration and unrelated weapon handling are not inferred; the worn strap form and other speed factors remain explicit.'
            elif item in base.get('vehicle_panel_sources', {}) and meaning[0] == 'function' and meaning[1].startswith(('remove_vehicle_', 'install_vehicle_', 'refit_vehicle_')):
                disposition = 'corrected'
                narrowing = 'The panel/glass exchange is represented for this exact part form with runtime FullType compatibility, actual tool/access predicates and server success/failure conditions. The template token and VehicleType suffix are retained as leads, not silently expanded into compatibility. The predecessor unconditional wording is narrowed to this supported conditional operation.'
            elif meaning[0] == 'role' and meaning[1:] in (['fire_starting', 'tinder'], ['burning', 'fuel']):
                disposition = 'corrected'
                narrowing = 'The broad predecessor tinder/fuel use is narrowed to the exact registered campfire route and its selection, inventory, consumption and server-state conditions. Other fire or heating systems are not represented by this match.'
            elif meaning == ['condition', 'animal_trapping', 'player_proximity']:
                disposition = 'corrected'
                narrowing = 'The predecessor proximity wording is replaced with the actual checkForAnimal guard: a loaded trap square skips catching. No fixed player radius or equivalence between distance and square loading is inferred.'
            elif meaning == ['constraint', 'rod_fishing', 'artificial_excludes_pike_baitfish']:
                disposition = 'corrected'
                narrowing = 'The exclusion is bounded to the supplied fish/lure table and actual lure-matching consumer. It does not exclude future runtime registry additions or guarantee a catch of other species.'
            elif meaning == ['role', 'food_preparation', 'ingredient'] and any(f['payload'] == {'function': 'prepare_opened_food_ingredient'} for f in matched):
                disposition = 'corrected'
                narrowing = 'The broad ingredient claim is narrowed to the exact food contents after the supported package-opening transformation. The unopened package is not an ingredient; opening and the resulting food eligibility are both represented.'
            claim.update(candidate_successor_fact_refs=sorted(refs), verified_source_refs=source_refs,
                         migration_disposition=disposition,
                         reason=narrowing or ('The core proposition survives with corrected source-admitted qualifiers; dependent references use their new semantic identities.' if disposition == 'corrected' else
                                 'The reviewed proposition matches the source-admitted payload and its context/qualifiers; the predecessor text is not the admission evidence.'),
                         remaining_uncertainty=None, remaining_work=None,
                         source_binding='source_bound', source_strength='consumer_confirmed', review_state='reviewed')
            locales = {}
            for locale in ('ko', 'en'):
                rendered = items[item]['locales'][locale]
                expanded = sorted({e for r in refs for e in rendered['fact_expressions'].get(r, [])})
                missing = refs - set(rendered['expanded_represented_fact_refs'])
                compact = refs & set(rendered['s2']['represented_fact_refs'])
                detail_reasons = [d['reason'] for d in rendered['s2'].get('detail_fact_omissions', [])
                                  if d['fact_ref'] in refs - compact]
                locales[locale] = {'expanded_outcome': 'expression_failure' if missing or not expanded else 'represented',
                                   'expanded_refs': expanded, 'compact_fact_refs': sorted(compact),
                                   'compact_outcome': 'represented' if compact == refs else 'detail_omission',
                                   'compact_omitted_fact_refs': sorted(refs - compact),
                                   'compact_omission_reason': None if compact == refs else
                                   ' '.join(detail_reasons) if detail_reasons else
                                   'The omitted references remain accessible in expanded as ordinary execution/detail qualifiers or facts outside first-contact selection; they do not remove the expressed functional context or its meaning-changing scope.'}
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'],
                                 'migration_disposition': claim['migration_disposition'], 'successor_fact_refs': sorted(refs),
                                 'locales': locales, 'residual': None,
                                 'conservation_status': 'conserved' if all(v['expanded_outcome'] == 'represented' for v in locales.values()) else 'expression_failure'})
            continue
        if meaning in (['function', 'receive_radio_signal'], ['function', 'transmit_radio_signal'], ['function', 'receive_tv_signal'],
                       ['function', 'play_recorded_media'], ['function', 'play_vhs'], ['function', 'play_cd_recording'],
                       ['condition', 'media_playback', 'compatible_player'], ['condition', 'recorded_media_playback', 'compatible_device']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            radio = fields.get('Type') == 'Radio' and not {'Type', 'TwoWay', 'IsTelevision', 'NoTransmit', 'AcceptMediaType'} & conflicts.keys()
            media = any(f['payload'] == {'function': 'insert_recorded_media'} for f in candidates)
            signal = radio and (
                (meaning == ['function', 'receive_radio_signal'] and fields.get('IsTelevision', '').lower() == 'false' and fields.get('NoTransmit', '').lower() != 'true')
                or (meaning == ['function', 'transmit_radio_signal'] and fields.get('TwoWay', '').lower() == 'true')
                or (meaning == ['function', 'receive_tv_signal'] and fields.get('IsTelevision', '').lower() == 'true'))
            playback = (media and meaning in (['function', 'play_recorded_media'], ['condition', 'media_playback', 'compatible_player'],
                                               ['condition', 'recorded_media_playback', 'compatible_device'])) or (
                radio and ((meaning == ['function', 'play_vhs'] and fields.get('IsTelevision', '').lower() == 'true' and fields.get('AcceptMediaType') == '1')
                           or (meaning == ['function', 'play_cd_recording'] and fields.get('AcceptMediaType') == '0')))
            if signal or playback:
                partial = [f['ref'] for f in candidates if f['payload'].get('function') in {
                    'open_device_controls', 'tune_radio', 'select_tv_channel', 'adjust_device_volume', 'toggle_radio_microphone',
                    'read_recorded_media_label', 'insert_recorded_media', 'control_device_media', 'edit_radio_presets'}]
                paths = [records[0]['path'], sources.RADIO_WINDOW, sources.RADIO_ACTION,
                         *( (sources.RADIO_SIGNAL, sources.RADIO_MIC, sources.RADIO_INTERACTIONS) if signal else
                            (sources.RADIO_MEDIA, sources.MEDIA_LOADER, sources.MEDIA_DATA, sources.CONTEXT_MEDIA, sources.RADIO_INTERACTIONS) )]
                uncertainty = {'meaning': meaning, 'examined': {
                    'fields': {k: fields.get(k) for k in ('Type', 'TwoWay', 'IsTelevision', 'NoTransmit', 'AcceptMediaType', 'MediaCategory')},
                    'control_fact_refs': partial,
                    'delivered_code_consumer': sources.RADIO_CODE_EFFECTS,
                    'boundary': ('Signal display reads native isReceivingSignal and interaction code receives delivered OnDeviceText. Channel/microphone setters do not implement signal transport.' if signal else
                                 'Media insertion checks recorded state and matching media type. TogglePlayMedia requires on/hasMedia and calls native StartPlayMedia/StopPlayMedia; the category loader registers records without assigning one to this item.')},
                    'required_input': ('Native device signal propagation, microphone pickup and receiver delivery for this declared subtype' if signal else
                                       'Native RecordedMedia assignment/type mapping and DeviceData playback/output for this exact media or accepting device'),
                    'reason': ('The exact declared device branch and local control consumers have been examined. A control setting or received-state display does not establish the actual claimed signal path; missing propagation/delivery implementation remains.' if signal else
                               'Conditional label/insertion or device controls are represented. The exact recording assignment and native executor still determine playable content and output; compatibility for insertion alone does not prove the complete playback claim.')}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                             verified_source_refs=[base['reader'].bindings[p] for p in paths], reason=uncertainty['reason'],
                             remaining_uncertainty=uncertainty, remaining_work=None, source_binding='source_bound',
                             source_strength='declared_device_and_exact_media_signal_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if meaning in (['function', 'check_time'], ['function', 'listen_through_radio_headphones']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            clock = meaning[1] == 'check_time' and fields.get('Type') in {'AlarmClock', 'AlarmClockClothing'} and 'Type' not in conflicts
            headphone = meaning[1] == 'listen_through_radio_headphones' and item in {'Base.Headphones', 'Base.Earbuds'} and len(records) == 1
            if clock or headphone:
                if clock:
                    paths = [records[0]['path'], semantic.MENU, sources.ALARM_DIALOG,
                             'lua/client/ISUI/ISButtonPrompt.lua', 'lua/client/XpSystem/ISUI/ISCharacterScreen.lua']
                    examined = {'declaration': fields,
                        'menu': 'AlarmClock/AlarmClockClothing collection only reaches set/stop-alarm options when isDigital is true.',
                        'display': 'ButtonPrompt reads the native UIManager clock visibility and dimensions. CharacterScreen gates survival-time display on its isDateVisible result. Neither Lua consumer identifies which held/worn clock enables the time display.'}
                    dependency = 'UIManager Clock visibility/time-display selection and exact AlarmClock or AlarmClockClothing instance binding'
                    reason = 'The local alarm operations and native-clock UI consumers are examined separately. Setting an alarm does not prove time-display eligibility for this exact item; the item-to-clock-display selection is not supplied by those Lua consumers.'
                    partial = [f['ref'] for f in candidates if f['payload'].get('function') in {'set_alarm', 'stop_alarm'}]
                else:
                    paths = [records[0]['path'], sources.RADIO_VOLUME, sources.RADIO_PANEL, sources.RADIO_WINDOW, sources.RADIO_ACTION]
                    examined = {'declaration': fields, 'connection': 'RWMVolume verifies exact headphone FullTypes; ISRadioAction passes a selected item to DeviceData.addHeadphones for an empty slot.',
                                'playback': 'The Lua volume controls read device power and set volume; they do not define headphone audio routing or audible output.'}
                    dependency = 'DeviceData headphone binding and native radio audio routing/playback for the connected device'
                    reason = 'The connection action is represented. The actual selected device audio path, power/reception and headphone playback remain native state and cannot be inferred from the connection request.'
                    partial = [f['ref'] for f in candidates if f['payload'] == {'function': 'connect_radio_headphones'}]
                for path in paths:
                    base['reader'].read(path)
                uncertainty = {'meaning': meaning, 'examined': examined, 'required_input': dependency, 'reason': reason}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                             verified_source_refs=[base['reader'].bindings[p] for p in paths], reason=reason,
                             remaining_uncertainty=uncertainty, remaining_work=None, source_binding='source_bound',
                             source_strength='exact_display_or_audio_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if meaning == ['function', 'shove']:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Weapon' and 'Type' not in conflicts:
                uncertainty = {'meaning': meaning,
                    'examined': {'declaration': fields, 'consumer': sources.FIREARM,
                                'branch': 'attackHook sends isDoShove through the non-shooting DoAttack path, including its vehicle exception.'},
                    'required_input': 'DoAttack/isDoShove interpretation identifying the selected weapon contribution to a shove',
                    'reason': 'The Lua branch dispatches a character-controlled shove but does not establish whether or how this exact weapon contributes to it. Ordinary weapon attack facts remain separate; neither intrinsic shove use nor absence of such use is inferred.'}
                evidence = [base['reader'].bindings[records[0]['path']], base['reader'].bindings[sources.FIREARM]]
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='character_weapon_dispatch_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if meaning in (['function', 'trigger_linked_device'], ['condition', 'remote_trigger', 'compatible_linked_device']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('RemoteController', '').lower() == 'true' and 'RemoteController' not in conflicts:
                partial = [f['ref'] for f in candidates if f['payload'].get('function') in {'link_remote_device', 'send_remote_trigger'}]
                if partial:
                    evidence = [base['reader'].bindings[p] for p in (records[0]['path'], semantic.MENU, sources.OBJECT_COMMANDS)]
                    uncertainty = {'meaning': meaning, 'examined': {'declaration': fields,
                        'linking': 'OnLinkRemoteController assigns an absent controller ID and copies it to the selected compatible item.',
                        'triggering': 'The active OnTriggerRemoteController sends object/triggerRemote with ID/range; Commands.object.triggerRemote passes both to IsoTrap.triggerRemote.',
                        'partial_fact_refs': partial},
                        'required_input': 'IsoTrap.triggerRemote matching, range and actual trap-effect interpretation',
                        'reason': 'ID assignment and request transmission are represented. The actual receiver delegates finding and triggering a matching placed trap to IsoTrap; neither an assigned ID nor its request proves that the linked device actually operates.'}
                    claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                                 verified_source_refs=evidence, reason=uncertainty['reason'], remaining_uncertainty=uncertainty,
                                 remaining_work=None, source_binding='source_bound', source_strength='exact_native_trap_handoff', review_state='reviewed')
                    conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                         'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty,
                                         'conservation_status': 'bounded_unresolved'})
                    continue
        if meaning[0] == 'effect' and meaning[1] in {'vehicle_traction', 'vehicle_engine_noise', 'vehicle_braking'}:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            field, template = {'vehicle_traction': ('WheelFriction', 'tire'),
                               'vehicle_engine_noise': ('EngineLoudness', 'muffler'),
                               'vehicle_braking': ('brakeForce', 'brake')}[meaning[1]]
            if fields.get('MechanicsItem', '').lower() == 'true' and field in fields and field not in conflicts:
                paths = [records[0]['path'], 'scripts/vehicles/template_' + template + '.txt',
                         'lua/client/Vehicles/ISUI/ISVehicleMechanics.lua',
                         'lua/client/Vehicles/ISUI/ISVehiclePartMenu.lua',
                         'lua/client/Vehicles/TimedActions/ISInstallVehiclePart.lua',
                         'lua/server/Vehicles/VehicleCommands.lua', 'lua/server/Vehicles/Vehicles.lua']
                for path in paths:
                    base['reader'].read(path)
                evidence = [base['reader'].bindings[p] for p in paths]
                uncertainty = {'meaning': meaning,
                    'examined': {'declaration': fields, 'template': paths[1],
                                'selection': 'ISVehicleMechanics matches runtime part:getItemType to exact FullType inventory entries with positive condition.',
                                'installation': 'The normal action transfers the item and sends vehicle/installPart. Its actual server handler conditionally sets the part inventory item; failure can damage or return it.',
                                'effect_boundary': 'The mechanical display reads part values. The supplied update callback handles condition loss or tire air/removal; it does not define how this declared stat changes traction or engine sound.'},
                    'required_input': 'VehicleScript itemType/VehicleType binding and VehiclePart/BaseVehicle interpretation of ' + field,
                    'reason': 'The exact mechanical field and actual client-to-server installation path have been examined. Neither the template token nor the mechanical UI number establishes the claimed vehicle effect; runtime type expansion and engine stat application remain unverified.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='vehicle_type_and_engine_boundary', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if meaning[0] == 'effect' and meaning[1] in {'recipe_knowledge', 'makeshift_radio_recipe_knowledge'}:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if (fields.get('Type') == 'Literature' and fields.get('TeachedRecipes') and not fields.get('SkillTrained')
                    and fields.get('CanBeWrite', '').lower() != 'true' and not {'Type', 'TeachedRecipes', 'SkillTrained', 'CanBeWrite'} & conflicts.keys()
                    and (len(meaning) == 3 or (meaning[3] in LEARNING_TOPICS
                         and set(LEARNING_TOPICS[meaning[3]]) <= set(fields['TeachedRecipes'].split(';'))))):
                partial = [f['ref'] for f in candidates if f['payload'] == {'function': 'read_literature'}]
                evidence = [base['reader'].bindings[p] for p in (records[0]['path'], semantic.MENU, semantic.READ)]
                uncertainty = {'meaning': meaning, 'examined': {'teached_recipes': fields['TeachedRecipes'],
                    'claimed_topic_entries': list(LEARNING_TOPICS[meaning[3]]) if len(meaning) > 3 else fields['TeachedRecipes'].split(';'),
                    'reading_path': 'ISReadABook.perform adds the FullType to alreadyReadBook for nonempty TeachedRecipes, then calls character:ReadLiterature for this nonskill book.',
                    'excluded_code': 'The explicit getKnownRecipes():add loop below is commented out.', 'partial_fact_refs': partial},
                    'required_input': 'IsoGameCharacter.ReadLiterature interpretation of TeachedRecipes and known-recipe mutation',
                    'reason': 'Reading the book is represented, and its exact recipe list is retained. The active Lua records a read-book identity but delegates learning to ReadLiterature; the commented known-recipe loop cannot establish recipe learning as an active Lua effect.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                             verified_source_refs=evidence, reason=uncertainty['reason'], remaining_uncertainty=uncertainty,
                             remaining_work=None, source_binding='source_bound', source_strength='exact_native_reading_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if item == 'Base.Coffee2' and meaning[0] in {'recipe_menu', 'recipe_relation'} and meaning[1] == 'coffee_preparation':
            records = base['declarations'][item]
            reason = 'Remove this exact coffee menu/recipe relation under the Layer 4 interaction responsibility. Coffee2 names the five HotDrink variants whose bases are water-filled mugs or teacup. The independently represented food-preparation ingredient role retains actual recipe acceptance and transfer/cooking/poisoning conditions; destination presence is not claimed.'
            claim.update(migration_disposition='responsibility_removed', reason=reason,
                verified_source_refs=[base['reader'].bindings[p] for p in (records[0]['path'], 'scripts/evolvedrecipes.txt', semantic.MENU, semantic.COOK, 'docs/ARCHITECTURE.md')],
                remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound', source_strength='responsibility_boundary', review_state='reviewed',
                owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': 'Layer 4 interaction information', 'destination_presence': 'not_claimed'})
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'responsibility_removed',
                'successor_fact_refs': [], 'locales': {}, 'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
            continue
        food_routes = [r for r in base.get('cooking_base_relations', {}).get(item, []) if r['field'] == 'ResultItem']
        food_route_claim = (meaning[0] == 'acquisition_process' and meaning[1] in {
            'boil_in_cup', 'boil_pasta', 'boil_rice', 'combine_ingredients', 'mix_ingredients',
            'put_food_or_ingredients_in_bowl_or_pot', 'pour_beer', 'pour_wine', 'pour_drink', 'cook_ingredients'}
            or meaning[0] in {'acquisition_container', 'preparation_form'}
            or meaning[0] == 'acquisition_material' and meaning[1] in {'water', 'ingredients'})
        if food_routes and food_route_claim:
            retain_boundary(claim, {semantic.MENU, semantic.COOK, *(r['path'] for r in food_routes)},
                {'exact_evolved_result_relations': food_routes, 'consumer': sources.COOKING_BASE},
                'Native evolved-recipe getItemsCanBeUse/addItem result identity, quantities and heating/state execution',
                'The exact base-to-result relation is source-bound and the ingredient-addition consumer is interpreted. Water-mug, tumbler, cup, wine glass and prepared-food bases remain distinct. A Cookable flag or Cooking category does not itself boil, bake or deliver the final food; the claimed result/form depends on native creation and state.')
            continue
        if meaning[0] == 'acquisition_process' and meaning[1] in {'cook_dough_or_ingredients', 'cook_ingredients'} and reviewed_results[item]:
            selected = list(reviewed_results[item].values())
            retain_boundary(claim, {semantic.CRAFT, semantic.GROUPS, *(p for r in selected for p in r['source_paths'])},
                {'reviewed_recipe_observation_refs': [r['observation_ref'] for r in selected]},
                'Native recipe result identity and any separate Food heating/cooking transition',
                'Actual preparation recipes for this exact result have been interpreted. For example scooping ice cream and coating/slicing ingredients do not execute heating merely because the predecessor says cooked. Their raw result and callback are retained without asserting a completed cooking outcome.')
            continue
        if meaning[0] in {'acquisition_place', 'acquisition_method'}:
            traced = {ref: t for token in (item, item.split('.', 1)[1]) for ref, t in loot_traces[token]}
            if not traced:
                paths = {r['path'] for r in base['acquisition']['source_bindings']
                    if r['path'].endswith(('Distributions.lua', 'ItemPicker.lua')) or '/Foraging/' in r['path']}
                paths.update(r['path'] for r in base['declarations'].get(item, []))
                for path in paths:
                    if path not in base['reader'].bindings:
                        base['reader'].read(path)
                retain_boundary(claim, paths, {'exact_fulltype': item, 'queried_tokens': [item, item.split('.', 1)[1]],
                    'loot_vehicle_connections': [], 'exact_declarations': base['declarations'].get(item, [])},
                    'An exact producer/alias and room/container/zone-to-place binding for the stated acquisition route',
                    'The bound loot/vehicle producer set has no connection for either exact or short token. Foraging registration and native selection are separate from similarly named wristwatches, jewelry or camping objects. No source supplied here corroborates this precise predecessor place/method; runtime impossibility is not asserted.')
                continue
        # Finite named residuals after positive fact/role reconciliation.
        records = base['declarations'].get(item, [])
        fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
        if item in {'Base.Bag_PistolCase', 'Base.Lemongrass', 'Base.NoiseMaker', 'Base.ShotgunCase1'} and len(records) != 1:
            paths = {r['path'] for r in records} or {r['path'] for r in base['semantic']['source_bindings'] if r['path'].startswith('scripts/')}
            retain_boundary(claim, paths, {'exact_fulltype': item, 'declarations': records},
                'An exact source declaration/alias binding' if not records else 'Native script loading and duplicate declaration precedence',
                'The complete bound item declarations have no exact definition for this predecessor identity.' if not records else
                'This exact FullType is declared twice. The declarations are retained independently; the historical model does not select a runtime winner. Similar or identical visible properties do not silently replace the required identity binding.')
            continue
        learning = {'generator_connection': 'Generator', 'generator_repair': 'Generator',
            'identify_poisonous_berries': 'Herbalist', 'identify_poisonous_mushrooms': 'Herbalist',
            'standard_vehicle_mechanics': 'Basic Mechanics', 'commercial_vehicle_mechanics': 'Intermediate Mechanics',
            'performance_vehicle_mechanics': 'Advanced Mechanics'}
        if meaning[0] == 'learning' and meaning[1] in learning and learning[meaning[1]] in fields.get('TeachedRecipes', '').split(';'):
            retain_boundary(claim, {records[0]['path'], semantic.READ, semantic.MENU, sources.WORLD_MENU, sources.VEHICLE_MENU},
                {'TeachedRecipes': fields['TeachedRecipes'], 'read_consumer': 'ISReadABook records alreadyReadBook, then calls native ReadLiterature; the explicit known-recipes loop is commented out.',
                 'selected_topic': learning[meaning[1]]},
                'Native ReadLiterature knowledge mutation and the exact learned-topic consumer',
                'The exact declared topic is bound to the actual reading branch. Generator menu gates and Herbalist poison labeling read known-recipe state; those checks do not implement the book granting it or guarantee every claimed repair/identification outcome.')
            continue
        food_thermal = fields.get('Type') == 'Food' and (
            meaning == ['function', 'bake_muffins'] or meaning == ['function', 'cook_rice_or_pasta']
            or meaning[0] == 'state_label' and meaning[1] in {'prepared_food', 'batter_filled_muffin_tray'})
        if food_thermal:
            retain_boundary(claim, {records[0]['path'], semantic.MENU, semantic.COOK, semantic.CRAFT, semantic.GROUPS},
                {'declaration': fields, 'evolved_relations': base.get('cooking_base_relations', {}).get(item, [])},
                'Native Food initialization/heating/cooking and RecipeManager result state',
                'The exact food declaration, ingredient-addition route and any independently represented portioning action are interpreted. IsCookable, times and a prepared-form name do not implement the claimed current cooked/batter state or guarantee successful baking. Portioning cooked food is separate from cooking it.')
            continue
        if (meaning[0] == 'output_identity' and item in base.get('package_opening_results', {})
                and (meaning[1] in {'ammunition', 'jarred_contents', 'vegetables'} or meaning == ['output_identity', 'food', 'tuna'])):
            routes = base['package_opening_results'][item]
            retain_boundary(claim, {semantic.CRAFT, semantic.GROUPS, *(r['path'] for r in routes)}, routes,
                'Native RecipeManager result identity/count and callback delivery',
                'The exact package-opening Result clauses identify the declared contents and their actual opening conditions. Native result creation remains separate; in particular the predecessor .556 label is not the source 5.56mm designation.')
            continue
        if meaning[0] == 'output_identity' and item in {'Base.CandyPackage', 'Base.Speaker', 'Base.HomeAlarm', 'Base.FishingNet'}:
            predicates = {'Base.CandyPackage': sources.CANDY_OPENING, 'Base.Speaker': sources.ELECTRONIC_SALVAGE,
                'Base.HomeAlarm': sources.ELECTRONIC_SALVAGE, 'Base.FishingNet': sources.NET_CHECKING}
            selected = [f for f in candidates if f['payload'] == {'predicate': predicates[item]}]
            if selected:
                paths = {observations[o]['source_path'] for f in selected
                    for p in semantic_facts[f['fact_id']]['provenance_refs'] for o in semantic_payload['provenance'][p]['observation_refs']}
                retain_boundary(claim, paths, {'actual_consumer': predicates[item]},
                    'Native result factory/count and conditional random inventory delivery',
                    'The exact opening, dismantling or net-checking source is interpreted. Candy declares five lollipops and its callback requests six mint candies; net checking is probabilistic. The source operation does not guarantee the claimed returned item delivery.')
                continue
        if item in {'Base.BucketConcreteFull', 'Base.ConcretePowder', 'Base.Screws', 'Base.Cornmeal', 'Base.IcePick', 'Base.Rake', 'Base.LeafRake'} and (
                meaning[0] in {'role', 'role_unspecified_context', 'context', 'consumption_property'}
                or item == 'Base.BucketConcreteFull' and meaning == ['acquisition_process', 'mix_ingredients']):
            paths = {records[0]['path'], semantic.MENU, semantic.CRAFT, semantic.GROUPS, semantic.BUILD, semantic.STAGE, semantic.MOVE, semantic.PROPS}
            retain_boundary(claim, paths, {'declaration': fields,
                'source_distinctions': 'ConcretePowder/BucketConcreteFull have no exact input/Result in the supplied recipes or active construction calls. Screws are breakage/salvage returns and box contents, not a demonstrated assembly/repair input. Cornmeal is the legacy Drainable, distinct from Food Cornflour. IcePick has weapon/spear-attachment use; Rake/LeafRake lack the gardening tags selected by the furrow menu.'},
                'An exact active input consumer for the separately claimed role or preparation',
                'The named role does not follow from display category, similarly named forms or output-only participation. Available exact consumers and independent roles were interpreted; the claim remains uncorroborated without asserting universal absence.')
            continue
        state_meaning = (meaning[0] in {'state', 'state_label'} and (
            meaning[1:] in (['container_contents', 'empty'], ['empty_container'], ['empty_reusable_container'], ['water_filled_container'])))
        if item == 'Base.BoxOfJars' and meaning == ['identity_label', '재료']:
            retain_boundary(claim, {records[0]['path'], semantic.MENU},
                {'declaration': records[0], 'conflicts': conflicts},
                'Native duplicate DisplayCategory assignment and category presentation',
                'The exact declaration assigns both Material and Cooking. Neither a declaration winner nor the predecessor material category is inferred. The separately represented opening operation remains intact; display-category ownership is not transferred into Layer 3.')
            continue
        empty_name = meaning[0] == 'identity_label' and meaning[1].startswith('빈 ')
        if records and len(records) == 1 and (state_meaning or empty_name):
            retain_boundary(claim, {records[0]['path'], semantic.MENU, sources.TAKE_WATER, sources.TRANSFER_WATER, sources.DUMP_CONTENTS},
                {'declaration': fields, 'represented_water_relation': base.get('water_container_sources', {}).get(item),
                 'emptying_relation': base.get('container_emptying_relations', {}).get(item)},
                'Native item factory, carried container contents and water/replacement initial state',
                'The exact empty or water form and its available filling/emptying paths were examined. A name or replacement target does not prove current contents, full quantity or general-purpose storage. Its separately represented water operation remains intact.')
            continue
        if item == 'Base.KeyRing' and meaning == ['storage_acceptance', 'keys'] and fields.get('OnlyAcceptCategory'):
            retain_boundary(claim, {records[0]['path'], semantic.TRANSFER, semantic.MENU},
                {'declaration': fields}, 'Native ItemContainer isItemAllowed and OnlyAcceptCategory interpretation',
                'The declaration supplies the Key category restriction and the transfer consumer delegates admission. The exact runtime category test remains separate from the represented storage/carrying operation.')
            continue
        if item.startswith('Base.Boilersuit') and meaning == ['visual_coverage', 'upper_and_lower_body']:
            retain_boundary(claim, {records[0]['path'], semantic.WEAR, sources.BODY_LOCATIONS}, {'declaration': fields},
                'Exact ClothingItem mesh/texture and native worn-body visual coverage',
                'The declared clothing and body slot are bound and wearing is represented. Slot identity or a garment name is not proof of its rendered upper/lower-body coverage.')
            continue
        if item in {'Base.Garter', 'Base.LongCoat_Bathrobe'} and meaning[0] == 'wear':
            retain_boundary(claim, {records[0]['path'], semantic.WEAR, sources.BODY_LOCATIONS}, {'declaration': fields},
                'A source-supported mapping from the exact body slot to the claimed underwear/outerwear layer',
                'The actual worn slot and its exclusivity are represented. The predecessor garment-layer term does not follow from that slot without the exact classification/visual binding.')
            continue
        if (item == 'Base.223Clip' and meaning == ['function', 'insert_matching_magazine']):
            retain_boundary(claim, {records[0]['path'], semantic.MENU, sources.FIREARM, sources.INSERT_MAGAZINE},
                {'declaration': fields, 'receiver': 'The VarmintRifle MagazineType=Base.223Clip line is commented out; active firearm declarations do not supply this exact magazine receiver.'},
                'An active compatible firearm MagazineType/native magazine binding for Base.223Clip',
                'Loading and unloading ammunition in this magazine are represented. A filled magazine does not by itself establish insertion into an active firearm, and the commented receiver is not an executable join.')
            continue
        if item in {'Base.FireWoodKit', 'Base.CompostBag', 'Base.Fertilizer', 'Base.Corkscrew'} and meaning in (
                ['context_label', 'camping'], ['context_label', 'gardening'], ['context_label', 'table_setting'], ['function', 'use_tableware']):
            reason = 'Remove this standalone activity/category or generic table-setting gloss under Layer 2 classification and the adopted general inventory-management exclusion. Exact preparation, fertilizing and recipe-tool participation remain separately accounted; no destination presence is claimed.'
            claim.update(migration_disposition='responsibility_removed', reason=reason,
                verified_source_refs=[base['reader'].bindings[records[0]['path']], base['reader'].bindings['docs/ARCHITECTURE.md']],
                remaining_work=None, remaining_uncertainty=None, source_binding='source_and_owner_bound', source_strength='responsibility_boundary', review_state='reviewed',
                owner_presence_evidence={'path': 'docs/ARCHITECTURE.md', 'section': 'Layer 2 category responsibility and P4 general inventory management', 'destination_presence': 'not_claimed'})
            conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'responsibility_removed',
                'successor_fact_refs': [], 'locales': {}, 'residual': None, 'removal_reason': reason, 'conservation_status': 'responsibility_removed'})
            continue
        if item in {'Base.Pot', 'Base.TinnedSoup', 'Base.CannedMushroomSoup'} and (
                meaning[0] == 'role' and meaning[1] == 'soup_preparation'
                or meaning[:2] == ['condition', 'soup_preparation']):
            retain_boundary(claim, {records[0]['path'], 'scripts/recipes.txt', 'scripts/evolvedrecipes.txt', semantic.CRAFT, semantic.GROUPS, semantic.COOK},
                {'legacy_source': 'All four Make Pot of Soup variants for opened/closed TinnedSoup and CannedMushroomSoup with Pot are inside the block comment at recipes.txt 195–243.',
                 'active_source': 'Opening cans is separate. Active Soup uses WaterPot as its evolved base and PotOfSoupRecipe as result.'},
                'An active exact canned-soup/Pot consumer for the claimed soup preparation',
                'The predecessor combination is present only in commented recipe text. It is not an active recipe or evidence that the closed can prepares soup. Opening and water-storage facts remain independently represented.')
            continue
        if item == 'Base.IronIngot' and meaning == ['role', 'metal_melting', 'material']:
            retain_boundary(claim, {records[0]['path'], sources.BLACKSMITH_MENU, semantic.CRAFT, semantic.GROUPS},
                {'menu': 'getMetal counts IronIngot drainable units for anvil construction, whose menu is disabled. Independent active smithing recipes consume ingot amounts; furnace lighting/fuel controls do not implement melting this carried ingot.'},
                'An exact active IronIngot melting consumer or native furnace input/execution binding',
                'The actual ingot forging and construction input routes were interpreted. Those roles cannot be renamed melting merely from a metal category or furnace presence.')
            continue
        if item == 'Base.Pipe' and meaning == ['negative_scope', 'crafting_use', 'Build 41']:
            retain_boundary(claim, {records[0]['path'], semantic.CRAFT, semantic.GROUPS, semantic.MOVE, semantic.PROPS},
                {'declaration': fields, 'identity': 'Normal Plastic Pipe, distinct from Weapon MetalPipe'},
                'Version-wide exact crafting/extension coverage sufficient for the stated negative',
                'The bound exact Plastic Pipe and supplied recipe/menu paths do not establish a universal no-crafting claim for all Build 41. The separate MetalPipe cannot be used as its alias.')
            continue
        if meaning[0] == 'identity_label' and item in {
                'Base.BrokenFishingNet', 'Base.LightBulbGreen', 'Base.CannedMushroomSoupOpen', 'Base.TinnedSoupOpen',
                'Base.Chainsaw', 'Base.UnusableWood', 'Base.UnusableMetal', 'Base.ShotgunSawnoff',
                'Base.DoubleBarrelShotgunSawnoff', 'Base.PickAxeHandleSpiked'} and len(records) == 1:
            retain_boundary(claim, {records[0]['path'], semantic.MENU, semantic.CRAFT, semantic.GROUPS},
                {'declaration': fields, 'claimed_name': meaning[1]},
                'Exact native item state/visual binding for the modifier in the predecessor name',
                'The declared form and its separately represented uses are retained. Broken/opened/sawn/spiked, green, powered and unusable wording is not expanded into guaranteed physical state, rendered color, engine operation or universal lack of utility merely from the display name.')
            continue
        legacy_food_routes = {'Base.BakingTrayBread', 'Base.Pancakes', 'Base.Toast', 'Base.Waffles',
            'Base.EggBoiled', 'Base.EggPoached', 'Base.GrilledCheese', 'Base.Guacamole', 'Base.Smore',
            'Base.DoughRolled', 'Base.FishRoe', 'Base.RamenBowl', 'Base.PotOfSoup',
            'Base.ColdCuppa', 'Base.ColdDrinkRed', 'Base.ColdDrinkSpiffo', 'Base.ColdDrinkWhite', 'Base.Mugfull', 'Base.TrapMouse'}
        if item in legacy_food_routes and meaning[0] == 'acquisition_process' and len(records) == 1:
            retain_boundary(claim, {records[0]['path'], 'scripts/recipes.txt', 'scripts/evolvedrecipes.txt', semantic.MENU, semantic.CRAFT, semantic.COOK, semantic.GROUPS},
                {'declaration': fields, 'reviewed_result_recipes': [r['observation_ref'] for r in reviewed_results[item].values()],
                 'evolved_relations': base.get('cooking_base_relations', {}).get(item, []),
                 'legacy_notes': 'Make Pot of Soup and EggBoiled replacement entries are commented out. PancakesCraft replaces to PancakesRecipe, not Base.Pancakes. Toast/Waffles evolved entries begin with existing food, not a producer from dough. No bound recipe produces the exact TrapMouse.'},
                'An active exact producer/callback or native food/replacement transition establishing the stated process',
                'The complete supplied recipe result set, evolved base/result relations and exact declared form were compared. Existing-form ingredient addition and similarly named results cannot establish this predecessor creation process. This is an uncorroborated route, not a claim that the item is globally unobtainable.')
            continue
        if item == 'Base.CompostBag' and meaning == ['acquisition_process', 'fill_ground_bag', 'compost']:
            retain_boundary(claim, {records[0]['path'], sources.WORLD_MENU, *sources.COMPOST_ACTIONS},
                {'consumer': sources.COMPOST_TRANSFER}, 'Native compost amount, empty-sack replacement and inventory delivery',
                'The compost menu/action fills the existing bag or replaces an empty sack with this exact bag using available compost. It may fill only partly and does not collect ordinary ground or create compost from food.')
            continue
        if item == 'Base.UnusableMetal' and meaning in (['negative_role', 'crafting', 'material'], ['acquisition_process', 'metal_dismantling']):
            retain_boundary(claim, {records[0]['path'], semantic.MOVE, semantic.PROPS, semantic.CRAFT, semantic.GROUPS},
                {'scrap_definitions': ['Fridge', 'MetalPlates', 'MetalPlatesAndBars', 'SmallMetalPlates'],
                 'consumer': 'getScrapItemsList checks each material. When no usable result was added and unusableItem exists, one or two random entries are appended; addAllScrapItems requests instanceItem and addOrDropItem.'},
                'Native material-to-object binding, random/factory delivery and any additional exact crafting consumer',
                'The supplied fallback can return this exact item when usable metal recovery fails. It is neither guaranteed metal salvage nor a proof that every crafting route excludes the item; the negative claim remains bounded to the supplied recipe/consumer snapshot.')
            continue
        reading_mood = meaning[0] == 'conditional_effect' and meaning[1] in {'boredom', 'stress', 'unhappiness'} and meaning[3] == 'reading'
        if reading_mood:
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Literature' and not fields.get('SkillTrained') and fields.get('CanBeWrite', '').lower() != 'true':
                partial = [f['ref'] for f in candidates if f['payload'] == {'property': meaning[1], 'direction': 'cap_at_reading_start'}]
                uncertainty = {'meaning': meaning, 'examined': {'declaration': fields, 'consumer': semantic.READ,
                                                              'partial_fact_refs': partial},
                               'required_input': 'IsoGameCharacter.ReadLiterature completion interpretation for this exact book',
                               'reason': 'The Lua reading update can restore a mood value that rose above its starting snapshot. That bounded stabilization is represented separately and does not prove the predecessor claim of mood reduction by completed reading.'}
                claim.update(migration_disposition='unresolved', candidate_successor_fact_refs=partial,
                             verified_source_refs=[base['reader'].bindings[records[0]['path']], base['reader'].bindings[semantic.READ]],
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='bounded_lua_and_engine_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': partial, 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
                continue
        if ((meaning[0] == 'effect' and meaning[1] in {'hunger', 'thirst', 'food_sickness', 'wound_infection'})
                or meaning == ['condition', 'raw_ingestion', 'hazard']):
            records = base['declarations'].get(item, [])
            fields, conflicts = sources.stable_properties(records[0]) if len(records) == 1 else ({}, {})
            if fields.get('Type') == 'Food' and not {'Type', 'CantEat', 'OnEat'} & conflicts.keys():
                evidence = [{'path': r['path'], 'line': r['line'], 'end_line': r['end_line'],
                             'sha256': base['reader'].bindings[r['path']]['sha256']} for r in records]
                evidence.append(base['reader'].bindings[semantic.EAT])
                uncertainty = {'examined': {'declaration': fields, 'consumer': semantic.EAT,
                                             'handoff': 'self.character:Eat(self.item, self.percentage)'},
                               'meaning': meaning, 'required_input': 'the native Eat effect interpretation for this exact food form',
                               'reason': 'The bound Lua checks eligibility but delegates the food state changes, including raw-food harm, to Eat. The exact DangerousUncooked, poison, nutritional and callback fields are retained in the declaration above; their presence or sign does not independently establish the claimed effect.'}
                claim.update(migration_disposition='unresolved', verified_source_refs=evidence,
                             reason=uncertainty['reason'], remaining_uncertainty=uncertainty, remaining_work=None,
                             source_binding='source_bound', source_strength='engine_handoff', review_state='reviewed')
                conservation.append({'predecessor_claim_id': claim['predecessor_claim_id'], 'migration_disposition': 'unresolved',
                                     'successor_fact_refs': [], 'locales': {}, 'residual': uncertainty,
                                     'conservation_status': 'bounded_unresolved'})
    inventory['conservation'] = conservation
    inventory['source_assessments'] = source_assessments
    for item in inventory['items']:
        claim_rows = [c for c in inventory['claims'] if c['item_id'] == item['item_id']]
        item['nonempty_internal_delta'] = {
            'already_represented': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'already_represented'],
            'recovered': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'recovered'],
            'corrected': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'corrected'],
            'unresolved': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'unresolved'],
            'responsibility_removed': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'responsibility_removed'],
            'pending': [c['predecessor_claim_id'] for c in claim_rows if c['migration_disposition'] == 'pending_investigation']}
    return inventory
