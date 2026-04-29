--[[
    IrisDesc Logger
    
    최소 warn 로거 구현
    
    ⚠️ 헌법: 경고 출력만. 보정/대체/중단 금지.
]]

local IrisDescLogger = {}

---경고 로그 출력
---@param msg string 경고 메시지
function IrisDescLogger.warn(msg)
    print("[Iris] " .. tostring(msg))
end

return IrisDescLogger
