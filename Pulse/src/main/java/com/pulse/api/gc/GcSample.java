package com.pulse.api.gc;

/**
 * GC 스냅샷 DTO.
 * 
 * 틱별 GC 상태 스냅샷을 나타냅니다.
 * Pulse에서 원시 신호만 제공하며, 판단은 Fuse에서 수행.
 * 
 * @since Pulse 1.1.0
 */
public record GcSample(
        /** 틱 ID */
        long tickId,
        /** 타임스탬프 (ms) */
        long timestampMs,
        /** 현재 힙 사용량 (bytes) */
        long heapUsed,
        /** 최대 힙 크기 (bytes) */
        long heapMax,
        /** 총 GC 횟수 (누적) */
        long gcCount,
        /** 총 GC 시간 (누적, ms) */
        long gcTimeMs,
        // --- 델타 값 (이전 샘플 대비) ---
        /** GC 횟수 변화량 */
        long gcCountDelta,
        /** GC 시간 변화량 (ms) */
        long gcTimeDeltaMs,
        /** 힙 사용량 변화량 (bytes) */
        long heapDelta) {
    /**
     * 힙 사용률 (0.0 ~ 1.0).
     * 
     * @return heapUsed / heapMax
     */
    public float heapUsageRatio() {
        if (heapMax <= 0)
            return 0f;
        return (float) heapUsed / heapMax;
    }

    /**
     * GC가 이 틱에서 발생했는지 여부.
     * 
     * @return gcCountDelta > 0 또는 gcTimeDeltaMs > 0
     */
    public boolean gcOccurred() {
        return gcCountDelta > 0 || gcTimeDeltaMs > 0;
    }

    /**
     * 빈 샘플 생성 (폴백용).
     */
    public static GcSample empty(long tickId) {
        return new GcSample(tickId, System.currentTimeMillis(), 0, 1, 0, 0, 0, 0, 0);
    }
}
