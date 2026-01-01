package com.fuse.guard;

import com.fuse.config.FuseConfig;
import com.fuse.telemetry.TelemetryReason;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.event.save.PostSaveEvent;
import com.pulse.api.event.save.PreSaveEvent;
import com.pulse.api.event.save.SaveEvent;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * IO Guard - 세이브/로드 중 시스템 부하 완충.
 * 
 * <h3>핵심 원칙:</h3>
 * <ol>
 * <li>IO 자체는 건드리지 않음</li>
 * <li>IO와 겹치는 다른 연산만 억제</li>
 * <li>복구는 점진적으로</li>
 * </ol>
 * 
 * <h3>상태 전이:</h3>
 * 
 * <pre>
 *                     ┌─────────────────────────────────────────┐
 *                     │              정상 흐름                    │
 *                     ▼                                         │
 * ┌──────┐  PreSaveEvent  ┌──────────┐  enterTicks  ┌──────────┐
 * │ IDLE │───────────────▶│ IO_ENTER │─────경과────▶│IO_ACTIVE │
 * └──────┘                └──────────┘              └──────────┘
 *     ▲                        │                         │
 *     │                        │ PostSaveEvent           │ PostSaveEvent
 *     │                        │ (빠른 세이브)            │ 또는 Timeout
 *     │                        ▼                         ▼
 *     │                   ┌─────────────────────────────────────┐
 *     │                   │           IO_EXIT                    │
 *     │                   │     (recoveryTicks 동안 램프업)       │
 *     │                   └─────────────────────────────────────┘
 *     │                                  │
 *     │                           recoveryTicks 경과
 *     │                                  ▼
 *     │                        ┌──────────────┐
 *     │                        │   COOLDOWN   │
 *     │                        │(cooldownTicks)│
 *     │                        └──────────────┘
 *     │                                  │
 *     │                           cooldownTicks 경과
 *     └──────────────────────────────────┘
 * 
 * 예외 전이:
 * - IO_ENTER + PostSaveEvent → IO_EXIT (빠른 세이브, ACTIVE 스킵)
 * - IO_ACTIVE + Timeout → IO_EXIT (이벤트 누락 대비)
 * - 모든 상태 + 3회 연속 오류 → IDLE + IOGuard 비활성화 (Fail-soft)
 * </pre>
 * 
 * @since Fuse 2.0.0
 */
public class IOGuard {

    private static final String LOG = "Fuse";

    // ═══════════════════════════════════════════════════════════════
    // 상태 열거형
    // ═══════════════════════════════════════════════════════════════

    public enum State {
        IDLE, // 정상
        IO_ENTER, // IO 진입 준비 (선제 감속)
        IO_ACTIVE, // IO 진행 중
        IO_EXIT, // 복구 중 (램프업)
        COOLDOWN // 재진입 방지
    }

    // ═══════════════════════════════════════════════════════════════
    // 핵심 상태 (Thread Safety)
    // ═══════════════════════════════════════════════════════════════

    private volatile State currentState = State.IDLE;
    private final AtomicBoolean stateTransitionInProgress = new AtomicBoolean(false);

    private long ioStartNanos = 0;
    private long lastIODurationMs = 0;
    private SaveEvent.SaveType currentSaveType = null;
    private String currentSaveName = null;

    // 상태별 틱 카운터
    private int enterTicksRemaining = 0;
    private int recoveryTicksRemaining = 0;
    private int cooldownTicksRemaining = 0;
    private int ioActiveTicksElapsed = 0;

    // 복구 진행률 (0.0 ~ 1.0)
    private float recoveryProgress = 0f;

    // 상태 변경 추적 (TelemetryReason 중복 방지)
    private State lastReportedState = State.IDLE;

    // ═══════════════════════════════════════════════════════════════
    // 설정 (FuseConfig에서 로드)
    // ═══════════════════════════════════════════════════════════════

    private boolean enabled = true;

    // 예산 배수
    private float enterBudgetMultiplier = 0.7f;
    private float activeBudgetMultiplier = 0.3f;
    private float cooldownBudgetMultiplier = 0.9f;

