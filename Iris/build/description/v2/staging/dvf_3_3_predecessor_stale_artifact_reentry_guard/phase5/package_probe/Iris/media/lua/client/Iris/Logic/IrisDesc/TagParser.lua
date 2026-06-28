--[[
    IrisDesc TagParser
    
    태그 검증 및 수집
    
    ⚠️ 헌법:
    - 잘못된 태그 → warn + 무시 + 계속 진행
    - 보정/대체/중단 금지
]]

local Logger = require("Iris/Logic/IrisDesc/Logger")

local IrisDescTagParser = {}


-- 소분류 ID 형식 패턴: {대분류}.{번호}-{코드}
-- 예: Tool.1-A, Combat.2-C, Consumable.3-B
local VALID_PATTERN = "^[A-Za-z]+%.[0-9]+%-[A-Z]$"


---태그가 유효한 소분류 ID인지 검증
---@param tag string 검사할 태그
---@return boolean 유효 여부
function IrisDescTagParser.isValidSubcategoryId(tag)
    if type(tag) ~= "string" then
        return false
    end
    return string.match(tag, VALID_PATTERN) ~= nil
end


---태그 목록에서 유효한 소분류 ID만 수집
---@param tags_iterable table 태그 배열 또는 iterable
---@return table set<string> 형태: { [tag] = true }
function IrisDescTagParser.collect(tags_iterable)
    Logger.debug("[TagParser.collect] ========== START ==========")
    Logger.debug("[TagParser.collect] tags_iterable type = " .. type(tags_iterable))
    
    local result = {}  -- { [tag] = true }
    
    if tags_iterable == nil then
        Logger.debug("[TagParser.collect] tags_iterable is nil, returning empty set")
        Logger.debug("[TagParser.collect] ========== END ==========")
        return result
    end
    
    Logger.debug("[TagParser.collect] tags_iterable count = " .. #tags_iterable)
    
    for i, tag in ipairs(tags_iterable) do
        Logger.debug("[TagParser.collect] Processing tag[" .. i .. "] = '" .. tostring(tag) .. "'")
        Logger.debug("[TagParser.collect]   tag type = " .. type(tag))
        
        if IrisDescTagParser.isValidSubcategoryId(tag) then
            Logger.debug("[TagParser.collect]   VALID - adding to result set")
            result[tag] = true
        else
            -- 잘못된 태그: 경고 + 무시 + 계속
            Logger.debug("[TagParser.collect]   INVALID - skipping (expected format: Category.N-X)")
            Logger.warn("invalid subcategory tag: " .. tostring(tag))
        end
    end
    
    -- 결과 집합 출력
    Logger.debug("[TagParser.collect] Result set contents:")
    local count = 0
    for k, v in pairs(result) do
        count = count + 1
        Logger.debug("[TagParser.collect]   result['" .. k .. "'] = " .. tostring(v))
    end
    Logger.debug("[TagParser.collect] Total valid tags = " .. count)
    Logger.debug("[TagParser.collect] ========== END ==========")
    
    return result
end


---set에 포함된 태그 수 반환
---@param tag_set table { [tag] = true } 형태
---@return number 태그 수
function IrisDescTagParser.count(tag_set)
    local n = 0
    for _ in pairs(tag_set) do
        n = n + 1
    end
    return n
end


---set을 배열로 변환
---@param tag_set table { [tag] = true } 형태
---@return table 태그 배열
function IrisDescTagParser.toArray(tag_set)
    local arr = {}
    for tag in pairs(tag_set) do
        table.insert(arr, tag)
    end
    return arr
end


return IrisDescTagParser

