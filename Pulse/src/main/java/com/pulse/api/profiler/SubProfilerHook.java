package com.pulse.api.profiler;

/**
 * SubProfiler Hooks for Echo.
 * 
 * Allows Echo to receive sub-profiler timing events from Pulse mixins.
 * 
 * @since Pulse 1.1
 */
public class SubProfilerHook {

    public interface ISubProfilerCallback {
        long start(String label);

        void end(String label, long startTime);
    }

    private static ISubProfilerCallback callback;

    public static void setCallback(ISubProfilerCallback cb) {
        callback = cb;
    }

    public static void clearCallback() {
        callback = null;
    }

    public static long start(String label) {
        if (callback != null) {
            return callback.start(label);
        }
        return -1;
    }

    public static void end(String label, long startTime) {
        if (callback != null) {
            callback.end(label, startTime);
        }
    }
}
