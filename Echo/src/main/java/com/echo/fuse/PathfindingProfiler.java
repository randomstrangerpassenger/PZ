package com.echo.fuse;

import com.echo.config.EchoConfig;
import java.util.EnumMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.LongAdder;

/**
 * AI Pathfinding Profiler for Fuse Deep Analysis.
 * Tracks detailed timing for pathfinding operations.
 * 
 * @since Echo 1.0 Phase 4
 */
public class PathfindingProfiler {

    private static final PathfindingProfiler INSTANCE = new PathfindingProfiler();

    public enum PathfindingStep {
        LOS_CALCULATION,
        GRID_SEARCH,
        OBSTACLE_CHECK,
        DOOR_WINDOW_DETECTION,
        BEHAVIOR
    }

    private final Map<PathfindingStep, LongAdder> stepTimes = new EnumMap<>(PathfindingStep.class);
    private final Map<PathfindingStep, LongAdder> stepCounts = new EnumMap<>(PathfindingStep.class);
    private final LongAdder totalPathRequests = new LongAdder();

    private PathfindingProfiler() {
        for (PathfindingStep step : PathfindingStep.values()) {
            stepTimes.put(step, new LongAdder());
            stepCounts.put(step, new LongAdder());
        }
    }

    public static PathfindingProfiler getInstance() {
        return INSTANCE;
    }

    public void recordStep(PathfindingStep step, long durationMicros) {
        if (!EchoConfig.getInstance().isDeepAnalysisEnabled())
            return;

        stepTimes.get(step).add(durationMicros);
        stepCounts.get(step).increment();
    }

    public void incrementPathRequests() {
        if (!EchoConfig.getInstance().isDeepAnalysisEnabled())
            return;
        totalPathRequests.increment();
    }

    public void reset() {
        for (PathfindingStep step : PathfindingStep.values()) {
            stepTimes.get(step).reset();
            stepCounts.get(step).reset();
        }
        totalPathRequests.reset();
    }

    /**
     * 총 패스파인딩 요청 수
     */
    public long getTotalRequests() {
        return totalPathRequests.sum();
    }

    /**
     * 총 패스파인딩 시간 (밀리초)
     */
    public double getTotalTimeMs() {
        double total = 0;
        for (PathfindingStep step : PathfindingStep.values()) {
            total += stepTimes.get(step).sum() / 1000.0;
        }
        return total;
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new ConcurrentHashMap<>();
        map.put("total_requests", totalPathRequests.sum());

        Map<String, Object> steps = new ConcurrentHashMap<>();
        for (PathfindingStep step : PathfindingStep.values()) {
            Map<String, Object> stepData = new ConcurrentHashMap<>();
            long time = stepTimes.get(step).sum();
            long count = stepCounts.get(step).sum();

            stepData.put("total_ms", time / 1000.0);
            stepData.put("count", count);
            stepData.put("avg_ms", count == 0 ? 0 : (time / 1000.0) / count);

            steps.put(step.name(), stepData);
        }
        map.put("steps", steps);

        return map;
    }
}
