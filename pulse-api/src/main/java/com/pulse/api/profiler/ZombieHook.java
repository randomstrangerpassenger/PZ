package com.pulse.api.profiler;

/**
 * Hook for detailed Zombie profiling.
 * 
 * @since Pulse 0.2.0
 */
public final class ZombieHook {

    private static volatile IZombieCallback callback;
    public static volatile boolean detailsEnabled = false;

    private ZombieHook() {
    }

    public static void setCallback(IZombieCallback cb) {
        callback = cb;
    }

    public static void onMotionUpdateStart() {
        IZombieCallback cb = callback;
        if (cb != null)
            cb.onMotionUpdateStart();
    }

    public static void onMotionUpdateEnd() {
        IZombieCallback cb = callback;
        if (cb != null)
            cb.onMotionUpdateEnd();
    }

    public static void onSoundPerceptionStart() {
        IZombieCallback cb = callback;
        if (cb != null)
            cb.onSoundPerceptionStart();
    }

    public static void onSoundPerceptionEnd() {
        IZombieCallback cb = callback;
        if (cb != null)
            cb.onSoundPerceptionEnd();
    }

    public static void onTargetTrackingStart() {
        IZombieCallback cb = callback;
        if (cb != null)
            cb.onTargetTrackingStart();
    }

    public static void onTargetTrackingEnd() {
        IZombieCallback cb = callback;
        if (cb != null)
            cb.onTargetTrackingEnd();
    }

    public static void onZombieUpdate() {
        IZombieCallback cb = callback;
        if (cb != null)
            cb.onZombieUpdate();
    }

    public interface IZombieCallback {
        void onMotionUpdateStart();

        void onMotionUpdateEnd();

        void onSoundPerceptionStart();

        void onSoundPerceptionEnd();

        void onTargetTrackingStart();

        void onTargetTrackingEnd();

        void onZombieUpdate();
    }
}
