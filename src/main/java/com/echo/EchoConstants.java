package com.echo;

/**
 * Echo Profiler 전역 상수
 */
public final class EchoConstants {

    private EchoConstants() {
        // 상수 클래스
    }

    // ============================================================
    // 버전
    // ============================================================

    /** 현재 Echo 버전 */
    public static final String VERSION = "2.0.0";

    // ============================================================
    // 스파이크 감지
    // ============================================================

    /** 기본 스파이크 임계값 (ms) - 30fps 기준 2프레임 */
    public static final double DEFAULT_SPIKE_THRESHOLD_MS = 33.33;

    /** 스파이크 로그 최대 엔트리 수 */
    public static final int SPIKE_LOG_MAX_ENTRIES = 100;

    /** 스파이크 스택 캡처 최대 깊이 */
    public static final int SPIKE_MAX_STACK_DEPTH = 10;

    // ============================================================
    // 히스토그램
    // ============================================================

    /** 히스토그램 최근 샘플 버퍼 크기 */
    public static final int HISTOGRAM_SAMPLE_BUFFER = 1000;

    /** 기본 히스토그램 버킷 경계 (ms) */
    public static final double[] DEFAULT_HISTOGRAM_BUCKETS = {
            0, 5, 10, 16.67, 20, 33.33, 50, 100, 200
    };

    // ============================================================
    // 롤링 통계
    // ============================================================

    /** 초당 예상 샘플 수 (60 FPS 기준) */
    public static final int SAMPLES_PER_SECOND = 60;

    /** 1초 윈도우 샘플 수 */
    public static final int ROLLING_WINDOW_1S = SAMPLES_PER_SECOND;

    /** 5초 윈도우 샘플 수 */
    public static final int ROLLING_WINDOW_5S = SAMPLES_PER_SECOND * 5;

    /** 60초 윈도우 샘플 수 */
    public static final int ROLLING_WINDOW_60S = SAMPLES_PER_SECOND * 60;

    // ============================================================
    // 객체 풀
    // ============================================================

    /** ProfilingScope 풀 크기 */
    public static final int SCOPE_POOL_SIZE = 16;

    // ============================================================
    // 리포트
    // ============================================================

    /** 기본 Top N 함수 표시 수 */
    public static final int DEFAULT_TOP_N = 10;

    /** 기본 리포트 저장 경로 */
    public static final String DEFAULT_REPORT_DIR = "./echo_reports";

    /** 기본 테스트 결과 저장 경로 */
    public static final String DEFAULT_TEST_DIR = "./echo_tests";

    // ============================================================
    // 타임아웃 및 캐시
    // ============================================================

    /** Lua 통계 캐시 TTL (ms) */
    public static final long LUA_CACHE_TTL_MS = 1000;

    /** 최근 샘플 버퍼 크기 */
    public static final int RECENT_SAMPLES_SIZE = 100;
}
