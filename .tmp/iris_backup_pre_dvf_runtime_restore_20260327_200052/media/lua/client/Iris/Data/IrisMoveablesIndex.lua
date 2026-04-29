--[[
    IrisMoveablesIndex.lua - Moveables 인덱스
    
    OnGameStart 이벤트에서 1회만 빌드.
    다른 훅 포인트 사용 금지 (재현성 보장).
    
    인덱스 구조:
    - itemId_registered: Set<fullType>
    - moveablesTag: fullType -> tag
]]

local IrisMoveablesIndex = {}

-- 인덱스 데이터
IrisMoveablesIndex._registered = {}     -- Set<fullType>
IrisMoveablesIndex._tagMapping = {}     -- fullType -> moveablesTag
IrisMoveablesIndex._built = false

-- MoveablesTag allowlist
local ALLOWED_MOVEABLES_TAGS = {
    "Crowbar",
    "SharpKnife",
    "Hammer",
    "Screwdriver",
    "Saw",
    "Wrench"
}

--- 인덱스 빌드 (OnGameStart에서 1회만 호출)
function IrisMoveablesIndex.build()
    if IrisMoveablesIndex._built then
        return
    end
    
    -- ISMoveableDefinitions에서 ToolDefinition 스캔
    if ISMoveableDefinitions and ISMoveableDefinitions.ToolDefinition then
        for toolName, toolDef in pairs(ISMoveableDefinitions.ToolDefinition) do
            -- itemId로 등록된 경우
            if toolDef.itemId then
                IrisMoveablesIndex._registered[toolDef.itemId] = true
            end
            
            -- moveablesTag로 등록된 경우
            if toolDef.tag then
                -- allowlist 확인
                for _, allowedTag in ipairs(ALLOWED_MOVEABLES_TAGS) do
                    if toolDef.tag == allowedTag then
                        -- 이 태그와 매칭되는 아이템들을 찾아야 함
                        -- 실제로는 아이템 스크립트의 Tags를 확인해야 함
                        -- TODO: 런타임에서 매칭 로직 구현
                        break
                    end
                end
            end
        end
    end
    
    IrisMoveablesIndex._built = true
end

--- 아이템 ID가 Moveables에 등록되었는지 확인
--- @param fullType string
--- @return boolean
function IrisMoveablesIndex.isItemIdRegistered(fullType)
    return IrisMoveablesIndex._registered[fullType] == true
end

--- 아이템의 MoveablesTag 조회
--- @param fullType string
--- @return string|nil
function IrisMoveablesIndex.getMoveablesTag(fullType)
    return IrisMoveablesIndex._tagMapping[fullType]
end

--- 아이템이 허용된 MoveablesTag 중 하나에 매칭되는지
--- @param fullType string
--- @param allowedTags table
--- @return boolean
function IrisMoveablesIndex.tagIn(fullType, allowedTags)
    local tag = IrisMoveablesIndex._tagMapping[fullType]
    if not tag then
        return false
    end
    
    for _, allowed in ipairs(allowedTags) do
        if tag == allowed then
            return true
        end
    end
    return false
end

return IrisMoveablesIndex
