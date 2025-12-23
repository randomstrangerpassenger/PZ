package com.fuse.telemetry;

import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.LongAdder;

/**
 * Reason Statistics for Fuse Telemetry.
 * 
 * 개입 이유(TelemetryReason)별 발생 횟수를 추적합니다.
 * LongAdder 배열 기반으로 고신뢰/저복잡 설계.
 * 
 * @since Fuse 1.1
 */
public class ReasonStats {

    private final LongAdder[] counters;
    private final int reasonCount;

    public ReasonStats() {
        this.reasonCount = TelemetryReason.values().length;
        this.counters = new LongAdder[reasonCount];
        for (int i = 0; i < reasonCount; i++) {
            counters[i] = new LongAdder();
        }
    }

    /**
     * Reason 발생 카운트 증가.
     * 
     * @param reason 발생한 개입 이유
     */
    public void increment(TelemetryReason reason) {
        if (reason != null) {
            counters[reason.ordinal()].increment();
        }
    }

    /**
     * 특정 Reason의 카운트 반환.
     */
    public long getCount(TelemetryReason reason) {
        return reason != null ? counters[reason.ordinal()].sum() : 0;
    }

    /**
     * 상위 N개 Reason 반환 (출력용).
     * 호출 빈도가 낮으므로 호출 시점에만 스캔/정렬.
     * 
     * @param n 상위 N개
     * @return (Reason, Count) 리스트 (내림차순)
     */
    public List<Map.Entry<TelemetryReason, Long>> getTop(int n) {
        TelemetryReason[] reasons = TelemetryReason.values();
        List<Map.Entry<TelemetryReason, Long>> entries = new ArrayList<>(reasonCount);

        for (int i = 0; i < reasonCount; i++) {
            long count = counters[i].sum();
            if (count > 0) {
                entries.add(new AbstractMap.SimpleEntry<>(reasons[i], count));
            }
        }

        entries.sort(Comparator.<Map.Entry<TelemetryReason, Long>>comparingLong(Map.Entry::getValue).reversed());

        return entries.size() > n ? entries.subList(0, n) : entries;
    }

    /**
     * 전체 통계를 Map으로 반환 (리포트용).
     */
    public Map<String, Long> toMap() {
        Map<String, Long> map = new LinkedHashMap<>();
        TelemetryReason[] reasons = TelemetryReason.values();

        for (int i = 0; i < reasonCount; i++) {
            long count = counters[i].sum();
            if (count > 0) {
                map.put(reasons[i].name(), count);
            }
        }
        return map;
    }

    /**
     * 총 개입 횟수 반환.
     */
    public long getTotalCount() {
        long total = 0;
        for (LongAdder counter : counters) {
            total += counter.sum();
        }
        return total;
    }

    /**
     * 통계 리셋.
     */
    public void reset() {
        for (LongAdder counter : counters) {
            counter.reset();
        }
    }
}
