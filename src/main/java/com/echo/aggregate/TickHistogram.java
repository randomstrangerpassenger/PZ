package com.echo.aggregate;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.LongAdder;

import com.echo.EchoConstants;

/**
 * 틱 히스토그램
 * 
 * 틱 시간 분포를 버킷별로 집계합니다.
 * 성능 분석 및 시각화에 사용됩니다.
 */
public class TickHistogram {

    // 기본 버킷 경계 (밀리초)
    private static final double[] DEFAULT_BUCKETS = EchoConstants.DEFAULT_HISTOGRAM_BUCKETS;

    private final double[] buckets;
    private final LongAdder[] counts;
    private final LongAdder totalSamples = new LongAdder();

    // 통계
    private final LongAdder sumMicros = new LongAdder();

    // Jank 카운터 (Phase 4)
    private final LongAdder jankCount60 = new LongAdder(); // >16.67ms (60fps 기준)
    private final LongAdder jankCount30 = new LongAdder(); // >33.33ms (30fps 기준)

    // Jank 임계값 (마이크로초)
    private static final long JANK_THRESHOLD_60_MICROS = 16_667; // 16.67ms
    private static final long JANK_THRESHOLD_30_MICROS = 33_333; // 33.33ms

    // 정확한 백분위수 계산을 위한 최근 샘플 추적
    private final long[] recentSamples = new long[EchoConstants.HISTOGRAM_SAMPLE_BUFFER];
    private int sampleIndex = 0;
    private final Object sampleLock = new Object();

    public TickHistogram() {
        this(DEFAULT_BUCKETS);
    }

    public TickHistogram(double[] bucketsMs) {
        this.buckets = Arrays.copyOf(bucketsMs, bucketsMs.length);
        this.counts = new LongAdder[buckets.length];
        for (int i = 0; i < counts.length; i++) {
            counts[i] = new LongAdder();
        }
    }

    /**
     * 샘플 추가
     * 
     * @param durationMicros 소요 시간 (마이크로초)
     */
    public void addSample(long durationMicros) {
        double durationMs = durationMicros / 1000.0;

        // 해당하는 버킷 찾기
        int bucketIndex = findBucket(durationMs);
        counts[bucketIndex].increment();
        totalSamples.increment();
        sumMicros.add(durationMicros);

        // Jank 카운터 업데이트
        if (durationMicros > JANK_THRESHOLD_60_MICROS) {
            jankCount60.increment();
        }
        if (durationMicros > JANK_THRESHOLD_30_MICROS) {
            jankCount30.increment();
        }

        // 최근 샘플 저장 (정확한 백분위수용)
        synchronized (sampleLock) {
            recentSamples[sampleIndex] = durationMicros;
            sampleIndex = (sampleIndex + 1) % recentSamples.length;
        }
    }

    private int findBucket(double durationMs) {
        for (int i = buckets.length - 1; i >= 0; i--) {
            if (durationMs >= buckets[i]) {
                return i;
            }
        }
        return 0;
    }

    /**
     * 버킷별 카운트 조회
     */
    public long[] getCounts() {
        long[] result = new long[counts.length];
        for (int i = 0; i < counts.length; i++) {
            result[i] = counts[i].sum();
        }
        return result;
    }

    /**
     * 버킷 경계값 조회
     */
    public double[] getBuckets() {
        return Arrays.copyOf(buckets, buckets.length);
    }

    /**
     * 총 샘플 수
     */
    public long getTotalSamples() {
        return totalSamples.sum();
    }

    /**
     * 백분위수 계산 (개선된 버전)
     * 
     * @param percentile 0-100 사이 값
     */
    public double getPercentile(double percentile) {
        long total = totalSamples.sum();
        if (total == 0)
            return 0;

        // 최근 샘플 기반 정확한 계산 시도
        synchronized (sampleLock) {
            int validSamples = (int) Math.min(total, recentSamples.length);
            if (validSamples >= 10) {
                long[] sorted = new long[validSamples];
                System.arraycopy(recentSamples, 0, sorted, 0, validSamples);
                java.util.Arrays.sort(sorted);
                int index = (int) Math.ceil(percentile / 100.0 * validSamples) - 1;
                index = Math.max(0, Math.min(index, validSamples - 1));
                return sorted[index] / 1000.0; // 마이크로초 -> 밀리초
            }
        }

        // 폴백: 버킷 기반 추정
        long target = (long) (total * percentile / 100.0);
        long cumulative = 0;

        for (int i = 0; i < counts.length; i++) {
            cumulative += counts[i].sum();
            if (cumulative >= target) {
                if (i == counts.length - 1) {
                    // 마지막 버킷: 경계값 + 50% 추정 대신 실제 버킷 시작값 사용
                    return buckets[i];
                }
                // 선형 보간
                double bucketStart = buckets[i];
                double bucketEnd = buckets[i + 1];
                long bucketCount = counts[i].sum();
                long prevCumulative = cumulative - bucketCount;
                double fraction = bucketCount > 0
                        ? (double) (target - prevCumulative) / bucketCount
                        : 0.5;
                return bucketStart + fraction * (bucketEnd - bucketStart);
            }
        }

        return buckets[buckets.length - 1];
    }

