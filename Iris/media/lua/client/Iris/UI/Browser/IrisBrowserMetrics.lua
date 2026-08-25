-- Browser build/query instrumentation. Diagnostic state never changes query results.
local IrisBrowserMetrics = {}

local ProtectedCall = require("Iris/Util/IrisProtectedCall")

local function newCounters()
    return {
        buildAttempts = 0,
        getAllItemsCallCount = 0,
        scannedItemCount = 0,
        lastBuildElapsedMilliseconds = 0,
        lastScanElapsedMilliseconds = 0,
        coldOpenCount = 0,
        warmReopenCount = 0,
        lastColdOpenElapsedMilliseconds = 0,
        lastWarmReopenElapsedMilliseconds = 0,
        generationInvalidationCount = 0,
        postIndexMaterializationPassCount = 0,
        materializedRowCount = 0,
        retainedItemReferenceCount = 0,
        tagArrayToSetConversionCount = 0,
        chooseLocationComparisonCount = 0,
        initialSearchSortCount = 0,
    }
end

function IrisBrowserMetrics.create()
    local enabled = false
    local counters = newCounters()
    local metrics = {}

    function metrics.isEnabled()
        return enabled
    end

    function metrics.setEnabled(value)
        enabled = value == true
        counters = newCounters()
    end

    function metrics.reset()
        counters = newCounters()
    end

    function metrics.nowMilliseconds()
        if getTimestampMs then
            local ok, value = ProtectedCall.engine(getTimestampMs)
            if ok and type(value) == "number" then return value end
        end
        if os and os.clock then return os.clock() * 1000 end
        return 0
    end

    function metrics.increment(name, amount)
        if not enabled then return end
        counters[name] = (counters[name] or 0) + (amount or 1)
    end

    function metrics.set(name, value)
        if not enabled then return end
        counters[name] = value
    end

    function metrics.finishBuild(startedAt)
        if not enabled then return end
        counters.lastBuildElapsedMilliseconds = math.max(
            0,
            metrics.nowMilliseconds() - startedAt
        )
    end

    function metrics.recordItemIndex(itemIndex)
        if not enabled or not itemIndex then return end
        metrics.increment("getAllItemsCallCount", itemIndex.getAllItemsCallCount or 0)
        metrics.increment("scannedItemCount", itemIndex.scannedItemCount or 0)
        metrics.set("lastScanElapsedMilliseconds", itemIndex.elapsedMilliseconds or 0)
    end

    function metrics.recordWarmReopen(startedAt)
        if not enabled then return end
        metrics.increment("warmReopenCount")
        metrics.set(
            "lastWarmReopenElapsedMilliseconds",
            math.max(0, metrics.nowMilliseconds() - startedAt)
        )
    end

    function metrics.recordColdOpen()
        if not enabled then return end
        metrics.increment("coldOpenCount")
        metrics.set(
            "lastColdOpenElapsedMilliseconds",
            counters.lastBuildElapsedMilliseconds
        )
    end

    function metrics.snapshot(state, generation)
        local result = {
            enabled = enabled,
            state = state,
            generation = generation,
            lastElapsedMilliseconds = counters.lastBuildElapsedMilliseconds,
        }
        for name, value in pairs(counters) do result[name] = value end
        return result
    end

    return metrics
end

return IrisBrowserMetrics
