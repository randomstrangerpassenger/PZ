local repoRoot = assert(arg[1], "repository root argument is required")
local luaRoot = repoRoot .. "/Iris/media/lua/client"
package.path = luaRoot .. "/?.lua;" .. luaRoot .. "/?/init.lua;" .. package.path

local function clearUseCaseModules()
    for moduleName, _ in pairs(package.loaded) do
        if moduleName == "Iris/Data/IrisUseCaseDescriptions" or
            moduleName == "Iris/Data/IrisUseCaseDescriptionsLookup" or
            moduleName:match("^Iris/Data/UseCaseDescriptions/") then
            package.loaded[moduleName] = nil
        end
    end
end

local function findTwoEmptyEntries(lookup)
    local lineCounts = require("Iris/Data/UseCaseDescriptions/LineCountIndex").lineCounts
    local found = {}
    for fullType, _ in pairs(lineCounts) do
        local entry, reason = lookup.get(fullType)
        assert(reason == nil, tostring(reason))
        if entry.debug_lines == nil then
            found[#found + 1] = { fullType = fullType, entry = entry }
            if #found == 2 then break end
        end
    end
    assert(#found == 2, "two sparse debug entries were not found")
    return found
end

-- lazy -> facade: demand chunks remain sparse until the compatibility facade
-- materializes and rehydrates the same require-cached entry objects.
clearUseCaseModules()
local lookup = require("Iris/Data/IrisUseCaseDescriptionsLookup")
local sparse = findTwoEmptyEntries(lookup)
assert(sparse[1].entry.debug_lines == nil and sparse[2].entry.debug_lines == nil)
local facade = require("Iris/Data/IrisUseCaseDescriptions")
assert(facade[sparse[1].fullType] == sparse[1].entry)
assert(facade[sparse[2].fullType] == sparse[2].entry)
assert(type(sparse[1].entry.debug_lines) == "table")
assert(type(sparse[2].entry.debug_lines) == "table")
assert(sparse[1].entry.debug_lines ~= sparse[2].entry.debug_lines)
sparse[1].entry.debug_lines[1] = "mutation-sentinel"
assert(sparse[2].entry.debug_lines[1] == nil)

-- facade -> lazy: every public entry has the historical table shape, and the
-- demand lookup observes the same non-aliased objects after materialization.
clearUseCaseModules()
facade = require("Iris/Data/IrisUseCaseDescriptions")
local entryCount = 0
local emptyA = nil
local emptyB = nil
local nonEmptyCount = 0
for fullType, entry in pairs(facade) do
    if type(fullType) == "string" and fullType:sub(1, 1) ~= "_" then
        entryCount = entryCount + 1
        assert(type(entry.debug_lines) == "table", fullType .. " debug_lines shape")
        if #entry.debug_lines == 0 then
            if emptyA == nil then emptyA = entry
            elseif emptyB == nil then emptyB = entry end
        else
            nonEmptyCount = nonEmptyCount + 1
        end
    end
end
assert(entryCount == 1631, "unexpected facade denominator")
assert(emptyA ~= nil and emptyB ~= nil and emptyA.debug_lines ~= emptyB.debug_lines)

lookup = require("Iris/Data/IrisUseCaseDescriptionsLookup")
local checkedFullType = nil
for fullType, entry in pairs(facade) do
    if type(fullType) == "string" and fullType:sub(1, 1) ~= "_" then
        checkedFullType = fullType
        local loaded, reason = lookup.get(fullType)
        assert(reason == nil and loaded == entry)
        assert(type(loaded.debug_lines) == "table")
        break
    end
end
assert(checkedFullType ~= nil)

print("IRIS_GENERATED_SPARSE_FIELDS_PASS")
print("facade_entries=" .. tostring(entryCount))
print("non_empty_debug_entries=" .. tostring(nonEmptyCount))
