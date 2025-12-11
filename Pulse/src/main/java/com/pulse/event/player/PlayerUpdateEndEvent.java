package com.pulse.event.player;

import com.pulse.event.Event;

/**
 * 플레이어 업데이트 종료 이벤트.
 * 
 * IsoPlayer.update() 종료 시 발생합니다.
 * 
 * @since Pulse 1.2
 */
public class PlayerUpdateEndEvent extends Event {

    private final long durationNanos;

    public PlayerUpdateEndEvent(long durationNanos) {
        super(false);
        this.durationNanos = durationNanos;
    }

    /**
     * 업데이트 소요 시간 (나노초)
     */
    public long getDurationNanos() {
        return durationNanos;
    }

    @Override
    public String getEventName() {
        return "PlayerUpdateEnd";
    }
}
