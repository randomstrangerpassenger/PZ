package com.echo.pulse;

import com.echo.subsystem.ZombieProfiler;
import com.pulse.api.di.PulseServices;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.IProfilerSink;

/**
 * Echo의 ProfilerSink 구현.
 * 
 * Pulse의 ProfilerBridge에 등록되어,
 * Fuse가 보내는 zombie step 데이터를 ZombieProfiler로 전달.
 * 
 * @since Echo 2.0
 */
public class EchoProfilerSink implements IProfilerSink {

    private static EchoProfilerSink INSTANCE;

    private EchoProfilerSink() {
    }

    public static void register() {
        try {
            INSTANCE = new EchoProfilerSink();
            PulseServices.profiler().setSink(INSTANCE);
            PulseLogger.info("Echo", "ProfilerSink registered with Pulse");
        } catch (Exception t) {
            PulseLogger.error("Echo", "Failed to register ProfilerSink: " + t.getMessage(), t);
        }
    }

    public static void unregister() {
        try {
            PulseServices.profiler().clearSink();
        } catch (Exception ignored) {
        }
        INSTANCE = null;
    }

    @Override
    public void onTickProfile(long tickNumber, long durationNanos) {
        // Forward to tick profiling if needed
    }

    @Override
    public void onRenderProfile(long frameNumber, long durationNanos) {
        // Forward to render profiling if needed
    }

    /**
     * Zombie step recording (v2.5 - called via reflection from
     * ProfilerSinkWrapper).
     */
    public void recordZombieStep(String step, long durationMicros) {
        try {
            ZombieProfiler.ZombieStep zombieStep = ZombieProfiler.ZombieStep.valueOf(step);
            ZombieProfiler.getInstance().recordStep(zombieStep, durationMicros);
        } catch (IllegalArgumentException e) {
            // Unknown step name, ignore
        }
    }

    /**
     * Increment zombie update count (v2.5 - called via reflection from
     * ProfilerSinkWrapper).
     */
    public void incrementZombieUpdates() {
        ZombieProfiler.getInstance().incrementZombieUpdates();
    }
}
