package com.pulse.api.profiler;

/**
 * Zombie Hooks for Echo/Fuse.
 * 
 * Phase 2 Optimized: 리플렉션 제거, 경량화
 * 
 * @since Pulse 1.2
 */
public class ZombieHook {

    /** Enable detailed profiling (계측 오버헤드 있음) */
    public static boolean profilingEnabled = false;

    /** Throttle policy (Fuse) */
    private static IZombieThrottlePolicy throttlePolicy;

    /** Profiling callback */
    private static IZombieCallback callback;

    // --- Registration ---

    public static void setCallback(IZombieCallback cb) {
        callback = cb;
    }

    public static void clearCallback() {
        callback = null;
    }

    public static void setThrottlePolicy(IZombieThrottlePolicy policy) {
        throttlePolicy = policy;
        if (policy != null) {
            System.out.println("[Pulse] ZombieThrottlePolicy registered");
        }
    }

    public static void clearThrottlePolicy() {
        throttlePolicy = null;
    }

    // --- Optimized Throttle Check (Mixin에서 직접 호출) ---

    /**
     * 경량 throttle 체크.
     * Mixin에서 직접 호출, 리플렉션 없음.
     */
    public static boolean shouldSkipFast(float distSq, boolean isAttacking, boolean hasTarget,
            int iterIndex, int worldTick) {
        if (throttlePolicy == null)
            return false;

        try {
            return throttlePolicy.shouldSkipFast(distSq, isAttacking, hasTarget, iterIndex, worldTick);
        } catch (Throwable t) {
            return false;
        }
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
    }
}
