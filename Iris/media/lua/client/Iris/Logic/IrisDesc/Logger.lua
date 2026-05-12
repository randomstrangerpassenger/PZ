--[[
    IrisDesc Logger

    IrisLogger adapter for the description pipeline.

    ⚠️ 헌법: 로그만 담당. 보정/대체/중단 금지.
]]

local IrisDescLogger = {}
local logger = require("Iris/Util/IrisLogger")

function IrisDescLogger.debug(msg)
    logger.debug(msg)
end

function IrisDescLogger.isDebugEnabled()
    return logger.isDebugEnabled()
end

function IrisDescLogger.info(msg)
    logger.info(msg)
end

---경고 로그 출력
---@param msg string 경고 메시지
function IrisDescLogger.warn(msg)
    logger.warn(msg)
end

function IrisDescLogger.error(msg)
    logger.error(msg)
end

return IrisDescLogger

