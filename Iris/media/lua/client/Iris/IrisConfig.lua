--[[
    IrisConfig.lua - Iris 설정값
    
    디버그 로그, 캐시 설정 등 Iris 동작 제어
]]

local IrisConfig = {}

-- 디버그 모드 (기본: OFF)
-- true일 때만 콘솔에 로그 출력
IrisConfig.DEBUG = true

-- Alt Tooltip 최대 줄 수 (불변, 변경 금지)
IrisConfig.ALT_TOOLTIP_MAX_LINES = 4

-- 캐시 활성화 여부
IrisConfig.CACHE_ENABLED = true

return IrisConfig
