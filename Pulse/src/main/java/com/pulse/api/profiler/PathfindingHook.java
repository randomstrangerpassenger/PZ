package com.pulse.api.profiler;

/**
 * Pathfinding Hooks for Echo.
 * 
 * Allows Echo to receive pathfinding-level timing events from Pulse mixins.
 * 
 * @since Pulse 1.1
 */
public class PathfindingHook {

    /**
     * 경로탐색 프로파일링 활성화 플래그.
     * Mixin에서 이 값을 체크하여 성능 오버헤드를 최소화합니다.
     */
    public static volatile boolean enabled = false;

    public interface IPathfindingCallback {
        void onLosCalculationStart();

        void onLosCalculationEnd();

        void onGridSearchStart();

        void onGridSearchEnd();

        void onPathRequest();
    }

    private static IPathfindingCallback callback;

    public static void setCallback(IPathfindingCallback cb) {
        callback = cb;
    }

    public static void clearCallback() {
        callback = null;
    }

    public static void onLosCalculationStart() {
        if (callback != null) {
            callback.onLosCalculationStart();
        }
    }

    public static void onLosCalculationEnd() {
        if (callback != null) {
            callback.onLosCalculationEnd();
        }
    }

    public static void onGridSearchStart() {
        if (callback != null) {
            callback.onGridSearchStart();
        }
    }

    public static void onGridSearchEnd() {
        if (callback != null) {
            callback.onGridSearchEnd();
        }
    }

    public static void onPathRequest() {
        if (callback != null) {
            callback.onPathRequest();
        }
    }
}
