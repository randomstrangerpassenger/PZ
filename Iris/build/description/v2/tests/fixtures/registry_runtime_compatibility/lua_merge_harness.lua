local moduleRoot = arg[1]
local expectedCount = tonumber(arg[2])

if not moduleRoot or not expectedCount then
    io.stderr:write("usage: lua_merge_harness.lua <client-lua-root> <expected-count>\n")
    os.exit(2)
end

package.path = moduleRoot .. "/?.lua;" .. package.path

local data = require("Iris/Data/IrisLayer3DataChunks")
if type(data) ~= "table" then
    io.stderr:write("runtime chunk manifest did not reconstruct a table\n")
    os.exit(2)
end

local function asciiLower(value)
    return (value:gsub("%u", string.lower))
end

local exactCount = 0
local comparisonMembers = {}
for key, payload in pairs(data) do
    if type(key) ~= "string" or type(payload) ~= "table" then
        io.stderr:write("runtime reconstruction has an invalid key or payload\n")
        os.exit(2)
    end
    exactCount = exactCount + 1
    local comparisonKey = asciiLower(key)
    local members = comparisonMembers[comparisonKey]
    if not members then
        members = {}
        comparisonMembers[comparisonKey] = members
    end
    members[#members + 1] = key
end

local collisionGroupCount = 0
for _, members in pairs(comparisonMembers) do
    if #members > 1 then
        collisionGroupCount = collisionGroupCount + 1
    end
end

if exactCount ~= expectedCount then
    io.stderr:write(
        string.format("expected %d exact keys, reconstructed %d\n", expectedCount, exactCount)
    )
    os.exit(2)
end

io.write(
    string.format(
        '{"collision_group_count":%d,"exact_key_count":%d,"status":"PASS"}\n',
        collisionGroupCount,
        exactCount
    )
)
