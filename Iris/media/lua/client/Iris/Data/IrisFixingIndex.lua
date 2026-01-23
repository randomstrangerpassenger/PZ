--[[
    IrisFixingIndex.lua - Fixing 인덱스
    
    OnGameStart 이벤트에서 1회만 빌드.
    다른 훅 포인트 사용 금지 (재현성 보장).
    
    인덱스 구조:
    - fixers: Set<fullType> (Fixer 역할로 등록된 아이템)
]]

local IrisFixingIndex = {}

-- 인덱스 데이터
IrisFixingIndex._fixers = {}   -- Set<fullType>
IrisFixingIndex._built = false

--- 인덱스 빌드 (OnGameStart에서 1회만 호출)
function IrisFixingIndex.build()
    if IrisFixingIndex._built then
        return
    end
    
    -- Fixing은 PZ의 Java 객체이므로 일반 테이블처럼 순회할 수 없음
    -- getFixing() 함수 사용이 필요하지만, OnGameBoot에서는 아직 사용 불가
    -- 현재는 빈 인덱스로 초기화하고, 나중에 OnGameStart에서 빌드
    -- 또는 수동 오버라이드로 처리
    
    -- 안전하게 Fixing 관련 데이터 접근 시도
    local ok, err = pcall(function()
        -- ScriptManager를 통한 Fixing 접근 시도
        if ScriptManager and ScriptManager.instance then
            local fixings = ScriptManager.instance:getAllFixing()
            if fixings and fixings.size then
                for i = 0, fixings:size() - 1 do
                    local fixingDef = fixings:get(i)
                    if fixingDef and fixingDef.getFixerList then
                        local fixerList = fixingDef:getFixerList()
                        if fixerList and fixerList.size then
                            for j = 0, fixerList:size() - 1 do
                                local fixer = fixerList:get(j)
                                if fixer and fixer.getFixerType then
                                    local fixerType = fixer:getFixerType()
                                    if fixerType then
                                        IrisFixingIndex._fixers[tostring(fixerType)] = true
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end
    end)
    
    if not ok then
        print("[IrisFixingIndex] WARNING: Fixing scan failed or not available yet: " .. tostring(err))
    end
    
    IrisFixingIndex._built = true
end

--- 아이템이 Fixer 역할인지 확인
--- @param fullType string
--- @return boolean
function IrisFixingIndex.isFixer(fullType)
    return IrisFixingIndex._fixers[fullType] == true
end

--- Fixer 역할이 특정 role과 일치하는지
--- @param fullType string
--- @param role string
--- @return boolean
function IrisFixingIndex.roleEq(fullType, role)
    if role == "Fixer" then
        return IrisFixingIndex.isFixer(fullType)
    end
    return false
end

return IrisFixingIndex
