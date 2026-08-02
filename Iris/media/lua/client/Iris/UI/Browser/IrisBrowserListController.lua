--[[
    IrisBrowserListController.lua

    Category, subcategory, item list, search, and selection behavior.
]]

local IrisBrowserListController = {}
local ItemAccess = require("Iris/Util/IrisItemAccess")
local BrowserBase = require("Iris/UI/Browser/IrisBrowserBase")

--- Resolve a scrolling-list selection without depending on the input device.
--- Event payload wins; keyboard/programmatic selection falls back to the list index.
--- @param list table|nil
--- @param eventItem table|nil
--- @return table|nil payload
--- @return string reason
function IrisBrowserListController.resolveSelectedPayload(list, eventItem)
    if type(eventItem) == "table" and eventItem.item ~= nil then
        return eventItem.item, "event_item"
    end

    local selectedIndex = list and list.selected
    if type(selectedIndex) == "number" and selectedIndex > 0 then
        local selectedItem = list.items and list.items[selectedIndex]
        if type(selectedItem) == "table" and selectedItem.item ~= nil then
            return selectedItem.item, "selected_index"
        end
        return nil, "selected_index_invalid"
    end

    return nil, "no_selection"
end

local function stableIdentity(payload, field)
    if type(payload) ~= "table" then return nil end
    return payload[field]
end

local function logSelection(debug, axis, fromValue, toValue, reason)
    debug("[IrisBrowser] selection axis=" .. axis ..
        " from=" .. tostring(fromValue) ..
        " to=" .. tostring(toValue) ..
        " reason=" .. tostring(reason))
end

