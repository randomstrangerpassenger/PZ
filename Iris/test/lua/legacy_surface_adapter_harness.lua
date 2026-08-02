local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local legacyLoadCalls = 0
package.preload["Iris/Data/IrisData"] = function()
    legacyLoadCalls = legacyLoadCalls + 1
    error("standalone legacy module missing")
end
IrisData = nil

local StaticData = require("Iris/API/StaticData")
assert(StaticData.getLegacyIrisData() == nil)
assert(StaticData.getLegacyIrisData() == nil)
assert(legacyLoadCalls == 1)
assert(StaticData.getFailureReason("legacyData") ~= nil)

local function item(fullType, displayName)
    local value = {}
    function value:getFullType() return fullType end
    function value:getFullName() return fullType end
    function value:getDisplayName() return displayName end
    return value
end

IrisData = {ItemGroups={fixture={"Base.Hammer","Base.Apple"}}}
local VariantIndex = require("Iris/UI/Browser/IrisBrowserVariantIndex")
local cache = {itemsByFullType={
    ["Base.Hammer"]=item("Base.Hammer","Hammer"),
    ["Base.Apple"]=item("Base.Apple","Apple"),
}}
local variants = VariantIndex.getGroupVariants(cache, "fixture", StaticData.getLegacyIrisData())
assert(variants and #variants == 2)
assert(variants[1].fullType == "Base.Apple" and variants[2].fullType == "Base.Hammer")
assert(VariantIndex.getGroupVariants(cache, "missing", StaticData.getLegacyIrisData()) == nil)

package.preload["Iris/Data/IrisCapabilities"] = function()
    return { ["Base.Hammer"]={"can_scrap_moveables"} }
end
local UseCases = require("Iris/API/UseCases")
assert(#UseCases.getCapabilities("Base.Hammer") == 1)
assert(UseCases.hasCapability("Base.Hammer", "can_scrap_moveables"))
assert(not UseCases.hasCapability("Base.Hammer", "invented_capability"))

print("IRIS_LEGACY_ADAPTER_PASS missing_load_calls=1 global_fallback=true capability_preserved=true")
