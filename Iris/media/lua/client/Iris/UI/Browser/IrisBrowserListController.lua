--[[
    IrisBrowserListController.lua

    Category, subcategory, item list, search, and selection behavior.
]]

local IrisBrowserListController = {}
local ItemAccess = require("Iris/Util/IrisItemAccess")
local BrowserBase = require("Iris/UI/Browser/IrisBrowserBase")

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
        debug("[IrisBrowser] onCategorySelected called")
        debug("[IrisBrowser] item type: " .. type(item))

        if not item then
            debug("[IrisBrowser] item is nil, returning")
            return
        end

        if type(item) == "table" then
            for k, v in pairs(item) do
                debug("[IrisBrowser] item." .. tostring(k) .. " = " .. tostring(v))
            end
        end

        local catData = item.item
        if not catData then
            debug("[IrisBrowser] catData is nil, trying self.categoryList.selected")
            local selectedIdx = self.categoryList.selected
            if selectedIdx and selectedIdx > 0 then
                local selectedItem = self.categoryList.items[selectedIdx]
                if selectedItem then
                    catData = selectedItem.item
                    debug("[IrisBrowser] Got catData from selected: " .. tostring(catData and catData.name))
                end
            end
        end

        if not catData then
            debug("[IrisBrowser] catData still nil, returning")
            return
        end

        debug("[IrisBrowser] Selected category: " .. tostring(catData.name))

        self.currentCategory = catData.name
        self.currentSubcategory = nil
        self.currentSelectedFullType = nil

        self:loadSubcategories(self.currentCategory)
        self.itemList:clear()
        self:showDetail(nil)
    end

    function IrisBrowser:onSubcategorySelected(item)
        debug("[IrisBrowser] onSubcategorySelected called")
        if not item then
            debug("[IrisBrowser] subitem is nil")
            return
        end
        local subData = item.item
        if not subData then
            debug("[IrisBrowser] subData is nil, trying selected index")
            local selectedIdx = self.subcategoryList.selected
            if selectedIdx and selectedIdx > 0 then
                local selectedItem = self.subcategoryList.items[selectedIdx]
                if selectedItem then
                    subData = selectedItem.item
                    debug("[IrisBrowser] Got subData from selected: " .. tostring(subData and subData.name))
                end
            end
        end

        if not subData then
            debug("[IrisBrowser] subData still nil")
            return
        end

        debug("[IrisBrowser] Selected subcategory: " .. tostring(subData.name))

        self.currentSubcategory = subData.name
        self.currentSelectedFullType = nil

        self:loadItems(self.currentCategory, self.currentSubcategory)
        self:showDetail(nil)
    end

    function IrisBrowser:onItemSelected(item)
        debug("[IrisBrowser] onItemSelected called")
        debug("[IrisBrowser] item = " .. tostring(item))
        debug("[IrisBrowser] item type = " .. type(item))

        if not item then
            debug("[IrisBrowser] item is nil, returning")
            return
        end

        if type(item) == "table" then
            for k, v in pairs(item) do
                debug("[IrisBrowser] item." .. tostring(k) .. " = " .. tostring(v))
            end
        end

        local itemData = item.item
        debug("[IrisBrowser] itemData = " .. tostring(itemData))
        debug("[IrisBrowser] itemData type = " .. type(itemData))

        if not itemData then
            debug("[IrisBrowser] itemData is nil, trying selected index")
            local selectedIdx = self.itemList.selected
            debug("[IrisBrowser] selectedIdx = " .. tostring(selectedIdx))
            if selectedIdx and selectedIdx > 0 then
                local selectedItem = self.itemList.items[selectedIdx]
                debug("[IrisBrowser] selectedItem = " .. tostring(selectedItem))
                if selectedItem then
                    itemData = selectedItem.item
                    debug("[IrisBrowser] Got itemData from selected: " .. tostring(itemData))
                end
            end
        end

        if not itemData then
            debug("[IrisBrowser] itemData still nil, returning")
            return
        end

        if type(itemData) == "table" then
            for k, v in pairs(itemData) do
                debug("[IrisBrowser] itemData." .. tostring(k) .. " = " .. tostring(v))
            end
        end

        debug("[IrisBrowser] itemData.fullType = " .. tostring(itemData.fullType))

        self.detailScrollY = 0
        self.currentSelectedFullType = itemData.fullType
        self.currentSelectedVariants = itemData.variants
        debug("[IrisBrowser] Set currentSelectedFullType = " .. tostring(self.currentSelectedFullType))
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
