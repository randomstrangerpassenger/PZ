package com.fuse.governor;

/**
 * Rolling Window Statistics for Tick Timing.
 * 
 * 히스테리시스 기반 throttle 진입/복구 조건 판단에 사용됩니다.
 * 1초 윈도우: max 값으로 스파이크 감지
 * 5초 윈도우: avg 값으로 안정성 판단
 * 
 * @since Fuse 1.1
 */
public class RollingTickStats {

    private static final int WINDOW_1S_TICKS = 60; // 60fps 기준 1초
    private static final int WINDOW_5S_TICKS = 300; // 60fps 기준 5초

    /** 원형 버퍼 - 5초 윈도우 */
    private final double[] tickDurations;
    private int writeIndex = 0;
    private int sampleCount = 0;

    public RollingTickStats() {
        this.tickDurations = new double[WINDOW_5S_TICKS];
    }

    /**
     * 틱 시간 기록.
     * 
     * @param tickMs 이번 틱의 소요 시간 (ms)
     */
    public void record(double tickMs) {
        tickDurations[writeIndex] = tickMs;
        writeIndex = (writeIndex + 1) % WINDOW_5S_TICKS;
        if (sampleCount < WINDOW_5S_TICKS) {
            sampleCount++;
        }
    }

    /**
     * 최근 1초(60틱) 내 최대값 반환.
     * 스파이크 감지에 사용.
     */
    public double getLast1sMaxMs() {
        if (sampleCount == 0) {
            return 0.0;
        }

        double max = 0.0;
        int count = Math.min(sampleCount, WINDOW_1S_TICKS);

        for (int i = 0; i < count; i++) {
            int idx = (writeIndex - 1 - i + WINDOW_5S_TICKS) % WINDOW_5S_TICKS;
            if (tickDurations[idx] > max) {
                max = tickDurations[idx];
            }
        }
        return max;
    }

    /**
     * 최근 5초(300틱) 평균값 반환.
     * 안정성 판단에 사용.
     */
    public double getLast5sAvgMs() {
        if (sampleCount == 0) {
            return 0.0;
        }

        double sum = 0.0;
        int count = sampleCount; // 전체 샘플 사용

        for (int i = 0; i < count; i++) {
            int idx = (writeIndex - 1 - i + WINDOW_5S_TICKS) % WINDOW_5S_TICKS;
            sum += tickDurations[idx];
        }
        return sum / count;
    }

    /**
     * 통계 리셋.
     */
    public void reset() {
        writeIndex = 0;
        sampleCount = 0;
        for (int i = 0; i < tickDurations.length; i++) {
            tickDurations[i] = 0.0;
        }
    }

    /**
     * 현재 샘플 수 반환.
     */
    public int getSampleCount() {
        return sampleCount;
    }

    /**
     * 충분한 데이터가 수집되었는지 확인.
     * 최소 1초(60틱) 이상의 데이터가 있어야 유의미한 통계.
     */
    public boolean hasEnoughData() {
        return sampleCount >= WINDOW_1S_TICKS;
    }
}