    // 틱 설정
    private int enterTicks = 5; // IO_ENTER 지속
    private int recoveryTicks = 30; // IO_EXIT 지속 (0.5초 @60fps)
    private int cooldownTicks = 10; // COOLDOWN 지속
    private int activeTimeoutTicks = 300; // Deadman Switch: 5초 @60fps

    // 필터링
    private boolean worldSaveOnly = false;
    private boolean logEnabled = true;

    // ═══════════════════════════════════════════════════════════════
    // Fail-soft
    // ═══════════════════════════════════════════════════════════════

    private int consecutiveErrors = 0;
    private static final int MAX_ERRORS = 3;

    // ═══════════════════════════════════════════════════════════════
    // 통계
    // ═══════════════════════════════════════════════════════════════

    private long totalIOEvents = 0;
    private long totalIOTimeMs = 0;
    private long maxIOTimeMs = 0;
    private long timeoutCount = 0;
    private long ioGuardOverrideCount = 0;

    // ═══════════════════════════════════════════════════════════════
    // 초기화
    // ═══════════════════════════════════════════════════════════════

    public IOGuard() {
        // 기본 설정으로 초기화
    }

    /**
     * FuseConfig에서 설정 로드.
     */
    public void loadConfig(FuseConfig config) {
        this.enabled = config.isIOGuardEnabled();
        this.enterBudgetMultiplier = config.getIOEnterBudgetMultiplier();
        this.activeBudgetMultiplier = config.getIOActiveBudgetMultiplier();
        this.cooldownBudgetMultiplier = config.getIOCooldownBudgetMultiplier();
        this.enterTicks = config.getIOEnterTicks();
        this.recoveryTicks = config.getIORecoveryTicks();
        this.cooldownTicks = config.getIOCooldownTicks();
        this.activeTimeoutTicks = config.getIOActiveTimeoutTicks();
        this.worldSaveOnly = config.isIOGuardWorldSaveOnly();
        this.logEnabled = config.isIOGuardLogEnabled();
    }

    // ═══════════════════════════════════════════════════════════════
    // 이벤트 핸들러
    // ═══════════════════════════════════════════════════════════════

    /**
     * PreSaveEvent 핸들러.
     */
    public void onPreSave(PreSaveEvent event) {
        if (!enabled)
            return;
        if (worldSaveOnly && event.getSaveType() != SaveEvent.SaveType.WORLD)
            return;
        if (currentState != State.IDLE && currentState != State.COOLDOWN)
            return;

        try {
            enterIOMode(event.getSaveType(), event.getSaveName());
            resetErrorCount();
        } catch (Throwable t) {
            handleError(t);
        }
    }

