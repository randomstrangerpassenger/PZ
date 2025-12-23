package com.pulse.lua;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.util.ReflectionCache;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * Lua 상태 관리자.
 * Lua 엔진 초기화 및 상태 관리를 담당합니다.
 * 
 * <p>
 * v2.0: LuaBridge에서 분리됨
 * </p>
 * 
 * @since Pulse 2.0
 */
public final class LuaStateManager {

    private static final String LOG = PulseLogger.PULSE;
    private static final LuaStateManager INSTANCE = new LuaStateManager();

    static final String LUA_MANAGER_CLASS = "zombie.Lua.LuaManager";

    private boolean initialized = false;
    private Object luaState; // KahluaThread 또는 LuaState

    // 캐싱된 리플렉션 참조
    private static volatile Class<?> cachedLuaManagerClass;
    private static volatile Method cachedCallMethod;
    private static volatile Method cachedGetGlobalMethod;
    private static volatile Method cachedSetGlobalMethod;
    private static volatile Method cachedExposeMethod;

    private LuaStateManager() {
    }

    public static LuaStateManager getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 초기화
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 브릿지 초기화.
     * PulseAgent에서 게임 시작 시 호출됨.
     */
    public void initialize() {
        if (initialized)
            return;

        try {
            Class<?> luaManagerClass = getLuaManagerClass();
            if (luaManagerClass == null) {
                PulseLogger.warn(LOG, "[Lua] PZ Lua classes not found - running outside game?");
                return;
            }

            Field stateField = ReflectionCache.getField(luaManagerClass, "thread");
            luaState = stateField.get(null);

            if (luaState != null) {
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
    static Class<?> getLuaManagerClass() {
        if (cachedLuaManagerClass == null) {
            synchronized (LuaStateManager.class) {
                if (cachedLuaManagerClass == null) {
                    cachedLuaManagerClass = ReflectionCache.getClassOrNull(
                            LUA_MANAGER_CLASS, LuaStateManager.class.getClassLoader());
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

    // ─────────────────────────────────────────────────────────────
    // 상태 조회
    // ─────────────────────────────────────────────────────────────

    /**
     * 런타임에 Lua 상태가 사용 가능한지 확인.
     */
    public boolean isAvailable() {
        return initialized && luaState != null;
    }

    /**
     * Lua 상태 반환.
     */
    public Object getLuaState() {
        return luaState;
    }

    /**
     * 초기화 여부 반환.
     */
    public boolean isInitialized() {
        return initialized;
    }

    // ─────────────────────────────────────────────────────────────
    // 캐싱된 메서드 접근자
    // ─────────────────────────────────────────────────────────────

    static Method getCachedCallMethod() {
        return cachedCallMethod;
    }

    static Method getCachedGetGlobalMethod() {
        return cachedGetGlobalMethod;
    }

    static Method getCachedSetGlobalMethod() {
        return cachedSetGlobalMethod;
    }

    static Method getCachedExposeMethod() {
        return cachedExposeMethod;
    }

    // ─────────────────────────────────────────────────────────────
    // 재초기화
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 상태 재초기화 (게임 재시작 시 호출).
     */
    public void reinitialize() {
        initialized = false;
        luaState = null;
        cachedLuaManagerClass = null;
        cachedCallMethod = null;
        cachedGetGlobalMethod = null;
        cachedSetGlobalMethod = null;
        cachedExposeMethod = null;
        initialize();
    }
}
