package com.echo.pulse;

import com.echo.lua.LuaCallTracker;
import com.echo.measure.EchoProfiler;
import com.pulse.hook.HookTypes;
import com.pulse.hook.HookTypes.ILuaCallCallback;
import com.pulse.hook.PulseHookRegistry;

import java.util.ArrayDeque;
import java.util.Deque;

/**
 * Pulse LUA_CALL Hook 어댑터
 * 
 * Pulse의 MixinKahluaThread가 브로드캐스트하는 Lua 호출을 수신하여
 * LuaCallTracker에 기록합니다.
 * 
 * @since 2.2.0 - Pulse LUA_CALL integration
 */
public class LuaHookAdapter implements ILuaCallCallback {

    private static LuaHookAdapter INSTANCE;
    private static volatile boolean registered = false;

    // 메인 스레드용 Fast-Path 스택 (ThreadLocal 우회)
    private static volatile Thread mainThread = null;
    private final Deque<LuaFrame> mainThreadStack = new ArrayDeque<>();

    // 다른 스레드용 스택
    private final ThreadLocal<Deque<LuaFrame>> frameStack = ThreadLocal.withInitial(ArrayDeque::new);

    // 의존성
    private final EchoProfiler profiler;
    private final LuaCallTracker tracker;

    /**
     * Lightweight frame for tracking nested Lua calls.
     * Uses startTime only - function identity is NOT relied upon for matching.
     */
    private static class LuaFrame {
        final long startNanos;
        final String functionName;

        LuaFrame(long startNanos, String functionName) {
            this.startNanos = startNanos;
            this.functionName = functionName;
        }
    }

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

        // Phase 2C: PulseLuaHook 콜백 등록 (신규 방식)
        registerPulseLuaHookCallback(tracker, profiler);

