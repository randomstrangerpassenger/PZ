package com.fuse.area7.governor;

import com.fuse.area7.PathfindingInvariants;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.spi.IPathfindingContext;

/**
 * 틱당 경로탐색 예산 관리자.
 * 
 * <p>
 * 3/3 모델 완전 합의: 틱당 경로탐색 요청 수 제한.
 * </p>
 * 
 * <h2>매커니즘</h2>
 * <ul>
 * <li>틱 시작 시 예산 리셋</li>
 * <li>COMBAT 우선순위는 무조건 허용</li>
 * <li>예산 내 요청은 허용 + 예산 차감</li>
 * <li>예산 초과 시 DeferQueue로 이월</li>
 * </ul>
 * 
 * <h2>헌법 준수</h2>
 * <ul>
 * <li>경로 "건너뛰기" ❌ → "지연" ✅</li>
 * <li>결과 동일, 시간만 분산</li>
 * </ul>
 * 
 * @since Fuse 2.2
 */
public class PathfindingBudgetGovernor {

    private static final String LOG = "Fuse";

    private final PathRequestDeferQueue deferQueue;

    private int budgetPerTick;
    private int remainingBudget;
    private long currentTick;
    private boolean conservativeMode;

    // 텔레메트리
    private int totalRequests;
    private int deferredRequests;
    private int combatBypassCount;

    public PathfindingBudgetGovernor(PathRequestDeferQueue deferQueue) {
        this.deferQueue = deferQueue;
        this.budgetPerTick = PathfindingInvariants.DEFAULT_BUDGET_PER_TICK;
        this.remainingBudget = budgetPerTick;
        this.currentTick = -1;
        this.conservativeMode = false;
    }

    /**
     * 틱 시작 시 호출.
     * 예산 리셋 + 지연 큐 처리.
     */
    public void onTickStart(long gameTick) {
        this.currentTick = gameTick;

        // 보수 모드 시 예산 감소
        if (conservativeMode) {
            this.remainingBudget = (int) (budgetPerTick * 0.5);
        } else {
            this.remainingBudget = budgetPerTick;
        }

        // 지연 큐의 이전 틱 요청 처리 (예산에서 차감)
        deferQueue.processDeferred(gameTick, this::consumeBudget);
    }

    /**
     * 경로탐색 요청 검사.
     * 
     * @param context 경로탐색 컨텍스트
     * @return true = 즉시 처리, false = 지연됨
     */
    public boolean checkRequest(IPathfindingContext context) {
        totalRequests++;

        // COMBAT은 무조건 허용 (안전 보장)
        if (context.getEngineAssignedPriority() >= PathfindingInvariants.PRIORITY_COMBAT
                || context.isInCombatState()) {
            combatBypassCount++;
            consumeBudget();
            return true;
        }

        // 근거리는 우선 처리
        if (context.getDistanceSquared() < PathfindingInvariants.NEAR_DIST_SQ) {
            if (remainingBudget > 0) {
                consumeBudget();
                return true;
            }
        }

        // 예산 검사
        if (remainingBudget > 0) {
            consumeBudget();
            return true;
        }

        // 예산 초과 → 지연
        context.setDeferred(true);
        deferQueue.enqueue(new DeferredPathRequest(
                context.getZombieId(),
                context.getEngineAssignedPriority(),
                context.getDistanceSquared(),
                context.getTargetX(),
                context.getTargetY(),
                currentTick));
        deferredRequests++;

        return false;
    }

    /**
     * 예산 소비.
     */
    private void consumeBudget() {
        if (remainingBudget > 0) {
            remainingBudget--;
        }
    }

    /**
     * 보수 모드 설정 (PanicProtocol에서 호출).
     */
    public void setConservativeMode(boolean conservative) {
        this.conservativeMode = conservative;
        if (conservative) {
            PulseLogger.info(LOG, "[Governor] Conservative mode enabled");
        }
    }

    /**
     * 틱당 예산 설정.
     */
    public void setBudgetPerTick(int budget) {
        this.budgetPerTick = budget;
    }

    // ═══════════════════════════════════════════════════════════════
    // 텔레메트리
    // ═══════════════════════════════════════════════════════════════

    public int getTotalRequests() {
        return totalRequests;
    }

    public int getDeferredRequests() {
        return deferredRequests;
    }

    public int getCombatBypassCount() {
        return combatBypassCount;
    }

    public int getRemainingBudget() {
        return remainingBudget;
    }

    public void resetTelemetry() {
        totalRequests = 0;
        deferredRequests = 0;
        combatBypassCount = 0;
    }
}
