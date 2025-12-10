package com.echo.pulse;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;

/**
 * Lua 프로파일러
 * 
 * Lua 이벤트 및 함수 호출을 측정합니다.
 * On-Demand 방식으로 필요할 때만 활성화합니다.
 * 
 * 주의: Lua 호출은 빈도가 높으므로 성능 영향을 줄 수 있습니다.
 */
public class LuaProfiler {

    private static final EchoProfiler profiler = EchoProfiler.getInstance();

    /**
     * Lua 이벤트 래퍼
     */
    public static void profileEvent(String eventName, Runnable luaCallback) {
        if (!profiler.isEnabled() || !profiler.isLuaProfilingEnabled()) {
            luaCallback.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.LUA_EVENT, eventName)) {
            luaCallback.run();
        }
    }

    /**
     * Lua 함수 호출 래퍼
     */
    public static void profileFunction(String functionName, Runnable luaFunction) {
        if (!profiler.isEnabled() || !profiler.isLuaProfilingEnabled()) {
            luaFunction.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.LUA_FUNCTION, functionName)) {
            luaFunction.run();
        }
    }

    /**
     * 결과를 반환하는 Lua 함수 호출 래퍼
     */
    public static <T> T profileFunctionWithResult(String functionName, java.util.function.Supplier<T> luaFunction) {
        if (!profiler.isEnabled() || !profiler.isLuaProfilingEnabled()) {
            return luaFunction.get();
        }

        try (var scope = profiler.scope(ProfilingPoint.LUA_FUNCTION, functionName)) {
            return luaFunction.get();
        }
    }

    /**
     * Lua GC 측정
     */
    public static void profileGC(Runnable gcTask) {
        if (!profiler.isEnabled() || !profiler.isLuaProfilingEnabled()) {
            gcTask.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.LUA_GC)) {
            gcTask.run();
        }
    }

    /**
     * Lua 프로파일링 활성화
     */
    public static void enable() {
        profiler.enableLuaProfiling();
    }

    /**
     * Lua 프로파일링 비활성화
     */
    public static void disable() {
        profiler.disableLuaProfiling();
    }

    /**
     * Lua 프로파일링 상태 확인
     */
    public static boolean isEnabled() {
        return profiler.isLuaProfilingEnabled();
    }

    /**
     * Lua 프로파일링 토글
     */
    public static boolean toggle() {
        if (profiler.isLuaProfilingEnabled()) {
            profiler.disableLuaProfiling();
            return false;
        } else {
            profiler.enableLuaProfiling();
            return true;
        }
    }
}
