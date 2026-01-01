package com.echo.pulse;

import com.echo.EchoMod;
import com.echo.measure.EchoProfiler;
import com.echo.measure.FreezeDetector;
import com.echo.measure.ProfilingPoint;
import com.echo.session.SessionManager;
import com.pulse.api.di.PulseServices;
import com.pulse.api.event.IEventBus;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.event.lifecycle.GameTickStartEvent;
import com.pulse.api.event.lifecycle.GameTickEndEvent;
import com.pulse.api.event.lifecycle.GameTickEvent;
import com.pulse.api.event.lifecycle.WorldLoadEvent;
import com.pulse.api.event.lifecycle.WorldUnloadEvent;
import com.pulse.api.event.lifecycle.MainMenuRenderEvent;
import com.pulse.api.event.gui.GuiRenderEvent;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Pulse 이벤트 버스 어댑터
 * 
 * PulseServices.events() API를 사용하여 Echo 프로파일러와 연결합니다.
 * 
 * @since 2.0.0 - Pulse Native Integration (Reflection 제거)
 * @since 2.1.0 - Session-based recording (WorldLoad/Unload)
 * @since 3.0.0 - Phase 3: EventBus → PulseServices.events() 마이그레이션
 */
public class PulseEventAdapter {

    private static final AtomicBoolean registered = new AtomicBoolean(false);
    private static TickProfiler tickProfiler;
    private static RenderProfiler renderProfiler;

    /**
     * Pulse 이벤트 버스에 리스너 등록
     * EchoMod.init()에서 호출됨
     */
    public static void register() {
        if (!registered.compareAndSet(false, true)) {
            PulseLogger.debug("Echo", "Pulse adapter already registered");
            return;
        }

        tickProfiler = new TickProfiler();
        renderProfiler = new RenderProfiler();

        // Phase 3: PulseServices.events() 사용 (컴파일 타임 pulse-api 의존)
        IEventBus events = PulseServices.events();

        // v0.9: GameTickStartEvent - 틱 시작 (계약 검증용)
        events.subscribe(GameTickStartEvent.class, event -> {
            tickProfiler.onTickStart();
            if (event.getTick() == 1) {
                PulseLogger.debug("Echo", "First GameTickStartEvent received!");
            }
        }, EchoMod.MOD_ID);

        // v0.9: GameTickEndEvent - 정밀 틱 소요 시간 기록 (Primary API)
        events.subscribe(GameTickEndEvent.class, event -> {
            FreezeDetector.getInstance().tick();
            tickProfiler.recordTickDuration(event.getDurationNanos());
            // Fix: Also update PulseContractVerifier tick count (converts ms to seconds)
            com.echo.validation.PulseContractVerifier.getInstance()
                    .onGameTick((float) (event.getDurationMs() / 1000.0));
            // TODO: TickProfiler inner class type mismatch with MetricCollector - needs API
            // alignment
            // com.echo.measure.EchoProfiler.getInstance().getMetricCollector().collect(tickProfiler,
            // renderProfiler);
            com.echo.subsystem.ZombieProfiler.getInstance().endTick();
            SessionManager.getInstance().onTick();

            if (event.getTick() > 0 && event.getTick() % 3600 == 0) {
                logEchoStatusSummary();
            }
            if (event.getTick() == 1) {
                PulseLogger.debug("Echo", "First GameTickEndEvent received! durationMs=" + event.getDurationMs());
            }
            if (event.getTick() % 1000 == 0) {
                PulseLogger.debug("Echo", String.format("GameTickEndEvent #%d, durationMs=%.4f",
                        event.getTick(), event.getDurationMs()));
            }
        }, EchoMod.MOD_ID);

        // Legacy: GameTickEvent - 하위 호환성 유지
        events.subscribe(GameTickEvent.class, event -> {
            com.echo.validation.PulseContractVerifier.getInstance().onGameTick(event.getDeltaTime());
            if (event.getTick() == 1) {
                PulseLogger.debug("Echo", "First GameTickEvent received (legacy) deltaTime=" + event.getDeltaTime());
            }
        }, EchoMod.MOD_ID);

        events.subscribe(GuiRenderEvent.class, event -> {
            PulseMetricsAdapter.onFrameStart();
            renderProfiler.onRenderPre();
        }, EchoMod.MOD_ID);

        // v2.1: 세션 라이프사이클 이벤트
        events.subscribe(WorldLoadEvent.class, event -> {
            boolean isMP = isMultiplayerWorld();
            SessionManager.getInstance().onWorldLoad(event.getWorldName(), isMP);
            // v2.2: Reset profilers on world load for accurate session-based FPS
            if (tickProfiler != null)
                tickProfiler.reset();
            if (renderProfiler != null)
                renderProfiler.reset();
            PulseLogger.debug("Echo", "Profilers reset on world load");

            // v2.3: Schedule Self-validation 60 seconds after world load
            // This ensures validation runs when actual game data (zombies, ticks) is
            // available
            com.echo.validation.SelfValidation.getInstance().scheduleValidation();
            PulseLogger.info("Echo", "Self-validation scheduled (60s after world load)");
        }, EchoMod.MOD_ID);

        events.subscribe(WorldUnloadEvent.class, event -> {
            SessionManager.getInstance().onWorldUnload();
        }, EchoMod.MOD_ID);

        // v2.1: 메인 메뉴 렌더 이벤트 구독 - 세션 종료 감지
        events.subscribe(MainMenuRenderEvent.class, event -> {
            SessionManager.getInstance().onMainMenuRender();
        }, EchoMod.MOD_ID);

        // Lua Call Hook (On-Demand profiling)
        LuaHookAdapter.register();

        PulseLogger.info("Echo", "Pulse event adapter registered (IEventBus API, Phase 3)");
    }

