package com.pulse.api.profiler;

/**
 * Zombie Hooks for Echo/Fuse.
 * 
 * Phase 2 Optimized: 리플렉션 제거, 경량화
 * Phase 3: Tiered throttle + ThreadLocal 컨텍스트
 * 
 * @since Pulse 1.2
 * @since Pulse 1.5 - ThrottleLevel 기반 Tiered throttle
 */
public class ZombieHook {

    /** Enable detailed profiling (계측 오버헤드 있음) */
    public static boolean profilingEnabled = false;

    /** Throttle policy (Fuse) */
    private static IZombieThrottlePolicy throttlePolicy;

    /** Profiling callback */
    private static IZombieCallback callback;

    // =================================================================
    // ThreadLocal ThrottleLevel Context (Stale 방지 포함)
    // =================================================================

    /** ThreadLocal 컨텍스트 (level + 설정 틱) */
    private static final ThreadLocal<ThrottleLevelContext> currentContext = new ThreadLocal<>();

    /** 컨텍스트 레코드 - level과 설정 틱을 함께 저장 */
    private static class ThrottleLevelContext {
        final ThrottleLevel level;
        final long setTick;

        ThrottleLevelContext(ThrottleLevel level, long setTick) {
            this.level = level;
            this.setTick = setTick;
        }
    }

    /**
     * 현재 좀비의 ThrottleLevel 설정 (Mixin update HEAD에서 호출).
     * 
     * @param level     ThrottleLevel
     * @param worldTick 현재 월드 틱 (stale 감지용)
     */
    public static void setCurrentThrottleLevel(ThrottleLevel level, long worldTick) {
        currentContext.set(new ThrottleLevelContext(level, worldTick));
    }

    /**
     * 현재 ThrottleLevel 조회 (Step hook에서 호출).
     * 
     * Stale 방지: 1틱 이상 지난 컨텍스트는 FULL로 폴백.
     * 
     * @param worldTick 현재 월드 틱
     * @return ThrottleLevel (stale이거나 null이면 FULL)
     */
    public static ThrottleLevel getCurrentThrottleLevel(long worldTick) {
        ThrottleLevelContext ctx = currentContext.get();
        if (ctx == null) {
            return ThrottleLevel.FULL;
        }

        // 1틱 이상 지났으면 stale → FULL 폴백
        if (worldTick - ctx.setTick > 1) {
            currentContext.remove();
            return ThrottleLevel.FULL;
        }
        return ctx.level;
    }

    /**
     * ThrottleLevel 컨텍스트 정리 (Mixin update RETURN에서 호출).
     */
    public static void clearCurrentThrottleLevel() {
        currentContext.remove();
    }

    // =================================================================
    // Registration
    // =================================================================

    public static void setCallback(IZombieCallback cb) {
        callback = cb;
    }

    public static void clearCallback() {
        callback = null;
    }

    public static void setThrottlePolicy(IZombieThrottlePolicy policy) {
        throttlePolicy = policy;
        if (policy != null) {
            System.out.println("[Pulse] ZombieThrottlePolicy registered (Tiered mode)");
        }
    }

    public static void clearThrottlePolicy() {
        throttlePolicy = null;
    }

    // =================================================================
    // ThrottleLevel API (신규)
    // =================================================================

    /**
     * ThrottleLevel 조회 (Mixin에서 호출).
     * 
     * @param distSq          플레이어까지 거리 제곱
     * @param isAttacking     공격 중 여부
     * @param hasTarget       타겟 있음 여부
     * @param recentlyEngaged 최근 60틱 내 교전 여부
     * @return ThrottleLevel (policy 없으면 FULL)
     */
    public static ThrottleLevel getThrottleLevel(float distSq, boolean isAttacking,
            boolean hasTarget, boolean recentlyEngaged) {
        if (throttlePolicy == null) {
            return ThrottleLevel.FULL;
        }

        try {
            return throttlePolicy.getThrottleLevel(distSq, isAttacking, hasTarget, recentlyEngaged);
        } catch (Throwable t) {
            return ThrottleLevel.FULL;
        }
    }

