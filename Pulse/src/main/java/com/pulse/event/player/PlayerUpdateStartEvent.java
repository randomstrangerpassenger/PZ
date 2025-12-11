package com.pulse.event.player;

import com.pulse.event.Event;

/**
 * 플레이어 업데이트 시작 이벤트.
 * 
 * IsoPlayer.update() 진입 시 발생합니다.
 * Nerve UI 이벤트에 사용됩니다.
 * 
 * @since Pulse 1.2
 */
public class PlayerUpdateStartEvent extends Event {

    private final long startTimeNanos;

    public PlayerUpdateStartEvent() {
        super(false);
        this.startTimeNanos = System.nanoTime();
    }

    /**
     * 업데이트 시작 시간 (나노초)
     */
    public long getStartTimeNanos() {
        return startTimeNanos;
    }

    @Override
    public String getEventName() {
        return "PlayerUpdateStart";
    }
}
