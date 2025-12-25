package com.fuse.guard;

import com.fuse.config.FuseConfig;
import com.fuse.governor.GCPressureSignal;
import com.fuse.governor.RollingTickStats;
import com.fuse.telemetry.ReasonStats;
import com.fuse.telemetry.TelemetryReason;
import com.pulse.api.gc.GcObservedEvent;
import com.pulse.api.gc.GcSample;
import com.pulse.api.log.PulseLogger;

/**
 * GC 압력 Guard.
 * 
 * 상태 머신 기반으로 GC 압력에 따라 예산 배수 조절.
 * Hub&Spoke: Pulse EventBus에서 GcObservedEvent를 구독.
 * 
 * 상태 전이:
 * - NORMAL → DIET: pressure ≥ dietThreshold
 * - NORMAL → POST_GC_RECOVERY: GC 발생
 * - DIET → POST_GC_RECOVERY: GC 발생
 * - DIET → RECOVERING: pressure < recoveryThreshold (hysteresis 만족)
 * - RECOVERING → NORMAL: recoveryTicks 완료
 * - POST_GC_RECOVERY → NORMAL: postGcRecoveryTicks 완료
 * 
 * @since Fuse 2.1.0
 */
public class GCPressureGuard {

    private static final String LOG = "Fuse";

    /**
     * Guard 상태.
     */
    public enum State {
        NORMAL, // 평상시
        DIET, // 예산 축소 중
        RECOVERING, // 점진적 복구 중
        POST_GC_RECOVERY // GC 직후 복구
    }

    // --- 설정 (보수적 초기값) ---
    private float dietThreshold = 0.60f;
    private float recoveryThreshold = 0.35f;
    private float dietMultiplier = 0.65f; // 보수적: 0.50 → 0.65
    private float criticalMultiplier = 0.45f; // 보수적: 0.30 → 0.45
    private int recoveryTicks = 60; // 1초 @60fps
    private int hysteresisWindow = 30; // 0.5초
    private int postGcRecoveryTicks = 45; // 0.75초

    // --- 상태 ---
    private State currentState = State.NORMAL;
    @SuppressWarnings("unused") // 향후 디버깅/로깅에 활용 예정
    private State previousState = State.NORMAL;
    private GCPressureSignal currentSignal = GCPressureSignal.normal();

    // --- 카운터 ---
    private int stabilityCounter = 0; // 히스테리시스 카운터
    private int recoveryTickCounter = 0; // 복구 틱 카운터
    private int postGcTickCounter = 0; // POST_GC 틱 카운터

    // --- Fail-soft ---
    private boolean enabled = true;
    private int consecutiveErrors = 0;
    private static final int MAX_ERRORS = 5;

    // --- 통계 ---
    private long dietCount = 0;
    private long recoveringCount = 0;
    private long postGcCount = 0;
    private long transitionCount = 0;

    // --- 의존성 ---
    private RollingTickStats rollingTickStats;
    private ReasonStats reasonStats;
    private TelemetryReason lastReason = null;

    public GCPressureGuard() {
        loadConfig();
        PulseLogger.info(LOG, "GCPressureGuard initialized (v2.1, conservative preset)");
    }

    private void loadConfig() {
        FuseConfig config = FuseConfig.getInstance();
        this.dietThreshold = config.getGcDietThreshold();
        this.recoveryThreshold = config.getGcRecoveryThreshold();
        this.dietMultiplier = config.getGcDietMultiplier();
        this.criticalMultiplier = config.getGcCriticalMultiplier();
        this.recoveryTicks = config.getGcRecoveryTicks();
        this.hysteresisWindow = config.getGcHysteresisWindow();
        this.postGcRecoveryTicks = config.getGcPostGcRecoveryTicks();
    }

    /**
     * RollingTickStats 설정 (jitter 계산용).
     */
    public void setRollingTickStats(RollingTickStats stats) {
        this.rollingTickStats = stats;
    }

    /**
     * ReasonStats 설정 (텔레메트리용).
     */
    public void setReasonStats(ReasonStats reasonStats) {
        this.reasonStats = reasonStats;
    }

    /**
     * GC 이벤트 처리.
     * FuseMod에서 EventBus 구독하여 호출.
     */
    public void onGcObserved(GcObservedEvent event) {
        if (!enabled)
            return;

        try {
            GcSample sample = event.getSample();

            // jitter는 Fuse 내부 RollingTickStats에서 (Hub&Spoke 준수)
            double jitter = (rollingTickStats != null) ? rollingTickStats.getStdDev() : 0.0;

            // 압력 신호 계산
            this.currentSignal = GCPressureSignal.from(sample, jitter);

            // 상태 머신 업데이트
            updateState(sample);

            // 오류 카운터 리셋
            consecutiveErrors = 0;

        } catch (Exception e) {
            handleError(e);
        }
    }

