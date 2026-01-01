package com.echo.measure;

import java.util.*;

/**
 * 렌더링 메트릭 수집기.
 * 
 * Phase 5.2: 렌더링 성능 모니터링.
 * Draw Call, 배치 통계, (가능시) GPU 시간 추적.
 * 
 * 참고: PZ의 렌더링 파이프라인 접근이 제한적이므로 가능한 범위 내에서 구현.
 * 
 * @since 1.0.1
 */
public class RenderMetrics implements IRenderMetrics {

    private static final RenderMetrics INSTANCE = new RenderMetrics();

    // Draw Call 통계
    private volatile long frameDrawCalls = 0;
    private volatile long totalDrawCalls = 0;
    private volatile long totalFrames = 0;

    // 배치 통계
    private volatile long frameBatches = 0;
    private volatile long totalBatches = 0;

    // 텍스처 스왑
    private volatile long frameTextureSwaps = 0;
    private volatile long totalTextureSwaps = 0;

    // 버텍스/인덱스 카운트
    private volatile long frameVertices = 0;
    private volatile long frameIndices = 0;

    // 프레임 타이밍
    private volatile double lastFrameTimeMs = 0;
    private volatile double avgFrameTimeMs = 0;
    private volatile double maxFrameTimeMs = 0;
    private final LinkedList<Double> frameTimeHistory = new LinkedList<>();
    private static final int HISTORY_SIZE = 60;

    // GPU 타이밍 (가능한 경우만)
    private volatile boolean gpuTimingAvailable = false;
    private volatile double gpuTimeMs = 0;

    public static RenderMetrics getInstance() {
        return INSTANCE;
    }

    /**
     * 프레임 시작
     */
    public void beginFrame() {
        frameDrawCalls = 0;
        frameBatches = 0;
        frameTextureSwaps = 0;
        frameVertices = 0;
        frameIndices = 0;
    }

    /**
     * 프레임 종료
     */
    public void endFrame(double frameTimeMs) {
        this.lastFrameTimeMs = frameTimeMs;
        totalFrames++;
        totalDrawCalls += frameDrawCalls;
        totalBatches += frameBatches;
        totalTextureSwaps += frameTextureSwaps;

        this.maxFrameTimeMs = Math.max(maxFrameTimeMs, frameTimeMs);

        synchronized (frameTimeHistory) {
            frameTimeHistory.addLast(frameTimeMs);
            while (frameTimeHistory.size() > HISTORY_SIZE) {
                frameTimeHistory.removeFirst();
            }

            double sum = 0;
            for (double t : frameTimeHistory) {
                sum += t;
            }
            avgFrameTimeMs = sum / frameTimeHistory.size();
        }
    }

    /**
     * Draw Call 기록
     */
    public void recordDrawCall() {
        frameDrawCalls++;
    }

    /**
     * 다수의 Draw Call 기록
     */
    public void recordDrawCalls(int count) {
        frameDrawCalls += count;
    }

    /**
     * 배치 기록
     */
    public void recordBatch() {
        frameBatches++;
    }

    /**
     * 텍스처 스왑 기록
     */
    public void recordTextureSwap() {
        frameTextureSwaps++;
    }

    /**
     * 지오메트리 기록
     */
    public void recordGeometry(int vertices, int indices) {
        frameVertices += vertices;
        frameIndices += indices;
    }

    /**
     * GPU 타이밍 업데이트 (OpenGL Query 사용 가능 시)
     */
    public void updateGpuTime(double gpuMs) {
        this.gpuTimingAvailable = true;
        this.gpuTimeMs = gpuMs;
    }

    // --- Getters ---

    public long getFrameDrawCalls() {
        return frameDrawCalls;
    }

    public double getAvgDrawCallsPerFrame() {
        return totalFrames > 0 ? (double) totalDrawCalls / totalFrames : 0;
    }

    public long getFrameBatches() {
        return frameBatches;
    }

