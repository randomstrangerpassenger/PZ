package com.echo.aggregate;

import com.echo.measure.ProfilingPoint;

import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentLinkedDeque;

/**
 * 스파이크 로그
 * 
 * 성능 스파이크 이벤트를 기록하고 분석합니다.
 */
public class SpikeLog {

    private static final int MAX_ENTRIES = 100;

    private final Deque<SpikeEntry> entries = new ConcurrentLinkedDeque<>();
    private final double thresholdMs;

    // 통계
    private long totalSpikes = 0;
    private long worstSpikeMicros = 0;
    private String worstSpikeLabel = "";

    public SpikeLog() {
        this(33.33); // 기본 2프레임 (30fps 기준)
    }

    public SpikeLog(double thresholdMs) {
        this.thresholdMs = thresholdMs;
    }

    /**
     * 스파이크 기록
     */
    public void logSpike(long durationMicros, ProfilingPoint point, String label) {
        double durationMs = durationMicros / 1000.0;
        if (durationMs < thresholdMs)
            return;

        SpikeEntry entry = new SpikeEntry(
                Instant.now(),
                durationMicros,
                point,
                label);

        entries.addLast(entry);
        totalSpikes++;

        // 최악 스파이크 갱신
        if (durationMicros > worstSpikeMicros) {
            worstSpikeMicros = durationMicros;
            worstSpikeLabel = (label != null ? label : point.name());
        }

        // 최대 엔트리 수 유지
        while (entries.size() > MAX_ENTRIES) {
            entries.pollFirst();
        }
    }

    /**
     * 간편 스파이크 로깅 (Tick용)
     */
    public void logTickSpike(long durationMicros) {
        logSpike(durationMicros, ProfilingPoint.TICK, null);
    }

    /**
     * 최근 스파이크 목록 조회
     */
    public List<SpikeEntry> getRecentSpikes(int count) {
        List<SpikeEntry> result = new ArrayList<>();
        Iterator<SpikeEntry> iter = entries.descendingIterator();
        while (iter.hasNext() && result.size() < count) {
            result.add(iter.next());
        }
        return result;
    }

    /**
     * 모든 스파이크 조회
     */
    public List<SpikeEntry> getAllSpikes() {
        return new ArrayList<>(entries);
    }

    /**
     * 총 스파이크 수
     */
    public long getTotalSpikes() {
        return totalSpikes;
    }

    /**
     * 최악 스파이크 시간 (밀리초)
     */
    public double getWorstSpikeMs() {
        return worstSpikeMicros / 1000.0;
    }

    /**
     * 최악 스파이크 라벨
     */
    public String getWorstSpikeLabel() {
        return worstSpikeLabel;
    }

    /**
     * 임계값 (밀리초)
     */
    public double getThresholdMs() {
        return thresholdMs;
    }

    /**
     * 포인트별 스파이크 카운트
     */
    public Map<ProfilingPoint, Long> getSpikesByPoint() {
        Map<ProfilingPoint, Long> result = new EnumMap<>(ProfilingPoint.class);
        for (SpikeEntry entry : entries) {
            result.merge(entry.point, 1L, Long::sum);
        }
        return result;
    }

    /**
     * JSON 출력용 Map
     */
    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("threshold_ms", thresholdMs);
        map.put("total_spikes", totalSpikes);
        map.put("worst_spike_ms", Math.round(getWorstSpikeMs() * 100) / 100.0);
        map.put("worst_spike_source", worstSpikeLabel);

        List<Map<String, Object>> recent = new ArrayList<>();
        for (SpikeEntry entry : getRecentSpikes(10)) {
            recent.add(entry.toMap());
        }
        map.put("recent_spikes", recent);

        return map;
    }

    /**
     * 초기화
     */
    public void reset() {
        entries.clear();
        totalSpikes = 0;
        worstSpikeMicros = 0;
        worstSpikeLabel = "";
    }

    // ============================================================
    // 스파이크 엔트리
    // ============================================================

    public static class SpikeEntry {
        private final Instant timestamp;
        private final long durationMicros;
        private final ProfilingPoint point;
        private final String label;

        public SpikeEntry(Instant timestamp, long durationMicros,
                ProfilingPoint point, String label) {
            this.timestamp = timestamp;
            this.durationMicros = durationMicros;
            this.point = point;
            this.label = label;
        }

        public Instant getTimestamp() {
            return timestamp;
        }

        public long getDurationMicros() {
            return durationMicros;
        }

        public double getDurationMs() {
            return durationMicros / 1000.0;
        }

        public ProfilingPoint getPoint() {
            return point;
        }

        public String getLabel() {
            return label;
        }

        public Map<String, Object> toMap() {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("timestamp", DateTimeFormatter.ISO_INSTANT.format(timestamp));
            map.put("duration_ms", Math.round(getDurationMs() * 100) / 100.0);
            map.put("point", point.name());
            map.put("label", label != null ? label : point.getDisplayName());
            return map;
        }

        @Override
        public String toString() {
            return String.format("[%s] %.2fms - %s (%s)",
                    DateTimeFormatter.ISO_LOCAL_TIME.format(
                            timestamp.atZone(java.time.ZoneId.systemDefault())),
                    getDurationMs(),
                    point.getDisplayName(),
                    label != null ? label : "");
        }
    }
}
