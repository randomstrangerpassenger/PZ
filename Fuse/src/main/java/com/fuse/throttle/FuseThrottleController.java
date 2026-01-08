package com.fuse.throttle;

import com.fuse.config.FuseConfig;
import com.fuse.governor.AdaptiveGate;
import com.fuse.governor.RollingTickStats;
import com.fuse.governor.SpikePanicProtocol;
import com.fuse.governor.TickBudgetGovernor;
import com.fuse.guard.StreamingGuard;
import com.fuse.guard.VehicleGuard;
import com.fuse.telemetry.ReasonStats;
import com.fuse.telemetry.TelemetryReason;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.IHookContext;
import com.pulse.api.profiler.IThrottlePolicy;

import java.util.EnumMap;
import java.util.Map;

/**
 * Tiered 거리 기반 좀비 업데이트 throttling (v2.3).
 * 히스테리시스 + Governor/Panic 연동.
 */
public class FuseThrottleController implements IThrottlePolicy {

    private static final String LOG = "Fuse";

    /** 압력의 원인 */
    public enum InterventionCause {
        TICK_SPIKE
    }

    /** 개입 차단 사유 */
    public enum InterventionBlocker {
        THRESHOLD_NOT_MET,
        NON_SLICEABLE,
        FAILOPEN_SAFETY,
        GUARD_DISABLED
    }

    // EnumMap 집계 (v2.2)
    private final EnumMap<InterventionCause, Integer> noInterventionByCause = new EnumMap<>(InterventionCause.class);
    private final EnumMap<InterventionBlocker, Integer> noInterventionByBlocker = new EnumMap<>(
            InterventionBlocker.class);
    private int noInterventionCountThisWindow = 0;

    // --- v1.1 컴포넌트 ---
    private TickBudgetGovernor governor;
    private SpikePanicProtocol panicProtocol;
    private RollingTickStats stats;
    private VehicleGuard vehicleGuard;
    private StreamingGuard streamingGuard;
    private ReasonStats reasonStats;

    // --- v2.5 AdaptiveGate ---
    private AdaptiveGate adaptiveGate;

    // --- 히스테리시스 설정 (윈도우 통계 기반) ---
    private static final double ENTRY_MAX_1S_MS = 33.33; // 진입: 1초 내 max > 33.33ms
    private static final double ENTRY_AVG_5S_MS = 20.0; // 또는: 5초 avg > 20ms
    private static final double EXIT_AVG_5S_MS = 12.0; // 복구: 5초 avg < 12ms
    private static final int EXIT_STABILITY_TICKS = 300; // 5초 유지 필요

    // --- 히스테리시스 상태 ---
    private ThrottleLevel hysteresisLevel = ThrottleLevel.FULL;
    private int stabilityCounter = 0;
    private boolean hysteresisActive = false;

    // --- 통계 ---
    private long fullCount = 0;
    private long reducedCount = 0;
    private long lowCount = 0;
    private long minimalCount = 0;
    private long engagedUpgradeCount = 0;
    private long panicOverrideCount = 0;
    private long guardOverrideCount = 0;
    // ioGuardOverrideCount, gcPressureOverrideCount removed in v2.3
    private long cutoffCount = 0;

    // 텔레메트리
    private TelemetryReason lastReason = null;

