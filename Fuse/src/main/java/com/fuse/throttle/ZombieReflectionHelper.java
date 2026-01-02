package com.fuse.throttle;

import com.pulse.api.log.PulseLogger;
import java.lang.reflect.Method;

/**
 * 좀비 객체 정보 접근 헬퍼.
 * 
 * Fuse가 Pulse 코어에 의존하지 않고 좀비 정보에 접근할 수 있도록
 * 리플렉션 기반으로 구현.
 * 
 * @since Fuse 2.2.0
 */
final class ZombieReflectionHelper {

    private static final String LOG = "Fuse";

    // Cached reflection methods
    private static Method getX;
    private static Method getY;
    private static Method isAttacking;
    private static Method getTarget;
    private static boolean initialized = false;
    private static boolean available = false;

    private ZombieReflectionHelper() {
    }

    /**
     * 리플렉션 메서드 초기화.
     */
    private static synchronized void init(Object zombie) {
        if (initialized)
            return;
        initialized = true;

        try {
            Class<?> clazz = zombie.getClass();
            PulseLogger.debug(LOG, "[DEBUG] ZombieReflectionHelper.init: class=" + clazz.getName());

            getX = clazz.getMethod("getX");
            getY = clazz.getMethod("getY");

            // isAttacking은 IsoZombie에 있을 수 있음
            try {
                isAttacking = clazz.getMethod("isAttacking");
            } catch (NoSuchMethodException e) {
                isAttacking = null;
                PulseLogger.debug(LOG, "[DEBUG] isAttacking method NOT FOUND");
            }

            // getTarget은 IsoGameCharacter에 있음
            try {
                getTarget = clazz.getMethod("getTarget");
            } catch (NoSuchMethodException e) {
                getTarget = null;
                PulseLogger.debug(LOG, "[DEBUG] getTarget method NOT FOUND");
            }

            available = true;
            PulseLogger.info(LOG, "ZombieReflectionHelper initialized: getX=" + (getX != null)
                    + ", getY=" + (getY != null)
                    + ", isAttacking=" + (isAttacking != null)
                    + ", getTarget=" + (getTarget != null));
        } catch (Throwable t) {
            available = false;
            PulseLogger.warn(LOG,
                    "ZombieReflectionHelper init FAILED: " + t.getClass().getSimpleName() + " - " + t.getMessage());
        }
    }

    /**
     * 좀비와 가장 가까운 플레이어 사이의 거리 제곱 반환.
     * 
     * 간단한 구현: 첫 번째 플레이어까지의 거리만 계산
     * (실제로는 모든 플레이어를 순회해야 하지만, 성능상 간소화)
     */
    public static float getDistanceSquaredToPlayer(Object zombie) {
        if (zombie == null)
            return Float.MAX_VALUE;

        if (!initialized)
            init(zombie);
        if (!available)
            return Float.MAX_VALUE;

        try {
            float zx = ((Number) getX.invoke(zombie)).floatValue();
            float zy = ((Number) getY.invoke(zombie)).floatValue();

            // 플레이어 위치 가져오기 (IsoPlayer.getInstance())
            Class<?> isoPlayerClass = Class.forName("zombie.characters.IsoPlayer");
            Method getInstance = isoPlayerClass.getMethod("getInstance");
            Object player = getInstance.invoke(null);

            if (player == null)
                return Float.MAX_VALUE;

            Method playerGetX = player.getClass().getMethod("getX");
            Method playerGetY = player.getClass().getMethod("getY");

            float px = ((Number) playerGetX.invoke(player)).floatValue();
            float py = ((Number) playerGetY.invoke(player)).floatValue();

            float dx = zx - px;
            float dy = zy - py;
            return dx * dx + dy * dy;
        } catch (Throwable t) {
            return Float.MAX_VALUE;
        }
    }

    /**
     * 좀비가 공격 중인지 확인.
     */
    public static boolean isAttacking(Object zombie) {
        if (zombie == null || !available || isAttacking == null)
            return false;

        if (!initialized)
            init(zombie);

        try {
            return (Boolean) isAttacking.invoke(zombie);
        } catch (Throwable t) {
            return false;
        }
    }

    /**
     * 좀비가 타겟을 가지고 있는지 확인.
     */
    public static boolean hasTarget(Object zombie) {
        if (zombie == null || !available)
            return false;

        if (!initialized)
            init(zombie);
        if (getTarget == null)
            return false;

        try {
            return getTarget.invoke(zombie) != null;
        } catch (Throwable t) {
            return false;
        }
    }
}
