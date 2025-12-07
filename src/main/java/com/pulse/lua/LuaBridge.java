package com.pulse.lua;

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

    private static final LuaBridge INSTANCE = new LuaBridge();

    private boolean initialized = false;
    private Object luaState; // KahluaThread 또는 LuaState

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

    private void init() {
        if (initialized)
            return;

        try {
            // PZ의 Lua 상태 가져오기 시도
            // zombie.Lua.LuaManager에 접근
            Class<?> luaManagerClass = Class.forName("zombie.Lua.LuaManager");
            java.lang.reflect.Field stateField = luaManagerClass.getDeclaredField("thread");
            stateField.setAccessible(true);
            luaState = stateField.get(null);

            if (luaState != null) {
                System.out.println("[Pulse/Lua] Lua state acquired successfully");
                initialized = true;
            } else {
                System.out.println("[Pulse/Lua] Lua state is null - game not fully loaded yet");
            }
        } catch (ClassNotFoundException e) {
            System.out.println("[Pulse/Lua] PZ Lua classes not found - running outside game?");
        } catch (Exception e) {
            System.err.println("[Pulse/Lua] Failed to initialize: " + e.getMessage());
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
            System.err.println("[Pulse/Lua] Cannot call - Lua not available");
            return null;
        }
        return INSTANCE.callInternal(functionPath, args);
    }

    private Object callInternal(String functionPath, Object... args) {
        try {
            // zombie.Lua.LuaManager.call 사용
            Class<?> luaManagerClass = Class.forName("zombie.Lua.LuaManager");
            java.lang.reflect.Method callMethod = luaManagerClass.getMethod(
                    "call", String.class, Object[].class);

            return callMethod.invoke(null, functionPath, args);
        } catch (Exception e) {
            System.err.println("[Pulse/Lua] Call failed: " + functionPath);
            e.printStackTrace();
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
            Class<?> luaManagerClass = Class.forName("zombie.Lua.LuaManager");
            java.lang.reflect.Method getMethod = luaManagerClass.getMethod(
                    "getGlobalObject", String.class);

            return getMethod.invoke(null, name);
        } catch (Exception e) {
            System.err.println("[Pulse/Lua] Failed to get global: " + name);
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

            Class<?> luaManagerClass = Class.forName("zombie.Lua.LuaManager");
            java.lang.reflect.Method setMethod = luaManagerClass.getMethod(
                    "setGlobalObject", String.class, Object.class);

            setMethod.invoke(null, name, converted);
        } catch (Exception e) {
            System.err.println("[Pulse/Lua] Failed to set global: " + name);
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
            Class<?> luaManagerClass = Class.forName("zombie.Lua.LuaManager");
            java.lang.reflect.Method exposeMethod = luaManagerClass.getMethod(
                    "expose", String.class, Class.class);

            exposeMethod.invoke(null, globalName, clazz);
            System.out.println("[Pulse/Lua] Exposed: " + globalName + " -> " + clazz.getSimpleName());
        } catch (Exception e) {
            System.err.println("[Pulse/Lua] Failed to expose: " + globalName);
            e.printStackTrace();
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
}
