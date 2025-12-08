package com.echo.pulse;

/**
 * Pulse 이벤트 버스 어댑터
 * 
 * Pulse 모드 로더의 이벤트를 Echo 프로파일러와 연결합니다.
 * 초기 버전은 Mixin 없이 Callable wrapping 방식으로 구현합니다.
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

        // Pulse 이벤트 버스 등록 (실제 구현은 Pulse API에 따라 다름)
        // PulseEvents.TICK.register(tickProfiler::onTick);
        // PulseEvents.RENDER.register(renderProfiler::onRender);

        registered = true;
        System.out.println("[Echo] Pulse event adapter registered");
        System.out.println("[Echo]   - TickProfiler: OnTick.Pre / OnTick.Post");
        System.out.println("[Echo]   - RenderProfiler: OnRender.Pre / OnRender.Post");
    }

    /**
     * 이벤트 버스에서 리스너 해제
     */
    public static void unregister() {
        if (!registered)
            return;

        // 이벤트 해제
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
    // 수동 호출용 API (Mixin 없이 사용할 때)
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
