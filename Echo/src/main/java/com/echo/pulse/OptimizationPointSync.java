package com.echo.pulse;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.optimization.OptimizationPointRegistry;
import com.pulse.api.optimization.OptimizationPointRegistry.OptimizationPointInfo;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Pulse OptimizationPointRegistry와 Echo 측정 시스템 동기화
 * 
 * Pulse에 등록된 모든 최적화 포인트를 Echo 프로파일러에서
 * 동적으로 사용할 수 있도록 합니다.
 * 
 * @since 2.0.0 - Pulse Native Integration
 */
public class OptimizationPointSync {

    // 동기화된 포인트 캐시
    private static final Map<String, OptimizationPointInfo> loadedPoints = new ConcurrentHashMap<>();

    // 동기화 상태
    private static boolean synced = false;

    private OptimizationPointSync() {
        // Utility class
    }

    /**
     * Pulse OptimizationPointRegistry에서 모든 포인트 동기화
     * EchoMod.init()에서 호출됨
     */
    public static void syncFromPulse() {
        if (synced) {
            PulseLogger.debug("Echo", "OptimizationPoint already synced");
            return;
        }

        try {
            Collection<OptimizationPointInfo> all = OptimizationPointRegistry.getAll();

            for (OptimizationPointInfo info : all) {
                loadedPoints.put(info.getId(), info);
            }

            synced = true;
            PulseLogger.info("Echo", "Synced " + loadedPoints.size() + " optimization points from Pulse");

            int count = 0;
            for (OptimizationPointInfo info : loadedPoints.values()) {
                if (count++ >= 5) {
                    PulseLogger.debug("Echo", "... and " + (loadedPoints.size() - 5) + " more");
                    break;
                }
                PulseLogger.debug("Echo", "- " + info.getId() + " (tier " + info.getTier() + ")");
            }
        } catch (Exception e) {
            PulseLogger.error("Echo", "Failed to sync optimization points: " + e.getMessage());
        }
    }

    /**
     * 동기화된 모든 포인트 반환
     * 
     * @return 불변 컬렉션
     */
    public static Collection<OptimizationPointInfo> getPoints() {
        return Collections.unmodifiableCollection(loadedPoints.values());
    }

    /**
     * ID로 포인트 조회
     * 
     * @param id 포인트 ID
     * @return OptimizationPointInfo or null
     */
    public static OptimizationPointInfo getPoint(String id) {
        return loadedPoints.get(id);
    }

    /**
     * 포인트 ID 존재 여부 확인
     * 
     * @param id 포인트 ID
     * @return 존재하면 true
     */
    public static boolean hasPoint(String id) {
        return loadedPoints.containsKey(id);
    }

    /**
     * 동기화된 포인트 수
     */
    public static int getPointCount() {
        return loadedPoints.size();
    }

    /**
     * 동기화 상태 확인
     */
    public static boolean isSynced() {
        return synced;
    }

    /**
     * Echo 라벨로 포인트 찾기
     * 
     * @param echoPrefix Echo 라벨 접두사
     * @return Optional containing the info
     */
    public static Optional<OptimizationPointInfo> findByEchoPrefix(String echoPrefix) {
        return loadedPoints.values().stream()
                .filter(info -> echoPrefix.equals(info.getEchoPrefix()))
                .findFirst();
    }

    /**
     * Tier로 포인트 필터링
     * 
     * @param tier Tier 레벨
     * @return 해당 Tier의 포인트 목록
     */
    public static List<OptimizationPointInfo> getPointsByTier(int tier) {
        return loadedPoints.values().stream()
                .filter(info -> info.getTier() == tier)
                .toList();
    }

    /**
     * 동기화 초기화 (테스트용)
     */
    public static void reset() {
        loadedPoints.clear();
        synced = false;
    }
}
