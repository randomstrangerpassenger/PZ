local Harness = {}

local function isArray(value)
    if type(value) ~= "table" then return false end
    local count, maximum = 0, 0
    for key, _ in pairs(value) do
        if type(key) ~= "number" or key < 1 or key % 1 ~= 0 then return false end
        count = count + 1
        if key > maximum then maximum = key end
    end
    return count == maximum
end

local function escape(value)
    return tostring(value):gsub("\\", "\\\\"):gsub('"', '\\"'):gsub("\n", "\\n"):gsub("\r", "\\r"):gsub("\t", "\\t")
end

local function encode(value)
    local kind = type(value)
    if value == nil then return "null" end
    if kind == "boolean" or kind == "number" then return tostring(value) end
    if kind == "string" then return '"' .. escape(value) .. '"' end
    if kind ~= "table" then return '"' .. escape(value) .. '"' end
    local parts = {}
    if isArray(value) then
        for i = 1, #value do parts[#parts + 1] = encode(value[i]) end
        return "[" .. table.concat(parts, ",") .. "]"
    end
    local keys = {}
    for key, _ in pairs(value) do keys[#keys + 1] = tostring(key) end
    table.sort(keys)
    for _, key in ipairs(keys) do parts[#parts + 1] = encode(key) .. ":" .. encode(value[key]) end
    return "{" .. table.concat(parts, ",") .. "}"
end

function Harness.runAll()
    local Description = require("Iris/API/Description")
    local failures = 0
    local rows = 0
    local function emit(caseId, fixtureId, passed, expected, observed, sensitive)
        rows = rows + 1
        if not passed then failures = failures + 1 end
        print("IRIS_CORE_ROW\t" .. encode({case_id=caseId,axis="description_single_path",fixture_id=fixtureId,owner_change=3,status=passed and "pass" or "fail",expected=expected,observed=observed,dialect_sensitive=sensitive,dialect_reasons=sensitive and {"Kahlua_string_bytes","runtime_generator"} or {},stubbed_dependencies={}}))
    end
    for _, fullType in ipairs({"Base.Hammer","Base.Pan","Base.WhiskeyFull"}) do
        local blocks = Description.getDescriptionBlocks(fullType, nil)
        local text = Description.getDescription(fullType, nil)
        local joined = table.concat(blocks, "\n\n")
        emit("description_acceptance." .. fullType:lower():gsub("[^a-z0-9]+","_"), fullType,
            #blocks > 0 and text == joined,{relation="single blocks path joined with double newline",nonempty=true},{block_count=#blocks,joined_equal=text == joined,text=text},true)
    end
    local nilBlocks = Description.getDescriptionBlocks(nil, nil)
    emit("description_acceptance.nil_fallback","nil_input",
        #nilBlocks == 0 and Description.getDescription(nil,nil) == "" and Description.getDescriptionForItem(nil,nil) == "",
        {blocks=0,text="",item_text=""},{blocks=#nilBlocks,text=Description.getDescription(nil,nil),item_text=Description.getDescriptionForItem(nil,nil)},false)
    print("IRIS_CORE_SUMMARY\t" .. encode({row_count=rows,failure_count=failures}))
    local success = failures == 0
    pcall(function() getCore():quitToDesktop() end)
    return success
end

return Harness

