--[[
    NerveLogger.lua
    Nerve 전용 로거 모듈
    
    v1.0 - Dedicated File Logging
    
    기능:
    - 전용 로그 파일 출력 (Zomboid/Lua/Nerve/nerve.log)
    - 콘솔 동시 출력
    - 로그 레벨 지원 (DEBUG, INFO, WARN, ERROR)
    - 타임스탬프 포함
    - 게임 시작 시 이전 로그 백업
]]

--------------------------------------------------------------------------------
-- NerveLogger 모듈
--------------------------------------------------------------------------------

local NerveLogger = {}

-- 로그 레벨
NerveLogger.LEVEL = {
    DEBUG = 1,
    INFO = 2,
    WARN = 3,
    ERROR = 4,
}

-- 레벨 이름
local LEVEL_NAMES = {
    [1] = "DEBUG",
    [2] = "INFO",
    [3] = "WARN",
    [4] = "ERROR",
}

-- 설정
NerveLogger.config = {
    logToFile = true,           -- 파일에 로그 출력
    logToConsole = true,        -- 콘솔에도 로그 출력
    minLevel = 2,               -- 최소 로그 레벨 (INFO)
    logDir = "Nerve",           -- 로그 디렉토리
    logFileName = "nerve.log",  -- 로그 파일 이름
    maxBackups = 3,             -- 최대 백업 파일 수
}

-- 초기화 상태
local initialized = false
local sessionStartTime = nil

--------------------------------------------------------------------------------
-- 유틸리티
--------------------------------------------------------------------------------

-- 타임스탬프 생성
local function getTimestamp()
    local gameTime = getGameTime()
    if gameTime then
        local hour = gameTime:getHour()
        local minute = gameTime:getMinutes()
        return string.format("[%02d:%02d]", hour, minute)
    end
    
    -- 게임 시간을 사용할 수 없으면 시스템 시간 사용
    local time = os.time()
    if time then
        return os.date("[%H:%M:%S]", time)
    end
    
    return "[--:--:--]"
end

-- 세션 시작 타임스탬프
local function getSessionTimestamp()
    if not sessionStartTime then
        local time = os.time()
        if time then
            sessionStartTime = os.date("%Y%m%d_%H%M%S", time)
        else
            sessionStartTime = "unknown"
        end
    end
    return sessionStartTime
end

--------------------------------------------------------------------------------
-- 파일 로깅
--------------------------------------------------------------------------------

-- 로그 파일에 쓰기
local function writeToFile(message)
    if not NerveLogger.config.logToFile then
        return
    end
    
    -- 파일 쓰기 시도
    local success, err = pcall(function()
        local writer = getFileWriter(
            NerveLogger.config.logDir .. "/" .. NerveLogger.config.logFileName,
            true,   -- create if missing
            true    -- append mode
        )
        
        if writer then
            writer:writeln(message)
            writer:close()
        end
    end)
    
    if not success and NerveLogger.config.logToConsole then
        -- 파일 쓰기 실패 시 콘솔에만 출력
        print("[NerveLogger] File write failed: " .. tostring(err))
    end
end

-- 로그 파일 백업
local function backupLogFile()
    local success = pcall(function()
        local logPath = NerveLogger.config.logDir .. "/" .. NerveLogger.config.logFileName
        
        -- 기존 로그 파일 읽기 시도
        local reader = getFileReader(logPath, false)
        if not reader then
            return  -- 기존 파일 없음
        end
        
        -- 내용 읽기
        local lines = {}
        local line = reader:readLine()
        while line do
            table.insert(lines, line)
            line = reader:readLine()
        end
        reader:close()
        
        if #lines == 0 then
            return  -- 빈 파일
        end
        
        -- 백업 파일로 저장
        local backupName = NerveLogger.config.logDir .. "/nerve_" .. getSessionTimestamp() .. ".log"
        local writer = getFileWriter(backupName, true, false)
        if writer then
            for _, l in ipairs(lines) do
                writer:writeln(l)
            end
            writer:close()
        end
    end)
    
    return success
end

-- 새 세션 시작 헤더 쓰기
local function writeSessionHeader()
    local header = string.format(
        "\n" ..
        "================================================================================\n" ..
        " NERVE LOG SESSION - %s\n" ..
        " Nerve v%s\n" ..
        "================================================================================",
        getSessionTimestamp(),
        (Nerve and Nerve.VERSION) or "unknown"
    )
    writeToFile(header)
end

--------------------------------------------------------------------------------
-- 로깅 API
--------------------------------------------------------------------------------

-- 로그 출력
-- @param level: 로그 레벨 (NerveLogger.LEVEL.*)
-- @param ...: 로그 메시지
function NerveLogger.log(level, ...)
    -- 레벨 체크
    if level < NerveLogger.config.minLevel then
        return
    end
    
    -- 메시지 조합
    local parts = {}
    for i = 1, select("#", ...) do
        local v = select(i, ...)
        table.insert(parts, tostring(v))
    end
    local message = table.concat(parts, " ")
    
    -- 포맷팅
    local levelName = LEVEL_NAMES[level] or "???"
    local timestamp = getTimestamp()
    local formatted = string.format("%s [Nerve/%s] %s", timestamp, levelName, message)
    
    -- 콘솔 출력
    if NerveLogger.config.logToConsole then
        print(formatted)
    end
    
    -- 파일 출력
    if NerveLogger.config.logToFile then
        writeToFile(formatted)
    end
end

-- 편의 함수들
function NerveLogger.debug(...)
    NerveLogger.log(NerveLogger.LEVEL.DEBUG, ...)
end

function NerveLogger.info(...)
    NerveLogger.log(NerveLogger.LEVEL.INFO, ...)
end

function NerveLogger.warn(...)
    NerveLogger.log(NerveLogger.LEVEL.WARN, ...)
end

function NerveLogger.error(...)
    NerveLogger.log(NerveLogger.LEVEL.ERROR, ...)
end

--------------------------------------------------------------------------------
-- 초기화
--------------------------------------------------------------------------------

-- 로거 초기화
function NerveLogger.init()
    if initialized then
        return
    end
    
    -- NerveConfig에서 설정 로드
    if NerveConfig and NerveConfig.logging then
        if NerveConfig.logging.toFile ~= nil then
            NerveLogger.config.logToFile = NerveConfig.logging.toFile
        end
        if NerveConfig.logging.toConsole ~= nil then
            NerveLogger.config.logToConsole = NerveConfig.logging.toConsole
        end
        if NerveConfig.logging.minLevel then
            NerveLogger.config.minLevel = NerveConfig.logging.minLevel
        end
    end
    
    -- 디버그 모드면 DEBUG 레벨로
    if NerveConfig and NerveConfig.debug then
        NerveLogger.config.minLevel = NerveLogger.LEVEL.DEBUG
    end
    
    -- 이전 로그 백업
    backupLogFile()
    
    -- 세션 헤더 쓰기
    writeSessionHeader()
    
    initialized = true
    NerveLogger.info("Logger initialized (file=" .. tostring(NerveLogger.config.logToFile) .. ")")
end

-- 디버그 모드 설정
function NerveLogger.setDebugMode(enabled)
    if enabled then
        NerveLogger.config.minLevel = NerveLogger.LEVEL.DEBUG
    else
        NerveLogger.config.minLevel = NerveLogger.LEVEL.INFO
    end
end

--------------------------------------------------------------------------------
-- Nerve에 등록
--------------------------------------------------------------------------------

Nerve = Nerve or {}
Nerve.Logger = NerveLogger

return NerveLogger
