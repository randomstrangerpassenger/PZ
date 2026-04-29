--[[
    IrisMapIcon.lua - 좌측 상단 UI에 Iris 아이콘 추가

    설계 원칙 (호환성 봉인):
    - 전역 함수 override 금지 (ISUIHandler.toggleUI 등 덮어쓰지 않음)
    - 독립 버튼을 "추가"만 함 (다른 모드와 충돌 없음)
    - UI 실패해도 Iris 데이터 기능은 정상 동작
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

-- 상태
IrisMapIcon._button = nil
IrisMapIcon._installed = false  -- UI 버튼 설치 여부 (재진입 방지)

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

--- 화면 좌측 상단에 독립 버튼 생성 (지도 아이콘 바로 밑)
--- 전역 함수를 override하지 않고, 버튼을 직접 추가만 함
function IrisMapIcon.createStandaloneButton()
    -- 재진입 방지: 플래그 + 실제 버튼 존재 여부 둘 다 확인
    -- (게임 재시작 시 플래그는 남아있지만 버튼은 사라질 수 있음)
    if IrisMapIcon._installed and IrisMapIcon._button then
        -- 버튼이 UIManager에 실제로 존재하는지 추가 확인
        if IrisMapIcon._button:getIsVisible() ~= nil then
            print("[IrisMapIcon] Already installed, skipping")
            return true
        end
        -- 버튼 객체가 무효화됨 - 재설치 필요
        IrisMapIcon._installed = false
        IrisMapIcon._button = nil
    end

    print("[IrisMapIcon] Creating standalone button...")

    -- 좌측 상단 아이콘 바 밑 (지도 아이콘 밑)
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
    IrisMapIcon._installed = true
    print("[IrisMapIcon] Standalone Iris button created below map icon")
end

--- OnGameStart 이벤트 핸들러
function IrisMapIcon.onGameStart()
    print("[IrisMapIcon] OnGameStart fired")
    IrisMapIcon.createStandaloneButton()
end

--- 게임 종료/메뉴 복귀 시 정리 (라이프사이클 안정성)
function IrisMapIcon.onMainMenuEnter()
    print("[IrisMapIcon] MainMenuEnter - cleaning up")
    if IrisMapIcon._button then
        pcall(function() IrisMapIcon._button:removeFromUIManager() end)
        IrisMapIcon._button = nil
    end
    IrisMapIcon._installed = false
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
    end

    -- OnMainMenuEnter 이벤트 등록 (라이프사이클 정리)
    if Events and Events.OnMainMenuEnter then
        Events.OnMainMenuEnter.Add(IrisMapIcon.onMainMenuEnter)
        print("[IrisMapIcon] OnMainMenuEnter event registered")
    end

    print("[IrisMapIcon] Initialization complete")
end

return IrisMapIcon
