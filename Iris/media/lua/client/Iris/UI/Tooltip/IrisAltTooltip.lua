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

-- Fit failures are retained on the opening and reported once per environment.
-- They are not valid absence or a successful four-line display.
local function fitFailure(opening, locale, reason, width, height, required)
    local identity = locale .. ":" .. reason .. ":" .. tostring(width) .. ":" .. tostring(height)
    if opening.fitFailureIdentity ~= identity then
        opening.fitFailureIdentity = identity
        print("Iris Tooltip fit failure: " .. opening.fullType .. " " .. identity .. " required=" .. tostring(required))
    end
    opening.displayStatus = "fit_failed"
    opening.fitFailure = {locale=locale, reason=reason, screenWidth=width, screenHeight=height, required=required}
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
        opening.view, opening.lookupError = Lookup.open(fullType, function(count)
            if ZombRand then return ZombRand(count)+1 end
            return math.random(count)
        end)
        if opening.lookupError then opening.displayStatus = "lookup_failed" end
    end
    local rows = opening.view and opening.view[locale]
    if not rows or #rows == 0 then return end

    local manager, font = getTextManager(), UIFont.Small
    local lineHeight = manager:getFontHeight(font)
    if type(lineHeight) ~= "number" or lineHeight <= 0 then return end
    local core = getCore()
    local screenWidth, screenHeight = core:getScreenWidth(), core:getScreenHeight()
    local absoluteX, absoluteY = tip:getAbsoluteX(), tip:getAbsoluteY()
    -- Every role occupies one physical line at the normal game font size.
    -- Widen to the measured original text, then choose a nonoverlapping side.
    local gap = 4
    local contentWidth = 0
    for i=1,#rows do
        contentWidth = math.max(contentWidth, manager:MeasureStringX(font, rows[i]))
    end
    local width = math.max(contentWidth+20, math.min(240, screenWidth))
    local blockHeight = #rows * lineHeight + 8
    if #rows > 4 or width > screenWidth or blockHeight > screenHeight then
        fitFailure(opening, locale, "screen_capacity", screenWidth, screenHeight, width)
        return
    end
    local rightSpace = screenWidth - (absoluteX+tip.width+gap)
    local leftSpace = absoluteX-gap
    local x, y
    if rightSpace >= width or leftSpace >= width then
        x = rightSpace >= width and tip.width+gap or -width-gap
        y = math.max(0, math.min(absoluteY, screenHeight-blockHeight)) - absoluteY
    else
        x = math.max(0, math.min(absoluteX, screenWidth-width)) - absoluteX
        if absoluteY+tip.height+gap+blockHeight <= screenHeight and absoluteY+tip.height+gap >= 0 then
            y = tip.height+gap
        elseif absoluteY-blockHeight-gap >= 0 and absoluteY-gap <= screenHeight then
            y = -blockHeight-gap
        else
            fitFailure(opening, locale, "no_nonoverlapping_position", screenWidth, screenHeight, blockHeight)
            return
        end
    end
    opening.displayStatus = "displayed"
    opening.fitFailure = nil
    local lines = rows
    tip:drawRect(x,y,width,blockHeight,0.9,0.05,0.15,0.2)
    tip:drawRectBorder(x,y,width,blockHeight,0.8,0.4,0.6,0.7)
    for i=1,#lines do
        tip:drawText(lines[i],x+10,y+4+(i-1)*lineHeight,0.8,0.9,0.9,1.0,font)
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
