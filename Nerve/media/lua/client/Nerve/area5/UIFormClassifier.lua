--[[
    UIFormClassifier.lua
    UI 붕괴 형태 분류
    
    v1.0 - Phase 2-A
    
    핵심 원칙:
    - 의미 판단 X, 중요도 판단 X
    - 형태만 분류 (LIST_BULK / TOOLTIP_CASCADE / CONTAINER_TOGGLE / ITEM_SYNC)
    - Classifier 출력은 sustained 판단 입력으로만 사용
    - 단독 정책 판단 금지
]]

require "Nerve/NerveUtils"

--------------------------------------------------------------------------------
-- UIFormClassifier 모듈
--------------------------------------------------------------------------------

local UIFormClassifier = {}

-- UI 형태 상수
UIFormClassifier.Form = {
    LIST_BULK = "list_bulk",           -- 리스트 대량 갱신
    TOOLTIP_CASCADE = "tooltip_cascade", -- 툴팁 연쇄 생성
    CONTAINER_TOGGLE = "container_toggle", -- 컨테이너 open/close 반복
    ITEM_SYNC = "item_sync",           -- 아이템 상태 동기화 폭주
    GENERIC = "generic",               -- 일반 UI 갱신
}

-- 함수명별 형태 매핑 (관측 데이터 기반 확장)
local functionFormMap = {
    -- 리스트 대량 갱신
    ["refreshBackpack"] = UIFormClassifier.Form.LIST_BULK,
    ["refreshContainer"] = UIFormClassifier.Form.LIST_BULK,
    
    -- 툴팁 연쇄
    ["setTooltip"] = UIFormClassifier.Form.TOOLTIP_CASCADE,
    ["createTooltip"] = UIFormClassifier.Form.TOOLTIP_CASCADE,
    
    -- 컨테이너 토글
    ["openContainer"] = UIFormClassifier.Form.CONTAINER_TOGGLE,
    ["closeContainer"] = UIFormClassifier.Form.CONTAINER_TOGGLE,
    
    -- 아이템 동기화
    ["syncItems"] = UIFormClassifier.Form.ITEM_SYNC,
    ["updateItem"] = UIFormClassifier.Form.ITEM_SYNC,
}

--------------------------------------------------------------------------------
-- 틱 통계
--------------------------------------------------------------------------------

local tickStats = {
    formCounts = {},       -- form -> count this tick
    functionCounts = {},   -- functionName -> count this tick
}

--------------------------------------------------------------------------------
-- 공개 API
--------------------------------------------------------------------------------

-- 틱 시작 시 초기화
function UIFormClassifier.onTickStart()
    NerveUtils.safeWipe(tickStats.formCounts)
    NerveUtils.safeWipe(tickStats.functionCounts)
end

-- 함수 호출 기록
function UIFormClassifier.recordFunction(functionName)
    local count = tickStats.functionCounts[functionName] or 0
    tickStats.functionCounts[functionName] = count + 1
    
    -- 형태별 카운트도 증가
    local form = UIFormClassifier.getForm(functionName)
    local formCount = tickStats.formCounts[form] or 0
    tickStats.formCounts[form] = formCount + 1
end

-- 정적 형태 조회
function UIFormClassifier.getForm(functionName)
    return functionFormMap[functionName] or UIFormClassifier.Form.GENERIC
end

-- 형태별 호출 횟수 조회
function UIFormClassifier.getFormCount(form)
    return tickStats.formCounts[form] or 0
end

-- 특정 형태가 폭주 중인지 확인
function UIFormClassifier.isFormFlooding(form, threshold)
    threshold = threshold or 5
    return UIFormClassifier.getFormCount(form) >= threshold
end

-- 통계 조회
function UIFormClassifier.getStats()
    return {
        formCounts = tickStats.formCounts,
        functionCounts = tickStats.functionCounts,
    }
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.UIFormClassifier = UIFormClassifier

return UIFormClassifier
