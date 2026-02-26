--[[
    IrisDesc TestHarness
    
    테스트 케이스 실행기
    
    ⚠️ 필수 케이스:
    1. Base.Hammer: 3블록, Tool.1-A → Tool.1-B → Combat.2-C
    2. Base.Pan: 2블록, Tool.1-D → Combat.2-C
    3. Base.WhiskeyFull: 4블록, Consumable.3-B → 3-C → 3-D → Resource.4-F
    4. 분류 없음: 빈 출력
]]

local Generator = require("Pulse/Iris/Logic/IrisDesc/Generator")
local Templates = require("Pulse/Iris/Logic/IrisDesc/Templates")

local IrisDescTest = {}

local passCount = 0
local failCount = 0


---테스트 결과 출력
---@param name string 테스트 이름
---@param passed boolean 통과 여부
---@param message string|nil 실패 메시지
local function report(name, passed, message)
    if passed then
        passCount = passCount + 1
        print("[PASS] " .. name)
    else
        failCount = failCount + 1
        print("[FAIL] " .. name .. ": " .. (message or ""))
    end
end


---블록 수 검증
---@param blocks table 블록 배열
---@param expected number 기대 블록 수
---@return boolean 통과 여부
local function assertBlockCount(blocks, expected)
    return #blocks == expected
end


---블록 순서 검증 (헤더에서 코드 추출)
---@param blocks table 블록 배열
---@param expected_order table 기대 소분류 ID 배열
---@return boolean 통과 여부
---@return string|nil 실패 메시지
local function assertBlockOrder(blocks, expected_order)
    if #blocks ~= #expected_order then
        return false, "block count mismatch: got " .. #blocks .. ", expected " .. #expected_order
    end
    
    for i, expected_id in ipairs(expected_order) do
        local template = Templates.getTemplate(expected_id)
        if not template then
            return false, "template not found for " .. expected_id
        end
        
        local expected_header = "[" .. template.header .. "]"
        local block = blocks[i]
        
        -- 블록 첫 줄이 헤더인지 확인
        local first_line = string.match(block, "^([^\n]+)")
        if first_line ~= expected_header then
            return false, "block " .. i .. " header mismatch: got '" .. (first_line or "nil") .. "', expected '" .. expected_header .. "'"
        end
    end
    
    return true
end


---템플릿 원문 무결성 검증
---@param blocks table 블록 배열
---@param expected_order table 기대 소분류 ID 배열
---@return boolean 통과 여부
---@return string|nil 실패 메시지
local function assertTemplateIntegrity(blocks, expected_order)
    for i, expected_id in ipairs(expected_order) do
        local template = Templates.getTemplate(expected_id)
        if not template then
            return false, "template not found for " .. expected_id
        end
        
        local block = blocks[i]
        
        -- 라인별 검증
        local block_lines = {}
        for line in string.gmatch(block, "[^\n]+") do
            table.insert(block_lines, line)
        end
        
        -- 첫 줄은 헤더, 나머지는 본문
        local expected_lines_count = #template.lines + 1  -- header + lines
        if #block_lines ~= expected_lines_count then
            return false, "block " .. i .. " line count mismatch: got " .. #block_lines .. ", expected " .. expected_lines_count
        end
        
        -- 본문 라인 검증 (완전 일치)
        for j, expected_line in ipairs(template.lines) do
            local actual_line = block_lines[j + 1]  -- +1 for header
            if actual_line ~= expected_line then
                return false, "block " .. i .. " line " .. j .. " mismatch"
            end
        end
    end
    
    return true
end


