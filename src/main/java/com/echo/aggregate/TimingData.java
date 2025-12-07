package com.echo.aggregate;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

/**
 * 타이밍 데이터 누적 및 통계 계산
 * 
 * 기능:
 * - 1초/5초/60초 단위 통계
 * - 평균/최대값/표준편차 계산
 * - 호출 빈도 추적
 * - Heavy Function Top N 랭킹
 */
public class TimingData {

    private final String name;

    // 원자적 카운터
    private final LongAdder callCount = new LongAdder();
    private final LongAdder totalTime = new LongAdder();
    private final AtomicLong maxTime = new AtomicLong(0);
    private final AtomicLong minTime = new AtomicLong(Long.MAX_VALUE);

    // 최근 샘플 (스파이크 감지용)
    private final long[] recentSamples = new long[100];
    private int sampleIndex = 0;
    private final Object sampleLock = new Object();

    // 시간대별 통계 (밀리초 단위)
    private final RollingStats stats1s = new RollingStats(1_000);
    private final RollingStats stats5s = new RollingStats(5_000);
    private final RollingStats stats60s = new RollingStats(60_000);

    // 라벨별 세부 통계 (예: 개별 Lua 함수)
    private final Map<String, SubTimingData> labelStats = new ConcurrentHashMap<>();

    public TimingData(String name) {
        this.name = name;
    }

    // ============================================================
    // 샘플 추가
    // ============================================================

    /**
     * 새 샘플 추가
     * 
     * @param elapsedNanos 소요 시간 (나노초)
     */
    public void addSample(long elapsedNanos) {
        addSample(elapsedNanos, null);
    }

    /**
     * 새 샘플 추가 (라벨 포함)
     * 
     * @param elapsedNanos 소요 시간 (나노초)
     * @param label        세부 라벨 (null 가능)
     */
    public void addSample(long elapsedNanos, String label) {
        long elapsedMicros = elapsedNanos / 1000;

        // 기본 통계 업데이트
        callCount.increment();
        totalTime.add(elapsedMicros);

        // 최대/최소 업데이트 (CAS)
        updateMax(elapsedMicros);
        updateMin(elapsedMicros);

        // 최근 샘플 저장
        synchronized (sampleLock) {
            recentSamples[sampleIndex] = elapsedMicros;
            sampleIndex = (sampleIndex + 1) % recentSamples.length;
        }

        // 롤링 통계 업데이트
        long now = System.currentTimeMillis();
        stats1s.addSample(elapsedMicros, now);
        stats5s.addSample(elapsedMicros, now);
        stats60s.addSample(elapsedMicros, now);

        // 라벨별 통계
        if (label != null && !label.isEmpty()) {
            labelStats.computeIfAbsent(label, SubTimingData::new)
                    .addSample(elapsedMicros);
        }
    }

    private void updateMax(long value) {
        long current;
        do {
            current = maxTime.get();
            if (value <= current)
                return;
        } while (!maxTime.compareAndSet(current, value));
    }

    private void updateMin(long value) {
        long current;
        do {
            current = minTime.get();
            if (value >= current)
                return;
        } while (!minTime.compareAndSet(current, value));
    }

    // ============================================================
    // 통계 조회
    // ============================================================

    public String getName() {
        return name;
    }

    public long getCallCount() {
        return callCount.sum();
    }

    /** 평균 시간 (마이크로초) */
    public double getAverageMicros() {
        long count = callCount.sum();
        return count == 0 ? 0 : (double) totalTime.sum() / count;
    }

    /** 최대 시간 (마이크로초) */
    public long getMaxMicros() {
        return maxTime.get();
    }

    /** 최소 시간 (마이크로초) */
    public long getMinMicros() {
        long min = minTime.get();
        return min == Long.MAX_VALUE ? 0 : min;
    }

    /** 총 누적 시간 (마이크로초) */
    public long getTotalMicros() {
        return totalTime.sum();
    }

    // 시간대별 통계
    public RollingStats getStats1s() {
        return stats1s;
    }

    public RollingStats getStats5s() {
        return stats5s;
    }

    public RollingStats getStats60s() {
        return stats60s;
    }

    /**
     * Top N Heavy 라벨 (총 시간 기준)
     */
    public List<SubTimingData> getTopNByTotalTime(int n) {
        return labelStats.values().stream()
                .sorted((a, b) -> Long.compare(b.getTotalMicros(), a.getTotalMicros()))
                .limit(n)
                .toList();
    }

