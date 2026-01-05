--[[
    CascadeGuard.lua
    이벤트 연쇄 깊이 관측
    
    v0.1 Final
    
    핵심 원칙:
    - 기본 OFF (observeOnly = true)
    - 스킵 없이 깊이만 로깅
    - v0.2에서 제어 모드 활성화 예정
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- CascadeGuard 모듈
--------------------------------------------------------------------------------

local CascadeGuard = {}

-- 상태
CascadeGuard.currentDepth = 0
CascadeGuard.maxObservedDepth = 0
CascadeGuard.depthHistogram = {}  -- depth -> count

--------------------------------------------------------------------------------
-- 설정 조회
--------------------------------------------------------------------------------

local function isEnabled()
    return NerveConfig 
        and NerveConfig.area6 
        and NerveConfig.area6.cascadeGuard 
        and NerveConfig.area6.cascadeGuard.enabled
end

local function isObserveOnly()
    if not NerveConfig 
        or not NerveConfig.area6 
        or not NerveConfig.area6.cascadeGuard then
        return true  -- 기본값: 관측만
    end
    return NerveConfig.area6.cascadeGuard.observeOnly ~= false
end

local function getMaxDepth()
    return NerveConfig 
        and NerveConfig.area6 
        and NerveConfig.area6.cascadeGuard 
        and NerveConfig.area6.cascadeGuard.maxDepth 
        or 10
end

--------------------------------------------------------------------------------
-- 깊이 추적
--------------------------------------------------------------------------------

-- 이벤트 진입
-- @param eventName: 이벤트 이름
-- @return: true (진행), false (스킵)
function CascadeGuard.enter(eventName)
    if not isEnabled() then
        return true  -- 비활성화 시 항상 진행
    end
    
    CascadeGuard.currentDepth = CascadeGuard.currentDepth + 1
    local depth = CascadeGuard.currentDepth
    
    -- 히스토그램 기록
    CascadeGuard.depthHistogram[depth] = (CascadeGuard.depthHistogram[depth] or 0) + 1
    
    -- 최대 깊이 갱신
    if depth > CascadeGuard.maxObservedDepth then
        CascadeGuard.maxObservedDepth = depth
        NerveUtils.debug("New max cascade depth: " .. depth .. " (event: " .. eventName .. ")")
    end
    
    -- 관측 모드에서는 항상 진행
    if isObserveOnly() then
        if depth > getMaxDepth() then
            NerveUtils.debug("CASCADE OBSERVE: " .. eventName .. " at depth " .. depth)
        end
        return true
    end
    
    -- 제어 모드: 최대 깊이 초과 시 스킵
    if depth > getMaxDepth() then
        NerveUtils.debug("CASCADE SKIP: " .. eventName .. " at depth " .. depth)
        CascadeGuard.currentDepth = CascadeGuard.currentDepth - 1  -- 롤백
        return false
    end
    
    return true
end

-- 이벤트 종료
function CascadeGuard.exit()
    if not isEnabled() then
        return
    end
    
    CascadeGuard.currentDepth = math.max(0, CascadeGuard.currentDepth - 1)
end

--------------------------------------------------------------------------------
-- 틱 시작 처리
--------------------------------------------------------------------------------

function CascadeGuard.onTickStart()
    -- 틱 시작 시 depth가 0이어야 정상
    if CascadeGuard.currentDepth > 0 then
        NerveUtils.warn("Cascade depth not zero at tick start: " .. CascadeGuard.currentDepth)
        CascadeGuard.currentDepth = 0  -- 강제 리셋
    end
end

--------------------------------------------------------------------------------
-- 통계 조회
--------------------------------------------------------------------------------

function CascadeGuard.getStats()
    return {
        currentDepth = CascadeGuard.currentDepth,
        maxObservedDepth = CascadeGuard.maxObservedDepth,
        depthHistogram = CascadeGuard.depthHistogram,
    }
end

-- 히스토그램 출력
function CascadeGuard.printHistogram()
    NerveUtils.info("Cascade Depth Histogram:")
    for depth = 1, CascadeGuard.maxObservedDepth do
        local count = CascadeGuard.depthHistogram[depth] or 0
        NerveUtils.info("  Depth " .. depth .. ": " .. count)
    end
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.CascadeGuard = CascadeGuard

return CascadeGuard
