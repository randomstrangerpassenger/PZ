local repositoryRoot = assert(arg and arg[1], "repository root argument is required"):gsub("\\", "/")
package.path = repositoryRoot .. "/Iris/media/lua/client/?.lua;" .. package.path

local nativeRequire = require
local requireCounts = {}
require = function(moduleName)
    requireCounts[moduleName] = (requireCounts[moduleName] or 0) + 1
    return nativeRequire(moduleName)
end

local CHUNK_INDEX = "Iris/Data/UseCaseDescriptions/ChunkIndex"
local LINE_INDEX = "Iris/Data/UseCaseDescriptions/LineCountIndex"
local LOOKUP = "Iris/Data/IrisUseCaseDescriptionsLookup"
local CHUNK = "Iris/Data/UseCaseDescriptions/Chunk999"
local MISSING = {}

local function rangeIndex(fullType, entryCount)
    return {
        schema_version = "iris_usecase_chunk_range_index_v1",
        entry_count = entryCount or 1,
        chunks = {{
            count = 1,
            first = fullType,
            last = fullType,
            module = CHUNK,
            sha256 = string.rep("0", 64),
        }},
    }
end

local function lineIndex(rows, entryCount)
    local count = entryCount or 0
    if entryCount == nil then
        for _, _ in pairs(rows) do count = count + 1 end
    end
    return {
        schema_version = "iris_usecase_line_count_index_v1",
        entry_count = count,
        lineCounts = rows,
    }
end

local function unload()
    for _, name in ipairs({ LOOKUP, CHUNK_INDEX, LINE_INDEX, CHUNK }) do
        package.loaded[name] = nil
        package.preload[name] = nil
    end
end

local function loadLookup(chunkValue, lineValue, chunkValueTable)
    unload()
    requireCounts = {}
    if chunkValue == MISSING then
        package.preload[CHUNK_INDEX] = function() error("fixture missing ChunkIndex") end
    else
        package.preload[CHUNK_INDEX] = function() return chunkValue end
    end
    package.preload[LINE_INDEX] = function() return lineValue end
    package.preload[CHUNK] = function() return chunkValueTable or {} end
    return require(LOOKUP)
end

local validChunk = rangeIndex("Base.Item")
local validLine = lineIndex({ ["Base.Item"] = 1 })
local validTarget = { ["Base.Item"] = { lines = {{ display_text = "fixture" }} } }
local lookup = loadLookup(validChunk, validLine, validTarget)
assert(requireCounts[CHUNK_INDEX] == nil and requireCounts[LINE_INDEX] == nil)
local before = lookup.getDiagnostics()
assert(before.chunkIndexState == "unloaded" and before.lineCountIndexState == "unloaded")
assert(before.indexMetadataMaterializationCount == 0)

local count, reason = lookup.getLineCount("Base.Item")
assert(count == 1 and reason == nil)
local afterCount = lookup.getDiagnostics()
assert(afterCount.chunkIndexState == "valid" and afterCount.lineCountIndexState == "valid")
assert(afterCount.crossCheckState == "valid")
assert(afterCount.indexMetadataMaterializationCount == 1)
assert(afterCount.chunkIndexRequireCallCount == 1 and afterCount.lineCountIndexRequireCallCount == 1)
assert(afterCount.indexEntryCountCrossCheckCount == 1)
assert(afterCount.loadedDescriptionChunkCount == 0)
assert(lookup.getLineCount("Base.Item") == 1)
assert(lookup.getDiagnostics().indexMetadataMaterializationCount == 1)

local entry = assert(lookup.get("Base.Item"))
assert(#entry.lines == 1)
local afterGet = lookup.getDiagnostics()
assert(afterGet.indexMetadataMaterializationCount == 1)
assert(afterGet.loadedDescriptionChunkCount == 1)

local malformedChunk = { schema_version = "invalid", chunks = {}, entry_count = 0 }
lookup = loadLookup(malformedChunk, validLine, validTarget)
count, reason = lookup.getLineCount("Base.Item")
assert(count == 1 and reason == nil)
local asymmetric = lookup.getDiagnostics()
assert(asymmetric.chunkIndexState == "invalid")
assert(asymmetric.lineCountIndexState == "valid")
assert(asymmetric.crossCheckState == "not_applicable")
assert(asymmetric.fallbackCount == 0)
local missingCount, missingReason = lookup.getLineCount("Base.Missing")
assert(missingCount == 0 and missingReason == nil)
local invalidEntry, invalidReason = lookup.get("Base.Item")
assert(invalidEntry == nil and invalidReason == "index_shape_invalid")

lookup = loadLookup(MISSING, validLine, validTarget)
count, reason = lookup.getLineCount("Base.Item")
assert(count == 1 and reason == nil)
local missingChunk = lookup.getDiagnostics()
assert(missingChunk.chunkIndexState == "invalid")
assert(missingChunk.chunkIndexReason == "router_unavailable")
assert(missingChunk.lineCountIndexState == "valid")
assert(missingChunk.crossCheckState == "not_applicable" and missingChunk.fallbackCount == 0)

local malformedLine = { schema_version = "invalid", lineCounts = {}, entry_count = 0 }
lookup = loadLookup(validChunk, malformedLine, validTarget)
local _, getReason = lookup.get("Base.Item")
local _, countReason = lookup.getLineCount("Base.Item")
assert(getReason == "index_shape_invalid" and countReason == "index_shape_invalid")

lookup = loadLookup(validChunk, lineIndex({ ["Base.Item"] = 1, ["Base.Other"] = 0 }), validTarget)
local mismatchCount, mismatchReason = lookup.getLineCount("Base.Item")
assert(mismatchCount == nil and mismatchReason == "index_content_mismatch")
local mismatchEntry, mismatchGetReason = lookup.get("Base.Item")
assert(mismatchEntry == nil and mismatchGetReason == "index_content_mismatch")

lookup = loadLookup(
    rangeIndex("Base.Other"),
    lineIndex({ ["Base.Item"] = 1 }),
    { ["Base.Other"] = { lines = {{ display_text = "other" }} } }
)
local absentRecord, absentReason = lookup.get("Base.Item")
assert(absentRecord == nil and absentReason == "index_content_mismatch")

print("IRIS_LINE_COUNT_LAZY_VALIDATION_PASS matrix=valid,chunk-invalid,line-invalid,mismatch,chunk-missing")
