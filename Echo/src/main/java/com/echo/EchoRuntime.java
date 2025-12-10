package com.echo;

import java.util.concurrent.atomic.AtomicInteger;

/**
 * Echo 런타임 상태 관리
 * 
 * 모든 Echo 진입점에서 통일된 활성화 체크를 제공합니다.
 * Fail-soft: 에러가 많이 발생하면 자동으로 비활성화됩니다.
 */
public final class EchoRuntime {

    private static volatile boolean enabled = true;
    private static volatile boolean silentMode = false;
    private static final AtomicInteger errorCount = new AtomicInteger(0);
    private static volatile long errorWindowStart = System.currentTimeMillis();

    /** 에러 카운터 리셋 윈도우 (1분) */
    private static final long ERROR_WINDOW_MS = 60_000;
    /** 영구 비활성화 임계값 (1분 내 5회) */
    private static final int ERROR_THRESHOLD = 5;

    private EchoRuntime() {
        // Utility class
    }

    /**
     * Echo가 활성화되어 있는지 확인
     * 모든 Echo 진입점에서 이 메서드를 호출해야 합니다.
     * 
     * @return Echo 활성화 여부
     */
    public static boolean isEnabled() {
        return enabled && !silentMode;
    }

    /**
     * Echo가 Silent Mode인지 확인 (서버 환경)
     * 
     * @return Silent Mode 여부
     */
    public static boolean isSilentMode() {
        return silentMode;
    }

    /**
     * Echo 비활성화
     * 
     * @param reason 비활성화 사유
     */
    public static void disable(String reason) {
        if (enabled) {
            enabled = false;
            System.out.println("[Echo] Disabled: " + reason);
        }
    }

    /**
     * Silent Mode 설정 (서버 환경)
     * 
     * @param reason Silent Mode 사유
     */
    public static void enableSilentMode(String reason) {
        if (!silentMode) {
            silentMode = true;
            System.out.println("[Echo] Silent Mode: " + reason);
        }
    }

    /**
     * 에러 기록 및 임계값 초과 시 자동 비활성화
     * 
     * Fail-soft 래퍼에서 예외 발생 시 호출합니다.
     * 1분 내 5회 에러 발생 시 영구 비활성화됩니다.
     * 
     * @param context 에러 발생 컨텍스트 (예: "HUD", "TickHook")
     * @param e       발생한 예외 (null 가능)
     */
    public static void recordError(String context, Exception e) {
        long now = System.currentTimeMillis();

        // 윈도우 리셋
        if (now - errorWindowStart > ERROR_WINDOW_MS) {
            errorCount.set(0);
            errorWindowStart = now;
        }

        int count = errorCount.incrementAndGet();

        // 첫 번째 에러만 상세 로그
        if (count == 1 && e != null) {
            System.err.println("[Echo] Error in " + context + ": " + e.getMessage());
        }

        // 임계값 초과 시 비활성화
        if (count >= ERROR_THRESHOLD) {
            disable("Too many errors (" + count + "/" + ERROR_THRESHOLD + " in " + context + ")");
        }
    }

    /**
     * 런타임 상태 리셋 (테스트용)
     */
    public static void reset() {
        enabled = true;
        silentMode = false;
        errorCount.set(0);
        errorWindowStart = System.currentTimeMillis();
    }

    /**
     * 현재 에러 카운트 조회 (진단용)
     * 
     * @return 현재 윈도우 내 에러 수
     */
    public static int getErrorCount() {
        return errorCount.get();
    }
}
