package com.echo.fuse;

import com.echo.config.EchoConfig;
import java.util.EnumMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.LongAdder;

/**
 * IsoGrid Profiler for Fuse Deep Analysis.
 * Tracks detailed timing for IsoGrid updates (Map rendering/update logic).
 * 
 * @since Echo 1.0 Phase 4
 */
public class IsoGridProfiler {

    private static final IsoGridProfiler INSTANCE = new IsoGridProfiler();

    public enum GridStep {
        FLOOR_UPDATE,
        LIGHTING_UPDATE,
        GENERATOR_UPDATE,
        WEATHER_IMPACT,
        ROOM_UPDATE
    }

    private final Map<GridStep, LongAdder> stepTimes = new EnumMap<>(GridStep.class);
    private final Map<GridStep, LongAdder> stepCounts = new EnumMap<>(GridStep.class);

    private IsoGridProfiler() {
        for (GridStep step : GridStep.values()) {
            stepTimes.put(step, new LongAdder());
            stepCounts.put(step, new LongAdder());
        }
    }

    public static IsoGridProfiler getInstance() {
        return INSTANCE;
    }

    public void recordStep(GridStep step, long durationMicros) {
        if (!EchoConfig.getInstance().isDeepAnalysisEnabled())
            return;

        stepTimes.get(step).add(durationMicros);
        stepCounts.get(step).increment();
    }

    public void reset() {
        for (GridStep step : GridStep.values()) {
            stepTimes.get(step).reset();
            stepCounts.get(step).reset();
        }
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new ConcurrentHashMap<>();

        Map<String, Object> steps = new ConcurrentHashMap<>();
        for (GridStep step : GridStep.values()) {
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
