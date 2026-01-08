package com.fuse.governor;

import com.fuse.telemetry.ReasonStats;
import com.fuse.telemetry.TelemetryReason;
import com.pulse.api.log.PulseLogger;

/**
 * Tick Budget Governor - 틱당 시간 상한 관리 (v2.6 Bundle C).
 * 예산 초과 시 컷오프, Batch Check로 nanoTime() 비용 최소화.
 * 
 * Bundle C: HardLimitObserver 패턴으로 AdaptiveGate에 hard limit 이벤트 통지.
 * 
 * @since Fuse 1.0.0
 * @since Fuse 2.6.0 - Bundle C: HardLimitObserver
 */
public class TickBudgetGovernor {

    private static final String LOG = "Fuse";

    // ═══════════════════════════════════════════════════════════════
    // Bundle C: HardLimitObserver 인터페이스 (순환 참조 방지)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Hard limit 이벤트 관측자.
     * AdaptiveGate가 구현하여 streak 카운팅에 사용.
     */
    public interface HardLimitObserver {
        void onHardLimitHit();

        void onHardLimitMiss();
    }

    // --- 설정값 ---
    private double budgetMs = 16.67;
    private double forceCutoffMs = 33.33;
    private int batchCheckSize = 20;

    // --- Fuse 오버헤드 예산 (v2.5) ---
    private static final double SOFT_LIMIT_MS = 0.5;
    private static final double HARD_LIMIT_MS = 2.0;

    // --- 상태 ---
    private long tickStartNanos = -1;
    private int zombiesProcessedThisTick = 0;
    private double lastTickMs = 0.0;
    private boolean cutoffTriggered = false;

    // --- Fuse 오버헤드 측정 (v2.5) ---
    private double fuseConsumedMs = 0.0;
    private long interventionStartNanos = 0;
    private boolean softLimitWarned = false;

    // --- Bundle C: 3점 봉인 플래그 (봉인#1) ---
    private boolean hardLimitHitThisTick = false;
    private HardLimitObserver observer;

    // --- 통계 ---
    private long totalCutoffs = 0;
    private long totalTicks = 0;
    private long softLimitHits = 0;
    private long hardLimitHits = 0;

    // 텔레메트리
    private TelemetryReason lastReason = null;
    private ReasonStats reasonStats;

    public TickBudgetGovernor() {
        PulseLogger.info(LOG, "TickBudgetGovernor initialized (budget: "
                + budgetMs + "ms, cutoff: " + forceCutoffMs + "ms, batch: " + batchCheckSize + ")");
    }

    // ═══════════════════════════════════════════════════════════════
    // Bundle C: Observer 설정
    // ═══════════════════════════════════════════════════════════════

    public void setHardLimitObserver(HardLimitObserver observer) {
        this.observer = observer;
    }

    // ═══════════════════════════════════════════════════════════════
    // 틱 라이프사이클
    // ═══════════════════════════════════════════════════════════════

    /**
     * 틱 시작 시 호출.
     */
    public void beginTick() {
        tickStartNanos = System.nanoTime();
        zombiesProcessedThisTick = 0;
        cutoffTriggered = false;
        lastReason = null;
        // v2.5: 오버헤드 측정 리셋
        fuseConsumedMs = 0.0;
        softLimitWarned = false;
        // Bundle C: 3점 봉인 1) 리셋
        hardLimitHitThisTick = false;
    }

    /**
     * 틱 종료 시 호출.
     */
    public void endTick() {
        if (tickStartNanos > 0) {
            lastTickMs = (System.nanoTime() - tickStartNanos) / 1_000_000.0;
            totalTicks++;
        }
        tickStartNanos = -1;

        // Bundle C: 3점 봉인 3) 조건부 miss 통지
        if (!hardLimitHitThisTick && observer != null) {
            observer.onHardLimitMiss();
        }
        // 재정리 (다음 틱 대비)
        hardLimitHitThisTick = false;
    }

    /**
     * ReasonStats 연동 (v2.5).
     */
    public void setReasonStats(ReasonStats reasonStats) {
        this.reasonStats = reasonStats;
    }

    // ═══════════════════════════════════════════════════════════════
    // 개입 측정
    // ═══════════════════════════════════════════════════════════════

    /**
     * Fuse 개입 시작 전 호출 - 타이머 시작.
     */
    public void beginIntervention() {
        interventionStartNanos = System.nanoTime();
    }

    /**
     * Fuse 개입 종료 후 호출 - 비용 자동 기록.
     */
    public void endIntervention() {
        if (interventionStartNanos > 0) {
            long elapsed = System.nanoTime() - interventionStartNanos;
            fuseConsumedMs += elapsed / 1_000_000.0;
            interventionStartNanos = 0;
        }
    }

