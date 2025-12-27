package com.echo.pulse;

import com.pulse.api.di.PulseServices;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.IOptimizationPointRegistry;

import java.util.*;

/**
 * Pulse OptimizationPointRegistry와 Echo 측정 시스템 동기화.
 * 
 * Phase 4: IOptimizationPointRegistry 인터페이스 사용하여 복원.
 * PulseServices.optimizationPoints()를 통해 최적화 포인트 정보에 접근합니다.
 * 
 * @since 2.0.0 - Pulse Native Integration
 * @since 3.0.0 - Stub Implementation (Phase 3)
 * @since 4.0.0 - Restored with IOptimizationPointRegistry (Phase 4)
 */
public class OptimizationPointSync {

    // 캐시된 포인트 데이터
    private static final Map<String, Long> cachedPoints = new LinkedHashMap<>();
    private static boolean synced = false;
    private static long lastSyncTick = 0;

    // 동기화 간격 (틱당 한 번만)
    private static final long SYNC_INTERVAL_MS = 1000;

    private OptimizationPointSync() {
        // Utility class
    }

    /**
     * Pulse OptimizationPointRegistry에서 모든 포인트 동기화.
     */
    public static void syncFromPulse() {
        if (synced && System.currentTimeMillis() - lastSyncTick < SYNC_INTERVAL_MS) {
            return; // 이미 최근에 동기화됨
        }

        try {
            IOptimizationPointRegistry registry = PulseServices.optimizationPoints();
            cachedPoints.clear();

            for (String pointId : registry.getPointIds()) {
                if (registry.isPointEnabled(pointId)) {
                    long value = registry.getPointValue(pointId);
                    cachedPoints.put(pointId, value);
                }
            }

            synced = true;
            lastSyncTick = System.currentTimeMillis();
            PulseLogger.debug("Echo", "OptimizationPointSync: synced " + cachedPoints.size() + " points");
        } catch (IllegalStateException e) {
            // PulseServices not initialized - use empty state
            if (!synced) {
                PulseLogger.debug("Echo", "OptimizationPointSync: PulseServices not ready");
                synced = true; // Mark as synced to avoid repeated warnings
            }
        } catch (Exception e) {
            PulseLogger.warn("Echo", "OptimizationPointSync failed: " + e.getMessage());
            synced = true;
        }
    }

    /**
     * 동기화된 모든 포인트 반환.
     * 
     * @return 포인트 ID → 측정값 맵 (읽기 전용)
     */
    public static Map<String, Long> getPoints() {
        syncFromPulse();
        return Collections.unmodifiableMap(cachedPoints);
    }

    /**
     * 특정 포인트 값 조회.
     * 
     * @param pointId 포인트 ID
     * @return 측정값 (나노초), 없으면 -1
     */
    public static long getPointValue(String pointId) {
        syncFromPulse();
        return cachedPoints.getOrDefault(pointId, -1L);
    }

    /**
     * 동기화된 포인트 수.
     */
    public static int getPointCount() {
        syncFromPulse();
        return cachedPoints.size();
    }

    /**
     * 동기화 상태 확인.
     */
    public static boolean isSynced() {
        return synced;
    }

    /**
     * 포인트 ID 존재 여부 확인.
     */
    public static boolean hasPoint(String id) {
        syncFromPulse();
        return cachedPoints.containsKey(id);
    }

    /**
     * 동기화 초기화 (테스트용).
     */
    public static void reset() {
        cachedPoints.clear();
        synced = false;
        lastSyncTick = 0;
    }

    /**
     * 강제 동기화 (다음 호출 시 새로 가져옴).
     */
    public static void invalidate() {
        lastSyncTick = 0;
    }
}
