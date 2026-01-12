package com.pulse.diagnostics;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 엔진 함수별 소요 시간을 기록하는 핫스팟 맵.
 * 
 * 개발자가 "어떤 함수가 병목인지" 자동으로 파악할 수 있게 합니다.
 * 로드맵의 "Hotspot Map API" 요구사항을 충족합니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // Mixin에서 시간 기록
 * long start = System.nanoTime();
 * // ... 함수 로직 ...
 * HotspotMap.record("IsoZombie.update", System.nanoTime() - start);
 * 
 * // 핫스팟 조회
 * List<HotspotEntry> top = HotspotMap.getTopHotspots(10);
 * }</pre>
 * 
 * @since Pulse 1.2
 */
public final class HotspotMap {

    private static final Map<String, TimingStats> hotspots = new ConcurrentHashMap<>();
    private static volatile boolean enabled = true;

    private HotspotMap() {
    }

    /**
     * 함수 실행 시간 기록
     * 
     * @param function 함수 식별자
     * @param nanos    소요 시간 (나노초)
     */
    public static void record(String function, long nanos) {
        if (!enabled || function == null || nanos < 0) {
            return;
        }
        hotspots.computeIfAbsent(function, k -> new TimingStats()).record(nanos);
    }

    /**
     * 모든 핫스팟 조회
     */
    public static Map<String, TimingStats> getAll() {
        return new HashMap<>(hotspots);
    }

    /**
     * 상위 N개 핫스팟 (총 시간 기준)
     */
    public static List<HotspotEntry> getTopHotspots(int n) {
        List<HotspotEntry> entries = new ArrayList<>();
        hotspots.forEach((name, stats) -> entries.add(new HotspotEntry(name, stats)));

        entries.sort((a, b) -> Long.compare(b.getTotalNanos(), a.getTotalNanos()));

        return entries.subList(0, Math.min(n, entries.size()));
    }

    /**
     * 특정 함수의 통계
     */
    public static TimingStats getStats(String function) {
        return hotspots.get(function);
    }

    /**
     * 모든 통계 초기화
     */
    public static void reset() {
        hotspots.clear();
    }

    /**
     * 활성화/비활성화
     */
    public static void setEnabled(boolean enabled) {
        HotspotMap.enabled = enabled;
    }

    public static boolean isEnabled() {
        return enabled;
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스
    // ─────────────────────────────────────────────────────────────

    /**
     * 함수별 타이밍 통계
     */
    public static class TimingStats {
        private final AtomicLong count = new AtomicLong(0);
        private final AtomicLong totalNanos = new AtomicLong(0);
        private volatile long minNanos = Long.MAX_VALUE;
        private volatile long maxNanos = 0;

        public void record(long nanos) {
            count.incrementAndGet();
            totalNanos.addAndGet(nanos);

            // Min/Max (경합 조건 있지만 정확도보다 성능 우선)
            if (nanos < minNanos)
                minNanos = nanos;
            if (nanos > maxNanos)
                maxNanos = nanos;
        }

        public long getCount() {
            return count.get();
        }

        public long getTotalNanos() {
            return totalNanos.get();
        }

        public long getMinNanos() {
            return minNanos == Long.MAX_VALUE ? 0 : minNanos;
        }

        public long getMaxNanos() {
            return maxNanos;
        }

        public double getAverageNanos() {
            long c = count.get();
            return c > 0 ? (double) totalNanos.get() / c : 0;
        }

        public double getAverageMs() {
            return getAverageNanos() / 1_000_000.0;
        }

        public double getTotalMs() {
            return totalNanos.get() / 1_000_000.0;
        }

        @Override
        public String toString() {
            return String.format("count=%d, total=%.2fms, avg=%.3fms, min=%.3fms, max=%.3fms",
                    count.get(), getTotalMs(), getAverageMs(),
                    getMinNanos() / 1_000_000.0, getMaxNanos() / 1_000_000.0);
        }
    }

    /**
     * 핫스팟 엔트리 (정렬용)
     */
    public static class HotspotEntry {
        private final String function;
        private final TimingStats stats;

        public HotspotEntry(String function, TimingStats stats) {
            this.function = function;
            this.stats = stats;
        }

        public String getFunction() {
            return function;
        }

        public long getCount() {
            return stats.getCount();
        }

        public long getTotalNanos() {
            return stats.getTotalNanos();
        }

        public double getTotalMs() {
            return stats.getTotalMs();
        }

        public double getAverageMs() {
            return stats.getAverageMs();
        }

        @Override
        public String toString() {
            return String.format("%s: %s", function, stats);
        }
    }
}
