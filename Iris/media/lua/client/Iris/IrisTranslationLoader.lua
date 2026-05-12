--[[
    IrisTranslationLoader.lua

    Iris UI translation loader.
    Canonical source is media/lua/shared/translate/*/Iris_*.txt.
    Runtime Lua data is generated for environments where PZ translation files
    are not loaded reliably for this mod.
]]

-- 전역 변수로 노출 (IrisBrowserData에서 접근 가능하도록)
IrisTranslationLoader = {}

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local debug = bootstrap.debug
local warn = bootstrap.warn

-- Translation data is generated from media/lua/shared/translate/*/Iris_*.txt.
local translationDataOk, TRANSLATIONS = safeRequire("Iris/Data/IrisTranslationData")
if not translationDataOk or type(TRANSLATIONS) ~= "table" then
    warn("[IrisTranslation] Translation data load failed; falling back to empty tables")
    TRANSLATIONS = { EN = {}, KO = {} }
end

-- Iris 번역 테이블 (전역)
IrisTranslations = nil

-- 캐시된 언어 키 (SSOT: 이 값만이 언어 키의 단일 진실 소스)
local _cachedLangKey = nil

function IrisTranslationLoader.init()
    debug("[IrisTranslation] Initializing translations...")
    
    -- 현재 언어 감지
    local lang = "EN"
    if Translator and Translator.getLanguage then
        local ok, result = ProtectedCall.engine(Translator.getLanguage)
        if ok and result then
            lang = tostring(result):upper()
        end
    end
    
    debug("[IrisTranslation] Detected language: " .. lang)
    
    -- 언어 키 캐시 (getLangKey()의 SSOT)
    _cachedLangKey = lang
    
    -- 해당 언어의 번역 테이블 로드
    IrisTranslations = TRANSLATIONS[lang] or TRANSLATIONS.EN
    
    debug("[IrisTranslation] Loaded " .. (lang == "KO" and "Korean" or "English") .. " translations")
    debug("[IrisTranslation] Total keys: " .. tostring(IrisTranslationLoader.countKeys(IrisTranslations)))
    
    return true
end

function IrisTranslationLoader.countKeys(t)
    if type(t) ~= "table" then
        return 0
    end
    local count = 0
    for _ in pairs(t) do count = count + 1 end
    return count
end

-- 번역 가져오기
function IrisTranslationLoader.get(key, fallback)
    if IrisTranslations and IrisTranslations[key] then
        return IrisTranslations[key]
    end
    if TRANSLATIONS.EN and TRANSLATIONS.EN[key] then
        return TRANSLATIONS.EN[key]
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
        local ok, result = ProtectedCall.engine(Translator.getLanguage)
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
