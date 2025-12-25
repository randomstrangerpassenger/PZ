package com.pulse.core.gc;

import com.pulse.api.gc.GcSample;

/**
 * GC 이벤트 상태 관리.
 * 
 * 매 틱 발행 (중복 틱 ID만 방지).
 * 선제적 DIET 진입을 위해 GC 미발생 틱에서도 이벤트 발행.
 * 
 * @since Pulse 1.1.0
 */
public class GcEventState {

    private long lastPublishedTickId = -1;

    /**
     * 이 샘플을 발행해야 하는지 판단.
     * 
     * 매 틱 발행 정책: 같은 틱 ID 중복만 방지.
     * 
     * @param sample GC 샘플
     * @return 발행 여부
     */
    public boolean shouldPublish(GcSample sample) {
        if (sample == null)
            return false;

        // 같은 틱 ID면 중복 발행 방지
        if (sample.tickId() == lastPublishedTickId) {
            return false;
        }

        lastPublishedTickId = sample.tickId();
        return true; // 매 틱 발행
    }

    /**
     * 상태 리셋.
     */
    public void reset() {
        lastPublishedTickId = -1;
    }

    /**
     * 마지막 발행된 틱 ID.
     */
    public long getLastPublishedTickId() {
        return lastPublishedTickId;
    }
}