    public FuseThrottleController() {
        // EnumMap 초기화
        for (InterventionCause c : InterventionCause.values()) {
            noInterventionByCause.put(c, 0);
        }
        for (InterventionBlocker b : InterventionBlocker.values()) {
            noInterventionByBlocker.put(b, 0);
        }
        PulseLogger.info(LOG, "ThrottleController initialized (v2.3 - IO/GC guards removed)");
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

    /**
     * v1.1: ReasonStats 설정.
     */
    public void setReasonStats(ReasonStats reasonStats) {
        this.reasonStats = reasonStats;
    }

    /**
     * v2.5: AdaptiveGate 설정.
     */
    public void setAdaptiveGate(AdaptiveGate adaptiveGate) {
        this.adaptiveGate = adaptiveGate;
    }

    // setIOGuard(), setGCPressureGuard() removed in v2.3

    // =================================================================
    // IThrottlePolicy 구현
    // =================================================================

    /**
     * 좀비 처리 여부 결정.
     * 
     * v2.5: AdaptiveGate Fast-Path 추가
     * - PASSTHROUGH: 즉시 true 반환 (제로 오버헤드)
     * - ACTIVE + canIntervene(): 기존 로직 (측정됨)
     * - ACTIVE + !canIntervene(): true 반환 (예산 초과)
     * 
     * @param context 훅 컨텍스트 (target = 좀비 객체)
     * @return true면 처리, false면 스킵
     */
    @Override
    public boolean shouldProcess(IHookContext context) {
        // ═══════════════════════════════════════════════════════
        // v2.5: Adaptive Gate Fast Path
        // PASSTHROUGH 상태: 즉시 true 반환 (제로 오버헤드)
        // ⚠️ 이 블록 내에서 로깅 절대 금지!
        // ═══════════════════════════════════════════════════════
        if (adaptiveGate != null && adaptiveGate.isPassthrough()) {
            return true;
        }

        // ═══════════════════════════════════════════════════════
        // ACTIVE 상태: Governor 예산 내에서만 개입
        // ═══════════════════════════════════════════════════════
        if (governor != null && !governor.canIntervene()) {
            return true; // 예산 초과 시 개입 중단 (바닐라처럼 처리)
        }

        // Fail-open: context가 없거나 target이 없으면 처리
        if (context == null || context.getTarget() == null) {
            return true;
        }

        // 개입 비용 측정 시작
        if (governor != null) {
            governor.beginIntervention();
        }

        try {
            Object target = context.getTarget();

            // ZombieReflectionHelper를 통해 거리 및 상태 조회 (리플렉션 기반)
            float distSq = ZombieReflectionHelper.getDistanceSquaredToPlayer(target);
            boolean isAttacking = ZombieReflectionHelper.isAttacking(target);
            boolean hasTarget = ZombieReflectionHelper.hasTarget(target);

            // 핵심: 반드시 getThrottleLevel() 호출하여 통계 갱신
            ThrottleLevel level = getThrottleLevel(distSq, isAttacking, hasTarget, false);

            // MINIMAL이면 스킵 (shouldProcess = false)
            return level != ThrottleLevel.MINIMAL;

        } finally {
            // 개입 비용 측정 종료
            if (governor != null) {
                governor.endIntervention();
            }
        }
    }

    @Override
    public int getAllowedBudget(IHookContext context) {
        // 현재 히스테리시스 레벨 기반 예산 반환
        return hysteresisLevel.budget;
    }

    // =================================================================
    // 내부 ThrottleLevel API (Fuse 전용)
    // =================================================================

    /**
     * 좀비 스로틀 레벨 계산 (내부 API).
     */
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
            recordReason(lastReason);
            return ThrottleLevel.FULL; // 최소 개입
        }
        if (streamingGuard != null && streamingGuard.shouldYieldToStreaming()) {
            guardOverrideCount++;
            lastReason = streamingGuard.getLastReason();
            recordReason(lastReason);
            return ThrottleLevel.MINIMAL; // 예산 양보
        }

        // 1.5/1.6 IOGuard/GCPressureGuard checks removed in v2.3

        // 2. Panic 체크
        float panicMultiplier = 1.0f;
        if (panicProtocol != null && panicProtocol.getState() != SpikePanicProtocol.State.NORMAL) {
            panicOverrideCount++;
            lastReason = panicProtocol.getLastReason();
            recordReason(lastReason);
            panicMultiplier = panicProtocol.getThrottleMultiplier();
        }

        // 2.5 Panic multiplier로 ThrottleLevel 결정 (v2.3 simplified)
        float combinedMultiplier = panicMultiplier;
        combinedMultiplier = Math.max(0.10f, combinedMultiplier); // 하한선

        // Min 합성 결과로 ThrottleLevel 결정
        if (combinedMultiplier <= 0.2f) {
            return ThrottleLevel.MINIMAL;
        } else if (combinedMultiplier <= 0.5f) {
            return ThrottleLevel.LOW;
        } else if (combinedMultiplier <= 0.8f) {
            // 다음 단계로 진행 (거리 기반 계산)
        } else {
            // combinedMultiplier > 0.8f: 정상 계산으로
        }

