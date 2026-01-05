--[[
    EventDeduplicator.lua
    틱 단위 이벤트 중복 제거
    
    v0.1 Final
    
    핵심 원칙:
    - contextKey가 nil이면 중복 체크 건너뛰기 (항상 실행)
    - seenThisTick 키 폭증 방지 (maxSeenEntriesPerTick)
    - table.wipe 폴백 사용
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- EventDeduplicator 모듈
--------------------------------------------------------------------------------

local EventDeduplicator = {}

-- 상태
EventDeduplicator.seenThisTick = {}
EventDeduplicator.entryCount = 0
EventDeduplicator.skipCount = 0
EventDeduplicator.totalCount = 0

--------------------------------------------------------------------------------
-- 틱 시작 처리
--------------------------------------------------------------------------------

function EventDeduplicator.onTickStart()
    -- 통계 기록 (디버그용)
    if NerveConfig and NerveConfig.debug and EventDeduplicator.skipCount > 0 then
        NerveUtils.debug("Dedup stats: total=" .. EventDeduplicator.totalCount 
            .. ", skipped=" .. EventDeduplicator.skipCount
            .. ", entries=" .. EventDeduplicator.entryCount)
    end
    
    -- 테이블 초기화 (재사용)
    NerveUtils.safeWipe(EventDeduplicator.seenThisTick)
    EventDeduplicator.entryCount = 0
    EventDeduplicator.skipCount = 0
    EventDeduplicator.totalCount = 0
end

--------------------------------------------------------------------------------
-- 중복 체크
--------------------------------------------------------------------------------

-- 이벤트를 스킵해야 하는지 판단
-- @param eventName: 이벤트 이름
-- @param contextKey: 컨텍스트 키 (nil이면 항상 실행)
-- @return: true (스킵), false (실행)
function EventDeduplicator.shouldSkip(eventName, contextKey)
    EventDeduplicator.totalCount = EventDeduplicator.totalCount + 1
    
    -- contextKey가 nil이면 중복 체크 안 함 (항상 실행)
    -- 이는 Entity Event 안전을 위한 핵심 로직
    if contextKey == nil then
        return false
    end
    
    -- 화이트리스트 체크
    local deduplicateEvents = NerveConfig 
        and NerveConfig.area6 
        and NerveConfig.area6.deduplicateEvents
    
    if deduplicateEvents and not deduplicateEvents[eventName] then
        -- 화이트리스트에 없으면 항상 실행
        return false
    end
    
    -- 키 폭증 방지
    local maxEntries = NerveConfig 
        and NerveConfig.area6 
        and NerveConfig.area6.maxSeenEntriesPerTick 
        or 1000
    
    if EventDeduplicator.entryCount >= maxEntries then
        if NerveConfig and NerveConfig.debug then
            NerveUtils.debug("WARN: seenThisTick limit reached, dedup disabled for this tick")
        end
        return false  -- 안전하게 통과
    end
    
    -- 키 생성
    local key = eventName .. ":" .. contextKey
    local count = EventDeduplicator.seenThisTick[key]
    
    -- 첫 등장 시 카운터 증가
    if count == nil then
        EventDeduplicator.entryCount = EventDeduplicator.entryCount + 1
        count = 0
    end
    
    -- 허용 횟수 확인
    local limit = NerveConfig 
        and NerveConfig.area6 
        and NerveConfig.area6.deduplicator 
        and NerveConfig.area6.deduplicator.defaultLimit 
        or 1
    
    if count >= limit then
        -- 중복 감지 - 스킵
        EventDeduplicator.skipCount = EventDeduplicator.skipCount + 1
        
        if NerveConfig and NerveConfig.debug then
            NerveUtils.debug("SKIP: " .. key .. " (count=" .. count .. ")")
        end
        
        return true
    end
    
    -- 카운트 증가 후 실행 허용
    EventDeduplicator.seenThisTick[key] = count + 1
    return false
end

--------------------------------------------------------------------------------
-- 통계 조회
--------------------------------------------------------------------------------

function EventDeduplicator.getStats()
    return {
        totalCount = EventDeduplicator.totalCount,
        skipCount = EventDeduplicator.skipCount,
        entryCount = EventDeduplicator.entryCount,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.EventDeduplicator = EventDeduplicator

return EventDeduplicator
