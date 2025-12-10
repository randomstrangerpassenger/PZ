package com.pulse.api.profiler;

/**
 * Hook for AI Pathfinding profiling.
 * 
 * @since Pulse 0.2.0
 */
public final class PathfindingHook {

    private static volatile IPathfindingCallback callback;
    public static volatile boolean enabled = false;

    private PathfindingHook() {
    }

    public static void setCallback(IPathfindingCallback cb) {
        callback = cb;
    }

    public static void onLosCalculationStart() {
        IPathfindingCallback cb = callback;
        if (cb != null)
            cb.onLosCalculationStart();
    }

    public static void onLosCalculationEnd() {
        IPathfindingCallback cb = callback;
        if (cb != null)
            cb.onLosCalculationEnd();
    }

    public static void onGridSearchStart() {
        IPathfindingCallback cb = callback;
        if (cb != null)
            cb.onGridSearchStart();
    }

    public static void onGridSearchEnd() {
        IPathfindingCallback cb = callback;
        if (cb != null)
            cb.onGridSearchEnd();
    }

    public static void onPathRequest() {
        IPathfindingCallback cb = callback;
        if (cb != null)
            cb.onPathRequest();
    }

    public interface IPathfindingCallback {
        void onLosCalculationStart();

        void onLosCalculationEnd();

        void onGridSearchStart();

        void onGridSearchEnd();

        void onPathRequest();
    }
}
