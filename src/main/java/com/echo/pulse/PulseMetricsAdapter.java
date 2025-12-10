package com.echo.pulse;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.aggregate.TimingData;

/**
 * Pulse 메트릭 어댑터
 * 
 * HUD/Panel에서 사용하는 메트릭 API입니다.
 * Pulse API가 있으면 Pulse에서, 없으면 Echo 내부 데이터에서 가져옵니다.
 */
public final class PulseMetricsAdapter {

    private static final long UPDATE_INTERVAL_MS = 500;

    // 캐시된 값 (0.5초마다 갱신)
    private static volatile double cachedFps = 60.0;
    private static volatile double cachedFrameTimeMs = 16.67;
    private static volatile double cachedTickTimeMs = 16.67;
    private static volatile long lastCacheUpdate = 0;

    // FPS 계산용
    private static long lastFrameTime = System.nanoTime();
    private static double frameTimeSmoothed = 16.67;
    private static final double SMOOTHING_FACTOR = 0.1;

    private PulseMetricsAdapter() {
        // Utility class
    }

    /**
     * 현재 FPS 조회
     * 
     * @return FPS (frames per second)
     */
    public static double getFps() {
        updateCacheIfNeeded();
        return cachedFps;
    }

    /**
     * 현재 프레임 시간 조회 (밀리초)
     * 
     * @return 프레임 시간 (ms)
     */
    public static double getFrameTimeMs() {
        updateCacheIfNeeded();
        return cachedFrameTimeMs;
    }

    /**
     * 현재 틱 시간 조회 (밀리초)
     * 
     * @return 틱 시간 (ms)
     */
    public static double getTickTimeMs() {
        updateCacheIfNeeded();
        return cachedTickTimeMs;
    }

    /**
     * 렌더 시작 시 호출 (프레임 시간 계산용)
     * PulseEventAdapter에서 호출됨
     */
    public static void onFrameStart() {
        long now = System.nanoTime();
        double deltaMs = (now - lastFrameTime) / 1_000_000.0;
        lastFrameTime = now;

        // Exponential smoothing
        frameTimeSmoothed = frameTimeSmoothed * (1 - SMOOTHING_FACTOR) + deltaMs * SMOOTHING_FACTOR;
    }

    /**
     * 캐시 업데이트 (0.5초마다)
     */
    private static void updateCacheIfNeeded() {
        long now = System.currentTimeMillis();
        if (now - lastCacheUpdate < UPDATE_INTERVAL_MS) {
            return;
        }
        lastCacheUpdate = now;

        // Pulse API 시도
        if (tryPulseApi()) {
            return;
        }

        // 폴백: Echo 내부 데이터
        updateFromEchoData();
    }

    /**
     * Pulse API에서 메트릭 가져오기 시도
     * 
     * @return Pulse API 사용 성공 여부
     */
    private static boolean tryPulseApi() {
        try {
            Class<?> pulseMetrics = Class.forName("com.pulse.api.PulseMetrics");

            // getFrameTimeMs()
            java.lang.reflect.Method getFrameTime = pulseMetrics.getMethod("getFrameTimeMs");
            Object frameTime = getFrameTime.invoke(null);
            if (frameTime instanceof Number) {
                cachedFrameTimeMs = ((Number) frameTime).doubleValue();
            }

            // getTickTimeMs()
            java.lang.reflect.Method getTickTime = pulseMetrics.getMethod("getTickTimeMs");
            Object tickTime = getTickTime.invoke(null);
            if (tickTime instanceof Number) {
                cachedTickTimeMs = ((Number) tickTime).doubleValue();
            }

            // getFps()
            java.lang.reflect.Method getFps = pulseMetrics.getMethod("getFps");
            Object fps = getFps.invoke(null);
            if (fps instanceof Number) {
                cachedFps = ((Number) fps).doubleValue();
            }

            return true;
        } catch (ClassNotFoundException e) {
            // Pulse API 없음
            return false;
        } catch (Exception e) {
            // Pulse API 호출 실패
            return false;
        }
    }

    /**
     * Echo 내부 데이터에서 메트릭 계산
     */
    private static void updateFromEchoData() {
        EchoProfiler profiler = EchoProfiler.getInstance();

        // Frame Time: smoothed value 사용
        cachedFrameTimeMs = frameTimeSmoothed;

        // FPS: 1000 / frameTimeMs
        if (cachedFrameTimeMs > 0) {
            cachedFps = 1000.0 / cachedFrameTimeMs;
        }

        // Tick Time: EchoProfiler의 TICK 데이터
        if (profiler.isEnabled()) {
            TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);
            if (tickData != null && tickData.getCallCount() > 0) {
                // 1초 윈도우의 평균 사용
                TimingData.RollingStats stats1s = tickData.getStats1s();
                if (stats1s.getSampleCount() > 0) {
                    cachedTickTimeMs = stats1s.getAverage() / 1000.0; // micros → ms
                }
            }
        }
    }

    /**
     * FPS 색상 등급 계산
     * 
     * @return 0=Good, 1=Warning, 2=Critical
     */
    public static int getFpsGrade() {
        double fps = getFps();
        if (fps >= 55)
            return 0; // Good
        if (fps >= 30)
            return 1; // Warning
        return 2; // Critical
    }

    /**
     * 프레임 시간 색상 등급 계산
     * 
     * @return 0=Good, 1=Warning, 2=Critical
     */
    public static int getFrameTimeGrade() {
        double ms = getFrameTimeMs();
        if (ms <= 16.67)
            return 0; // Good (60fps)
        if (ms <= 33.33)
            return 1; // Warning (30fps)
        return 2; // Critical
    }

    /**
     * 틱 시간 색상 등급 계산
     * 
     * @return 0=Good, 1=Warning, 2=Critical
     */
    public static int getTickTimeGrade() {
        double ms = getTickTimeMs();
        if (ms <= 16.67)
            return 0; // Good
        if (ms <= 33.33)
            return 1; // Warning
        return 2; // Critical
    }
}
