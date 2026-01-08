package com.fuse.governor;

import com.fuse.telemetry.ReasonStats;
import com.fuse.telemetry.TelemetryReason;
import com.pulse.api.log.PulseLogger;

/**
 * Adaptive Gate - 조건부 개입 스위치 (v2.5).
 * 
 * 평시(PASSTHROUGH): Fuse 개입 완전 비활성화 → 제로 오버헤드
 * 위기(ACTIVE): 기존 Throttle 로직 활성화
 * 
 * 상태 전이 조건:
 * - PASSTHROUGH → ACTIVE: max1s > 25ms OR avg5s > 18ms
 * - ACTIVE → PASSTHROUGH: avg5s < 12ms (3초 유지)
 * 
 * @since Fuse 2.5.0
 */
public class AdaptiveGate {

    private static final String LOG = "Fuse";

    /** Gate 상태 */
    public enum GateState {
        PASSTHROUGH, // 평시: 개입 없음
        ACTIVE // 위기: 개입 활성화
    }

    // --- 진입 임계값 (보수적) ---
    private static final double ENTRY_1S_MAX_MS = 25.0; // max1s > 25ms
    private static final double ENTRY_5S_AVG_MS = 18.0; // avg5s > 18ms

    // --- 복귀 임계값 ---
    private static final double EXIT_5S_AVG_MS = 12.0; // avg5s < 12ms
    private static final int EXIT_STABILITY_TICKS = 180; // 3초 (60fps 기준)

    // --- 상태 ---
    private GateState state = GateState.PASSTHROUGH;
    private int stabilityCounter = 0;

    // --- 진동 모니터링 (Gemini 권고) ---
    private long stateTransitions = 0;

    // --- 의존성 ---
    private final RollingTickStats stats;
    private final SpikePanicProtocol panicProtocol;
    private final ReasonStats reasonStats;

    public AdaptiveGate(RollingTickStats stats, SpikePanicProtocol panicProtocol,
            ReasonStats reasonStats) {
        this.stats = stats;
        this.panicProtocol = panicProtocol;
        this.reasonStats = reasonStats;
        PulseLogger.info(LOG, "AdaptiveGate initialized (entry: max1s>"
                + ENTRY_1S_MAX_MS + "ms OR avg5s>" + ENTRY_5S_AVG_MS
                + "ms, exit: avg5s<" + EXIT_5S_AVG_MS + "ms for "
                + EXIT_STABILITY_TICKS + " ticks)");
    }

    /**
     * 틱 시작 시 1회만 호출 - O(1) 비용.
     * 
     * ⚠️ 이 메서드 내부에서 Fast-Path 로깅 금지!
     * 상태 전이 시에만 로깅 허용.
     */
    public GateState evaluateThisTick() {
        // Panic 상태면 무조건 ACTIVE
        if (panicProtocol != null &&
                panicProtocol.getState() != SpikePanicProtocol.State.NORMAL) {
            return transitionTo(GateState.ACTIVE, TelemetryReason.PANIC_WINDOW_SPIKES);
        }

        // 데이터 부족 시 현상 유지
        if (stats == null || !stats.hasEnoughData()) {
            return state;
        }

        double max1s = stats.getLast1sMaxMs();
        double avg5s = stats.getLast5sAvgMs();

        switch (state) {
            case PASSTHROUGH:
                // 진입 조건: 스파이크 또는 평균 초과
                if (max1s > ENTRY_1S_MAX_MS || avg5s > ENTRY_5S_AVG_MS) {
                    return transitionTo(GateState.ACTIVE,
                            TelemetryReason.ADAPTIVE_GATE_ACTIVATED);
                }
                break;

            case ACTIVE:
                // 복귀 조건: 평균이 안정화되고 3초 유지
                if (avg5s < EXIT_5S_AVG_MS) {
                    stabilityCounter++;
                    if (stabilityCounter >= EXIT_STABILITY_TICKS) {
                        return transitionTo(GateState.PASSTHROUGH,
                                TelemetryReason.ADAPTIVE_GATE_PASSTHROUGH);
                    }
                } else {
                    stabilityCounter = 0; // 안정성 깨짐
                }
                break;
        }

        return state;
    }

    /**
     * 상태 전이 (로깅은 여기서만).
     */
    private GateState transitionTo(GateState newState, TelemetryReason reason) {
        if (state != newState) {
            // 상태 전이 시에만 로그 출력 (Fast-Path 아님)
            PulseLogger.info(LOG, "AdaptiveGate: " + state + " → " + newState);
            state = newState;
            stateTransitions++;

            if (reasonStats != null && reason != null) {
                reasonStats.increment(reason);
            }

            if (newState == GateState.PASSTHROUGH) {
                stabilityCounter = 0;
            }
        }
        return state;
    }

    /**
     * PASSTHROUGH 상태인지 확인 (Fast-Path 체크용).
     * 
     * ⚠️ 이 메서드는 Hot Path에서 호출됨 - 로깅 금지!
     */
    public boolean isPassthrough() {
        return state == GateState.PASSTHROUGH;
    }

    public GateState getState() {
        return state;
    }

    /**
     * 상태 전이 횟수 (진동 모니터링용).
     */
    public long getStateTransitions() {
        return stateTransitions;
    }

    public int getStabilityCounter() {
        return stabilityCounter;
    }

    /**
     * 상태 리셋 (디버깅/테스트용).
     */
    public void reset() {
        state = GateState.PASSTHROUGH;
        stabilityCounter = 0;
        stateTransitions = 0;
    }
}
