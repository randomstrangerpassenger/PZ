--[[
    AIrisBoot.lua - Iris 모드 부트스트래퍼
    
    PZ가 자동 로드하는 엔트리 포인트.
    media/lua/client/ 바로 아래에 있어야 자동 실행됨.
]]

print("[Iris] Bootstrap start")

local ProtectedCall = require("Iris/Util/IrisProtectedCall")

-- Iris 메인 모듈 로드 (에러 캐치)
local success, errOrModule = ProtectedCall.require("Iris/IrisMain")

if success then
    print("[Iris] IrisMain loaded")
else
    print("[Iris] IrisMain load failed: " .. tostring(errOrModule))
end

print("[Iris] Bootstrap complete")


