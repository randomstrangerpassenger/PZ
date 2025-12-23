package com.nerve.guard;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.spi.ITickHealthProvider;

/**
 * SlowTick Guard for Nerve.
 * 
 * SlowTick 상태일 때만 완충 모드를 활성화.
 * 
 * 핵심 철학:
 * - Nerve는 Echo를 전혀 모름 (import 없음)
 * - 오직 Pulse SPI(ITickHealthProvider)만 사용
 * - Provider가 없으면 fail-open (완충 비활성화)
 * 
 * v0.1: 기본 OFF + 보수적 스코프
 * 
 * @since Nerve 0.3.0
 */
public class SlowTickGuard {

    private static final String LOG = "Nerve";

    // --- 설정 ---
    private boolean enabled = false; // 기본 OFF
    private int spikeThreshold = 2; // N회 이상 스파이크 시 완충 진입
    @SuppressWarnings("unused") // 향후 동적 임계값에 사용 예정
    private double slowTickThresholdMs = 33.33; // SlowTick 임계값

    // --- 상태 ---
    private boolean bufferMode = false;
    private int consecutiveErrors = 0;
    private static final int MAX_ERRORS = 3;

    // --- Provider (Pulse를 통해 조회) ---
    private ITickHealthProvider healthProvider;

    public SlowTickGuard() {
        // 기본 fail-open provider 사용 (나중에 실제 provider로 교체)
        this.healthProvider = ITickHealthProvider.DEFAULT;
        PulseLogger.info(LOG, "SlowTickGuard initialized (default OFF, fail-open)");
    }

    /**
     * Provider 설정 (Pulse 레지스트리에서 조회 후 호출).
     * Nerve는 Echo를 직접 참조하지 않고, 이 메서드를 통해 provider만 받음.
     */
    public void setHealthProvider(ITickHealthProvider provider) {
        this.healthProvider = provider != null ? provider : ITickHealthProvider.DEFAULT;
        PulseLogger.debug(LOG, "SlowTickGuard: HealthProvider set to " + this.healthProvider.getId());
    }

    /**
     * 완충 모드 활성화 여부 확인.
     * SlowTick 상태일 때만 true.
     */
    public boolean shouldBuffer() {
        if (!enabled) {
            return false;
        }

        try {
            boolean isSlowTick = healthProvider.isSlowTick();
            int spikeCount = healthProvider.getRecentSpikeCount();

            boolean wasPreviousBuffer = bufferMode;

            // 진입 조건: SlowTick 또는 스파이크 임계값 초과
            if (isSlowTick || spikeCount >= spikeThreshold) {
                bufferMode = true;
            } else {
                bufferMode = false;
            }

            // 상태 변경 로그
            if (bufferMode && !wasPreviousBuffer) {
                PulseLogger.debug(LOG, "SlowTickGuard: BUFFER mode (slowTick=" + isSlowTick
                        + ", spikes=" + spikeCount + ")");
            } else if (!bufferMode && wasPreviousBuffer) {
                PulseLogger.debug(LOG, "SlowTickGuard: NORMAL mode");
            }

            // 성공 시 에러 카운터 리셋
            consecutiveErrors = 0;

            return bufferMode;
        } catch (Exception e) {
            // Fail-open: 에러 발생 시 완충 비활성화
            recordError(e);
            return false;
        }
    }

    /**
     * Fail-open 에러 핸들링.
     * 연속 N회 에러 시 자동으로 Guard 비활성화.
     */
    private void recordError(Throwable t) {
        consecutiveErrors++;
        PulseLogger.warn(LOG, "SlowTickGuard: Error (" + consecutiveErrors + "/" + MAX_ERRORS + "): "
                + t.getMessage());

        if (consecutiveErrors >= MAX_ERRORS) {
            enabled = false;
            bufferMode = false;
            PulseLogger.warn(LOG, "SlowTickGuard: AUTO-DISABLED due to consecutive errors (fail-open)");
        }
    }

    // --- 제어 API ---

    public void enable() {
        this.enabled = true;
        this.consecutiveErrors = 0;
        PulseLogger.info(LOG, "SlowTickGuard: ENABLED");
    }

    public void disable() {
        this.enabled = false;
        this.bufferMode = false;
        PulseLogger.info(LOG, "SlowTickGuard: DISABLED");
    }

    public boolean isEnabled() {
        return enabled;
    }

    public boolean isBufferMode() {
        return bufferMode;
    }

    public void setSpikeThreshold(int threshold) {
        this.spikeThreshold = Math.max(1, threshold);
    }

    public void setSlowTickThresholdMs(double thresholdMs) {
        this.slowTickThresholdMs = thresholdMs;
    }

    public void reset() {
        bufferMode = false;
        consecutiveErrors = 0;
    }

    // --- Getters for status display ---

    public String getProviderId() {
        return healthProvider != null ? healthProvider.getId() : "none";
    }

    public int getConsecutiveErrors() {
        return consecutiveErrors;
    }
}
