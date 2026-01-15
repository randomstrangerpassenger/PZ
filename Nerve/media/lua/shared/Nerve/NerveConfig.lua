--[[
    NerveConfig.lua
    Nerve 모드 설정 파일
    
    v0.2 - Area 5 제거됨 (폐기)
]]

NerveConfig = NerveConfig or {}

--------------------------------------------------------------------------------
-- 기본 설정
--------------------------------------------------------------------------------

-- Pulse 모드 ID (대소문자/폴더명 변경 대비)
NerveConfig.pulseModId = "Pulse"

-- 디버그 모드 (로그 상세 출력)
NerveConfig.debug = false

--------------------------------------------------------------------------------
-- Area 6: 이벤트 디스패치 안정화
--------------------------------------------------------------------------------

NerveConfig.area6 = {
    -- 활성화 여부
    -- [SEALED] DEFAULT OFF: 바닐라 동일 보장 (헌법 준수)
    enabled = false,
    
    -- 래핑 대상 이벤트 목록 (최소 5~10개로 제한)
    -- "재현된 폭주가 확인된" 이벤트만 추가
    -- 과다 등록 금지: 전 이벤트 래핑은 그 자체가 리스크
    targetEvents = {
        "OnTick",
        "OnTickEvenPaused",
        "OnContainerUpdate",
        "OnInventoryUpdate",
        "OnObjectAdded",
        "OnObjectRemoved",
        -- 추후 관측 데이터 기반으로 확장
    },
    
    -- 기술적 안정성 목적 중복 제거 대상 이벤트 집합
    -- (이벤트 의미 기반 선별이 아닌, contextKey 존재 + 동일 틱 중복 제거 가능)
    deduplicateEvents = {
        ["OnContainerUpdate"] = true,
        ["OnInventoryUpdate"] = true,
        -- OnTick은 중복 제거하면 안 됨 (매 틱 호출이 정상)
    },
    
    -- EventRecursionGuard 설정 (관측 전용)
    -- [FIX] strict 옵션 제거 - Drop 금지 원칙 준수
    recursionGuard = {
        enabled = true,         -- 관측은 항상 활성화
        maxDepth = 5000,        -- 폭주 임계값 (경고 로그 기준)
    },
    
    -- seenThisTick 키 폭증 방지
    maxSeenEntriesPerTick = 1000,
    
    -- CascadeGuard 설정 (관측 전용)
    -- [FIX] strict 옵션 제거 - Drop 금지 원칙 준수
    cascadeGuard = {
        enabled = false,        -- 기본 OFF
        observeOnly = true,     -- 항상 관측 전용
        maxDepth = 10,          -- 경고 로그 기준
    },
    
    -- [REMOVED] 정책성 컴포넌트 설정 제거 (헌법 준수)
    -- sustainedPressure, earlyExit는 더 이상 사용되지 않음
}

--------------------------------------------------------------------------------
-- Fail-soft 설정
--------------------------------------------------------------------------------

NerveConfig.failsoft = {
    -- 최대 연속 오류 횟수 (초과 시 컴포넌트 비활성화)
    maxErrors = 3,
    -- 비활성화 후 cooldown (ms)
    cooldownMs = 10000,  -- 10초
}

--------------------------------------------------------------------------------
-- 타이밍 설정
--------------------------------------------------------------------------------

NerveConfig.timing = {
    -- 느린 틱 판정 기준 (ms)
    slowThresholdMs = 50,  -- 20fps 미만
}

--------------------------------------------------------------------------------
-- 유틸리티
--------------------------------------------------------------------------------

-- 설정값 안전 조회
function NerveConfig.get(path, default)
    local parts = {}
    for part in string.gmatch(path, "[^.]+") do
        table.insert(parts, part)
    end
    
    local current = NerveConfig
    for _, part in ipairs(parts) do
        if type(current) ~= "table" then
            return default
        end
        current = current[part]
    end
    
    if current == nil then
        return default
    end
    return current
end

return NerveConfig
