package com.pulse.api;

/**
 * Pulse 전역 상수.
 * 매직 넘버 대신 이 상수들을 사용하세요.
 * 
 * @since 1.1.0
 */
public final class PulseConstants {

    private PulseConstants() {
    }

    // ═══════════════════════════════════════════════════════════════
    // 파일 경로
    // ═══════════════════════════════════════════════════════════════

    /** 모드 디렉토리명 */
    public static final String MODS_DIR_NAME = "mods";

    /** 설정 디렉토리명 */
    public static final String CONFIG_DIR_NAME = "config";

    // ═══════════════════════════════════════════════════════════════
    // 타이밍 상수 (밀리초)
    // ═══════════════════════════════════════════════════════════════

    /** 기본 틱 간격 (ms) - 60 FPS 기준 */
    public static final long TICK_INTERVAL_MS = 16;

    /** 틱 타임아웃 (ms) - 이 시간 초과 시 프리즈로 간주 */
    public static final long TICK_TIMEOUT_MS = 3000;

    /** Fallback 틱 체크 간격 (ms) */
    public static final long FALLBACK_CHECK_INTERVAL_MS = 5000;

    /** Rate Limiting 정리 임계값 (ms) */
    public static final long RATE_LIMIT_CLEANUP_THRESHOLD_MS = 60_000;

    /** 프로파일러 분석 간격 (ms) */
    public static final long PROFILER_ANALYSIS_INTERVAL_MS = 5000;

    // ═══════════════════════════════════════════════════════════════
    // 스파이크/성능 임계값 (마이크로초)
    // ═══════════════════════════════════════════════════════════════

    /** 스파이크 감지 임계값 (μs) - 33ms 초과 시 스파이크 */
    public static final long SPIKE_THRESHOLD_MICROS = 33_000;

    /** 프리즈 감지 임계값 (μs) - 100ms 초과 시 프리즈 */
    public static final long FREEZE_THRESHOLD_MICROS = 100_000;

    /** 심각한 프리즈 임계값 (μs) - 500ms 초과 */
    public static final long SEVERE_FREEZE_THRESHOLD_MICROS = 500_000;

    // ═══════════════════════════════════════════════════════════════
    // 품질 점수
    // ═══════════════════════════════════════════════════════════════

    /** 최소 샘플 수 (품질 점수 계산용) */
    public static final int MIN_SAMPLES_FOR_QUALITY = 100;

    /** 최소 세션 시간 (초) */
    public static final int MIN_SESSION_SECONDS = 30;

    // ═══════════════════════════════════════════════════════════════
    // 캐시/풀 크기
    // ═══════════════════════════════════════════════════════════════

    /** ProfilingScope 풀 크기 */
    public static final int PROFILING_SCOPE_POOL_SIZE = 16;

    /** 스파이크 로그 최대 항목 수 */
    public static final int MAX_SPIKE_LOG_ENTRIES = 1000;

    /** 콜 스택 로그 최대 항목 수 */
    public static final int MAX_CALL_STACK_ENTRIES = 50;

    // ═══════════════════════════════════════════════════════════════
    // 버전 정보
    // ═══════════════════════════════════════════════════════════════

    /** Pulse 버전 */
    public static final String PULSE_VERSION = "1.1.0";

    // [REMOVED] Spoke 버전 상수 - Hub는 Spoke 존재를 몰라야 함 (헌법 준수)
}