    /**
     * Pulse 이벤트 버스에서 리스너 해제
     */
    public static void unregister() {
        if (!registered.compareAndSet(true, false)) {
            return;
        }

        PulseServices.events().unsubscribeAll(EchoMod.MOD_ID);
        LuaHookAdapter.unregister();

        PulseLogger.info("Echo", "Pulse event adapter unregistered");
    }

    public static TickProfiler getTickProfiler() {
        return tickProfiler;
    }

    public static RenderProfiler getRenderProfiler() {
        return renderProfiler;
    }

    private static boolean isMultiplayerWorld() {
        // TODO: PZ stubs needed for zombie.network.GameClient access
        // Simplified to avoid compile-time dependency
        return false;
    }

    private static void logEchoStatusSummary() {
        double avgFps = renderProfiler != null ? renderProfiler.getAverageFps() : -1;
        double avgTick = tickProfiler != null ? tickProfiler.getAverageTickMs() : -1;
        PulseLogger.info("Echo", String.format("[Echo Status] avgFps=%.1f, avgTickMs=%.2f", avgFps, avgTick));
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // TickProfiler - 게임 틱 통계
    // ─────────────────────────────────────────────────────────────────────────────

    public static class TickProfiler {
        private long tickCount = 0;
        private long totalDurationNanos = 0;
        private double lastDurationMs = 0;
        private double peakDurationMs = 0;

        public void onTickStart() {
            // Tick start timing - duration is calculated by IsoWorldMixin and passed via
            // GameTickEndEvent
        }

        public void recordTickDuration(long durationNanos) {
            tickCount++;
            totalDurationNanos += durationNanos;
            lastDurationMs = durationNanos / 1_000_000.0;
            if (lastDurationMs > peakDurationMs) {
                peakDurationMs = lastDurationMs;
            }

            // Fix: Record timing data to EchoProfiler so total_ticks is properly counted
            EchoProfiler profiler = EchoProfiler.getInstance();
            if (profiler.isEnabled()) {
                profiler.getTimingData(ProfilingPoint.TICK).addSample(durationNanos, null);

                // Also record to histogram
                long durationMicros = durationNanos / 1000;
                if (profiler.getSessionDurationMs() < 3000) {
                    profiler.getTickHistogram().addWarmupSample(durationMicros);
                } else {
                    profiler.getTickHistogram().addSample(durationMicros);
                }
            }
        }

        public long getTickCount() {
            return tickCount;
        }

        public double getLastDurationMs() {
            return lastDurationMs;
        }

        public double getPeakDurationMs() {
            return peakDurationMs;
        }

        public double getAverageTickMs() {
            if (tickCount == 0)
                return 0;
            return (totalDurationNanos / 1_000_000.0) / tickCount;
        }

        public void reset() {
            tickCount = 0;
            totalDurationNanos = 0;
            lastDurationMs = 0;
            peakDurationMs = 0;
        }
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // RenderProfiler - 렌더 프레임 통계
    // ─────────────────────────────────────────────────────────────────────────────

    public static class RenderProfiler {
        private long frameCount = 0;
        private long startTimeMs = System.currentTimeMillis();

        public void onRenderPre() {
            frameCount++;
            if (frameCount % 3600 == 0) {
                long elapsed = System.currentTimeMillis() - startTimeMs;
                if (elapsed > 0) {
                    double fps = (frameCount * 1000.0) / elapsed;
                    PulseLogger.debug("Echo",
                            String.format("RenderProfiler: %d frames, avg %.1f FPS", frameCount, fps));
                }
            }
        }

        public long getFrameCount() {
            return frameCount;
        }

        public double getAverageFps() {
            long elapsed = System.currentTimeMillis() - startTimeMs;
            if (elapsed <= 0)
                return 0;
            return (frameCount * 1000.0) / elapsed;
        }

        public void reset() {
            frameCount = 0;
            startTimeMs = System.currentTimeMillis();
        }
    }
}
