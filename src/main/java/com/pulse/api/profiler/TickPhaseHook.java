package com.pulse.api.profiler;

/**
 * Tick Phase Hooks for Echo.
 * 
 * Allows Echo to receive phase-level timing events from Pulse mixins.
 * 
 * @since Pulse 1.1
 */
public class TickPhaseHook {

    public interface ITickPhaseCallback {
        long startPhase(String phase);

        void endPhase(String phase, long startTime);

        void onTickComplete();
    }

    private static ITickPhaseCallback callback;

    public static void setCallback(ITickPhaseCallback cb) {
        callback = cb;
    }

    public static void clearCallback() {
        callback = null;
    }

    public static long startPhase(String phase) {
        if (callback != null) {
            return callback.startPhase(phase);
        }
        return -1;
    }

    public static void endPhase(String phase, long startTime) {
        if (callback != null) {
            callback.endPhase(phase, startTime);
        }
    }

    public static void onTickComplete() {
        if (callback != null) {
            callback.onTickComplete();
        }
    }
}
