from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any


PRIMARY_USE_EXACT_REWRITES: dict[str, tuple[str, str]] = {
    "몸에 착용해 복장과 보호 구성을 할 때 쓰는 의류다": (
        "clothing_identity_fallback",
        "몸에 입거나 걸쳐 착용하는 의류다",
    ),
    "몸에 착용해 복장 구성을 할 때 쓰는 액세서리다": (
        "accessory_identity_fallback",
        "몸에 걸쳐 착용하는 액세서리다",
    ),
    "몸에 걸쳐 입고 활동 복장으로 갖출 때 입는다": (
        "wearing_clothing_surface_cleanup",
        "몸에 걸쳐 입어 차림을 갖출 때 입는다",
    ),
    "몸에 장식하거나 시야를 보조하려고 걸칠 때 착용한다": (
        "wearing_accessory_surface_cleanup",
        "몸에 장식하거나 시야를 보조할 때 착용한다",
    ),
    "용기다": (
        "container_role_fallback",
        "물건을 담아 보관하거나 옮길 때 쓰는 용기다",
    ),
    "재료다": (
        "material_role_fallback",
        "다른 제작이나 보수에 보태 쓸 수 있는 재료다",
    ),
    "도구다": (
        "tool_role_fallback",
        "여러 상황에 두루 쓸 수 있는 도구다",
    ),
    "조리나 식사 준비 작업에서 먹거나 나눠 먹을 때 쓴다": (
        "food_preparation_chain",
        "섭취하여 포만감을 얻을 수 있다",
    ),
    "학습 작업에서 기술이나 제작법을 익히려고 읽거나 참고할 때 본다": (
        "learning_reference",
        "기술이나 제작법을 익히려고 읽거나 참고할 때 본다",
    ),
    "착용 작업에서 몸에 걸쳐 입고 활동 복장으로 갖출 때 입는다": (
        "wearing_clothing",
        "몸에 걸쳐 입어 차림을 갖출 때 입는다",
    ),
    "음료 섭취 작업에서 마시거나 나눠 마실 때 쓴다": (
        "drink_consumption",
        "마시거나 나눠 마실 때 쓴다",
    ),
    "보관 정리 작업에서 물건을 상자나 가방에 담아 옮길 때 쓴다": (
        "storage_sorting",
        "물건을 상자나 가방에 담아 옮길 때 쓴다",
    ),
    "착용 작업에서 몸에 장식하거나 시야 보조용으로 걸칠 때 착용한다": (
        "wearing_accessory",
        "몸에 장식하거나 시야를 보조할 때 착용한다",
    ),
    "보관이나 휴대 작업에 쓰는 가방이다": (
        "bag_role_fallback",
        "물건을 담아 옮길 때 쓰는 가방이다",
    ),
    "물건을 담아 보관하거나 들고 다닐 때 쓰는 가방이다": (
        "bag_role_fallback",
        "물건을 담아 옮길 때 쓰는 가방이다",
    ),
    "수확물 정리 작업에서 포대를 풀거나 나눌 때 쓴다": (
        "harvest_pack_sorting",
        "수확물을 포대에서 풀거나 나눌 때 쓴다",
    ),
    "총기 개조 작업에 들어가는 부품이다": (
        "gun_modding_membership",
        "총기 개조에 들어가는 부품이다",
    ),
    "전자 조립 작업에 들어가는 부품이다": (
        "electronics_membership",
        "전자 조립에 들어가는 부품이다",
    ),
    "장식이나 마감 작업에서 표면을 칠할 때 쓰는 도료다": (
        "paint_finishing",
        "표면을 칠하거나 마감할 때 쓰는 도료다",
    ),
    "독서 작업에서 읽거나 훑어보며 내용을 살필 때 본다": (
        "reading_reference",
        "읽거나 훑어보며 내용을 살필 때 본다",
    ),
    "착용 작업에서 머리나 얼굴에 걸쳐 가리거나 보호할 때 착용한다": (
        "wearing_head_face",
        "머리나 얼굴에 걸쳐 가리거나 보호할 때 착용한다",
    ),
    "야외 이동 작업에서 펼쳐 비를 막거나 접어 휴대할 때 쓴다": (
        "weather_cover_use",
        "펼쳐 비를 막거나 접어 휴대할 때 쓴다",
    ),
    "근접 전투 작업에서 휘둘러 공격하거나 밀어낼 때 쓴다": (
        "melee_action_direct",
        "휘둘러 공격하거나 밀어낼 때 쓴다",
    ),
    "근접 전투나 작업에 함께 쓰는 도구다": (
        "hybrid_tool_role",
        "근접 전투에도 쓰고 다른 일에도 함께 쓰는 도구다",
    ),
    "연료 취급 작업에서 연료를 옮기거나 넣을 때 쓴다": (
        "fuel_transfer",
        "연료를 옮기거나 넣을 때 쓴다",
    ),
    "기호품 소비 작업에서 피우거나 마시며 기분을 달랠 때 쓴다": (
        "comfort_consumption",
        "피우거나 마시며 기분을 달랠 때 쓴다",
    ),
    "건설이나 보수 작업에서 틈을 메우거나 마감할 때 쓴다": (
        "construction_seal_finish",
        "건설이나 보수에서 틈을 메우거나 마감할 때 쓴다",
    ),
    "상처 처치 작업에 쓰는 의료 소모품이다": (
        "medical_consumable_role",
        "상처 처치에 쓰는 의료 소모품이다",
    ),
    "설치하거나 투척해 기폭하는 전투 작업에 쓰는 폭발물이다": (
        "explosive_combat_role",
        "설치하거나 투척해 기폭할 때 쓰는 폭발물이다",
    ),
    "즉석 폭발물 조립 작업에서 격발 장치를 붙여 완성할 때 쓴다": (
        "explosive_assembly_action",
        "격발 장치를 붙여 즉석 폭발물을 완성할 때 쓴다",
    ),
    "벌목 작업에서 나무를 찍거나 자를 때 쓴다": (
        "woodcutting_action_direct",
        "나무를 찍거나 자를 때 쓴다",
    ),
    "상처 처치 작업에 쓰는 의료 용품이다": (
        "medical_item_role",
        "상처 처치에 쓰는 의료 용품이다",
    ),
    "제작이나 수리 작업에 들어가는 소모성 재료다": (
        "consumable_material_role",
        "제작이나 수리에 들어가는 소모성 재료다",
    ),
    "휴대 작업에서 메거나 들고 다니며 물건을 담아 옮길 때 쓴다": (
        "portable_storage_action",
        "메거나 들고 다니며 물건을 담아 옮길 때 쓴다",
    ),
    "침구 제작 작업에서 속재를 맞추거나 꿰맬 때 쓴다": (
        "bedding_assembly_action",
        "침구를 만들 때 속재를 맞추거나 꿰맬 때 쓴다",
    ),
    "즉석 폭발물 제작 작업에서 내용물을 담거나 분사성 재료를 조합할 때 쓴다": (
        "explosive_material_mix_action",
        "내용물을 담거나 분사성 재료를 조합해 즉석 폭발물을 만들 때 쓴다",
    ),
    "덫 및 어망 제작 작업에 들어가는 재료다": (
        "trap_net_membership",
        "덫이나 어망을 만들 때 들어가는 재료다",
    ),
    "수리 작업에서 망가진 장비를 다시 연결하거나 손볼 때 쓴다": (
        "repair_action_direct",
        "망가진 장비를 다시 연결하거나 손볼 때 쓴다",
    ),
    "전력 작업에서 설치해 주변 기기에 전기를 공급할 때 쓴다": (
        "power_supply_action",
        "설치해 주변 기기에 전기를 공급할 때 쓴다",
    ),
    "금속 제작 작업에서 녹이거나 두드려 다른 부품으로 만들 때 쓴다": (
        "metalwork_material_action",
        "금속을 녹이거나 두드려 다른 부품으로 만들 때 쓴다",
    ),
    "이동 계획 작업에서 위치를 확인하려고 펼쳐 볼 때 참고한다": (
        "map_planning_action",
        "위치를 확인하려고 펼쳐 볼 때 참고한다",
    ),
    "묶거나 연결이 필요한 제작 작업에 쓰는 로프 재료다": (
        "rope_material_role",
        "묶거나 연결할 때 쓰는 로프 재료다",
    ),
    "즉석 제작 작업에서 막대나 가지를 손잡이나 몸체로 맞출 때 쓴다": (
        "improvised_assembly_action",
        "막대나 가지를 손잡이나 몸체로 맞출 때 쓴다",
    ),
    "의료 처치 작업에서 소독하거나 약재로 써 상처를 돌볼 때 쓴다": (
        "medical_treatment_action",
        "소독하거나 약재로 써 상처를 돌볼 때 쓴다",
    ),
    "근접 전투 작업에서 거리를 두고 찌르거나 밀어낼 때 쓴다": (
        "reach_melee_action",
        "거리를 두고 찌르거나 밀어낼 때 쓴다",
    ),
    "재배와 관리 작업에 쓰는 원예 용품이다": (
        "gardening_role_fallback",
        "재배와 관리에 쓰는 원예 용품이다",
    ),
    "재배 준비에서 흙이나 토양에 보충 재료를 더할 때 쓰는 원예 재료다": (
        "soil_input_material_surface_cleanup",
        "흙이나 토양에 보충 재료를 더할 때 쓰는 원예 재료다",
    ),
    "작물 관리에서 해충이나 병해를 막기 위해 뿌리는 원예 분무제다": (
        "crop_treatment_spray_surface_cleanup",
        "작물에 뿌려 해충이나 병해를 막을 때 쓰는 원예 분무제다",
    ),
    "먹거나 나눠 먹을 때 쓴다": (
        "food_preparation_chain",
        "섭취하여 포만감을 얻을 수 있다",
    ),
    "조리 준비 작업에서 재료를 담거나 섞고 익히기 전에 다룰 때 쓴다": (
        "cooking_prep_before_handling",
        "재료를 담거나 섞어 조리할 때 쓴다",
    ),
    "장전 준비 작업에서 탄약을 상자나 클립에 담거나 꺼낼 때 다룬다": (
        "ammo_loading_prep",
        "탄약을 상자나 클립에 담거나 꺼낼 때 쓴다",
    ),
    "조리 작업에서 재료를 익히거나 다룰 때 쓴다": (
        "cooking_use_action",
        "재료를 익히거나 조리할 때 쓴다",
    ),
    "조리 작업에서 재료를 다루거나 익힐 때 쓰는 도구다": (
        "cooking_tool_fallback",
        "재료를 익히거나 조리할 때 쓰는 도구다",
    ),
    "건축 준비 작업에서 자재를 가공하거나 맞출 때 쓴다": (
        "construction_prep_action",
        "건축 시 자재를 가공하거나 맞출 때 쓴다",
    ),
    "농사 준비 작업에서 씨앗을 꺼내거나 나눌 때 쓴다": (
        "seed_handling_prep",
        "씨앗을 꺼내거나 나눌 때 쓴다",
    ),
    "야영 준비 작업에서 임시 거처를 설치할 때 쓴다": (
        "field_shelter_prep",
        "임시 거처를 설치할 때 쓴다",
    ),
    "야외에서 불을 피우는 준비 작업에 쓴다": (
        "campfire_prep",
        "야외에서 불을 피울 때 쓴다",
    ),
    "건설이나 제작 준비 작업에서 자재를 깎거나 맞춰 다른 도구 부품으로 만들 때 쓴다": (
        "construction_material_prep",
        "자재를 깎거나 맞춰 다른 도구 부품으로 만들 때 쓴다",
    ),
    "원시 제작 작업에서 석기나 즉석 무기를 깎아 만들 때 쓴다": (
        "primitive_crafting_action",
        "석기나 즉석 무기를 깎아 만들 때 쓴다",
    ),
    "즉석 무기 제작 작업에서 창 끝을 보강할 때 쓴다": (
        "improvised_weapon_tip_attachment",
        "창 끝에 부착해 즉석 무기를 만들 때 쓴다",
    ),
    "공간 연출 작업에서 장식물, 전시물, 표지물을 세우거나 치우며 구역 표시를 정리할 때 다룬다": (
        "staged_space_arrangement",
        "장식물이나 표지물을 세우거나 치워 구역 표시를 정리할 때 쓴다",
    ),
    "설비 배치 작업에서 기기나 고정 설비를 떼어내거나 다시 설치할 때 다룬다": (
        "fixture_installation_handling",
        "기기나 고정 설비를 떼어내거나 다시 설치할 때 쓴다",
    ),
    "실내 배치 작업에서 의자나 탁자, 휴식 가구를 옮겨 자리를 잡을 때 다룬다": (
        "furniture_arrangement_handling",
        "의자나 탁자 같은 가구를 옮겨 배치할 때 쓴다",
    ),
    "보관 작업에서 소지품이나 내용물을 담아 휴대하거나 나눠 옮길 때 다룬다": (
        "container_storage_handling",
        "소지품이나 내용물을 담아 휴대하거나 나눠 옮길 때 쓴다",
    ),
    "차량 정비 작업에서 주행 부품을 분리하거나 교체해 구동 상태를 복구할 때 다룬다": (
        "vehicle_running_gear_handling",
        "차량 정비에서 주행 부품을 분리하거나 교체할 때 쓰인다",
    ),
    "분장 작업에서 얼굴이나 눈, 입술 부위에 색을 입히거나 무늬를 올릴 때 다룬다": (
        "makeup_application_handling",
        "얼굴이나 눈, 입술 부위에 색을 입히거나 무늬를 더할 때 쓴다",
    ),
    "전자 작업에서 기기를 분해하거나 회로를 맞출 때 다룬다": (
        "electronics_handling",
        "기기를 분해하거나 회로를 맞출 때 쓰인다",
    ),
    "차량 정비 작업에서 차체 패널이나 유리를 떼어내거나 다시 끼울 때 다룬다": (
        "vehicle_body_panel_handling",
        "차량 정비에서 차체 패널이나 유리를 떼어내거나 다시 끼울 때 쓰인다",
    ),
    "여가 작업에서 사진이나 기록 매체, 기념품 장난감을 꺼내 보거나 모아둘 때 다룬다": (
        "collectible_viewing_handling",
        "사진이나 기록 매체, 기념품 장난감을 꺼내 보거나 모아둘 때 쓴다",
    ),
    "폭발물 운용 작업에서 기폭 장치를 갖춘 폭발물을 설치할 때 다룬다": (
        "explosive_device_handling",
        "기폭 장치를 갖춘 폭발물을 설치할 때 쓴다",
    ),
    "차량 정비 작업에서 좌석이나 적재 모듈을 분리하거나 다시 끼울 때 다룬다": (
        "vehicle_cabin_module_handling",
        "차량 정비에서 좌석이나 적재 모듈을 분리하거나 다시 끼울 때 쓰인다",
    ),
    "차량 정비 작업에서 연료 탱크를 떼어내거나 교체할 때 다룬다": (
        "vehicle_fuel_tank_handling",
        "차량 정비에서 연료 탱크를 떼어내거나 교체할 때 쓰인다",
    ),
    "생활 관리 작업에서 몸과 주변을 닦고 정리하거나 실내에 필요한 소모품을 챙길 때 다룬다": (
        "household_care_handling",
        "몸과 주변을 닦고 정리하거나 실내에 필요한 소모품을 챙길 때 쓴다",
    ),
    "외형 손질 작업에서 머리색이나 화장 바탕을 정리하고 준비할 때 다룬다": (
        "appearance_prep_handling",
        "머리색이나 화장 바탕을 정리할 때 쓴다",
    ),
    "착용 작업에서 손목에 시계를 채워 시간을 확인하거나 알람을 맞출 때 다룬다": (
        "watch_wearing_handling",
        "손목에 차고 시간을 확인하거나 알람을 맞출 때 쓴다",
    ),
    "놀이 작업에서 판과 카드, 말, 작은 장난감을 꺼내 가볍게 즐길 때 다룬다": (
        "casual_game_handling",
        "판이나 카드, 말, 작은 장난감을 꺼내 즐길 때 쓴다",
    ),
    "문서 정리 작업에서 쓰고 지우거나 종이를 집고 고정할 때 다룬다": (
        "desk_supply_handling",
        "쓰고 지우거나 종이를 집고 고정할 때 쓴다",
    ),
    "생활 작업에서 작은 소품이나 장식, 반려동물 물건을 곁에 두고 챙길 때 다룬다": (
        "small_accessory_handling",
        "작은 소품이나 장식, 반려동물 물건을 곁에 두고 챙길 때 쓴다",
    ),
    "자재 정리 작업에서 거친 재료나 남은 부품을 모아 다음 제작용으로 분류할 때 다룬다": (
        "reclaimed_material_sorting",
        "거친 재료나 남은 부품을 모아 다음 제작용으로 분류할 때 쓴다",
    ),
    "주방 작업에서 식기와 상차림 소품을 꺼내 쓰거나 식사 준비에 곁들일 때 다룬다": (
        "table_setting_handling",
        "식기와 상차림 소품을 꺼내 쓰거나 식사 자리를 차릴 때 쓴다",
    ),
    "경기나 레저 활동에서 종목에 맞는 라켓이나 스틱, 패들류 장비로 다룬다": (
        "sports_equipment_handling",
        "경기나 레저 활동에서 종목에 맞는 라켓이나 스틱, 패들로 쓴다",
    ),
    "놀이 작업에서 던지거나 차고 튀기며 스포츠용 물건을 가지고 놀 때 다룬다": (
        "ball_play_handling",
        "던지거나 차고 튀기며 가지고 놀 때 쓴다",
    ),
    "보안 작업에서 자물쇠나 차량, 문 장치를 열거나 잠글 때 다룬다": (
        "security_access_handling",
        "자물쇠나 차량, 문 장치를 열거나 잠글 때 쓴다",
    ),
    "빈 용기 정리 작업에서 남은 캔이나 용기를 비우고 따로 모아 다시 쓰거나 처리할 때 다룬다": (
        "empty_container_reuse",
        "남은 캔이나 용기를 비우고 따로 모아 다시 쓰거나 처리할 때 쓴다",
    ),
    "실내 정리 작업에서 수납 가구나 보관함을 옮겨 배치할 때 다룬다": (
        "moveable_storage_handling",
        "수납 가구나 보관함을 옮겨 배치할 때 쓴다",
    ),
    "재배와 야외 관리 작업에서 흙이나 바닥 재료를 다룰 때 쓰는 도구다": (
        "gardening_tool_handling",
        "흙이나 바닥 재료를 고르거나 옮길 때 쓰는 도구다",
    ),
    "몸단장 작업에서 향을 더하거나 빗고 면도, 양치 같은 손질 준비를 할 때 다룬다": (
        "grooming_handling",
        "향을 더하거나 빗고 면도, 양치할 때 쓴다",
    ),
    "물가 활동을 준비하며 채비를 갖추고 낚시 장비를 다룰 때 쓴다": (
        "fishing_prep_handling",
        "채비를 갖추고 낚시 장비를 쓸 때 쓴다",
    ),
    "건설이나 보수 작업에서 채우거나 마감할 자재로 다룬다": (
        "construction_finishing_material",
        "건설이나 보수 작업에서 틈을 메우거나 마감할 때 쓴다",
    ),
    "소지품 정리 작업에서 현금과 카드, 지갑을 챙겨 들고 다닐 때 다룬다": (
        "wallet_handling",
        "현금과 카드, 지갑을 챙겨 들고 다닐 때 쓴다",
    ),
    "차량 정비 작업에서 배터리를 연결하거나 교체해 전기 계통을 복구할 때 다룬다": (
        "vehicle_battery_handling",
        "차량 정비에서 배터리를 연결하거나 교체할 때 쓰인다",
    ),
    "교란 작업에서 소리를 내는 장치를 설치하거나 던질 때 다룬다": (
        "noise_device_handling",
        "소리를 내는 장치를 설치하거나 던질 때 쓴다",
    ),
    "청취 작업에서 휴대용 라디오를 켜고 주파수를 맞춰 방송을 들을 때 다룬다": (
        "portable_radio_handling",
        "휴대용 라디오를 켜고 주파수를 맞춰 방송을 들을 때 쓴다",
    ),
}