    /**
     * P50 (중앙값)
     */
    public double getP50() {
        return getPercentile(50);
    }

    /**
     * P95
     */
    public double getP95() {
        return getPercentile(95);
    }

    /**
     * P99
     */
    public double getP99() {
        return getPercentile(99);
    }

    /**
     * 평균값 (밀리초)
     */
    public double getAverageMs() {
        long total = totalSamples.sum();
        if (total == 0)
            return 0;
        return (sumMicros.sum() / 1000.0) / total;
    }

    // ============================================================
    // Jank 통계 (Phase 4)
    // ============================================================

    /**
     * 60fps 기준 Jank 비율 (>16.67ms)
     * 
     * @return Jank 비율 (0-100%)
     */
    public double getJankPercent60() {
        long total = totalSamples.sum();
        if (total == 0)
            return 0;
        return (jankCount60.sum() * 100.0) / total;
    }

    /**
     * 30fps 기준 Jank 비율 (>33.33ms)
     * 
     * @return Jank 비율 (0-100%)
     */
    public double getJankPercent30() {
        long total = totalSamples.sum();
        if (total == 0)
            return 0;
        return (jankCount30.sum() * 100.0) / total;
    }

    /**
     * 60fps 기준 Jank 카운트
     */
    public long getJankCount60() {
        return jankCount60.sum();
    }

    /**
     * 30fps 기준 Jank 카운트
     */
    public long getJankCount30() {
        return jankCount30.sum();
    }

    /**
     * JSON 출력용 Map 생성
     */
    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();

        // 버킷 라벨 생성
        String[] labels = new String[buckets.length];
        for (int i = 0; i < buckets.length; i++) {
            if (i == buckets.length - 1) {
                labels[i] = String.format(">=%.1fms", buckets[i]);
            } else {
                labels[i] = String.format("%.1f-%.1fms", buckets[i], buckets[i + 1]);
            }
        }

        map.put("buckets_ms", buckets);
        map.put("labels", labels);
        map.put("counts", getCounts());
        map.put("total_samples", getTotalSamples());
        map.put("average_ms", Math.round(getAverageMs() * 100) / 100.0);
        map.put("p50_ms", Math.round(getP50() * 100) / 100.0);
        map.put("p95_ms", Math.round(getP95() * 100) / 100.0);
        map.put("p99_ms", Math.round(getP99() * 100) / 100.0);
        map.put("jank_percent_60fps", Math.round(getJankPercent60() * 100) / 100.0);
        map.put("jank_percent_30fps", Math.round(getJankPercent30() * 100) / 100.0);

        return map;
    }

    /**
     * 콘솔 출력용 문자열
     */
    public String toAsciiChart() {
        StringBuilder sb = new StringBuilder();
        long[] countArray = getCounts();
        long maxCount = Arrays.stream(countArray).max().orElse(1);

        sb.append("Tick Time Distribution:\n");
        sb.append("────────────────────────────────────────────────\n");

        for (int i = 0; i < buckets.length; i++) {
            String label;
            if (i == buckets.length - 1) {
                label = String.format(">=%5.1fms", buckets[i]);
            } else {
                label = String.format("%5.1f-%5.1fms", buckets[i], buckets[i + 1]);
            }

            int barLength = (int) ((countArray[i] * 30) / Math.max(maxCount, 1));
            String bar = "█".repeat(barLength);

            double percentage = getTotalSamples() > 0
                    ? (countArray[i] * 100.0 / getTotalSamples())
                    : 0;

            sb.append(String.format("  %s │ %s %d (%.1f%%)\n",
                    label, bar, countArray[i], percentage));
        }

        sb.append("────────────────────────────────────────────────\n");
        sb.append(String.format("  Total: %,d samples | P50: %.1fms | P95: %.1fms | P99: %.1fms\n",
                getTotalSamples(), getP50(), getP95(), getP99()));

        return sb.toString();
    }

    /**
     * 초기화
     */
    public void reset() {
        for (LongAdder count : counts) {
            count.reset();
        }
        totalSamples.reset();
        sumMicros.reset();
        jankCount60.reset();
        jankCount30.reset();
        synchronized (sampleLock) {
            java.util.Arrays.fill(recentSamples, 0);
            sampleIndex = 0;
        }
    }
}
