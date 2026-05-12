--[[
    IrisBrowserRecipeNav.lua

    Navigation from IrisBrowser recipe entries into the PZ crafting UI.
]]

local IrisBrowserRecipeNav = {}

local ProtectedCall = require("Iris/Util/IrisProtectedCall")

function IrisBrowserRecipeNav.install(IrisBrowser, context)
    function IrisBrowser:onRecipeGoToCrafting(button)
        local ref = button and button.recipe_nav_ref
        if not ref then return end

        local playerNum = self.playerNum or 0
        local ok, craftUI = ProtectedCall.ui(getPlayerCraftingUI, playerNum)
        if not ok or not craftUI then return end

        ProtectedCall.ui(function()
            if not craftUI:getIsVisible() then
                craftUI:setVisible(true)
                craftUI:addToUIManager()
            end
            craftUI:bringToTop()
        end)

        if ref.category and craftUI.panel then
            ProtectedCall.ui(function()
                local tabName = getTextOrNull("IGUI_CraftCategory_" .. ref.category)
                    or ref.category
                craftUI.panel:activateView(tabName)
            end)
        end

        if ref.original_name and craftUI.panel then
            ProtectedCall.ui(function()
                local activeView = craftUI.panel:getActiveView()
                if activeView and activeView.filterEntry then
                    local filterText = ref.translated_name or ref.original_name
                    activeView.filterEntry:setText(filterText)
                end
                if activeView and activeView.filterAll then
                    activeView.filterAll:setSelected(1, true)
                end
            end)
        end
    end
end

return IrisBrowserRecipeNav
