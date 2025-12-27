package com.pulse.event.npc;

import com.pulse.api.event.Event;

/**
 * 좀비 업데이트 루프 시작 이벤트.
 * 
 * 프레임당 모든 좀비 업데이트가 시작되기 전에 발생합니다.
 * Fuse의 AI 최적화 결정에 사용됩니다.
 * 
 * @since Pulse 1.2
 */
public class ZombieUpdateStartEvent extends Event {

    private final long startTimeNanos;
    private final int zombieCount;

    public ZombieUpdateStartEvent(int zombieCount) {
        super(false);
        this.startTimeNanos = System.nanoTime();
        this.zombieCount = zombieCount;
    }

    /**
     * 업데이트 시작 시간 (나노초)
     */
    public long getStartTimeNanos() {
        return startTimeNanos;
    }

    /**
     * 업데이트할 좀비 수
     */
    public int getZombieCount() {
        return zombieCount;
    }

    @Override
    public String getEventName() {
        return "ZombieUpdateStart";
    }
}
