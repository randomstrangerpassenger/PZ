package com.echo.spi;

import com.pulse.api.spi.IProfilerProvider;
import com.pulse.api.spi.Priority;
import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.aggregate.TimingData;

/**
 * Echo의 IProfilerProvider 구현.
 * Pulse SPI를 통해 다른 모드와 연동 가능.
 */
public class EchoProfilerProvider implements IProfilerProvider {

    private static final String ID = "echo";
    private static final String NAME = "Echo Profiler";
    private static final String VERSION = "1.0.0";

    private final EchoProfiler profiler;
    private boolean enabled = true;

    public EchoProfilerProvider() {
        this.profiler = EchoProfiler.getInstance();
    }

    // ============================================================
    // IProvider 기본 메서드
    // ============================================================

    @Override
    public String getId() {
        return ID;
    }

    @Override
    public String getName() {
        return NAME;
    }

    @Override
    public String getVersion() {
        return VERSION;
    }

    @Override
    public String getDescription() {
        return "Real-time performance profiling tool for Project Zomboid";
    }

    @Override
    public int getPriority() {
        return Priority.HIGH; // 프로파일러는 높은 우선순위
    }

    @Override
    public void onInitialize() {
        System.out.println("[Echo] ProfilerProvider initialized");
        profiler.enable();
    }

    @Override
    public void onShutdown() {
        System.out.println("[Echo] ProfilerProvider shutting down");
        profiler.disable();
    }

    @Override
    public boolean isEnabled() {
        return enabled;
    }

    // ============================================================
    // IProfilerProvider 구현
    // ============================================================

    @Override
    public void onTickStart() {
        profiler.push(ProfilingPoint.TICK);
    }

    @Override
    public void onTickEnd(long tickTimeNanos) {
        profiler.pop(ProfilingPoint.TICK);
    }

    @Override
    public void onFrameStart() {
        profiler.push(ProfilingPoint.RENDER);
    }

    @Override
    public void onFrameEnd(long frameTimeNanos) {
        profiler.pop(ProfilingPoint.RENDER);
    }

    @Override
    public double getCurrentFps() {
        TimingData renderData = profiler.getTimingData(ProfilingPoint.RENDER);
        if (renderData != null && renderData.getCallCount() > 0) {
            double avgMicros = renderData.getStats1s().getAverage();
            if (avgMicros > 0) {
                return 1_000_000.0 / avgMicros;
            }
        }
        return 60.0; // 기본값
    }

    @Override
    public double getAverageTickTimeMs() {
        TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);
        if (tickData != null && tickData.getCallCount() > 0) {
            return tickData.getStats1s().getAverage() / 1000.0; // micros to ms
        }
        return 16.67; // 기본값
    }

    @Override
    public double getAverageFrameTimeMs() {
        TimingData renderData = profiler.getTimingData(ProfilingPoint.RENDER);
        if (renderData != null && renderData.getCallCount() > 0) {
            return renderData.getStats1s().getAverage() / 1000.0; // micros to ms
        }
        return 16.67; // 기본값
    }

    @Override
    public void startProfiling() {
        profiler.enable();
        enabled = true;
        System.out.println("[Echo] Profiling started");
    }

    @Override
    public void stopProfiling() {
        profiler.disable();
        enabled = false;
        System.out.println("[Echo] Profiling stopped");
    }

    @Override
    public boolean isProfiling() {
        return profiler.isEnabled();
    }

    @Override
    public void resetData() {
        profiler.reset();
        System.out.println("[Echo] Profiling data reset");
    }

    // ============================================================
    // Echo 전용 확장 메서드
    // ============================================================

    /**
     * 내부 EchoProfiler 인스턴스 접근
     */
    public EchoProfiler getProfiler() {
        return profiler;
    }

    /**
     * 특정 ProfilingPoint의 데이터 조회
     */
    public TimingData getTimingData(ProfilingPoint point) {
        return profiler.getTimingData(point);
    }
}
