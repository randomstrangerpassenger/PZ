package com.fuse.governor;

import com.pulse.api.gc.GcSample;

/**
 * GC 압력 신호.
 * 
 * 가중치 기반으로 압력값 (0.0~1.0) 산출.
 * Pulse는 원시 신호만 제공, 판단은 Fuse에서 수행.
 * 
 * @since Fuse 2.1.0
 */
public class GCPressureSignal {

    /**
     * 압력 레벨.
     */
    public enum Level {
        NORMAL, // < 0.35
        ELEVATED, // 0.35 ~ 0.60
        HIGH, // 0.60 ~ 0.80
        CRITICAL // >= 0.80
    }

    // --- 가중치 ---
    private static final float W_HEAP = 0.40f; // 힙 사용률
    private static final float W_GC_TIME = 0.30f; // GC 소요 시간
    private static final float W_GC_FREQ = 0.20f; // GC 빈도
    private static final float W_JITTER = 0.10f; // 틱 jitter

    // --- 정규화 기준 ---
    private static final double GC_TIME_NORM_MS = 8.0; // 8ms = 1.0
    private static final double GC_FREQ_NORM = 1.0; // 1회 = 1.0
    private static final double JITTER_NORM_MS = 20.0; // 20ms = 1.0

    // --- 레벨 임계값 ---
    private static final float CRITICAL_THRESHOLD = 0.80f;
    private static final float HIGH_THRESHOLD = 0.60f;
    private static final float ELEVATED_THRESHOLD = 0.35f;

    private final float pressureValue;
    private final Level level;
    private final boolean gcOccurred;

    private GCPressureSignal(float pressureValue, boolean gcOccurred) {
        this.pressureValue = clamp(pressureValue, 0f, 1f);
        this.level = calculateLevel(this.pressureValue);
        this.gcOccurred = gcOccurred;
    }

    /**
     * GC 샘플과 틱 jitter로부터 압력 신호 계산.
     * 
     * @param sample     GC 샘플
     * @param tickJitter 틱 표준편차 (ms) - Fuse RollingTickStats에서 제공
     * @return GCPressureSignal
     */
    public static GCPressureSignal from(GcSample sample, double tickJitter) {
        if (sample == null) {
            return new GCPressureSignal(0f, false);
        }

        // 각 요소 점수 계산
        float heapScore = sample.heapUsageRatio();
        float gcTimeScore = normalize(sample.gcTimeDeltaMs(), GC_TIME_NORM_MS);
        float gcFreqScore = normalize(sample.gcCountDelta(), GC_FREQ_NORM);
        float jitterScore = normalize(tickJitter, JITTER_NORM_MS);

        // 가중 합산
        float pressure = W_HEAP * heapScore
                + W_GC_TIME * gcTimeScore
                + W_GC_FREQ * gcFreqScore
                + W_JITTER * jitterScore;

        return new GCPressureSignal(pressure, sample.gcOccurred());
    }

    /**
     * 기본 압력 신호 (jitter 없이).
     */
    public static GCPressureSignal from(GcSample sample) {
        return from(sample, 0.0);
    }

    /**
     * NORMAL 상태 기본값.
     */
    public static GCPressureSignal normal() {
        return new GCPressureSignal(0f, false);
    }

    private static Level calculateLevel(float pressure) {
        if (pressure >= CRITICAL_THRESHOLD)
            return Level.CRITICAL;
        if (pressure >= HIGH_THRESHOLD)
            return Level.HIGH;
        if (pressure >= ELEVATED_THRESHOLD)
            return Level.ELEVATED;
        return Level.NORMAL;
    }

    private static float normalize(double value, double base) {
        if (base <= 0)
            return 0f;
        return clamp((float) (value / base), 0f, 1f);
    }

    private static float clamp(float value, float min, float max) {
        return Math.max(min, Math.min(max, value));
    }

    // --- Getters ---

    public float getPressureValue() {
        return pressureValue;
    }

    public Level getLevel() {
        return level;
    }

    public boolean isGcOccurred() {
        return gcOccurred;
    }

    public boolean isHighOrAbove() {
        return level == Level.HIGH || level == Level.CRITICAL;
    }

    public boolean isCritical() {
        return level == Level.CRITICAL;
    }

    @Override
    public String toString() {
        return String.format("GCPressureSignal{pressure=%.2f, level=%s, gc=%s}",
                pressureValue, level, gcOccurred);
    }
}
