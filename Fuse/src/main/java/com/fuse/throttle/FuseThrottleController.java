package com.fuse.throttle;

import com.fuse.config.FuseConfig;
import com.fuse.governor.RollingTickStats;
import com.fuse.governor.SpikePanicProtocol;
import com.fuse.governor.TickBudgetGovernor;
import com.fuse.guard.StreamingGuard;
import com.fuse.guard.VehicleGuard;
import com.fuse.telemetry.TelemetryReason;
import com.pulse.api.profiler.IZombieThrottlePolicy;
import com.pulse.api.profiler.ThrottleLevel;

/**
 * Fuse Throttle Controller.
 * 
 * Tiered 거리 기반 좀비 업데이트 throttling.
 * update()는 절대 취소하지 않고, ThrottleLevel만 반환.
 * 
 * v1.1: 윈도우 기반 히스테리시스 + Governor/Panic 연동
 * 
 * @since Fuse 0.3.0
 * @since Fuse 0.5.0 - Tiered ThrottleLevel 방식으로 전환
 * @since Fuse 1.1.0 - Window-based hysteresis + Governor/Panic integration
 */
public class FuseThrottleController implements IZombieThrottlePolicy {

    private static final String LOG = "Fuse";

    // --- v1.1 컴포넌트 ---
    private TickBudgetGovernor governor;
    private SpikePanicProtocol panicProtocol;
    private RollingTickStats stats;
    private VehicleGuard vehicleGuard;
    private StreamingGuard streamingGuard;

    // --- 히스테리시스 설정 (윈도우 통계 기반) ---
    private static final double ENTRY_MAX_1S_MS = 33.33; // 진입: 1초 내 max > 33.33ms
    private static final double ENTRY_AVG_5S_MS = 20.0; // 또는: 5초 avg > 20ms
    private static final double EXIT_AVG_5S_MS = 12.0; // 복구: 5초 avg < 12ms
    private static final int EXIT_STABILITY_TICKS = 300; // 5초 유지 필요

    // --- 히스테리시스 상태 ---
    private ThrottleLevel hysteresisLevel = ThrottleLevel.FULL;
    private int stabilityCounter = 0;
    private boolean hysteresisActive = false;

    // --- 멀티플레이어 캐시 ---
    private boolean isMultiplayer = false;
    private int lastMpCheckTick = -100;

    // --- 통계 ---
    private long fullCount = 0;
    private long reducedCount = 0;
    private long lowCount = 0;
    private long minimalCount = 0;
    private long engagedUpgradeCount = 0;
    private long panicOverrideCount = 0;
    private long guardOverrideCount = 0;
    private long cutoffCount = 0;

    // 텔레메트리
    private TelemetryReason lastReason = null;

    public FuseThrottleController() {
        System.out.println("[" + LOG + "] ThrottleController initialized (v1.1 with hysteresis)");
    }

    /**
     * v1.1: Governor/Panic 컴포넌트 설정.
     */
    public void setGovernor(TickBudgetGovernor governor) {
        this.governor = governor;
    }

    public void setPanicProtocol(SpikePanicProtocol panicProtocol) {
        this.panicProtocol = panicProtocol;
    }

    public void setStats(RollingTickStats stats) {
        this.stats = stats;
    }

    /**
     * v1.1: Guard 설정.
     */
    public void setGuards(VehicleGuard vehicleGuard, StreamingGuard streamingGuard) {
        this.vehicleGuard = vehicleGuard;
        this.streamingGuard = streamingGuard;
    }

    @Override
    public ThrottleLevel getThrottleLevel(float distSq, boolean isAttacking,
            boolean hasTarget, boolean recentlyEngaged) {

        // 0. Config 체크
        if (!FuseConfig.getInstance().isThrottlingEnabled()) {
            return ThrottleLevel.FULL;
        }

        // 1. Guard 체크 (차량/스트리밍)
        if (vehicleGuard != null && vehicleGuard.shouldPassive()) {
            guardOverrideCount++;
            lastReason = vehicleGuard.getLastReason();
            return ThrottleLevel.FULL; // 최소 개입
        }
        if (streamingGuard != null && streamingGuard.shouldYieldToStreaming()) {
            guardOverrideCount++;
            lastReason = streamingGuard.getLastReason();
            return ThrottleLevel.MINIMAL; // 예산 양보
        }

        // 2. Panic 체크
        if (panicProtocol != null && panicProtocol.getState() != SpikePanicProtocol.State.NORMAL) {
            panicOverrideCount++;
            lastReason = panicProtocol.getLastReason();

            // Panic/Recovering 배수 적용
            float multiplier = panicProtocol.getThrottleMultiplier();
            if (multiplier <= 0.2f) {
                return ThrottleLevel.MINIMAL; // 극도 축소
            } else if (multiplier <= 0.6f) {
                return ThrottleLevel.LOW;
            } else if (multiplier <= 0.8f) {
                return ThrottleLevel.REDUCED;
            }
            // 1.0 근처면 정상 계산으로
        }

        // 3. Governor 컷오프 체크
        if (governor != null && !governor.shouldContinueThisTick()) {
            cutoffCount++;
            lastReason = governor.getLastReason();
            return hysteresisLevel; // 현재 히스테리시스 레벨 유지
        }

        // 4. 즉시 FULL 승격 조건 (공격/타겟/최근 교전)
        if (isAttacking || hasTarget || recentlyEngaged) {
            fullCount++;
            if (recentlyEngaged && !isAttacking && !hasTarget) {
                engagedUpgradeCount++;
            }
            lastReason = null;
            return ThrottleLevel.FULL;
        }

        // 5. 거리 기반 Tiered 레벨 계산
        ThrottleLevel calculated = calculateDistanceLevel(distSq);

        // 6. 윈도우 기반 히스테리시스 적용
        ThrottleLevel final_ = applyHysteresis(calculated);

        // 통계 업데이트
        updateStats(final_);

        return final_;
    }

