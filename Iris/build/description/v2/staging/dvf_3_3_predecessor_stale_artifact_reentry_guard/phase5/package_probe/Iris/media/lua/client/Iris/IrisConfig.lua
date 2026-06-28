--[[
    IrisConfig.lua - Iris 설정값
    
    디버그 로그, 캐시 설정 등 Iris 동작 제어
]]

local IrisConfig = {}

local DEFAULT_ALT_TOOLTIP_MAX_LINES = 4
local DEFAULT_MAP_ICON_BUTTON_X = 18
local DEFAULT_MAP_ICON_BUTTON_Y = 360
local DEFAULT_MAP_ICON_BUTTON_WIDTH = 32
local DEFAULT_MAP_ICON_BUTTON_HEIGHT = 32

-- 디버그 모드 (기본: OFF)
-- true일 때만 콘솔에 로그 출력
IrisConfig.DEBUG = false

-- Alt Tooltip 최대 줄 수 (불변, 변경 금지)
IrisConfig.ALT_TOOLTIP_MAX_LINES = DEFAULT_ALT_TOOLTIP_MAX_LINES

-- 캐시 활성화 여부
IrisConfig.CACHE_ENABLED = true

-- UseCase debug_lines UI 노출 여부 (기본: OFF)
-- true일 때만 위키 패널에서 REVIEW-only 항목(debug_lines) 표시
-- 주의: IrisConfig.DEBUG는 콘솔 로깅 전용, UI 노출 판단에 사용 금지
IrisConfig.SHOW_DEBUG_USECASES = false

-- 게임 시작 시 IrisDesc 테스트 자동 실행 (개발/검증용)
-- DEBUG=true일 때만 dev TestHarness require 경로를 시도한다.
-- true: 게임 시작 시 TestHarness 자동 실행, 결과 콘솔 출력
-- false: 테스트 실행 안 함 (배포 시 false 설정)
IrisConfig.RUN_TESTS_ON_START = false

-- Iris Browser 독립 버튼 위치
-- 기존 좌측 아이콘 바 아래 배치를 보존하는 기본값
IrisConfig.MAP_ICON_BUTTON = {
    x = DEFAULT_MAP_ICON_BUTTON_X,
    y = DEFAULT_MAP_ICON_BUTTON_Y,
    width = DEFAULT_MAP_ICON_BUTTON_WIDTH,
    height = DEFAULT_MAP_ICON_BUTTON_HEIGHT,
}

return IrisConfig