PROTECTIVE_WEAR_CONTEXT_RULES: tuple[dict[str, Any], ...] = (
    {
        "rule_id": "protective_bulletproof_vest",
        "item_prefixes": ("Base.Vest_Bullet",),
        "primary_use_inputs": (
            "몸에 착용해 복장과 보호 구성을 할 때 쓰는 의류다",
            "몸에 입거나 걸쳐 착용하는 의류다",
            "총격에 대비해 몸통을 보호하려고 입는 의류다",
        ),
        "cleaned_text": "착용 시 몸통을 보호할 수 있다",
    },
    {
        "rule_id": "protective_torso_wear",
        "item_prefixes": ("Base.Jacket_Fireman",),
        "primary_use_inputs": (
            "몸에 착용해 복장과 보호 구성을 할 때 쓰는 의류다",
            "몸에 입거나 걸쳐 착용하는 의류다",
            "몸을 보호하려고 입는 의류다",
        ),
        "cleaned_text": "착용 시 몸을 보호할 수 있다",
    },
    {
        "rule_id": "protective_headgear",
        "item_prefixes": (
            "Base.Hat_HardHat",
            "Base.Hat_CrashHelmet",
            "Base.Hat_FootballHelmet",
            "Base.Hat_HockeyHelmet",
            "Base.Hat_RidingHelmet",
            "Base.Hat_RiotHelmet",
            "Base.Hat_Army",
            "Base.Hat_SPHhelmet",
            "Base.Hat_Fireman",
            "Base.Hat_BaseballHelmet_",
            "Base.Hat_JockeyHelmet",
            "Base.Hat_Boxing",
        ),
        "primary_use_inputs": (
            "몸에 착용해 복장 구성을 할 때 쓰는 액세서리다",
            "몸에 걸쳐 착용하는 액세서리다",
            "머리를 보호하려고 쓰는 장비다",
        ),
        "cleaned_text": "착용 시 머리를 보호할 수 있다",
    },
    {
        "rule_id": "protective_facegear",
        "item_prefixes": (
            "Base.Hat_HockeyMask",
        ),
        "primary_use_inputs": (
            "몸에 착용해 복장 구성을 할 때 쓰는 액세서리다",
            "몸에 걸쳐 착용하는 액세서리다",
            "얼굴을 보호하려고 착용하는 장비다",
        ),
        "cleaned_text": "착용 시 얼굴을 보호할 수 있다",
    },
    {
        "rule_id": "protective_respirator",
        "item_prefixes": (
            "Base.Hat_GasMask",
            "Base.Hat_NBCmask",
            "Base.Hat_DustMask",
        ),
        "primary_use_inputs": (
            "몸에 착용해 복장 구성을 할 때 쓰는 액세서리다",
            "몸에 걸쳐 착용하는 액세서리다",
            "몸을 보호하려고 착용하는 장비다",
            "호흡기를 보호하려고 착용하는 장비다",
        ),
        "cleaned_text": "착용 시 호흡기를 보호할 수 있다",
    },
    {
        "rule_id": "protective_hearing_gear",
        "item_prefixes": (
            "Base.Hat_EarMuff_Protectors",
        ),
        "primary_use_inputs": (
            "몸에 착용해 복장 구성을 할 때 쓰는 액세서리다",
            "몸에 걸쳐 착용하는 액세서리다",
            "몸을 보호하려고 착용하는 장비다",
            "귀를 보호하려고 착용하는 장비다",
        ),
        "cleaned_text": "착용 시 귀를 보호할 수 있다",
    },
    {
        "rule_id": "protective_gloves",
        "item_prefixes": (
            "Base.Gloves_LeatherGloves",
            "Base.Gloves_Boxing",
        ),
        "primary_use_inputs": (
            "몸에 착용해 복장 구성을 할 때 쓰는 액세서리다",
            "몸에 걸쳐 착용하는 액세서리다",
            "손을 보호하려고 끼는 장비다",
        ),
        "cleaned_text": "착용 시 손을 보호할 수 있다",
    },
    {
        "rule_id": "protective_footwear",
        "item_prefixes": (
            "Base.Shoes_ArmyBoots",
            "Base.Shoes_BlackBoots",
            "Base.Shoes_RidingBoots",
            "Base.Shoes_Wellies",
        ),
        "primary_use_inputs": (
            "몸에 착용해 복장과 보호 구성을 할 때 쓰는 의류다",
            "몸에 입거나 걸쳐 착용하는 의류다",
            "발을 보호하려고 신는 의류다",
        ),
        "cleaned_text": "착용 시 발을 보호할 수 있다",
    },
)

