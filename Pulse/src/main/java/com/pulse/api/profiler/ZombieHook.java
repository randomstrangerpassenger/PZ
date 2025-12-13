package com.pulse.api.profiler;

/**
 * Zombie Hooks for Echo.
 * 
 * Allows Echo to receive zombie-level timing events from Pulse mixins.
 * 
 * @since Pulse 1.1
 */
public class ZombieHook {

    /**
     * Enable detailed zombie profiling (motion, perception, tracking).
     * Set by Echo config at startup.
     */
    public static boolean detailsEnabled = false;

    public interface IZombieCallback {
        void onMotionUpdateStart();

        void onMotionUpdateEnd();

        void onSoundPerceptionStart();

        void onSoundPerceptionEnd();

        void onTargetTrackingStart();

        void onTargetTrackingEnd();

        void onZombieUpdate();
    }

    private static IZombieCallback callback;

    public static void setCallback(IZombieCallback cb) {
        callback = cb;
    }

    public static void clearCallback() {
        callback = null;
    }

    public static void onMotionUpdateStart() {
        if (callback != null) {
            callback.onMotionUpdateStart();
        }
    }

    public static void onMotionUpdateEnd() {
        if (callback != null) {
            callback.onMotionUpdateEnd();
        }
    }

    public static void onSoundPerceptionStart() {
        if (callback != null) {
            callback.onSoundPerceptionStart();
        }
    }

    public static void onSoundPerceptionEnd() {
        if (callback != null) {
            callback.onSoundPerceptionEnd();
        }
    }

    public static void onTargetTrackingStart() {
        if (callback != null) {
            callback.onTargetTrackingStart();
        }
    }

    public static void onTargetTrackingEnd() {
        if (callback != null) {
            callback.onTargetTrackingEnd();
        }
    }

    public static void onZombieUpdate() {
        if (callback != null) {
            callback.onZombieUpdate();
        }
    }
}
