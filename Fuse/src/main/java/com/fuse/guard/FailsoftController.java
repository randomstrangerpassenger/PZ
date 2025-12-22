package com.fuse.guard;

import com.fuse.telemetry.TelemetryReason;
import com.pulse.api.log.PulseLogger;

/**
 * Fail-soft Controller.
 * 
 * 예외 상황 발생 시 자동으로 안전한 방향(개입 비활성화)으로 전환합니다.
 * 
 * 핵심 규칙: 자동 ON ❌ / 자동 OFF만 허용 ⭕
 * shutdown() 대신 "개입만 OFF"로 모드 자체는 유지 (디버깅 용이)
 * 
 * @since Fuse 1.1
 */
public class FailsoftController {

    private static final String LOG = "Fuse";

    // --- 설정값 ---
    private int maxConsecutiveErrors = 3;

    // --- 상태 ---
    private int consecutiveErrors = 0;
    private boolean interventionDisabled = false;
    private Throwable lastError = null;
    private long lastErrorTimestamp = 0;

    // 텔레메트리
    private TelemetryReason lastReason = null;

    public FailsoftController() {
        PulseLogger.info(LOG, "FailsoftController initialized (max errors: "
                + maxConsecutiveErrors + ")");
    }

    /**
     * 성공 기록 - 에러 카운터 리셋.
     */
    public void recordSuccess() {
        if (consecutiveErrors > 0) {
            consecutiveErrors = 0;
        }
    }

    /**
     * 에러 기록.
     * 연속 N회 에러 시 개입 비활성화.
     */
    public void recordError(Throwable t) {
        consecutiveErrors++;
        lastError = t;
        lastErrorTimestamp = System.currentTimeMillis();

        PulseLogger.warn(LOG, "FailsoftController: Error recorded ("
                + consecutiveErrors + "/" + maxConsecutiveErrors + ")");

        if (t != null) {
            PulseLogger.error(LOG, "Error: " + t.getClass().getSimpleName()
                    + ": " + t.getMessage(), t);
        }

        if (consecutiveErrors >= maxConsecutiveErrors) {
            disableIntervention();
        }
    }

    /**
     * 개입 비활성화.
     * shutdown()과 달리 Fuse 모드는 유지 (상태 조회/디버깅 가능)
     */
    private void disableIntervention() {
        if (interventionDisabled) {
            return;
        }

        interventionDisabled = true;
        lastReason = TelemetryReason.FAILSOFT_ERROR;

        PulseLogger.error(LOG, "");
        PulseLogger.error(LOG, "╔═══════════════════════════════════════════════╗");
        PulseLogger.error(LOG, "║     ⚠️ FAILSOFT: Intervention Disabled        ║");
        PulseLogger.error(LOG, "║     Fuse is running in SAFE MODE              ║");
        PulseLogger.error(LOG, "║     (All throttling bypassed, vanilla only)   ║");
        PulseLogger.error(LOG, "╚═══════════════════════════════════════════════╝");
        PulseLogger.error(LOG, "");

        if (lastError != null) {
            PulseLogger.error(LOG, "Stack trace:", lastError);
        }
    }

    /**
     * 개입이 비활성화되었는지.
     */
    public boolean isInterventionDisabled() {
        return interventionDisabled;
    }

    /**
     * 마지막 텔레메트리 이유.
     */
    public TelemetryReason getLastReason() {
        return lastReason;
    }

    /**
     * 마지막 에러.
     */
    public Throwable getLastError() {
        return lastError;
    }

    /**
     * 마지막 에러 타임스탬프.
     */
    public long getLastErrorTimestamp() {
        return lastErrorTimestamp;
    }

    /**
     * 연속 에러 수.
     */
    public int getConsecutiveErrors() {
        return consecutiveErrors;
    }

    // --- 설정 ---

    public void setMaxConsecutiveErrors(int max) {
        this.maxConsecutiveErrors = Math.max(1, max);
    }

    /**
     * 수동 리셋 (관리자 명령어용).
     * 개입 재활성화는 세션 재시작 또는 명시적 명령 필요.
     */
    public void manualReset() {
        consecutiveErrors = 0;
        interventionDisabled = false;
        lastError = null;
        lastErrorTimestamp = 0;
        lastReason = null;
        PulseLogger.info(LOG, "FailsoftController manually reset");
    }

    public void printStatus() {
        PulseLogger.info(LOG, "Failsoft Status:");
        PulseLogger.info(LOG, "  Intervention Disabled: " + interventionDisabled);
        PulseLogger.info(LOG, "  Consecutive Errors: " + consecutiveErrors + "/" + maxConsecutiveErrors);
        if (lastError != null) {
            PulseLogger.info(LOG, "  Last Error: " + lastError.getClass().getSimpleName());
            PulseLogger.info(LOG, "  Error Time: " + new java.util.Date(lastErrorTimestamp));
        }
    }
}
