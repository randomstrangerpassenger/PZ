--[[
    Area6ErrorSig.lua
    에러 서명(Signature) 정규화 모듈
    
    v1.0 - Phase 3: Fail-Soft Isolation
    
    핵심 역할:
    - 에러 메시지에서 고유 서명 추출
    - 레이트리밋용 키 생성
    - 스택트레이스 정규화
    
    [CONSTITUTION 준수]
    - 누적 통계 없음 (서명 생성만)
    - 의미 분석/분류 없음
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- Area6ErrorSig 모듈
--------------------------------------------------------------------------------

local Area6ErrorSig = {}

--------------------------------------------------------------------------------
-- 서명 생성
--------------------------------------------------------------------------------

-- 에러 메시지에서 서명 추출
-- @param errMsg: 에러 메시지 문자열
-- @return: 정규화된 서명 문자열
function Area6ErrorSig.extractSignature(errMsg)
    if type(errMsg) ~= "string" then
        return "unknown"
    end
    
    -- 1. 파일명:라인번호 패턴 추출
    -- 예: "...Nerve/area6/Test.lua:123: error message"
    local filePattern = "([^/\\]+%.lua):(%d+)"
    local fileName, lineNum = string.match(errMsg, filePattern)
    
    if fileName and lineNum then
        -- 2. 에러 메시지 첫 50자 (변수/숫자 제거)
        local msgStart = string.sub(errMsg, 1, 50)
        -- 숫자를 # 으로 대체 (variant 제거)
        msgStart = string.gsub(msgStart, "%d+", "#")
        -- 따옴표 내용 제거
        msgStart = string.gsub(msgStart, "'[^']*'", "'...'")
        msgStart = string.gsub(msgStart, '"[^"]*"', '"..."')
        
        return fileName .. ":" .. lineNum .. ":" .. msgStart
    end
    
    -- 파일 패턴 없으면 메시지 해시
    local msgStart = string.sub(errMsg, 1, 80)
    msgStart = string.gsub(msgStart, "%d+", "#")
    return "msg:" .. msgStart
end

-- 레이트리밋 키 생성
-- @param eventName: 이벤트 이름
-- @param listenerId: 리스너 식별자
-- @param errSig: 에러 서명
-- @return: 레이트리밋 키
function Area6ErrorSig.makeRateLimitKey(eventName, listenerId, errSig)
    return eventName .. "|" .. tostring(listenerId) .. "|" .. errSig
end

--------------------------------------------------------------------------------
-- 스택트레이스 정규화
--------------------------------------------------------------------------------

-- 스택트레이스에서 관련 라인만 추출
-- @param fullStack: 전체 스택트레이스
-- @param maxLines: 최대 라인 수 (기본: 5)
-- @return: 정규화된 스택 문자열
function Area6ErrorSig.normalizeStack(fullStack, maxLines)
    if type(fullStack) ~= "string" then
        return ""
    end
    
    maxLines = maxLines or 5
    local lines = {}
    local count = 0
    
    for line in string.gmatch(fullStack, "[^\n]+") do
        -- Nerve 내부 라인 제외 (사용자 코드에 집중)
        if not string.find(line, "Area6") 
            and not string.find(line, "NerveUtils") then
            count = count + 1
            if count <= maxLines then
                table.insert(lines, line)
            end
        end
    end
    
    return table.concat(lines, "\n")
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area6ErrorSig = Area6ErrorSig

return Area6ErrorSig
