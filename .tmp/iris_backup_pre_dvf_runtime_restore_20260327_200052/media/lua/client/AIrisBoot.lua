--[[
    AIrisBoot.lua - Iris 모드 부트스트래퍼
    
    PZ가 자동 로드하는 엔트리 포인트.
    media/lua/client/ 바로 아래에 있어야 자동 실행됨.
]]

print("!!!!! IRIS BOOTSTRAP: START LOAD !!!!!")

-- Iris 메인 모듈 로드 (에러 캐치)
local success, errOrModule = pcall(require, "Iris/IrisMain")

if success then
    print("!!!!! IRIS BOOTSTRAP: IrisMain loaded successfully !!!!!")
else
    print("!!!!! IRIS BOOTSTRAP: FAILED to load IrisMain: " .. tostring(errOrModule) .. " !!!!!")
end

print("[Iris] Bootstrap complete")


