package com.fuse.throttle;

import com.fuse.config.FuseConfig;
import com.fuse.governor.RollingTickStats;
import com.fuse.telemetry.ReasonStats;
import com.fuse.telemetry.TelemetryReason;

/**
 * ThrottleCalculator - 거리 기반 레벨 계산 + 히스테리시스 로직
 * 
 * Phase 1-C Stage 2: FuseThrottleController에서 분리
 * 
 * <p>
 * 순수 계산 로직만 담당하며, Governor/Panic/Guard 연동은
 * FuseThrottleController에서 처리합니다.
 * </p>
 */
public class ThrottleCalculator {

    // --- 히스테리시스 설정 (윈도우 통계 기반) ---
    private static final double ENTRY_MAX_1S_MS = 33.33; // 진입: 1초 내 max > 33.33ms
    private static final double ENTRY_AVG_5S_MS = 20.0; // 또는: 5초 avg > 20ms
    private static final double EXIT_AVG_5S_MS = 12.0; // 복구: 5초 avg < 12ms
    private static final int EXIT_STABILITY_TICKS = 300; // 5초 유지 필요

    // --- 히스테리시스 상태 ---
    private ThrottleLevel hysteresisLevel = ThrottleLevel.FULL;
    private int stabilityCounter = 0;
    private boolean hysteresisActive = false;

    // 텔레메트리
    private TelemetryReason lastReason = null;
    private ReasonStats reasonStats;

    /**
     * ReasonStats 설정 (텔레메트리용)
     */
    public void setReasonStats(ReasonStats reasonStats) {
        this.reasonStats = reasonStats;
    }

    /**
     * 거리 기반 ThrottleLevel 계산
     * 
     * @param distSq 거리 제곱값
     * @return 거리 기반 ThrottleLevel
     */
    public ThrottleLevel calculateDistanceLevel(float distSq) {
        FuseConfig config = FuseConfig.getInstance();

        if (distSq < config.getNearDistSq()) {
            return ThrottleLevel.FULL;
        }
        if (distSq < config.getMediumDistSq()) {
            return ThrottleLevel.REDUCED;
        }
        if (distSq < config.getFarDistSq()) {
            return ThrottleLevel.LOW;
        }
        return ThrottleLevel.MINIMAL;
    }

    /**
     * 윈도우 통계 기반 히스테리시스 적용
     * 
     * @param newLevel 새로 계산된 레벨
     * @param stats    롤링 통계 (nullable)
     * @return 히스테리시스 적용 후 레벨
     */
    public ThrottleLevel applyHysteresis(ThrottleLevel newLevel, RollingTickStats stats) {
        if (stats == null || !stats.hasEnoughData()) {
            return newLevel; // 데이터 부족 시 bypass
        }

        double max1s = stats.getLast1sMaxMs();
        double avg5s = stats.getLast5sAvgMs();

        // 진입 조건: 1초 내 max > 33.33ms 또는 5초 avg > 20ms
        if (max1s > ENTRY_MAX_1S_MS || avg5s > ENTRY_AVG_5S_MS) {
            stabilityCounter = 0;
            hysteresisActive = true;
            lastReason = max1s > ENTRY_MAX_1S_MS
                    ? TelemetryReason.THROTTLE_WINDOW_EXCEEDED
                    : TelemetryReason.THROTTLE_AVG_HIGH;
            recordReason(lastReason);

            // 더 보수적인 레벨로 전환
            hysteresisLevel = getMoreConservativeLevel(hysteresisLevel);
            return hysteresisLevel;
        }

        // 복구 조건: 5초 avg < 12ms가 N초 유지
        if (avg5s < EXIT_AVG_5S_MS) {
            stabilityCounter++;
            if (stabilityCounter >= EXIT_STABILITY_TICKS) {
                hysteresisActive = false;
                hysteresisLevel = ThrottleLevel.FULL;
                lastReason = null;
                return newLevel; // 완전 복구
            }
        } else {
            stabilityCounter = 0; // 안정성 깨짐
        }

        // 히스테리시스 활성 중이면 현재 레벨 유지
        if (hysteresisActive) {
            return hysteresisLevel;
        }

        return newLevel;
    }

    /**
     * 더 보수적인 ThrottleLevel 반환
     */
    public ThrottleLevel getMoreConservativeLevel(ThrottleLevel current) {
        return switch (current) {
            case FULL -> ThrottleLevel.REDUCED;
            case REDUCED -> ThrottleLevel.LOW;
            case LOW, MINIMAL -> ThrottleLevel.MINIMAL;
        };
    }

    /**
     * 히스테리시스 상태 리셋
     */
    public void reset() {
        hysteresisLevel = ThrottleLevel.FULL;
        stabilityCounter = 0;
        hysteresisActive = false;
        lastReason = null;
    }

    // --- Getters ---

    public ThrottleLevel getHysteresisLevel() {
        return hysteresisLevel;
    }

    public boolean isHysteresisActive() {
        return hysteresisActive;
    }

    public TelemetryReason getLastReason() {
        return lastReason;
    }

    public int getStabilityCounter() {
        return stabilityCounter;
    }

    /**
     * ReasonStats에 개입 이유 기록
     */
    private void recordReason(TelemetryReason reason) {
        if (reasonStats != null && reason != null) {
            reasonStats.increment(reason);
        }
    }
}
