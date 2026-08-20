local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local ObjectAccess = require("Iris/Util/IrisObjectAccess")
local target = { value = 7 }
function target:zero() return self.value end
function target:one(argument) return argument end
function target:two(left, right) return left .. right end
function target:nilResult() return nil end
function target:falseResult() return false end
function target:zeroResult() return 0 end
function target:explode() error("fixture explosion") end

local ok, value = ObjectAccess.call0(target, "zero")
assert(ok and value == 7)
ok, value = ObjectAccess.call1(target, "one", "argument")
assert(ok and value == "argument")
ok, value = ObjectAccess.call1(target, "one", nil)
assert(ok and value == nil)
for _, argument in ipairs({ false, 0 }) do
    local genericOk, genericValue = ObjectAccess.call(target, "one", argument)
    local fastOk, fastValue = ObjectAccess.call1(target, "one", argument)
    assert(genericOk == fastOk and genericValue == fastValue)
end
ok, value = ObjectAccess.call(target, "two", "a", "b")
assert(ok and value == "ab")

for _, methodName in ipairs({ "nilResult", "falseResult", "zeroResult" }) do
    local genericOk, genericValue = ObjectAccess.call(target, methodName)
    local fastOk, fastValue = ObjectAccess.call0(target, methodName)
    assert(genericOk == fastOk and genericValue == fastValue)
end

local genericErrorOk = ObjectAccess.call(target, "explode")
local fastErrorOk = ObjectAccess.call0(target, "explode")
assert(genericErrorOk == false and fastErrorOk == false)
local genericOneErrorOk = ObjectAccess.call(target, "explode", "argument")
local fastOneErrorOk = ObjectAccess.call1(target, "explode", "argument")
assert(genericOneErrorOk == false and fastOneErrorOk == false)
assert(ObjectAccess.call0(target, "missing") == false)
assert(ObjectAccess.call1(nil, "one", 1) == false)

print("IRIS_OBJECT_ACCESS_FAST_PATH_PASS generic_routing=predecessor")