    /**
     * Top N Heavy 라벨 (최대 시간 기준 - 스파이크 감지)
     */
    public List<SubTimingData> getTopNByMaxTime(int n) {
        return labelStats.values().stream()
                .sorted((a, b) -> Long.compare(b.getMaxMicros(), a.getMaxMicros()))
                .limit(n)
                .toList();
    }

    /**
     * Top N Heavy 라벨 (호출 빈도 기준)
     */
    public List<SubTimingData> getTopNByCallCount(int n) {
        return labelStats.values().stream()
                .sorted((a, b) -> Long.compare(b.getCallCount(), a.getCallCount()))
                .limit(n)
                .toList();
    }

    /**
     * 모든 라벨 통계 조회
     */
    public Map<String, SubTimingData> getLabelStats() {
        return Collections.unmodifiableMap(labelStats);
    }

    /**
     * 초기화
     */
    public void reset() {
        callCount.reset();
        totalTime.reset();
        maxTime.set(0);
        minTime.set(Long.MAX_VALUE);

        synchronized (sampleLock) {
            Arrays.fill(recentSamples, 0);
            sampleIndex = 0;
        }

        stats1s.reset();
        stats5s.reset();
        stats60s.reset();

        labelStats.clear();
    }

    // ============================================================
    // 내부 클래스: 롤링 통계
    // ============================================================

    /**
     * 시간 윈도우 기반 롤링 통계
     */
    public static class RollingStats {
        private final long windowMs;
        private final Deque<Sample> samples = new ArrayDeque<>();
        private final Object lock = new Object();

        public RollingStats(long windowMs) {
            this.windowMs = windowMs;
        }

        public void addSample(long value, long timestamp) {
            synchronized (lock) {
                samples.addLast(new Sample(value, timestamp));
                cleanup(timestamp);
            }
        }

        private void cleanup(long now) {
            long threshold = now - windowMs;
            while (!samples.isEmpty() && samples.peekFirst().timestamp < threshold) {
                samples.pollFirst();
            }
        }

        public long getAverage() {
            synchronized (lock) {
                if (samples.isEmpty())
                    return 0;
                cleanup(System.currentTimeMillis());
                return (long) samples.stream()
                        .mapToLong(s -> s.value)
                        .average()
                        .orElse(0);
            }
        }

        public long getMax() {
            synchronized (lock) {
                if (samples.isEmpty())
                    return 0;
                cleanup(System.currentTimeMillis());
                return samples.stream()
                        .mapToLong(s -> s.value)
                        .max()
                        .orElse(0);
            }
        }

        public int getSampleCount() {
            synchronized (lock) {
                cleanup(System.currentTimeMillis());
                return samples.size();
            }
        }

        public long getWindowMs() {
            return windowMs;
        }

        public void reset() {
            synchronized (lock) {
                samples.clear();
            }
        }

        /**
         * 오래된 샘플 정리 (외부 호출용)
         */
        public void performCleanup() {
            synchronized (lock) {
                cleanup(System.currentTimeMillis());
            }
        }

        private record Sample(long value, long timestamp) {
        }
    }

    // ============================================================
    // 내부 클래스: 라벨별 세부 통계
    // ============================================================

    /**
     * 개별 라벨(함수)에 대한 세부 통계
     */
    public static class SubTimingData {
        private final String label;
        private final LongAdder callCount = new LongAdder();
        private final LongAdder totalTime = new LongAdder();
        private final AtomicLong maxTime = new AtomicLong(0);

        public SubTimingData(String label) {
            this.label = label;
        }

        public void addSample(long elapsedMicros) {
            callCount.increment();
            totalTime.add(elapsedMicros);

            long current;
            do {
                current = maxTime.get();
                if (elapsedMicros <= current)
                    return;
            } while (!maxTime.compareAndSet(current, elapsedMicros));
        }

        public String getLabel() {
            return label;
        }

        public long getCallCount() {
            return callCount.sum();
        }

        public long getTotalMicros() {
            return totalTime.sum();
        }

        public long getMaxMicros() {
            return maxTime.get();
        }

        public double getAverageMicros() {
            long count = callCount.sum();
            return count == 0 ? 0 : (double) totalTime.sum() / count;
        }
    }
}
