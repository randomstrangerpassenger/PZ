package com.pulse.api.lua;

import com.pulse.api.PublicAPI;

/**
 * Lua 실행 컨텍스트.
 * try-with-resources 패턴을 지원하여 자동으로 budget 정산.
 * 
 * <pre>
 * // 사용 예시
 * LuaBudgetManager budget = LuaBudgetManager.getInstance();
 * 
 * try (LuaExecutionContext ctx = budget.beginExecution("mymod.update")) {
 *     while (ctx.hasRemainingBudget()) {
 *         doSomeLuaWork();
 *         ctx.checkpoint(); // 중간 체크
 *     }
 * } // 자동으로 정산됨
 * </pre>
 * 
 * @since 1.0.1
 */
@PublicAPI(since = "1.0.1", status = PublicAPI.Status.EXPERIMENTAL)
public final class LuaExecutionContext implements AutoCloseable {

    private final String contextId;
    private final long budgetMicros;
    private final long startNanos;
    private final LuaBudgetManager manager;

    private volatile long lastCheckpointNanos;
    private volatile int checkpointCount = 0;
    private volatile boolean closed = false;

    /**
     * 컨텍스트 생성 (LuaBudgetManager 내부용).
     */
    LuaExecutionContext(String contextId, long budgetMicros, LuaBudgetManager manager) {
        this.contextId = contextId;
        this.budgetMicros = budgetMicros;
        this.manager = manager;
        this.startNanos = System.nanoTime();
        this.lastCheckpointNanos = startNanos;
    }

    /**
     * 컨텍스트 ID 반환.
     */
    public String getContextId() {
        return contextId;
    }

    /**
     * 설정된 Budget 반환 (마이크로초).
     */
    public long getBudgetMicros() {
        return budgetMicros;
    }

    /**
     * 경과 시간 반환 (마이크로초).
     */
    public long getElapsedMicros() {
        return (System.nanoTime() - startNanos) / 1000;
    }

    /**
     * 남은 Budget 반환 (마이크로초).
     * 음수면 이미 초과됨.
     */
    public long getRemainingMicros() {
        return budgetMicros - getElapsedMicros();
    }

    /**
     * 남은 Budget이 있는지 확인.
     * 
     * @return Budget이 남아있으면 true
     */
    public boolean hasRemainingBudget() {
        return getRemainingMicros() > 0;
    }

    /**
     * Budget 초과 여부 확인.
     * 
     * @return 초과했으면 true
     */
    public boolean isOverBudget() {
        return getRemainingMicros() < 0;
    }

    /**
     * 중간 체크포인트.
     * 긴 작업 중간에 호출하여 budget 상태 업데이트.
     * 
     * @return 남은 budget이 있으면 true
     */
    public boolean checkpoint() {
        lastCheckpointNanos = System.nanoTime();
        checkpointCount++;
        return hasRemainingBudget();
    }

    /**
     * 마지막 체크포인트 이후 경과 시간 (마이크로초).
     */
    public long getMicrosSinceLastCheckpoint() {
        return (System.nanoTime() - lastCheckpointNanos) / 1000;
    }

    /**
     * 체크포인트 호출 횟수.
     */
    public int getCheckpointCount() {
        return checkpointCount;
    }

    /**
     * 컨텍스트가 아직 활성 상태인지 확인.
     */
    public boolean isActive() {
        return !closed;
    }

    /**
     * 특정 작업에 필요한 budget이 남아있는지 확인.
     * 
     * @param requiredMicros 필요한 시간 (마이크로초)
     * @return 충분한 budget이 있으면 true
     */
    public boolean hasBudgetFor(long requiredMicros) {
        return getRemainingMicros() >= requiredMicros;
    }

    /**
     * Budget의 X% 이상 남았는지 확인.
     * 
     * @param percentRemaining 남아야 할 비율 (0.0 ~ 1.0)
     * @return 충분히 남았으면 true
     */
    public boolean hasPercentRemaining(double percentRemaining) {
        long required = (long) (budgetMicros * percentRemaining);
        return getRemainingMicros() >= required;
    }

    /**
     * 경과 시간의 비율 (0.0 ~ 1.0+).
     * 1.0 이상이면 budget 초과.
     */
    public double getElapsedRatio() {
        return (double) getElapsedMicros() / budgetMicros;
    }

    /**
     * 컨텍스트 종료.
     * AutoCloseable 구현으로 try-with-resources 지원.
     */
    @Override
    public void close() {
        if (!closed) {
            closed = true;
            manager.endExecution(this);
        }
    }

    @Override
    public String toString() {
        return String.format("LuaExecutionContext[%s, elapsed=%.2fms/%.2fms, remaining=%.2fms]",
                contextId,
                getElapsedMicros() / 1000.0,
                budgetMicros / 1000.0,
                getRemainingMicros() / 1000.0);
    }
}