CONTEXTUAL_PRIMARY_USE_RULES: tuple[dict[str, Any], ...] = (
    {
        "rule_id": "firearm_shotgun_primary_use_cleanup",
        "item_ids": (
            "Base.Shotgun",
            "Base.DoubleBarrelShotgun",
        ),
        "primary_use_inputs": (
            "총기 개조에 들어가는 부품이다",
        ),
        "cleaned_text": "사격 전투에 쓰는 화기다",
    },
)

IDENTITY_HINT_CONTEXT_RULES: tuple[dict[str, Any], ...] = (
    {
        "rule_id": "firearm_rifle_identity_cleanup",
        "item_prefixes": (
            "Base.AssaultRifle",
            "Base.HuntingRifle",
            "Base.VarmintRifle",
        ),
        "identity_hint_inputs": (
            "근접 무기",
        ),
        "primary_use_inputs": (
            "사격 전투에 쓰는 화기다",
        ),
        "cleaned_text": "소총",
    },
    {
        "rule_id": "firearm_shotgun_identity_cleanup",
        "item_prefixes": (
            "Base.Shotgun",
            "Base.DoubleBarrelShotgun",
        ),
        "identity_hint_inputs": (
            "근접 무기",
        ),
        "primary_use_inputs": (
            "사격 전투에 쓰는 화기다",
        ),
        "cleaned_text": "산탄총",
    },
)