    /**
     * 거리 기반 ThrottleLevel 계산.
     */
    private ThrottleLevel calculateDistanceLevel(float distSq) {
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
     * 윈도우 통계 기반 히스테리시스 적용.
     */
    private ThrottleLevel applyHysteresis(ThrottleLevel newLevel) {
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
     * 더 보수적인 ThrottleLevel 반환.
     */
    private ThrottleLevel getMoreConservativeLevel(ThrottleLevel current) {
        return switch (current) {
            case FULL -> ThrottleLevel.REDUCED;
            case REDUCED -> ThrottleLevel.LOW;
            case LOW, MINIMAL -> ThrottleLevel.MINIMAL;
        };
    }

    /**
     * 통계 업데이트.
     */
    private void updateStats(ThrottleLevel level) {
        switch (level) {
            case FULL -> fullCount++;
            case REDUCED -> reducedCount++;
            case LOW -> lowCount++;
            case MINIMAL -> minimalCount++;
        }
    }

    // --- Legacy ---

    /**
     * @deprecated Tiered 방식으로 전환됨. 하위 호환용.
     */
    @Deprecated
    @SuppressWarnings("unused")
    private int getIntervalMask(float distSq) {
        FuseConfig config = FuseConfig.getInstance();
        if (distSq < config.getNearDistSq())
            return 0;
        if (distSq < config.getMediumDistSq())
            return 1;
        if (distSq < config.getFarDistSq())
            return 3;
        return 7;
    }

    @SuppressWarnings("unused")
    private boolean checkMultiplayer(int currentTick) {
        if (currentTick - lastMpCheckTick < 100) {
            return isMultiplayer;
        }
        lastMpCheckTick = currentTick;
        try {
            Class<?> gc = Class.forName("zombie.network.GameClient");
            isMultiplayer = (boolean) gc.getField("bClient").get(null);
        } catch (Throwable t) {
            isMultiplayer = false;
        }
        return isMultiplayer;
    }

    // --- Stats ---

    public long getFullCount() {
        return fullCount;
    }

    public long getReducedCount() {
        return reducedCount;
    }

    public long getLowCount() {
        return lowCount;
    }

    public long getMinimalCount() {
        return minimalCount;
    }

    public long getEngagedUpgradeCount() {
        return engagedUpgradeCount;
    }

    public long getPanicOverrideCount() {
        return panicOverrideCount;
    }

    public long getGuardOverrideCount() {
        return guardOverrideCount;
    }

    public long getCutoffCount() {
        return cutoffCount;
    }

    public long getTotalCount() {
        return fullCount + reducedCount + lowCount + minimalCount;
    }

    public TelemetryReason getLastReason() {
        return lastReason;
    }

    public boolean isHysteresisActive() {
        return hysteresisActive;
    }

    public void resetStats() {
        fullCount = 0;
        reducedCount = 0;
        lowCount = 0;
        minimalCount = 0;
        engagedUpgradeCount = 0;
        panicOverrideCount = 0;
        guardOverrideCount = 0;
        cutoffCount = 0;
        stabilityCounter = 0;
        hysteresisActive = false;
        hysteresisLevel = ThrottleLevel.FULL;
    }

    public void printStatus() {
        long total = getTotalCount();
        System.out.println("[" + LOG + "] Throttle Controller Status (v1.1):");
        System.out.println("  FULL: " + fullCount + " (" + pct(fullCount, total) + "%)");
        System.out.println("  REDUCED: " + reducedCount + " (" + pct(reducedCount, total) + "%)");
        System.out.println("  LOW: " + lowCount + " (" + pct(lowCount, total) + "%)");
        System.out.println("  MINIMAL: " + minimalCount + " (" + pct(minimalCount, total) + "%)");
        System.out.println("  ---");
        System.out.println("  EngagedUpgrade: " + engagedUpgradeCount);
        System.out.println("  PanicOverride: " + panicOverrideCount);
        System.out.println("  GuardOverride: " + guardOverrideCount);
        System.out.println("  CutoffCount: " + cutoffCount);
        System.out.println("  ---");
        System.out.println("  HysteresisActive: " + hysteresisActive);
        System.out.println("  HysteresisLevel: " + hysteresisLevel);
        System.out.println("  StabilityCounter: " + stabilityCounter + "/" + EXIT_STABILITY_TICKS);
    }

    private String pct(long count, long total) {
        return total == 0 ? "0.0" : String.format("%.1f", (count * 100.0) / total);
    }
}
