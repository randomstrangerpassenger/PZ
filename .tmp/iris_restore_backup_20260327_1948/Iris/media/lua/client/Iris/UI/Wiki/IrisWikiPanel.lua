require "ISUI/ISCollapsableWindow"
require "ISUI/ISScrollingListBox"
require "ISUI/ISTextEntryBox"
require "ISUI/ISRichTextPanel"
require "Iris/IrisDvfBridge"

local FONT_HGT_SMALL = getTextManager():getFontHeight(UIFont.Small)

IrisWikiPanel = ISCollapsableWindow:derive("IrisWikiPanel")
IrisWikiPanelList = ISScrollingListBox:derive("IrisWikiPanelList")

local function trim(text)
    if not text then
        return ""
    end
    return (text:gsub("^%s+", ""):gsub("%s+$", ""))
end

local function containsLower(haystack, needle)
    return string.find(string.lower(haystack), string.lower(needle), 1, true) ~= nil
end

function IrisWikiPanelList:doDrawItem(y, item, alt)
    if y + self:getYScroll() >= self.height then return y + item.height end
    if y + item.height + self:getYScroll() <= 0 then return y + item.height end

    if self.selected == item.index then
        self:drawRect(0, y, self:getWidth(), self.itemheight - 1, 0.3, 0.7, 0.35, 0.15)
    end

    self:drawRectBorder(0, y, self:getWidth(), self.itemheight, 0.4, 0.5, 0.5, 0.5)
    self:drawText(item.text, 10, y + (item.height - self.fontHgt) / 2, 0.9, 0.9, 0.9, 1.0, UIFont.Small)
    return y + self.itemheight
end

function IrisWikiPanelList:onMouseDown(x, y)
    local row = self:rowAt(x, y)
    if row == -1 then
        return true
    end

    self.selected = row
    local item = self.items[row]
    if item and self.owner then
        self.owner:selectItem(item.item)
    end
    return true
end

function IrisWikiPanel:initialise()
    ISCollapsableWindow.initialise(self)
    self.title = "Iris Wiki"
end

function IrisWikiPanel:createChildren()
    ISCollapsableWindow.createChildren(self)

    local th = self:titleBarHeight()
    local rh = self:resizeWidgetHeight()
    local pad = 8
    local entryHgt = FONT_HGT_SMALL + 8
    local listWidth = math.floor(self.width * 0.36)
    local contentY = th + pad + entryHgt + pad
    local contentHeight = self.height - contentY - rh - pad

    self.searchEntry = ISTextEntryBox:new("", pad, th + pad, listWidth, entryHgt)
    self.searchEntry:initialise()
    self.searchEntry:instantiate()
    self.searchEntry:setClearButton(true)
    self:addChild(self.searchEntry)

    self.listBox = IrisWikiPanelList:new(pad, contentY, listWidth, contentHeight)
    self.listBox.owner = self
    self.listBox:initialise()
    self.listBox:setAnchorBottom(true)
    self.listBox:setFont(UIFont.Small, 2)
    self:addChild(self.listBox)

    self.richText = ISRichTextPanel:new(
        self.listBox:getRight() + pad,
        contentY,
        self.width - self.listBox:getRight() - pad * 2,
        contentHeight
    )
    self.richText:initialise()
    self.richText.background = false
    self.richText.autosetheight = false
    self.richText.clip = true
    self.richText:addScrollBars()
    self:addChild(self.richText)

    self.searchEntry.onTextChange = function()
        self:applyFilter(self.searchEntry:getInternalText())
    end

    self.itemIds = IrisDvfBridge.listItemIds()
    self.filteredIds = {}
    self:applyFilter("")
end

function IrisWikiPanel:onResize()
    ISUIElement.onResize(self)

    local th = self:titleBarHeight()
    local rh = self:resizeWidgetHeight()
    local pad = 8
    local entryHgt = FONT_HGT_SMALL + 8
    local listWidth = math.floor(self.width * 0.36)
    local contentY = th + pad + entryHgt + pad
    local contentHeight = self.height - contentY - rh - pad

    self.searchEntry:setX(pad)
    self.searchEntry:setY(th + pad)
    self.searchEntry:setWidth(listWidth)

    self.listBox:setX(pad)
    self.listBox:setY(contentY)
    self.listBox:setWidth(listWidth)
    self.listBox:setHeight(contentHeight)

    self.richText:setX(self.listBox:getRight() + pad)
    self.richText:setY(contentY)
    self.richText:setWidth(self.width - self.listBox:getRight() - pad * 2)
    self.richText:setHeight(contentHeight)
end

function IrisWikiPanel:applyFilter(rawFilter)
    local filter = trim(rawFilter)
    self.filteredIds = {}
    self.listBox:clear()

    for _, itemId in ipairs(self.itemIds or {}) do
        local entry = IrisDvfBridge.getEntry(itemId)
        local text = entry and entry.text_ko or ""
        local haystack = itemId .. " " .. text
        if filter == "" or containsLower(haystack, filter) then
            table.insert(self.filteredIds, itemId)
            self.listBox:addItem(itemId, itemId)
        end
    end

    if #self.filteredIds > 0 then
        self:selectItem(self.filteredIds[1])
    else
        self.listBox.selected = -1
        self.richText.text = "No bridged entries for the current filter."
        self.richText:paginate()
        self.richText:setYScroll(0)
    end
end

function IrisWikiPanel:selectItem(itemId)
    if not itemId then
        return
    end

    for index, rowId in ipairs(self.filteredIds or {}) do
        if rowId == itemId then
            self.listBox.selected = index
            break
        end
    end

    local entry = IrisDvfBridge.getEntry(itemId)
    if not entry then
        self.richText.text = itemId .. "\n\nNo 3-3 entry is available."
    else
        self.richText.text = table.concat(
            {
                itemId,
                "",
                entry.text_ko or "No rendered text.",
                "",
                "source: " .. tostring(entry.source or "unknown"),
            },
            "\n"
        )
    end

    self.richText:paginate()
    self.richText:setYScroll(0)
end

function IrisWikiPanel:new(x, y, width, height)
    local o = ISCollapsableWindow:new(x, y, width, height)
    setmetatable(o, self)
    self.__index = self
    o.backgroundColor = { r = 0, g = 0, b = 0, a = 0.9 }
    return o
end

return IrisWikiPanel
