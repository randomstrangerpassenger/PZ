package com.pulse.event.lifecycle;

import com.pulse.api.event.Event;

/**
 * 게임 틱 시작 이벤트.
 * 
 * IsoWorld.update() 진입 직전에 발생합니다.
 * TickPhaseProfiler에서 정확한 틱 시작점을 측정하는 데 사용됩니다.
 * 
 * @since Pulse 1.2
 */
public class GameTickStartEvent extends Event {

    private final long tick;
    private final long startTimeNanos;

    public GameTickStartEvent(long tick) {
        super(false); // 취소 불가
        this.tick = tick;
        this.startTimeNanos = System.nanoTime();
    }

    /**
     * 현재 틱 번호
     */
    public long getTick() {
        return tick;
    }

    /**
     * 틱 시작 시간 (나노초)
     */
    public long getStartTimeNanos() {
        return startTimeNanos;
    }

    @Override
    public String getEventName() {
        return "GameTickStart";
    }
}