        // 3. Governor 컷오프 체크
        if (governor != null && !governor.shouldContinueThisTick()) {
            cutoffCount++;
            lastReason = governor.getLastReason();
            recordReason(lastReason);
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
     * 더 보수적인 ThrottleLevel 반환.
     */
    private ThrottleLevel getMoreConservativeLevel(ThrottleLevel current) {
        return switch (current) {
            case FULL -> ThrottleLevel.REDUCED;
            case REDUCED -> ThrottleLevel.LOW;
            case LOW, MINIMAL -> ThrottleLevel.MINIMAL;
        };
    }

    private void updateStats(ThrottleLevel level) {
        switch (level) {
            case FULL -> fullCount++;
            case REDUCED -> reducedCount++;
            case LOW -> lowCount++;
            case MINIMAL -> minimalCount++;
        }
    }

    /**
     * ReasonStats에 개입 이유 기록.
     */
    private void recordReason(TelemetryReason reason) {
        if (reasonStats != null && reason != null) {
            reasonStats.increment(reason);
        }
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

    /**
     * 현재 히스테리시스 레벨 반환 (Step 동기화용).
     */
    public ThrottleLevel getCurrentLevel() {
        return hysteresisLevel;
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
        PulseLogger.info(LOG, "Throttle Controller Status (v2.3):");
        PulseLogger.info(LOG, "  FULL: " + fullCount + " (" + pct(fullCount, total) + "%)");
        PulseLogger.info(LOG, "  REDUCED: " + reducedCount + " (" + pct(reducedCount, total) + "%)");
        PulseLogger.info(LOG, "  LOW: " + lowCount + " (" + pct(lowCount, total) + "%)");
        PulseLogger.info(LOG, "  MINIMAL: " + minimalCount + " (" + pct(minimalCount, total) + "%)");
        PulseLogger.info(LOG, "  ---");
        PulseLogger.info(LOG, "  EngagedUpgrade: " + engagedUpgradeCount);
        PulseLogger.info(LOG, "  PanicOverride: " + panicOverrideCount);
        PulseLogger.info(LOG, "  GuardOverride: " + guardOverrideCount);
        // IOGuardOverride, GCPressureOverride removed in v2.3
        PulseLogger.info(LOG, "  CutoffCount: " + cutoffCount);
        PulseLogger.info(LOG, "  ---");
        PulseLogger.info(LOG, "  HysteresisActive: " + hysteresisActive);
        PulseLogger.info(LOG, "  HysteresisLevel: " + hysteresisLevel);
        PulseLogger.info(LOG, "  StabilityCounter: " + stabilityCounter + "/" + EXIT_STABILITY_TICKS);
    }

    private String pct(long count, long total) {
        return total == 0 ? "0.0" : String.format("%.1f", (count * 100.0) / total);
    }

    // =================================================================
    // NO_INTERVENTION 추적 API (v2.2)
    // =================================================================

    /**
     * 압력 감지되었으나 개입하지 않음을 기록.
     * 
     * @param cause   압력 원인
     * @param blocker 차단 사유
     */
    public void logNoIntervention(InterventionCause cause, InterventionBlocker blocker) {
        noInterventionByCause.merge(cause, 1, Integer::sum);
        noInterventionByBlocker.merge(blocker, 1, Integer::sum);
        noInterventionCountThisWindow++;
        PulseLogger.debug(LOG, "PRESSURE_DETECTED cause={} blocker={}", cause, blocker);
    }

    /**
     * 60초 요약용: cause별 미개입 카운트.
     */
    public Map<InterventionCause, Integer> getNoInterventionByCause() {
        return new EnumMap<>(noInterventionByCause);
    }

    /**
     * 60초 요약용: blocker별 미개입 카운트.
     */
    public Map<InterventionBlocker, Integer> getNoInterventionByBlocker() {
        return new EnumMap<>(noInterventionByBlocker);
    }

    /**
     * 60초 요약용: 이번 윈도우 총 미개입 횟수.
     */
    public int getNoInterventionCountThisWindow() {
        return noInterventionCountThisWindow;
    }

    /**
     * 60초 요약 후 미개입 메트릭 리셋.
     */
    public void resetNoInterventionMetrics() {
        for (InterventionCause c : InterventionCause.values()) {
            noInterventionByCause.put(c, 0);
        }
        for (InterventionBlocker b : InterventionBlocker.values()) {
            noInterventionByBlocker.put(b, 0);
        }
        noInterventionCountThisWindow = 0;
    }
}
