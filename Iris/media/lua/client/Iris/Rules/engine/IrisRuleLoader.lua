--[[
    IrisRuleLoader.lua - Ruleset 로더
    
    엔트리 파일(iris_ruleset.lua)에서 명시적 로드 목록 고정.
    디렉토리 스캔 금지.
    
    로드 순서: allowlist → validator → ruleset
    로드 실패 시 전체 중단 (Fail-Fast).
]]

local IrisRuleLoader = {}

local IrisRuleValidator = require "Iris/Rules/engine/IrisRuleValidator"

-- 로드된 규칙들
IrisRuleLoader._rules = {}
IrisRuleLoader._manualOverrides = {}
IrisRuleLoader._loaded = false
IrisRuleLoader._failed = false
IrisRuleLoader._errorMessage = nil

--- Ruleset 로드 (OnGameStart에서 1회만 호출)
--- @return boolean 성공 여부
function IrisRuleLoader.load()
    if IrisRuleLoader._loaded then
        return not IrisRuleLoader._failed
    end
    
    IrisRuleLoader._loaded = true
    
    -- Manual Overrides 로드
    local overridesOk, overrides = pcall(require, "Iris/Rules/overrides_manual")
    if overridesOk and overrides then
        -- 검증
        local valid, err = IrisRuleValidator.validateManualOverrides(overrides)
        if not valid then
            IrisRuleLoader._failed = true
            IrisRuleLoader._errorMessage = "Iris: Manual override validation failed - " .. err
            print("[Iris] ERROR: " .. IrisRuleLoader._errorMessage)
            return false
        end
        IrisRuleLoader._manualOverrides = overrides
    end
    
    -- Ruleset 로드 (엔트리 파일에서 명시적 목록)
    local rulesetOk, ruleset = pcall(require, "Iris/Ruleset/iris_ruleset")
    if not rulesetOk then
        -- Ruleset이 없으면 빈 상태로 시작 (에러 아님)
        IrisRuleLoader._rules = {}
        return true
    end
    
    -- 각 규칙 파일 검증 및 로드
    local allRules = {}
    for _, ruleFile in ipairs(ruleset) do
        if type(ruleFile) == "table" then
            -- 직접 포함된 규칙 테이블
            local valid, err = IrisRuleValidator.validateRuleset(ruleFile)
            if not valid then
                IrisRuleLoader._failed = true
                IrisRuleLoader._errorMessage = "Iris: Rule validation failed - " .. err
                print("[Iris] ERROR: " .. IrisRuleLoader._errorMessage)
                return false
            end
            
            for _, rule in ipairs(ruleFile) do
                table.insert(allRules, rule)
            end
        end
    end
    
    IrisRuleLoader._rules = allRules
    print("[IrisRuleLoader] Loaded " .. #allRules .. " rules successfully")
    return true
end

--- 로드된 규칙 반환
--- @return table[]
function IrisRuleLoader.getRules()
    return IrisRuleLoader._rules
end

--- Manual Overrides 반환
--- @return table
function IrisRuleLoader.getManualOverrides()
    return IrisRuleLoader._manualOverrides
end

--- 로드 실패 여부
--- @return boolean
function IrisRuleLoader.hasFailed()
    return IrisRuleLoader._failed
end

--- 에러 메시지 반환
--- @return string|nil
function IrisRuleLoader.getErrorMessage()
    return IrisRuleLoader._errorMessage
end

return IrisRuleLoader
