--[[
    IrisTranslationLoader.lua
    
    Iris 모드 번역을 PZ Translator에 직접 등록
    PZ가 모드 번역 파일을 자동 로드하지 않는 문제 해결용
]]

-- 전역 변수로 노출 (IrisBrowserData에서 접근 가능하도록)
IrisTranslationLoader = {}

-- 번역 데이터 (언어별)
local TRANSLATIONS = {
    KO = {
        Iris_UI_CategoryLabel = "\235\140\128\235\182\132\235\165\152",  -- 대분류
        Iris_UI_SubcategoryLabel = "\236\134\140\235\182\132\235\165\152",  -- 소분류
        Iris_UI_ItemLabel = "\236\149\132\236\157\180\237\133\156",  -- 아이템
        Iris_UI_DetailLabel = "\236\131\129\236\132\184\236\160\149\235\179\180",  -- 상세정보
        Iris_UI_SearchPlaceholder = "\234\178\128\236\131\137...",  -- 검색...
        Iris_UI_NoInfo = "\236\182\148\234\176\128 \236\160\149\235\179\180 \236\151\134\236\157\140",  -- 추가 정보 없음
        
        -- 상세 정보 레이블
        Iris_Detail_Weight = "\235\172\180\234\178\140",  -- 무게
        Iris_Detail_Type = "\237\131\128\236\158\133",  -- 타입
        Iris_Detail_Module = "\235\170\168\235\147\136",  -- 모듈
        Iris_Detail_Tags = "\235\182\132\235\165\152",  -- 분류
        Iris_Detail_Hunger = "\235\176\176\234\179\160\237\148\148",  -- 배고픔
        Iris_Detail_Thirst = "\234\176\136\236\166\157",  -- 갈증
        Iris_Detail_Stress = "\236\138\164\237\138\184\235\160\136\236\138\164",  -- 스트레스
        Iris_Detail_Boredom = "\234\182\140\237\131\156\234\176\144",  -- 권태감
        Iris_Detail_Calories = "\236\185\188\235\161\156\235\166\172",  -- 칼로리
        Iris_Detail_Damage = "\235\141\176\235\175\184\236\167\128",  -- 데미지
        Iris_Detail_Range = "\236\130\172\234\177\176\235\166\172",  -- 사거리
        Iris_Detail_Critical = "\237\129\172\235\166\172\237\139\176\236\187\172",  -- 크리티컬
        Iris_Detail_Durability = "\235\130\180\234\181\172\235\143\132",  -- 내구도
        Iris_Detail_Recipe = "\235\160\136\236\139\156\237\148\188",  -- 레시피
        Iris_Detail_Furniture = "\234\176\128\234\181\172\237\149\180\236\178\180",  -- 가구해체
        Iris_Detail_Fixer = "\236\136\152\235\166\172\235\143\132\234\181\172",  -- 수리도구
        Iris_Detail_Capacity = "\236\154\169\235\159\137",  -- 용량
        Iris_Detail_Light = "\234\180\145\236\155\144",  -- 광원
        Iris_Detail_Waterproof = "\235\176\169\236\136\152",  -- 방수
        Iris_Detail_Insulation = "\235\179\180\236\152\168",  -- 보온
        
        Iris_Cat_Tool = "\235\143\132\234\181\172",  -- 도구
        Iris_Cat_Combat = "\236\160\132\237\136\172",  -- 전투
        Iris_Cat_Consumable = "\236\134\140\235\170\168\237\146\136",  -- 소모품
        Iris_Cat_Resource = "\236\158\144\236\155\144",  -- 자원
        Iris_Cat_Literature = "\235\172\184\237\151\140",  -- 문헌
        Iris_Cat_Wearable = "\236\157\152\235\165\152",  -- 의류
        
        Iris_Sub_1A = "\234\177\180\236\132\164/\236\160\156\236\158\145",  -- 건설/제작
        Iris_Sub_1B = "\235\182\132\237\149\180/\234\176\156\235\176\169",  -- 분해/개방
        Iris_Sub_1C = "\236\160\149\235\185\132",  -- 정비
        Iris_Sub_1D = "\236\161\176\235\166\172",  -- 조리
        Iris_Sub_1E = "\235\134\141\236\151\133/\236\177\132\236\167\145",  -- 농업/채집
        Iris_Sub_1F = "\236\157\152\235\163\140",  -- 의료
        Iris_Sub_1G = "\237\143\172\237\154\141",  -- 포획
        Iris_Sub_1H = "\234\180\145\236\155\144/\236\160\144\237\153\148",  -- 광원/점화
        Iris_Sub_1I = "\237\134\181\236\139\160",  -- 통신
        Iris_Sub_1J = "\236\160\132\235\160\165",  -- 전력
        
        Iris_Sub_2A = "\235\143\132\235\129\188\235\165\152",  -- 도끼류
        Iris_Sub_2B = "\236\158\165\235\145\148\234\184\176",  -- 장둔기
        Iris_Sub_2C = "\235\139\168\235\145\148\234\184\176",  -- 단둔기
        Iris_Sub_2D = "\236\158\165\234\178\128\235\165\152",  -- 장검류
        Iris_Sub_2E = "\235\139\168\234\178\128\235\165\152",  -- 단검류
        Iris_Sub_2F = "\236\176\189\235\165\152",  -- 창류
        Iris_Sub_2G = "\234\182\140\236\180\157",  -- 권총
        Iris_Sub_2H = "\236\134\140\236\180\157",  -- 소총
        Iris_Sub_2I = "\236\130\176\237\131\132\236\180\157",  -- 산탄총
        Iris_Sub_2J = "\237\136\172\236\178\153/\237\143\173\235\176\156",  -- 투척/폭발
        Iris_Sub_2K = "\237\131\132\236\149\189",  -- 탄약
        Iris_Sub_2L = "\236\180\157\234\184\176\235\182\128\237\146\136",  -- 총기부품
        
        Iris_Sub_3A = "\236\139\157\237\146\136",  -- 식품
        Iris_Sub_3B = "\236\157\140\235\163\140",  -- 음료
        Iris_Sub_3C = "\236\157\152\236\149\189\237\146\136",  -- 의약품
        Iris_Sub_3D = "\234\184\176\237\152\184\237\146\136",  -- 기호품
        Iris_Sub_3E = "\236\149\189\236\180\136",  -- 약초
        
        Iris_Sub_4A = "\234\177\180\236\132\164 \236\158\172\235\163\140",  -- 건설 재료
        Iris_Sub_4B = "\236\161\176\235\166\172 \236\158\172\235\163\140",  -- 조리 재료
        Iris_Sub_4C = "\236\157\152\235\163\140 \236\158\172\235\163\140",  -- 의료 재료
        Iris_Sub_4D = "\236\151\176\235\163\140",  -- 연료
        Iris_Sub_4E = "\236\160\132\236\158\144\235\182\128\237\146\136",  -- 전자부품
        Iris_Sub_4F = "\234\184\176\237\131\128 \236\158\172\235\163\140",  -- 기타 재료
        
        Iris_Sub_5A = "\236\138\164\237\130\172\235\182\129",  -- 스킬북
        Iris_Sub_5B = "\235\160\136\236\139\156\237\148\188\236\158\161\236\167\128",  -- 레시피잡지
        Iris_Sub_5C = "\236\167\128\235\143\132",  -- 지도
        Iris_Sub_5D = "\236\157\188\235\176\152 \236\132\156\236\160\129",  -- 일반 서적
        
        Iris_Sub_6A = "\235\170\168\236\158\144/\237\151\172\235\169\167",  -- 모자/헬멧
        Iris_Sub_6B = "\236\131\129\236\157\152",  -- 상의
        Iris_Sub_6C = "\237\149\152\236\157\152",  -- 하의
        Iris_Sub_6D = "\236\158\165\234\176\145",  -- 장갑
        Iris_Sub_6E = "\236\139\160\235\176\156",  -- 신발
        Iris_Sub_6F = "\235\176\176\235\130\173",  -- 배낭
        Iris_Sub_6G = "\236\149\161\236\132\184\236\132\156\235\166\172",  -- 액세서리
        
        -- 상호작용 섹션
        Iris_Detail_Interaction = "\236\131\129\237\152\184\236\158\145\236\154\169",  -- 상호작용
        Iris_Prefix_Recipe = "[\235\160\136\236\139\156\237\148\188]",  -- [레시피]
        Iris_Prefix_RightClick = "[\236\154\176\237\129\180\235\166\173]",  -- [우클릭]
        
        -- 우클릭 Capability 라벨
        Iris_Cap_ExtinguishFire = "\235\182\136 \235\129\132\234\184\176",  -- 불 끄기
        Iris_Cap_AddGeneratorFuel = "\235\176\156\236\160\132\234\184\176 \236\151\176\235\163\140 \235\132\163\234\184\176",  -- 발전기 연료 넣기
        Iris_Cap_ScrapMoveables = "\234\176\128\234\181\172 \237\149\180\236\178\180",  -- 가구 해체
        Iris_Cap_OpenCannedFood = "\236\186\148 \235\148\176\234\184\176",  -- 캔 따기
        Iris_Cap_StitchWound = "\236\131\129\236\178\152 \235\180\137\237\149\169",  -- 상처 봉합
        Iris_Cap_RemoveEmbeddedObject = "\235\176\149\237\158\128 \235\172\188\236\178\180 \236\160\156\234\177\176",  -- 박힌 물체 제거
        Iris_Cap_AttachWeaponMod = "\235\172\180\234\184\176 \235\182\128\236\176\169\235\172\188 \236\158\165\236\176\169",  -- 무기 부착물 장착
    },
    EN = {
        Iris_UI_CategoryLabel = "Category",
        Iris_UI_SubcategoryLabel = "Subcategory",
        Iris_UI_ItemLabel = "Items",
        Iris_UI_DetailLabel = "Details",
        Iris_UI_SearchPlaceholder = "Search...",
        Iris_UI_NoInfo = "No additional info",
        
        -- Detail labels
        Iris_Detail_Weight = "Weight",
        Iris_Detail_Type = "Type",
        Iris_Detail_Module = "Module",
        Iris_Detail_Tags = "Tags",
        Iris_Detail_Hunger = "Hunger",
        Iris_Detail_Thirst = "Thirst",
        Iris_Detail_Stress = "Stress",
        Iris_Detail_Boredom = "Boredom",
        Iris_Detail_Calories = "Calories",
        Iris_Detail_Damage = "Damage",
        Iris_Detail_Range = "Range",
        Iris_Detail_Critical = "Critical",
        Iris_Detail_Durability = "Durability",
        Iris_Detail_Recipe = "Recipe",
        Iris_Detail_Furniture = "Furniture",
        Iris_Detail_Fixer = "Fixer",
        Iris_Detail_Capacity = "Capacity",
        Iris_Detail_Light = "Light",
        Iris_Detail_Waterproof = "Waterproof",
        Iris_Detail_Insulation = "Insulation",
        
        Iris_Cat_Tool = "Tool",
        Iris_Cat_Combat = "Combat",
        Iris_Cat_Consumable = "Consumable",
        Iris_Cat_Resource = "Resource",
        Iris_Cat_Literature = "Literature",
        Iris_Cat_Wearable = "Wearable",
        
        Iris_Sub_1A = "Construction/Crafting",
        Iris_Sub_1B = "Disassembly/Opening",
        Iris_Sub_1C = "Maintenance",
        Iris_Sub_1D = "Cooking",
        Iris_Sub_1E = "Farming/Foraging",
        Iris_Sub_1F = "Medical",
        Iris_Sub_1G = "Trapping",
        Iris_Sub_1H = "Light/Ignition",
        Iris_Sub_1I = "Communication",
        Iris_Sub_1J = "Electrical",
        
        Iris_Sub_2A = "Axes",
        Iris_Sub_2B = "Long Blunt",
        Iris_Sub_2C = "Short Blunt",
        Iris_Sub_2D = "Long Blades",
        Iris_Sub_2E = "Short Blades",
        Iris_Sub_2F = "Spears",
        Iris_Sub_2G = "Pistols",
        Iris_Sub_2H = "Rifles",
        Iris_Sub_2I = "Shotguns",
        Iris_Sub_2J = "Thrown/Explosives",
        Iris_Sub_2K = "Ammo",
        Iris_Sub_2L = "Gun Parts",
        
        Iris_Sub_3A = "Food",
        Iris_Sub_3B = "Drinks",
        Iris_Sub_3C = "Medicine",
        Iris_Sub_3D = "Luxuries",
        Iris_Sub_3E = "Herbs",
        
        Iris_Sub_4A = "Building Materials",
        Iris_Sub_4B = "Cooking Ingredients",
        Iris_Sub_4C = "Medical Supplies",
        Iris_Sub_4D = "Fuel",
        Iris_Sub_4E = "Electronics",
        Iris_Sub_4F = "Misc Materials",
        
        Iris_Sub_5A = "Skill Books",
        Iris_Sub_5B = "Recipe Magazines",
        Iris_Sub_5C = "Maps",
        Iris_Sub_5D = "General Books",
        
        Iris_Sub_6A = "Hats/Helmets",
        Iris_Sub_6B = "Tops",
        Iris_Sub_6C = "Bottoms",
        Iris_Sub_6D = "Gloves",
        Iris_Sub_6E = "Shoes",
        Iris_Sub_6F = "Backpacks",
        Iris_Sub_6G = "Accessories",
        
        -- Interaction Section
        Iris_Detail_Interaction = "Interactions",
        Iris_Prefix_Recipe = "[Recipe]",
        Iris_Prefix_RightClick = "[Action]",
        
        -- Right-Click Capability Labels
        Iris_Cap_ExtinguishFire = "Extinguish Fire",
        Iris_Cap_AddGeneratorFuel = "Add Generator Fuel",
        Iris_Cap_ScrapMoveables = "Scrap Furniture",
        Iris_Cap_OpenCannedFood = "Open Canned Food",
        Iris_Cap_StitchWound = "Stitch Wound",
        Iris_Cap_RemoveEmbeddedObject = "Remove Embedded Object",
        Iris_Cap_AttachWeaponMod = "Attach Weapon Mod",
    }
}

