package com.pulse.adapter.lua;

import com.pulse.api.version.GameVersion;

/**
 * Lua 어댑터 제공자.
 * 
 * 현재 게임 버전에 맞는 ILuaAdapter를 반환합니다.
 * 
 * @since Pulse 1.4
 */
public final class LuaAdapterProvider {

    private static volatile ILuaAdapter instance;
    private static final Object LOCK = new Object();

    private LuaAdapterProvider() {
    }

    /**
     * 현재 게임 버전에 맞는 어댑터 반환.
     * 
     * @return ILuaAdapter 구현체
     */
    public static ILuaAdapter get() {
        if (instance == null) {
            synchronized (LOCK) {
                if (instance == null) {
                    instance = createAdapter();
                }
            }
        }
        return instance;
    }

    /**
     * 어댑터 초기화 (테스트용).
     */
    public static void reset() {
        synchronized (LOCK) {
            instance = null;
        }
    }

    /**
     * 어댑터 수동 설정 (테스트용).
     */
    public static void override(ILuaAdapter adapter) {
        synchronized (LOCK) {
            instance = adapter;
            System.out.println("[Pulse/LuaAdapterProvider] Overridden with: " + adapter.getName());
        }
    }

    private static ILuaAdapter createAdapter() {
        int version = GameVersion.get();

        ILuaAdapter adapter;

        if (version >= GameVersion.BUILD_42) {
            Build42LuaAdapter b42 = new Build42LuaAdapter();
            if (b42.isCompatible()) {
                adapter = b42;
                System.out.println("[Pulse/LuaAdapterProvider] Using Build42LuaAdapter");
            } else {
                adapter = new Build41LuaAdapter();
                System.out.println("[Pulse/LuaAdapterProvider] Build 42 not compatible, using Build41LuaAdapter");
            }
        } else {
            adapter = new Build41LuaAdapter();
            System.out.println("[Pulse/LuaAdapterProvider] Using Build41LuaAdapter");
        }

        return adapter;
    }
}
