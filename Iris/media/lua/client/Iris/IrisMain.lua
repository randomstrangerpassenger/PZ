--[[
    IrisMain.lua - Iris 모드 엔트리 포인트

    Iris는 100% Lua 기반 위키피디아형 아이템 정보 모드입니다.
    게임플레이에 영향 없이 아이템 정보를 제공합니다.

    핵심 원칙:
    - Client-only 정보 레이어 (게임플레이 영향 0)
    - Alt 키: 4줄 툴팁 오버레이
    - 우클릭 -> "Iris: 더보기" 위키 패널

    로드 순서: allowlist -> validator -> ruleset
]]

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create({ printFallback = true })
local safeRequire = bootstrap.safeRequire
local ProtectedCall = require("Iris/Util/IrisProtectedCall")
local debug = bootstrap.debug
local warn = bootstrap.warn
local logError = bootstrap.logError

debug("[Iris:IrisMain] ========== MODULE LOAD START ==========")

local Iris = {}

-- 모듈 참조
Iris.Config = nil
Iris.API = nil

-- 초기화 상태
Iris._initialized = false

local function loadModule(moduleName)
    return function()
        return safeRequire(moduleName)
    end
end

local function assignApi(moduleResult)
    Iris.API = moduleResult
end

local function hookTooltip(moduleResult)
    if not moduleResult or type(moduleResult.hookTooltip) ~= "function" then
        return false
    end
    moduleResult.hookTooltip()
    return true
end

local function installBulletReloadCompat(moduleResult)
    if not moduleResult or type(moduleResult.install) ~= "function" then
        return false
    end
    moduleResult.install()
    return true
end

local function installContextMenuTextureCompat(moduleResult)
    if not moduleResult or type(moduleResult.install) ~= "function" then
        return false
    end
    moduleResult.install()
    return true
end

local function hookContextMenu(moduleResult)
    if not moduleResult or type(moduleResult.hookContextMenu) ~= "function" then
        return false
    end
    moduleResult.hookContextMenu()
    return true
end

local function buildBrowserData(moduleResult)
    if not moduleResult or type(moduleResult.build) ~= "function" then
        return false
    end
    moduleResult.build()
    return true
end

local function initMapIcon(moduleResult)
    if not moduleResult or type(moduleResult.init) ~= "function" then
        return false
    end
    moduleResult.init()
    return true
end

local INIT_MODULES = {
    { step = "Step 2a", label = "IrisRecipeIndex", load = loadModule("Iris/Data/IrisRecipeIndex"), ready = "RecipeIndex precompiled data ready" },
    { step = "Step 2b", label = "IrisMoveablesIndex", load = loadModule("Iris/Data/IrisMoveablesIndex"), ready = "MoveablesIndex precompiled data ready" },
    { step = "Step 2c", label = "IrisFixingIndex", load = loadModule("Iris/Data/IrisFixingIndex"), ready = "FixingIndex precompiled data ready" },
    { step = "Step 3", label = "IrisClassifications", load = loadModule("Iris/Data/IrisClassifications"), ready = "IrisClassifications loaded successfully" },
    { step = "Step 4", label = "IrisAPI", load = loadModule("Iris/IrisAPI"), onLoaded = assignApi },
    { step = "Step 5a", label = "IrisAltTooltip", load = loadModule("Iris/UI/Tooltip/IrisAltTooltip"), invoke = hookTooltip, protectedCall = ProtectedCall.ui, unavailable = "hookTooltip() is not available", success = "hookTooltip() success" },
    { step = "Step 5b", label = "IrisContextMenuTextureCompat", load = loadModule("Iris/Compat/IrisContextMenuTextureCompat"), invoke = installContextMenuTextureCompat, protectedCall = ProtectedCall.compat, unavailable = "install() is not available", success = "ContextMenuTextureCompat.install() success" },
    -- validation anchor: require, "Iris/Compat/IrisBulletReloadCompat"; BulletReloadCompat.install()
    { step = "Step 5c", label = "IrisBulletReloadCompat", load = loadModule("Iris/Compat/IrisBulletReloadCompat"), invoke = installBulletReloadCompat, protectedCall = ProtectedCall.compat, unavailable = "install() is not available", success = "BulletReloadCompat.install() success" },
    -- validation anchor: require, "Iris/UI/Wiki/IrisContextMenu"; hookContextMenu()
    { step = "Step 5d", label = "IrisContextMenu", load = loadModule("Iris/UI/Wiki/IrisContextMenu"), invoke = hookContextMenu, protectedCall = ProtectedCall.ui, unavailable = "hookContextMenu() is not available", success = "hookContextMenu() success" },
    { step = "Step 5e", label = "IrisBrowserData", load = loadModule("Iris/UI/Browser/IrisBrowserData"), invoke = buildBrowserData, protectedCall = ProtectedCall.data, unavailable = "build() is not available", success = "BrowserData.build() success" },
    { step = "Step 5f", label = "IrisMapIcon", load = loadModule("Iris/UI/Browser/IrisMapIcon"), invoke = initMapIcon, protectedCall = ProtectedCall.ui, unavailable = "init() is not available", success = "MapIcon.init() success" },
}

