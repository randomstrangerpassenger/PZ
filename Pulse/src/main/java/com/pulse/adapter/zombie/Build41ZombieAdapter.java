package com.pulse.adapter.zombie;

import com.pulse.api.version.GameVersion;
import com.pulse.api.log.PulseLogger;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;

/**
 * Build 41 전용 IsoZombie 어댑터.
 * 
 * Build 41의 IsoZombie 클래스 구조를 기반으로 구현되어 있습니다.
 * classcodes/IsoZombie.txt 참고.
 * 
 * 주요 메서드:
 * - getOnlineID(): short 반환
 * - getID(): Object ID
 * - getTarget(): IsoMovingObject
 * - isAttacking(): boolean
 * - getX(), getY(), getZ(): float
 * 
 * @since Pulse 1.4
 */
public class Build41ZombieAdapter implements IZombieAdapter {

    private static final String LOG = "Pulse";

    // 캐시된 메서드 (성능 최적화)
    private Method methodGetOnlineID;
    private Method methodGetID;
    private Method methodGetX;
    private Method methodGetY;
    private Method methodGetZ;
    private Method methodIsAttacking;
    private Method methodGetTarget;
    private Method methodIsCrawling;
    private Method methodIsOnFloor;
    private Method methodGetHitTime;

    // 플레이어 클래스 캐시
    private Class<?> playerClass;
    private Field playersField;

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
            Class.forName("zombie.characters.IsoZombie");
            return true;
        } catch (ClassNotFoundException e) {
            return false;
        }
    }

    @Override
    public String getName() {
        return "Build41ZombieAdapter";
    }

    // ═══════════════════════════════════════════════════════════════
    // IZombieAdapter Implementation
    // ═══════════════════════════════════════════════════════════════

    @Override
    public int getZombieId(Object zombie) {
        // MP first: getOnlineID()
        int onlineId = getOnlineId(zombie);
        if (onlineId > 0) {
            return onlineId;
        }

        // SP fallback: getID()
        int localId = getLocalId(zombie);
        if (localId > 0) {
            return localId;
        }

        // Final fallback
        return System.identityHashCode(zombie);
    }

    @Override
    public int getOnlineId(Object zombie) {
        try {
            ensureInitialized(zombie);
            if (methodGetOnlineID != null) {
                Object result = methodGetOnlineID.invoke(zombie);
                if (result instanceof Number) {
                    return ((Number) result).intValue();
                }
            }
        } catch (Throwable t) {
            // Silently fail
        }
        return -1;
    }

    @Override
    public int getLocalId(Object zombie) {
        try {
            ensureInitialized(zombie);
            if (methodGetID != null) {
                Object result = methodGetID.invoke(zombie);
                if (result instanceof Number) {
                    return ((Number) result).intValue();
                }
            }
        } catch (Throwable t) {
            // Silently fail
        }
        return -1;
    }

    @Override
    public float getX(Object zombie) {
        return invokeFloatMethod(zombie, methodGetX, "getX", 0f);
    }

    @Override
    public float getY(Object zombie) {
        return invokeFloatMethod(zombie, methodGetY, "getY", 0f);
    }

    @Override
    public float getZ(Object zombie) {
        return invokeFloatMethod(zombie, methodGetZ, "getZ", 0f);
    }

    @Override
    public float getDistanceSquaredToNearestPlayer(Object zombie) {
        try {
            ensureInitialized(zombie);

            float zx = getX(zombie);
            float zy = getY(zombie);

            if (playerClass == null || playersField == null) {
                return Float.MAX_VALUE;
            }

            ArrayList<?> players = (ArrayList<?>) playersField.get(null);

            if (players == null || players.isEmpty()) {
                return Float.MAX_VALUE;
            }

            float minDistSq = Float.MAX_VALUE;
            for (Object player : players) {
                if (player == null)
                    continue;

                float px = invokeFloatMethod(player, null, "getX", 0f);
                float py = invokeFloatMethod(player, null, "getY", 0f);

                float dx = zx - px;
                float dy = zy - py;
                float distSq = dx * dx + dy * dy;

                if (distSq < minDistSq) {
                    minDistSq = distSq;
                }
            }
            return minDistSq;
        } catch (Throwable t) {
            return Float.MAX_VALUE;
        }
    }

    @Override
    public boolean isAttacking(Object zombie) {
        return invokeBooleanMethod(zombie, methodIsAttacking, "isAttacking", false);
    }

    @Override
    public boolean hasTarget(Object zombie) {
        return getTarget(zombie) != null;
    }

    @Override
    public Object getTarget(Object zombie) {
        try {
            ensureInitialized(zombie);
            if (methodGetTarget != null) {
                return methodGetTarget.invoke(zombie);
            }
        } catch (Throwable t) {
            // Silently fail
        }
        return null;
    }

    @Override
    public boolean isCrawler(Object zombie) {
        return invokeBooleanMethod(zombie, methodIsCrawling, "isCrawling", false);
    }

    @Override
    public boolean isOnFloor(Object zombie) {
        return invokeBooleanMethod(zombie, methodIsOnFloor, "isOnFloor", false);
    }

    @Override
    public int getHitTime(Object zombie) {
        return invokeIntMethod(zombie, methodGetHitTime, "getHitTime", 0);
    }

    // ═══════════════════════════════════════════════════════════════
    // Internal Helpers
    // ═══════════════════════════════════════════════════════════════

    private void ensureInitialized(Object zombie) {
        if (initialized)
            return;

        try {
            Class<?> zombieClass = zombie.getClass();

            // Method 캐싱
            methodGetOnlineID = findMethod(zombieClass, "getOnlineID");
            methodGetID = findMethod(zombieClass, "getID");
            methodGetX = findMethod(zombieClass, "getX");
            methodGetY = findMethod(zombieClass, "getY");
            methodGetZ = findMethod(zombieClass, "getZ");
            methodIsAttacking = findMethod(zombieClass, "isAttacking");
            methodGetTarget = findMethod(zombieClass, "getTarget");
            methodIsCrawling = findMethod(zombieClass, "isCrawling");
            methodIsOnFloor = findMethod(zombieClass, "isOnFloor");
            methodGetHitTime = findMethod(zombieClass, "getHitTime");

            // 플레이어 클래스 캐싱
            playerClass = Class.forName("zombie.characters.IsoPlayer");
            playersField = playerClass.getField("players");

            initialized = true;
        } catch (Throwable t) {
            PulseLogger.error(LOG, "Build41ZombieAdapter failed to initialize: " + t.getMessage());
        }
    }

    private Method findMethod(Class<?> clazz, String name) {
        try {
            Method m = clazz.getMethod(name);
            m.setAccessible(true);
            return m;
        } catch (NoSuchMethodException e) {
            return null;
        }
    }

    private float invokeFloatMethod(Object obj, Method cached, String methodName, float fallback) {
        try {
            Method m = cached;
            if (m == null) {
                m = obj.getClass().getMethod(methodName);
            }
            Object result = m.invoke(obj);
            if (result instanceof Number) {
                return ((Number) result).floatValue();
            }
        } catch (Throwable t) {
            // Silently fail
        }
        return fallback;
    }

    private boolean invokeBooleanMethod(Object obj, Method cached, String methodName, boolean fallback) {
        try {
            Method m = cached;
            if (m == null) {
                m = obj.getClass().getMethod(methodName);
            }
            Object result = m.invoke(obj);
            if (result instanceof Boolean) {
                return (Boolean) result;
            }
        } catch (Throwable t) {
            // Silently fail
        }
        return fallback;
    }

    private int invokeIntMethod(Object obj, Method cached, String methodName, int fallback) {
        try {
            Method m = cached;
            if (m == null) {
                m = obj.getClass().getMethod(methodName);
            }
            Object result = m.invoke(obj);
            if (result instanceof Number) {
                return ((Number) result).intValue();
            }
        } catch (Throwable t) {
            // Silently fail
        }
        return fallback;
    }
}