-- Iris 번역 테이블 (전역)
IrisTranslations = nil

-- 캐시된 언어 키 (SSOT: 이 값만이 언어 키의 단일 진실 소스)
local _cachedLangKey = nil

function IrisTranslationLoader.init()
    print("[IrisTranslation] Initializing translations...")
    
    -- 현재 언어 감지
    local lang = "EN"
    if Translator and Translator.getLanguage then
        local ok, result = pcall(Translator.getLanguage)
        if ok and result then
            lang = tostring(result):upper()
        end
    end
    
    print("[IrisTranslation] Detected language: " .. lang)
    
    -- 언어 키 캐시 (getLangKey()의 SSOT)
    _cachedLangKey = lang
    
    -- 해당 언어의 번역 테이블 로드
    IrisTranslations = TRANSLATIONS[lang] or TRANSLATIONS.EN
    
    print("[IrisTranslation] Loaded " .. (lang == "KO" and "Korean" or "English") .. " translations")
    print("[IrisTranslation] Total keys: " .. tostring(IrisTranslationLoader.countKeys(IrisTranslations)))
    
    return true
end

function IrisTranslationLoader.countKeys(t)
    local count = 0
    for _ in pairs(t) do count = count + 1 end
    return count
end

-- 번역 가져오기
function IrisTranslationLoader.get(key, fallback)
    if IrisTranslations and IrisTranslations[key] then
        return IrisTranslations[key]
    end
    return fallback or key
end

--- 언어 키 단일 반환 (SSOT)
--- 다른 모듈은 Translator.getLanguage()를 직접 호출하지 말고 이 함수를 사용
--- @return string "KO" | "EN" | ...
function IrisTranslationLoader.getLangKey()
    if _cachedLangKey then
        return _cachedLangKey
    end
    -- init()이 아직 안 돌았으면 직접 감지
    local lang = "EN"
    if Translator and Translator.getLanguage then
        local ok, result = pcall(Translator.getLanguage)
        if ok and result then
            lang = tostring(result):upper()
        end
    end
    _cachedLangKey = lang
    return lang
end

-- 파일 로드 시 즉시 초기화 (OnGameBoot보다 먼저 실행되어야 함)
IrisTranslationLoader.init()

return IrisTranslationLoader
