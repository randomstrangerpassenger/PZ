package com.echo.pulse;

import com.echo.lua.LuaCallTracker;
import com.echo.measure.EchoProfiler;
import com.pulse.hook.HookTypes;
import com.pulse.hook.HookTypes.ILuaCallCallback;
import com.pulse.hook.PulseHookRegistry;

/**
 * Pulse LUA_CALL Hook 어댑터 (v2.0 - 중계자 역할)
 * 
 * Pulse의 MixinKahluaThread가 브로드캐스트하는 Lua 호출을 수신하여
 * LuaCallTracker에 직접 위임합니다.
 * 
 * 기존 스택 관리 로직 제거 - LuaCallTracker가 전담.
 */
public class LuaHookAdapter implements ILuaCallCallback {

    private static LuaHookAdapter INSTANCE;
    private static volatile boolean registered = false;

    private final EchoProfiler profiler;
    private final LuaCallTracker tracker;

    public LuaHookAdapter(EchoProfiler profiler, LuaCallTracker tracker) {
        this.profiler = profiler;
        this.tracker = tracker;
    }

    /**
     * Pulse Hook Registry에 콜백 등록
     */
    public static void register() {
        if (registered) {
            System.out.println("[Echo/LuaHook] Already registered");
            return;
        }

        EchoProfiler profiler = EchoProfiler.getInstance();
        LuaCallTracker tracker = LuaCallTracker.getInstance();
        INSTANCE = new LuaHookAdapter(profiler, tracker);

        // Phase 2C: PulseLuaHook 콜백 등록 (InternalLuaHook)
        registerPulseLuaHookCallback(tracker, profiler);

        try {
            PulseHookRegistry.register(HookTypes.LUA_CALL, INSTANCE, "Echo");
            registered = true;

            int callbackCount = PulseHookRegistry.getCallbacks(HookTypes.LUA_CALL).size();
            System.out.println("[Echo/LuaHook] ✅ LUA_CALL callback registered (v2.0)");
            System.out.println("[Echo/LuaHook]   lua_profiling.enabled = " + profiler.isLuaProfilingEnabled());
            System.out.println("[Echo/LuaHook]   LUA_CALL callbacks count = " + callbackCount);
        } catch (Exception e) {
            System.err.println("[Echo/LuaHook] ❌ Failed to register LUA_CALL callback: " + e.getMessage());
            registered = false;
        }
    }

    private static void registerPulseLuaHookCallback(LuaCallTracker tracker, EchoProfiler profiler) {
        try {
            com.pulse.internal.InternalLuaHook.setCallback(
                    (eventName, durationMicros) -> {
                        tracker.recordEventCall(eventName, durationMicros, 1);
                    });

            com.pulse.internal.InternalLuaHook.setProfilingEnabled(profiler.isLuaProfilingEnabled());
            System.out.println("[Echo/LuaHook] ✅ InternalLuaHook callback registered");
        } catch (NoClassDefFoundError e) {
            System.out.println("[Echo/LuaHook] ⚠ InternalLuaHook not available");
        } catch (Exception e) {
            System.err.println("[Echo/LuaHook] ❌ Failed to register InternalLuaHook: " + e.getMessage());
        }
    }

    public static void unregister() {
        if (!registered || INSTANCE == null)
            return;

        try {
            PulseHookRegistry.unregister(HookTypes.LUA_CALL, INSTANCE);
            System.out.println("[Echo/LuaHook] LUA_CALL callback unregistered");
        } catch (Exception e) {
            System.err.println("[Echo/LuaHook] Failed to unregister: " + e.getMessage());
        } finally {
            registered = false;
            INSTANCE = null;
        }
    }

    public static boolean isRegistered() {
        return registered;
    }

    // ─────────────────────────────────────────────────────────────
    // ILuaCallCallback Implementation (nanoTime 버전 사용)
    // ─────────────────────────────────────────────────────────────

    @Override
    public void onLuaCallStart(Object function, long startNanos) {
        // LuaCallTracker에 직접 위임 (스택 관리는 Tracker에서)
        tracker.recordCallStart(function, startNanos);
    }

    @Override
    public void onLuaCallEnd(Object function, long endNanos) {
        // LuaCallTracker에 직접 위임
        tracker.recordCallEnd(function, endNanos);
    }

    // Legacy 메서드 (하위 호환성 - 사용되지 않음)
    @Override
    public void onLuaCallStart(Object function) {
        // nanoTime 버전이 호출되므로 여기는 실행되지 않음
    }

    @Override
    public void onLuaCallEnd(Object function) {
        // nanoTime 버전이 호출되므로 여기는 실행되지 않음
    }

    /**
     * 진단 정보 출력
     */
    public static void printDiagnostics() {
        System.out.println("\n[Echo/LuaHook] === Diagnostics ===");
        System.out.println("  registered = " + registered);
        if (INSTANCE != null) {
            System.out.println("  lua_profiling.enabled = " + INSTANCE.profiler.isLuaProfilingEnabled());
            System.out.println("  detailed_active = " + INSTANCE.tracker.isDetailedActive());
            System.out.println("  total_calls = " + INSTANCE.tracker.getTotalCalls());
            System.out.println("  sampled_calls = " + INSTANCE.tracker.getSampledCalls());
        }
        try {
            int count = PulseHookRegistry.getCallbacks(HookTypes.LUA_CALL).size();
            System.out.println("  LUA_CALL callbacks = " + count);
        } catch (Exception e) {
            System.out.println("  LUA_CALL callbacks = (error: " + e.getMessage() + ")");
        }
        System.out.println();
    }
}
