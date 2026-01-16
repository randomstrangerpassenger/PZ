--[[
    CascadeGuard.lua
    이벤트 연쇄 깊이 관측 (관측 전용)
    
    ┌──────────────────────────────────────────────────────────────────────────┐
    │ ⚠️ DEPRECATED - DO NOT USE                                              │
    │                                                                          │
    │ This module is superseded by Area6Depth.lua (evidence-only)              │
    │ Kept only for backward compatibility. Will be removed in future version. │
    └──────────────────────────────────────────────────────────────────────────┘
    
    v0.3 - Pure Observation Mode (헌법 준수)
    
    핵심 원칙:
    - 항상 통과 (Drop 금지 원칙 준수)
    - 깊이 초과 시 경고 로그만 출력
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
-- @return: true (항상 통과 - Drop 금지 원칙)
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
    
    -- 최대 깊이 초과 시 경고 로그만 (관측 전용)
    if depth > getMaxDepth() then
        NerveUtils.warn("CASCADE: " .. eventName .. " depth=" .. depth .. " (observe-only)")
    end
    
    return true  -- [FIX] 항상 통과 (Drop 금지 원칙)
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
