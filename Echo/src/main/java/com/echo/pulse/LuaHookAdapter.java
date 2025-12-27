package com.echo.pulse;

import com.echo.lua.LuaCallTracker;
import com.echo.measure.EchoProfiler;
import com.pulse.api.di.PulseServices;
import com.pulse.api.hook.HookType;
import com.pulse.api.log.PulseLogger;

/**
 * Pulse LUA_CALL Hook 어댑터.
 * 
 * Lua 함수 호출을 추적하여 EchoProfiler에 전달합니다.
 * Phase 4: IPulseHookRegistry.register() 사용하여 복원.
 * 
 * @since Echo 2.0
 * @since Echo 3.0 - Stub Implementation (Phase 3)
 * @since Echo 4.0 - Restored with IPulseHookRegistry (Phase 4)
 */
public class LuaHookAdapter {

    private static final String OWNER_ID = "echo";
    private static volatile boolean registered = false;
    private static LuaCallCallback callback;

    /**
     * Lua Call 콜백 인터페이스.
     * Pulse Hook에서 호출됩니다.
     */
    public interface LuaCallCallback {
        void onLuaCall(String functionName, long durationNanos);
    }

    /**
     * Pulse Hook Registry에 콜백 등록.
     */
    public static void register() {
        if (registered) {
            return;
        }

        try {
            callback = LuaHookAdapter::handleLuaCall;
            PulseServices.hooks().register(HookType.LUA_CALL, callback, OWNER_ID);
            registered = true;
            PulseLogger.info("Echo/LuaHook", "LuaHookAdapter registered (Phase 4 - IPulseHookRegistry)");
        } catch (IllegalStateException e) {
            PulseLogger.warn("Echo/LuaHook", "LuaHookAdapter registration failed: PulseServices not initialized");
        } catch (Exception e) {
            PulseLogger.error("Echo/LuaHook", "LuaHookAdapter registration failed: " + e.getMessage());
        }
    }

    /**
     * Pulse Hook Registry에서 콜백 해제.
     */
    public static void unregister() {
        if (!registered) {
            return;
        }

        try {
            if (callback != null) {
                PulseServices.hooks().unregister(HookType.LUA_CALL, callback);
                callback = null;
            }
            registered = false;
            PulseLogger.info("Echo/LuaHook", "LuaHookAdapter unregistered");
        } catch (Exception e) {
            // Ignore - may already be shutdown
        }
    }

    /**
     * Lua 호출 처리 - Pulse에서 콜백됨.
     */
    private static void handleLuaCall(String functionName, long durationNanos) {
        try {
            EchoProfiler profiler = EchoProfiler.getInstance();
            if (profiler.isLuaProfilingEnabled()) {
                // Convert nanos to micros
                long durationMicros = durationNanos / 1000;
                LuaCallTracker.getInstance().recordFunctionCall(functionName, durationMicros);
            }
        } catch (Exception e) {
            // Silent fail - don't disrupt game
        }
    }

    public static boolean isRegistered() {
        return registered;
    }

    /**
     * 진단 정보 출력.
     */
    public static void printDiagnostics() {
        PulseLogger.info("Echo/LuaHook", "=== Diagnostics ===");
        PulseLogger.info("Echo/LuaHook", "registered = " + registered);
        PulseLogger.info("Echo/LuaHook", "status = " + (registered ? "ACTIVE" : "INACTIVE"));

        try {
            int hookCount = PulseServices.hooks().getCallbackCount(HookType.LUA_CALL);
            PulseLogger.info("Echo/LuaHook", "total_lua_hooks = " + hookCount);
        } catch (Exception e) {
            PulseLogger.info("Echo/LuaHook", "total_lua_hooks = UNAVAILABLE");
        }

        EchoProfiler profiler = EchoProfiler.getInstance();
        LuaCallTracker tracker = LuaCallTracker.getInstance();

        PulseLogger.info("Echo/LuaHook", "lua_profiling.enabled = " + profiler.isLuaProfilingEnabled());
        PulseLogger.info("Echo/LuaHook", "detailed_active = " + tracker.isDetailedActive());
        PulseLogger.info("Echo/LuaHook", "total_calls = " + tracker.getTotalCalls());
    }
}
