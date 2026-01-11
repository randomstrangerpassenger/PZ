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
    
    -- 기술적 안정성 목적 중복 제거 대상 이벤트 집합
    -- (이벤트 의미 기반 선별이 아닌, contextKey 존재 + 동일 틱 중복 제거 가능)
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
    
    -- [Phase 1-B] Sustained Event Pressure 감지
    -- 느림 판정: Lua wall-clock delta (os.clock() 기반, 추세 판단용)
    sustainedPressure = {
        enabled = false,        -- opt-in 기본 OFF
        windowMs = 100,         -- 압력 감지 창 (ms)
        threshold = 5,          -- 창 내 동일 이벤트 임계값
    },
    
    -- [Phase 1-D] Early Exit & Cooldown
    -- Fuse 철학 차용, 구현은 Nerve
    earlyExit = {
        enabled = false,        -- opt-in 기본 OFF
        activeMaxMs = 500,      -- ACTIVE 최대 지속 시간
        cooldownMs = 1000,      -- COOLDOWN 지속 시간
    },
}

--------------------------------------------------------------------------------
-- Area 5: UI/인벤토리 안정화
-- "데이터는 즉시, 시각은 모아서"
--------------------------------------------------------------------------------

NerveConfig.area5 = {
    -- 활성화 여부
    enabled = true,
    
    -- InventoryGuard: refreshBackpack 틱 단위 coalesce
    inventoryGuard = {
        enabled = true,
    },
    
    -- UIRefreshCoalescer: 범용 UI 갱신 합치기
    uiCoalesce = {
        enabled = true,
        maxPanelsPerTick = 50,      -- 폭주 방지 상한
        overflowBehavior = "bypass", -- bypass: coalesce 포기 후 즉시 실행
        -- defer: ❌ 금지 (틱 넘김 = 캐시)
        -- drop: ❌ 금지 (UI 누락 = 의미 변화)
    },
    
    -- ContainerScanDedup: 컨테이너 스캔 중복 제거
    containerScan = {
        enabled = true,
    },
    
    -- 지연 초기화 재시도
    retryInit = {
        enabled = true,
        maxRetries = 3,
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
