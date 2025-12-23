package com.pulse.lua;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.util.ReflectionCache;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Lua 함수 호출 및 전역 변수 접근.
 * 
 * <p>
 * v2.0: LuaBridge에서 분리됨
 * </p>
 * 
 * @since Pulse 2.0
 */
public final class LuaCallInvoker {

    private static final String LOG = PulseLogger.PULSE;
    private static final LuaCallInvoker INSTANCE = new LuaCallInvoker();
    private static final AtomicLong callCount = new AtomicLong(0);

    private LuaCallInvoker() {
    }

    public static LuaCallInvoker getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // Lua 함수 호출
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 함수 호출.
     * 
     * @param functionPath 함수 경로 (예: "Events.OnTick.Add" 또는 단순히 "print")
     * @param args         인자들
     * @return 반환값 (없으면 null)
     */
    public Object call(String functionPath, Object... args) {
        if (!LuaStateManager.getInstance().isAvailable()) {
            PulseLogger.error(LOG, "[Lua] Cannot call - Lua not available");
            return null;
        }

        callCount.incrementAndGet();
        try {
            Method cachedCallMethod = LuaStateManager.getCachedCallMethod();
            if (cachedCallMethod != null) {
                return cachedCallMethod.invoke(null, functionPath, args);
            }
            // Fallback
            Class<?> luaManagerClass = LuaStateManager.getLuaManagerClass();
            if (luaManagerClass == null)
                return null;
            Method callMethod = ReflectionCache.getMethod(
                    luaManagerClass, "call", String.class, Object[].class);
            return callMethod.invoke(null, functionPath, args);
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Call failed: {}", functionPath, e);
            return null;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 전역 변수 접근
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 전역 변수 읽기.
     */
    public Object getGlobal(String name) {
        if (!LuaStateManager.getInstance().isAvailable())
            return null;

        try {
            Method cachedGetGlobalMethod = LuaStateManager.getCachedGetGlobalMethod();
            if (cachedGetGlobalMethod != null) {
                return cachedGetGlobalMethod.invoke(null, name);
            }
            Class<?> luaManagerClass = LuaStateManager.getLuaManagerClass();
            if (luaManagerClass == null)
                return null;
            Method getMethod = ReflectionCache.getMethod(
                    luaManagerClass, "getGlobalObject", String.class);
            return getMethod.invoke(null, name);
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to get global: {}", name);
            return null;
        }
    }

    /**
     * Lua 전역 변수 설정.
     */
    public void setGlobal(String name, Object value) {
        if (!LuaStateManager.getInstance().isAvailable())
            return;

        try {
            Object converted = LuaTypeConverter.javaToLua(value);
            Method cachedSetGlobalMethod = LuaStateManager.getCachedSetGlobalMethod();
            if (cachedSetGlobalMethod != null) {
                cachedSetGlobalMethod.invoke(null, name, converted);
                return;
            }
            Class<?> luaManagerClass = LuaStateManager.getLuaManagerClass();
            if (luaManagerClass == null)
                return;
            Method setMethod = ReflectionCache.getMethod(
                    luaManagerClass, "setGlobalObject", String.class, Object.class);
            setMethod.invoke(null, name, converted);
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to set global: {}", name);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // Lua 코드 실행
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 코드 문자열 직접 실행.
     * 
     * @param luaCode 실행할 Lua 코드 문자열
     * @return 실행 결과 또는 null
     */
    public Object executeLuaCode(String luaCode) {
        if (!LuaStateManager.getInstance().isAvailable()) {
            PulseLogger.error(LOG, "[Lua] Cannot execute - Lua not available");
            return null;
        }

        try {
            Class<?> luaManagerClass = LuaStateManager.getLuaManagerClass();
            if (luaManagerClass == null)
                return null;

            // RunLua 메서드 시도
            Method runMethod = ReflectionCache.getMethodOrNull(luaManagerClass, "RunLua", String.class);
            if (runMethod != null) {
                return runMethod.invoke(null, luaCode);
            }

            // 대안: LuaManager.convertor.load() 시도
            try {
                Field convertorField = ReflectionCache.getField(luaManagerClass, "convertor");
                Object convertor = convertorField.get(null);

                if (convertor != null) {
                    Method loadMethod = ReflectionCache.getMethod(
                            convertor.getClass(), "load", String.class, String.class);
                    return loadMethod.invoke(convertor, luaCode, "Pulse");
                }
            } catch (NoSuchFieldException | NoSuchMethodException ignored) {
            }
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to execute code: {}", e.getMessage(), e);
        }

        return null;
    }

    /**
     * 간단한 print 문 실행.
     */
    public void luaPrint(String message) {
        executeLuaCode("print(\"" + message.replace("\"", "\\\"") + "\")");
    }

    // ─────────────────────────────────────────────────────────────
    // 통계
    // ─────────────────────────────────────────────────────────────

    /**
     * Get the total number of Lua calls made.
     */
    public long getCallCount() {
        return callCount.get();
    }
}