---테스트: Base.Hammer
function IrisDescTest.testHammer()
    local tags = { "Tool.1-A", "Tool.1-B", "Combat.2-C" }
    local expected_order = { "Tool.1-A", "Tool.1-B", "Combat.2-C" }
    
    local blocks = Generator.generate("Base.Hammer", tags, nil)
    
    -- 블록 수 검증
    if not assertBlockCount(blocks, 3) then
        report("Hammer.blockCount", false, "expected 3, got " .. #blocks)
        return
    end
    report("Hammer.blockCount", true)
    
    -- 블록 순서 검증
    local orderOk, orderMsg = assertBlockOrder(blocks, expected_order)
    report("Hammer.blockOrder", orderOk, orderMsg)
    
    -- 템플릿 무결성 검증
    local integrityOk, integrityMsg = assertTemplateIntegrity(blocks, expected_order)
    report("Hammer.templateIntegrity", integrityOk, integrityMsg)
end


---테스트: Base.Pan
function IrisDescTest.testPan()
    local tags = { "Tool.1-D", "Combat.2-C" }
    local expected_order = { "Tool.1-D", "Combat.2-C" }
    
    local blocks = Generator.generate("Base.Pan", tags, nil)
    
    if not assertBlockCount(blocks, 2) then
        report("Pan.blockCount", false, "expected 2, got " .. #blocks)
        return
    end
    report("Pan.blockCount", true)
    
    local orderOk, orderMsg = assertBlockOrder(blocks, expected_order)
    report("Pan.blockOrder", orderOk, orderMsg)
    
    local integrityOk, integrityMsg = assertTemplateIntegrity(blocks, expected_order)
    report("Pan.templateIntegrity", integrityOk, integrityMsg)
end


---테스트: Base.WhiskeyFull
function IrisDescTest.testWhiskeyFull()
    local tags = { "Consumable.3-B", "Consumable.3-C", "Consumable.3-D", "Resource.4-F" }
    local expected_order = { "Consumable.3-B", "Consumable.3-C", "Consumable.3-D", "Resource.4-F" }
    
    local blocks = Generator.generate("Base.WhiskeyFull", tags, nil)
    
    if not assertBlockCount(blocks, 4) then
        report("WhiskeyFull.blockCount", false, "expected 4, got " .. #blocks)
        return
    end
    report("WhiskeyFull.blockCount", true)
    
    local orderOk, orderMsg = assertBlockOrder(blocks, expected_order)
    report("WhiskeyFull.blockOrder", orderOk, orderMsg)
    
    local integrityOk, integrityMsg = assertTemplateIntegrity(blocks, expected_order)
    report("WhiskeyFull.templateIntegrity", integrityOk, integrityMsg)
end


---테스트: 분류 없음
function IrisDescTest.testEmpty()
    local tags = {}
    
    local blocks = Generator.generate("Base.Unknown", tags, nil)
    
    if not assertBlockCount(blocks, 0) then
        report("Empty.blockCount", false, "expected 0, got " .. #blocks)
        return
    end
    report("Empty.blockCount", true)
end


---테스트: 잘못된 태그 형식 (무시되어야 함)
function IrisDescTest.testInvalidTags()
    local tags = { "Tool.1-A", "invalid", "3-C", "Combat.2-C" }
    -- "invalid"와 "3-C"는 무시됨
    local expected_order = { "Tool.1-A", "Combat.2-C" }
    
    local blocks = Generator.generate("Base.Test", tags, nil)
    
    if not assertBlockCount(blocks, 2) then
        report("InvalidTags.blockCount", false, "expected 2 (invalid tags ignored), got " .. #blocks)
        return
    end
    report("InvalidTags.blockCount", true)
    
    local orderOk, orderMsg = assertBlockOrder(blocks, expected_order)
    report("InvalidTags.blockOrder", orderOk, orderMsg)
end


---테스트: meta primary 지정
function IrisDescTest.testMetaPrimary()
    local tags = { "Combat.2-C", "Tool.1-A", "Tool.1-B" }
    -- meta로 Tool.1-B를 primary로 지정
    local expected_order = { "Tool.1-B", "Tool.1-A", "Combat.2-C" }
    
    local blocks = Generator.generate("Base.Test", tags, "Tool.1-B")
    
    if not assertBlockCount(blocks, 3) then
        report("MetaPrimary.blockCount", false, "expected 3, got " .. #blocks)
        return
    end
    report("MetaPrimary.blockCount", true)
    
    local orderOk, orderMsg = assertBlockOrder(blocks, expected_order)
    report("MetaPrimary.blockOrder", orderOk, orderMsg)
end


---전체 테스트 실행
function IrisDescTest.runAll()
    print("========================================")
    print("[IrisDesc] Running all tests...")
    print("========================================")
    
    passCount = 0
    failCount = 0
    
    IrisDescTest.testHammer()
    IrisDescTest.testPan()
    IrisDescTest.testWhiskeyFull()
    IrisDescTest.testEmpty()
    IrisDescTest.testInvalidTags()
    IrisDescTest.testMetaPrimary()
    
    print("========================================")
    print("[IrisDesc] Test Results: " .. passCount .. " passed, " .. failCount .. " failed")
    print("========================================")
    
    return failCount == 0
end


return IrisDescTest