    /**
     * PostSaveEvent 핸들러.
     */
    public void onPostSave(PostSaveEvent event) {
        if (!enabled)
            return;
        if (currentState != State.IO_ACTIVE && currentState != State.IO_ENTER)
            return;

        try {
            exitIOMode(event.isSuccess());
            resetErrorCount();
        } catch (Throwable t) {
            handleError(t);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 상태 전이
    // ═══════════════════════════════════════════════════════════════

    private void enterIOMode(SaveEvent.SaveType saveType, String saveName) {
        if (!stateTransitionInProgress.compareAndSet(false, true)) {
            return; // 이미 전이 중
        }

        try {
            currentState = State.IO_ENTER;
            ioStartNanos = System.nanoTime();
            currentSaveType = saveType;
            currentSaveName = saveName;
            enterTicksRemaining = enterTicks;
            ioActiveTicksElapsed = 0;

            if (logEnabled) {
                PulseLogger.info(LOG,
                        "IOGuard: Entering IO mode (" + saveType + ": " + saveName + ")");
            }
        } finally {
            stateTransitionInProgress.set(false);
        }
    }

    private void exitIOMode(boolean success) {
        if (!stateTransitionInProgress.compareAndSet(false, true)) {
            return;
        }

        try {
            lastIODurationMs = (System.nanoTime() - ioStartNanos) / 1_000_000;

            // 통계 갱신
            totalIOEvents++;
            totalIOTimeMs += lastIODurationMs;
            maxIOTimeMs = Math.max(maxIOTimeMs, lastIODurationMs);

            // 복구 시작
            currentState = State.IO_EXIT;
            recoveryTicksRemaining = recoveryTicks;
            recoveryProgress = 0f;

            if (logEnabled) {
                PulseLogger.info(LOG,
                        "IOGuard: IO complete (" + lastIODurationMs + "ms), starting recovery");
            }
        } finally {
            stateTransitionInProgress.set(false);
        }
    }

    /**
     * Deadman Switch: 강제 IO_EXIT 전이.
     */
    private void forceExitDueToTimeout() {
        if (!stateTransitionInProgress.compareAndSet(false, true)) {
            return;
        }

        try {
            timeoutCount++;
            lastIODurationMs = (System.nanoTime() - ioStartNanos) / 1_000_000;

            PulseLogger.warn(LOG,
                    "IOGuard: Deadman timeout (" + ioActiveTicksElapsed + " ticks) - " +
                            "no PostSaveEvent in PZ, assuming save complete");

            currentState = State.IO_EXIT;
            recoveryTicksRemaining = recoveryTicks;
            recoveryProgress = 0f;
        } finally {
            stateTransitionInProgress.set(false);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 틱 업데이트
    // ═══════════════════════════════════════════════════════════════

    /**
     * 매 게임 틱마다 호출.
     */
    public void tick() {
        if (!enabled)
            return;

        try {
            switch (currentState) {
                case IO_ENTER:
                    tickIOEnter();
                    break;
                case IO_ACTIVE:
                    tickIOActive();
                    break;
                case IO_EXIT:
                    tickIOExit();
                    break;
                case COOLDOWN:
                    tickCooldown();
                    break;
                default:
                    // IDLE: nothing to do
                    break;
            }
            resetErrorCount();
        } catch (Throwable t) {
            handleError(t);
        }
    }

    private void tickIOEnter() {
        enterTicksRemaining--;
        if (enterTicksRemaining <= 0) {
            // IO_ENTER 만료 → IO_ACTIVE로 전이
            currentState = State.IO_ACTIVE;
            ioActiveTicksElapsed = 0;
        }
    }

    private void tickIOActive() {
        ioActiveTicksElapsed++;

        // Deadman Switch: 타임아웃 체크
        if (ioActiveTicksElapsed > activeTimeoutTicks) {
            forceExitDueToTimeout();
        }
    }

    private void tickIOExit() {
        recoveryTicksRemaining--;
        recoveryProgress = 1.0f - ((float) recoveryTicksRemaining / recoveryTicks);

        if (recoveryTicksRemaining <= 0) {
            currentState = State.COOLDOWN;
            cooldownTicksRemaining = cooldownTicks;
        }
    }

    private void tickCooldown() {
        cooldownTicksRemaining--;
        if (cooldownTicksRemaining <= 0) {
            currentState = State.IDLE;
            currentSaveType = null;
            currentSaveName = null;
            recoveryProgress = 0f;

            if (logEnabled) {
                PulseLogger.debug(LOG, "IOGuard: Fully recovered");
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 예산 계산 (핵심)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 현재 상태 기반 예산 배수 반환.
     * 
     * @return 0.0 ~ 1.0 사이의 배수
     */
    public float getBudgetMultiplier() {
        if (!enabled)
            return 1.0f;

        switch (currentState) {
            case IO_ENTER:
                return enterBudgetMultiplier;

            case IO_ACTIVE:
                return activeBudgetMultiplier;

            case IO_EXIT:
                // 점진적 램프업: active → 1.0
                return activeBudgetMultiplier +
                        (1.0f - activeBudgetMultiplier) * recoveryProgress;

            case COOLDOWN:
                return cooldownBudgetMultiplier;

            default:
                return 1.0f;
        }
    }

    /**
     * IOGuard가 활성 상태인지 반환.
     */
    public boolean isActive() {
        return enabled && currentState != State.IDLE;
    }

    /**
     * Override 카운트 증가 (ThrottleController에서 호출).
     */
    public void incrementOverrideCount() {
        ioGuardOverrideCount++;
    }

    // ═══════════════════════════════════════════════════════════════
    // Telemetry
    // ═══════════════════════════════════════════════════════════════

    /**
     * 현재 상태에 대한 TelemetryReason 반환.
     * 상태 전이 시에만 새 reason을 반환 (중복 방지).
     * 
     * @return TelemetryReason 또는 null (변경 없음)
     */
    public TelemetryReason getTelemetryReason() {
        TelemetryReason currentReason = switch (currentState) {
            case IO_ENTER, IO_ACTIVE -> TelemetryReason.IO_GUARD_ACTIVE;
            case IO_EXIT, COOLDOWN -> TelemetryReason.IO_GUARD_RECOVERY;
            default -> null;
        };

        // 이전과 다를 때만 반환 (중복 방지)
        if (currentState != lastReportedState) {
            lastReportedState = currentState;
            return currentReason;
        }
        return null;
    }

    /**
     * 상태 변경 여부 확인.
     */
    public boolean hasStateChanged() {
        return currentState != lastReportedState;
    }

    // ═══════════════════════════════════════════════════════════════
    // Fail-soft
    // ═══════════════════════════════════════════════════════════════

    private void handleError(Throwable t) {
        consecutiveErrors++;
        PulseLogger.warn(LOG, "IOGuard error: " + t.getMessage());

        if (consecutiveErrors >= MAX_ERRORS) {
            enabled = false;
            currentState = State.IDLE;
            PulseLogger.error(LOG,
                    "IOGuard disabled due to repeated errors (fail-soft)", t);
        }
    }

    private void resetErrorCount() {
        consecutiveErrors = 0;
    }

    // ═══════════════════════════════════════════════════════════════
    // 디버그 / 상태 조회
    // ═══════════════════════════════════════════════════════════════

    public State getCurrentState() {
        return currentState;
    }

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
        if (!enabled) {
            currentState = State.IDLE;
        }
        PulseLogger.info(LOG, "IOGuard: " + (enabled ? "ENABLED" : "DISABLED"));
    }

    public long getTotalIOEvents() {
        return totalIOEvents;
    }

    public long getTotalIOTimeMs() {
        return totalIOTimeMs;
    }

    public long getAverageIOTimeMs() {
        return totalIOEvents > 0 ? totalIOTimeMs / totalIOEvents : 0;
    }

    public long getMaxIOTimeMs() {
        return maxIOTimeMs;
    }

    public long getTimeoutCount() {
        return timeoutCount;
    }

    public long getIOGuardOverrideCount() {
        return ioGuardOverrideCount;
    }

    public float getRecoveryProgress() {
        return recoveryProgress;
    }

    public SaveEvent.SaveType getCurrentSaveType() {
        return currentSaveType;
    }

    public String getCurrentSaveName() {
        return currentSaveName;
    }

    public void resetStats() {
        totalIOEvents = 0;
        totalIOTimeMs = 0;
        maxIOTimeMs = 0;
        timeoutCount = 0;
        ioGuardOverrideCount = 0;
    }

    /**
     * 상태 정보 출력.
     */
    public void printStatus() {
        PulseLogger.info(LOG, "IOGuard Status (v2.0):");
        PulseLogger.info(LOG, "  State: " + currentState);
        PulseLogger.info(LOG, "  Enabled: " + enabled);
        PulseLogger.info(LOG, "  Multiplier: " + String.format("%.2f", getBudgetMultiplier()));
        if (currentState == State.IO_EXIT) {
            PulseLogger.info(LOG, "  Recovery: " + String.format("%.0f%%", recoveryProgress * 100));
        }
        PulseLogger.info(LOG, "  ---");
        PulseLogger.info(LOG, "  Total IO Events: " + totalIOEvents);
        PulseLogger.info(LOG, "  Total IO Time: " + totalIOTimeMs + "ms");
        PulseLogger.info(LOG, "  Avg IO Time: " + getAverageIOTimeMs() + "ms");
        PulseLogger.info(LOG, "  Max IO Time: " + maxIOTimeMs + "ms");
        PulseLogger.info(LOG, "  Timeouts: " + timeoutCount);
        PulseLogger.info(LOG, "  Overrides: " + ioGuardOverrideCount);
    }
}
