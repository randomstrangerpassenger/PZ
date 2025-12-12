package com.echo.aggregate;

import java.util.*;

/**
 * 메모리 스냅샷 타임시리즈.
 * 
 * GC/메모리 데이터를 시계열로 기록합니다.
 * 틱 히스토그램과 동일한 주기로 스냅샷을 저장합니다.
 * 
 * @since 1.0.1
 */
public class MemoryTimeSeries {

    private static final MemoryTimeSeries INSTANCE = new MemoryTimeSeries();

    // 기본 버퍼 크기 (5분 * 60fps = 18000, 하지만 메모리 절약을 위해 1초당 1개만)
    private static final int DEFAULT_BUFFER_SIZE = 300; // 5분 worth
    private static final long SAMPLE_INTERVAL_MS = 1000; // 1초

    private final LinkedList<MemorySnapshot> snapshots = new LinkedList<>();
    private int maxSize = DEFAULT_BUFFER_SIZE;
    private long lastSampleTime = 0;

    public static MemoryTimeSeries getInstance() {
        return INSTANCE;
    }

    /**
     * 메모리 스냅샷 기록 (매 틱 호출 가능하지만 실제로는 1초 간격)
     */
    public void record() {
        long now = System.currentTimeMillis();
        if (now - lastSampleTime < SAMPLE_INTERVAL_MS) {
            return;
        }
        lastSampleTime = now;

        MemorySnapshot snapshot = MemorySnapshot.capture();
        synchronized (snapshots) {
            snapshots.addLast(snapshot);
            while (snapshots.size() > maxSize) {
                snapshots.removeFirst();
            }
        }
    }

    /**
     * 지정 시간 범위의 스냅샷 조회
     * 
     * @param durationMs 최근 N 밀리초
     */
    public List<MemorySnapshot> getRecent(long durationMs) {
        long cutoff = System.currentTimeMillis() - durationMs;
        List<MemorySnapshot> result = new ArrayList<>();
        synchronized (snapshots) {
            for (MemorySnapshot s : snapshots) {
                if (s.timestamp >= cutoff) {
                    result.add(s);
                }
            }
        }
        return result;
    }

    /**
     * 전체 스냅샷 조회
     */
    public List<MemorySnapshot> getAll() {
        synchronized (snapshots) {
            return new ArrayList<>(snapshots);
        }
    }

    /**
     * 트렌드 분석 (최근 N초 동안의 메모리 추세)
     */
    public TrendAnalysis analyzeTrend(long durationMs) {
        List<MemorySnapshot> recent = getRecent(durationMs);
        if (recent.size() < 2) {
            return new TrendAnalysis(0, 0, TrendDirection.STABLE);
        }

        MemorySnapshot first = recent.get(0);
        MemorySnapshot last = recent.get(recent.size() - 1);

        long heapDelta = last.heapUsed - first.heapUsed;
        long timeDelta = last.timestamp - first.timestamp;

        double ratePerSecond = timeDelta > 0 ? (heapDelta * 1000.0 / timeDelta) : 0;

        TrendDirection direction;
        if (ratePerSecond > 1024 * 1024) { // 1MB/s 증가
            direction = TrendDirection.INCREASING;
        } else if (ratePerSecond < -1024 * 1024) { // 1MB/s 감소
            direction = TrendDirection.DECREASING;
        } else {
            direction = TrendDirection.STABLE;
        }

        // GC 빈도 계산
        int gcCount = 0;
        long prevGc = first.gcCount;
        for (MemorySnapshot s : recent) {
            if (s.gcCount > prevGc) {
                gcCount++;
                prevGc = s.gcCount;
            }
        }
        double gcFrequency = timeDelta > 0 ? (gcCount * 60000.0 / timeDelta) : 0; // GC per minute

        return new TrendAnalysis(ratePerSecond, gcFrequency, direction);
    }

    /**
     * JSON 출력용 Map
     */
    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();

        List<MemorySnapshot> recent = getRecent(60000); // 최근 1분

        map.put("sample_count", recent.size());

        if (!recent.isEmpty()) {
            MemorySnapshot latest = recent.get(recent.size() - 1);
            map.put("latest_heap_mb", latest.heapUsed / (1024 * 1024));
            map.put("latest_gc_count", latest.gcCount);
            map.put("latest_gc_time_ms", latest.gcTimeMs);
        }

        TrendAnalysis trend = analyzeTrend(60000);
        Map<String, Object> trendMap = new LinkedHashMap<>();
        trendMap.put("direction", trend.direction.name());
        trendMap.put("rate_bytes_per_sec", Math.round(trend.ratePerSecond));
        trendMap.put("gc_per_minute", Math.round(trend.gcFrequency * 100) / 100.0);
        map.put("trend", trendMap);

        return map;
    }

    /**
     * 초기화
     */
    public void reset() {
        synchronized (snapshots) {
            snapshots.clear();
        }
        lastSampleTime = 0;
    }

    public void setMaxSize(int size) {
        this.maxSize = size;
    }

    // ============================================================
    // 내부 클래스
    // ============================================================

    /**
     * 메모리 스냅샷
     */
    public static class MemorySnapshot {
        public final long timestamp;
        public final long heapUsed;
        public final long heapMax;
        public final long gcCount;
        public final long gcTimeMs;
        public final double allocationRateMBps;

        public MemorySnapshot(long timestamp, long heapUsed, long heapMax,
                long gcCount, long gcTimeMs, double allocationRateMBps) {
            this.timestamp = timestamp;
            this.heapUsed = heapUsed;
            this.heapMax = heapMax;
            this.gcCount = gcCount;
            this.gcTimeMs = gcTimeMs;
            this.allocationRateMBps = allocationRateMBps;
        }

        public static MemorySnapshot capture() {
            Runtime rt = Runtime.getRuntime();
            long heapUsed = rt.totalMemory() - rt.freeMemory();
            long heapMax = rt.maxMemory();

            long gcCount = 0;
            long gcTime = 0;
            for (java.lang.management.GarbageCollectorMXBean gc : java.lang.management.ManagementFactory
                    .getGarbageCollectorMXBeans()) {
                if (gc.getCollectionCount() >= 0)
                    gcCount += gc.getCollectionCount();
                if (gc.getCollectionTime() >= 0)
                    gcTime += gc.getCollectionTime();
            }

            return new MemorySnapshot(
                    System.currentTimeMillis(),
                    heapUsed,
                    heapMax,
                    gcCount,
                    gcTime,
                    0 // Allocation rate calculated separately
            );
        }
    }

    /**
     * 트렌드 분석 결과
     */
    public static class TrendAnalysis {
        public final double ratePerSecond;
        public final double gcFrequency;
        public final TrendDirection direction;

        public TrendAnalysis(double ratePerSecond, double gcFrequency, TrendDirection direction) {
            this.ratePerSecond = ratePerSecond;
            this.gcFrequency = gcFrequency;
            this.direction = direction;
        }
    }

    public enum TrendDirection {
        INCREASING,
        DECREASING,
        STABLE
    }
}
