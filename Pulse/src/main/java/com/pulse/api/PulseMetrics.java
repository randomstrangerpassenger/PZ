package com.pulse.api;

/**
 * Pulse 메트릭 정적 접근 클래스.
 * 
 * Echo의 PulseMetricsAdapter가 reflection으로 이 클래스를 찾습니다.
 * 게임 상태에서 성능 메트릭을 수집하여 제공합니다.
 * 
 * @since 1.0.1
 */
public final class PulseMetrics {

    // Smoothing factors
    private static final double SMOOTHING_FACTOR = 0.1;

    // Frame/Tick tracking
    private static long lastFrameNanos = System.nanoTime();
    private static long lastTickNanos = System.nanoTime();
    private static volatile double frameTimeMs = 16.67;
    private static volatile double tickTimeMs = 16.67;
    private static volatile double fps = 60.0;
    private static volatile double tps = 60.0;

    // Rolling averages
    private static volatile double avgTickTimeMs = 16.67;
    private static volatile double maxTickTimeMs = 16.67;

    private PulseMetrics() {
        // Utility class
    }

    // ============================================================
    // Public API (Echo PulseMetricsAdapter에서 reflection으로 호출)
    // ============================================================

    /**
     * 현재 FPS
     */
    public static double getFps() {
        return fps;
    }

    /**
     * 현재 프레임 시간 (밀리초)
     */
    public static double getFrameTimeMs() {
        return frameTimeMs;
    }

    /**
     * 현재 틱 시간 (밀리초)
     */
    public static double getTickTimeMs() {
        return tickTimeMs;
    }

    /**
     * 평균 틱 시간 (밀리초)
     */
    public static double getAverageTickTimeMs() {
        return avgTickTimeMs;
    }

    /**
     * 최대 틱 시간 (밀리초)
     */
    public static double getMaxTickTimeMs() {
        return maxTickTimeMs;
    }

    /**
     * TPS (Ticks Per Second)
     */
    public static double getTps() {
        return tps;
    }

    // ============================================================
    // Internal Update Methods (Pulse Mixin에서 호출)
    // ============================================================

    /**
     * 프레임 시작 시 호출.
     * Pulse Mixin에서 호출됩니다.
     */
    @InternalAPI
    public static void onFrameStart() {
        long now = System.nanoTime();
        double deltaMs = (now - lastFrameNanos) / 1_000_000.0;
        lastFrameNanos = now;

        // Exponential smoothing
        frameTimeMs = frameTimeMs * (1 - SMOOTHING_FACTOR) + deltaMs * SMOOTHING_FACTOR;

        // FPS calculation
        if (frameTimeMs > 0) {
            fps = 1000.0 / frameTimeMs;
        }
    }

    /**
     * 틱 종료 시 호출.
     * Pulse Mixin에서 호출됩니다.
     */
    @InternalAPI
    public static void onTickEnd(long tickDurationNanos) {
        double deltaMs = tickDurationNanos / 1_000_000.0;

        // Exponential smoothing
        tickTimeMs = tickTimeMs * (1 - SMOOTHING_FACTOR) + deltaMs * SMOOTHING_FACTOR;

        // TPS calculation
        if (tickTimeMs > 0) {
            tps = 1000.0 / tickTimeMs;
        }

        // Update rolling stats
        avgTickTimeMs = tickTimeMs; // Could be enhanced with proper rolling average
        if (deltaMs > maxTickTimeMs) {
            maxTickTimeMs = deltaMs;
        }
    }

    /**
     * 틱 시작 시 호출.
     * 내부 타이밍 추적용.
     */
    @InternalAPI
    public static void onTickStart() {
        lastTickNanos = System.nanoTime();
    }

    /**
     * 현재 진행 중인 틱 시간 계산.
     */
    @InternalAPI
    public static long getCurrentTickDurationNanos() {
        return System.nanoTime() - lastTickNanos;
    }

    // ============================================================
    // IPulseMetrics 누락 메서드 구현 (Phase 0)
    // ============================================================

    /**
     * 현재 로드된 청크 수
     * Echo 및 다른 모듈에서 성능 상관관계 분석에 사용
     */
    public static int getLoadedChunkCount() {
        return GameAccess.getLoadedCellCount();
    }

    /**
     * 현재 엔티티 수 (좀비 + NPC + 차량)
     * Echo 및 다른 모듈에서 성능 상관관계 분석에 사용
     */
    public static int getEntityCount() {
        return GameAccess.getTotalEntityCount();
    }

    /**
     * 현재 사용 중인 메모리 (MB)
     */
    public static long getUsedMemoryMB() {
        Runtime rt = Runtime.getRuntime();
        return (rt.totalMemory() - rt.freeMemory()) / (1024 * 1024);
    }

    /**
     * 최대 할당 가능 메모리 (MB)
     */
    public static long getMaxMemoryMB() {
        return Runtime.getRuntime().maxMemory() / (1024 * 1024);
    }

    /**
     * 최대 틱 시간 리셋 (주기적으로 호출)
     */
    @InternalAPI
    public static void resetMaxTickTime() {
        maxTickTimeMs = tickTimeMs;
    }
}
