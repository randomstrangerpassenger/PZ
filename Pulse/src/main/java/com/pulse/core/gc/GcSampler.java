package com.pulse.core.gc;

import com.pulse.api.gc.GcSample;

import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.MemoryUsage;
import java.util.List;

/**
 * GC 샘플러.
 * 
 * JMX를 사용하여 매 틱 GC 상태를 샘플링합니다.
 * MemoryMXBean + GarbageCollectorMXBean 모두 사용.
 * 
 * @since Pulse 1.1.0
 */
public class GcSampler {

    private final MemoryMXBean memoryBean;
    private final List<GarbageCollectorMXBean> gcBeans;

    // 이전 샘플 값 (델타 계산용)
    private long lastGcCount = 0;
    private long lastGcTimeMs = 0;
    private long lastHeapUsed = 0;
    private long lastTickId = -1;

    public GcSampler() {
        this.memoryBean = ManagementFactory.getMemoryMXBean();
        this.gcBeans = ManagementFactory.getGarbageCollectorMXBeans();
    }

    /**
     * 현재 틱의 GC 샘플 생성.
     * 
     * @param tickId 현재 틱 ID
     * @return GcSample 스냅샷
     */
    public GcSample sample(long tickId) {
        try {
            // 힙 메모리 사용량
            MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();
            long heapUsed = heapUsage.getUsed();
            long heapMax = heapUsage.getMax();
            if (heapMax <= 0) {
                heapMax = heapUsage.getCommitted(); // max가 정의되지 않은 경우
            }

            // GC 총 횟수 및 시간 집계
            long totalGcCount = 0;
            long totalGcTimeMs = 0;
            for (GarbageCollectorMXBean bean : gcBeans) {
                long count = bean.getCollectionCount();
                long time = bean.getCollectionTime();
                if (count != -1)
                    totalGcCount += count;
                if (time != -1)
                    totalGcTimeMs += time;
            }

            // 델타 계산
            long gcCountDelta = (lastTickId >= 0) ? totalGcCount - lastGcCount : 0;
            long gcTimeDeltaMs = (lastTickId >= 0) ? totalGcTimeMs - lastGcTimeMs : 0;
            long heapDelta = (lastTickId >= 0) ? heapUsed - lastHeapUsed : 0;

            // 음수 델타 방지 (JVM 리셋 등)
            if (gcCountDelta < 0)
                gcCountDelta = 0;
            if (gcTimeDeltaMs < 0)
                gcTimeDeltaMs = 0;

            // 현재 값 저장
            lastGcCount = totalGcCount;
            lastGcTimeMs = totalGcTimeMs;
            lastHeapUsed = heapUsed;
            lastTickId = tickId;

            return new GcSample(
                    tickId,
                    System.currentTimeMillis(),
                    heapUsed,
                    heapMax,
                    totalGcCount,
                    totalGcTimeMs,
                    gcCountDelta,
                    gcTimeDeltaMs,
                    heapDelta);
        } catch (Exception e) {
            // Fail-soft: 오류 시 빈 샘플 반환
            return GcSample.empty(tickId);
        }
    }

    /**
     * 샘플러 리셋.
     */
    public void reset() {
        lastGcCount = 0;
        lastGcTimeMs = 0;
        lastHeapUsed = 0;
        lastTickId = -1;
    }
}
