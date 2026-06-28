--[[
    IrisBrowserLayout.lua

    Layout and widget construction for IrisBrowser.
]]

require "ISUI/ISPanel"
require "ISUI/ISScrollingListBox"
require "ISUI/ISTextEntryBox"
require "ISUI/ISButton"
require "ISUI/ISLabel"

local IrisBrowserLayout = {}
local Theme = require("Iris/UI/Browser/IrisBrowserTheme")

function IrisBrowserLayout.install(IrisBrowser, context)
    local tr = context.tr

    function IrisBrowser:createChildren()
        ISPanel.createChildren(self)

        local headerHeight = 40
        local listTop = headerHeight + 10
        local listHeight = self.height - listTop - 10

        local colCatW = self.width * Theme.COLUMNS.category
        local colSubW = self.width * Theme.COLUMNS.subcategory
        local colItemW = self.width * Theme.COLUMNS.items
        local colDetailW = self.width * Theme.COLUMNS.detail

        local col1X = 5
        local col2X = col1X + colCatW + 5
        local col3X = col2X + colSubW + 5
        local col4X = col3X + colItemW + 5

        self.titleLabel = ISLabel:new(10, 10, 25, "Iris Browser", 0.6, 0.9, 1.0, 1.0, UIFont.Medium, true)
        self:addChild(self.titleLabel)

        local closeBtnWidth = 25
        local closeBtnX = self.width - closeBtnWidth - 5
        local searchBarWidth = 200
        local searchBarX = closeBtnX - searchBarWidth - 10

        self.searchBar = ISTextEntryBox:new("", searchBarX, 8, searchBarWidth, 24)
        self.searchBar:initialise()
        self.searchBar:instantiate()
        self.searchBar.onTextChange = function()
            self:onGlobalSearchChange()
        end
        self:addChild(self.searchBar)

        self.closeBtn = ISButton:new(closeBtnX, 5, closeBtnWidth, 25, "X", self, self.close)
        self.closeBtn:initialise()
        self.closeBtn.borderColor = Theme.color("closeButtonBorder")
        self:addChild(self.closeBtn)

        self.categoryLabel = ISLabel:new(col1X, listTop - 18, 16, tr("Iris_UI_CategoryLabel", "Category"), 0.7, 0.7, 0.7, 1, UIFont.Small, true)
        self:addChild(self.categoryLabel)

        self.categoryList = ISScrollingListBox:new(col1X, listTop, colCatW - 5, listHeight)
        self.categoryList:initialise()
        self.categoryList:instantiate()
        self.categoryList.onmousedown = function(list, item)
            self:onCategorySelected(item)
        end
        self.categoryList.font = UIFont.Small
        self.categoryList.fontHgt = getTextManager():getFontHeight(UIFont.Small)
        self.categoryList.itemheight = self.categoryList.fontHgt + 4
        self:addChild(self.categoryList)

        self.subcategoryLabel = ISLabel:new(col2X, listTop - 18, 16, tr("Iris_UI_SubcategoryLabel", "Subcategory"), 0.7, 0.7, 0.7, 1, UIFont.Small, true)
        self:addChild(self.subcategoryLabel)

        self.subcategorySearchBar = ISTextEntryBox:new("", col2X, listTop, colSubW - 5, 20)
        self.subcategorySearchBar:initialise()
        self.subcategorySearchBar:instantiate()
        self.subcategorySearchBar.onTextChange = function()
            self:onSubcategorySearchChange()
        end
        self:addChild(self.subcategorySearchBar)

        self.subcategoryList = ISScrollingListBox:new(col2X, listTop + 25, colSubW - 5, listHeight - 25)
        self.subcategoryList:initialise()
        self.subcategoryList:instantiate()
        self.subcategoryList.onmousedown = function(list, item)
            self:onSubcategorySelected(item)
        end
        self.subcategoryList.font = UIFont.Small
        self.subcategoryList.fontHgt = getTextManager():getFontHeight(UIFont.Small)
        self.subcategoryList.itemheight = self.subcategoryList.fontHgt + 4
        self:addChild(self.subcategoryList)

        self.itemLabel = ISLabel:new(col3X, listTop - 18, 16, tr("Iris_UI_ItemLabel", "Items"), 0.7, 0.7, 0.7, 1, UIFont.Small, true)
        self:addChild(self.itemLabel)

        self.itemSearchBar = ISTextEntryBox:new("", col3X, listTop, colItemW - 5, 20)
        self.itemSearchBar:initialise()
        self.itemSearchBar:instantiate()
        self.itemSearchBar.onTextChange = function()
            self:onItemSearchChange()
        end
        self:addChild(self.itemSearchBar)

        self.itemList = ISScrollingListBox:new(col3X, listTop + 25, colItemW - 5, listHeight - 25)
        self.itemList:initialise()
        self.itemList:instantiate()
        self.itemList.onmousedown = function(list, item)
            self:onItemSelected(item)
        end
        self.itemList.font = UIFont.Small
        self.itemList.fontHgt = getTextManager():getFontHeight(UIFont.Small)
        self.itemList.itemheight = self.itemList.fontHgt + 4
        self:addChild(self.itemList)

        self.detailLabel = ISLabel:new(col4X, listTop - 18, 16, tr("Iris_UI_DetailLabel", "Details"), 0.7, 0.7, 0.7, 1, UIFont.Small, true)
        self:addChild(self.detailLabel)

        local scrollBarWidth = 13
        local detailPanelWidth = self.width - col4X - 10 - scrollBarWidth
        self.detailPanel = ISPanel:new(col4X, listTop, detailPanelWidth, listHeight)
        self.detailPanel:initialise()
        self.detailPanel.backgroundColor = Theme.color("detailPanelBackground")
        self.detailPanel.borderColor = Theme.color("detailPanelBorder")

        local browser = self
        self.detailPanel.onMouseWheel = function(self, del)
            browser:onDetailMouseWheel(del)
            return true
        end

        local originalPrerender = self.detailPanel.prerender
        self.detailPanel.prerender = function(self)
            if originalPrerender then originalPrerender(self) end
            self:setStencilRect(0, 0, self.width, self.height)
        end

        local originalRender = self.detailPanel.render
        self.detailPanel.render = function(self)
            if originalRender then originalRender(self) end
            self:clearStencilRect()
        end

        self:addChild(self.detailPanel)

        self.detailScrollBarPanel = ISPanel:new(col4X + detailPanelWidth, listTop, scrollBarWidth, listHeight)
        self.detailScrollBarPanel:initialise()
        self.detailScrollBarPanel.backgroundColor = Theme.color("transparent")
        self.detailScrollBarPanel.borderColor = Theme.color("transparent")

        local browserRef = self
        self.detailScrollBarPanel.render = function(scrollPanel)
            if not browserRef.currentSelectedFullType then
                return
            end

            local needsScroll = browserRef.detailContentHeight > browserRef.detailPanel.height
            if not needsScroll then
                return
            end

            Theme.drawRect(scrollPanel, 0, 0, scrollPanel.width, scrollPanel.height, "detailScrollTrack")

            local maxScroll = math.max(1, browserRef.detailContentHeight - browserRef.detailPanel.height)
            local ratio = browserRef.detailScrollY / maxScroll
            local trackHeight = scrollPanel.height - 4
            local thumbHeight = math.max(20, (browserRef.detailPanel.height / math.max(1, browserRef.detailContentHeight)) * trackHeight)
            local thumbY = 2 + ratio * (trackHeight - thumbHeight)

            Theme.drawRect(scrollPanel, 2, thumbY, scrollBarWidth - 4, thumbHeight, "detailScrollThumb")
        end

        self:addChild(self.detailScrollBarPanel)
        self:loadCategories()
    end
end

return IrisBrowserLayout
