package com.pulse.api.profiler;

import com.pulse.api.spi.IPathfindingContext;
import com.pulse.api.spi.IPathfindingGuard;

/**
 * Hook for AI Pathfinding profiling and guard integration.
 * 
 * Area 7 확장: IPathfindingGuard를 통해 Fuse가 경로탐색 요청을 검사/지연.
 * 
 * @since Pulse 0.2.0
 * @since Pulse 2.1 - Added IPathfindingGuard support for Area 7
 */
public final class PathfindingHook {

    private static volatile IPathfindingCallback callback;
    private static volatile IPathfindingGuard guard;
    public static volatile boolean enabled = false;

    private PathfindingHook() {
    }

    public static void setCallback(IPathfindingCallback cb) {
        callback = cb;
    }

    // ═══════════════════════════════════════════════════════════════
    // Area 7: Guard Integration
    // ═══════════════════════════════════════════════════════════════

    /**
     * 가드 설정 (Fuse가 호출).
     */
    public static void setGuard(IPathfindingGuard g) {
        guard = g;
    }

    /**
     * 가드 해제.
     */
    public static void clearGuard() {
        guard = null;
    }

    /**
     * 경로탐색 요청 허용 여부 검사.
     * 
     * Fail-open: 가드가 없으면 항상 허용.
     * 
     * @param context 경로탐색 컨텍스트
     * @return true = 즉시 처리, false = 지연 요청됨
     */
    public static boolean shouldProceed(IPathfindingContext context) {
        IPathfindingGuard g = guard;
        if (g == null) {
            return true; // Fail-open: 가드 없으면 통과
        }
        return g.checkPathRequest(context);
    }

    /**
     * 틱 시작 알림 (Pulse GameTick에서 호출).
     */
    public static void notifyTickStart(long gameTick) {
        IPathfindingGuard g = guard;
        if (g != null) {
            g.onTickStart(gameTick);
        }
    }

    /**
     * 틱 종료 알림.
     */
    public static void notifyTickEnd(long gameTick) {
        IPathfindingGuard g = guard;
        if (g != null) {
            g.onTickEnd(gameTick);
        }
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
