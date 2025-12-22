package com.pulse.handler;

/**
 * Tick 종료 결과 DTO.
 * 
 * <p>
 * WorldTickHandler.onUpdateEnd() 메서드의 결과를 담습니다.
 * Mixin에서 GameTickEvent 및 GameTickEndEvent 발행에 필요한 정보를 제공합니다.
 * </p>
 * 
 * @since Pulse 1.6
 */
public final class TickEndResult {

    private final long tickCount;
    private final long durationNanos;
    private final float deltaTime;

    /**
     * Create a new TickEndResult.
     * 
     * @param tickCount     Current tick count after this tick
     * @param durationNanos Tick duration in nanoseconds
     * @param deltaTime     Delta time in seconds (since last tick)
     */
    public TickEndResult(long tickCount, long durationNanos, float deltaTime) {
        this.tickCount = tickCount;
        this.durationNanos = durationNanos;
        this.deltaTime = deltaTime;
    }

    /**
     * Current tick count after this tick.
     */
    public long getTickCount() {
        return tickCount;
    }

    /**
     * Tick duration in nanoseconds.
     */
    public long getDurationNanos() {
        return durationNanos;
    }

    /**
     * Delta time in seconds (since last tick).
     */
    public float getDeltaTime() {
        return deltaTime;
    }
}
