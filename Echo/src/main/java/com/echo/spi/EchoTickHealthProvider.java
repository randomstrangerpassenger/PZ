package com.echo.spi;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.aggregate.TimingData;
import com.pulse.api.spi.ITickHealthProvider;
import com.pulse.api.spi.Priority;

/**
 * Echo 기반 Tick Health Provider.
 * 
 * Pulse SPI(ITickHealthProvider) 구현체.
 * Echo의 프로파일링 데이터를 기반으로 Tick 건강 상태 제공.
 * 
 * Nerve는 이 클래스를 직접 참조하지 않고, Pulse 레지스트리를 통해
 * ITickHealthProvider 인터페이스로만 접근함.
 * 
 * @since Echo 1.1
 */
public class EchoTickHealthProvider implements ITickHealthProvider {

    private static final String PROVIDER_ID = "echo-tick-health";
    private static final String PROVIDER_NAME = "Echo Tick Health Provider";
    private static final String VERSION = "1.1.0";

    // --- 임계값 ---
    private static final double SLOW_TICK_THRESHOLD_MS = 33.33; // 30fps 기준
    private static final int SPIKE_WINDOW_SECONDS = 5;

    // --- 캐시 (틱당 계산 최소화) ---
    private volatile boolean slowTickCached = false;
    private volatile int spikeCountCached = 0;
    private volatile double last1sMaxCached = 0.0;
    private volatile double last5sAvgCached = 0.0;
    private volatile long lastUpdateTick = -1;

    private EchoProfiler profiler;

    public EchoTickHealthProvider() {
        // Profiler는 나중에 설정 (lazy init)
    }

    /**
     * EchoProfiler 참조 설정.
     * Echo 초기화 시 호출.
     */
    public void setProfiler(EchoProfiler profiler) {
        this.profiler = profiler;
    }

    /**
     * 틱마다 호출하여 데이터 갱신.
     * EchoMod.onTick()에서 호출.
     */
    public void update() {
        if (profiler == null) {
            return;
        }

        long currentTick = profiler.getTickHistogram().getTotalSamples();
        if (currentTick == lastUpdateTick) {
            return; // 이미 이번 틱에 갱신됨
        }
        lastUpdateTick = currentTick;

        try {
            TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);
            if (tickData != null) {
                TimingData.RollingStats stats1s = tickData.getStats1s();
                TimingData.RollingStats stats5s = tickData.getStats5s();

                // 1초 내 최대값
                last1sMaxCached = stats1s.getMax() / 1000.0;

                // 5초 평균
                last5sAvgCached = stats5s.getAverage() / 1000.0;

                // SlowTick 판정
                slowTickCached = last1sMaxCached > SLOW_TICK_THRESHOLD_MS;

                // 스파이크 카운트 (최근 N초 내 스파이크 수)
                // SpikeLog.getAllSpikes()에서 timestamp 기반으로 필터링
                spikeCountCached = countRecentSpikes(SPIKE_WINDOW_SECONDS);
            }
        } catch (Exception e) {
            // 오류 시 안전 기본값
            slowTickCached = false;
            spikeCountCached = 0;
        }
    }

    /**
     * 최근 N초 내 스파이크 수 계산.
     */
    @SuppressWarnings("unused") // windowSeconds 파라미터는 향후 정밀 필터링에 사용 예정
    private int countRecentSpikes(int windowSeconds) {
        if (profiler == null) {
            return 0;
        }
        // SpikeLog의 총 스파이크 수 반환 (단순화)
        // 더 정밀한 시간 기반 필터링이 필요하면 getAllSpikes() 사용
        return (int) Math.min(profiler.getSpikeLog().getTotalSpikes(), Integer.MAX_VALUE);
    }

    // ===================================
    // ITickHealthProvider 구현
    // ===================================

    @Override
    public boolean isSlowTick() {
        return slowTickCached;
    }

    @Override
    public int getRecentSpikeCount() {
        return spikeCountCached;
    }

    @Override
    public double getLast1sMaxMs() {
        return last1sMaxCached;
    }

    @Override
    public double getLast5sAvgMs() {
        return last5sAvgCached;
    }

    // ===================================
    // IProvider 구현
    // ===================================

    @Override
    public String getId() {
        return PROVIDER_ID;
    }

    @Override
    public String getName() {
        return PROVIDER_NAME;
    }

    @Override
    public String getVersion() {
        return VERSION;
    }

    @Override
    public String getDescription() {
        return "Provides tick health metrics based on Echo profiling data";
    }

    @Override
    public int getPriority() {
        return Priority.NORMAL;
    }

    @Override
    public boolean isEnabled() {
        return profiler != null;
    }

    @Override
    public void onInitialize() {
        // Profiler는 setProfiler()를 통해 나중에 설정됨
    }

    @Override
    public void onShutdown() {
        // 정리 작업 없음 (profiler는 EchoMod에서 관리)
    }
}