    /**
     * 상태 머신 업데이트.
     */
    private void updateState(GcSample sample) {
        previousState = currentState;
        boolean gcOccurred = (sample != null && sample.gcOccurred());
        float pressure = currentSignal.getPressureValue();

        switch (currentState) {
            case NORMAL:
                if (gcOccurred) {
                    // GC 발생 → 즉시 POST_GC_RECOVERY 진입
                    transitionTo(State.POST_GC_RECOVERY, TelemetryReason.GC_PRESSURE_POST_GC);
                    postGcTickCounter = 0;
                } else if (pressure >= dietThreshold) {
                    // 압력 상승 → DIET 진입
                    transitionTo(State.DIET, TelemetryReason.GC_PRESSURE_DIET);
                    stabilityCounter = 0;
                }
                break;

            case DIET:
                dietCount++;
                if (gcOccurred) {
                    // GC 발생 → POST_GC_RECOVERY 진입
                    transitionTo(State.POST_GC_RECOVERY, TelemetryReason.GC_PRESSURE_POST_GC);
                    postGcTickCounter = 0;
                } else if (pressure < recoveryThreshold) {
                    // 압력 감소 → 히스테리시스 카운터 증가
                    stabilityCounter++;
                    if (stabilityCounter >= hysteresisWindow) {
                        // 안정 확인 → RECOVERING 진입
                        transitionTo(State.RECOVERING, TelemetryReason.GC_PRESSURE_RECOVERING);
                        recoveryTickCounter = 0;
                    }
                } else {
                    // 압력 유지 → 카운터 리셋
                    stabilityCounter = 0;
                }
                break;

            case RECOVERING:
                recoveringCount++;
                recoveryTickCounter++;
                if (gcOccurred) {
                    // GC 재발생 → POST_GC_RECOVERY (틱 리셋)
                    transitionTo(State.POST_GC_RECOVERY, TelemetryReason.GC_PRESSURE_POST_GC);
                    postGcTickCounter = 0;
                } else if (pressure >= dietThreshold) {
                    // 압력 재상승 → DIET 복귀
                    transitionTo(State.DIET, TelemetryReason.GC_PRESSURE_DIET);
                    stabilityCounter = 0;
                } else if (recoveryTickCounter >= recoveryTicks) {
                    // 복구 완료 → NORMAL
                    transitionTo(State.NORMAL, null);
                }
                break;

            case POST_GC_RECOVERY:
                postGcCount++;
                postGcTickCounter++;
                if (gcOccurred) {
                    // GC 재발생 → 카운터 리셋
                    postGcTickCounter = 0;
                } else if (postGcTickCounter >= postGcRecoveryTicks) {
                    // 복구 완료 → 압력 확인 후 상태 결정
                    if (pressure >= dietThreshold) {
                        transitionTo(State.DIET, TelemetryReason.GC_PRESSURE_DIET);
                    } else {
                        transitionTo(State.NORMAL, null);
                    }
                }
                break;
        }
    }

    /**
     * 상태 전이 처리.
     */
    private void transitionTo(State newState, TelemetryReason reason) {
        if (currentState != newState) {
            transitionCount++;

            // 상태 전이 시에만 로그 출력
            PulseLogger.info(LOG, "GCPressure: {} → {} (pressure={}, heap={}%, mult={})",
                    currentState, newState,
                    String.format("%.2f", currentSignal.getPressureValue()),
                    String.format("%.0f", currentSignal.getPressureValue() * 100), // 근사
                    String.format("%.2f", getBudgetMultiplier()));

            currentState = newState;
            lastReason = reason;
            recordReason(reason);
        }
    }

    private void recordReason(TelemetryReason reason) {
        if (reasonStats != null && reason != null) {
            reasonStats.increment(reason);
        }
    }

    /**
     * 현재 예산 배수 반환.
     * 
     * @return 0.0 ~ 1.0 (1.0 = 개입 없음)
     */
    public float getBudgetMultiplier() {
        if (!enabled)
            return 1.0f;

        return switch (currentState) {
            case NORMAL -> 1.0f;
            case DIET -> currentSignal.isCritical() ? criticalMultiplier : dietMultiplier;
            case RECOVERING -> {
                // 점진적 복구: recoveryTickCounter / recoveryTicks 비율로 램프업
                float progress = (float) recoveryTickCounter / recoveryTicks;
                float base = dietMultiplier;
                yield base + (1.0f - base) * progress;
            }
            case POST_GC_RECOVERY -> {
                // POST_GC도 점진적 복구
                float progress = (float) postGcTickCounter / postGcRecoveryTicks;
                float base = dietMultiplier;
                yield base + (1.0f - base) * progress;
            }
        };
    }

    /**
     * Guard가 활성 상태인지.
     */
    public boolean isActive() {
        return enabled && currentState != State.NORMAL;
    }

    /**
     * Fail-soft 오류 처리.
     */
    private void handleError(Throwable t) {
        consecutiveErrors++;
        PulseLogger.warn(LOG, "GCPressureGuard error ({}/{}): {}",
                consecutiveErrors, MAX_ERRORS, t.getMessage());

        if (consecutiveErrors >= MAX_ERRORS) {
            enabled = false;
            currentState = State.NORMAL;
            PulseLogger.error(LOG, "GCPressureGuard disabled (fail-soft)");
        }
    }

    // --- Getters ---

    public State getCurrentState() {
        return currentState;
    }

    public GCPressureSignal getCurrentSignal() {
        return currentSignal;
    }

    public TelemetryReason getLastReason() {
        return lastReason;
    }

    public boolean isEnabled() {
        return enabled;
    }

    public long getDietCount() {
        return dietCount;
    }

    public long getRecoveringCount() {
        return recoveringCount;
    }

    public long getPostGcCount() {
        return postGcCount;
    }

    public long getTransitionCount() {
        return transitionCount;
    }

    /**
     * 상태 요약 문자열.
     */
    public String getStatusSummary() {
        return String.format("GCPressure: %s (p=%.2f, mult=%.2f, trans=%d)",
                currentState,
                currentSignal.getPressureValue(),
                getBudgetMultiplier(),
                transitionCount);
    }

    /**
     * 상태 리셋.
     */
    public void reset() {
        currentState = State.NORMAL;
        previousState = State.NORMAL;
        currentSignal = GCPressureSignal.normal();
        stabilityCounter = 0;
        recoveryTickCounter = 0;
        postGcTickCounter = 0;
        dietCount = 0;
        recoveringCount = 0;
        postGcCount = 0;
        transitionCount = 0;
        lastReason = null;
        consecutiveErrors = 0;
        enabled = true;
    }
}
