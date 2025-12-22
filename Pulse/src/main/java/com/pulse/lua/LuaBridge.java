package com.pulse.lua;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.util.ReflectionCache;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * Lua-Java 브릿지.
 * Java에서 Lua 함수를 호출하고 Lua에서 Java를 호출할 수 있도록 함.
 * 
 * PZ는 Kahlua2 기반 Lua 엔진을 사용하므로, 이 브릿지는 그에 맞춰 설계됨.
 * 
 * 사용 예:
 * 
 * <pre>
 * // Lua 함수 호출
 * LuaBridge.call("Events.OnTick.Add", myJavaCallback);
 * 
 * // Lua 전역 변수 접근
 * Object value = LuaBridge.getGlobal("SomeGlobalVar");
 * 
 * // Java 메서드를 Lua에 노출
 * LuaBridge.expose("MyMod", MyModAPI.class);
 * </pre>
 */
public class LuaBridge {

    private static final String LOG = PulseLogger.PULSE;
    private static final LuaBridge INSTANCE = new LuaBridge();

    private boolean initialized = false;
    private Object luaState; // KahluaThread 또는 LuaState
    private static final java.util.concurrent.atomic.AtomicLong callCount = new java.util.concurrent.atomic.AtomicLong(
            0);

    private LuaBridge() {
    }

    public static LuaBridge getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 초기화
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 브릿지 초기화.
     * PulseAgent에서 게임 시작 시 호출됨.
     */
    public static void initialize() {
        INSTANCE.init();
    }

    // 캐싱된 리플렉션 참조 (Phase 1 성능 최적화)
    private static final String LUA_MANAGER_CLASS = "zombie.Lua.LuaManager";
    private static volatile Class<?> cachedLuaManagerClass;
    private static volatile Method cachedCallMethod;
    private static volatile Method cachedGetGlobalMethod;
    private static volatile Method cachedSetGlobalMethod;
    private static volatile Method cachedExposeMethod;

    private void init() {
        if (initialized)
            return;

        try {
            // PZ의 Lua 상태 가져오기 시도 (ReflectionCache 사용)
            Class<?> luaManagerClass = getLuaManagerClass();
            if (luaManagerClass == null) {
                PulseLogger.warn(LOG, "[Lua] PZ Lua classes not found - running outside game?");
                return;
            }

            Field stateField = ReflectionCache.getField(luaManagerClass, "thread");
            luaState = stateField.get(null);

            if (luaState != null) {
                // 초기화 시 자주 사용하는 메서드들 캐싱
                initMethodCache(luaManagerClass);
                PulseLogger.info(LOG, "[Lua] Lua state acquired successfully (cached)");
                initialized = true;
            } else {
                PulseLogger.warn(LOG, "[Lua] Lua state is null - game not fully loaded yet");
            }
        } catch (NoSuchFieldException e) {
            PulseLogger.warn(LOG, "[Lua] LuaManager.thread field not found");
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to initialize: {}", e.getMessage());
        }
    }

    /**
     * LuaManager 클래스 캐싱된 조회
     */
    private static Class<?> getLuaManagerClass() {
        if (cachedLuaManagerClass == null) {
            synchronized (LuaBridge.class) {
                if (cachedLuaManagerClass == null) {
                    cachedLuaManagerClass = ReflectionCache.getClassOrNull(
                            LUA_MANAGER_CLASS, LuaBridge.class.getClassLoader());
                }
            }
        }
        return cachedLuaManagerClass;
    }

    /**
     * 자주 호출되는 메서드들 초기화 시 캐싱
     */
    private void initMethodCache(Class<?> luaManagerClass) {
        try {
            cachedCallMethod = ReflectionCache.getMethodOrNull(
                    luaManagerClass, "call", String.class, Object[].class);
            cachedGetGlobalMethod = ReflectionCache.getMethodOrNull(
                    luaManagerClass, "getGlobalObject", String.class);
            cachedSetGlobalMethod = ReflectionCache.getMethodOrNull(
                    luaManagerClass, "setGlobalObject", String.class, Object.class);
            cachedExposeMethod = ReflectionCache.getMethodOrNull(
                    luaManagerClass, "expose", String.class, Class.class);
        } catch (Exception e) {
            PulseLogger.warn(LOG, "[Lua] Some methods not cached: {}", e.getMessage());
        }
    }

