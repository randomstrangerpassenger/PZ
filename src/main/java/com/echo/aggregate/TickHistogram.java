package com.echo.aggregate;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.LongAdder;

/**
 * 틱 히스토그램
 * 
 * 틱 시간 분포를 버킷별로 집계합니다.
 * 성능 분석 및 시각화에 사용됩니다.
 */
public class TickHistogram {

    // 기본 버킷 경계 (밀리초)
    private static final double[] DEFAULT_BUCKETS = {
            0, 5, 10, 16.67, 20, 33.33, 50, 100, 200
    };

    private final double[] buckets;
    private final LongAdder[] counts;
    private final LongAdder totalSamples = new LongAdder();

    // 통계
    private final LongAdder sumMicros = new LongAdder();

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
     * 백분위수 계산
     * 
     * @param percentile 0-100 사이 값
     */
    public double getPercentile(double percentile) {
        long total = totalSamples.sum();
        if (total == 0)
            return 0;

        long target = (long) (total * percentile / 100.0);
        long cumulative = 0;

        for (int i = 0; i < counts.length; i++) {
            cumulative += counts[i].sum();
            if (cumulative >= target) {
                // 해당 버킷의 중간값 반환
                if (i == counts.length - 1) {
                    return buckets[i] * 1.5; // 마지막 버킷
                }
                return (buckets[i] + buckets[i + 1]) / 2;
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
    }
}