    /**
     * Fuse 개입 가능 여부 (단계적 상한).
     */
    public boolean canIntervene() {
        // Hard limit 초과 시 강제 중단
        if (fuseConsumedMs >= HARD_LIMIT_MS) {
            if (reasonStats != null) {
                reasonStats.increment(TelemetryReason.BUDGET_HARD_LIMIT);
            }
            hardLimitHits++;
            // Bundle C: 3점 봉인 2) 세팅 + Observer 통지
            hardLimitHitThisTick = true;
            if (observer != null) {
                observer.onHardLimitHit();
            }
            return false;
        }

        // Soft limit 초과 시 경고 (1회만)
        if (fuseConsumedMs >= SOFT_LIMIT_MS && !softLimitWarned) {
            if (reasonStats != null) {
                reasonStats.increment(TelemetryReason.BUDGET_SOFT_LIMIT);
            }
            softLimitWarned = true;
            softLimitHits++;
        }

        return true;
    }

    /**
     * 현재 Fuse 오버헤드 소비량.
     */
    public double getFuseConsumedMs() {
        return fuseConsumedMs;
    }

    // ═══════════════════════════════════════════════════════════════
    // 컷오프 로직
    // ═══════════════════════════════════════════════════════════════

    /**
     * 컷오프 스위치 - Batch Check로 N마리마다 시간 체크.
     */
    public boolean shouldContinueThisTick() {
        zombiesProcessedThisTick++;

        if (zombiesProcessedThisTick % batchCheckSize != 0) {
            return !cutoffTriggered;
        }

        double elapsedMs = getElapsedMs();
        if (elapsedMs >= forceCutoffMs) {
            if (!cutoffTriggered) {
                cutoffTriggered = true;
                totalCutoffs++;
                lastReason = TelemetryReason.GOVERNOR_CUTOFF;
                if (totalCutoffs % 100 == 1) {
                    PulseLogger.debug(LOG, "Governor cutoff triggered at "
                            + String.format("%.2f", elapsedMs) + "ms (total: " + totalCutoffs + ")");
                }
            }
            return false;
        }

        return true;
    }

    public double getElapsedMs() {
        if (tickStartNanos < 0) {
            return 0.0;
        }
        return (System.nanoTime() - tickStartNanos) / 1_000_000.0;
    }

    public double getLastTickMs() {
        return lastTickMs;
    }

    public int getZombiesProcessedThisTick() {
        return zombiesProcessedThisTick;
    }

    public boolean wasCutoffTriggered() {
        return cutoffTriggered;
    }

    public TelemetryReason getLastReason() {
        return lastReason;
    }

    // --- 통계 ---

    public long getTotalCutoffs() {
        return totalCutoffs;
    }

    public long getTotalTicks() {
        return totalTicks;
    }

    public double getCutoffRatio() {
        return totalTicks == 0 ? 0.0 : (double) totalCutoffs / totalTicks;
    }

    public void resetStats() {
        totalCutoffs = 0;
        totalTicks = 0;
    }

    // --- 설정 ---

    public void setBudgetMs(double budgetMs) {
        this.budgetMs = budgetMs;
    }

    public void setForceCutoffMs(double forceCutoffMs) {
        this.forceCutoffMs = forceCutoffMs;
    }

    public void setBatchCheckSize(int batchCheckSize) {
        this.batchCheckSize = Math.max(1, batchCheckSize);
    }

    public void printStatus() {
        PulseLogger.info(LOG, "Governor Status:");
        PulseLogger.info(LOG, "  Budget: " + budgetMs + "ms");
        PulseLogger.info(LOG, "  Force Cutoff: " + forceCutoffMs + "ms");
        PulseLogger.info(LOG, "  Batch Check Size: " + batchCheckSize);
        PulseLogger.info(LOG, "  Total Ticks: " + totalTicks);
        PulseLogger.info(LOG, "  Total Cutoffs: " + totalCutoffs + " ("
                + String.format("%.2f", getCutoffRatio() * 100) + "%)");
        PulseLogger.info(LOG, "  Last Tick: " + String.format("%.2f", lastTickMs) + "ms");
        PulseLogger.info(LOG, "  Fuse Overhead Limit: soft=" + SOFT_LIMIT_MS + "ms, hard=" + HARD_LIMIT_MS + "ms");
        PulseLogger.info(LOG, "  Soft Limit Hits: " + softLimitHits);
        PulseLogger.info(LOG, "  Hard Limit Hits: " + hardLimitHits);
    }
}
