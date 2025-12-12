package com.pulse.api;

import com.pulse.api.access.*;
import com.pulse.api.util.ReflectionUtil;

/**
 * 게임 내부 접근 API.
 * 리플렉션을 사용하여 게임 코드에 접근.
 * 게임 버전 변경에 유연하게 대응 가능.
 * 
 * <p>
 * <strong>Migration Notice (v1.1.0):</strong>
 * </p>
 * <p>
 * 이 클래스의 메서드들은 다음 클래스들로 분리되었습니다.
 * v1.3.0에서 deprecated 메서드들이 제거될 예정입니다.
 * </p>
 * <ul>
 * <li>{@link WorldAccess} - 월드 관련</li>
 * <li>{@link PlayerAccess} - 플레이어 관련</li>
 * <li>{@link TimeAccess} - 시간 관련</li>
 * <li>{@link NetworkAccess} - 네트워크 상태</li>
 * <li>{@link ZombieAccess} - 좀비 관련</li>
 * <li>{@link ReflectionUtil} - 리플렉션 유틸리티</li>
 * </ul>
 * 
 * @deprecated Use specific Access classes instead.
 */
@Deprecated(since = "1.1.0", forRemoval = true)
public final class GameAccess {

    private GameAccess() {
    }

    /**
     * @deprecated Use specific Access classes' refresh() method.
     */
    @Deprecated(since = "1.1.0", forRemoval = true)
    public static void ensureInitialized() {
        refresh();
    }

    /**
     * @deprecated Use specific Access classes' refresh() method.
     */
    @Deprecated(since = "1.1.0", forRemoval = true)
    public static void refresh() {
        WorldAccess.refresh();
        PlayerAccess.refresh();
        TimeAccess.refresh();
        NetworkAccess.refresh();
        ZombieAccess.refresh();
    }

    // ─────────────────────────────────────────────────────────────
    // WorldAccess
    // ─────────────────────────────────────────────────────────────

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static Object getIsoWorldInstance() {
        return WorldAccess.getIsoWorldInstance();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static boolean isWorldLoaded() {
        return WorldAccess.isWorldLoaded();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static String getWorldName() {
        return WorldAccess.getWorldName();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static int getLoadedCellCount() {
        return WorldAccess.getLoadedCellCount();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static int getTotalEntityCount() {
        return WorldAccess.getTotalEntityCount();
    }

    // ─────────────────────────────────────────────────────────────
    // PlayerAccess
    // ─────────────────────────────────────────────────────────────

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static Object getLocalPlayer() {
        return PlayerAccess.getLocalPlayer();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static boolean isPlayerAlive() {
        return PlayerAccess.isPlayerAlive();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static float getPlayerHealth() {
        return PlayerAccess.getPlayerHealth();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static float getPlayerX() {
        return PlayerAccess.getPlayerX();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static float getPlayerY() {
        return PlayerAccess.getPlayerY();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static float getPlayerZ() {
        return PlayerAccess.getPlayerZ();
    }

    // ─────────────────────────────────────────────────────────────
    // TimeAccess
    // ─────────────────────────────────────────────────────────────

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static Object getGameTimeInstance() {
        return TimeAccess.getGameTimeInstance();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static int getGameHour() {
        return TimeAccess.getGameHour();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static int getGameMinute() {
        return TimeAccess.getGameMinute();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static int getGameDay() {
        return TimeAccess.getGameDay();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static int getGameMonth() {
        return TimeAccess.getGameMonth();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static int getGameYear() {
        return TimeAccess.getGameYear();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static boolean isNight() {
        return TimeAccess.isNight();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static boolean isDay() {
        return TimeAccess.isDay();
    }

    // ─────────────────────────────────────────────────────────────
    // NetworkAccess
    // ─────────────────────────────────────────────────────────────

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static boolean isPaused() {
        return NetworkAccess.isPaused();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static boolean isMultiplayer() {
        return NetworkAccess.isMultiplayer();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static boolean isServer() {
        return NetworkAccess.isServer();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static boolean isClient() {
        return NetworkAccess.isClient();
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static boolean isSinglePlayer() {
        return NetworkAccess.isSinglePlayer();
    }

    // ─────────────────────────────────────────────────────────────
    // ReflectionUtil
    // ─────────────────────────────────────────────────────────────

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static Object getStaticField(String className, String fieldName) {
        return ReflectionUtil.getStaticField(className, fieldName);
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static Object invokeStaticMethod(String className, String methodName, Object... args) {
        return ReflectionUtil.invokeStaticMethod(className, methodName, args);
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static Class<?> getGameClass(String className) {
        return ReflectionUtil.getGameClass(className);
    }

    // ─────────────────────────────────────────────────────────────
    // ZombieAccess
    // ─────────────────────────────────────────────────────────────

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static java.util.List<Object> getNearbyZombies(float x, float y, float radius) {
        return ZombieAccess.getNearbyZombies(x, y, radius);
    }

    @Deprecated(since = "1.1.0", forRemoval = true)
    public static java.util.List<Object> getAllZombies() {
        return ZombieAccess.getAllZombies();
    }
}
