--[[
    allowlist.lua - Iris Evidence Allowlist
    
    Rule DSL v1.1.x 명세 기반.
    여기에 없는 필드/값/연산자는 사용 금지.
    
    로드 순서: allowlist → validator → ruleset
]]

local Allowlist = {}

-- eq 연산자 허용 필드 (단일 값)
Allowlist.EQ_FIELDS = {
    -- Type enum
    "Type",
    "SubCategory",
    
    -- Boolean
    "Alcoholic",
    "CanStoreWater",
    "TorchCone",
    "ActivatedItem",
    "TwoWay",
    "IsLiterature",
    "IsAimedFirearm",
}

-- Type 허용값
Allowlist.TYPE_VALUES = {
    "Weapon",
    "Food",
    "Literature",
    "Clothing",
    "Drainable",
    "Radio",
    "Map",
    "Normal",
}

-- SubCategory 허용값 (eq만 허용, contains 금지)
Allowlist.SUBCATEGORY_VALUES = {
    "Firearm",
    "Swinging",
    "Stab",
    "Spear",
}

-- has/not_has 연산자 허용 필드
Allowlist.HAS_FIELDS = {
    "LightStrength",
    "LightDistance",
    "HungerChange",
    "ThirstChange",
    "StressChange",
    "UnhappyChange",
    "MountOn",
    "SkillTrained",
    "TeachedRecipes",
    "Map",
    "TwoHandWeapon",
}

-- contains 연산자 허용 필드 (리스트 필드만)
Allowlist.CONTAINS_FIELDS = {
    "Categories",
    "Tags",
    "CustomContextMenu",
}

-- Categories 허용값
Allowlist.CATEGORIES_VALUES = {
    "Blunt",
    "Blade",
    "Axe",
    "Spear",
    "Firearm",
    "Thrown",
}

-- Tags 허용값
Allowlist.TAGS_VALUES = {
    "Cookware",
    "Medical",
    "Tool",
    "Weapon",
    "Clothing",
    "Food",
    "Literature",
    "StartFire",
    "Lighter",
}

-- CustomContextMenu 허용값
Allowlist.CUSTOM_CONTEXT_MENU_VALUES = {
    "Disinfect",
    "Bandage",
    "Splint",
    "Stitch",
    "RemoveBullet",
    "RemoveGlass",
    "CleanWound",
}

-- BodyLocation 허용값
Allowlist.BODY_LOCATION_VALUES = {
    "Head",
    "Torso",
    "Torso_Upper",
    "Torso_Lower",
    "Hands",
    "Legs",
    "Groin",
    "Feet",
    "Back",
    "FannyPack",
    "Neck",
    "Eyes",
    "Belt",
    "BeltExtra",
    "Waist",
}

-- AmmoType 허용값
Allowlist.AMMO_TYPE_VALUES = {
    -- 권총 (2-G)
    "Base.Bullets9mm",
    "Base.Bullets45",
    "Base.Bullets44",
    "Base.Bullets38",
    -- 소총 (2-H)
    "Base.223Bullets",
    "Base.308Bullets",
    "Base.556Bullets",
    -- 산탄총 (2-I)
    "Base.ShotgunShells",
}

-- Recipe role 허용값
Allowlist.RECIPE_ROLES = {
    "input",
    "keep",
    "require",
    "output",  -- 연결 정보 표시용만, 분류 태그 부여 증거로 사용 금지
}

-- Recipe category 허용값
Allowlist.RECIPE_CATEGORIES = {
    "Carpentry",
    "MetalWelding",
    "Masonry",
    "Cooking",
    "Mechanics",
    "Farming",
    "Trapping",
    "Fishing",
    "Electronics",
    "Electrical",
}

-- GetItemTypes 그룹 허용값
Allowlist.GET_ITEM_TYPES_GROUPS = {
    "CanOpener",
}

-- MoveablesTag 허용값
Allowlist.MOVEABLES_TAGS = {
    "Crowbar",
    "SharpKnife",
    "Hammer",
    "Screwdriver",
    "Saw",
    "Wrench",
}

-- Fixing role 허용값
Allowlist.FIXING_ROLES = {
    "Fixer",
}

-- Guarded Fields (단독 has() 사용 금지)
Allowlist.GUARDED_FIELDS = {
    LightStrength = { "ActivatedItem", "TorchCone" },
    LightDistance = { "ActivatedItem", "TorchCone" },
    HungerChange = { "Type" },  -- Type=Food
    ThirstChange = { "Type" },  -- Type=Food 또는 Type=Drainable+보조가드
    StressChange = { "Type" },  -- Type=Food
    UnhappyChange = { "Type" }, -- Type=Food
    CanStoreWater = { "Tags", "recipe" }, -- Cookware 또는 Recipe Cooking
}

-- Guarded Types (단독 사용 금지)
Allowlist.GUARDED_TYPES = {
    Drainable = { "ThirstChange", "CanStoreWater" },
}

-- 금지 연산자 (AST 노드 타입 자체가 없어야 함)
Allowlist.FORBIDDEN_OPERATORS = {
    "gt",
    "lt",
    "gte",
    "lte",
    "remove",
    "replace",
    "override",
    "priority",
}

return Allowlist
