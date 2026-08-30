-- Alt-only presentation of complete T2 rows. Vanilla owns the base tooltip.
local IrisAltTooltip = {}
local ItemKey = require("Iris/Util/ItemKey")
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local Lookup = require("Iris/Data/IrisTooltipT2Lookup")
local instrumentationEnabled = false

local function newMetrics()
    return {
        inactiveRenders=0, fullTypeResolutions=0, localeResolutions=0, staticLookups=0,
        -- Retained observation names are zero: no display cache or summary state.
        hits=0, misses=0, summaryLoadAttempts=0, summaryGetCalls=0,
        temporaryDetailTables=0, displayLineBuilds=0, lineCopies=0,
        keyStringConversions=0, detailLineCacheLookups=0, cacheEntryAllocations=0,
        retainedFullTypeEntries=0, retainedProjectionEntries=0,
    }
end
local metrics = newMetrics()
function IrisAltTooltip.resetDisplayLineCache() metrics = newMetrics() end
function IrisAltTooltip.setInstrumentationEnabled(enabled)
    instrumentationEnabled = enabled == true
    metrics = newMetrics()
end
function IrisAltTooltip.getDisplayLineCacheMetrics()
    local copy = {enabled=instrumentationEnabled}
    for key, value in pairs(metrics) do copy[key]=value end
    return copy
end

local function restoreHeight(tip)
    if tip._irisBaseHeight and tip.height == tip._irisAppliedHeight then
        tip:setHeight(tip._irisBaseHeight)
    end
    tip._irisBaseHeight, tip._irisAppliedHeight = nil, nil
end

-- Engine-measured wrapping on UTF-8 boundaries. Every byte stays in order,
-- including whitespace; only physical drawing runs are split.
local function wrapRow(text, width, manager, font, lines)
    local ends = {}
    for i=1,#text do
        local following = text:byte(i+1)
        if not following or following < 128 or following >= 192 then ends[#ends+1]=i end
    end
    local first, startByte = 1, 1
    while first <= #ends do
        local low, high, fit = first, #ends, first-1
        while low <= high do
            local middle = math.floor((low+high)/2)
            if manager:MeasureStringX(font, text:sub(startByte, ends[middle])) <= width then
                fit=middle; low=middle+1
            else high=middle-1 end
        end
        if fit < first then return false end
        if fit < #ends then
            for i=fit,first,-1 do
                if text:sub(ends[i],ends[i]):match("%s") then fit=i; break end
            end
        end
        lines[#lines+1]=text:sub(startByte, ends[fit])
        startByte=ends[fit]+1
        first=fit+1
    end
    return true
end

local function addOverlay(tip)
    -- No item, locale, payload, or row work while Alt is released.
    if not isKeyDown or not (isKeyDown(56) or isKeyDown(184)) then
        if instrumentationEnabled then metrics.inactiveRenders=metrics.inactiveRenders+1 end
        return
    end
    if not tip.item then return end
    if instrumentationEnabled then metrics.fullTypeResolutions=metrics.fullTypeResolutions+1 end
    local fullType = ItemKey.getFullTypeFromItem(tip.item)
    if instrumentationEnabled then metrics.localeResolutions=metrics.localeResolutions+1 end
    local key = TranslationResolver.getDetectedLangKey()
    local locale = key == "KO" and "ko" or key == "EN" and "en" or nil
    if not locale or type(fullType) ~= "string" or fullType == "" then return end
    if instrumentationEnabled then metrics.staticLookups=metrics.staticLookups+1 end
    local rows = Lookup.get(fullType, locale)
    if not rows or #rows == 0 then return end

    local manager, font = getTextManager(), UIFont.Small
    local lineHeight = manager:getFontHeight(font)
    if type(lineHeight) ~= "number" or lineHeight <= 0 then return end
    local core = getCore()
    local screenWidth, screenHeight = core:getScreenWidth(), core:getScreenHeight()
    local absoluteX, absoluteY = tip:getAbsoluteX(), tip:getAbsoluteY()
    local width = math.min(tip.width, screenWidth)
    if width <= 20 then return end
    local lines = {}
    for i=1,#rows do
        if not wrapRow(rows[i], width-20, manager, font, lines) then return end
    end
    local blockHeight = #lines * lineHeight + 8
    local x = math.max(0, math.min(absoluteX, screenWidth-width)) - absoluteX
    local y = tip.height
    if absoluteY+y+blockHeight > screenHeight then
        -- Vanilla was already drawn. Place Iris above without moving vanilla.
        y = -blockHeight
        if absoluteY+y < 0 then return end
    end
    if y >= 0 then
        tip._irisBaseHeight = tip.height
        tip._irisAppliedHeight = tip.height+blockHeight
        tip:setHeight(tip._irisAppliedHeight)
    end
    tip:drawRect(x,y,width,blockHeight,0.9,0.05,0.15,0.2)
    tip:drawRectBorder(x,y,width,blockHeight,0.8,0.4,0.6,0.7)
    for i=1,#lines do
        tip:drawText(lines[i],x+10,y+4+(i-1)*lineHeight,0.8,0.9,0.9,1.0,font)
    end
end

function IrisAltTooltip.addIrisOverlay(tip)
    if tip._irisRendered then return end
    tip._irisRendered = true
    local ok = ProtectedCall.call(addOverlay, tip)
    if not ok then ProtectedCall.call(restoreHeight, tip) end
end

local hooked = false
function IrisAltTooltip.hookTooltip()
    if hooked or not ISToolTipInv or type(ISToolTipInv.render) ~= "function" then return end
    local originalRender = ISToolTipInv.render
    ISToolTipInv.render = function(self)
        ProtectedCall.call(restoreHeight, self)
        self._irisRendered = nil
        -- Vanilla errors remain visible; only Iris is isolated.
        originalRender(self)
        IrisAltTooltip.addIrisOverlay(self)
    end
    hooked = true
end

return IrisAltTooltip