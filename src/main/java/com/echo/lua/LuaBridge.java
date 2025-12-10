package com.echo.lua;

import com.echo.config.EchoConfig;

/**
 * Bridge for Lua scripts to communicate with Echo.
 * Exposed methods should be called from Lua.
 */
public class LuaBridge {

    /**
     * Check if Sampling Profiler should be enabled.
     */
    public static boolean isSamplingEnabled() {
        return EchoConfig.getInstance().isLuaProfilingEnabled() && EchoConfig.getInstance().isLuaSamplingEnabled(); // Need
                                                                                                                    // to
                                                                                                                    // add
                                                                                                                    // isLuaSamplingEnabled
                                                                                                                    // to
                                                                                                                    // config
    }

    /**
     * Record a sample from Lua.
     */
    public static void recordSample(String functionName, String source) {
        // Pass to LuaCallTracker
        // For sampling, we might want a separate 'SampleStats' or just increment call
        // count?
        // Sampling tells us "Time spent in function". effectively similar to duration.
        // If we sample every X instructions, frequency ~ time.

        // For now, let's log or aggregate in tracker.
        // We'll add recordSample to LuaCallTracker.
        LuaCallTracker.getInstance().recordFunctionCall(functionName, source, 1); // treating 1 sample as 1 unit of
                                                                                  // "heavy"
    }
}
