--[[
    IrisMain.lua - Iris 모드 엔트리 포인트
    
    Iris는 100% Lua 기반 위키피디아형 아이템 정보 모드입니다.
    게임플레이에 영향 없이 아이템 정보를 제공합니다.
    
    핵심 원칙:
    - Client-only 정보 레이어 (게임플레이 영향 0)
    - Alt 키: 4줄 툴팁 오버레이
    - 우클릭 → "Iris: 더보기" 위키 패널
    
    로드 순서: allowlist → validator → ruleset
]]

print("[Iris:IrisMain] ========== MODULE LOAD START ==========")

local Iris = {}

-- 모듈 참조
Iris.Config = nil
Iris.API = nil

-- 초기화 상태
Iris._initialized = false

--- Iris 초기화
--- OnGameStart 이벤트에서 1회만 호출
function Iris.initialize()
    print("[Iris:initialize] ========== INITIALIZE START ==========")
    
    if Iris._initialized then
        print("[Iris:initialize] Already initialized, skipping")
        return
    end
    
    -- Step 1: 설정 로드
    print("[Iris:initialize] Step 1: Loading IrisConfig...")
    local configOk, configResult = pcall(require, "Iris/IrisConfig")
    if configOk then
        Iris.Config = configResult
        print("[Iris:initialize] Step 1: IrisConfig loaded, DEBUG=" .. tostring(Iris.Config.DEBUG))
    else
        print("[Iris:initialize] Step 1: FAILED to load IrisConfig: " .. tostring(configResult))
        Iris.Config = { DEBUG = true, ALT_TOOLTIP_MAX_LINES = 4, CACHE_ENABLED = false }
    end
    
    print("[Iris:initialize] Step 2: Loading Data Indexes...")
    
    -- Step 2a: RecipeIndex
    print("[Iris:initialize] Step 2a: Loading IrisRecipeIndex...")
    local recipeOk, recipeResult = pcall(require, "Iris/Data/IrisRecipeIndex")
    if recipeOk then
        print("[Iris:initialize] Step 2a: IrisRecipeIndex loaded")
        local buildOk, buildErr = pcall(function() recipeResult.build() end)
        if buildOk then
            print("[Iris:initialize] Step 2a: RecipeIndex.build() success")
        else
            print("[Iris:initialize] Step 2a: RecipeIndex.build() FAILED: " .. tostring(buildErr))
        end
    else
        print("[Iris:initialize] Step 2a: FAILED to load IrisRecipeIndex: " .. tostring(recipeResult))
    end
    
    -- Step 2b: MoveablesIndex
    print("[Iris:initialize] Step 2b: Loading IrisMoveablesIndex...")
    local moveOk, moveResult = pcall(require, "Iris/Data/IrisMoveablesIndex")
    if moveOk then
        print("[Iris:initialize] Step 2b: IrisMoveablesIndex loaded")
        local buildOk, buildErr = pcall(function() moveResult.build() end)
        if buildOk then
            print("[Iris:initialize] Step 2b: MoveablesIndex.build() success")
        else
            print("[Iris:initialize] Step 2b: MoveablesIndex.build() FAILED: " .. tostring(buildErr))
        end
    else
        print("[Iris:initialize] Step 2b: FAILED to load IrisMoveablesIndex: " .. tostring(moveResult))
    end
    
    -- Step 2c: FixingIndex
    print("[Iris:initialize] Step 2c: Loading IrisFixingIndex...")
    local fixOk, fixResult = pcall(require, "Iris/Data/IrisFixingIndex")
    if fixOk then
        print("[Iris:initialize] Step 2c: IrisFixingIndex loaded")
        local buildOk, buildErr = pcall(function() fixResult.build() end)
        if buildOk then
            print("[Iris:initialize] Step 2c: FixingIndex.build() success")
        else
            print("[Iris:initialize] Step 2c: FixingIndex.build() FAILED: " .. tostring(buildErr))
        end
    else
        print("[Iris:initialize] Step 2c: FAILED to load IrisFixingIndex: " .. tostring(fixResult))
    end
    
    -- Step 3: Rule Engine
    print("[Iris:initialize] Step 3: Loading IrisRuleLoader...")
    local loaderOk, loaderResult = pcall(require, "Iris/Rules/engine/IrisRuleLoader")
    if loaderOk then
        print("[Iris:initialize] Step 3: IrisRuleLoader loaded")
        local loadOk, loadErr = pcall(function() return loaderResult.load() end)
        if loadOk then
            print("[Iris:initialize] Step 3: RuleLoader.load() success")
        else
            print("[Iris:initialize] Step 3: RuleLoader.load() FAILED: " .. tostring(loadErr))
        end
    else
        print("[Iris:initialize] Step 3: FAILED to load IrisRuleLoader: " .. tostring(loaderResult))
    end
    
    -- Step 4: API
    print("[Iris:initialize] Step 4: Loading IrisAPI...")
    local apiOk, apiResult = pcall(require, "Iris/IrisAPI")
    if apiOk then
        Iris.API = apiResult
        print("[Iris:initialize] Step 4: IrisAPI loaded")
    else
        print("[Iris:initialize] Step 4: FAILED to load IrisAPI: " .. tostring(apiResult))
    end
    
    -- Step 5: UI Hooks
    print("[Iris:initialize] Step 5: Loading UI modules...")
    
    -- Step 5a: AltTooltip
    print("[Iris:initialize] Step 5a: Loading IrisAltTooltip...")
    local tooltipOk, tooltipResult = pcall(require, "Iris/UI/Tooltip/IrisAltTooltip")
    if tooltipOk then
        print("[Iris:initialize] Step 5a: IrisAltTooltip loaded")
        local hookOk, hookErr = pcall(function() tooltipResult.hookTooltip() end)
        if hookOk then
            print("[Iris:initialize] Step 5a: hookTooltip() success")
        else
            print("[Iris:initialize] Step 5a: hookTooltip() FAILED: " .. tostring(hookErr))
        end
    else
        print("[Iris:initialize] Step 5a: FAILED to load IrisAltTooltip: " .. tostring(tooltipResult))
    end
    
    -- Step 5b: ContextMenu
    print("[Iris:initialize] Step 5b: Loading IrisContextMenu...")
    local menuOk, menuResult = pcall(require, "Iris/UI/Wiki/IrisContextMenu")
    if menuOk then
        print("[Iris:initialize] Step 5b: IrisContextMenu loaded")
        local hookOk, hookErr = pcall(function() menuResult.hookContextMenu() end)
        if hookOk then
            print("[Iris:initialize] Step 5b: hookContextMenu() success")
        else
            print("[Iris:initialize] Step 5b: hookContextMenu() FAILED: " .. tostring(hookErr))
        end
    else
        print("[Iris:initialize] Step 5b: FAILED to load IrisContextMenu: " .. tostring(menuResult))
    end
    
    -- Step 5c: BrowserData
    print("[Iris:initialize] Step 5c: Loading IrisBrowserData...")
    local browserDataOk, browserDataResult = pcall(require, "Iris/UI/Browser/IrisBrowserData")
    if browserDataOk then
        print("[Iris:initialize] Step 5c: IrisBrowserData loaded")
        local buildOk, buildErr = pcall(function() browserDataResult.build() end)
        if buildOk then
            print("[Iris:initialize] Step 5c: BrowserData.build() success")
        else
            print("[Iris:initialize] Step 5c: BrowserData.build() FAILED: " .. tostring(buildErr))
        end
    else
        print("[Iris:initialize] Step 5c: FAILED to load IrisBrowserData: " .. tostring(browserDataResult))
    end
    
    -- Step 5d: MapIcon
    print("[Iris:initialize] Step 5d: Loading IrisMapIcon...")
    local iconOk, iconResult = pcall(require, "Iris/UI/Browser/IrisMapIcon")
    if iconOk then
        print("[Iris:initialize] Step 5d: IrisMapIcon loaded")
        local initOk, initErr = pcall(function() iconResult.init() end)
        if initOk then
            print("[Iris:initialize] Step 5d: MapIcon.init() success")
        else
            print("[Iris:initialize] Step 5d: MapIcon.init() FAILED: " .. tostring(initErr))
        end
    else
        print("[Iris:initialize] Step 5d: FAILED to load IrisMapIcon: " .. tostring(iconResult))
    end
    
    -- 완료
    Iris._initialized = true
    print("[Iris:initialize] ========== INITIALIZE COMPLETE ==========")
