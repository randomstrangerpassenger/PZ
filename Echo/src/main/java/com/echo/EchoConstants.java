package com.echo;

/**
 * Echo Profiler 전역 상수
 * 
 * @since 0.8.0
 * @since 0.9.0 - Validation, Session, FreezeDetector 상수 추가
 */
public final class EchoConstants {

    private EchoConstants() {
    }

    // ═══════════════════════════════════════════════════════════════
    // Version
    // ═══════════════════════════════════════════════════════════════

    /** 현재 Echo 버전 */
    public static final String VERSION = "0.9.0";

    // ═══════════════════════════════════════════════════════════════
    // Spike Detection
    // ═══════════════════════════════════════════════════════════════

    /** 기본 스파이크 임계값 (ms) - 30fps 기준 2프레임 */
    public static final double DEFAULT_SPIKE_THRESHOLD_MS = 33.33;

    /** 스파이크 로그 최대 엔트리 수 */
    public static final int SPIKE_LOG_MAX_ENTRIES = 100;

    /** 스파이크 스택 캡처 최대 깊이 */
    public static final int SPIKE_MAX_STACK_DEPTH = 10;

    // ═══════════════════════════════════════════════════════════════
    // Histogram
    // ═══════════════════════════════════════════════════════════════

    /** 히스토그램 최근 샘플 버퍼 크기 */
    public static final int HISTOGRAM_SAMPLE_BUFFER = 1000;

    /** 기본 히스토그램 버킷 경계 (ms) */
    public static final double[] DEFAULT_HISTOGRAM_BUCKETS = {
            0, 5, 10, 16.67, 20, 33.33, 50, 100, 200
    };

    // ═══════════════════════════════════════════════════════════════
    // Rolling Stats
    // ═══════════════════════════════════════════════════════════════

    /** 초당 예상 샘플 수 (60 FPS 기준) */
    public static final int SAMPLES_PER_SECOND = 60;

    /** 1초 윈도우 샘플 수 */
    public static final int ROLLING_WINDOW_1S = SAMPLES_PER_SECOND;

    /** 5초 윈도우 샘플 수 */
    public static final int ROLLING_WINDOW_5S = SAMPLES_PER_SECOND * 5;

    /** 60초 윈도우 샘플 수 */
    public static final int ROLLING_WINDOW_60S = SAMPLES_PER_SECOND * 60;

    // ═══════════════════════════════════════════════════════════════
    // Object Pool
    // ═══════════════════════════════════════════════════════════════

    /** ProfilingScope 풀 크기 */
    public static final int SCOPE_POOL_SIZE = 16;

    // ═══════════════════════════════════════════════════════════════
    // Report
    // ═══════════════════════════════════════════════════════════════

    /** 기본 Top N 함수 표시 수 */
    public static final int DEFAULT_TOP_N = 10;

    /** 기본 리포트 저장 경로 */
    public static final String DEFAULT_REPORT_DIR = System.getProperty("user.home") + "/Zomboid/echo_reports";

    /** 기본 테스트 결과 저장 경로 */
    public static final String DEFAULT_TEST_DIR = "./echo_tests";

    // ═══════════════════════════════════════════════════════════════
    // Validation (Self-Validation)
    // ═══════════════════════════════════════════════════════════════

    /** 자가검증 지연 시간 (ms) */
    public static final long VALIDATION_DELAY_MS = 10_000;

    /** 워밍업 기간 (ms) */
    public static final long WARMUP_DURATION_MS = 5_000;

    /** Fallback 활성화 대기 시간 (ms) */
    public static final long FALLBACK_ACTIVATION_DELAY_MS = 3_000;

    /** Fallback 재시도 최대 횟수 */
    public static final int FALLBACK_MAX_RETRIES = 3;

    // ═══════════════════════════════════════════════════════════════
    // Session Management
    // ═══════════════════════════════════════════════════════════════

    /** 세션 dirty 판정 최소 틱 수 */
    public static final int MIN_TICKS_FOR_DIRTY = 600;

    /** 메뉴 렌더 세션 종료 프레임 수 */
    public static final int MENU_RENDER_THRESHOLD = 10;

    /** 메뉴 이탈 감지 틱 수 */
    public static final int MENU_EXIT_THRESHOLD = 60;

    // ═══════════════════════════════════════════════════════════════
    // Freeze Detector
    // ═══════════════════════════════════════════════════════════════

    /** 프리즈 감지 임계값 (ms) */
    public static final long FREEZE_THRESHOLD_MS = 500;

    /** Watchdog 체크 주기 (ms) */
    public static final long WATCHDOG_CHECK_INTERVAL_MS = 100;

    /** 프리즈 히스토리 최대 항목 수 */
    public static final int MAX_FREEZE_HISTORY = 10;

    // ═══════════════════════════════════════════════════════════════
    // Timeout & Cache
    // ═══════════════════════════════════════════════════════════════

    /** Lua 통계 캐시 TTL (ms) */
    public static final long LUA_CACHE_TTL_MS = 1000;

    /** 최근 샘플 버퍼 크기 */
    public static final int RECENT_SAMPLES_SIZE = 100;

    // ═══════════════════════════════════════════════════════════════
    // UI Constants
    // ═══════════════════════════════════════════════════════════════

    /** HotspotPanel 업데이트 간격 (ms) */
    public static final long UI_UPDATE_INTERVAL_MS = 1000;

    /** HotspotPanel 폭 */
    public static final int HOTSPOT_PANEL_WIDTH = 280;

    /** HotspotPanel 레이어 우선순위 */
    public static final int HOTSPOT_PANEL_LAYER_PRIORITY = 110;

    // ═══════════════════════════════════════════════════════════════
    // Log Tags (for PulseLogger)
    // ═══════════════════════════════════════════════════════════════

    /** Echo 기본 로그 태그 */
    public static final String LOG = "Echo";

    /** LuaHook 서브모듈 */
    public static final String LOG_LUA_HOOK = "Echo/LuaHook";

    /** FallbackTick 서브모듈 */
    public static final String LOG_FALLBACK_TICK = "Echo/FallbackTick";

    /** SubProfiler 브릿지 */
    public static final String LOG_SUB_PROFILER_BRIDGE = "Echo/SubProfilerBridge";

    /** DetailedWindow 서브모듈 */
    public static final String LOG_DETAILED_WINDOW = "Echo/DetailedWindow";

    /** LuaTracker 서브모듈 */
    public static final String LOG_LUA_TRACKER = "Echo/LuaTracker";

    /** TickPhase 서브모듈 */
    public static final String LOG_TICK_PHASE = "Echo/TickPhase";

    /** Mixin 관련 로그 */
    public static final String LOG_MIXIN = "Echo/Mixin";
}
