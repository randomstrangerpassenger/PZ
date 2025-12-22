package com.fuse.governor;

import com.fuse.telemetry.TelemetryReason;

/**
 * Tick Budget Governor.
 * 
 * ZombieUpdate 계열 작업에 틱당 시간 상한을 부여합니다.
 * 컷오프 스위치 방식: 예산 초과 시 남은 작업은 다음 틱에서 자연스럽게 처리됩니다.
 * Batch Check로 System.nanoTime() 호출 비용을 최소화합니다.
 * 
 * @since Fuse 1.1
 */
public class TickBudgetGovernor {

    private static final String LOG = "Fuse";

    // --- 설정값 ---
    private double budgetMs = 16.67; // 60fps 유지선
    private double forceCutoffMs = 33.33; // 30fps 방어선
    private int batchCheckSize = 20; // N마리마다 시간 체크

    // --- 상태 ---
    private long tickStartNanos = -1;
    private int zombiesProcessedThisTick = 0;
    private double lastTickMs = 0.0;
    private boolean cutoffTriggered = false;

    // --- 통계 ---
    private long totalCutoffs = 0;
    private long totalTicks = 0;

    // 텔레메트리
    private TelemetryReason lastReason = null;

    public TickBudgetGovernor() {
        System.out.println("[" + LOG + "] TickBudgetGovernor initialized (budget: "
                + budgetMs + "ms, cutoff: " + forceCutoffMs + "ms, batch: " + batchCheckSize + ")");
    }

    /**
     * 틱 시작 시 호출.
     */
    public void beginTick() {
        tickStartNanos = System.nanoTime();
        zombiesProcessedThisTick = 0;
        cutoffTriggered = false;
        lastReason = null;
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
    }

    /**
     * 컷오프 스위치 - 이번 틱 계속 처리 가능 여부.
     * 
     * Batch Check: batchCheckSize마다만 시간 체크하여 nanoTime() 호출 비용 최소화.
     * 
     * @return true면 계속 처리, false면 이번 틱 종료 (남은 작업은 다음 틱에서)
     */
    public boolean shouldContinueThisTick() {
        zombiesProcessedThisTick++;

        // Batch Check: N마리마다만 시간 체크
        if (zombiesProcessedThisTick % batchCheckSize != 0) {
            return !cutoffTriggered; // 이미 컷오프됐으면 false
        }

        // 시간 체크
        double elapsedMs = getElapsedMs();
        if (elapsedMs >= forceCutoffMs) {
            if (!cutoffTriggered) {
                cutoffTriggered = true;
                totalCutoffs++;
                lastReason = TelemetryReason.GOVERNOR_CUTOFF;
                // 과도한 로깅 방지: 100번마다 한 번만 로그
                if (totalCutoffs % 100 == 1) {
                    System.out.println("[" + LOG + "] Governor cutoff triggered at "
                            + String.format("%.2f", elapsedMs) + "ms (total: " + totalCutoffs + ")");
                }
            }
            return false;
        }

        return true;
    }

    /**
     * 현재 경과 시간 (ms).
     */
    public double getElapsedMs() {
        if (tickStartNanos < 0) {
            return 0.0;
        }
        return (System.nanoTime() - tickStartNanos) / 1_000_000.0;
    }

    /**
     * 마지막 틱 소요 시간 (ms).
     */
    public double getLastTickMs() {
        return lastTickMs;
    }

    /**
     * 이번 틱에서 처리된 좀비 수.
     */
    public int getZombiesProcessedThisTick() {
        return zombiesProcessedThisTick;
    }

    /**
     * 이번 틱에서 컷오프가 발생했는지.
     */
    public boolean wasCutoffTriggered() {
        return cutoffTriggered;
    }

    /**
     * 마지막 텔레메트리 이유.
     */
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
        System.out.println("[" + LOG + "] Governor Status:");
        System.out.println("  Budget: " + budgetMs + "ms");
        System.out.println("  Force Cutoff: " + forceCutoffMs + "ms");
        System.out.println("  Batch Check Size: " + batchCheckSize);
        System.out.println("  Total Ticks: " + totalTicks);
        System.out.println("  Total Cutoffs: " + totalCutoffs + " ("
                + String.format("%.2f", getCutoffRatio() * 100) + "%)");
        System.out.println("  Last Tick: " + String.format("%.2f", lastTickMs) + "ms");
    }
}
