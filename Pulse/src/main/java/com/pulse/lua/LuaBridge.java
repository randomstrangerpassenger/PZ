package com.pulse.lua;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.util.ReflectionCache;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Map;
import java.util.function.Function;

/**
 * Lua-Java 브릿지 (파사드).
 * 
 * <p>
 * Java에서 Lua 함수를 호출하고 Lua에서 Java를 호출할 수 있도록 함.
 * PZ는 Kahlua2 기반 Lua 엔진을 사용하므로, 이 브릿지는 그에 맞춰 설계됨.
 * </p>
 * 
 * <p>
 * v2.0: 책임 분리됨
 * </p>
 * <ul>
 * <li>{@link LuaStateManager} - 초기화 및 상태 관리</li>
 * <li>{@link LuaCallInvoker} - Lua 함수 호출 및 코드 실행</li>
 * <li>{@link LuaExposure} - Java 클래스 노출 및 테이블 관리</li>
 * </ul>
 * 
 * <h2>사용 예</h2>
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
 * 
 * @since Pulse 1.0
 * @since Pulse 2.0 - 책임 분리 (LuaStateManager, LuaCallInvoker, LuaExposure)
 */
public class LuaBridge {

    private static final String LOG = PulseLogger.PULSE;
    private static final LuaBridge INSTANCE = new LuaBridge();

    private LuaBridge() {
    }

    public static LuaBridge getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 초기화 (위임: LuaStateManager)
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 브릿지 초기화.
     */
    public static void initialize() {
        LuaStateManager.getInstance().initialize();
    }

    /**
     * 런타임에 Lua 상태가 사용 가능한지 확인.
     */
    public static boolean isAvailable() {
        return LuaStateManager.getInstance().isAvailable();
    }

    /**
     * Lua 상태 재초기화.
     */
    public static void reinitialize() {
        LuaStateManager.getInstance().reinitialize();
    }

    // ─────────────────────────────────────────────────────────────
    // Lua 함수 호출 (위임: LuaCallInvoker)
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 함수 호출.
     */
    public static Object call(String functionPath, Object... args) {
        return LuaCallInvoker.getInstance().call(functionPath, args);
    }

    /**
     * Lua 전역 변수 읽기.
     */
    public static Object getGlobal(String name) {
        return LuaCallInvoker.getInstance().getGlobal(name);
    }

    /**
     * Lua 전역 변수 설정.
     */
    public static void setGlobal(String name, Object value) {
        LuaCallInvoker.getInstance().setGlobal(name, value);
    }

    /**
     * Lua 코드 문자열 직접 실행.
     */
    public static Object executeLuaCode(String luaCode) {
        return LuaCallInvoker.getInstance().executeLuaCode(luaCode);
    }

    /**
     * 간단한 print 문 실행.
     */
    public static void luaPrint(String message) {
        LuaCallInvoker.getInstance().luaPrint(message);
    }

    /**
     * Get the total number of Lua calls made.
     */
    public static long getCallCount() {
        return LuaCallInvoker.getInstance().getCallCount();
    }

    // ─────────────────────────────────────────────────────────────
    // Java 클래스 노출 (위임: LuaExposure)
    // ─────────────────────────────────────────────────────────────

    /**
     * Java 클래스를 Lua 전역으로 노출.
     */
    public static void expose(String globalName, Class<?> clazz) {
        LuaExposure.getInstance().expose(globalName, clazz);
    }

    /**
     * 대기 중인 노출 처리.
     */
    public static void processPendingExposures() {
        LuaExposure.getInstance().processPendingExposures();
    }

    /**
     * 새 Lua 테이블 생성.
     */
    public static Object createLuaTable() {
        return LuaExposure.getInstance().createLuaTable();
    }

    /**
     * Lua 테이블에 값 설정.
     */
    public static void setTableField(Object table, String key, Object value) {
        LuaExposure.getInstance().setTableField(table, key, value);
    }

    /**
     * Lua 테이블에서 값 가져오기.
     */
    public static Object getTableField(Object table, String key) {
        return LuaExposure.getInstance().getTableField(table, key);
    }

    /**
     * Java Map을 Lua 테이블로 변환하여 전역에 설정.
     */
    public static void setGlobalTable(String name, Map<String, Object> map) {
        LuaExposure.getInstance().setGlobalTable(name, map);
    }

    /**
     * Java 콜백을 Lua에서 호출 가능하게 등록.
     */
    public static void registerCallback(String name, Function<Object[], Object> callback) {
        LuaExposure.getInstance().registerCallback(name, callback);
    }

    // ─────────────────────────────────────────────────────────────
    // 디버그 유틸리티
    // ─────────────────────────────────────────────────────────────

    /**
     * 디버그: Lua 전역 변수 덤프.
     */
    public static void dumpGlobals() {
        if (!isAvailable())
            return;

        try {
            Class<?> luaManagerClass = LuaStateManager.getLuaManagerClass();
            if (luaManagerClass == null)
                return;

            Field envField = ReflectionCache.getField(luaManagerClass, "env");
            Object env = envField.get(null);

            PulseLogger.info(LOG, "[Lua] === Global Variables ===");
            if (env != null) {
                PulseLogger.info(LOG, "[Lua] Env type: {}", env.getClass().getName());

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
