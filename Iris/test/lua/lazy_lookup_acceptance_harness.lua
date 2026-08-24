local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
local mode = assert(arg and arg[2], "lookup mode argument is required")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local nativeRequire = require
local requireCounts = {}
require = function(moduleName)
    requireCounts[moduleName] = (requireCounts[moduleName] or 0) + 1
    return nativeRequire(moduleName)
end

local RuntimeDiagnostics = require("Iris/Data/IrisRuntimeLookupDiagnostics")
assert(RuntimeDiagnostics.getDiagnostics().metricsEnabled == false)
RuntimeDiagnostics.recordMetric("probe", "disabled", 1)
assert(RuntimeDiagnostics.getDiagnostics().metrics.probe == nil)
RuntimeDiagnostics.setMetricsEnabled(true)
assert(RuntimeDiagnostics.getDiagnostics().metricsEnabled == true)

local function onlyRangeIndex(schemaVersion, moduleName, fullType)
    local rangeKey = fullType or "Base.223Box"
    return {
        schema_version = schemaVersion,
        entry_count = 1,
        chunks = {{
            count = 1,
            first = rangeKey,
            last = rangeKey,
            module = moduleName,
            sha256 = string.rep("0", 64),
        }},
    }
end

local function onlyLineCountIndex(schemaVersion, fullType, lineCount)
    local rangeKey = fullType or "Base.223Box"
    return {
        schema_version = schemaVersion,
        entry_count = 1,
        lineCounts = { [rangeKey] = lineCount or 1 },
    }
end

local function deepEqual(left, right, seen)
    if type(left) ~= type(right) then return false end
    if type(left) ~= "table" then return left == right end
    seen = seen or {}
    if seen[left] == right then return true end
    seen[left] = right
    for key, value in pairs(left) do
        if not deepEqual(value, right[key], seen) then return false end
    end
    for key, _ in pairs(right) do
        if left[key] == nil then return false end
    end
    return true
end

