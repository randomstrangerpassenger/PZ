--[[
    Area9Forensic.lua
    포렌식 링버퍼 모듈 (숫자만)
    
    [헌법 준수]
    - 고정 크기 링버퍼
    - 레코드: 정수만 (categoryId, reasonCode, tickDelta, aux1, aux2)
    - tick당 1회/카테고리당 1회 레이트리밋
    - 출력 기본 0, 수동 dump만
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- Area9Forensic 모듈
--------------------------------------------------------------------------------

local Area9Forensic = {}

--------------------------------------------------------------------------------
-- Category/ReasonCode enum (정수만)
--------------------------------------------------------------------------------

Area9Forensic.Category = {
    REENTRY = 1,
    DUPLICATE = 2,
    SHAPE_FAIL = 3,
    DEPTH_EXCEED = 4,
    ERROR = 5,
    QUARANTINE = 6,
}

Area9Forensic.ReasonCode = {
    -- Reentry
    REENTRY_DETECTED = 101,
    REENTRY_BYPASS = 102,
    
    -- Duplicate
    DUP_COUNT_HIGH = 201,
    
    -- Shape
    SHAPE_HARD_FAIL = 301,
    SHAPE_SOFT_FAIL = 302,
    
    -- Depth
    DEPTH_EXCEED_ENTER = 401,
    DEPTH_EXCEED_EXIT = 402,
    
    -- Error
    ERROR_PCALL = 501,
    ERROR_HANDLER_NIL = 502,
    
    -- Quarantine
    QUARANTINE_ENTER = 601,
    QUARANTINE_EXIT = 602,
}

--------------------------------------------------------------------------------
-- 링버퍼
--------------------------------------------------------------------------------

-- 버퍼 크기 (config에서 가져옴, 기본 128)
local function getBufferSize()
    return NerveConfig 
        and NerveConfig.area9 
        and NerveConfig.area9.forensic 
        and NerveConfig.area9.forensic.ringBufferSize 
        or 128
end

-- 링버퍼 저장소
Area9Forensic.buffer = {}
Area9Forensic.bufferHead = 0  -- 다음 쓰기 위치
Area9Forensic.bufferCount = 0 -- 현재 저장된 레코드 수

-- 레이트리밋 상태 (tick-local)
Area9Forensic.rateLimitState = {}
Area9Forensic.lastWipeTick = 0

--------------------------------------------------------------------------------
-- 틱 관리
--------------------------------------------------------------------------------

local function ensureCurrentTick()
    local TickCtx = Nerve.Area9TickCtx
    local currentTick = TickCtx and TickCtx.getCurrentTickId() or 0
    
    if currentTick ~= Area9Forensic.lastWipeTick then
        NerveUtils.safeWipe(Area9Forensic.rateLimitState)
        Area9Forensic.lastWipeTick = currentTick
    end
end

--------------------------------------------------------------------------------
-- 레코드 추가
--------------------------------------------------------------------------------

-- 레코드 구조: { categoryId, reasonCode, tickDelta, aux1, aux2 }
-- @param categoryId: Category enum
-- @param reasonCode: ReasonCode enum
-- @param aux1: 보조 데이터 1 (정수)
-- @param aux2: 보조 데이터 2 (정수)
function Area9Forensic.record(categoryId, reasonCode, aux1, aux2)
    ensureCurrentTick()
    
    -- 레이트리밋 체크 (카테고리당 tick 1회)
    local rateLimitKey = categoryId
    if Area9Forensic.rateLimitState[rateLimitKey] then
        return false  -- 이미 이 tick에 기록됨
    end
    Area9Forensic.rateLimitState[rateLimitKey] = true
    
    -- tickDelta 계산
    local TickCtx = Nerve.Area9TickCtx
    local currentTick = TickCtx and TickCtx.getCurrentTickId() or 0
    local prevTick = TickCtx and TickCtx.prevTickId or 0
    local tickDelta = currentTick - prevTick
    
    -- 레코드 생성 (정수만)
    local record = {
        categoryId or 0,
        reasonCode or 0,
        tickDelta or 0,
        aux1 or 0,
        aux2 or 0,
    }
    
    -- 링버퍼에 추가
    local bufferSize = getBufferSize()
    Area9Forensic.bufferHead = (Area9Forensic.bufferHead % bufferSize) + 1
    Area9Forensic.buffer[Area9Forensic.bufferHead] = record
    
    if Area9Forensic.bufferCount < bufferSize then
        Area9Forensic.bufferCount = Area9Forensic.bufferCount + 1
    end
    
    return true
end

--------------------------------------------------------------------------------
-- Dump (수동 출력만)
--------------------------------------------------------------------------------

-- 버퍼 내용 덤프 (출력 기본 0, 수동 호출 시에만)
function Area9Forensic.dump()
    if Area9Forensic.bufferCount == 0 then
        NerveUtils.info("[Area9Forensic] Buffer empty")
        return {}
    end
    
    local results = {}
    local bufferSize = getBufferSize()
    
    -- 가장 오래된 것부터 순서대로
    local startIdx = (Area9Forensic.bufferHead - Area9Forensic.bufferCount + bufferSize) % bufferSize + 1
    
    for i = 0, Area9Forensic.bufferCount - 1 do
        local idx = ((startIdx + i - 1) % bufferSize) + 1
        local record = Area9Forensic.buffer[idx]
        if record then
            table.insert(results, {
                categoryId = record[1],
                reasonCode = record[2],
                tickDelta = record[3],
                aux1 = record[4],
                aux2 = record[5],
            })
        end
    end
    
    NerveUtils.info("[Area9Forensic] Dumped " .. #results .. " records")
    return results
end

-- 버퍼 통계
function Area9Forensic.getStats()
    return {
        count = Area9Forensic.bufferCount,
        capacity = getBufferSize(),
        head = Area9Forensic.bufferHead,
    }
end

-- 버퍼 초기화
function Area9Forensic.clear()
    NerveUtils.safeWipe(Area9Forensic.buffer)
    Area9Forensic.bufferHead = 0
    Area9Forensic.bufferCount = 0
    NerveUtils.safeWipe(Area9Forensic.rateLimitState)
end

--------------------------------------------------------------------------------
-- 편의 함수 (카테고리별)
--------------------------------------------------------------------------------

function Area9Forensic.recordReentry(reasonCode, aux1, aux2)
    return Area9Forensic.record(Area9Forensic.Category.REENTRY, reasonCode, aux1, aux2)
end

function Area9Forensic.recordDuplicate(reasonCode, aux1, aux2)
    return Area9Forensic.record(Area9Forensic.Category.DUPLICATE, reasonCode, aux1, aux2)
end

function Area9Forensic.recordShapeFail(reasonCode, aux1, aux2)
    return Area9Forensic.record(Area9Forensic.Category.SHAPE_FAIL, reasonCode, aux1, aux2)
end

function Area9Forensic.recordDepthExceed(reasonCode, aux1, aux2)
    return Area9Forensic.record(Area9Forensic.Category.DEPTH_EXCEED, reasonCode, aux1, aux2)
end

function Area9Forensic.recordError(reasonCode, aux1, aux2)
    return Area9Forensic.record(Area9Forensic.Category.ERROR, reasonCode, aux1, aux2)
end

function Area9Forensic.recordQuarantine(reasonCode, aux1, aux2)
    return Area9Forensic.record(Area9Forensic.Category.QUARANTINE, reasonCode, aux1, aux2)
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Area9Forensic = Area9Forensic

return Area9Forensic
