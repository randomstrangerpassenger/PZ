package com.echo.pulse;

import com.echo.EchoMod;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;
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
        EventBus.subscribe(GameTickEvent.class, event -> {
            tickProfiler.onTickPre();
            // 틱 처리는 이벤트 핸들러가 완료된 후 측정
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

    // ============================================================
    // 수동 호출용 API (Mixin 사용 시 또는 테스팅용)
    // ============================================================

    /**
     * 틱 시작 시 호출 (수동)
     */
    public static void onTickStart() {
        if (tickProfiler != null) {
            tickProfiler.onTickPre();
        }
    }

    /**
     * 틱 종료 시 호출 (수동)
     */
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
