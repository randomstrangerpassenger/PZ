-- Alt-only presentation of complete static rows. Vanilla owns the base tooltip.
local IrisAltTooltip = {}
local ItemKey = require("Iris/Util/ItemKey")
local TranslationResolver = require("Iris/Util/IrisTranslationResolver")
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local Lookup = require("Iris/Data/IrisTooltipStaticDataLookup")
local instrumentationEnabled = false

local function newMetrics()
    return {
        inactiveRenders=0, fullTypeResolutions=0, localeResolutions=0, staticLookups=0,
        -- No FullType-indexed display cache or legacy summary state. The tip
        -- retains only its current opening's bilingual view until it closes.
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
        tip._irisOpening = nil
        if instrumentationEnabled then metrics.inactiveRenders=metrics.inactiveRenders+1 end
        return
    end
    if not tip.item or (ISContextMenu and ISContextMenu.instance and ISContextMenu.instance.visibleCheck) then
        tip._irisOpening = nil
        return
    end
    if instrumentationEnabled then metrics.fullTypeResolutions=metrics.fullTypeResolutions+1 end
    local fullType = ItemKey.getFullTypeFromItem(tip.item)
    if instrumentationEnabled then metrics.localeResolutions=metrics.localeResolutions+1 end
    local key = TranslationResolver.getDetectedLangKey()
    local locale = key == "KO" and "ko" or key == "EN" and "en" or nil
    if not locale or type(fullType) ~= "string" or fullType == "" then return end
    local opening = tip._irisOpening
    if not opening or opening.item ~= tip.item or opening.fullType ~= fullType then
        if instrumentationEnabled then metrics.staticLookups=metrics.staticLookups+1 end
        opening = {item=tip.item, fullType=fullType}
        tip._irisOpening = opening
        opening.view = Lookup.open(fullType, function(count)
            if ZombRand then return ZombRand(count)+1 end
            return math.random(count)
        end)
    end
    local rows = opening.view and opening.view[locale]
    if not rows or #rows == 0 then return end

    local manager, font = getTextManager(), UIFont.Small
    local lineHeight = manager:getFontHeight(font)
    if type(lineHeight) ~= "number" or lineHeight <= 0 then return end
    local core = getCore()
    local screenWidth, screenHeight = core:getScreenWidth(), core:getScreenHeight()
    local absoluteX, absoluteY = tip:getAbsoluteX(), tip:getAbsoluteY()
    -- A separate reading panel, independent of vanilla's often narrow width.
    local gap, minWidth, maxWidth = 4, 240, 360
    -- PZ's rendered glyphs can extend slightly beyond MeasureStringX at some
    -- UI scales. Keep scale-aware breathing room inside the panel and wrap
    -- before the measured edge instead of letting the final glyph be clipped.
    local paddingX = math.max(14, math.ceil(lineHeight * 0.9))
    local paddingY = math.max(5, math.ceil(lineHeight * 0.35))
    local measurementSlack = math.max(8, math.ceil(lineHeight * 0.75))
    local contentWidth = 0
    for i=1,#rows do
        contentWidth = math.max(contentWidth, manager:MeasureStringX(font, rows[i]))
    end
    local width = math.min(math.min(math.max(contentWidth+paddingX*2+measurementSlack, minWidth), maxWidth), screenWidth)
    local rightSpace = screenWidth - (absoluteX+tip.width+gap)
    local leftSpace = absoluteX-gap
    local x, side
    if rightSpace >= width then
        x, side = tip.width+gap, true
    elseif leftSpace >= width then
        x, side = -width-gap, true
    elseif math.max(rightSpace, leftSpace) >= minWidth then
        -- Keep the panel alongside vanilla when a readable narrower panel fits.
        if rightSpace >= leftSpace then
            width = math.min(width, rightSpace)
            x = tip.width+gap
        else
            width = math.min(width, leftSpace)
            x = -width-gap
        end
        side = true
    else
        -- Very narrow viewports: use vertical placement only as a last resort.
        x = math.max(0, math.min(absoluteX, screenWidth-width)) - absoluteX
    end
    local wrapWidth = width-paddingX*2-measurementSlack
    if wrapWidth <= 0 then return end
    local lines = {}
    for i=1,#rows do
        if not wrapRow(rows[i], wrapWidth, manager, font, lines) then return end
    end
    local blockHeight = #lines * lineHeight + paddingY*2
    if blockHeight > screenHeight then return end
    local y
    if side then
        -- Top aligned unless the screen bottom requires moving only Iris up.
        y = math.max(0, math.min(absoluteY, screenHeight-blockHeight)) - absoluteY
    else
        y = tip.height+gap
        if absoluteY+y < 0 or absoluteY+y+blockHeight > screenHeight then
            y = -blockHeight-gap
            if absoluteY+y < 0 or absoluteY+y+blockHeight > screenHeight then return end
        end
    end
    tip:drawRect(x,y,width,blockHeight,0.9,0.05,0.15,0.2)
    tip:drawRectBorder(x,y,width,blockHeight,0.8,0.4,0.6,0.7)
    for i=1,#lines do
        tip:drawText(lines[i],x+paddingX,y+paddingY+(i-1)*lineHeight,0.8,0.9,0.9,1.0,font)
    end
end

function IrisAltTooltip.addIrisOverlay(tip)
    if tip._irisRendered then return end
    tip._irisRendered = true
    ProtectedCall.call(addOverlay, tip)
end

local hooked = false
function IrisAltTooltip.hookTooltip()
    if hooked or not ISToolTipInv or type(ISToolTipInv.render) ~= "function" then return end
    local originalRender = ISToolTipInv.render
    ISToolTipInv.render = function(self)
        self._irisRendered = nil
        -- Vanilla errors remain visible; only Iris is isolated.
        originalRender(self)
        IrisAltTooltip.addIrisOverlay(self)
    end
    -- PZ hides and reuses the same tooltip when hovering out and back in.
    -- Reset even when Alt stays pressed and no intervening render occurs.
    local originalSetVisible = ISToolTipInv.setVisible
    if type(originalSetVisible) == "function" then
        ISToolTipInv.setVisible = function(self, visible)
            if not visible then self._irisOpening = nil end
            return originalSetVisible(self, visible)
        end
    end
    hooked = true
end

return IrisAltTooltip