ITEM_SPECIFIC_FACT_RULES: tuple[dict[str, Any], ...] = (
    {
        "rule_id": "school_bag_surface_override",
        "item_id": "Base.Bag_Schoolbag",
        "primary_use_inputs": (
            "보관이나 휴대 작업에 쓰는 가방이다",
            "물건을 담아 옮길 때 쓰는 가방이다",
            "소지품을 담는 학생용 배낭이다",
        ),
        "primary_use": "소지품을 담는 학생용 배낭이다",
        "secondary_use": "등에 착용해 추가 수납 공간을 제공한다",
    },
    {
        "rule_id": "generic_bag_surface_override",
        "identity_hint_inputs": (
            "가방",
        ),
        "excluded_item_ids": (
            "Base.Bag_Schoolbag",
        ),
        "primary_use_inputs": (
            "보관이나 휴대 작업에 쓰는 가방이다",
            "물건을 담아 옮길 때 쓰는 가방이다",
            "소지품을 담는 배낭이다",
        ),
        "primary_use": "소지품을 담는 배낭이다",
        "secondary_use": "등에 착용해 추가 수납 공간을 제공한다",
    },
)

TRANSLATIONESE_TOKENS = (
    "작업",
    "준비 작업",
    "다룬다",
    "다룰 때",
    "다루거나",
)