end

--- OnGameStart 이벤트 핸들러
local function onGameStart()
    print("[Iris:onGameStart] ========== OnGameStart EVENT FIRED ==========")
    local ok, err = pcall(Iris.initialize)
    if not ok then
        print("[Iris:onGameStart] CRITICAL ERROR in initialize(): " .. tostring(err))
    end
end

-- 이벤트 등록 (여러 이벤트에 등록하여 확실하게 초기화)
print("[Iris:IrisMain] Registering event handlers...")

if Events then
    print("[Iris:IrisMain] Events table exists")
    
    -- OnGameStart 등록
    if Events.OnGameStart and Events.OnGameStart.Add then
        print("[Iris:IrisMain] Registering OnGameStart...")
        Events.OnGameStart.Add(onGameStart)
        print("[Iris:IrisMain] OnGameStart registered")
    end
    
    -- OnMainMenuEnter 등록 (메인 메뉴 진입 시)
    if Events.OnMainMenuEnter and Events.OnMainMenuEnter.Add then
        print("[Iris:IrisMain] Registering OnMainMenuEnter...")
        Events.OnMainMenuEnter.Add(function()
            print("[Iris] OnMainMenuEnter fired")
        end)
    end
    
    -- OnGameBoot 등록 (게임 부팅 시)
    if Events.OnGameBoot and Events.OnGameBoot.Add then
        print("[Iris:IrisMain] Registering OnGameBoot...")
        Events.OnGameBoot.Add(function()
            print("[Iris] OnGameBoot fired - initializing...")
            Iris.initialize()
        end)
        print("[Iris:IrisMain] OnGameBoot registered")
    end
    
    -- OnCreatePlayer 등록 (플레이어 생성 시 - 확실한 게임 시작)
    if Events.OnCreatePlayer and Events.OnCreatePlayer.Add then
        print("[Iris:IrisMain] Registering OnCreatePlayer...")
        Events.OnCreatePlayer.Add(function(playerNum)
            print("[Iris] OnCreatePlayer fired for player " .. tostring(playerNum))
            Iris.initialize()
        end)
        print("[Iris:IrisMain] OnCreatePlayer registered")
    end
else
    print("[Iris:IrisMain] WARNING: Events table is nil")
end

print("[Iris:IrisMain] ========== MODULE LOAD COMPLETE ==========")

return Iris

