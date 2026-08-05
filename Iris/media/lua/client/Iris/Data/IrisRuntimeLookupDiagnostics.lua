-- Shared lazy-lookup diagnostics, including failures that occur before a router can load.
local IrisRuntimeLookupDiagnostics = {}

local countsBySurface = {}

local function surfaceState(surface)
    local state = countsBySurface[surface]
    if not state then
        state = { fallbackCount = 0, fallbackReasons = {} }
        countsBySurface[surface] = state
    end
    return state
end

function IrisRuntimeLookupDiagnostics.recordFallback(surface, reason)
    local normalizedSurface = tostring(surface or "unknown")
    local normalizedReason = tostring(reason or "unknown")
    local state = surfaceState(normalizedSurface)
    state.fallbackCount = state.fallbackCount + 1
    state.fallbackReasons[normalizedReason] = (state.fallbackReasons[normalizedReason] or 0) + 1
end

function IrisRuntimeLookupDiagnostics.getDiagnostics()
    local surfaces = {}
    local total = 0
    for surface, state in pairs(countsBySurface) do
        local reasons = {}
        for reason, count in pairs(state.fallbackReasons) do reasons[reason] = count end
        surfaces[surface] = {
            fallbackCount = state.fallbackCount,
            fallbackReasons = reasons,
        }
        total = total + state.fallbackCount
    end
    return { fallbackCount = total, surfaces = surfaces }
end

function IrisRuntimeLookupDiagnostics.reset()
    countsBySurface = {}
end

return IrisRuntimeLookupDiagnostics