    // =================================================================
    // Legacy API (Deprecated - 하위 호환용)
    // =================================================================

    /**
     * @deprecated Use getThrottleLevel() instead
     */
    @Deprecated
    public static boolean shouldSkipFast(float distSq, boolean isAttacking, boolean hasTarget,
            int iterIndex, int worldTick) {
        ThrottleLevel level = getThrottleLevel(distSq, isAttacking, hasTarget, false);
        return level != ThrottleLevel.FULL;
    }

    // --- Profiling (조건부) ---

    public static void onZombieUpdate(Object zombie) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onZombieUpdateWithContext(zombie);
            } catch (Throwable t) {
            }
        }
    }

    public static void onMotionUpdateStart(Object zombie) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onMotionUpdateStartWithContext(zombie);
            } catch (Throwable t) {
            }
        }
    }

    public static void onMotionUpdateEnd(Object zombie) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onMotionUpdateEndWithContext(zombie);
            } catch (Throwable t) {
            }
        }
    }

    // --- Phase 2: New Zombie Event Hooks ---

    public static void onZombieSpotted(Object zombie, Object target, boolean forced) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onZombieSpottedWithContext(zombie, target, forced);
            } catch (Throwable t) {
            }
        }
    }

    public static void onZombieHit(Object zombie, Object attacker, float damage) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onZombieHitWithContext(zombie, attacker, damage);
            } catch (Throwable t) {
            }
        }
    }

    public static void onZombieKill(Object zombie, Object killer) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onZombieKillWithContext(zombie, killer);
            } catch (Throwable t) {
            }
        }
    }

    // Legacy - disabled
    public static void onZombieUpdate() {
    }

    public static void onMotionUpdateStart() {
    }

    public static void onMotionUpdateEnd() {
    }

    public static void onSoundPerceptionStart() {
    }

    public static void onSoundPerceptionEnd() {
    }

    public static void onTargetTrackingStart() {
    }

    public static void onTargetTrackingEnd() {
    }

    public static void onSoundPerceptionStart(Object z) {
    }

    public static void onSoundPerceptionEnd(Object z) {
    }

    public static void onTargetTrackingStart(Object z) {
    }

    public static void onTargetTrackingEnd(Object z) {
    }

    // --- Callback Interface ---

    public interface IZombieCallback {
        default void onZombieUpdate() {
        }

        default void onMotionUpdateStart() {
        }

        default void onMotionUpdateEnd() {
        }

        default void onSoundPerceptionStart() {
        }

        default void onSoundPerceptionEnd() {
        }

        default void onTargetTrackingStart() {
        }

        default void onTargetTrackingEnd() {
        }

        default void onZombieUpdateWithContext(Object zombie) {
            onZombieUpdate();
        }

        default void onMotionUpdateStartWithContext(Object zombie) {
            onMotionUpdateStart();
        }

        default void onMotionUpdateEndWithContext(Object zombie) {
            onMotionUpdateEnd();
        }

        default void onSoundPerceptionStartWithContext(Object zombie) {
            onSoundPerceptionStart();
        }

        default void onSoundPerceptionEndWithContext(Object zombie) {
            onSoundPerceptionEnd();
        }

        default void onTargetTrackingStartWithContext(Object zombie) {
            onTargetTrackingStart();
        }

        default void onTargetTrackingEndWithContext(Object zombie) {
            onTargetTrackingEnd();
        }

        // Phase 2: New Event Hooks
        default void onZombieSpotted(Object target, boolean forced) {
        }

        default void onZombieSpottedWithContext(Object zombie, Object target, boolean forced) {
            onZombieSpotted(target, forced);
        }

        default void onZombieHit(Object attacker, float damage) {
        }

        default void onZombieHitWithContext(Object zombie, Object attacker, float damage) {
            onZombieHit(attacker, damage);
        }

        default void onZombieKill(Object killer) {
        }

        default void onZombieKillWithContext(Object zombie, Object killer) {
            onZombieKill(killer);
        }
    }
}
