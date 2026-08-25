-- Owns Browser cache generation, dependency readiness, and explicit invalidation.
local IrisBrowserLifecycle = {}

local bootstrap = require("Iris/Util/IrisModuleBootstrap").create()
local safeRequire = bootstrap.safeRequire
local debug = bootstrap.debug
local warn = bootstrap.warn
local IrisBrowserItemIndex = require("Iris/UI/Browser/IrisBrowserItemIndex")
local ProjectionBuilder = require("Iris/UI/Browser/IrisBrowserProjectionBuilder")
local IrisLogger = require("Iris/Util/IrisLogger")

local READY_STATES = {
    ready = true,
    degraded_ready = true,
}

function IrisBrowserLifecycle.create(options)
    options = options or {}
    local metrics = options.metrics
    local cache = nil
    local irisApi = nil
    local state = "uninitialized"
    local reason = "not_built"
    local dependency = nil
    local generation = 0
    local lifecycle = {}

    local function setState(nextState, nextReason, nextDependency)
        state = nextState
        reason = nextReason
        dependency = nextDependency
    end

    local function snapshot()
        return {
            state = state,
            reason = reason,
            dependency = dependency,
            generation = generation,
        }
    end

    local function ensureDependencies()
        if not irisApi then
            local ok, result = safeRequire("Iris/IrisAPI")
            if ok then irisApi = result end
        end
    end

    function lifecycle.getState()
        return snapshot()
    end

    function lifecycle.isReady()
        return READY_STATES[state] == true
    end

    function lifecycle.getCache()
        return cache
    end

    function lifecycle.getApi()
        return irisApi
    end

    function lifecycle.getGeneration()
        return generation
    end

    function lifecycle.ensureReady()
        local callStartedAt = metrics.isEnabled() and metrics.nowMilliseconds() or 0
        if READY_STATES[state] then
            metrics.recordWarmReopen(callStartedAt)
            return true, snapshot()
        end
        if state == "building" then return false, snapshot() end

        local buildStartedAt = metrics.isEnabled() and metrics.nowMilliseconds() or 0
        setState("building", "build_in_progress", nil)
        metrics.increment("buildAttempts")
        if IrisLogger.isDebugEnabled() then debug("[IrisBrowserData] Building cache...") end
        ensureDependencies()

        if not irisApi then
            metrics.finishBuild(buildStartedAt)
            setState("retryable_failed", "required_dependency_unavailable", "Iris/IrisAPI")
            warn("[IrisBrowserData] required dependency unavailable: Iris/IrisAPI")
            return false, snapshot()
        end
        if not irisApi.Tags or not irisApi.Tags.getTagsForItem then
            metrics.finishBuild(buildStartedAt)
            setState("retryable_failed", "required_dependency_unavailable", "IrisAPI.Tags")
            warn("[IrisBrowserData] required dependency unavailable: IrisAPI.Tags")
            return false, snapshot()
        end

        local itemIndexOk, itemIndex, itemIndexFailure = pcall(IrisBrowserItemIndex.build)
        if not itemIndexOk then
            metrics.finishBuild(buildStartedAt)
            setState("retryable_failed", "item_index_build_failed", "getAllItems")
            warn("[IrisBrowserData] item index build failed: " .. tostring(itemIndex))
            return false, snapshot()
        end
        metrics.recordItemIndex(itemIndex)
        if itemIndexFailure then
            metrics.finishBuild(buildStartedAt)
            setState(
                "retryable_failed",
                itemIndexFailure or "item_index_unavailable",
                "getAllItems"
            )
            warn("[IrisBrowserData] item index unavailable: " .. tostring(itemIndexFailure))
            return false, snapshot()
        end

        local buildOk, candidate, taggedCount, errorCount = pcall(
            ProjectionBuilder.build,
            itemIndex,
            {
                categoryOrder = options.categoryOrder,
                subcategoryMap = options.subcategoryMap,
                currentGeneration = generation,
                metrics = metrics,
            }
        )
        if not buildOk then
            metrics.finishBuild(buildStartedAt)
            setState("retryable_failed", "cache_build_failed", "IrisBrowserData.cache")
            warn("[IrisBrowserData] cache build failed: " .. tostring(candidate))
            return false, snapshot()
        end
        cache = candidate
        generation = candidate.generation
        metrics.finishBuild(buildStartedAt)
        metrics.recordColdOpen()

        if not irisApi.Index or not irisApi.Index.getRecipeConnectionsForItem then
            setState("degraded_ready", "optional_dependency_unavailable", "IrisAPI.Index")
            warn("[IrisBrowserData] optional dependency unavailable: IrisAPI.Index")
        else
            setState("ready", "build_complete", nil)
        end
        if IrisLogger.isDebugEnabled() then
            debug("[IrisBrowserData] Cache built: " .. tostring(candidate.itemIndex.itemCount) ..
                " items indexed, " .. taggedCount .. " tagged, errors=" .. errorCount ..
                ", state=" .. state)
        end
        return true, snapshot()
    end

    function lifecycle.resetForReload()
        irisApi = nil
        cache = nil
        metrics.increment("generationInvalidationCount")
        setState("uninitialized", "explicit_reload_reset", nil)
    end

    return lifecycle
end

return IrisBrowserLifecycle