@dataclass(frozen=True)
class PrimaryUseCleanupResult:
    cleaned_text: str
    applied_rule_id: str | None


def rewrite_protective_wear_primary_use(row: dict[str, Any]) -> PrimaryUseCleanupResult:
    item_id = str(row.get("item_id") or "")
    primary_use = row.get("primary_use")
    if not isinstance(primary_use, str):
        return PrimaryUseCleanupResult(cleaned_text=primary_use or "", applied_rule_id=None)

    for rule in PROTECTIVE_WEAR_CONTEXT_RULES:
        if primary_use not in rule["primary_use_inputs"]:
            continue
        if any(item_id.startswith(prefix) for prefix in rule["item_prefixes"]):
            return PrimaryUseCleanupResult(
                cleaned_text=rule["cleaned_text"],
                applied_rule_id=str(rule["rule_id"]),
            )
    return PrimaryUseCleanupResult(cleaned_text=primary_use, applied_rule_id=None)


def rewrite_primary_use(text: str | None) -> PrimaryUseCleanupResult:
    if not isinstance(text, str):
        return PrimaryUseCleanupResult(cleaned_text=text or "", applied_rule_id=None)
    rewrite = PRIMARY_USE_EXACT_REWRITES.get(text)
    if rewrite is None:
        return PrimaryUseCleanupResult(cleaned_text=text, applied_rule_id=None)
    rule_id, cleaned_text = rewrite
    return PrimaryUseCleanupResult(cleaned_text=cleaned_text, applied_rule_id=rule_id)


