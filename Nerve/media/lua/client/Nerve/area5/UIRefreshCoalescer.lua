--[[
    UIRefreshCoalescer.lua
    범용 UI 갱신 합치기
    
    v0.1 Final
    
    원칙:
    - 틱 내 중복 패널 갱신 합치기
    - overflow 시 bypass (defer/drop 금지)
    - 스냅샷 패턴 (순회 중 삭제 안전)
]]

require "Nerve/NerveUtils"
require "Nerve/area5/Area5Stats"

local UIRefreshCoalescer = {}

UIRefreshCoalescer.pendingRefresh = {}      -- { panelId: true }
UIRefreshCoalescer.refreshedThisTick = {}   -- 이미 갱신된 패널
UIRefreshCoalescer.MAX = 50                 -- NerveConfig에서 로드

--------------------------------------------------------------------------------
-- 갱신 요청
--------------------------------------------------------------------------------

-- 패널 갱신 요청
-- @param panelId: 패널 식별자
-- @return: true (요청 성공), false (이미 갱신됨)
function UIRefreshCoalescer.requestRefresh(panelId)
    if not NerveConfig.area5 or not NerveConfig.area5.uiCoalesce 
        or not NerveConfig.area5.uiCoalesce.enabled then
        return true  -- 비활성화 시 항상 허용
    end
    
    -- 이번 틱에 이미 갱신됨
    if UIRefreshCoalescer.refreshedThisTick[panelId] then
        if NerveConfig.debug then
            NerveUtils.debug("Area5: SKIP duplicate refresh - " .. tostring(panelId))
        end
        return false
    end
    
    UIRefreshCoalescer.pendingRefresh[panelId] = true
    return true
end

--------------------------------------------------------------------------------
-- 플러시
--------------------------------------------------------------------------------

-- pending 갱신 실행
-- @param executeFn: 실행 함수 (optional, nil이면 NOP)
function UIRefreshCoalescer.flush(executeFn)
    -- executeFn optional (fail-soft)
    if not executeFn then
        NerveUtils.safeWipe(UIRefreshCoalescer.pendingRefresh)
        return
    end
    
    -- 설정에서 MAX 로드
    local max = UIRefreshCoalescer.MAX
    if NerveConfig.area5 and NerveConfig.area5.uiCoalesce then
        max = NerveConfig.area5.uiCoalesce.maxPanelsPerTick or max
    end
    
    -- 스냅샷 패턴 (순회 중 삭제 안전)
    local ids = {}
    for panelId in pairs(UIRefreshCoalescer.pendingRefresh) do
        table.insert(ids, panelId)
    end
    
    local count = 0
    for _, panelId in ipairs(ids) do
        if count >= max then
            -- overflow: bypass (coalesce 포기, 남은 것 즉시 실행)
            Area5Stats.overflowCount = Area5Stats.overflowCount + 1
            NerveUtils.warn("Area5: Overflow (" .. #ids .. " panels), bypassing coalesce")
            
            for i = count + 1, #ids do
                pcall(executeFn, ids[i])
            end
            break
        end
        
        local ok, err = pcall(executeFn, panelId)
        if ok then
            UIRefreshCoalescer.refreshedThisTick[panelId] = true
        else
            NerveUtils.warn("Area5: Flush error - " .. tostring(err))
        end
        count = count + 1
    end
    
    NerveUtils.safeWipe(UIRefreshCoalescer.pendingRefresh)
end

--------------------------------------------------------------------------------
-- 틱 초기화
--------------------------------------------------------------------------------

function UIRefreshCoalescer.onTickStart()
    NerveUtils.safeWipe(UIRefreshCoalescer.refreshedThisTick)
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.UIRefreshCoalescer = UIRefreshCoalescer

return UIRefreshCoalescer
