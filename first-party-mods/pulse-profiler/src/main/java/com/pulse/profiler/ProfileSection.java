package com.pulse.profiler;

/**
 * 프로파일 구간 데이터.
 */
public class ProfileSection {

    private final String name;
    private long totalNanos = 0;
    private long callCount = 0;
    private long minNanos = Long.MAX_VALUE;
    private long maxNanos = 0;

    public ProfileSection(String name) {
        this.name = name;
    }

    /**
     * 측정 결과 기록
     */
    public synchronized void record(long elapsedNanos) {
        totalNanos += elapsedNanos;
        callCount++;
        minNanos = Math.min(minNanos, elapsedNanos);
        maxNanos = Math.max(maxNanos, elapsedNanos);
    }

    /**
     * 통계 초기화
     */
    public synchronized void reset() {
        totalNanos = 0;
        callCount = 0;
        minNanos = Long.MAX_VALUE;
        maxNanos = 0;
    }

    // ─────────────────────────────────────────────────────────────
    // Getters
    // ─────────────────────────────────────────────────────────────

    public String getName() {
        return name;
    }

    public long getTotalNanos() {
        return totalNanos;
    }

    public long getCallCount() {
        return callCount;
    }

    public long getMinNanos() {
        return callCount > 0 ? minNanos : 0;
    }

    public long getMaxNanos() {
        return maxNanos;
    }

    public long getAverageNanos() {
        return callCount > 0 ? totalNanos / callCount : 0;
    }

    public double getTotalMs() {
        return totalNanos / 1_000_000.0;
    }

    public double getAverageMs() {
        return getAverageNanos() / 1_000_000.0;
    }

    @Override
    public String toString() {
        return String.format("%s: avg=%.3fms, total=%.3fms, calls=%d",
                name, getAverageMs(), getTotalMs(), callCount);
    }
}