if mode == "layer3" then
    local current = require("Iris/Data/IrisLayer3DataCurrent")
    local expectedChunk1 = current.chunk_modules[1]
    local expectedChunk2 = current.chunk_modules[2]
    local missingChunk = "Iris/Data/IrisLayer3Generations/dvf33-" ..
        string.rep("0", 64) .. "/Chunks/Chunk999"
    local realLayer3Index = require("Iris/Data/IrisLayer3DataChunkIndex")
    local lookup = require("Iris/Data/IrisLayer3DataLookup")
    local first = assert(lookup.get("Base.223Box"))
    local afterFirst = lookup.getDiagnostics()
    assert(afterFirst.loadedChunkCount == 1 and afterFirst.requireCallCount == 1)
    assert(#afterFirst.loadedChunkModules == 1)
    assert(afterFirst.loadedChunkModules[1] == expectedChunk1)
    assert(requireCounts[expectedChunk1] == 1)
    assert(requireCounts[expectedChunk2] == nil)
    local sameChunkLast = assert(lookup.get("Base.BookElectrician5"))
    local afterSameChunk = lookup.getDiagnostics()
    assert(afterSameChunk.loadedChunkCount == 1 and afterSameChunk.requireCallCount == 1)
    assert(#afterSameChunk.loadedChunkModules == 1)
    local adjacentFirst = assert(lookup.get("Base.BookFarming1"))
    assert(first ~= nil and sameChunkLast ~= nil and adjacentFirst ~= nil)
    local beforeRepeat = lookup.getDiagnostics()
    assert(beforeRepeat.loadedChunkCount == 2 and beforeRepeat.requireCallCount == 2)
    assert(#beforeRepeat.loadedChunkModules == 2)
    assert(beforeRepeat.loadedChunkModules[1] == expectedChunk1)
    assert(beforeRepeat.loadedChunkModules[2] == expectedChunk2)
    assert(requireCounts[expectedChunk1] == 1)
    assert(requireCounts[expectedChunk2] == 1)
    for moduleName, count in pairs(requireCounts) do
        if moduleName:match("^Iris/Data/IrisLayer3Generations/.+/Chunks/Chunk%d%d%d$") then
            assert(
                (moduleName == expectedChunk1 or moduleName == expectedChunk2) and count == 1,
                "unexpected initial Layer3 chunk module: " .. moduleName
            )
        end
    end
    assert(lookup.get("Base.223Box") == first)
    local afterRepeat = lookup.getDiagnostics()
    assert(afterRepeat.loadedChunkCount == 2 and afterRepeat.requireCallCount == 2)
    assert(afterRepeat.fallbackCount == 0)

    local facade = require("Iris/Data/IrisLayer3DataChunks")
    local parityCount = 0
    for fullType, entry in pairs(facade) do
        local focused, reason = lookup.get(fullType)
        assert(reason == nil and focused == entry, "Layer3 parity mismatch: " .. tostring(fullType))
        parityCount = parityCount + 1
    end
    assert(parityCount == 2105 and IrisLayer3Data == facade)

    package.loaded["Iris/Data/layer3_renderer"] = nil
    package.loaded["Iris/Data/IrisLayer3EnglishLookup"] = nil
    package.preload["Iris/Data/IrisLayer3EnglishLookup"] = function()
        return { get=function(fullType)
            if fullType == "Base.BarbedWire" then return "stale English text" end
            return nil
        end }
    end
    local silentRenderer = require("Iris/Data/layer3_renderer")
    assert(facade["Base.BarbedWire"] and facade["Base.BarbedWire"].text_ko == nil)
    assert(silentRenderer.getRawText("Base.BarbedWire", { locale = "EN" }) == nil)
    assert(silentRenderer.getText("Base.BarbedWire", { locale = "EN" }) == nil)
    package.loaded["Iris/Data/layer3_renderer"] = nil
    package.loaded["Iris/Data/IrisLayer3EnglishLookup"] = nil
    package.preload["Iris/Data/IrisLayer3EnglishLookup"] = nil

    RuntimeDiagnostics.reset()
    package.loaded["Iris/Data/IrisLayer3DataLookup"] = nil
    package.loaded["Iris/Data/IrisLayer3DataChunkIndex"] = nil
    package.loaded["Iris/Data/layer3_renderer"] = nil
    package.loaded["Iris/Data/IrisLayer3DataChunks"] = nil
    package.preload["Iris/Data/IrisLayer3DataChunkIndex"] = function() return realLayer3Index end
    local normalMissFacadeLoads = 0
    package.preload["Iris/Data/IrisLayer3DataChunks"] = function()
        normalMissFacadeLoads = normalMissFacadeLoads + 1
        return facade
    end
    local missRenderer = require("Iris/Data/layer3_renderer")
    assert(missRenderer.getText("Missing.DoesNotExist") == nil)
    local normalMissDiagnostics = RuntimeDiagnostics.getDiagnostics()
    assert(normalMissFacadeLoads == 0 and normalMissDiagnostics.fallbackCount == 0)
    assert(normalMissDiagnostics.metrics.layer3.lookup_miss == 1)
    local normalMissFacadeLoadsAtObservation = normalMissFacadeLoads

    local function assertConsumerFallback(indexValue, expectedReason)
        RuntimeDiagnostics.reset()
        package.loaded["Iris/Data/IrisLayer3DataLookup"] = nil
        package.loaded["Iris/Data/IrisLayer3DataChunkIndex"] = nil
        package.loaded["Iris/Data/layer3_renderer"] = nil
        package.preload["Iris/Data/IrisLayer3DataLookup"] = nil
        package.preload["Iris/Data/IrisLayer3DataChunkIndex"] = function() return indexValue end
        local renderer = require("Iris/Data/layer3_renderer")
        local expected = facade["Base.223Box"]
        assert(renderer.getPublishState("Base.223Box") == expected.publish_state)
        assert(renderer.getRawText("Base.223Box") == expected.text_ko)
        assert(renderer.getText("Base.223Box", { include_internal_only = true }) == expected.text_ko)
        local shared = RuntimeDiagnostics.getDiagnostics()
        assert(shared.fallbackCount == 3)
        assert(shared.surfaces.layer3.fallbackReasons[expectedReason] == 3)
    end

    assertConsumerFallback(
        { schema_version = "invalid", chunks = {}, entry_count = 0 },
        "index_shape_invalid"
    )
    assertConsumerFallback(
        onlyRangeIndex("iris_layer3_chunk_range_index_v1", "invalid/module"),
        "module_name_invalid"
    )
    assertConsumerFallback(
        onlyRangeIndex(
            "iris_layer3_chunk_range_index_v1",
            missingChunk,
            nil
        ),
        "target_module_load_failure"
    )
    assertConsumerFallback(
        onlyRangeIndex(
            "iris_layer3_chunk_range_index_v1",
            expectedChunk1
        ),
        "index_content_mismatch"
    )

    RuntimeDiagnostics.reset()
    local missingEntry, missingReason = lookup.get("Missing.DoesNotExist")
    assert(missingEntry == nil and missingReason == "lookup_miss")
    local missingDiagnostics = RuntimeDiagnostics.getDiagnostics()
    assert(missingDiagnostics.fallbackCount == 0)
    assert(missingDiagnostics.metrics.layer3.lookup_miss == 1)

    package.loaded["Iris/Data/IrisLayer3DataLookup"] = nil
    package.loaded["Iris/Data/IrisLayer3DataChunkIndex"] = nil
    package.preload["Iris/Data/IrisLayer3DataChunkIndex"] = function()
        return { schema_version = "invalid", chunks = {}, entry_count = 0 }
    end
    local invalidLookup = require("Iris/Data/IrisLayer3DataLookup")
    local invalidEntry, invalidReason = invalidLookup.get("Base.223Box")
    assert(invalidEntry == nil and invalidReason == "index_shape_invalid")

    package.loaded["Iris/Data/IrisLayer3DataLookup"] = nil
    package.loaded["Iris/Data/IrisLayer3DataChunkIndex"] = nil
    package.preload["Iris/Data/IrisLayer3DataChunkIndex"] = function()
        return onlyRangeIndex("iris_layer3_chunk_range_index_v1", "invalid/module")
    end
    local invalidModuleLookup = require("Iris/Data/IrisLayer3DataLookup")
    local invalidModuleEntry, invalidModuleReason = invalidModuleLookup.get("Base.223Box")
    assert(invalidModuleEntry == nil and invalidModuleReason == "module_name_invalid")

    package.loaded["Iris/Data/IrisLayer3DataLookup"] = nil
    package.loaded["Iris/Data/IrisLayer3DataChunkIndex"] = nil
    package.preload["Iris/Data/IrisLayer3DataChunkIndex"] = function()
        return onlyRangeIndex(
            "iris_layer3_chunk_range_index_v1",
            missingChunk,
            nil
        )
    end
    package.preload[missingChunk] = function()
        error("standalone target chunk failure")
    end
    local failedModuleLookup = require("Iris/Data/IrisLayer3DataLookup")
    local failedModuleEntry, failedModuleReason = failedModuleLookup.get("Base.223Box")
    assert(failedModuleEntry == nil and failedModuleReason == "target_module_load_failure")

    RuntimeDiagnostics.reset()
    package.loaded["Iris/Data/IrisLayer3DataLookup"] = nil
    package.loaded["Iris/Data/layer3_renderer"] = nil
    package.preload["Iris/Data/IrisLayer3DataLookup"] = function()
        error("standalone router unavailable")
    end
    local renderer = require("Iris/Data/layer3_renderer")
    assert(renderer.getPublishState("Base.223Box") == facade["Base.223Box"].publish_state)
    local unavailableDiagnostics = RuntimeDiagnostics.getDiagnostics()
    assert(unavailableDiagnostics.surfaces.layer3.fallbackReasons.router_unavailable == 1)
    print("IRIS_LAYER3_LAZY_LOOKUP_PASS parity_count=" .. tostring(parityCount) ..
        " first_lookup_loaded_chunks=" .. tostring(afterFirst.loadedChunkCount) ..
        " first_lookup_loaded_modules=" .. table.concat(afterFirst.loadedChunkModules, ",") ..
        " initial_loaded_chunks=" .. tostring(beforeRepeat.loadedChunkCount) ..
        " initial_loaded_modules=" .. table.concat(beforeRepeat.loadedChunkModules, ",") ..
        " router_unavailable_count=" ..
        tostring(unavailableDiagnostics.surfaces.layer3.fallbackReasons.router_unavailable) ..
        " normal_miss_facade_loads=" .. tostring(normalMissFacadeLoadsAtObservation))
elseif mode == "usecase" then
    local realUseCaseChunkIndex = require("Iris/Data/UseCaseDescriptions/ChunkIndex")
    local realUseCaseLineCountIndex = require("Iris/Data/UseCaseDescriptions/LineCountIndex")
    local lookup = require("Iris/Data/IrisUseCaseDescriptionsLookup")
    local lineCount, lineReason = lookup.getLineCount("Base.223Box")
    assert(lineReason == nil and lineCount == 1)
    local afterLineCount = lookup.getDiagnostics()
    assert(afterLineCount.indexValid == true)
    assert(afterLineCount.chunkIndexValid == true and afterLineCount.lineCountIndexValid == true)
    assert(afterLineCount.loadedDescriptionChunkCount == 0)

    local missingLineCount, missingLineReason = lookup.getLineCount("Missing.DoesNotExist")
    assert(missingLineReason == nil and missingLineCount == 0)
    local coldMissingSummary = require("Iris/UI/Tooltip/IrisTooltipSummary")
    assert(coldMissingSummary.get("Missing.DoesNotExist").useCaseCount == 0)
    local afterMissingSummary = lookup.getDiagnostics()
    assert(afterMissingSummary.loadedDescriptionChunkCount == 0)
    assert(afterMissingSummary.descriptionRequireCallCount == 0)
    assert(requireCounts["Iris/Data/IrisUseCaseDescriptions"] == nil)
    for moduleName, count in pairs(requireCounts) do
        if moduleName:match("^Iris/Data/UseCaseDescriptions/Chunk%d%d%d$") then
            assert(count == 0, "missing UseCase tooltip loaded a description chunk")
        end
    end

    local first = assert(lookup.get("Base.223Box"))
    local afterFirst = lookup.getDiagnostics()
    assert(afterFirst.loadedDescriptionChunkCount == 1 and afterFirst.descriptionRequireCallCount == 1)
    assert(#afterFirst.loadedDescriptionChunkModules == 1)
    assert(afterFirst.loadedDescriptionChunkModules[1] == "Iris/Data/UseCaseDescriptions/Chunk001")
    assert(requireCounts["Iris/Data/UseCaseDescriptions/Chunk001"] == 1)
    assert(requireCounts["Iris/Data/UseCaseDescriptions/Chunk002"] == nil)
    local sameChunkLast = assert(lookup.get("Base.BookMetalWelding4"))
    local afterSameChunk = lookup.getDiagnostics()
    assert(afterSameChunk.loadedDescriptionChunkCount == 1)
    assert(afterSameChunk.descriptionRequireCallCount == 1)
    assert(#afterSameChunk.loadedDescriptionChunkModules == 1)
    local adjacentFirst = assert(lookup.get("Base.BookMetalWelding5"))
    assert(first ~= nil and sameChunkLast ~= nil and adjacentFirst ~= nil)
    local beforeRepeat = lookup.getDiagnostics()
    assert(beforeRepeat.loadedDescriptionChunkCount == 2 and beforeRepeat.descriptionRequireCallCount == 2)
    assert(#beforeRepeat.loadedDescriptionChunkModules == 2)
    assert(beforeRepeat.loadedDescriptionChunkModules[1] == "Iris/Data/UseCaseDescriptions/Chunk001")
    assert(beforeRepeat.loadedDescriptionChunkModules[2] == "Iris/Data/UseCaseDescriptions/Chunk002")
    assert(requireCounts["Iris/Data/UseCaseDescriptions/Chunk001"] == 1)
    assert(requireCounts["Iris/Data/UseCaseDescriptions/Chunk002"] == 1)
    for moduleName, count in pairs(requireCounts) do
        if moduleName:match("^Iris/Data/UseCaseDescriptions/Chunk%d%d%d$") then
            assert(
                (moduleName == "Iris/Data/UseCaseDescriptions/Chunk001" or
                    moduleName == "Iris/Data/UseCaseDescriptions/Chunk002") and count == 1,
                "unexpected initial UseCase chunk module: " .. moduleName
            )
        end
    end
    assert(lookup.get("Base.223Box") == first)
    local afterRepeat = lookup.getDiagnostics()
    assert(afterRepeat.loadedDescriptionChunkCount == 2 and afterRepeat.descriptionRequireCallCount == 2)

    RuntimeDiagnostics.reset()
    local missingEntry, missingReason = lookup.get("Missing.DoesNotExist")
    assert(missingEntry == nil and missingReason == "lookup_miss")
    local missingDiagnostics = RuntimeDiagnostics.getDiagnostics()
    assert(missingDiagnostics.fallbackCount == 0)
    assert(missingDiagnostics.metrics.usecase.lookup_miss == 1)

    local facade = require("Iris/Data/IrisUseCaseDescriptions")
    local parityCount = 0
    for fullType, entry in pairs(facade) do
        if fullType ~= "_requirementsLookup" then
            local focused, reason = lookup.get(fullType)
            assert(reason == nil and focused == entry, "UseCase parity mismatch: " .. tostring(fullType))
            local focusedLineCount, countReason = lookup.getLineCount(fullType)
            assert(countReason == nil and focusedLineCount == #(entry.lines or {}),
                "UseCase line-count parity mismatch: " .. tostring(fullType))
            parityCount = parityCount + 1
        end
    end
    assert(parityCount == 1631)

    local function assertConsumerFallback(indexValue, lineCountValue, expectedReason)
        RuntimeDiagnostics.reset()
        package.loaded["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
        package.loaded["Iris/Data/UseCaseDescriptions/ChunkIndex"] = nil
        package.loaded["Iris/Data/UseCaseDescriptions/LineCountIndex"] = nil
        package.loaded["Iris/API/UseCases"] = nil
        package.preload["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
        package.preload["Iris/Data/UseCaseDescriptions/ChunkIndex"] = function() return indexValue end
        package.preload["Iris/Data/UseCaseDescriptions/LineCountIndex"] = function() return lineCountValue end
        local fallbackUseCases = require("Iris/API/UseCases")
        local state = fallbackUseCases._getDescriptionState("Base.223Box")
        assert(state.status == "available" and state.fallback_used == true)
        assert(state.reason == expectedReason)
        assert(deepEqual(state.lines, facade["Base.223Box"].lines))
        assert(deepEqual(state.debug_lines, facade["Base.223Box"].debug_lines))
        local shared = RuntimeDiagnostics.getDiagnostics()
        assert(shared.fallbackCount == 1)
        assert(shared.surfaces.usecase.fallbackReasons[expectedReason] == 1)
        local splitDiagnostics = require("Iris/Data/IrisUseCaseDescriptionsLookup").getDiagnostics()
        assert(type(splitDiagnostics.chunkIndexValid) == "boolean")
        assert(type(splitDiagnostics.lineCountIndexValid) == "boolean")
        assert(splitDiagnostics.indexValid ==
            (splitDiagnostics.chunkIndexValid and splitDiagnostics.lineCountIndexValid and
                splitDiagnostics.crossCheckState == "valid"))
    end

    local function assertLineCountFallback(indexValue, expectedReason)
        RuntimeDiagnostics.reset()
        package.loaded["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
        package.loaded["Iris/Data/UseCaseDescriptions/LineCountIndex"] = nil
        package.loaded["Iris/UI/Tooltip/IrisTooltipSummary"] = nil
        package.preload["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
        package.preload["Iris/Data/UseCaseDescriptions/LineCountIndex"] = function()
            return indexValue
        end
        local fallbackSummary = require("Iris/UI/Tooltip/IrisTooltipSummary")
        assert(fallbackSummary.get("Base.223Box").useCaseCount == #facade["Base.223Box"].lines)
        local shared = RuntimeDiagnostics.getDiagnostics()
        assert(shared.fallbackCount == 2)
        assert(shared.surfaces.usecase.fallbackReasons[expectedReason] == 1)
        assert(shared.surfaces.usecase_tooltip_line_count.fallbackReasons[expectedReason] == 1)
        local splitDiagnostics = require("Iris/Data/IrisUseCaseDescriptionsLookup").getDiagnostics()
        assert(type(splitDiagnostics.chunkIndexValid) == "boolean")
        assert(type(splitDiagnostics.lineCountIndexValid) == "boolean")
        assert(splitDiagnostics.indexValid ==
            (splitDiagnostics.chunkIndexValid and splitDiagnostics.lineCountIndexValid and
                splitDiagnostics.crossCheckState == "valid"))
    end

    local malformedLineCounts = onlyLineCountIndex(
        "iris_usecase_line_count_index_v1", "Base.223Box", 1
    )
    malformedLineCounts.lineCounts["Base.223Box"] = "invalid"
    assertLineCountFallback(malformedLineCounts, "index_shape_invalid")
    assertConsumerFallback(
        onlyRangeIndex("iris_usecase_chunk_range_index_v1", "invalid/module"),
        onlyLineCountIndex("iris_usecase_line_count_index_v1"),
        "module_name_invalid"
    )
    assertConsumerFallback(
        onlyRangeIndex(
            "iris_usecase_chunk_range_index_v1",
            "Iris/Data/UseCaseDescriptions/Chunk999"
        ),
        onlyLineCountIndex("iris_usecase_line_count_index_v1"),
        "target_module_load_failure"
    )
    assertConsumerFallback(
        onlyRangeIndex(
            "iris_usecase_chunk_range_index_v1",
            "Iris/Data/UseCaseDescriptions/Chunk001"
        ),
        onlyLineCountIndex("iris_usecase_line_count_index_v1"),
        "index_content_mismatch"
    )

    RuntimeDiagnostics.reset()
    package.loaded["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/ChunkIndex"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/LineCountIndex"] = nil
    package.loaded["Iris/API/UseCases"] = nil
    package.loaded["Iris/API/StaticData"] = nil
    package.preload["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
    package.preload["Iris/Data/UseCaseDescriptions/ChunkIndex"] = function() return realUseCaseChunkIndex end
    package.preload["Iris/Data/UseCaseDescriptions/LineCountIndex"] = function() return realUseCaseLineCountIndex end
    local normalMissFacadeLoads = 0
    package.preload["Iris/API/StaticData"] = function()
        return {get=function(dataset)
            if dataset == "useCaseDescriptions" then normalMissFacadeLoads = normalMissFacadeLoads + 1 end
            return nil
        end}
    end
    local missUseCases = require("Iris/API/UseCases")
    local missState = missUseCases._getDescriptionState("Missing.DoesNotExist")
    assert(missState.status == "verified_empty" and missState.reason == "lookup_miss")
    assert(missState.fallback_used == false)
    assert(#missUseCases.getUseCaseLines("Missing.DoesNotExist").lines == 0)
    assert(missUseCases._getDescriptionEntry("Missing.DoesNotExist") == nil)
    assert(missUseCases._getUseCaseLineCount("Missing.DoesNotExist") == 0)
    assert(normalMissFacadeLoads == 0)
    local normalMissDiagnostics = RuntimeDiagnostics.getDiagnostics()
    assert(normalMissDiagnostics.fallbackCount == 0)
    local normalMissFacadeLoadsAtObservation = normalMissFacadeLoads
    package.preload["Iris/API/StaticData"] = nil
    package.loaded["Iris/API/StaticData"] = nil

    RuntimeDiagnostics.reset()
    package.loaded["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/ChunkIndex"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/LineCountIndex"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/RequirementsLookup"] = nil
    package.loaded["Iris/API/StaticData"] = nil
    package.loaded["Iris/API/UseCases"] = nil
    package.preload["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
    package.preload["Iris/Data/UseCaseDescriptions/ChunkIndex"] = nil
    package.preload["Iris/Data/UseCaseDescriptions/LineCountIndex"] = nil
    package.preload["Iris/Data/UseCaseDescriptions/RequirementsLookup"] = nil
    local coldLookup = require("Iris/Data/IrisUseCaseDescriptionsLookup")
    local coldRequirements, coldRequirementsReason =
        coldLookup.getRequirements("Add Timer")
    assert(coldRequirementsReason == nil)
    assert(deepEqual(coldRequirements, facade._requirementsLookup["Add Timer"]))
    local coldRequirementsDiagnostics = coldLookup.getDiagnostics()
    assert(coldRequirementsDiagnostics.loadedDescriptionChunkCount == 0)
    assert(coldRequirementsDiagnostics.descriptionRequireCallCount == 0)
    assert(coldRequirementsDiagnostics.requirementsRequireCallCount == 1)

    local useCases = require("Iris/API/UseCases")
    local availableState = useCases._getDescriptionState("Base.223Box")
    assert(availableState.status == "available" and availableState.fallback_used == false)
    local copied = useCases.getUseCaseLines("Base.223Box")
    assert(deepEqual(copied.lines, facade["Base.223Box"].lines))
    assert(coldLookup.getDiagnostics().loadedDescriptionChunkCount == 1)
    assert(RuntimeDiagnostics.getDiagnostics().fallbackCount == 0)
    local originalCount = #copied.lines
    table.insert(copied.lines, { display_text = "mutation" })
    assert(#useCases.getUseCaseLines("Base.223Box").lines == originalCount)
    local copiedRequirements = useCases._getRequirements("Open Box of .223 Ammo")
    local originalRequirementCount = #copiedRequirements
    table.insert(copiedRequirements, { display_text = "mutation" })
    assert(#useCases._getRequirements("Open Box of .223 Ammo") == originalRequirementCount)

    package.loaded["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/ChunkIndex"] = nil
    package.preload["Iris/Data/UseCaseDescriptions/ChunkIndex"] = function()
        return { schema_version = "invalid", chunks = {}, entry_count = 0 }
    end
    local invalidLookup = require("Iris/Data/IrisUseCaseDescriptionsLookup")
    local invalidEntry, invalidReason = invalidLookup.get("Base.223Box")
    assert(invalidEntry == nil and invalidReason == "index_shape_invalid")

    package.loaded["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/ChunkIndex"] = nil
    package.preload["Iris/Data/UseCaseDescriptions/ChunkIndex"] = function()
        return onlyRangeIndex("iris_usecase_chunk_range_index_v1", "invalid/module")
    end
    local invalidModuleLookup = require("Iris/Data/IrisUseCaseDescriptionsLookup")
    local invalidModuleEntry, invalidModuleReason = invalidModuleLookup.get("Base.223Box")
    assert(invalidModuleEntry == nil and invalidModuleReason == "module_name_invalid")

    package.loaded["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/ChunkIndex"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/LineCountIndex"] = nil
    package.preload["Iris/Data/UseCaseDescriptions/ChunkIndex"] = function()
        return onlyRangeIndex(
            "iris_usecase_chunk_range_index_v1",
            "Iris/Data/UseCaseDescriptions/Chunk999"
        )
    end
    package.preload["Iris/Data/UseCaseDescriptions/LineCountIndex"] = function()
        return onlyLineCountIndex("iris_usecase_line_count_index_v1")
    end
    package.preload["Iris/Data/UseCaseDescriptions/Chunk999"] = function()
        error("standalone target chunk failure")
    end
    local failedModuleLookup = require("Iris/Data/IrisUseCaseDescriptionsLookup")
    local failedModuleEntry, failedModuleReason = failedModuleLookup.get("Base.223Box")
    assert(failedModuleEntry == nil and failedModuleReason == "target_module_load_failure")

    package.loaded["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/ChunkIndex"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/LineCountIndex"] = nil
    package.loaded["Iris/Data/UseCaseDescriptions/RequirementsLookup"] = nil
    package.preload["Iris/Data/UseCaseDescriptions/ChunkIndex"] = nil
    package.preload["Iris/Data/UseCaseDescriptions/LineCountIndex"] = nil
    package.preload["Iris/Data/UseCaseDescriptions/RequirementsLookup"] = function()
        error("standalone requirements failure")
    end
    local failedRequirementsLookup = require("Iris/Data/IrisUseCaseDescriptionsLookup")
    local failedRequirements, failedRequirementsReason =
        failedRequirementsLookup.getRequirements("Open Box of .223 Ammo")
    assert(failedRequirements == nil and failedRequirementsReason == "target_module_load_failure")

    RuntimeDiagnostics.reset()
    package.loaded["Iris/Data/IrisUseCaseDescriptionsLookup"] = nil
    package.loaded["Iris/API/UseCases"] = nil
    package.loaded["Iris/UI/Tooltip/IrisTooltipSummary"] = nil
    package.preload["Iris/Data/IrisUseCaseDescriptionsLookup"] = function()
        error("standalone router unavailable")
    end
    local unavailableUseCases = require("Iris/API/UseCases")
    local unavailableState = unavailableUseCases._getDescriptionState("Base.223Box")
    assert(unavailableState.status == "available" and unavailableState.fallback_used == true)
    assert(#unavailableState.lines == #facade["Base.223Box"].lines)
    local faultState = unavailableUseCases._getDescriptionState("Missing.DoesNotExist")
    assert(faultState.status == "fault" and faultState.reason == "router_unavailable")
    assert(faultState.fallback_used == false)
    local unavailableSummary = require("Iris/UI/Tooltip/IrisTooltipSummary")
    assert(unavailableSummary.get("Base.223Box").useCaseCount == #facade["Base.223Box"].lines)
    local unavailableDiagnostics = RuntimeDiagnostics.getDiagnostics()
    assert(unavailableDiagnostics.surfaces.usecase.fallbackReasons.router_unavailable == 2)
    assert(unavailableDiagnostics.surfaces.usecase_tooltip_line_count.fallbackReasons.router_unavailable == 1)
    print("IRIS_USECASE_LAZY_LOOKUP_PASS parity_count=" .. tostring(parityCount) ..
        " line_count_loaded_chunks=" .. tostring(afterLineCount.loadedDescriptionChunkCount) ..
        " first_lookup_loaded_chunks=" .. tostring(afterFirst.loadedDescriptionChunkCount) ..
        " first_lookup_loaded_modules=" ..
        table.concat(afterFirst.loadedDescriptionChunkModules, ",") ..
        " initial_loaded_modules=" .. table.concat(beforeRepeat.loadedDescriptionChunkModules, ",") ..
        " router_unavailable_count=" ..
        tostring(unavailableDiagnostics.surfaces.usecase.fallbackReasons.router_unavailable) ..
        " normal_miss_facade_loads=" .. tostring(normalMissFacadeLoadsAtObservation))
else
    error("unsupported lookup mode: " .. tostring(mode))
end