    public double getBatchingEfficiency() {
        if (frameDrawCalls == 0)
            return 100;
        return (1.0 - (double) frameBatches / frameDrawCalls) * 100;
    }

    public long getFrameTextureSwaps() {
        return frameTextureSwaps;
    }

    public long getFrameVertices() {
        return frameVertices;
    }

    public long getFrameIndices() {
        return frameIndices;
    }

    public double getLastFrameTimeMs() {
        return lastFrameTimeMs;
    }

    @Override
    public double getAvgFrameTimeMs() {
        return avgFrameTimeMs;
    }

    public double getMaxFrameTimeMs() {
        return maxFrameTimeMs;
    }

    @Override
    public double getFps() {
        return avgFrameTimeMs > 0 ? 1000.0 / avgFrameTimeMs : 0;
    }

    public boolean isGpuTimingAvailable() {
        return gpuTimingAvailable;
    }

    public double getGpuTimeMs() {
        return gpuTimeMs;
    }

    public long getTotalFrames() {
        return totalFrames;
    }

    /**
     * 렌더 효율성 등급
     */
    @Override
    public RenderEfficiency getRenderEfficiency() {
        double batching = getBatchingEfficiency();
        double drawCalls = getAvgDrawCallsPerFrame();

        if (batching >= 80 && drawCalls < 500)
            return RenderEfficiency.EXCELLENT;
        if (batching >= 60 && drawCalls < 1000)
            return RenderEfficiency.GOOD;
        if (batching >= 40 || drawCalls < 2000)
            return RenderEfficiency.FAIR;
        return RenderEfficiency.POOR;
    }

    /**
     * 초기화
     */
    public void reset() {
        frameDrawCalls = 0;
        totalDrawCalls = 0;
        totalFrames = 0;
        frameBatches = 0;
        totalBatches = 0;
        frameTextureSwaps = 0;
        totalTextureSwaps = 0;
        frameVertices = 0;
        frameIndices = 0;
        lastFrameTimeMs = 0;
        avgFrameTimeMs = 0;
        maxFrameTimeMs = 0;
        gpuTimingAvailable = false;
        gpuTimeMs = 0;
        synchronized (frameTimeHistory) {
            frameTimeHistory.clear();
        }
    }

    /**
     * JSON 출력
     */
    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();

        // 프레임 통계
        Map<String, Object> frame = new LinkedHashMap<>();
        frame.put("total_frames", totalFrames);
        frame.put("fps", Math.round(getFps() * 10) / 10.0);
        frame.put("avg_frame_ms", Math.round(avgFrameTimeMs * 100) / 100.0);
        frame.put("max_frame_ms", Math.round(maxFrameTimeMs * 100) / 100.0);
        map.put("frame", frame);

        // Draw Call 통계
        Map<String, Object> drawCalls = new LinkedHashMap<>();
        drawCalls.put("per_frame", frameDrawCalls);
        drawCalls.put("avg_per_frame", Math.round(getAvgDrawCallsPerFrame()));
        drawCalls.put("total", totalDrawCalls);
        map.put("draw_calls", drawCalls);

        // 배칭 통계
        Map<String, Object> batching = new LinkedHashMap<>();
        batching.put("batches_per_frame", frameBatches);
        batching.put("total_batches", totalBatches);
        batching.put("efficiency_percent", Math.round(getBatchingEfficiency() * 10) / 10.0);
        map.put("batching", batching);

        // 텍스처 스왑
        map.put("texture_swaps_per_frame", frameTextureSwaps);
        map.put("total_texture_swaps", totalTextureSwaps);

        // 지오메트리
        Map<String, Object> geometry = new LinkedHashMap<>();
        geometry.put("vertices", frameVertices);
        geometry.put("indices", frameIndices);
        map.put("geometry", geometry);

        // GPU 타이밍
        if (gpuTimingAvailable) {
            map.put("gpu_time_ms", Math.round(gpuTimeMs * 100) / 100.0);
        }

        // 효율성 등급
        map.put("efficiency", getRenderEfficiency().name());

        return map;
    }
}
