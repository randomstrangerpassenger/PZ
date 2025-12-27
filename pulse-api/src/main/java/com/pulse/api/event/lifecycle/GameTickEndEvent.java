package com.pulse.api.event.lifecycle;

import com.pulse.api.event.Event;

/**
 * 게임 틱 종료 이벤트.
 * 
 * IsoWorld.update() 종료 직후에 발생합니다.
 * Echo에서 틱 소요 시간을 계산하고 분석하는 데 사용됩니다.
 * 
 * @since Pulse 1.2
 */
public class GameTickEndEvent extends Event {

    private final long tick;
    private final long durationNanos;

    public GameTickEndEvent(long tick, long durationNanos) {
        super(false); // 취소 불가
        this.tick = tick;
        this.durationNanos = durationNanos;
    }

    /**
     * 현재 틱 번호
     */
    public long getTick() {
        return tick;
    }

    /**
     * 틱 소요 시간 (나노초)
     */
    public long getDurationNanos() {
        return durationNanos;
    }

    /**
     * 틱 소요 시간 (밀리초)
     */
    public double getDurationMs() {
        return durationNanos / 1_000_000.0;
    }

    @Override
    public String getEventName() {
        return "GameTickEnd";
    }
}
