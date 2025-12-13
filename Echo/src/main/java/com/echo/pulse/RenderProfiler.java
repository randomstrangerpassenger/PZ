package com.echo.pulse;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.measure.ProfilingScope;

/**
 * 렌더 프로파일러
 * 
 * 렌더링 프레임 시간을 측정합니다.
 * Pulse OnRender 이벤트와 연동됩니다.
 */
public class RenderProfiler {

    private final EchoProfiler profiler = EchoProfiler.getInstance();

    // 현재 활성 스코프
    private ProfilingScope currentScope = null;

    // 프레임 카운터
    private long frameCount = 0;

    // FPS 계산용
    private long fpsStartTime = 0;
    private int fpsFrameCount = 0;
    private double currentFps = 0;

    // 마지막 프레임 시간
    private long lastFrameStartTime = 0;
    private long lastFrameDuration = 0;

    /**
     * 렌더 시작 시 호출
     */
    public void onRenderPre() {
        if (!profiler.isEnabled())
            return;

        lastFrameStartTime = System.nanoTime();
        currentScope = profiler.scope(ProfilingPoint.FRAME);
        frameCount++;
        fpsFrameCount++;

        // 1초마다 FPS 계산
        long now = System.currentTimeMillis();
        if (fpsStartTime == 0) {
            fpsStartTime = now;
        } else if (now - fpsStartTime >= 1000) {
            currentFps = fpsFrameCount * 1000.0 / (now - fpsStartTime);
            fpsFrameCount = 0;
            fpsStartTime = now;
        }
    }

    /**
     * 렌더 종료 시 호출
     */
    public void onRenderPost() {
        if (currentScope == null)
            return;

        currentScope.close();
        currentScope = null;

        // 프레임 시간 계산
        long elapsed = System.nanoTime() - lastFrameStartTime;
        lastFrameDuration = elapsed / 1000; // 마이크로초
    }

    /**
     * 월드 렌더링 래퍼
     */
    public void profileWorldRender(Runnable worldRender) {
        if (!profiler.isEnabled()) {
            worldRender.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.RENDER_WORLD)) {
            worldRender.run();
        }
    }

    /**
     * UI 렌더링 래퍼
     */
    public void profileUIRender(Runnable uiRender) {
        if (!profiler.isEnabled()) {
            uiRender.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.RENDER_UI)) {
            uiRender.run();
        }
    }

    // --- 조회 ---

    /**
     * 총 프레임 카운트
     */
    public long getFrameCount() {
        return frameCount;
    }

    /**
     * 현재 FPS
     */
    public double getCurrentFps() {
        return currentFps;
    }

    /**
     * 마지막 프레임 시간 (마이크로초)
     */
    public long getLastFrameDurationMicros() {
        return lastFrameDuration;
    }

    /**
     * 마지막 프레임 시간 (밀리초)
     */
    public double getLastFrameDurationMs() {
        return lastFrameDuration / 1000.0;
    }

    // GPU Timing (Requires GL33)
    private boolean glQuerySupported = false;
    private long lastGpuDuration = 0;

    // Placeholder for OpenGL Query Object
    private final GpuQueryRing gpuQueryRing = new GpuQueryRing();

    /**
     * GPU 시간 측정 시작 (glQueryCounter)
     */
    public void startGpuTimer() {
        if (!glQuerySupported)
            return;
        gpuQueryRing.start();
    }

    /**
     * GPU 시간 측정 종료 및 수집
     */
    public void endGpuTimer() {
        if (!glQuerySupported)
            return;
        gpuQueryRing.end();
    }

    /**
     * 프레임 드랍 원인 분석
     */
    public FrameDropCause analyzeFrameDrop() {
        if (lastFrameDuration < 16666) { // 60 FPS (16.6ms)
            return FrameDropCause.NONE;
        }

        // If GPU time makes up > 80% of frame time, it's likely GPU bound
        if (lastGpuDuration > 0 && lastGpuDuration > lastFrameDuration * 0.8) {
            return FrameDropCause.GPU_BOUND;
        }

        // Otherwise, assume CPU bound
        return FrameDropCause.CPU_BOUND;
    }

    public enum FrameDropCause {
        NONE,
        CPU_BOUND,
        GPU_BOUND,
        UNKNOWN
    }

    /**
     * Placeholder Inner Class for GPU Queries
     */
    private static class GpuQueryRing {
        public void start() {
        }

        public void end() {
        }
    }

    /**
     * 카운터 초기화
     */
    public void reset() {
        frameCount = 0;
        lastFrameDuration = 0;
        fpsStartTime = 0;
        fpsFrameCount = 0;
        currentFps = 0;
    }
}
