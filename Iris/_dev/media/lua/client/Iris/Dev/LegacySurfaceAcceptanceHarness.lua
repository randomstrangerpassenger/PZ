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

local function copy(values)
    local result = {}
    for _, value in ipairs(values or {}) do result[#result + 1] = value end
    return result
end

function Harness.runAll()
    local IrisAPI = require("Iris/IrisAPI")
    local BrowserData = require("Iris/UI/Browser/IrisBrowserData")
    local TooltipSummary = require("Iris/UI/Tooltip/IrisTooltipSummary")
    local StaticData = require("Iris/API/StaticData")
    local failures, rows = 0, 0
    local function emit(caseId, fixtureId, passed, expected, observed, sensitive, stubs)
        rows = rows + 1
        if not passed then failures = failures + 1 end
        print("IRIS_CORE_ROW\t" .. encode({
            case_id=caseId,axis="legacy_surface",fixture_id=fixtureId,owner_change=6,
            status=passed and "pass" or "fail",expected=expected,observed=observed,
            dialect_sensitive=sensitive == true,dialect_reasons=sensitive and {"legacy_global_boundary"} or {},
            stubbed_dependencies=stubs or {},
        }))
    end

    local capabilities = IrisAPI.getCapabilities("Base.Hammer")
    local tags = IrisAPI.getTags("Base.Hammer")
    local summary = TooltipSummary.get("Base.Hammer")
    local hasCapability = IrisAPI.hasCapability("Base.Hammer", "can_scrap_moveables")
    emit("legacy_acceptance.capability_tooltip", "Base.Hammer",
        #capabilities > 0 and #tags > 0 and summary and #summary.tags > 0 and hasCapability,
        {capability_nonempty=true,tags_nonempty=true,tooltip_tags_nonempty=true,has_scrap_capability=true},
        {capabilities=copy(capabilities),tags=copy(tags),tooltip_tags=summary and copy(summary.tags) or {},
            has_scrap_capability=hasCapability},false)

    local category, subcategory = BrowserData.getItemLocation("Base.Hammer")
    local categoryLabel = BrowserData.getCategoryLabel(category)
    local subcategoryLabel = BrowserData.getSubcategoryLabel(subcategory)
    emit("legacy_acceptance.taxonomy_projection", "Base.Hammer",
        category == "Tool" and subcategory == "1-B" and #tags >= 2 and categoryLabel and categoryLabel ~= "" and subcategoryLabel and subcategoryLabel ~= "",
        {category="Tool",subcategory="1-B",multi_classification=true,labels_nonempty=true},
        {category=category or "nil",subcategory=subcategory or "nil",tag_count=#tags,
            category_label=categoryLabel or "nil",subcategory_label=subcategoryLabel or "nil"},false)

    local missingBefore = BrowserData.getGroupVariants("__iris_missing_group__")
    local legacyData = StaticData.getLegacyIrisData()
    local originalGroups = legacyData and legacyData.ItemGroups or nil
    if legacyData then
        legacyData.ItemGroups = {
            iris_acceptance_group = {"Base.Hammer", "Base.Apple"},
        }
    end
    local variants = BrowserData.getGroupVariants("iris_acceptance_group")
    if legacyData then legacyData.ItemGroups = originalGroups end
    local members = {}
    for _, variant in ipairs(variants or {}) do members[variant.fullType] = true end
    local sortedByDisplay = variants and #variants == 2 and variants[1].displayName <= variants[2].displayName
    emit("legacy_acceptance.variant_adapter", "legacy_global_only_group",
        missingBefore == nil and variants and #variants == 2 and members["Base.Apple"] and members["Base.Hammer"] and sortedByDisplay,
        {missing_group=nil,signature="table|nil",members={"Base.Apple","Base.Hammer"},ordering="displayName then fullType"},
        {missing_group=missingBefore,variant_count=variants and #variants or 0,
            first=variants and variants[1] and variants[1].fullType or "nil",
            second=variants and variants[2] and variants[2].fullType or "nil",sorted_by_display=sortedByDisplay},
        true,{"temporary legacy IrisData.ItemGroups fixture"})

    print("IRIS_CORE_SUMMARY\t" .. encode({row_count=rows,failure_count=failures}))
    local success = failures == 0
    pcall(function() getCore():quitToDesktop() end)
    return success
end

return Harness
