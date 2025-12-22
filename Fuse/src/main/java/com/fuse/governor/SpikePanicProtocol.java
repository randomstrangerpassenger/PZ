package com.fuse.governor;

import com.fuse.telemetry.TelemetryReason;

/**
 * Spike Panic Protocol.
 * 
 * 대규모 스파이크 발생 시 연쇄 프리즈를 차단하는 비상 프로토콜입니다.
 * 슬라이딩 윈도우 기반으로 스파이크를 감지하고,
 * RECOVERING 상태에서 점진적으로 복구합니다.
 * 
 * @since Fuse 1.1
 */
public class SpikePanicProtocol {

    private static final String LOG = "Fuse";

    // --- 설정값 (FuseConfig에서 로드 가능) ---
    private long spikeThresholdMs = 100;
    private long windowSizeMs = 5000; // 5초 윈도우
    private int spikeCountThreshold = 2;
    private int recoveryPhaseTicks = 30; // 각 복구 단계 30틱

    // --- 상태 ---
    public enum State {
        NORMAL,
        PANIC,
        RECOVERING
    }

    private State state = State.NORMAL;

    // 점진적 복구: 0.5 → 0.75 → 1.0
    private int recoveryPhase = 0; // 0, 1, 2 (3이면 NORMAL)
    private int recoveryTickCounter = 0;
    private int normalTickCounter = 0;

    // 슬라이딩 윈도우 카운터
    private final SlidingWindowCounter spikeCounter;

    // 텔레메트리
    private TelemetryReason lastReason = null;

    public SpikePanicProtocol() {
        this.spikeCounter = new SlidingWindowCounter(windowSizeMs);
        System.out.println("[" + LOG + "] SpikePanicProtocol initialized (sliding window: "
                + windowSizeMs + "ms, threshold: " + spikeCountThreshold + " spikes)");
    }

    /**
     * 틱 시간 기록 및 상태 전이.
     * 
     * @param durationMs 이번 틱의 소요 시간 (ms)
     */
    public void recordTickDuration(long durationMs) {
        // 스파이크 감지
        if (durationMs >= spikeThresholdMs) {
            spikeCounter.recordEvent();
        }

        // 상태 머신
        switch (state) {
            case NORMAL:
                handleNormalState();
                break;
            case PANIC:
                handlePanicState(durationMs);
                break;
            case RECOVERING:
                handleRecoveringState(durationMs);
                break;
        }
    }

    private void handleNormalState() {
        int spikeCount = spikeCounter.getCountInWindow();
        if (spikeCount >= spikeCountThreshold) {
            enterPanic();
        }
    }

    private void handlePanicState(long durationMs) {
        // PANIC 상태에서는 AI 개입이 극도로 축소되므로 틱이 정상화됨
        // 일정 시간 후 RECOVERING으로 전이
        if (durationMs < spikeThresholdMs) {
            normalTickCounter++;
            if (normalTickCounter >= recoveryPhaseTicks) {
                enterRecovering();
            }
        } else {
            normalTickCounter = 0; // 스파이크 발생 시 카운터 리셋
        }
    }

    private void handleRecoveringState(long durationMs) {
        if (durationMs >= spikeThresholdMs) {
            // 복구 중 스파이크 발생 → 다시 PANIC
            enterPanic();
            return;
        }

        recoveryTickCounter++;
        if (recoveryTickCounter >= recoveryPhaseTicks) {
            recoveryPhase++;
            recoveryTickCounter = 0;

            if (recoveryPhase >= 3) {
                // 완전 복구
                enterNormal();
            } else {
                lastReason = TelemetryReason.RECOVERING_GRADUAL;
                System.out.println("[" + LOG + "] SpikePanicProtocol: Recovery phase "
                        + recoveryPhase + "/3 (multiplier: " + getThrottleMultiplier() + ")");
            }
        }
    }

    private void enterPanic() {
        state = State.PANIC;
        recoveryPhase = 0;
        recoveryTickCounter = 0;
        normalTickCounter = 0;
        lastReason = TelemetryReason.PANIC_WINDOW_SPIKES;
        System.err.println("[" + LOG + "] ⚠️ PANIC mode entered! "
                + spikeCounter.getCountInWindow() + " spikes in " + windowSizeMs + "ms window");
    }

    private void enterRecovering() {
        state = State.RECOVERING;
        recoveryPhase = 0;
        recoveryTickCounter = 0;
        lastReason = TelemetryReason.RECOVERING_GRADUAL;
        System.out.println("[" + LOG + "] SpikePanicProtocol: Entering RECOVERING state");
    }

    private void enterNormal() {
        state = State.NORMAL;
        recoveryPhase = 0;
        recoveryTickCounter = 0;
        normalTickCounter = 0;
        lastReason = null;
        System.out.println("[" + LOG + "] SpikePanicProtocol: Recovered to NORMAL state");
    }

    /**
     * 현재 상태 반환.
     */
    public State getState() {
        return state;
    }

    /**
     * Throttle 배수 반환.
     * PANIC: 0.1 (극도 축소)
     * RECOVERING: 0.5 → 0.75 → 1.0 (점진적)
     * NORMAL: 1.0
     */
    public float getThrottleMultiplier() {
        return switch (state) {
            case PANIC -> 0.1f;
            case RECOVERING -> 0.5f + (recoveryPhase * 0.25f); // 0.5, 0.75, 1.0
            case NORMAL -> 1.0f;
        };
    }

    /**
     * 마지막 텔레메트리 이유 반환.
     */
    public TelemetryReason getLastReason() {
        return lastReason;
    }

    /**
     * 상태 리셋 (디버깅/테스트용).
     */
    public void reset() {
        state = State.NORMAL;
        recoveryPhase = 0;
        recoveryTickCounter = 0;
        normalTickCounter = 0;
        spikeCounter.clear();
        lastReason = null;
    }

    // --- Inner Class: 슬라이딩 윈도우 카운터 ---

    /**
     * 슬라이딩 윈도우 기반 이벤트 카운터.
     */
    private static class SlidingWindowCounter {
        private final long windowMs;
        private final java.util.Deque<Long> timestamps = new java.util.ArrayDeque<>();

        SlidingWindowCounter(long windowMs) {
            this.windowMs = windowMs;
        }

        void recordEvent() {
            long now = System.currentTimeMillis();
            timestamps.addLast(now);
            cleanup(now);
        }

        int getCountInWindow() {
            cleanup(System.currentTimeMillis());
            return timestamps.size();
        }

        private void cleanup(long now) {
            long cutoff = now - windowMs;
            while (!timestamps.isEmpty() && timestamps.peekFirst() < cutoff) {
                timestamps.pollFirst();
            }
        }

        void clear() {
            timestamps.clear();
        }
    }
}
