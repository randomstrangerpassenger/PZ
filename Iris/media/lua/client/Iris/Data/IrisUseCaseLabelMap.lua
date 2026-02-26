-- Iris UseCase Label Map (i18n)
-- 런타임에서 label_key → 표시 문자열 단순 치환용
-- 자동 생성: convert_labelmap_to_lua.py
-- 조건분기/추론 금지: 키→문자열 lookup만 수행

local IrisUseCaseLabelMap = {}

-- use_case_id → 표시 문자열 (KO)
IrisUseCaseLabelMap.KO = {
    ["uc.craft.blowtorch"] = "용접 토치 사용",
    ["uc.craft.carpentry_material"] = "목공에 사용",
    ["uc.craft.carpentry_tool"] = "목공 도구로 사용",
    ["uc.craft.cooking_material"] = "요리에 사용",
    ["uc.craft.cooking_tool"] = "요리 도구로 사용",
    ["uc.craft.electrical_material"] = "전기 작업에 사용",
    ["uc.craft.engineer_material"] = "공학 작업에 사용",
    ["uc.craft.hammer"] = "망치로 사용",
    ["uc.craft.health_material"] = "의료 제작에 사용",
    ["uc.craft.saw"] = "톱으로 사용",
    ["uc.craft.screwdriver"] = "드라이버로 사용",
    ["uc.craft.smithing_material"] = "대장간 작업에 사용",
    ["uc.craft.smithing_tool"] = "대장간 도구로 사용",
    ["uc.craft.trapping_tool"] = "덫 설치에 사용",
    ["uc.craft.welding_material"] = "용접에 사용",
    ["uc.exclusion.consumption_displaycategory_food"] = "음식으로 소비",
    ["uc.exclusion.consumption_food"] = "음식으로 소비",
    ["uc.exclusion.consumption_literature"] = "읽어서 소비",
    ["uc.exclusion.equip_clothing"] = "의류로 착용",
    ["uc.exclusion.inputmaterial_ammo"] = "탄약으로 소비",
    ["uc.exclusion.inputmaterial_material"] = "재료로 소비",
    ["uc.firefighting.extinguish"] = "소화에 사용",
    ["uc.food.open_can"] = "캔 따기",
    ["uc.medical.remove_bullet"] = "총알 제거",
    ["uc.medical.remove_glass"] = "유리 제거",
    ["uc.medical.stitch"] = "봉합",
    ["uc.vehicle.fuel"] = "주유에 사용",
    ["uc.weapon.attach_part"] = "무기 부품 장착",
}

-- use_case_id → 표시 문자열 (EN)
IrisUseCaseLabelMap.EN = {
    ["uc.craft.blowtorch"] = "Blowtorch Use",
    ["uc.craft.carpentry_material"] = "Used in Carpentry",
    ["uc.craft.carpentry_tool"] = "Used as Carpentry Tool",
    ["uc.craft.cooking_material"] = "Used in Cooking",
    ["uc.craft.cooking_tool"] = "Used as Cooking Tool",
    ["uc.craft.electrical_material"] = "Used in Electrical",
    ["uc.craft.engineer_material"] = "Used in Engineering",
    ["uc.craft.hammer"] = "Hammer Use",
    ["uc.craft.health_material"] = "Used in Health Crafting",
    ["uc.craft.saw"] = "Saw Use",
    ["uc.craft.screwdriver"] = "Screwdriver Use",
    ["uc.craft.smithing_material"] = "Used in Smithing",
    ["uc.craft.smithing_tool"] = "Used as Smithing Tool",
    ["uc.craft.trapping_tool"] = "Used for Trapping",
    ["uc.craft.welding_material"] = "Used in Welding",
    ["uc.exclusion.consumption_displaycategory_food"] = "Consumed as Food",
    ["uc.exclusion.consumption_food"] = "Consumed as Food",
    ["uc.exclusion.consumption_literature"] = "Consumed by Reading",
    ["uc.exclusion.equip_clothing"] = "Equipped as Clothing",
    ["uc.exclusion.inputmaterial_ammo"] = "Used as Ammo",
    ["uc.exclusion.inputmaterial_material"] = "Used as Material",
    ["uc.firefighting.extinguish"] = "Fire Extinguishing",
    ["uc.food.open_can"] = "Can Opening",
    ["uc.medical.remove_bullet"] = "Bullet Removal",
    ["uc.medical.remove_glass"] = "Glass Removal",
    ["uc.medical.stitch"] = "Stitching",
    ["uc.vehicle.fuel"] = "Used for Refueling",
    ["uc.weapon.attach_part"] = "Weapon Part Attach",
}

-- surface 키 → 표시 문자열
IrisUseCaseLabelMap.SURFACE_KO = {
    both = "우클릭+레시피",
    context_menu = "우클릭",
    recipe_ui = "레시피",
}

IrisUseCaseLabelMap.SURFACE_EN = {
    both = "Right-click+Recipe",
    context_menu = "Right-click",
    recipe_ui = "Recipe",
}

-- strength 키 → 표시 문자열
IrisUseCaseLabelMap.STRENGTH_KO = {
    STRONG = " [강]",
    WEAK = " [약]",
}

IrisUseCaseLabelMap.STRENGTH_EN = {
    STRONG = " [Strong]",
    WEAK = " [Weak]",
}

-- uniqueness 키 → 표시 문자열
IrisUseCaseLabelMap.UNIQUENESS_KO = {
    shared = " [공유]",
    unique = " [고유]",
}

IrisUseCaseLabelMap.UNIQUENESS_EN = {
    shared = " [Shared]",
    unique = " [Unique]",
}

return IrisUseCaseLabelMap
