--[[
    IrisMapIcon.lua - 좌측 상단 UI 아이콘 바에 Iris 아이콘 추가
    
    기본 UI 아이콘들(인벤토리, 건강, 배치, 탐색, 지도) 옆에 Iris 아이콘 배치
    클릭 시 IrisBrowser.openSearch() 호출
]]

require "ISUI/ISButton"

local IrisMapIcon = {}

-- 의존성 (lazy load)
local IrisBrowser = nil

local function ensureDeps()
    if not IrisBrowser then
        local ok, result = pcall(require, "Iris/UI/Browser/IrisBrowser")
        if ok then IrisBrowser = result end
    end
end

-- 버튼 인스턴스
IrisMapIcon._button = nil
IrisMapIcon._hooked = false

--- Iris 버튼 클릭 핸들러
function IrisMapIcon.onIrisButtonClick()
    print("[IrisMapIcon] Iris button clicked")
    
    ensureDeps()
    
    if IrisBrowser and IrisBrowser.openSearch then
        IrisBrowser.openSearch()
    else
        print("[IrisMapIcon] ERROR: IrisBrowser.openSearch not available")
    end
end

--- 좌측 상단 UI 바에 아이콘 추가
function IrisMapIcon.addToTopLeftBar()
    print("[IrisMapIcon] Adding Iris icon to top-left UI bar...")
    
    -- ISUIHandler가 있는지 확인
    if not ISUIHandler then
        print("[IrisMapIcon] WARNING: ISUIHandler not found")
        return false
    end
    
    -- isToggleButtonCreated 확인을 위해 OnGameStart에서 호출되어야 함
    local originalGetPlayerInventory = ISUIHandler.getPlayerInventory
    if not originalGetPlayerInventory then
        print("[IrisMapIcon] WARNING: ISUIHandler.getPlayerInventory not found")
        return false
    end
    
    -- ISUIHandler.toggleUI 후킹하여 Iris 버튼 추가
    local originalToggleUI = ISUIHandler.toggleUI
    
    ISUIHandler.toggleUI = function(button)
        -- 원본 호출
        if originalToggleUI then
            originalToggleUI(button)
        end
        
        -- button.internal에 따라 분기
        if button and button.internal == "IRIS" then
            IrisMapIcon.onIrisButtonClick()
        end
    end
    
    print("[IrisMapIcon] ISUIHandler hooked successfully")
    return true
end

--- 화면 렌더링 시 아이콘 추가 (OnGameStart 이후)
function IrisMapIcon.addIrisButton()
    print("[IrisMapIcon] Attempting to add Iris button...")
    
    if IrisMapIcon._hooked then
        print("[IrisMapIcon] Already hooked, skipping")
        return
    end
    
    -- getPlayer가 있어야 버튼 추가 가능
    local player = getPlayer and getPlayer()
    if not player then
        print("[IrisMapIcon] Player not found, will retry later")
        return
    end
    
    -- UI 핸들러의 버튼 패널 찾기
    local uiHandler = getPlayerUIHandler and getPlayerUIHandler(0)
    if not uiHandler then
        print("[IrisMapIcon] UIHandler not found")
        return
    end
    
    -- bottomPanel이 아이콘 바
    local iconBar = uiHandler.bottomPanel
    if not iconBar then
        print("[IrisMapIcon] Icon bar (bottomPanel) not found, trying alternative")
        -- 대안: 직접 버튼 생성하여 화면 좌측 상단에 배치
        IrisMapIcon.createStandaloneButton()
        return
    end
    
    -- 아이콘 바에 버튼 추가
    local btnWidth = 32
    local btnHeight = 32
    local x = iconBar.width  -- 맨 오른쪽에 추가
    local y = 0
    
    local irisBtn = ISButton:new(x, y, btnWidth, btnHeight, "I", iconBar, function()
        IrisMapIcon.onIrisButtonClick()
    end)
    irisBtn:initialise()
    irisBtn.backgroundColor = {r=0.1, g=0.3, b=0.4, a=0.8}
    irisBtn.backgroundColorMouseOver = {r=0.2, g=0.4, b=0.5, a=0.9}
    irisBtn.borderColor = {r=0.4, g=0.6, b=0.7, a=1}
    irisBtn.textColor = {r=0.6, g=0.9, b=1.0, a=1}
    irisBtn.tooltip = "Iris Browser"
    iconBar:addChild(irisBtn)
    
    IrisMapIcon._button = irisBtn
    IrisMapIcon._hooked = true
    print("[IrisMapIcon] Iris button added to icon bar")
end

--- 화면 좌측 상단에 독립 버튼 생성 (지도 아이콘 바로 밑)
function IrisMapIcon.createStandaloneButton()
    print("[IrisMapIcon] Creating standalone button below map icon...")
    
    -- 좌측 상단 아이콘 바의 맨 아래(지도 아이콘 밑)에 버튼 생성
    -- 좌측 상단 아이콘 바의 맨 아래(지도 아이콘 밑)에 버튼 생성
    -- 8개 아이콘: 무기2 + 인벤/건강/제작/배치/탐색/지도
    local btnWidth = 32
    local btnHeight = 32
    local x = 18  -- 좌측 아이콘들과 정렬
    local y = 360  -- 지도 아이콘 밑 (조금 위로 조정)
    
    local irisBtn = ISButton:new(x, y, btnWidth, btnHeight, "", nil, function()
        IrisMapIcon.onIrisButtonClick()
    end)
    irisBtn:initialise()
    irisBtn:instantiate()
    
    -- 이미지 설정
    local tex = getTexture("media/textures/Iris-logo_32px.png")
    if tex then
        irisBtn:setImage(tex)
    else
        print("[IrisMapIcon] WARNING: Iris-logo_32px.png not found")
        irisBtn.title = "I"  -- 이미지 실패 시 텍스트 복구
    end
    
    -- 스타일 조정 (투명 배경)
    irisBtn:setEnable(true)
    irisBtn.backgroundColor = {r=0, g=0, b=0, a=0}  -- 완전 투명 배경
    irisBtn.backgroundColorMouseOver = {r=0.2, g=0.2, b=0.2, a=0.5}  -- 마우스 오버 시 약간 어둡게
    irisBtn.borderColor = {r=0, g=0, b=0, a=0}  -- 테두리 없음
    irisBtn.tooltip = "Iris Browser"
    
    irisBtn:addToUIManager()
    irisBtn:setVisible(true)
    
    IrisMapIcon._button = irisBtn
    IrisMapIcon._hooked = true
    print("[IrisMapIcon] Standalone Iris button created below map icon")
end

--- OnGameStart 이벤트에서 버튼 추가 시도
function IrisMapIcon.onGameStart()
    print("[IrisMapIcon] OnGameStart fired, adding button...")
    IrisMapIcon.createStandaloneButton()
end

--- 초기화
function IrisMapIcon.init()
    print("[IrisMapIcon] Initializing...")
    
    -- OnGameStart 이벤트 등록
    if Events and Events.OnGameStart then
        Events.OnGameStart.Add(IrisMapIcon.onGameStart)
        print("[IrisMapIcon] OnGameStart event registered")
    else
        print("[IrisMapIcon] WARNING: Events.OnGameStart not available")
        -- 직접 버튼 생성 시도
        IrisMapIcon.createStandaloneButton()
    end
    
    print("[IrisMapIcon] Initialization complete")
end

return IrisMapIcon
