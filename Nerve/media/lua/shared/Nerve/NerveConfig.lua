--[[
    NerveConfig.lua
    Nerve 모드 설정 파일
    
    v0.1 Final - 이벤트 디스패치 안정화
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
    enabled = true,
    
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
    
    -- 중복 제거 적용 이벤트 (화이트리스트)
    -- targetEvents 중에서도 중복 제거가 안전한 이벤트만
    deduplicateEvents = {
        ["OnContainerUpdate"] = true,
        ["OnInventoryUpdate"] = true,
        -- OnTick은 중복 제거하면 안 됨 (매 틱 호출이 정상)
    },
    
    -- EventDeduplicator 설정
    deduplicator = {
        enabled = true,
        defaultLimit = 1,       -- 틱당 기본 허용 횟수
    },
    
    -- seenThisTick 키 폭증 방지
    maxSeenEntriesPerTick = 1000,
    
    -- CascadeGuard 설정
    cascadeGuard = {
        enabled = false,        -- v0.1: 기본 OFF
        observeOnly = true,     -- 스킵 없이 로그만
        maxDepth = 10,          -- 관측 시에는 높게
    },
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
