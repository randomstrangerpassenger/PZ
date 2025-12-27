package com.pulse.event.npc;

import com.pulse.api.event.Event;

/**
 * 좀비 업데이트 루프 종료 이벤트.
 * 
 * 프레임당 모든 좀비 업데이트가 완료된 후 발생합니다.
 * Fuse의 병목 분석에 사용됩니다.
 * 
 * @since Pulse 1.2
 */
public class ZombieUpdateEndEvent extends Event {

    private final long durationNanos;
    private final int updatedCount;

    public ZombieUpdateEndEvent(long durationNanos, int updatedCount) {
        super(false);
        this.durationNanos = durationNanos;
        this.updatedCount = updatedCount;
    }

    /**
     * 총 업데이트 소요 시간 (나노초)
     */
    public long getDurationNanos() {
        return durationNanos;
    }

    /**
     * 업데이트된 좀비 수
     */
    public int getUpdatedCount() {
        return updatedCount;
    }

    /**
     * 좀비당 평균 업데이트 시간 (나노초)
     */
    public double getAveragePerZombie() {
        return updatedCount > 0 ? (double) durationNanos / updatedCount : 0;
    }

    @Override
    public String getEventName() {
        return "ZombieUpdateEnd";
    }
}
