package com.pulse.handler;

/**
 * Tick 시작 결과 DTO.
 * 
 * <p>
 * WorldTickHandler.onUpdateStart() 메서드의 결과를 담습니다.
 * Mixin에서 이벤트 발행 결정에 필요한 정보를 제공합니다.
 * </p>
 * 
 * @since Pulse 1.6
 */
public final class TickStartResult {

    private final boolean firstTick;
    private final long startNanos;
    private final long expectedTickCount;

    /**
     * Create a new TickStartResult.
     * 
     * @param firstTick         True if this is the first tick (world just loaded)
     * @param startNanos        Tick start timestamp in nanoseconds
     * @param expectedTickCount Expected tick number after this tick completes
     */
    public TickStartResult(boolean firstTick, long startNanos, long expectedTickCount) {
        this.firstTick = firstTick;
        this.startNanos = startNanos;
        this.expectedTickCount = expectedTickCount;
    }

    /**
     * Whether this is the first tick (indicates WorldLoadEvent should be posted).
     */
    public boolean isFirstTick() {
        return firstTick;
    }

    /**
     * Tick start timestamp in nanoseconds.
     */
    public long getStartNanos() {
        return startNanos;
    }

    /**
     * Expected tick number after this tick completes.
     */
    public long getExpectedTickCount() {
        return expectedTickCount;
    }
}
