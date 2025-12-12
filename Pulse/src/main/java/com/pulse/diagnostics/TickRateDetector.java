package com.pulse.diagnostics;

import com.pulse.api.InternalAPI;

/**
 * 동적 틱 레이트 감지기.
 * 
 * PZ의 가변 FPS(30~144+)를 하드코딩하지 않고 런타임에서 실제 델타 시간을
 * 기반으로 틱 레이트를 감지합니다.
 * 
 * @since 1.0.1
 */
public class TickRateDetector {

    private static final TickRateDetector INSTANCE = new TickRateDetector();

    // 기본값: 60 FPS
    private volatile double detectedTickRate = 60.0;
    private volatile double expectedTickMs = 16.67;
    private final double smoothingFactor = 0.1;

    // 유효한 델타 범위 (5ms = 200fps ~ 200ms = 5fps)
    private static final long MIN_DELTA_MS = 5;
    private static final long MAX_DELTA_MS = 200;

    // 통계
    private volatile long sampleCount = 0;
    private volatile long invalidSampleCount = 0;

    private TickRateDetector() {
    }

    public static TickRateDetector getInstance() {
        return INSTANCE;
    }

    /**
     * 실제 프레임/틱 델타 시간으로 틱 레이트 업데이트.
     * Pulse Mixin에서 각 틱 또는 프레임 시작 시 호출합니다.
     * 
     * @param deltaMs 이전 틱과의 시간 차이 (밀리초)
     * @return true if sample was valid and used, false if filtered out
     */
    @InternalAPI
    public boolean updateFromActualDelta(long deltaMs) {
        // 노이즈 필터링: 범위를 벗어난 델타는 무시
        if (deltaMs < MIN_DELTA_MS || deltaMs > MAX_DELTA_MS) {
            invalidSampleCount++;
            return false;
        }

        // 순간 틱 레이트 계산
        double instantRate = 1000.0 / deltaMs;

        // 지수 평활법으로 스무딩
        detectedTickRate = detectedTickRate * (1 - smoothingFactor)
                + instantRate * smoothingFactor;

        // 예상 틱 시간 업데이트
        expectedTickMs = 1000.0 / detectedTickRate;

        sampleCount++;
        return true;
    }

    /**
     * 감지된 틱 레이트 (초당 틱 수)
     */
    public double getDetectedTickRate() {
        return detectedTickRate;
    }

    /**
     * 감지된 틱 레이트 기준 예상 틱 시간 (ms)
     * Echo의 TickHistogram 등에서 기준값으로 사용
     */
    public double getExpectedTickMs() {
        return expectedTickMs;
    }

    /**
     * 현재 틱 시간이 예상 범위 내인지 확인
     * 
     * @param actualMs         실제 틱 시간
     * @param tolerancePercent 허용 오차 (예: 0.5 = 50%)
     */
    public boolean isWithinExpectedRange(double actualMs, double tolerancePercent) {
        double lower = expectedTickMs * (1 - tolerancePercent);
        double upper = expectedTickMs * (1 + tolerancePercent);
        return actualMs >= lower && actualMs <= upper;
    }

    /**
     * 유효 샘플 수
     */
    public long getSampleCount() {
        return sampleCount;
    }

    /**
     * 필터링된 무효 샘플 수 (노이즈)
     */
    public long getInvalidSampleCount() {
        return invalidSampleCount;
    }

    /**
     * 데이터 품질 지표 (0.0 ~ 1.0)
     * 유효 샘플 비율
     */
    public double getDataQuality() {
        long total = sampleCount + invalidSampleCount;
        if (total == 0)
            return 1.0;
        return (double) sampleCount / total;
    }

    /**
     * 상태 초기화
     */
    @InternalAPI
    public void reset() {
        detectedTickRate = 60.0;
        expectedTickMs = 16.67;
        sampleCount = 0;
        invalidSampleCount = 0;
    }

    /**
     * 디버그 정보
     */
    @Override
    public String toString() {
        return String.format("TickRateDetector[rate=%.2f, expectedMs=%.2f, samples=%d, quality=%.2f%%]",
                detectedTickRate, expectedTickMs, sampleCount, getDataQuality() * 100);
    }
}
