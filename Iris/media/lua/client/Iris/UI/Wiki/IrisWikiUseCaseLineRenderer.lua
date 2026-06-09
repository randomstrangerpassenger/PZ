--[[
    IrisWikiUseCaseLineRenderer.lua

    UseCase line struct -> display string mapping (pure key->string lookup;
    조건분기/추론 금지). Split out of IrisWikiSections (Change 9b) as the
    "usecase line renderer" responsibility. Behaviour byte-identical to the
    former local renderUseCaseLine; IrisWikiSections delegates to this module.
]]

local IrisWikiUseCaseLineRenderer = {}

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")

local IrisUseCaseLabelMap = nil

local function ensureLabelMap()
    if not IrisUseCaseLabelMap then
        local ok, result = safeRequire("Iris/Data/IrisUseCaseLabelMap")
        if ok then IrisUseCaseLabelMap = result end
    end
end

local function getRuntimeLangKey()
    return TranslationResolver.getLangKey("EN")
end

--- UseCase line 구조체 → 표시 문자열 치환
--- 키→문자열 단순 lookup만 수행 (조건분기/추론 금지)
function IrisWikiUseCaseLineRenderer.renderLine(lineObj)
    ensureLabelMap()

    -- 1순위: Python 빌드 파이프라인에서 이미 렌더링된 display_text 우선
    if lineObj.display_text then
        local displayStr = lineObj.display_text
        -- strength가 존재하고 필요하다면 후행 처리(선택)
        local strengthStr = ""
        local uniquenessStr = ""
        if lineObj.strength and IrisUseCaseLabelMap then
            local lang = getRuntimeLangKey()
            local strMapKey = "STRENGTH_" .. lang
            local strMap = IrisUseCaseLabelMap[strMapKey] or IrisUseCaseLabelMap.STRENGTH_EN or {}
            strengthStr = strMap[lineObj.strength] or ""
        end
        return "- " .. displayStr .. strengthStr
    end

    -- 2순위: 레거시 label_key 및 속성 개별 결합 처리
    local label = lineObj.label_key or "?"
    local surface = lineObj.surface or "context_menu"
    local strength = lineObj.strength
    local uniqueness = lineObj.uniqueness

    -- 런타임 언어 감지 (SSOT: IrisTranslationLoader.getLangKey())
    local lang = getRuntimeLangKey()

    -- label_key → 표시 문자열 (현재 언어)
    if IrisUseCaseLabelMap then
        local langMap = IrisUseCaseLabelMap[lang] or IrisUseCaseLabelMap.EN or {}
        local mapped = langMap[label]
        if mapped then label = mapped end
    end

    -- surface 키 → 표시 문자열
    local surfaceStr = surface
    if IrisUseCaseLabelMap then
        local surfMapKey = "SURFACE_" .. lang
        local surfMap = IrisUseCaseLabelMap[surfMapKey] or IrisUseCaseLabelMap.SURFACE_EN or {}
        surfaceStr = surfMap[surface] or surface
    end

    -- strength 키 → 표시 문자열
    local strengthStr = ""
    if strength and IrisUseCaseLabelMap then
        local strMapKey = "STRENGTH_" .. lang
        local strMap = IrisUseCaseLabelMap[strMapKey] or IrisUseCaseLabelMap.STRENGTH_EN or {}
        strengthStr = strMap[strength] or ""
    end

    -- uniqueness 키 → 표시 문자열
    local uniquenessStr = ""
    if uniqueness and IrisUseCaseLabelMap then
        local uniMapKey = "UNIQUENESS_" .. lang
        local uniMap = IrisUseCaseLabelMap[uniMapKey] or IrisUseCaseLabelMap.UNIQUENESS_EN or {}
        uniquenessStr = uniMap[uniqueness] or ""
    end

    return "- " .. label .. " (" .. surfaceStr .. ")" .. strengthStr .. uniquenessStr
end

return IrisWikiUseCaseLineRenderer
