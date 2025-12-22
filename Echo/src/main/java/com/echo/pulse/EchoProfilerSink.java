package com.echo.pulse;

import com.echo.fuse.ZombieProfiler;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.ProfilerBridge;
import com.pulse.api.profiler.ProfilerSink;

/**
 * Echo의 ProfilerSink 구현.
 * 
 * Pulse의 ProfilerBridge에 등록되어,
 * Fuse가 보내는 zombie step 데이터를 ZombieProfiler로 전달.
 * 
 * @since Echo 2.0
 */
public class EchoProfilerSink implements ProfilerSink {

    private static EchoProfilerSink INSTANCE;

    private EchoProfilerSink() {
    }

    public static void register() {
        try {
            INSTANCE = new EchoProfilerSink();
            ProfilerBridge.setSink(INSTANCE);
            PulseLogger.info("Echo", "ProfilerSink registered with Pulse");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "Failed to register ProfilerSink: " + t.getMessage());
        }
    }

    public static void unregister() {
        ProfilerBridge.clearSink();
        INSTANCE = null;
    }

    @Override
    public void recordZombieStep(String step, long durationMicros) {
        try {
            ZombieProfiler.ZombieStep zombieStep = ZombieProfiler.ZombieStep.valueOf(step);
            ZombieProfiler.getInstance().recordStep(zombieStep, durationMicros);
        } catch (IllegalArgumentException e) {
            // Unknown step name, ignore
        }
    }

    @Override
    public void incrementZombieUpdates() {
        ZombieProfiler.getInstance().incrementZombieUpdates();
    }
}
