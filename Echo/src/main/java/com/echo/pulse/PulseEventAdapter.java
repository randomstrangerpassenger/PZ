package com.echo.pulse;

import com.echo.EchoMod;
import com.echo.measure.FreezeDetector;
import com.echo.session.SessionManager;
import com.pulse.api.log.PulseLogger;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.event.lifecycle.GameTickStartEvent;
import com.pulse.event.lifecycle.GameTickEndEvent;
import com.pulse.event.lifecycle.WorldLoadEvent;
import com.pulse.event.lifecycle.WorldUnloadEvent;
import com.pulse.event.gui.GuiRenderEvent;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Pulse 이벤트 버스 어댑터
 * 
 * Pulse EventBus API를 직접 사용하여 Echo 프로파일러와 연결합니다.
 * 
 * @since 2.0.0 - Pulse Native Integration (Reflection 제거)
 * @since 2.1.0 - Session-based recording (WorldLoad/Unload)
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

        // Pulse EventBus 직접 구독 (v2.0 Native)

        // v0.9: GameTickStartEvent - 틱 시작 (계약 검증용)
        EventBus.subscribe(GameTickStartEvent.class, event -> {
            tickProfiler.onTickStart();

            if (event.getTick() == 1) {
                PulseLogger.debug("Echo", "First GameTickStartEvent received!");
            }
        }, EchoMod.MOD_ID);

        // v0.9: GameTickEndEvent - 정밀 틱 소요 시간 기록 (Primary API)
        EventBus.subscribe(GameTickEndEvent.class, event -> {
            // Echo 1.0: FreezeDetector 생존 신고
            FreezeDetector.getInstance().tick();

            // 정밀 타이밍 기록 (Pulse에서 계산한 nanos 사용)
            tickProfiler.recordTickDuration(event.getDurationNanos());

            // Phase 3: Metric Collection
            com.echo.measure.EchoProfiler.getInstance().getMetricCollector().collect(tickProfiler, renderProfiler);
            com.echo.subsystem.ZombieProfiler.getInstance().endTick();

            // v2.1: 세션 데이터 수집 마킹
            SessionManager.getInstance().onTick();

            // v1.1: 주기적 Echo 상태 로깅 (60초마다)
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

        // Legacy: GameTickEvent - 하위 호환성 유지 (deltaTime 기반 계약 검증)
        // GameTickEvent는 틱 완료 후 발생하므로 Pre/Post가 아닌 단일 이벤트로 처리
        EventBus.subscribe(GameTickEvent.class, event -> {
            // Contract 검증만 수행 (Start/End가 primary)
            com.echo.validation.PulseContractVerifier.getInstance().onGameTick(event.getDeltaTime());

            if (event.getTick() == 1) {
                PulseLogger.debug("Echo", "First GameTickEvent received (legacy) deltaTime=" + event.getDeltaTime());
            }
        }, EchoMod.MOD_ID);

        EventBus.subscribe(GuiRenderEvent.class, event -> {
            // 렌더 프레임 시작 알림
            PulseMetricsAdapter.onFrameStart();
            renderProfiler.onRenderPre();
        }, EchoMod.MOD_ID);

        // v2.1: 세션 라이프사이클 이벤트
        EventBus.subscribe(WorldLoadEvent.class, event -> {
            boolean isMP = isMultiplayerWorld();
            SessionManager.getInstance().onWorldLoad(event.getWorldName(), isMP);
        }, EchoMod.MOD_ID);

        EventBus.subscribe(WorldUnloadEvent.class, event -> {
            SessionManager.getInstance().onWorldUnload();
        }, EchoMod.MOD_ID);

        // v2.1: 메인 메뉴 렌더 이벤트 구독 - 세션 종료 감지
        EventBus.subscribe(com.pulse.event.lifecycle.MainMenuRenderEvent.class, event -> {
            SessionManager.getInstance().onMainMenuRender();
        }, EchoMod.MOD_ID);

        // Lua Call Hook (On-Demand profiling)
        LuaHookAdapter.register();

        try {
            com.echo.lua.DetailedWindowManager.getInstance()
                    .startManualCapture(5000);
            PulseLogger.info("Echo", "✓ Initial Detailed Window opened (5s auto-capture)");
        } catch (Exception e) {
            PulseLogger.error("Echo", "Failed to open initial Detailed Window: " + e.getMessage());
        }

        PulseLogger.info("Echo", "Pulse event adapter registered (Native EventBus)");
        PulseLogger.debug("Echo", "- TickProfiler: GameTickEvent");
        PulseLogger.debug("Echo", "- RenderProfiler: GuiRenderEvent");
        PulseLogger.debug("Echo", "- SessionManager: WorldLoad/Unload/MainMenuRender");
        PulseLogger.debug("Echo", "- LuaHookAdapter: LUA_CALL (Auto-capture enabled)");
    }

    /**
     * 이벤트 버스에서 리스너 해제
     */
    public static void unregister() {
        if (!registered.compareAndSet(true, false))
            return;

        // 모든 Echo 리스너 해제
        EventBus.unsubscribeAll(EchoMod.MOD_ID);

        // Lua Hook 해제
        LuaHookAdapter.unregister();

        PulseLogger.info("Echo", "Pulse event adapter unregistered");
    }

    /**
     * 등록 상태 확인
     */
    public static boolean isRegistered() {
        return registered.get();
    }

    /**
     * 멀티플레이어 환경인지 확인
     */
    private static boolean isMultiplayerWorld() {
        try {
            Class<?> gameClient = Class.forName("zombie.network.GameClient");
            java.lang.reflect.Field bClient = gameClient.getField("bClient");
            return Boolean.TRUE.equals(bClient.get(null));
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * v1.1: 주기적 Echo 상태 요약 로깅 (60초마다).
     * PulseContractVerifier의 stall_events 분리 확인용.
     */
    private static void logEchoStatusSummary() {
        try {
            com.echo.validation.PulseContractVerifier verifier = com.echo.validation.PulseContractVerifier
                    .getInstance();

            StringBuilder sb = new StringBuilder();
            sb.append("\n========== [Echo v1.1] 60s Status Summary ==========\n");
            sb.append("  Contract Status: ").append(verifier.getStatusForDisplay()).append("\n");
            sb.append("  True Violations: ").append(verifier.getTotalViolationCount()).append("\n");
            sb.append("  Stall Events: ").append(verifier.getStallEventCount()).append("\n");

            // Freeze 정보
            com.echo.measure.FreezeDetector detector = com.echo.measure.FreezeDetector.getInstance();
            sb.append("  Freezes (main loop): ").append(detector.getMainLoopFreezes().size()).append("\n");
            sb.append("  Freezes (all): ").append(detector.getRecentFreezes().size()).append("\n");

            sb.append("====================================================\n");

            PulseLogger.info("Echo", sb.toString());
        } catch (Exception e) {
            PulseLogger.warn("Echo", "Failed to log status summary: " + e.getMessage());
        }
    }

    /**
     * TickProfiler 인스턴스 반환
     */
    public static TickProfiler getTickProfiler() {
        return tickProfiler;
    }

    /**
     * RenderProfiler 인스턴스 반환
     */
    public static RenderProfiler getRenderProfiler() {
        return renderProfiler;
    }

    // --- Legacy Manual API ---

    /**
     * 틱 시작 시 호출 (수동)
     * 
     * @deprecated Use GameTickEvent-based profiling instead
     */
    @Deprecated
    public static void onTickStart() {
        if (tickProfiler != null) {
            tickProfiler.onTickPre();
        }
    }

    /**
     * 틱 종료 시 호출 (수동)
     * 
     * @deprecated Use GameTickEvent-based profiling instead
     */
    @Deprecated
    public static void onTickEnd() {
        if (tickProfiler != null) {
            tickProfiler.onTickPost();
        }
    }

    /**
     * 렌더 시작 시 호출 (수동)
     */
    public static void onRenderStart() {
        // PulseMetricsAdapter에 프레임 시작 알림
        PulseMetricsAdapter.onFrameStart();

        if (renderProfiler != null) {
            renderProfiler.onRenderPre();
        }
    }

    /**
     * 렌더 종료 시 호출 (수동)
     */
    public static void onRenderEnd() {
        if (renderProfiler != null) {
            renderProfiler.onRenderPost();
        }
    }
}
