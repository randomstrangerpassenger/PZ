package com.pulse.adapter.lua;

import com.pulse.api.version.GameVersion;
import com.pulse.internal.InternalLuaHook;

/**
 * Build 41 전용 Lua 시스템 어댑터.
 * 
 * Build 41의 LuaEventManager, LuaManager 클래스 구조를 기반으로 구현.
 * 
 * Build 41 Lua 특징:
 * - zombie.Lua.LuaEventManager.triggerEvent() (0~8 인자 오버로드)
 * - zombie.Lua.LuaManager.GlobalLua (글로벌 환경)
 * 
 * @since Pulse 1.4
 */
public class Build41LuaAdapter implements ILuaAdapter {

    private static final String EVENT_MANAGER_CLASS = "zombie.Lua.LuaEventManager";
    private static final String LUA_MANAGER_CLASS = "zombie.Lua.LuaManager";
    private static final int MAX_TRIGGER_EVENT_ARGS = 8;

    // 캐시된 클래스
    private Class<?> luaManagerClass;
    private Object globalLuaEnv;
    private boolean initialized = false;

    // ═══════════════════════════════════════════════════════════════
    // IVersionAdapter Implementation
    // ═══════════════════════════════════════════════════════════════

    @Override
    public int getSupportedBuild() {
        return GameVersion.BUILD_41;
    }

    @Override
    public boolean isCompatible() {
        try {
            Class.forName(EVENT_MANAGER_CLASS);
            return true;
        } catch (ClassNotFoundException e) {
            return false;
        }
    }

    @Override
    public String getName() {
        return "Build41LuaAdapter";
    }

    // ═══════════════════════════════════════════════════════════════
    // ILuaAdapter Implementation
    // ═══════════════════════════════════════════════════════════════

    @Override
    public String getEventManagerClassName() {
        return EVENT_MANAGER_CLASS;
    }

    @Override
    public String getLuaManagerClassName() {
        return LUA_MANAGER_CLASS;
    }

    @Override
    public int getMaxTriggerEventArgs() {
        return MAX_TRIGGER_EVENT_ARGS;
    }

    @Override
    public void onEventStart(String eventName) {
        // InternalLuaHook에 위임 (기존 로직 유지)
        InternalLuaHook.fireEventStart(eventName);
    }

    @Override
    public void onEventEnd() {
        // InternalLuaHook에 위임 (기존 로직 유지)
        InternalLuaHook.fireEventEnd();
    }

    @Override
    public boolean hasGlobalLuaAccess() {
        ensureInitialized();
        return globalLuaEnv != null;
    }

    @Override
    public Object getGlobalLuaValue(String name) {
        try {
            ensureInitialized();
            if (globalLuaEnv == null)
                return null;

            // LuaManager.GlobalLua.rawget(name) 호출
            java.lang.reflect.Method rawgetMethod = globalLuaEnv.getClass().getMethod("rawget", Object.class);
            return rawgetMethod.invoke(globalLuaEnv, name);
        } catch (Throwable t) {
            return null;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Internal Helpers
    // ═══════════════════════════════════════════════════════════════

    private void ensureInitialized() {
        if (initialized)
            return;

        try {
            luaManagerClass = Class.forName(LUA_MANAGER_CLASS);

            // GlobalLua 필드 접근
            java.lang.reflect.Field globalField = luaManagerClass.getField("GlobalLua");
            globalLuaEnv = globalField.get(null);

            initialized = true;
        } catch (Throwable t) {
            System.err.println("[Pulse/Build41LuaAdapter] Init failed: " + t.getMessage());
            initialized = true; // 재시도 방지
        }
    }
}
