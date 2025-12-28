package com.echo.pulse;

import com.echo.lua.LuaCallTracker;
import com.echo.measure.EchoProfiler;
import com.pulse.api.di.PulseServices;
import com.pulse.api.hook.HookType;
import com.pulse.api.hook.ILuaCallCallback;
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
 * @since Echo 4.1 - Uses pulse-api ILuaCallCallback interface
 */
public class LuaHookAdapter {

    private static final String OWNER_ID = "echo";
    private static volatile boolean registered = false;
    private static ILuaCallCallback callback;

    /**
     * Pulse Hook Registry에 콜백 등록.
     */
    public static void register() {
        if (registered) {
            return;
        }

        try {
            callback = new EchoLuaCallCallback();
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

    /**
     * ILuaCallCallback 구현체.
     * pulse-api의 공통 인터페이스를 구현.
     */
    private static class EchoLuaCallCallback implements ILuaCallCallback {

        @Override
        public void onLuaCall(String functionName, long durationNanos) {
            try {
                EchoProfiler profiler = EchoProfiler.getInstance();
                if (profiler.isLuaProfilingEnabled()) {
                    long durationMicros = durationNanos / 1000;
                    LuaCallTracker.getInstance().recordFunctionCall(functionName, durationMicros);
                }
            } catch (Exception e) {
                // Silent fail - don't disrupt game
            }
        }

        @Override
        public void onLuaCallEnd(Object function, long endNanos) {
            // 이 메서드는 Mixin에서 호출됨 - 여기서는 사용하지 않음
        }
    }
}
