package com.echo.pulse;

import com.echo.EchoMod;
import com.echo.measure.FreezeDetector;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.event.lifecycle.GameTickStartEvent;
import com.pulse.event.lifecycle.GameTickEndEvent;
import com.pulse.event.gui.GuiRenderEvent;

/**
 * Pulse 이벤트 버스 어댑터
 * 
 * Pulse EventBus API를 직접 사용하여 Echo 프로파일러와 연결합니다.
 * 
 * @since 2.0.0 - Pulse Native Integration (Reflection 제거)
 */
public class PulseEventAdapter {

    private static boolean registered = false;
    private static TickProfiler tickProfiler;
    private static RenderProfiler renderProfiler;

    /**
     * Pulse 이벤트 버스에 리스너 등록
     * EchoMod.init()에서 호출됨
     */
    public static void register() {
        if (registered) {
            System.out.println("[Echo] Pulse adapter already registered");
            return;
        }

        tickProfiler = new TickProfiler();
        renderProfiler = new RenderProfiler();

        // Pulse EventBus 직접 구독 (v2.0 Native)

        // v0.9: GameTickStartEvent - 틱 시작 (계약 검증용)
        EventBus.subscribe(GameTickStartEvent.class, event -> {
            tickProfiler.onTickStart();

            // 디버그: 첫 이벤트 수신 확인
            if (event.getTick() == 1) {
                System.out.println("[Echo/DEBUG] First GameTickStartEvent received!");
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
            com.echo.fuse.ZombieProfiler.getInstance().endTick();

            // 디버그: 첫 이벤트 수신 확인
            if (event.getTick() == 1) {
                System.out.println("[Echo/DEBUG] First GameTickEndEvent received! durationMs=" + event.getDurationMs());
            }
            // 매 1000번째 틱마다 상태 출력
            if (event.getTick() % 1000 == 0) {
                System.out.printf("[Echo/DEBUG] GameTickEndEvent #%d, durationMs=%.4f%n",
                        event.getTick(), event.getDurationMs());
            }
        }, EchoMod.MOD_ID);

        // Legacy: GameTickEvent - 하위 호환성 유지 (deltaTime 기반 계약 검증)
        // GameTickEvent는 틱 완료 후 발생하므로 Pre/Post가 아닌 단일 이벤트로 처리
        EventBus.subscribe(GameTickEvent.class, event -> {
            // Contract 검증만 수행 (Start/End가 primary)
            com.echo.validation.PulseContractVerifier.getInstance().onGameTick(event.getDeltaTime());

            // 디버그: 첫 이벤트 수신 확인
            if (event.getTick() == 1) {
                System.out.println(
                        "[Echo/DEBUG] First GameTickEvent received (legacy) deltaTime=" + event.getDeltaTime());
            }
        }, EchoMod.MOD_ID);

        EventBus.subscribe(GuiRenderEvent.class, event -> {
            // 렌더 프레임 시작 알림
            PulseMetricsAdapter.onFrameStart();
            renderProfiler.onRenderPre();
        }, EchoMod.MOD_ID);

        registered = true;
        System.out.println("[Echo] Pulse event adapter registered (Native EventBus)");
        System.out.println("[Echo]   - TickProfiler: GameTickEvent");
        System.out.println("[Echo]   - RenderProfiler: GuiRenderEvent");
    }

    /**
     * 이벤트 버스에서 리스너 해제
     */
    public static void unregister() {
        if (!registered)
            return;

        // 모든 Echo 리스너 해제
        EventBus.unsubscribeAll(EchoMod.MOD_ID);

        registered = false;
        System.out.println("[Echo] Pulse event adapter unregistered");
    }

    /**
     * 등록 상태 확인
     */
    public static boolean isRegistered() {
        return registered;
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
