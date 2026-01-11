--[[
    EventFormClassifier.lua
    이벤트 폭주 형태 기반 분류
    
    v1.0 - Phase 1-A
    
    핵심 원칙:
    - 의미 판단 X, 중요도 판단 X
    - 형태만 분류 (SINGLE / HIGH_FREQ / CASCADE / FRAME_BOUND)
    - Classifier 출력은 sustained 판단 입력으로만 사용
    - 단독 정책 판단 금지
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- EventFormClassifier 모듈
--------------------------------------------------------------------------------

local EventFormClassifier = {}

-- 이벤트 형태 상수
EventFormClassifier.Form = {
    SINGLE = "single",           -- 단발
    HIGH_FREQ = "high_freq",     -- 고빈도 반복
    CASCADE = "cascade",         -- 연쇄 트리거 (이벤트가 다른 이벤트 유발)
    FRAME_BOUND = "frame_bound", -- 프레임 종속 (렌더/UI 연관)
}

-- 이벤트별 기본 형태 매핑 (관측 데이터 기반 확장)
local eventFormMap = {
    -- 단발 이벤트
    ["OnGameBoot"] = EventFormClassifier.Form.SINGLE,
    ["OnGameStart"] = EventFormClassifier.Form.SINGLE,
    ["OnNewGame"] = EventFormClassifier.Form.SINGLE,
    
    -- 고빈도 반복 이벤트
    ["OnTick"] = EventFormClassifier.Form.HIGH_FREQ,
    ["OnTickEven"] = EventFormClassifier.Form.HIGH_FREQ,
    ["OnTickEvenPaused"] = EventFormClassifier.Form.HIGH_FREQ,
    
    -- 연쇄 트리거 가능 이벤트
    ["OnContainerUpdate"] = EventFormClassifier.Form.CASCADE,
    ["OnInventoryUpdate"] = EventFormClassifier.Form.CASCADE,
    ["OnObjectAdded"] = EventFormClassifier.Form.CASCADE,
    ["OnObjectRemoved"] = EventFormClassifier.Form.CASCADE,
    
    -- 프레임 종속 이벤트
    ["OnPreUIDraw"] = EventFormClassifier.Form.FRAME_BOUND,
    ["OnPostUIDraw"] = EventFormClassifier.Form.FRAME_BOUND,
}

--------------------------------------------------------------------------------
-- 틱 통계 (형태 판단용)
--------------------------------------------------------------------------------

local tickStats = {
    eventCounts = {},      -- eventName -> count this tick
    lastTick = 0,
}

--------------------------------------------------------------------------------
-- 공개 API
--------------------------------------------------------------------------------

-- 틱 시작 시 초기화
function EventFormClassifier.onTickStart()
    NerveUtils.safeWipe(tickStats.eventCounts)
    tickStats.lastTick = tickStats.lastTick + 1
end

-- 이벤트 발생 기록
function EventFormClassifier.recordEvent(eventName)
    local count = tickStats.eventCounts[eventName] or 0
    tickStats.eventCounts[eventName] = count + 1
end

-- 정적 형태 조회 (매핑 기반)
function EventFormClassifier.getStaticForm(eventName)
    return eventFormMap[eventName]
end

-- 동적 형태 판단 (틱 내 발생 패턴 기반)
-- 정적 형태가 없을 때 폴백으로 사용
function EventFormClassifier.getDynamicForm(eventName)
    local count = tickStats.eventCounts[eventName] or 0
    
    -- 고빈도 판단: 틱당 3회 이상이면 HIGH_FREQ로 추정
    if count >= 3 then
        return EventFormClassifier.Form.HIGH_FREQ
    end
    
    -- 기본값: SINGLE
    return EventFormClassifier.Form.SINGLE
end

-- 종합 형태 조회
function EventFormClassifier.getForm(eventName)
    -- 정적 매핑 우선
    local staticForm = EventFormClassifier.getStaticForm(eventName)
    if staticForm then
        return staticForm
    end
    
    -- 동적 판단 폴백
    return EventFormClassifier.getDynamicForm(eventName)
end

-- 형태별 필터링
function EventFormClassifier.isForm(eventName, form)
    return EventFormClassifier.getForm(eventName) == form
end

-- 이벤트가 고빈도인지 확인
function EventFormClassifier.isHighFrequency(eventName)
    local form = EventFormClassifier.getForm(eventName)
    return form == EventFormClassifier.Form.HIGH_FREQ 
        or form == EventFormClassifier.Form.CASCADE
end

-- 통계 조회
function EventFormClassifier.getStats()
    return {
        tickEventCounts = tickStats.eventCounts,
        currentTick = tickStats.lastTick,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.EventFormClassifier = EventFormClassifier

return EventFormClassifier
