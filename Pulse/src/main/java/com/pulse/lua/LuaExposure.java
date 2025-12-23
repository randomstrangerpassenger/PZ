package com.pulse.lua;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.util.ReflectionCache;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;

/**
 * Java 클래스를 Lua에 노출하고 테이블/콜백을 관리.
 * 
 * <p>
 * v2.0: LuaBridge에서 분리됨
 * </p>
 * 
 * @since Pulse 2.0
 */
public final class LuaExposure {

    private static final String LOG = PulseLogger.PULSE;
    private static final LuaExposure INSTANCE = new LuaExposure();

    // 지연 노출 대기열
    private static final Map<String, Class<?>> pendingExposures = new ConcurrentHashMap<>();

    private LuaExposure() {
    }

    public static LuaExposure getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // Java 클래스 노출
    // ─────────────────────────────────────────────────────────────

    /**
     * Java 클래스를 Lua 전역으로 노출.
     * 정적 메서드들이 Lua에서 호출 가능해짐.
     * 
     * @param globalName Lua에서 사용할 이름
     * @param clazz      노출할 클래스
     */
    public void expose(String globalName, Class<?> clazz) {
        if (!LuaStateManager.getInstance().isAvailable()) {
            pendingExposures.put(globalName, clazz);
            return;
        }
        exposeInternal(globalName, clazz);
    }

    private void exposeInternal(String globalName, Class<?> clazz) {
        try {
            Method cachedExposeMethod = LuaStateManager.getCachedExposeMethod();
            if (cachedExposeMethod != null) {
                cachedExposeMethod.invoke(null, globalName, clazz);
                PulseLogger.info(LOG, "[Lua] Exposed: {} -> {}", globalName, clazz.getSimpleName());
                return;
            }
            Class<?> luaManagerClass = LuaStateManager.getLuaManagerClass();
            if (luaManagerClass == null)
                return;
            Method exposeMethod = ReflectionCache.getMethod(
                    luaManagerClass, "expose", String.class, Class.class);
            exposeMethod.invoke(null, globalName, clazz);
            PulseLogger.info(LOG, "[Lua] Exposed: {} -> {}", globalName, clazz.getSimpleName());
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to expose: {}", globalName, e);
        }
    }

    /**
     * 대기 중인 노출 처리 (초기화 후 호출).
     */
    public void processPendingExposures() {
        if (!LuaStateManager.getInstance().isAvailable())
            return;
        for (var entry : pendingExposures.entrySet()) {
            exposeInternal(entry.getKey(), entry.getValue());
        }
        pendingExposures.clear();
    }

    // ─────────────────────────────────────────────────────────────
    // Lua 테이블 생성/조작
    // ─────────────────────────────────────────────────────────────

    /**
     * 새 Lua 테이블 생성.
     * 
     * @return Lua 테이블 객체 또는 null
     */
    public Object createLuaTable() {
        if (!LuaStateManager.getInstance().isAvailable()) {
            return null;
        }

        try {
            Class<?> kahluaTableClass = ReflectionCache.getClassOrNull(
                    "se.krka.kahlua.vm.KahluaTable", LuaExposure.class.getClassLoader());
            if (kahluaTableClass != null) {
                return kahluaTableClass.getDeclaredConstructor().newInstance();
            }

            Class<?> luaManagerClass = LuaStateManager.getLuaManagerClass();
            if (luaManagerClass != null) {
                Field envField = ReflectionCache.getField(luaManagerClass, "env");
                Object env = envField.get(null);

                if (env != null) {
                    Method newTableMethod = ReflectionCache.getMethod(env.getClass(), "newTable");
                    return newTableMethod.invoke(env);
                }
            }
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to create table: {}", e.getMessage());
        }

        return null;
    }

    /**
     * Lua 테이블에 값 설정.
     */
    public void setTableField(Object table, String key, Object value) {
        if (table == null)
            return;

        try {
            Method rawsetMethod = table.getClass().getMethod("rawset", Object.class, Object.class);
            Object converted = LuaTypeConverter.javaToLua(value);
            rawsetMethod.invoke(table, key, converted);
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to set table field: {}", key);
        }
    }

    /**
     * Lua 테이블에서 값 가져오기.
     */
    public Object getTableField(Object table, String key) {
        if (table == null)
            return null;

        try {
            Method rawgetMethod = table.getClass().getMethod("rawget", Object.class);
            return rawgetMethod.invoke(table, key);
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to get table field: {}", key);
            return null;
        }
    }

    /**
     * Java Map을 Lua 테이블로 변환하여 전역에 설정.
     */
    public void setGlobalTable(String name, Map<String, Object> map) {
        if (!LuaStateManager.getInstance().isAvailable())
            return;

        Object table = createLuaTable();
        if (table == null)
            return;

        for (var entry : map.entrySet()) {
            setTableField(table, entry.getKey(), entry.getValue());
        }

        LuaCallInvoker.getInstance().setGlobal(name, table);
    }

    // ─────────────────────────────────────────────────────────────
    // Java 콜백 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * Java 콜백을 Lua에서 호출 가능하게 등록.
     */
    public void registerCallback(String name, Function<Object[], Object> callback) {
        if (!LuaStateManager.getInstance().isAvailable()) {
            PulseLogger.error(LOG, "[Lua] Cannot register callback - Lua not available");
            return;
        }

        Object wrapper = createCallableWrapper(callback);
        if (wrapper != null) {
            LuaCallInvoker.getInstance().setGlobal(name, wrapper);
            PulseLogger.info(LOG, "[Lua] Registered callback: {}", name);
        }
    }

    private Object createCallableWrapper(Function<Object[], Object> callback) {
        try {
            Class<?> luaCallerClass = ReflectionCache.getClassOrNull(
                    "se.krka.kahlua.vm.LuaCallable", LuaExposure.class.getClassLoader());
            if (luaCallerClass == null) {
                PulseLogger.warn(LOG, "[Lua] LuaCallable class not found");
                return null;
            }

            return java.lang.reflect.Proxy.newProxyInstance(
                    luaCallerClass.getClassLoader(),
                    new Class<?>[] { luaCallerClass },
                    (proxy, method, args) -> {
                        if (method.getName().equals("call")) {
                            Object callFrame = args[0];
                            int argCount = (int) args[1];

                            Object[] luaArgs = new Object[argCount];
                            Method getMethod = ReflectionCache.getMethod(callFrame.getClass(), "get", int.class);
                            for (int i = 0; i < argCount; i++) {
                                luaArgs[i] = getMethod.invoke(callFrame, i);
                            }

                            Object result = callback.apply(luaArgs);

                            if (result != null) {
                                Method pushMethod = ReflectionCache.getMethod(callFrame.getClass(), "push",
                                        Object.class);
                                pushMethod.invoke(callFrame, LuaTypeConverter.javaToLua(result));
                                return 1;
                            }
                            return 0;
                        }
                        return null;
                    });
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to create callable wrapper: {}", e.getMessage());
            return null;
        }
    }
}
