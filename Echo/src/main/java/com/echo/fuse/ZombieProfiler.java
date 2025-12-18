package com.echo.fuse;

import com.echo.config.EchoConfig;
import java.util.EnumMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.LongAdder;

/**
 * Zombie Profiler for Fuse Deep Analysis.
 * Tracks detailed timing for individual zombie update steps.
 * 
 * @since Echo 1.0 Phase 4
 */
public class ZombieProfiler {

    private static final ZombieProfiler INSTANCE = new ZombieProfiler();

    public enum ZombieStep {
        MOTION_UPDATE,
        SOUND_PERCEPTION,
        TARGET_TRACKING,
        COLLISION,
        BEHAVIOR_TICK,
        // Phase 1 추가: IsoZombie 분석 기반
        PLAYER_DETECTION, // spotted() 메서드
        PATH_RECALC, // pathToCharacter() 경로 재계산
        LOS_CHECK // 시야 확인 (Line of Sight)
    }

    private final Map<ZombieStep, LongAdder> stepTimes = new EnumMap<>(ZombieStep.class);
    private final Map<ZombieStep, LongAdder> stepCounts = new EnumMap<>(ZombieStep.class);
    private final LongAdder totalZombiesUpdated = new LongAdder(); // Total zombie update calls
    private final LongAdder tickZombiesUpdated = new LongAdder(); // Per-tick updates

    private ZombieProfiler() {
        for (ZombieStep step : ZombieStep.values()) {
            stepTimes.put(step, new LongAdder());
            stepCounts.put(step, new LongAdder());
        }
    }

    public static ZombieProfiler getInstance() {
        return INSTANCE;
    }

    public void recordStep(ZombieStep step, long durationMicros) {
        if (!EchoConfig.getInstance().isDeepAnalysisEnabled())
            return;

        stepTimes.get(step).add(durationMicros);
        stepCounts.get(step).increment();
    }

    public void incrementZombieUpdates() {
        if (!EchoConfig.getInstance().isDeepAnalysisEnabled())
            return;
        totalZombiesUpdated.increment();
        tickZombiesUpdated.increment();
    }

    public long getZombieCount() {
        return totalZombiesUpdated.sum();
    }

    public long getTickZombieCount() {
        return tickZombiesUpdated.sum();
    }

    public void endTick() {
        tickZombiesUpdated.reset();
    }

    public void reset() {
        for (ZombieStep step : ZombieStep.values()) {
            stepTimes.get(step).reset();
            stepCounts.get(step).reset();
        }
        totalZombiesUpdated.reset();
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new ConcurrentHashMap<>();
        map.put("total_updates", totalZombiesUpdated.sum());

        Map<String, Object> steps = new ConcurrentHashMap<>();
        for (ZombieStep step : ZombieStep.values()) {
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
