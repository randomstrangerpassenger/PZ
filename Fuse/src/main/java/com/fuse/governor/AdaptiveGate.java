package com.fuse.governor;

import com.fuse.config.FuseConfig;
import com.fuse.telemetry.ReasonStats;
import com.fuse.telemetry.TelemetryReason;
import com.pulse.api.log.PulseLogger;

/**
 * Adaptive Gate - 조건부 개입 스위치 (v2.6 Bundle C).
 * 
 * 평시(PASSTHROUGH): Fuse 개입 완전 비활성화 → 제로 오버헤드
 * 위기(ACTIVE): 기존 Throttle 로직 활성화
 * 강제휴식(COOLDOWN): Bundle C - 개입 강제 차단 (Sustained 감지 후)
 * 
 * Bundle C 정체성: "성능 최적화"가 아닌 "손 떼기 안전장치"
 * - ACTIVE가 오래 유지되면 COOLDOWN으로 강제 복귀
 * - "Fuse ON이 더 끊김" 문제를 구조적으로 차단
 * 
 * @since Fuse 2.5.0
 * @since Fuse 2.6.0 - Bundle C: Sustained Early Exit
 */
public class AdaptiveGate implements TickBudgetGovernor.HardLimitObserver {

    private static final String LOG = "Fuse";

    /** Gate 상태 */
    public enum GateState {
        PASSTHROUGH, // 평시: 개입 없음
        ACTIVE, // 위기: 개입 활성화
        COOLDOWN // Bundle C: 강제 개입 금지
    }

    /** Bundle C: Escape 사유 */
    private enum EscapeReason {
        TIMEOUT, // ACTIVE 시간 상한 초과
        HARD_STREAK // hard_limit 연속 발생
    }

    // --- 진입 임계값 (보수적) ---
    private static final double ENTRY_1S_MAX_MS = 25.0;
    private static final double ENTRY_5S_AVG_MS = 18.0;

    // --- 복귀 임계값 ---
    private static final double EXIT_5S_AVG_MS = 12.0;
    private static final int EXIT_STABILITY_TICKS = 180;

    // --- Bundle C: 로그 레이트리밋 ---
    private static final int ESCAPE_LOG_LIMIT = 10;

    // --- 상태 ---
    private GateState state = GateState.PASSTHROUGH;
    private int stabilityCounter = 0;
    private long stateTransitions = 0;

    // --- Bundle C: Sustained Early Exit 상태 ---
    private long activeEnterMs = 0; // ACTIVE 진입 시각 (1회만 설정!)
    private long cooldownUntilMs = 0; // COOLDOWN 만료 시각
    private int hardLimitStreak = 0; // 연속 hard limit 횟수
    private int hardLimitStreakMax = 0; // 세션 최대 (사실 로그용)
    private long escapeCount = 0; // 총 escape 횟수
    private long escapeByTimeoutCount = 0;
    private long escapeByHardStreakCount = 0;
    private int escapeLogCount = 0; // 로그 레이트리밋용

    // --- 의존성 ---
    private final RollingTickStats stats;
    private final SpikePanicProtocol panicProtocol;
    private final ReasonStats reasonStats;
    private final FuseConfig config;

