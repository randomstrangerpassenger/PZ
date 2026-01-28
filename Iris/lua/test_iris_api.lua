--[[
    Iris API Test Script
    
    Run with: lua test_iris_api.lua
]]

-- Load modules
dofile("IrisData.lua")
dofile("IrisApi.lua")

print("\n" .. string.rep("=", 50))
print(" Iris API Test")
print(string.rep("=", 50))

-- Test 1: getTags
print("\n[Test 1] Iris.getTags('Base.Hammer')")
local tags = Iris.getTags("Base.Hammer")
if tags then
    print("  Result: " .. table.concat(tags, ", "))
else
    print("  Result: nil")
end

-- Test 2: hasTag
print("\n[Test 2] Iris.hasTag('Base.Hammer', 'Tool.1-B')")
local result = Iris.hasTag("Base.Hammer", "Tool.1-B")
print("  Result: " .. tostring(result))

print("\n[Test 3] Iris.hasTag('Base.Hammer', 'Combat.2-A')")
result = Iris.hasTag("Base.Hammer", "Combat.2-A")
print("  Result: " .. tostring(result))

-- Test 3: isClassified
print("\n[Test 4] Iris.isClassified('Base.Axe')")
print("  Result: " .. tostring(Iris.isClassified("Base.Axe")))

print("\n[Test 5] Iris.isClassified('Base.NonExistent')")
print("  Result: " .. tostring(Iris.isClassified("Base.NonExistent")))

-- Test 4: getMajorCategory
print("\n[Test 6] Iris.getMajorCategory('Base.Pistol')")
print("  Result: " .. tostring(Iris.getMajorCategory("Base.Pistol")))

-- Test 5: getItemsByTag
print("\n[Test 7] Iris.getItemsByTag('Combat.2-D') -- Long Blades")
local items = Iris.getItemsByTag("Combat.2-D")
print("  Count: " .. #items)
if #items > 0 then
    print("  Sample: " .. items[1])
end

-- Test 6: getStats
print("\n[Test 8] Iris.getStats()")
local stats = Iris.getStats()
print("  Total items: " .. stats.totalItems)
print("  Categories:")
for cat, count in pairs(stats.categoryCounts) do
    print("    " .. cat .. ": " .. count)
end

-- Test 7: debug
print("\n[Test 9] Iris.debug('Base.Katana')")
Iris.debug("Base.Katana")

print("\n" .. string.rep("=", 50))
print(" All tests completed!")
print(string.rep("=", 50))
