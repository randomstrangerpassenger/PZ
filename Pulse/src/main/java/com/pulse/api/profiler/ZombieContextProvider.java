package com.pulse.api.profiler;

/**
 * Zombie Context Provider.
 * 
 * IsoZombie 객체에서 IZombieContext를 생성.
 * Mixin에서 호출하여 컨텍스트를 제공.
 * 
 * @since Pulse 1.2 / Phase 2
 */
public class ZombieContextProvider {

    private static int currentIterationIndex = 0;
    private static int worldTick = 0;

    /**
     * 현재 iteration index 증가 및 반환.
     */
    public static int nextIterationIndex() {
        return currentIterationIndex++;
    }

    /**
     * 틱 시작 시 iteration index 리셋.
     */
    public static void resetIterationIndex() {
        currentIterationIndex = 0;
    }

    /**
     * 월드 틱 업데이트.
     */
    public static void setWorldTick(int tick) {
        worldTick = tick;
    }

    public static int getWorldTick() {
        return worldTick;
    }

    /**
     * IsoZombie에서 Context 생성.
     * PZ 클래스에 대한 리플렉션으로 의존성 분리.
     */
    public static IZombieContext createContext(Object zombie) {
        if (zombie == null)
            return null;

        int index = nextIterationIndex();
        int tick = worldTick;

        try {
            // 리플렉션으로 PZ 클래스 메서드 호출
            Class<?> zombieClass = zombie.getClass();

            // getDistanceSq - 플레이어까지 거리
            float distSq = getDistanceToNearestPlayer(zombie, zombieClass);

            // isAttacking
            boolean attacking = invokeBoolean(zombie, zombieClass, "isAttacking", false);

            // getTarget
            Object target = invokeObject(zombie, zombieClass, "getTarget");
            boolean hasTarget = target != null;

            return new ZombieContext(distSq, attacking, hasTarget, index, tick);
        } catch (Throwable t) {
            // Failsoft: 에러 시 안전한 기본값 (스킵 안함)
            return new ZombieContext(0f, true, true, index, tick);
        }
    }

    private static float getDistanceToNearestPlayer(Object zombie, Class<?> zombieClass) {
        try {
            // zombie.getX(), getY() 가져오기
            float zx = invokeFloat(zombie, zombieClass, "getX", 0f);
            float zy = invokeFloat(zombie, zombieClass, "getY", 0f);

            // IsoPlayer.players 순회하여 가장 가까운 플레이어 찾기
            Class<?> playerClass = Class.forName("zombie.characters.IsoPlayer");
            java.lang.reflect.Field playersField = playerClass.getField("players");
            Object playersArray = playersField.get(null);

            if (playersArray == null)
                return Float.MAX_VALUE;

            // ArrayList<IsoPlayer>
            java.util.ArrayList<?> players = (java.util.ArrayList<?>) playersArray;

            float minDistSq = Float.MAX_VALUE;
            for (Object player : players) {
                if (player == null)
                    continue;
                float px = invokeFloat(player, player.getClass(), "getX", 0f);
                float py = invokeFloat(player, player.getClass(), "getY", 0f);
                float dx = zx - px;
                float dy = zy - py;
                float distSq = dx * dx + dy * dy;
                if (distSq < minDistSq) {
                    minDistSq = distSq;
                }
            }
            return minDistSq;
        } catch (Throwable t) {
            return Float.MAX_VALUE; // 에러 시 멀리있다고 가정
        }
    }

    private static boolean invokeBoolean(Object obj, Class<?> clazz, String method, boolean def) {
        try {
            return (boolean) clazz.getMethod(method).invoke(obj);
        } catch (Throwable t) {
            return def;
        }
    }

    private static float invokeFloat(Object obj, Class<?> clazz, String method, float def) {
        try {
            return (float) clazz.getMethod(method).invoke(obj);
        } catch (Throwable t) {
            return def;
        }
    }

    private static Object invokeObject(Object obj, Class<?> clazz, String method) {
        try {
            return clazz.getMethod(method).invoke(obj);
        } catch (Throwable t) {
            return null;
        }
    }

    /**
     * 내부 Context 구현.
     */
    private static class ZombieContext implements IZombieContext {
        private final float distSq;
        private final boolean attacking;
        private final boolean hasTarget;
        private final int index;
        private final int tick;

        ZombieContext(float distSq, boolean attacking, boolean hasTarget, int index, int tick) {
            this.distSq = distSq;
            this.attacking = attacking;
            this.hasTarget = hasTarget;
            this.index = index;
            this.tick = tick;
        }

        @Override
        public float getDistanceSquaredToPlayer() {
            return distSq;
        }

        @Override
        public boolean isAttacking() {
            return attacking;
        }

        @Override
        public boolean hasTarget() {
            return hasTarget;
        }

        @Override
        public int getIterationIndex() {
            return index;
        }

        @Override
        public int getWorldTick() {
            return tick;
        }
    }
}
