package com.fuse.throttle;

import com.fuse.governor.RollingTickStats;
import com.fuse.telemetry.TelemetryReason;

/**
 * 스로틀 히스테리시스 상태 머신.
 * 
 * <h2>설계 원칙 (Phase 1-B)</h2>
 * <ul>
 * <li>히스테리시스 상태 전이 로직만 담당</li>
 * <li>정책 판단은 없음 - 통계 기반 전이만</li>
 * <li>O(1) 연산으로 Hot-path 최적화</li>
 * </ul>
 * 
 * @since Fuse 2.4.0
 */
public class ThrottleStateMachine {

    // --- 히스테리시스 임계값 (불변) ---
    private final double entryMax1sMs;
    private final double entryAvg5sMs;
    private final double exitAvg5sMs;
    private final int exitStabilityTicks;

    // --- 상태 ---
    private ThrottleLevel currentLevel = ThrottleLevel.FULL;
    private int stabilityCounter = 0;
    private boolean active = false;
    private TelemetryReason lastReason = null;

    /**
     * 기본 임계값으로 생성.
     */
    public ThrottleStateMachine() {
        this(33.33, 20.0, 12.0, 300);
    }

    /**
     * 커스텀 임계값으로 생성.
     */
    public ThrottleStateMachine(double entryMax1sMs, double entryAvg5sMs,
            double exitAvg5sMs, int exitStabilityTicks) {
        this.entryMax1sMs = entryMax1sMs;
        this.entryAvg5sMs = entryAvg5sMs;
        this.exitAvg5sMs = exitAvg5sMs;
        this.exitStabilityTicks = exitStabilityTicks;
    }

    /**
     * 윈도우 통계 기반 히스테리시스 적용.
     * 
     * @param stats      롤링 통계
     * @param inputLevel 입력 레벨 (거리 기반 계산 결과)
     * @return 히스테리시스 적용된 최종 레벨
     */
    public ThrottleLevel apply(RollingTickStats stats, ThrottleLevel inputLevel) {
        if (stats == null || !stats.hasEnoughData()) {
            return inputLevel; // 데이터 부족 시 bypass
        }

        double max1s = stats.getLast1sMaxMs();
        double avg5s = stats.getLast5sAvgMs();

        // === 진입 조건 ===
        if (max1s > entryMax1sMs || avg5s > entryAvg5sMs) {
            stabilityCounter = 0;
            active = true;
            lastReason = max1s > entryMax1sMs
                    ? TelemetryReason.THROTTLE_WINDOW_EXCEEDED
                    : TelemetryReason.THROTTLE_AVG_HIGH;

            currentLevel = getMoreConservativeLevel(currentLevel);
            return currentLevel;
        }

        // === 복구 조건 ===
        if (avg5s < exitAvg5sMs) {
            stabilityCounter++;
            if (stabilityCounter >= exitStabilityTicks) {
                active = false;
                currentLevel = ThrottleLevel.FULL;
                lastReason = null;
                return inputLevel; // 완전 복구
            }
        } else {
            stabilityCounter = 0; // 안정성 깨짐
        }

        // 활성 중이면 현재 레벨 유지
        return active ? currentLevel : inputLevel;
    }

    /**
     * 더 보수적인 레벨로 강등.
     */
    private ThrottleLevel getMoreConservativeLevel(ThrottleLevel current) {
        return switch (current) {
            case FULL -> ThrottleLevel.REDUCED;
            case REDUCED -> ThrottleLevel.LOW;
            case LOW, MINIMAL -> ThrottleLevel.MINIMAL;
        };
    }

    // === Getters ===

    public ThrottleLevel getCurrentLevel() {
        return currentLevel;
    }

    public boolean isActive() {
        return active;
    }

    public int getStabilityCounter() {
        return stabilityCounter;
    }

    public TelemetryReason getLastReason() {
        return lastReason;
    }

    /**
     * 상태 리셋.
     */
    public void reset() {
        currentLevel = ThrottleLevel.FULL;
        stabilityCounter = 0;
        active = false;
        lastReason = null;
    }
}
