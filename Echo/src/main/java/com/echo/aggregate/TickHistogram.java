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
    private final LongAdder sumSquaresMicros = new LongAdder(); // v0.9: 표준편차 계산용

    // Jank 카운터 (Phase 4)
    private final LongAdder jankCount60 = new LongAdder(); // >16.67ms (60fps 기준)
    private final LongAdder jankCount30 = new LongAdder(); // >33.33ms (30fps 기준)
    private final LongAdder jankCount100 = new LongAdder(); // >100ms (Major Stutter)
    private final LongAdder warmupCount = new LongAdder(); // Warmup 기간 틱 수 (Echo 0.9.0)

    // v0.9: 틱 간 편차 추적
    private long lastSampleMicros = -1;
    private final LongAdder varianceSum = new LongAdder(); // abs(current - prev) 누적
    private final LongAdder varianceCount = new LongAdder();

    // Jank 임계값 (마이크로초)
    private static final long JANK_THRESHOLD_60_MICROS = 16_667; // 16.67ms
    private static final long JANK_THRESHOLD_30_MICROS = 33_333; // 33.33ms
    private static final long JANK_THRESHOLD_100_MICROS = 100_000; // 100ms

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
        if (durationMicros > JANK_THRESHOLD_100_MICROS) {
            jankCount100.increment();
        }

        // v0.9: 표준편차 계산용 제곱합
        sumSquaresMicros.add(durationMicros * durationMicros / 1000); // overflow 방지: micros^2 / 1000

        // v0.9: 틱 간 편차 추적
        if (lastSampleMicros >= 0) {
            long variance = Math.abs(durationMicros - lastSampleMicros);
            varianceSum.add(variance);
            varianceCount.increment();
        }
        lastSampleMicros = durationMicros;

        // 최근 샘플 저장 (정확한 백분위수용)
        synchronized (sampleLock) {
            recentSamples[sampleIndex] = durationMicros;
            sampleIndex = (sampleIndex + 1) % recentSamples.length;
        }
    }

    // ... (Skipping methods)

    /**
     * 100ms 초과 Major Stutter 비율
     */
    public double getJankPercent100() {
        long total = totalSamples.sum();
        if (total == 0)
            return 0;
        return (jankCount100.sum() * 100.0) / total;
    }

    public long getJankCount100() {
        return jankCount100.sum();
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
        map.put("jank_percent_100ms", Math.round(getJankPercent100() * 100) / 100.0);
        map.put("warmup_ticks", warmupCount.sum());

        // v0.9: 품질 측정 지표
        map.put("std_deviation_ms", Math.round(getStandardDeviationMs() * 100) / 100.0);
        map.put("p99_spike_count", getP99SpikeCount());
        map.put("variance_rate_ms", Math.round(getVarianceRateMs() * 100) / 100.0);
        map.put("quality_score", getQualityScore());

        return map;
    }

    /**
     * Warmup 샘플 추가 (통계 제외, 카운트만)
     */
    public void addWarmupSample(long durationMicros) {
        warmupCount.increment();
        // Warmup 데이터는 메인 통계(P50 등)에 포함하지 않음
        // 필요시 나중에 별도 분석용으로 저장 가능
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

    // ============================================================
    // v0.9: Histogram 품질 측정 (Fuse/Nerve 지원)
    // ============================================================

    /**
     * 표준편차 (밀리초)
     * 틱 시간의 분포 폭을 측정합니다.
     */
    public double getStandardDeviationMs() {
        long n = totalSamples.sum();
        if (n < 2)
            return 0;

        double mean = (sumMicros.sum() / 1000.0) / n; // ms
        double sumSq = sumSquaresMicros.sum(); // micros^2 / 1000 단위

        // Variance = E[X^2] - (E[X])^2
        // sumSq는 micros^2/1000 단위이므로 변환 필요
        double meanSq = mean * mean;
        double varMs = (sumSq / n / 1000.0) - meanSq; // 근사치

        return varMs > 0 ? Math.sqrt(varMs) : 0;
    }

    /**
     * 상위 1% 스파이크 수 (P99 초과 샘플 수)
     */
    public long getP99SpikeCount() {
        long total = totalSamples.sum();
        if (total == 0)
            return 0;

        // 상위 1% = P99 초과
        return (long) Math.ceil(total * 0.01);
    }

    /**
     * 틱 간 편차 변화율 (밀리초)
     * 연속된 틱 사이의 평균 시간 차이를 측정합니다.
     * 낮을수록 일관성 있는 프레임 타이밍.
     */
    public double getVarianceRateMs() {
        long count = varianceCount.sum();
        if (count == 0)
            return 0;
        return (varianceSum.sum() / 1000.0) / count;
    }

    /**
     * 품질 점수 (0-100)
     * P99/P50 비율과 표준편차를 기반으로 버퍼 안정성을 평가합니다.
     */
    public int getQualityScore() {
        long samples = totalSamples.sum();
        if (samples < 60)
            return 0; // 최소 60 샘플 (1초) 필요

        double p50 = getP50();
        double p99 = getP99();
        double stdDev = getStandardDeviationMs();

        if (p50 <= 0)
            return 0;

        // P99/P50 ratio: 1.0 = 완벽, 2.0+ = 불안정
        double ratio = p99 / p50;
        int ratioScore = (int) Math.max(0, 100 - (ratio - 1) * 30);

        // StdDev: 0 = 완벽, 10ms+ = 불안정
        int stdDevScore = (int) Math.max(0, 100 - stdDev * 5);

        // Jank 60fps: 0% = 완벽, 10%+ = 불안정
        int jankScore = (int) Math.max(0, 100 - getJankPercent60() * 5);

        return (ratioScore + stdDevScore + jankScore) / 3;
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
        sumSquaresMicros.reset();
        jankCount60.reset();
        jankCount30.reset();
        warmupCount.reset();
        varianceSum.reset();
        varianceCount.reset();
        lastSampleMicros = -1;
        synchronized (sampleLock) {
            java.util.Arrays.fill(recentSamples, 0);
            sampleIndex = 0;
        }
    }
}
