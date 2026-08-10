local repoRoot = assert(arg[1], "repository root argument is required")
local mode = assert(arg[2], "metrics mode argument is required")
local luaRoot = repoRoot .. "/Iris/media/lua/client"
package.path = luaRoot .. "/?.lua;" .. luaRoot .. "/?/init.lua;" .. package.path

local function emit(key, value)
    print(tostring(key) .. "=" .. tostring(value))
end

local function runSearch()
    local Query = require("Iris/UI/Browser/IrisBrowserQuery")
    local rows = {
        {"Base.Alpha", "Alpha", "Tool", "1-A"},
        {"Base.Alpine", "Alpine Saw", "Tool", "1-A"},
        {"Base.Beta", "Beta", "Resource", "4-A"},
        {"Base.Better", "Better Hammer", "Tool", "1-A"},
        {"Base.Gamma", "Gamma", "Consumable", "3-A"},
        {"Base.Map", "Road Map", "Literature", "5-A"},
        {"Base.Axe", "Wood Axe", "Combat", "2-A"},
        {"Base.Apple", "Apple", "Consumable", "3-A"},
    }
    local cache = {
        itemsByFullType = {},
        searchKeysByFullType = {},
        primaryLocationByFullType = {},
        searchKeysLocale = "EN",
        generation = 7,
        searchMetrics = {
            searchCalls=0,totalScanRows=0,lastScanRows=0,prefixReuseCount=0,
            locationLookupCount=0,internalRowCopyCount=0,publicRowCopyCount=0,
            localeInvalidationCount=0,generationInvalidationCount=0,
        },
    }
    local locations = {}
    for _, row in ipairs(rows) do
        local fullType, displayName, category, subcategory = row[1], row[2], row[3], row[4]
        cache.itemsByFullType[fullType] = {}
        cache.searchKeysByFullType[fullType] = {
            displayName = displayName,
            folded = displayName:lower() .. "\0" .. fullType:lower(),
        }
        cache.primaryLocationByFullType[fullType] = {
            category = category,
            subcategory = subcategory,
        }
        locations[fullType] = {category, subcategory}
    end
    local callbackCalls = 0
    local function location(fullType)
        callbackCalls = callbackCalls + 1
        local value = locations[fullType]
        return value and value[1] or nil, value and value[2] or nil
    end
    local signature = {}
    local returnedRows = 0
    for _, query in ipairs({"a", "al", "alp", "b", "be", "map"}) do
        local result = Query.searchAll(cache, query, location, "EN")
        returnedRows = returnedRows + #result
        local items = {}
        for _, row in ipairs(result) do
            items[#items + 1] = table.concat({row.fullType, row.displayName,
                row.category or "nil", row.subcategory or "nil"}, ":")
        end
        signature[#signature + 1] = query .. "=" .. table.concat(items, ",")
        if #result > 0 then result[1].displayName = "caller-mutation" end
    end
    local final = Query.searchAll(cache, "alph", location, "EN")
    assert(#final == 1 and final[1].displayName == "Alpha")
    returnedRows = returnedRows + #final
    signature[#signature + 1] = "alph=" .. final[1].fullType .. ":" .. final[1].displayName
    local metrics = cache.searchMetrics
    emit("mode", "search")
    emit("returned_rows", returnedRows)
    emit("location_lookups", metrics.locationLookupCount or callbackCalls)
    emit("callback_calls", callbackCalls)
    emit("internal_row_copies", metrics.internalRowCopyCount or 0)
    emit("public_row_copies", metrics.publicRowCopyCount or 0)
    emit("scan_rows", metrics.totalScanRows or 0)
    emit("prefix_reuse", metrics.prefixReuseCount or 0)
    emit("signature", table.concat(signature, "|"))
end

local function installRuntimeStubs()
    package.preload["Iris/Util/IrisModuleBootstrap"] = function()
        return {
            create = function()
                return {
                    safeRequire = function(name)
                        local ok, value = pcall(require, name)
                        return ok, value
                    end,
                    debug = function() end,
                    warn = function() end,
                    logError = function() end,
                }
            end,
        }
    end
    package.preload["Iris/Util/IrisProtectedCall"] = function()
        local function protected(fn, ...)
            local values = {pcall(fn, ...)}
            local ok = table.remove(values, 1)
            return ok, values[1]
        end
        return {engine=protected,data=protected,call=protected}
    end
end

local function runTooltip()
    installRuntimeStubs()
    local locale = "EN"
    local revision = "fixture-r1"
    local summaryLoads = 0
    local publicSummary = {
        fullType="Base.Hammer",tags={"Tool.1-A"},connections={"Recipe"},
        useCaseCount=1,revision=revision,
    }
    package.preload["Iris/Util/ItemKey"] = function()
        return {getFullTypeFromItem=function(item) return item.fullType end}
    end
    package.preload["Iris/Util/IrisTranslationResolver"] = function()
        return {
            get=function(_key, fallback) return fallback end,
            getLangKey=function() return locale end,
        }
    end
    package.preload["Iris/UI/Tooltip/IrisTooltipSummary"] = function()
        summaryLoads = summaryLoads + 1
        return {
            _getCached=function()
                publicSummary.revision = revision
                return publicSummary
            end,
            get=function()
                return {
                    fullType=publicSummary.fullType,
                    tags={publicSummary.tags[1]},
                    connections={publicSummary.connections[1]},
                    useCaseCount=publicSummary.useCaseCount,
                    revision=revision,
                }
            end,
            reset=function() end,
        }
    end
    UIFont = {Small="Small"}
    local altPressed = false
    isKeyDown = function(code) return altPressed and code == 56 end
    local drawCalls = 0
    local function tooltip()
        return {
            item={fullType="Base.Hammer"},height=20,width=200,
            drawRect=function() drawCalls = drawCalls + 1 end,
            drawRectBorder=function() drawCalls = drawCalls + 1 end,
            drawText=function() drawCalls = drawCalls + 1 end,
            setHeight=function(self, height) self.height = height end,
        }
    end
    local Tooltip = require("Iris/UI/Tooltip/IrisAltTooltip")
    Tooltip.resetDisplayLineCache()
    for _ = 1, 1000 do Tooltip.addIrisOverlay(tooltip()) end
    local inactive = Tooltip.getDisplayLineCacheMetrics()
    local inactiveDrawCalls = drawCalls

    altPressed = true
    for _ = 1, 100 do Tooltip.addIrisOverlay(tooltip()) end
    local warm = Tooltip.getDisplayLineCacheMetrics()
    locale = "KO"
    Tooltip.addIrisOverlay(tooltip())
    revision = "fixture-r2"
    Tooltip.addIrisOverlay(tooltip())
    local invalidated = Tooltip.getDisplayLineCacheMetrics()
    emit("mode", "tooltip")
    emit("inactive_renders", inactive.inactiveRenders)
    emit("inactive_summary_loads", inactive.summaryLoadAttempts)
    emit("inactive_summary_gets", inactive.summaryGetCalls)
    emit("inactive_temporary_tables", inactive.temporaryDetailTables)
    emit("inactive_draw_calls", inactiveDrawCalls)
    emit("warm_hits", warm.hits)
    emit("warm_misses", warm.misses)
    emit("warm_display_builds", warm.displayLineBuilds)
    emit("warm_line_copies", warm.lineCopies)
    emit("summary_module_loads", summaryLoads)
    emit("invalidation_misses", invalidated.misses)
    emit("draw_calls", drawCalls)
end

local function runViewModel()
    installRuntimeStubs()
    package.preload["Iris/Util/IrisItemAccess"] = function()
        return {
            getFullType=function(item) return item.fullType end,
            getDisplayName=function(item) return item.displayName end,
            getModuleName=function(item) return item.moduleName end,
            getType=function(item) return item.itemType end,
        }
    end
    package.preload["Iris/UI/Layer3/IrisLayer3DisplayFormatter"] = function()
        return {format=function(value) return value end}
    end
    package.preload["Iris/Util/IrisTranslationResolver"] = function()
        return {getLangKey=function() return "EN" end}
    end
    package.preload["Iris/Data/layer3_renderer"] = function()
        return {getText=function() return nil end,getPublishState=function() return nil end}
    end
    package.preload["Iris/IrisAPI"] = function()
        return {
            Tags={getTagsForItem=function() return { ["Tool.1-A"] = true } end},
            UseCases={
                getUseCaseLines=function() return {lines={},debug_lines={}} end,
                getCapabilities=function() return {} end,
            },
            Index={
                getRecipeConnectionsForItem=function() return {} end,
                getMoveablesInfoForItem=function() return nil end,
                getFixingInfoForItem=function() return nil end,
            },
        }
    end

    local engineCalls = 0
    local function method(field)
        return function(self)
            engineCalls = engineCalls + 1
            return self.values[field]
        end
    end
    local methodFields = {
        getHungerChange="hunger",getThirstChange="thirst",getStressChange="stress",
        getBoredomChange="boredom",getCalories="calories",getMinDamage="minDamage",
        getMaxDamage="maxDamage",getMinRange="minRange",getMaxRange="maxRange",
        getCriticalChance="criticalChance",getConditionMax="conditionMax",
        getNumberOfPages="numberOfPages",getSkillTrained="skillTrained",
        getLvlSkillTrained="level",getNumLevelsTrained="levelCount",
        getCapacity="capacity",getLightStrength="lightStrength",
        isWaterproof="waterproof",getInsulation="insulation",
    }
    local function item(kind, index)
        local value = {
            fullType="Fixture." .. kind .. tostring(index),
            displayName=kind .. tostring(index),moduleName="Fixture",itemType=kind,
            category=kind,subcategory="Fixture",weight=index,
            values={},
        }
        value.getActualWeight = function(self) engineCalls=engineCalls+1 return self.weight end
        value.getWeight = function(self) engineCalls=engineCalls+1 return self.weight end
        value.getDisplayCategory = function(self) engineCalls=engineCalls+1 return self.category end
        value.getCategory = function(self) engineCalls=engineCalls+1 return self.category end
        value.getSubCategory = function(self) engineCalls=engineCalls+1 return self.subcategory end
        for name, field in pairs(methodFields) do value[name] = method(field) end
        if kind == "Food" then value.values.hunger=-0.2; value.values.calories=120 end
        if kind == "Weapon" then value.values.minDamage=1; value.values.conditionMax=10 end
        if kind == "Literature" then value.values.numberOfPages=220; value.values.skillTrained="Aiming" end
        if kind == "Moveable" then value.values.capacity=30; value.values.waterproof=false end
        return value
    end

    local ViewModel = require("Iris/UI/Detail/IrisItemDetailViewModel")
    ViewModel.resetInstrumentation()
    local signature = {}
    local retained = nil
    for _, kind in ipairs({"Food", "Weapon", "Literature", "Moveable", "Normal"}) do
        for index = 1, 20 do
            local source = item(kind, index)
            local model = ViewModel.fromItem(source)
            assert(model.sourceItem == source)
            signature[#signature + 1] = table.concat({kind,index,model.weight,
                model.food.hunger or "nil",model.weapon.minDamage or "nil",
                model.literature.numberOfPages or "nil",model.moveable.capacity or "nil"}, ":")
            if retained == nil then retained = {source=source,model=model} end
        end
    end
    local metrics = ViewModel.getInstrumentation()
    local measuredEngineCalls = engineCalls
    retained.source.weight = 999
    local refreshed = ViewModel.fromItem(retained.source)
    assert(refreshed ~= retained.model and refreshed.sourceItem == retained.source)
    assert(refreshed.weight == 999 and retained.model.weight ~= 999)
    emit("mode", "viewmodel")
    emit("items", 100)
    emit("method_attempts", metrics.methodAttempts)
    emit("engine_method_calls", measuredEngineCalls)
    emit("food_skips", (metrics.groupSkips and metrics.groupSkips.food) or 0)
    emit("weapon_skips", (metrics.groupSkips and metrics.groupSkips.weapon) or 0)
    emit("literature_skips", (metrics.groupSkips and metrics.groupSkips.literature) or 0)
    emit("moveable_skips", (metrics.groupSkips and metrics.groupSkips.moveable) or 0)
    emit("static_cache_hits", metrics.staticCacheHits or 0)
    emit("static_cache_misses", metrics.staticCacheMisses or 0)
    emit("instance_isolation", "PASS")
    emit("signature", table.concat(signature, "|"))
end

local function runOrdering()
    local priorityCalls = 0
    local priorities = {Tool=1,Combat=2,Consumable=3,Resource=4,Literature=5,Wearable=6}
    package.preload["Iris/Logic/CategoryPresentationOrder"] = function()
        return {getDescriptionPriority=function(category)
            priorityCalls = priorityCalls + 1
            return priorities[category] or 999
        end}
    end
    package.preload["Iris/Logic/IrisDesc/Logger"] = function()
        return {isDebugEnabled=function() return false end,debug=function() end}
    end
    local Ordering = require("Iris/Logic/IrisDesc/Ordering")
    if Ordering.resetInstrumentation then Ordering.resetInstrumentation() end
    local tags = {
        ["Tool.1-C"]=true,["Tool.1-A"]=true,["Combat.2-B"]=true,
        ["Combat.2-A"]=true,["Consumable.3-D"]=true,["Consumable.3-A"]=true,
        ["Resource.4-C"]=true,["Resource.4-A"]=true,["Literature.5-B"]=true,
        ["Literature.5-A"]=true,["Wearable.6-B"]=true,["Wearable.6-A"]=true,
    }
    local anchor, ordered = Ordering.resolveSubcategories(tags, nil)
    local metrics = Ordering.getInstrumentation and Ordering.getInstrumentation() or {}
    emit("mode", "ordering")
    emit("rows", #ordered)
    emit("priority_calls", priorityCalls)
    emit("sort_key_derivations", metrics.sortKeyDerivations or priorityCalls)
    emit("sort_passes", metrics.sortPasses or 1)
    emit("anchor", anchor)
    emit("signature", table.concat(ordered, ","))
end

if mode == "search" then runSearch()
elseif mode == "tooltip" then runTooltip()
elseif mode == "viewmodel" then runViewModel()
elseif mode == "ordering" then runOrdering()
else error("unknown metrics mode: " .. tostring(mode)) end
