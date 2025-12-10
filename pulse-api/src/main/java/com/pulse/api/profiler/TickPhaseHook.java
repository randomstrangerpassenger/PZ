package com.pulse.api.profiler;

/**
 * TickPhase Hook API
 * 
 * Echo의 TickPhaseProfiler를 Pulse Mixin에서 호출하기 위한 인터페이스.
 * Echo가 로드되지 않은 환경에서도 안전하게 동작합니다.
 * 
 * @since Pulse 1.1 / Echo 1.0
 */
public final class TickPhaseHook {

    private static volatile ITickPhaseCallback callback = null;

    private TickPhaseHook() {
    }

    /**
     * 콜백 등록 (Echo 초기화 시 호출됨)
     */
    public static void setCallback(ITickPhaseCallback cb) {
        callback = cb;
        System.out.println("[Pulse/TickPhaseHook] Callback registered: " + (cb != null));
    }

    /**
     * 콜백 해제
     */
    public static void clearCallback() {
        callback = null;
    }

    /**
     * Phase 측정 시작
     * 
     * @param phase TickPhase 이름 (예: "AI_PHASE", "PHYSICS_PHASE")
     * @return 시작 시간 (나노초), 비활성화 시 -1
     */
    public static long startPhase(String phase) {
        ITickPhaseCallback cb = callback;
        if (cb != null) {
            return cb.startPhase(phase);
        }
        return -1;
    }

    /**
     * Phase 측정 종료
     * 
     * @param phase     TickPhase 이름
     * @param startTime startPhase()에서 반환받은 시작 시간
     */
    public static void endPhase(String phase, long startTime) {
        if (startTime < 0)
            return;
        ITickPhaseCallback cb = callback;
        if (cb != null) {
            cb.endPhase(phase, startTime);
        }
    }

    /**
     * 틱 완료 알림
     */
    public static void onTickComplete() {
        ITickPhaseCallback cb = callback;
        if (cb != null) {
            cb.onTickComplete();
        }
    }

    /**
     * TickPhase 콜백 인터페이스
     */
    public interface ITickPhaseCallback {
        long startPhase(String phase);

        void endPhase(String phase, long startTime);

        void onTickComplete();
    }
}
