--[[
    IrisAltTooltip.lua - Iris 툴팁 오버레이
    
    동작 방식:
    - Alt 키 누름 시에만 상세 정보 표시 (태그, 연결, 더보기 안내)
    - 평상시에는 아무것도 표시하지 않음
    
    ISToolTipInv 구조:
    - self.item: InventoryItem
    - self.tooltip: ObjectTooltip (실제 렌더링 담당)
]]

local IrisAltTooltip = {}

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local ItemKey = require("Iris/Util/ItemKey")
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")
local debug = bootstrap.debug
local warn = bootstrap.warn
local logError = bootstrap.logError

local IrisTooltipSummaryLocal = nil
local displayLineCache = {}
local instrumentationEnabled = false

local function newDisplayLineCacheMetrics()
    return {
        hits = 0,
        misses = 0,
        inactiveRenders = 0,
        summaryLoadAttempts = 0,
        summaryGetCalls = 0,
        temporaryDetailTables = 0,
        displayLineBuilds = 0,
        lineCopies = 0,
    }
end

local displayLineCacheMetrics = newDisplayLineCacheMetrics()

local function tr(key, fallback)
    return TranslationResolver.get(key, fallback or key)
end

local function ensureSummary()
    if not IrisTooltipSummaryLocal then
        if instrumentationEnabled then
            displayLineCacheMetrics.summaryLoadAttempts =
                displayLineCacheMetrics.summaryLoadAttempts + 1
        end
        local ok, result = safeRequire("Iris/UI/Tooltip/IrisTooltipSummary")
        if ok then
            IrisTooltipSummaryLocal = result
        end
    end
    return IrisTooltipSummaryLocal
end

-- Alt 키코드 상수 (LWJGL 키보드 코드)
local KEY_LALT = 56
local KEY_RALT = 184

--- Alt 키 눌림 상태 확인
local function isAltPressed()
    if not isKeyDown then 
        return false 
    end
    local leftAlt = isKeyDown(KEY_LALT)
    local rightAlt = isKeyDown(KEY_RALT)
    return leftAlt or rightAlt
end

local function buildDetailLines(summary)
    if instrumentationEnabled then
        displayLineCacheMetrics.displayLineBuilds =
            displayLineCacheMetrics.displayLineBuilds + 1
        displayLineCacheMetrics.temporaryDetailTables =
            displayLineCacheMetrics.temporaryDetailTables + 1
    end
    if not summary then
        return {
            tr("Iris_Tooltip_Tags", "Tags") .. ": (" .. tr("Iris_Tooltip_ApiLoadFailed", "API load failed") .. ")",
            tr("Iris_Tooltip_More", "More") .. ": " .. tr("Iris_Tooltip_RightClickHint", "Right-click > Iris"),
        }
    end

    local detailLines = {}
    local tagList = summary.tags or {}
    if #tagList > 0 then
        local tagStr = table.concat(tagList, ", ")
        if #tagStr > 50 then
            tagStr = tagStr:sub(1, 47) .. "..."
        end
        table.insert(detailLines, tr("Iris_Tooltip_Tags", "Tags") .. ": " .. tagStr)
    else
        table.insert(detailLines, tr("Iris_Tooltip_Tags", "Tags") .. ": (" .. tr("Iris_Tooltip_None", "None") .. ")")
    end

    local connections = summary.connections or {}
    if #connections > 0 then
        table.insert(detailLines, tr("Iris_Tooltip_Connections", "Connections") .. ": " .. table.concat(connections, ", "))
    else
        table.insert(detailLines, tr("Iris_Tooltip_Connections", "Connections") .. ": " .. tr("Iris_Tooltip_None", "None"))
    end

    local useCaseCount = summary.useCaseCount or 0
    if useCaseCount > 0 then
        table.insert(detailLines, tr("Iris_Tooltip_UseCase", "Use cases") .. ": " .. useCaseCount ..
            tr("Iris_Tooltip_CountSuffix", ""))
    end

    table.insert(detailLines, tr("Iris_Tooltip_More", "More") .. ": " ..
        tr("Iris_Tooltip_RightClickHint", "Right-click > Iris"))
    return detailLines
end

local function getDetailLines(fullType, summary)
    local fullTypeKey = tostring(fullType)
    local localeKey = tostring(TranslationResolver.getLangKey("EN"))
    local revisionKey = tostring(summary and summary.revision or "missing")
    local byLocale = displayLineCache[fullTypeKey]
    if not byLocale then
        byLocale = {}
        displayLineCache[fullTypeKey] = byLocale
    end
    local byRevision = byLocale[localeKey]
    if not byRevision then
        byRevision = {}
        byLocale[localeKey] = byRevision
    end
    local cached = byRevision[revisionKey]
    if cached then
        if instrumentationEnabled then
            displayLineCacheMetrics.hits = displayLineCacheMetrics.hits + 1
        end
        return cached
    end
    if instrumentationEnabled then
        displayLineCacheMetrics.misses = displayLineCacheMetrics.misses + 1
    end
    local lines = buildDetailLines(summary)
    byRevision[revisionKey] = lines
    return lines
