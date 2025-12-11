package com.pulse.api.profiler;

import com.pulse.api.FailsoftPolicy;

/**
 * TickPhase Hook API
 * 
 * Echo의 TickPhaseProfiler를 Pulse Mixin에서 호출하기 위한 인터페이스.
 * Echo가 로드되지 않은 환경에서도 안전하게 동작합니다.
 * 
 * v0.9: Phase 시퀀스 검증 및 자동 state reset 추가
 * 
 * @since Pulse 1.1 / Echo 1.0
 * @since Pulse 0.9 - Phase sequence validation
 */
public final class TickPhaseHook {

    private static volatile ITickPhaseCallback callback = null;

    // v0.9: Phase state tracking for sequence validation
    private static volatile String currentOpenPhase = null;
    private static volatile long currentPhaseStartTime = -1;

    // 경고 스로틀링 (처음 3회만 출력)
    private static volatile int phaseErrorCount = 0;
    private static final int MAX_PHASE_WARNINGS = 3;

    // ═══════════════════════════════════════════════════════════════
    // v0.9: Predefined Phase 상수 (Echo TickPhaseBridge 매핑용)
    // ═══════════════════════════════════════════════════════════════
    public static final String PHASE_WORLD_UPDATE = "PULSE_WORLD_UPDATE";
    public static final String PHASE_AI_UPDATE = "PULSE_AI_UPDATE";
    public static final String PHASE_PHYSICS_UPDATE = "PULSE_PHYSICS_UPDATE";
    public static final String PHASE_ZOMBIE_UPDATE = "PULSE_ZOMBIE_UPDATE";
    public static final String PHASE_PLAYER_UPDATE = "PULSE_PLAYER_UPDATE";
    public static final String PHASE_RENDER_PREP = "PULSE_RENDER_PREP";
    public static final String PHASE_ISOGRID_UPDATE = "PULSE_ISOGRID_UPDATE";

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
        // v0.9: 이전 phase가 닫히지 않았으면 경고 후 자동 리셋
        if (currentOpenPhase != null) {
            reportPhaseSequenceError("startPhase('" + phase + "') called but '"
                    + currentOpenPhase + "' was not closed");
            // 자동 리셋
            currentOpenPhase = null;
            currentPhaseStartTime = -1;
        }

        // 현재 phase 추적
        currentOpenPhase = phase;
        currentPhaseStartTime = System.nanoTime();

        ITickPhaseCallback cb = callback;
        if (cb != null) {
            return cb.startPhase(phase);
        }
        return currentPhaseStartTime;
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

        // v0.9: Phase 순서 검증
        if (currentOpenPhase == null) {
            reportPhaseSequenceError("endPhase('" + phase + "') called but no phase is open");
        } else if (!currentOpenPhase.equals(phase)) {
            reportPhaseSequenceError("endPhase('" + phase + "') called but '"
                    + currentOpenPhase + "' is open");
        }

        // 상태 리셋
        currentOpenPhase = null;
        currentPhaseStartTime = -1;

        ITickPhaseCallback cb = callback;
        if (cb != null) {
            cb.endPhase(phase, startTime);
        }
    }

    /**
     * 틱 완료 알림
     * 
     * v0.9: 틱 끝에 열린 phase가 있으면 자동 리셋
     */
    public static void onTickComplete() {
        // v0.9: Phase state validation - 열린 phase 자동 리셋
        if (currentOpenPhase != null) {
            reportPhaseSequenceError("Tick ended but phase '" + currentOpenPhase + "' was not closed");
            currentOpenPhase = null;
            currentPhaseStartTime = -1;
        }

        ITickPhaseCallback cb = callback;
        if (cb != null) {
            cb.onTickComplete();
        }
    }

    /**
     * v0.9: Phase 시퀀스 에러 보고
     */
    private static void reportPhaseSequenceError(String detail) {
        phaseErrorCount++;

        // FailsoftPolicy로 보고
        FailsoftPolicy.report(FailsoftPolicy.Action.PHASE_SEQUENCE_ERROR, detail, "TickPhaseHook");

        // 처음 몇 번만 콘솔 경고 출력
        if (phaseErrorCount <= MAX_PHASE_WARNINGS) {
            System.err.println("[Pulse/TickPhaseHook] Phase sequence error: " + detail);
            if (phaseErrorCount == MAX_PHASE_WARNINGS) {
                System.err.println("[Pulse/TickPhaseHook] (Further phase warnings suppressed)");
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // v0.9: 상태 조회 API
    // ═══════════════════════════════════════════════════════════════

    /**
     * 현재 열린 phase 이름 반환
     */
    public static String getCurrentOpenPhase() {
        return currentOpenPhase;
    }

    /**
     * Phase 에러 카운트 반환
     */
    public static int getPhaseErrorCount() {
        return phaseErrorCount;
    }

    /**
     * 상태 리셋 (테스트용)
     */
    public static void reset() {
        currentOpenPhase = null;
        currentPhaseStartTime = -1;
        phaseErrorCount = 0;
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
