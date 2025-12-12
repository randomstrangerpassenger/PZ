package com.echo.validation;

import com.echo.aggregate.DataQualityFlag;

/**
 * Warmup 감지기.
 * 
 * 게임 시작 직후 몇 초간은 클래스 로딩, JIT 컴파일 등으로
 * 프로파일링 데이터가 불안정합니다. 이 기간을 감지하여
 * 데이터 품질 플래그를 적용합니다.
 * 
 * @since 1.0.1
 */
public class WarmupDetector {

    private static final WarmupDetector INSTANCE = new WarmupDetector();

    // Warmup 기간 (밀리초)
    private static final long DEFAULT_WARMUP_DURATION_MS = 5000; // 5초

    private long sessionStartTime;
    private long warmupDurationMs = DEFAULT_WARMUP_DURATION_MS;
    private volatile boolean warmupComplete = false;

    private WarmupDetector() {
        this.sessionStartTime = System.currentTimeMillis();
    }

    public static WarmupDetector getInstance() {
        return INSTANCE;
    }

    /**
     * 세션 시작 시간 초기화
     */
    public void startSession() {
        this.sessionStartTime = System.currentTimeMillis();
        this.warmupComplete = false;
    }

    /**
     * Warmup 기간 설정
     * 
     * @param durationMs 밀리초 단위 기간
     */
    public void setWarmupDuration(long durationMs) {
        this.warmupDurationMs = durationMs;
    }

    /**
     * 현재 Warmup 기간 중인지 확인
     */
    public boolean isInWarmup() {
        if (warmupComplete) {
            return false;
        }

        long elapsed = System.currentTimeMillis() - sessionStartTime;
        if (elapsed >= warmupDurationMs) {
            warmupComplete = true;
            return false;
        }
        return true;
    }

    /**
     * Warmup 상태를 확인하고 해당 시 플래그 반환
     * 
     * @return WARMUP_PERIOD if in warmup, null otherwise
     */
    public DataQualityFlag checkAndFlag() {
        return isInWarmup() ? DataQualityFlag.WARMUP_PERIOD : null;
    }

    /**
     * Warmup 경과 시간 (밀리초)
     */
    public long getElapsedWarmupMs() {
        return System.currentTimeMillis() - sessionStartTime;
    }

    /**
     * Warmup 진행률 (0.0 ~ 1.0)
     */
    public double getWarmupProgress() {
        if (warmupComplete)
            return 1.0;
        long elapsed = System.currentTimeMillis() - sessionStartTime;
        return Math.min(1.0, (double) elapsed / warmupDurationMs);
    }

    /**
     * Warmup 완료 여부
     */
    public boolean isWarmupComplete() {
        // 부작용으로 상태 업데이트
        isInWarmup();
        return warmupComplete;
    }

    /**
     * 강제로 Warmup 완료 처리
     */
    public void forceComplete() {
        this.warmupComplete = true;
    }

    /**
     * 상태 초기화
     */
    public void reset() {
        this.sessionStartTime = System.currentTimeMillis();
        this.warmupComplete = false;
    }
}