end

function IrisAltTooltip.resetDisplayLineCache()
    displayLineCache = {}
    displayLineCacheMetrics = newDisplayLineCacheMetrics()
    if IrisTooltipSummaryLocal and IrisTooltipSummaryLocal.reset then
        IrisTooltipSummaryLocal.reset()
    end
end

function IrisAltTooltip.getDisplayLineCacheMetrics()
    return {
        enabled = instrumentationEnabled,
        hits = displayLineCacheMetrics.hits,
        misses = displayLineCacheMetrics.misses,
        inactiveRenders = displayLineCacheMetrics.inactiveRenders,
        summaryLoadAttempts = displayLineCacheMetrics.summaryLoadAttempts,
        summaryGetCalls = displayLineCacheMetrics.summaryGetCalls,
        temporaryDetailTables = displayLineCacheMetrics.temporaryDetailTables,
        displayLineBuilds = displayLineCacheMetrics.displayLineBuilds,
        lineCopies = displayLineCacheMetrics.lineCopies,
    }
end

function IrisAltTooltip.setInstrumentationEnabled(enabled)
    instrumentationEnabled = enabled == true
    displayLineCacheMetrics = newDisplayLineCacheMetrics()
end

--- 아이템 툴팁에 Iris 정보 추가
--- @param tooltipInv ISToolTipInv
function IrisAltTooltip.addIrisOverlay(tooltipInv)
    -- 중복 삽입 가드
    if tooltipInv._irisRendered then
        return
    end
    tooltipInv._irisRendered = true

    -- The inactive path is called every rendered frame. Leave it before
    -- coordinate setup, temporary arrays, and the summary module boundary.
    local isAlt = isAltPressed()
    if not isAlt then
        if instrumentationEnabled then
            displayLineCacheMetrics.inactiveRenders =
                displayLineCacheMetrics.inactiveRenders + 1
        end
        return
    end
    if not tooltipInv.item then return end

    local summaryModule = ensureSummary()
    local fullType = ItemKey.getFullTypeFromItem(tooltipInv.item)
    if instrumentationEnabled then
        displayLineCacheMetrics.summaryGetCalls =
            displayLineCacheMetrics.summaryGetCalls + 1
    end
    local summary = nil
    if summaryModule then
        if summaryModule._getCached then
            summary = summaryModule._getCached(fullType)
        elseif summaryModule.get then
            summary = summaryModule.get(fullType)
        end
    end
    local detailLines = getDetailLines(fullType, summary)
    if #detailLines == 0 then return end

    local lineHeight = 16
    local x = 10
    local startY = tooltipInv.height

    -- 전체 높이 계산 (상세 정보만)
    local totalLines = #detailLines
    local irisHeight = (lineHeight * totalLines) + 8
    
    -- 배경 색상 (어두운 시안)
    local bgR, bgG, bgB, bgA = 0.05, 0.15, 0.2, 0.9
    -- 상세 텍스트 색상 (밝은 회색)
    local txtR, txtG, txtB, txtA = 0.8, 0.9, 0.9, 1.0
    
    -- 배경 박스 그리기
    tooltipInv:drawRect(0, startY, tooltipInv.width, irisHeight, bgA, bgR, bgG, bgB)
    tooltipInv:drawRectBorder(0, startY, tooltipInv.width, irisHeight, 0.8, 0.4, 0.6, 0.7)
    
    -- 상세 정보 (Alt 눌렀을 때만)
    local currentY = startY + 4
    for _, line in ipairs(detailLines) do
        tooltipInv:drawText(line, x, currentY, txtR, txtG, txtB, txtA, UIFont.Small)
        currentY = currentY + lineHeight
    end
    
    -- 높이 조정
    tooltipInv:setHeight(tooltipInv.height + irisHeight)
end

--- ISToolTipInv.render 후킹
local originalRender = nil
local hooked = false

function IrisAltTooltip.hookTooltip()
    debug("[Iris:hookTooltip] === Starting tooltip hook ===")
    
    if hooked then
        debug("[Iris:hookTooltip] Already hooked, skipping")
        return
    end
    
    if not ISToolTipInv then
        logError("[Iris:hookTooltip] ISToolTipInv is nil")
        return
    end
    
    if not ISToolTipInv.render then
        logError("[Iris:hookTooltip] ISToolTipInv.render is nil")
        return
    end
    
    debug("[Iris:hookTooltip] ISToolTipInv.render found - hooking...")
    originalRender = ISToolTipInv.render
    
    ISToolTipInv.render = function(self)
        -- 매 프레임마다 플래그 리셋
        self._irisRendered = nil
        
        -- 원본 렌더 먼저
        originalRender(self)
        
        -- Iris 오버레이 추가 (항상, Alt 상태에 따라 상세 정보 추가)
        if self.item then
            IrisAltTooltip.addIrisOverlay(self)
        end
    end
    
    hooked = true
    debug("[Iris:hookTooltip] SUCCESS: ISToolTipInv.render hooked!")
end

return IrisAltTooltip
