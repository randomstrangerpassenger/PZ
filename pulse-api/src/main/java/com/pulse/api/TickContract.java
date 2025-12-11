package com.pulse.api;

/**
 * Pulse-Echo 공유 Tick 계약 상수
 * 
 * Pulse와 Echo가 동일한 기준으로 Tick 이벤트를 해석하기 위한 공식 계약.
 * 모든 시간 단위는 milliseconds로 통일됨.
 * 
 * @since Pulse 0.9 / Echo 0.9
 */
public final class TickContract {

    private TickContract() {
    }

    // ═══════════════════════════════════════════════════════════════
    // 계약 버전 (Fuse/Nerve 호환성 확인용)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 계약 버전. 변경 시 Echo Report에 기록됨.
     */
    public static final int VERSION = 1;

    // ═══════════════════════════════════════════════════════════════
    // Tick 타이밍 계약
    // ═══════════════════════════════════════════════════════════════

    /**
     * 목표 Tick Rate (FPS)
     * TARGET_FPS와 동일한 의미, 명확성을 위해 추가.
     */
    public static final int TARGET_TICK_RATE = 60;

    /**
     * 목표 FPS (Project Zomboid 기본값)
     */
    public static final int TARGET_FPS = TARGET_TICK_RATE;

    /**
     * 예상 틱 간격 (nanoseconds)
     * 16,666,666ns
     */
    public static final long TARGET_TICK_DELTA_NANOS = 1_000_000_000L / TARGET_TICK_RATE;

    /**
     * 예상 틱 간격 (ms)
     * = 1000 / 60 ≈ 16.67ms
     */
    public static final float EXPECTED_DELTA_MS = 1000.0f / TARGET_FPS;

    /**
     * 스파이크 임계값 (ms)
     * 이 값 초과 시 "large delta" 경고 발생
     */
    public static final float MAX_REASONABLE_DELTA_MS = 100.0f;

    /**
     * 절대 최대 델타 (ms)
     * 5초 이상은 비정상 상태로 간주
     */
    public static final float MAX_ABSOLUTE_DELTA_MS = 5000.0f;

    /**
     * 중복 이벤트 감지 임계값 (nanoseconds)
     * 1ms 이내 연속 틱은 중복으로 간주
     */
    public static final long DUPLICATE_THRESHOLD_NS = 1_000_000L;

    // ═══════════════════════════════════════════════════════════════
    // Fallback 정책
    // ═══════════════════════════════════════════════════════════════

    /**
     * 기본 Fallback tick 간격 (ms)
     * = EXPECTED_DELTA_MS * 12 ≈ 200ms
     */
    public static final long DEFAULT_FALLBACK_INTERVAL_MS = 200L;

    /**
     * Fallback 활성화 대기 시간 (ms)
     * 이 시간 동안 tick hook이 없으면 fallback 활성화 고려
     */
    public static final long FALLBACK_ACTIVATION_DELAY_MS = 3000L;

    // ═══════════════════════════════════════════════════════════════
    // 유틸리티 메서드
    // ═══════════════════════════════════════════════════════════════

    /**
     * 주어진 delta time이 유효한지 검사
     * 
     * @param deltaMs delta time in milliseconds
     * @return true if valid, false otherwise
     */
    public static boolean isValidDelta(float deltaMs) {
        return deltaMs > 0 && deltaMs <= MAX_ABSOLUTE_DELTA_MS;
    }

    /**
     * 주어진 delta time이 스파이크인지 검사
     * 
     * @param deltaMs delta time in milliseconds
     * @return true if spike, false otherwise
     */
    public static boolean isSpike(float deltaMs) {
        return deltaMs > MAX_REASONABLE_DELTA_MS && deltaMs <= MAX_ABSOLUTE_DELTA_MS;
    }

    /**
     * 계약 정보 문자열 반환
     */
    public static String getContractInfo() {
        return String.format("TickContract v%d (FPS=%d, expected=%.2fms, max=%,.0fms)",
                VERSION, TARGET_FPS, EXPECTED_DELTA_MS, MAX_ABSOLUTE_DELTA_MS);
    }
}