    /**
     * 런타임에 Lua 상태가 사용 가능한지 확인.
     */
    public static boolean isAvailable() {
        return INSTANCE.initialized && INSTANCE.luaState != null;
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
    public static Object call(String functionPath, Object... args) {
        if (!isAvailable()) {
            PulseLogger.error(LOG, "[Lua] Cannot call - Lua not available");
            return null;
        }
        return INSTANCE.callInternal(functionPath, args);
    }

    private Object callInternal(String functionPath, Object... args) {
        callCount.incrementAndGet();
        try {
            // 캐싱된 메서드 사용 (Phase 1 성능 최적화)
            if (cachedCallMethod != null) {
                return cachedCallMethod.invoke(null, functionPath, args);
            }
            // Fallback: 캐시 미스 시 ReflectionCache 사용
            Class<?> luaManagerClass = getLuaManagerClass();
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
    public static Object getGlobal(String name) {
        if (!isAvailable())
            return null;
        return INSTANCE.getGlobalInternal(name);
    }

    private Object getGlobalInternal(String name) {
        try {
            // 캐싱된 메서드 사용 (Phase 1 성능 최적화)
            if (cachedGetGlobalMethod != null) {
                return cachedGetGlobalMethod.invoke(null, name);
            }
            // Fallback
            Class<?> luaManagerClass = getLuaManagerClass();
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
    public static void setGlobal(String name, Object value) {
        if (!isAvailable())
            return;
        INSTANCE.setGlobalInternal(name, value);
    }

    private void setGlobalInternal(String name, Object value) {
        try {
            Object converted = LuaTypeConverter.javaToLua(value);
            // 캐싱된 메서드 사용 (Phase 1 성능 최적화)
            if (cachedSetGlobalMethod != null) {
                cachedSetGlobalMethod.invoke(null, name, converted);
                return;
            }
            // Fallback
            Class<?> luaManagerClass = getLuaManagerClass();
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
    // Java 클래스 노출
    // ─────────────────────────────────────────────────────────────

    /**
     * Java 클래스를 Lua 전역으로 노출.
     * 정적 메서드들이 Lua에서 호출 가능해짐.
     * 
     * @param globalName Lua에서 사용할 이름
     * @param clazz      노출할 클래스
     */
    public static void expose(String globalName, Class<?> clazz) {
        if (!isAvailable()) {
            // 나중에 초기화되면 노출하도록 예약
            PendingExposures.add(globalName, clazz);
            return;
        }
        INSTANCE.exposeInternal(globalName, clazz);
    }

    private void exposeInternal(String globalName, Class<?> clazz) {
        try {
            // 캐싱된 메서드 사용 (Phase 1 성능 최적화)
            if (cachedExposeMethod != null) {
                cachedExposeMethod.invoke(null, globalName, clazz);
                PulseLogger.info(LOG, "[Lua] Exposed: {} -> {}", globalName, clazz.getSimpleName());
                return;
            }
            // Fallback
            Class<?> luaManagerClass = getLuaManagerClass();
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
    public static void processPendingExposures() {
        if (!isAvailable())
            return;
        PendingExposures.processAll();
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스: 지연 노출 관리
    // ─────────────────────────────────────────────────────────────

    private static class PendingExposures {
        private static final java.util.Map<String, Class<?>> pending = new java.util.concurrent.ConcurrentHashMap<>();

        static void add(String name, Class<?> clazz) {
            pending.put(name, clazz);
        }

        static void processAll() {
            for (var entry : pending.entrySet()) {
                INSTANCE.exposeInternal(entry.getKey(), entry.getValue());
            }
            pending.clear();
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
    public static Object executeLuaCode(String luaCode) {
        if (!isAvailable()) {
            PulseLogger.error(LOG, "[Lua] Cannot execute - Lua not available");
            return null;
        }

        try {
            // ReflectionCache 사용 (Phase 1 성능 최적화)
            Class<?> luaManagerClass = getLuaManagerClass();
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
                // convertor 방식 실패
            }
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to execute code: {}", e.getMessage(), e);
        }

        return null;
    }

    /**
     * 간단한 print 문 실행.
     */
    public static void luaPrint(String message) {
        executeLuaCode("print(\"" + message.replace("\"", "\\\"") + "\")");
    }

    // ─────────────────────────────────────────────────────────────
    // Lua 테이블 생성/조작
    // ─────────────────────────────────────────────────────────────

    /**
     * 새 Lua 테이블 생성.
     * 
     * @return Lua 테이블 객체 또는 null
     */
    public static Object createLuaTable() {
        if (!isAvailable()) {
            return null;
        }

        try {
            // ReflectionCache 사용 (Phase 1 성능 최적화)
            Class<?> kahluaTableClass = ReflectionCache.getClassOrNull(
                    "se.krka.kahlua.vm.KahluaTable", LuaBridge.class.getClassLoader());
            if (kahluaTableClass != null) {
                return kahluaTableClass.getDeclaredConstructor().newInstance();
            }

            // 대안: LuaManager를 통한 테이블 생성
            Class<?> luaManagerClass = getLuaManagerClass();
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
     * 
     * @param table Lua 테이블 객체
     * @param key   키
     * @param value 값
     */
    public static void setTableField(Object table, String key, Object value) {
        if (table == null)
            return;

        try {
            java.lang.reflect.Method rawsetMethod = table.getClass().getMethod("rawset", Object.class, Object.class);
            Object converted = LuaTypeConverter.javaToLua(value);
            rawsetMethod.invoke(table, key, converted);
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to set table field: {}", key);
        }
    }

    /**
     * Lua 테이블에서 값 가져오기.
     */
    public static Object getTableField(Object table, String key) {
        if (table == null)
            return null;

        try {
            java.lang.reflect.Method rawgetMethod = table.getClass().getMethod("rawget", Object.class);
            return rawgetMethod.invoke(table, key);
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to get table field: {}", key);
            return null;
        }
    }

    /**
     * Java Map을 Lua 테이블로 변환하여 전역에 설정.
     * 
     * @param name 전역 변수 이름
     * @param map  변환할 Map
     */
    public static void setGlobalTable(String name, java.util.Map<String, Object> map) {
        if (!isAvailable())
            return;

        Object table = createLuaTable();
        if (table == null)
            return;

        for (var entry : map.entrySet()) {
            setTableField(table, entry.getKey(), entry.getValue());
        }

        setGlobal(name, table);
    }

    // ─────────────────────────────────────────────────────────────
    // Java 콜백 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * Java 콜백을 Lua에서 호출 가능하게 등록.
     * 
     * @param name     Lua에서 호출할 이름
     * @param callback 콜백 함수
     */
    public static void registerCallback(String name, java.util.function.Function<Object[], Object> callback) {
        if (!isAvailable()) {
            PulseLogger.error(LOG, "[Lua] Cannot register callback - Lua not available");
            return;
        }

        // LuaCallable 래퍼 생성
        Object wrapper = createCallableWrapper(callback);
        if (wrapper != null) {
            setGlobal(name, wrapper);
            PulseLogger.info(LOG, "[Lua] Registered callback: {}", name);
        }
    }

    /**
     * Java 함수를 Lua에서 호출 가능한 객체로 래핑.
     */
    private static Object createCallableWrapper(java.util.function.Function<Object[], Object> callback) {
        try {
            // ReflectionCache 사용 (Phase 1 성능 최적화)
            Class<?> luaCallerClass = ReflectionCache.getClassOrNull(
                    "se.krka.kahlua.vm.LuaCallable", LuaBridge.class.getClassLoader());
            if (luaCallerClass == null) {
                PulseLogger.warn(LOG, "[Lua] LuaCallable class not found");
                return null;
            }

            return java.lang.reflect.Proxy.newProxyInstance(
                    luaCallerClass.getClassLoader(),
                    new Class<?>[] { luaCallerClass },
                    (proxy, method, args) -> {
                        if (method.getName().equals("call")) {
                            // args[0] = LuaCallFrame, args[1] = int argCount
                            Object callFrame = args[0];
                            int argCount = (int) args[1];

                            // 인자 추출 (ReflectionCache 사용)
                            Object[] luaArgs = new Object[argCount];
                            Method getMethod = ReflectionCache.getMethod(callFrame.getClass(), "get", int.class);
                            for (int i = 0; i < argCount; i++) {
                                luaArgs[i] = getMethod.invoke(callFrame, i);
                            }

                            // Java 콜백 호출
                            Object result = callback.apply(luaArgs);

                            // 결과 반환
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

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 상태 재초기화 (게임 재시작 시 호출).
     */
    public static void reinitialize() {
        INSTANCE.initialized = false;
        INSTANCE.luaState = null;
        initialize();
    }

    /**
     * Get the total number of Lua calls made.
     */
    public static long getCallCount() {
        return callCount.get();
    }

    /**
     * 디버그: Lua 전역 변수 덤프.
     */
    public static void dumpGlobals() {
        if (!isAvailable())
            return;

        try {
            // ReflectionCache 사용 (Phase 1 성능 최적화)
            Class<?> luaManagerClass = getLuaManagerClass();
            if (luaManagerClass == null)
                return;

            Field envField = ReflectionCache.getField(luaManagerClass, "env");
            Object env = envField.get(null);

            PulseLogger.info(LOG, "[Lua] === Global Variables ===");
            if (env != null) {
                PulseLogger.info(LOG, "[Lua] Env type: {}", env.getClass().getName());

                // keys() 메서드로 전역 변수 이름 가져오기
                Method keysMethod = ReflectionCache.getMethodOrNull(env.getClass(), "keys");
                if (keysMethod != null) {
                    Object keys = keysMethod.invoke(env);

                    if (keys instanceof Iterable<?> iterable) {
                        int count = 0;
                        for (Object key : iterable) {
                            PulseLogger.info(LOG, "[Lua]   - {}", key);
                            count++;
                            if (count >= 50) {
                                PulseLogger.info(LOG, "[Lua]   ... (truncated, {}+ items)", count);
                                break;
                            }
                        }
                    } else if (keys != null) {
                        PulseLogger.info(LOG, "[Lua] Keys type: {}", keys.getClass().getName());
                    }
                } else {
                    PulseLogger.info(LOG, "[Lua] (keys() method not available)");
                }
            } else {
                PulseLogger.info(LOG, "[Lua] (env is null)");
            }
            PulseLogger.info(LOG, "[Lua] ========================");
        } catch (Exception e) {
            PulseLogger.error(LOG, "[Lua] Failed to dump globals: {}", e.getMessage());
        }
    }
}