local DEV_TESTHARNESS_MODULE = "Iris/Dev/IrisDesc/TestHarness"

local function loadConfig()
    debug("[Iris:initialize] Step 1: Loading IrisConfig...")
    local configOk, configResult = safeRequire("Iris/IrisConfig")
    if configOk then
        Iris.Config = configResult
        debug("[Iris:initialize] Step 1: IrisConfig loaded, DEBUG=" .. tostring(Iris.Config.DEBUG))
        return
    end

    logError("[Iris:initialize] Step 1: FAILED to load IrisConfig: " .. tostring(configResult))
    Iris.Config = { DEBUG = false, ALT_TOOLTIP_MAX_LINES = 4, CACHE_ENABLED = false, RUN_TESTS_ON_START = false }
end

local function runModuleSpec(spec)
    debug("[Iris:initialize] " .. spec.step .. ": Loading " .. spec.label .. "...")

    local moduleOk, moduleResult = spec.load()
    if not moduleOk then
        logError("[Iris:initialize] " .. spec.step .. ": FAILED to load " .. spec.label .. ": " .. tostring(moduleResult))
        return nil
    end

    debug("[Iris:initialize] " .. spec.step .. ": " .. spec.label .. " loaded")
    if spec.onLoaded then
        spec.onLoaded(moduleResult)
    end
    if spec.ready then
        debug("[Iris:initialize] " .. spec.step .. ": " .. spec.ready)
    end

    if spec.invoke then
        local protectedCall = spec.protectedCall or ProtectedCall.engine
        local callOk, callResult = protectedCall(function()
            return spec.invoke(moduleResult)
        end)
        if callOk and callResult ~= false then
            debug("[Iris:initialize] " .. spec.step .. ": " .. spec.success)
        elseif callOk then
            warn("[Iris:initialize] " .. spec.step .. ": " .. spec.label .. "." .. spec.unavailable)
        else
            logError("[Iris:initialize] " .. spec.step .. ": " .. spec.label .. " callback FAILED: " .. tostring(callResult))
        end
    end

    return moduleResult
end

local function runStartupTests()
    if not Iris.Config or Iris.Config.DEBUG ~= true or Iris.Config.RUN_TESTS_ON_START ~= true then
        return
    end

    debug("[Iris:initialize] Step 6: Running IrisDesc tests...")
    local testOk, testResult = safeRequire(DEV_TESTHARNESS_MODULE)
    if not testOk or not testResult or not testResult.runAll then
        logError("[Iris:initialize] Step 6: TestHarness load failed: " .. tostring(testResult))
        return
    end

    local runOk, allPassed = ProtectedCall.data(testResult.runAll)
    if not runOk then
        logError("[Iris:initialize] Step 6: Test execution error: " .. tostring(allPassed))
    elseif allPassed then
        debug("[Iris:initialize] Step 6: All IrisDesc tests PASSED")
    else
        warn("[Iris:initialize] Step 6: Some IrisDesc tests FAILED")
    end
end

--- Iris 초기화
--- OnGameBoot 이벤트에서 1회만 호출
function Iris.initialize()
    debug("[Iris:initialize] ========== INITIALIZE START ==========")

    if Iris._initialized then
        debug("[Iris:initialize] Already initialized, skipping")
        return
    end

    loadConfig()
    debug("[Iris:initialize] Step 2: Loading Data Indexes...")
    for _, spec in ipairs(INIT_MODULES) do
        runModuleSpec(spec)
    end
    runStartupTests()

    -- 완료
    Iris._initialized = true
    debug("[Iris:initialize] ========== INITIALIZE COMPLETE ==========")
end

-- 이벤트 등록
debug("[Iris:IrisMain] Registering event handlers...")

if Events then
    debug("[Iris:IrisMain] Events table exists")

    -- OnGameBoot is the sole initializer. P3-5 event tracing showed it runs
    -- before OnCreatePlayer and OnGameStart, which only repeated initialize().
    if Events.OnGameBoot and Events.OnGameBoot.Add then
        debug("[Iris:IrisMain] Registering OnGameBoot...")
        Events.OnGameBoot.Add(function()
            debug("[Iris] OnGameBoot fired - initializing...")
            Iris.initialize()
        end)
        debug("[Iris:IrisMain] OnGameBoot registered")
    end
else
    warn("[Iris:IrisMain] Events table is nil")
end

debug("[Iris:IrisMain] ========== MODULE LOAD COMPLETE ==========")

return Iris