def rewrite_contextual_primary_use(row: dict[str, Any]) -> PrimaryUseCleanupResult:
    item_id = str(row.get("item_id") or "")
    primary_use = row.get("primary_use")
    if not isinstance(primary_use, str):
        return PrimaryUseCleanupResult(cleaned_text=primary_use or "", applied_rule_id=None)

    for rule in CONTEXTUAL_PRIMARY_USE_RULES:
        if primary_use not in rule["primary_use_inputs"]:
            continue
        if item_id in rule["item_ids"]:
            return PrimaryUseCleanupResult(
                cleaned_text=rule["cleaned_text"],
                applied_rule_id=str(rule["rule_id"]),
            )
    return PrimaryUseCleanupResult(cleaned_text=primary_use, applied_rule_id=None)


def rewrite_identity_hint(row: dict[str, Any]) -> PrimaryUseCleanupResult:
    item_id = str(row.get("item_id") or "")
    identity_hint = row.get("identity_hint")
    primary_use = row.get("primary_use")
    if not isinstance(identity_hint, str):
        return PrimaryUseCleanupResult(cleaned_text=identity_hint or "", applied_rule_id=None)

    for rule in IDENTITY_HINT_CONTEXT_RULES:
        if identity_hint not in rule["identity_hint_inputs"]:
            continue
        if primary_use not in rule["primary_use_inputs"]:
            continue
        if any(item_id.startswith(prefix) for prefix in rule["item_prefixes"]):
            return PrimaryUseCleanupResult(
                cleaned_text=rule["cleaned_text"],
                applied_rule_id=str(rule["rule_id"]),
            )
    return PrimaryUseCleanupResult(cleaned_text=identity_hint, applied_rule_id=None)


