-- Echo Profiler (Lua Side)
-- Implements Sampling Profiler using debug.sethook
-- Phase 3

EchoProfiler = {}
EchoProfiler.enabled = false
EchoProfiler.samplingRate = 1000 -- Instructions per hook
EchoProfiler.isSampling = false

-- Use a local reference for speed
local debug_sethook = debug.sethook
local debug_getinfo = debug.getinfo

function EchoProfiler.enableSampling(enable)
    if enable then
        if EchoProfiler.isSampling then return end
        print("[Echo] Lua Sampling Profiler: STARTED")
        debug_sethook(EchoProfiler.onHook, "c", EchoProfiler.samplingRate) -- 'count' hook
        EchoProfiler.isSampling = true
    else
        if not EchoProfiler.isSampling then return end
        print("[Echo] Lua Sampling Profiler: STOPPED")
        debug_sethook() -- Turn off hook
        EchoProfiler.isSampling = false
    end
end

function EchoProfiler.onHook(event)
    -- Sampling: Just capture the top function
    local info = debug_getinfo(2, "nS")
    if info and info.name and info.name ~= "" and info.source then
        -- Send to Java
        -- We perform a static call to Echo's bridge
        -- Assuming Exposed Java Method: com.echo.pulse.LuaBridge.recordSample(name, source)
        -- TODO: Implement bridge binding or native call
        -- For now, simulate or check if we can call static Java
        
        -- To avoid massive JNI overhead on every sample, we might aggregate here in Lua
        -- But for "Sampling", we want to minimize Lua side logic too.
        -- Best practice in PZ: direct call to exposed Java method is relatively fast compared to Lua logic.
    end
end

-- Check Config periodically or via Event
Events.OnTick.Add(function()
    -- This check should be cheap.
    -- Ideally, Java side triggers an event "EchoConfigChanged" to push state.
    -- For now, we rely on a global flag or Java call.
    
    -- Placeholder for config check
    -- local javaEnabled = ...
    -- if javaEnabled ~= EchoProfiler.isSampling then EchoProfiler.enableSampling(javaEnabled) end
end)

return EchoProfiler