        try {
            PulseHookRegistry.register(HookTypes.LUA_CALL, INSTANCE, "Echo");
            registered = true;

            // [Safeguard A] 등록 성공 로그
            int callbackCount = PulseHookRegistry.getCallbacks(HookTypes.LUA_CALL).size();
            System.out.println("[Echo/LuaHook] ✅ LUA_CALL callback registered");
            System.out.println("[Echo/LuaHook]   lua_profiling.enabled = " + profiler.isLuaProfilingEnabled());
            System.out.println("[Echo/LuaHook]   LUA_CALL callbacks count = " + callbackCount);
        } catch (Exception e) {
            System.err.println("[Echo/LuaHook] ❌ Failed to register LUA_CALL callback: " + e.getMessage());
            registered = false;
        }
    }

    /**
     * Phase 2C: InternalLuaHook 콜백 등록
     * 
     * MixinLuaEventManager → InternalLuaHook → 이 콜백 → LuaCallTracker
     * (pulse-api 대신 Pulse 내부 클래스 사용 - Gradle 의존성 문제 우회)
     */
    private static void registerPulseLuaHookCallback(LuaCallTracker tracker, EchoProfiler profiler) {
        try {
            com.pulse.internal.InternalLuaHook.setCallback(
                    (eventName, durationMicros) -> {
                        // LuaCallTracker.recordEventCall(eventName, durationMicros, handlerCount)
                        // handlerCount는 현재 알 수 없으므로 1로 설정
                        tracker.recordEventCall(eventName, durationMicros, 1);
                    });

            // 프로파일링 활성화 상태 동기화
            com.pulse.internal.InternalLuaHook.setProfilingEnabled(profiler.isLuaProfilingEnabled());

            System.out.println("[Echo/LuaHook] ✅ InternalLuaHook callback registered (Phase 2C)");
            System.out.println("[Echo/LuaHook]   profilingEnabled = " + profiler.isLuaProfilingEnabled());
        } catch (NoClassDefFoundError e) {
            System.out.println("[Echo/LuaHook] ⚠ InternalLuaHook not available (Phase 2C disabled)");
        } catch (Exception e) {
            System.err.println("[Echo/LuaHook] ❌ Failed to register InternalLuaHook callback: " + e.getMessage());
        }
    }

    /**
     * Pulse Hook Registry에서 콜백 해제
     */
    public static void unregister() {
        if (!registered || INSTANCE == null) {
            return;
        }

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

    /**
     * 등록 상태 확인
     */
    public static boolean isRegistered() {
        return registered;
    }

    /**
     * 메인 스레드 설정 (Fast-Path용)
     */
    public static void setMainThread(Thread thread) {
        mainThread = thread;
    }

    // --- ILuaCallCallback Implementation ---

    @Override
    public void onLuaCallStart(Object function) {
        // [Safeguard D] Performance double-guard - Echo 측 체크
        if (!profiler.isLuaProfilingEnabled()) {
            return;
        }

        String funcName = extractFunctionName(function);
        long startNanos = System.nanoTime();

        // [Safeguard C] Stack에는 frame만 push (function 객체 동일성 의존 안 함)
        getStack().push(new LuaFrame(startNanos, funcName));
    }

    @Override
    public void onLuaCallEnd(Object function) {
        if (!profiler.isLuaProfilingEnabled()) {
            return;
        }

        Deque<LuaFrame> stack = getStack();
        if (stack.isEmpty()) {
            return; // Unmatched end - skip silently
        }

        // [Safeguard C] Pop만 하고 function은 이름 추출용으로만 사용
        LuaFrame frame = stack.pop();
        long durationMicros = (System.nanoTime() - frame.startNanos) / 1000;

        // Record to LuaCallTracker
        tracker.recordFunctionCall(frame.functionName, durationMicros);
    }

    // --- Internal Helpers ---

    private Deque<LuaFrame> getStack() {
        if (Thread.currentThread() == mainThread) {
            return mainThreadStack;
        }
        return frameStack.get();
    }

    /**
     * Function object에서 이름 추출 (Reflection 기반)
     * LuaClosure 타입에 직접 의존하지 않아 컴파일 시점에 kahlua.jar 불필요
     */
    private String extractFunctionName(Object function) {
        if (function == null) {
            return "<anonymous>";
        }

        // Reflection으로 LuaClosure.prototype.name 추출 시도
        try {
            // function.prototype 필드 접근
            java.lang.reflect.Field prototypeField = function.getClass().getField("prototype");
            Object prototype = prototypeField.get(function);

            if (prototype != null) {
                // prototype.name 필드 접근
                java.lang.reflect.Field nameField = prototype.getClass().getField("name");
                Object name = nameField.get(prototype);
                if (name != null) {
                    return name.toString();
                }

                // name이 없으면 lines[0] 시도
                java.lang.reflect.Field linesField = prototype.getClass().getField("lines");
                Object lines = linesField.get(prototype);
                if (lines != null && lines.getClass().isArray()) {
                    int length = java.lang.reflect.Array.getLength(lines);
                    if (length > 0) {
                        Object firstLine = java.lang.reflect.Array.get(lines, 0);
                        return "<closure@line:" + firstLine + ">";
                    }
                }
            }
        } catch (NoSuchFieldException | IllegalAccessException | SecurityException e) {
            // Reflection 실패 - fallback 사용
        }

        // Fallback: toString()
        String str = function.toString();
        if (str.length() > 50) {
            return str.substring(0, 47) + "...";
        }
        return str;
    }

    /**
     * 진단 정보 출력
     */
    public static void printDiagnostics() {
        System.out.println("\n[Echo/LuaHook] === Diagnostics ===");
        System.out.println("  registered = " + registered);
        if (INSTANCE != null) {
            System.out.println("  lua_profiling.enabled = " + INSTANCE.profiler.isLuaProfilingEnabled());
            System.out.println("  mainThread set = " + (mainThread != null));
            System.out.println("  mainThreadStack size = " + INSTANCE.mainThreadStack.size());
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