function IrisBrowserListController.install(IrisBrowser, context)
    local debug = context.debug
    local logError = context.logError

    function IrisBrowser:loadCategories()
        debug("[IrisBrowser] ========== loadCategories() START ==========")
        self.categoryList:clear()

        local IrisBrowserData = BrowserBase.getBrowserData(context)
        if not IrisBrowserData then
            logError("[IrisBrowser] IrisBrowserData is nil")
            return
        end

        debug("[IrisBrowser] Calling IrisBrowserData.getCategories()...")
        local categories = IrisBrowserData.getCategories()
        debug("[IrisBrowser] Got " .. #categories .. " categories")

        for i, cat in ipairs(categories) do
            local displayLabel = cat.label or cat.name
            debug("[IrisBrowser] Adding category " .. i .. ": '" .. displayLabel .. "' (code=" .. cat.name .. ")")
            self.categoryList:addItem(displayLabel, cat)
        end

        debug("[IrisBrowser] categoryList.items count = " .. #self.categoryList.items)
        debug("[IrisBrowser] ========== loadCategories() END ==========")
    end

    function IrisBrowser:loadSubcategories(categoryName)
        debug("[IrisBrowser] loadSubcategories called for: " .. tostring(categoryName))
        self.subcategoryList:clear()

        local IrisBrowserData = BrowserBase.getBrowserData(context)
        if not IrisBrowserData or not categoryName then
            debug("[IrisBrowser] IrisBrowserData or categoryName missing")
            return
        end

        local subcategories = IrisBrowserData.getSubcategories(categoryName)
        debug("[IrisBrowser] getSubcategories returned: " .. #subcategories .. " items")

        local filterText = self.subcategorySearchBar:getText():lower()

        local addedCount = 0
        for _, sub in ipairs(subcategories) do
            local labelLower = (sub.label or sub.name):lower()
            local codeLower = sub.name:lower()
            if filterText == "" or labelLower:find(filterText, 1, true) or codeLower:find(filterText, 1, true) then
                local displayLabel = sub.name .. " " .. (sub.label or "") .. " (" .. sub.itemCount .. ")"
                self.subcategoryList:addItem(displayLabel, sub)
                addedCount = addedCount + 1
            end
        end
        debug("[IrisBrowser] Added " .. addedCount .. " subcategories to list")
    end

    function IrisBrowser:loadItems(categoryName, subcategoryName)
        debug("[IrisBrowser] loadItems called: " .. tostring(categoryName) .. "." .. tostring(subcategoryName))
        self.itemList:clear()

        local IrisBrowserData = BrowserBase.getBrowserData(context)
        if not IrisBrowserData or not categoryName or not subcategoryName then
            debug("[IrisBrowser] loadItems - missing params, returning")
            return
        end

        local items = IrisBrowserData.getItems(categoryName, subcategoryName)
        debug("[IrisBrowser] getItems returned " .. #items .. " items")

        local filterText = self.itemSearchBar:getText():lower()
        local addedCount = 0

        for _, item in ipairs(items) do
            if filterText == "" or item.displayName:lower():find(filterText, 1, true) then
                self.itemList:addItem(item.displayName, item)
                addedCount = addedCount + 1
            end
        end
        debug("[IrisBrowser] Added " .. addedCount .. " items to list")
    end

    function IrisBrowser:onCategorySelected(item)
        local catData, reason = IrisBrowserListController.resolveSelectedPayload(self.categoryList, item)
        if not catData then
            logSelection(debug, "category", self.currentCategory, nil, reason)
            return
        end

        local previous = self.currentCategory
        self.currentCategory = catData.name
        self.currentSubcategory = nil
        self.currentSelectedFullType = nil
        logSelection(debug, "category", previous, stableIdentity(catData, "name"), reason)

        self:loadSubcategories(self.currentCategory)
        self.itemList:clear()
        self:showDetail(nil)
    end

    function IrisBrowser:onSubcategorySelected(item)
        local subData, reason = IrisBrowserListController.resolveSelectedPayload(self.subcategoryList, item)
        if not subData then
            logSelection(debug, "subcategory", self.currentSubcategory, nil, reason)
            return
        end

        local previous = self.currentSubcategory
        self.currentSubcategory = subData.name
        self.currentSelectedFullType = nil
        logSelection(debug, "subcategory", previous, stableIdentity(subData, "name"), reason)

        self:loadItems(self.currentCategory, self.currentSubcategory)
        self:showDetail(nil)
    end

    function IrisBrowser:onItemSelected(item)
        local itemData, reason = IrisBrowserListController.resolveSelectedPayload(self.itemList, item)
        if not itemData then
            logSelection(debug, "item", self.currentSelectedFullType, nil, reason)
            return
        end

        local previous = self.currentSelectedFullType
        self.detailScrollY = 0
        self.currentSelectedFullType = itemData.fullType
        self.currentSelectedVariants = itemData.variants
        logSelection(debug, "item", previous, stableIdentity(itemData, "fullType"), reason)
        self:showDetail(self.currentSelectedFullType)
    end

    function IrisBrowser:onGlobalSearchChange()
        local query = self.searchBar:getText()
        if query == "" then
            self:loadCategories()
            return
        end

        local IrisBrowserData = BrowserBase.getBrowserData(context)
        if not IrisBrowserData then return end

        local results = IrisBrowserData.searchAll(query)

        self.categoryList:clear()
        self.subcategoryList:clear()

        self.itemList:clear()
        for _, result in ipairs(results) do
            self.itemList:addItem(result.displayName, result)
        end
    end

    function IrisBrowser:onSubcategorySearchChange()
        if self.currentCategory then
            self:loadSubcategories(self.currentCategory)
        end
    end

    function IrisBrowser:onItemSearchChange()
        if self.currentCategory and self.currentSubcategory then
            self:loadItems(self.currentCategory, self.currentSubcategory)
        end
    end

    function IrisBrowser:selectItem(item)
        if not item then return end

        local fullType = ItemAccess.getFullType(item)
        if not fullType then
            return
        end
        local IrisBrowserData = BrowserBase.getBrowserData(context)
        local targetCat, targetSub = nil, nil
        if IrisBrowserData and IrisBrowserData.getItemLocation then
            targetCat, targetSub = IrisBrowserData.getItemLocation(fullType)
        end

        if targetCat and targetSub then
            self.currentCategory = targetCat
            self:loadSubcategories(targetCat)

            self.currentSubcategory = targetSub
            self:loadItems(targetCat, targetSub)

            self.detailScrollY = 0
            self.currentSelectedFullType = fullType
            self:showDetail(fullType)

            debug("[IrisBrowser] Selected item: " .. fullType .. " in " .. targetCat .. "." .. targetSub)
        else
            self.detailScrollY = 0
            self.currentSelectedFullType = fullType
            self:showDetail(fullType)
            debug("[IrisBrowser] Item not classified: " .. fullType)
        end
    end
end

return IrisBrowserListController