    public AdaptiveGate(RollingTickStats stats, SpikePanicProtocol panicProtocol,
            ReasonStats reasonStats) {
        this.stats = stats;
        this.panicProtocol = panicProtocol;
        this.reasonStats = reasonStats;
        this.config = FuseConfig.getInstance();
        PulseLogger.info(LOG, "AdaptiveGate initialized (entry: max1s>"
                + ENTRY_1S_MAX_MS + "ms OR avg5s>" + ENTRY_5S_AVG_MS
                + "ms, exit: avg5s<" + EXIT_5S_AVG_MS + "ms for "
                + EXIT_STABILITY_TICKS + " ticks)");
        if (config.isSustainedEarlyExitEnabled()) {
            PulseLogger.info(LOG, "Bundle C enabled: activeMax=" + config.getActiveMaxMs()
                    + "ms, hardStreakMax=" + config.getHardStreakMax()
                    + ", cooldown=" + config.getCooldownMs() + "ms");
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // HardLimitObserver 구현 (봉인#1: streak 오염 방지)
    // ═══════════════════════════════════════════════════════════════

    @Override
    public void onHardLimitHit() {
        if (state == GateState.ACTIVE) {
            hardLimitStreak++;
            hardLimitStreakMax = Math.max(hardLimitStreakMax, hardLimitStreak);
        }
    }

    @Override
    public void onHardLimitMiss() {
        if (state == GateState.ACTIVE) {
            hardLimitStreak = 0;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 메인 평가 로직
    // ═══════════════════════════════════════════════════════════════

    /**
     * 틱 시작 시 1회만 호출 - O(1) 비용.
     * 
     * ⚠️ 이 메서드 내부에서 Fast-Path 로깅 금지!
     * 상태 전이 시에만 로깅 허용.
     */
    public GateState evaluateThisTick() {
        long nowMs = System.currentTimeMillis();

        // ═══ 0. COOLDOWN 만료 복귀 (최상단 고정) ═══
        handleCooldownRecovery(nowMs);

        // ═══ 1. Bundle C: Sustained Early Exit (opt-in 체크) ═══
        if (config.isSustainedEarlyExitEnabled() && state == GateState.ACTIVE) {
            if (isSustainedActive(nowMs)) {
                EscapeReason reason = getSustainedReason(nowMs);
                transitionTo(GateState.COOLDOWN, TelemetryReason.SUSTAINED_EARLY_EXIT);
                recordEscape(reason);
                return state; // 즉시 반환 (개입 프레임 삭제)
            }
        }

        // ═══ 2. COOLDOWN 중 즉시 반환 (개입 금지) ═══
        if (state == GateState.COOLDOWN) {
            return state;
        }

        // ═══ 3. Panic 상태면 무조건 ACTIVE ═══
        if (panicProtocol != null &&
                panicProtocol.getState() != SpikePanicProtocol.State.NORMAL) {
            return transitionTo(GateState.ACTIVE, TelemetryReason.PANIC_WINDOW_SPIKES);
        }

        // ═══ 4. 데이터 부족 시 현상 유지 ═══
        if (stats == null || !stats.hasEnoughData()) {
            return state;
        }

        double max1s = stats.getLast1sMaxMs();
        double avg5s = stats.getLast5sAvgMs();

        // ═══ 5. 상태별 전이 로직 ═══
        switch (state) {
            case PASSTHROUGH:
                if (max1s > ENTRY_1S_MAX_MS || avg5s > ENTRY_5S_AVG_MS) {
                    return transitionTo(GateState.ACTIVE,
                            TelemetryReason.ADAPTIVE_GATE_ACTIVATED);
                }
                break;

            case ACTIVE:
                if (avg5s < EXIT_5S_AVG_MS) {
                    stabilityCounter++;
                    if (stabilityCounter >= EXIT_STABILITY_TICKS) {
                        return transitionTo(GateState.PASSTHROUGH,
                                TelemetryReason.ADAPTIVE_GATE_PASSTHROUGH);
                    }
                } else {
                    stabilityCounter = 0;
                }
                break;

            default:
                break;
        }

        return state;
    }

    // ═══════════════════════════════════════════════════════════════
    // Bundle C: Sustained 판정 (O(1) 핫패스)
    // ═══════════════════════════════════════════════════════════════

    /**
     * ACTIVE 상태에서만 Sustained 조건 판정.
     * COOLDOWN과 의미 분리됨 (봉인#2).
     */
    private boolean isSustainedActive(long nowMs) {
        // 타이머 가드: 미초기화 방어 (확인#B)
        if (activeEnterMs <= 0)
            return false;

        // 시간상한 초과
        if ((nowMs - activeEnterMs) >= config.getActiveMaxMs()) {
            return true;
        }
        // hard_limit 연속 초과
        if (hardLimitStreak >= config.getHardStreakMax()) {
            return true;
        }
        return false;
    }

    /**
     * Sustained 사유 반환 (reason 분기용).
     */
    private EscapeReason getSustainedReason(long nowMs) {
        if ((nowMs - activeEnterMs) >= config.getActiveMaxMs()) {
            return EscapeReason.TIMEOUT;
        }
        return EscapeReason.HARD_STREAK;
    }

    // ═══════════════════════════════════════════════════════════════
    // COOLDOWN 복귀 (최상단 호출)
    // ═══════════════════════════════════════════════════════════════

    private void handleCooldownRecovery(long nowMs) {
        if (state == GateState.COOLDOWN && nowMs >= cooldownUntilMs) {
            transitionTo(GateState.PASSTHROUGH, TelemetryReason.ADAPTIVE_GATE_PASSTHROUGH);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 상태 전이 단일 관문 (확인#A)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 상태 전이 (로깅/ReasonStats 증분 단일 지점).
     */
    private GateState transitionTo(GateState newState, TelemetryReason reason) {
        if (state == newState)
            return state;

        GateState oldState = state;
        state = newState;
        stateTransitions++;

        // PASSTHROUGH → ACTIVE: 타이머 시작 (1회 설정, 확인#B)
        if (oldState == GateState.PASSTHROUGH && newState == GateState.ACTIVE) {
            activeEnterMs = System.currentTimeMillis();
            hardLimitStreak = 0;
        }

        // → COOLDOWN: 만료 시각 설정 + 타이머/스트릭 리셋
        if (newState == GateState.COOLDOWN) {
            cooldownUntilMs = System.currentTimeMillis() + config.getCooldownMs();
            activeEnterMs = 0;
            hardLimitStreak = 0;
        }

        // → PASSTHROUGH: stabilityCounter 리셋
        if (newState == GateState.PASSTHROUGH) {
            stabilityCounter = 0;
        }

        // 로깅 (전이 시에만 - 핫패스 아님)
        PulseLogger.info(LOG, "AdaptiveGate: " + oldState + " → " + newState);

        if (reasonStats != null && reason != null) {
            reasonStats.increment(reason);
        }

        return state;
    }

    // ═══════════════════════════════════════════════════════════════
    // Bundle C: Escape 카운터 기록 (레이트리밋)
    // ═══════════════════════════════════════════════════════════════

    private void recordEscape(EscapeReason reason) {
        escapeCount++;
        if (reason == EscapeReason.TIMEOUT) {
            escapeByTimeoutCount++;
        } else {
            escapeByHardStreakCount++;
        }

        // 로그 레이트리밋: 첫 N회만 INFO, 이후 DEBUG
        escapeLogCount++;
        if (escapeLogCount <= ESCAPE_LOG_LIMIT) {
            PulseLogger.info(LOG, "ESCAPE (" + reason + ") [" + escapeLogCount + "/" + ESCAPE_LOG_LIMIT + "]");
        } else {
            PulseLogger.debug(LOG, "ESCAPE (" + reason + ")");
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 공개 API
    // ═══════════════════════════════════════════════════════════════

    /**
     * 순수 PASSTHROUGH 상태인지 확인 (기존 의미 보존, 봉인#2).
     * 
     * ⚠️ 이 메서드는 Hot Path에서 호출됨 - 로깅 금지!
     */
    public boolean isPassthrough() {
        return state == GateState.PASSTHROUGH;
    }

    /**
     * 개입 차단 상태 (PASSTHROUGH 또는 COOLDOWN).
     * Bundle C 이후 shouldProcess() 등에서 이 API 사용 (봉인#2).
     * 
     * ⚠️ 이 메서드는 Hot Path에서 호출됨 - 로깅 금지!
     */
    public boolean isInterventionBlocked() {
        return state == GateState.PASSTHROUGH || state == GateState.COOLDOWN;
    }

    public GateState getState() {
        return state;
    }

    public long getStateTransitions() {
        return stateTransitions;
    }

    public int getStabilityCounter() {
        return stabilityCounter;
    }

    // --- Bundle C Getters (Snapshot용) ---

    public long getEscapeCount() {
        return escapeCount;
    }

    public long getEscapeByTimeoutCount() {
        return escapeByTimeoutCount;
    }

    public long getEscapeByHardStreakCount() {
        return escapeByHardStreakCount;
    }

    public int getHardLimitStreakMax() {
        return hardLimitStreakMax;
    }

    public int getHardLimitStreak() {
        return hardLimitStreak;
    }

    /**
     * 상태 리셋 (디버깅/테스트용).
     */
    public void reset() {
        state = GateState.PASSTHROUGH;
        stabilityCounter = 0;
        stateTransitions = 0;
        // Bundle C 리셋
        activeEnterMs = 0;
        cooldownUntilMs = 0;
        hardLimitStreak = 0;
        hardLimitStreakMax = 0;
        escapeCount = 0;
        escapeByTimeoutCount = 0;
        escapeByHardStreakCount = 0;
        escapeLogCount = 0;
    }
}
