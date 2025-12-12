package com.pulse.api.access;

import com.pulse.PulseEnvironment;
import com.pulse.api.GameAccess;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * 네트워크 관련 접근 API.
 * GameAccess에서 분리된 네트워크/게임 상태 전용 유틸리티.
 * 
 * @since 1.1.0
 * @see GameAccess
 */
public final class NetworkAccess {

    private NetworkAccess() {
    }

    // 캐시된 클래스 참조
    private static Class<?> gameClientClass;
    private static Class<?> gameServerClass;
    private static Class<?> coreClass;
    private static boolean initialized = false;

    private static void ensureInitialized() {
        if (initialized)
            return;
        ClassLoader gameLoader = PulseEnvironment.getGameClassLoader();
        if (gameLoader == null)
            gameLoader = ClassLoader.getSystemClassLoader();
        try {
            gameClientClass = gameLoader.loadClass("zombie.network.GameClient");
        } catch (ClassNotFoundException e) {
            // 무시
        }
        try {
            gameServerClass = gameLoader.loadClass("zombie.network.GameServer");
        } catch (ClassNotFoundException e) {
            // 무시
        }
        try {
            coreClass = gameLoader.loadClass("zombie.core.Core");
        } catch (ClassNotFoundException e) {
            // 무시
        }
        initialized = true;
    }

    /**
     * 클래스 참조 갱신.
     */
    public static void refresh() {
        initialized = false;
        ensureInitialized();
    }

    /**
     * 게임 일시정지 상태인지 확인.
     */
    public static boolean isPaused() {
        ensureInitialized();

        if (coreClass != null) {
            try {
                Method getInstance = coreClass.getMethod("getInstance");
                Object core = getInstance.invoke(null);
                if (core != null) {
                    Method isGamePaused = coreClass.getMethod("isGamePaused");
                    Object result = isGamePaused.invoke(core);
                    if (result instanceof Boolean b) {
                        return b;
                    }
                }
            } catch (Exception e) {
                // 무시
            }
        }

        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();
            Class<?> uiManagerClass = loader.loadClass("zombie.ui.UIManager");
            Field suspendField = uiManagerClass.getDeclaredField("bSuspend");
            suspendField.setAccessible(true);
            Object result = suspendField.get(null);
            if (result instanceof Boolean b) {
                return b;
            }
        } catch (Exception e) {
            // 무시
        }

        return false;
    }

    /**
     * 멀티플레이어인지 확인.
     */
    public static boolean isMultiplayer() {
        ensureInitialized();

        if (gameClientClass != null) {
            try {
                Field bClientField = gameClientClass.getDeclaredField("bClient");
                bClientField.setAccessible(true);
                Object result = bClientField.get(null);
                if (result instanceof Boolean b && b) {
                    return true;
                }
            } catch (Exception e) {
                // 무시
            }
        }

        if (gameServerClass != null) {
            try {
                Field bServerField = gameServerClass.getDeclaredField("bServer");
                bServerField.setAccessible(true);
                Object result = bServerField.get(null);
                if (result instanceof Boolean b && b) {
                    return true;
                }
            } catch (Exception e) {
                // 무시
            }
        }

        return false;
    }

    /**
     * 서버인지 확인 (멀티플레이어).
     */
    public static boolean isServer() {
        ensureInitialized();

        if (gameServerClass != null) {
            try {
                Field bServerField = gameServerClass.getDeclaredField("bServer");
                bServerField.setAccessible(true);
                Object result = bServerField.get(null);
                if (result instanceof Boolean b) {
                    return b;
                }
            } catch (Exception e) {
                // 무시
            }
        }

        return false;
    }

    /**
     * 클라이언트인지 확인 (멀티플레이어).
     */
    public static boolean isClient() {
        ensureInitialized();

        if (gameClientClass != null) {
            try {
                Field bClientField = gameClientClass.getDeclaredField("bClient");
                bClientField.setAccessible(true);
                Object result = bClientField.get(null);
                if (result instanceof Boolean b) {
                    return b;
                }
            } catch (Exception e) {
                // 무시
            }
        }

        return false;
    }

    /**
     * 싱글플레이어인지 확인.
     */
    public static boolean isSinglePlayer() {
        return !isMultiplayer();
    }
}