def rewrite_item_specific_fact_fields(row: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    item_id = str(row.get("item_id") or "")
    identity_hint = row.get("identity_hint")
    primary_use = row.get("primary_use")
    if not isinstance(primary_use, str):
        return row, None

    for rule in ITEM_SPECIFIC_FACT_RULES:
        rule_item_id = rule.get("item_id")
        if rule_item_id is not None and item_id != rule_item_id:
            continue
        excluded_item_ids = set(rule.get("excluded_item_ids") or ())
        if item_id in excluded_item_ids:
            continue
        identity_hint_inputs = tuple(rule.get("identity_hint_inputs") or ())
        if identity_hint_inputs and identity_hint not in identity_hint_inputs:
            continue
        if primary_use not in rule["primary_use_inputs"]:
            continue
        updated = dict(row)
        updated["primary_use"] = rule["primary_use"]
        updated["secondary_use"] = rule["secondary_use"]
        return updated, str(rule["rule_id"])
    return row, None


def collect_translationese_hits(text: str | None) -> list[str]:
    if not isinstance(text, str):
        return []
    return [token for token in TRANSLATIONESE_TOKENS if token in text]


def cleanup_fact_row(row: dict[str, Any]) -> tuple[dict[str, Any], tuple[str, ...]]:
    updated = dict(row)
    applied_rule_ids: list[str] = []
    result = rewrite_primary_use(row.get("primary_use"))
    if result.applied_rule_id is None:
        result = rewrite_contextual_primary_use(row)
    if result.applied_rule_id is None:
        result = rewrite_protective_wear_primary_use(row)
    if result.applied_rule_id is not None:
        updated["primary_use"] = result.cleaned_text
        applied_rule_ids.append(result.applied_rule_id)

    identity_result = rewrite_identity_hint(updated)
    if identity_result.applied_rule_id is not None:
        updated["identity_hint"] = identity_result.cleaned_text
        applied_rule_ids.append(identity_result.applied_rule_id)

    updated, item_specific_rule_id = rewrite_item_specific_fact_fields(updated)
    if item_specific_rule_id is not None:
        applied_rule_ids.append(item_specific_rule_id)

    if not applied_rule_ids:
        return updated, ()

    slot_meta = dict(updated.get("slot_meta") or {})
    slot_meta["body_role_lexical_cleanup"] = {
        "applied": True,
        "rule_id": applied_rule_ids[-1],
        "rule_ids": applied_rule_ids,
    }
    updated["slot_meta"] = slot_meta
    return updated, tuple(applied_rule_ids)


def cleanup_facts_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cleaned_rows: list[dict[str, Any]] = []
    changed_items: list[str] = []
    rule_counter: Counter[str] = Counter()
    residual_counter: Counter[str] = Counter()

    for row in rows:
        cleaned_row, applied_rule_ids = cleanup_fact_row(row)
        cleaned_rows.append(cleaned_row)
        if applied_rule_ids:
            changed_items.append(str(row["item_id"]))
            for rule_id in applied_rule_ids:
                rule_counter[rule_id] += 1
        for hit in collect_translationese_hits(cleaned_row.get("primary_use")):
            residual_counter[hit] += 1

    summary = {
        "changed_item_ids": sorted(changed_items),
        "changed_count": len(changed_items),
        "rule_counts": dict(sorted(rule_counter.items())),
        "residual_translationese_counts": dict(sorted(residual_counter.items())),
    }
    return cleaned_rows, summary
