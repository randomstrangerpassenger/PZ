package com.pulse.api.access;

import com.pulse.api.GameAccess;
import com.pulse.api.util.ReflectionClassCache;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * 플레이어 관련 접근 API.
 * GameAccess에서 분리된 플레이어 전용 유틸리티.
 * 
 * @since 1.1.0
 * @see GameAccess
 */
public final class PlayerAccess {

    private PlayerAccess() {
    }

    // ReflectionClassCache 사용으로 ensureInitialized() 패턴 제거
    private static final ReflectionClassCache<Object> isoPlayerCache = new ReflectionClassCache<>(
            "zombie.characters.IsoPlayer");

    /**
     * 클래스 참조 갱신.
     */
    public static void refresh() {
        isoPlayerCache.refresh();
    }

    /**
     * 로컬 플레이어 가져오기.
     */
    public static Object getLocalPlayer() {
        Class<?> isoPlayerClass = isoPlayerCache.get();
        if (isoPlayerClass == null)
            return null;

        try {
            Method getInstance = isoPlayerClass.getMethod("getInstance");
            return getInstance.invoke(null);
        } catch (Exception e) {
            try {
                Field playersField = isoPlayerClass.getDeclaredField("players");
                playersField.setAccessible(true);
                Object players = playersField.get(null);
                if (players instanceof java.util.List<?> list && !list.isEmpty()) {
                    return list.get(0);
                }
            } catch (Exception e2) {
                // 무시
            }
            return null;
        }
    }

    /**
     * 플레이어가 살아있는지 확인.
     */
    public static boolean isPlayerAlive() {
        Object player = getLocalPlayer();
        if (player == null)
            return false;

        try {
            Method isDead = player.getClass().getMethod("isDead");
            Object result = isDead.invoke(player);
            return result instanceof Boolean b && !b;
        } catch (Exception e) {
            return true;
        }
    }

    /**
     * 플레이어 체력 가져오기.
     */
    public static float getPlayerHealth() {
        Object player = getLocalPlayer();
        if (player == null)
            return 0;

        try {
            Method getHealth = player.getClass().getMethod("getHealth");
            Object result = getHealth.invoke(player);
            if (result instanceof Number num) {
                return num.floatValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 0;
    }

    /**
     * 플레이어 위치 X.
     */
    public static float getPlayerX() {
        Object player = getLocalPlayer();
        if (player == null)
            return 0;

        try {
            Method getX = player.getClass().getMethod("getX");
            Object result = getX.invoke(player);
            if (result instanceof Number num) {
                return num.floatValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 0;
    }

    /**
     * 플레이어 위치 Y.
     */
    public static float getPlayerY() {
        Object player = getLocalPlayer();
        if (player == null)
            return 0;

        try {
            Method getY = player.getClass().getMethod("getY");
            Object result = getY.invoke(player);
            if (result instanceof Number num) {
                return num.floatValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 0;
    }

    /**
     * 플레이어 위치 Z (층).
     */
    public static float getPlayerZ() {
        Object player = getLocalPlayer();
        if (player == null)
            return 0;

        try {
            Method getZ = player.getClass().getMethod("getZ");
            Object result = getZ.invoke(player);
            if (result instanceof Number num) {
                return num.floatValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 0;
    }
}
