package com.echo.report.collector;

import com.echo.config.EchoConfig;
import com.echo.measure.EchoProfiler;

import java.time.Instant;

/**
 * 리포트 생성 컨텍스트 (불변 스냅샷).
 * 
 * <h2>설계 원칙 (Phase 1-A, BS-2 Mocking Hell 방지)</h2>
 * <ul>
 * <li>ReportContext는 <b>틱 종료 시점</b>에 캡처된 불변 스냅샷</li>
 * <li>게임 객체(IsoZombie 등) 복제 금지 - Primitive DTO만 허용</li>
 * <li>Collector들은 이 컨텍스트만 읽고, 직접 싱글톤 접근 최소화</li>
 * </ul>
 * 
 * <h2>스냅샷 경계</h2>
 * <p>
 * captureAt() 호출 시점의 상태가 고정됨. 리포트 생성 중 원본 데이터 변경과 무관.
 * </p>
 * 
 * @since Echo 2.1.0
 */
public class ReportContext {

    // ========================================
    // Immutable Fields (스냅샷)
    // ========================================

    private final long captureTimestamp;
    private final Instant captureInstant;
    private final long sessionDurationSeconds;
    private final long sessionStartTime;

    // Profiler 참조 (읽기 전용으로 사용)
    private final EchoProfiler profiler;

    // Config 스냅샷 (필수 필드만)
    private final int topN;
    private final boolean deepAnalysisEnabled;
    private final boolean luaProfilingEnabled;
    private final boolean debugMode;

    // ========================================
    // Constructor (private - use captureAt)
    // ========================================

    private ReportContext(EchoProfiler profiler, EchoConfig config) {
        this.captureTimestamp = System.currentTimeMillis();
        this.captureInstant = Instant.now();
        this.profiler = profiler;
        this.sessionDurationSeconds = profiler.getSessionDurationSeconds();
        this.sessionStartTime = profiler.getSessionStartTime();

        // Config 스냅샷 (변경 불가)
        this.topN = config.getTopNFunctions();
        this.deepAnalysisEnabled = config.isDeepAnalysisEnabled();
        this.luaProfilingEnabled = config.isLuaProfilingEnabled();
        this.debugMode = config.isDebugMode();
    }

    // ========================================
    // Factory (스냅샷 캡처)
    // ========================================

    /**
     * 현재 시점의 불변 스냅샷 생성.
     * 
     * @param profiler 프로파일러
     * @return 불변 ReportContext
     */
    public static ReportContext captureNow(EchoProfiler profiler) {
        return new ReportContext(profiler, EchoConfig.getInstance());
    }

    /**
     * 테스트용 팩토리 (Mocking 지원).
     * 
     * @param profiler 프로파일러
     * @param config   설정
     * @return 불변 ReportContext
     */
    public static ReportContext captureWith(EchoProfiler profiler, EchoConfig config) {
        return new ReportContext(profiler, config);
    }

    // ========================================
    // Getters (불변)
    // ========================================

    public long getCaptureTimestamp() {
        return captureTimestamp;
    }

    public Instant getCaptureInstant() {
        return captureInstant;
    }

    public long getSessionDurationSeconds() {
        return sessionDurationSeconds;
    }

    public long getSessionStartTime() {
        return sessionStartTime;
    }

    public EchoProfiler getProfiler() {
        return profiler;
    }

    public int getTopN() {
        return topN;
    }

    public boolean isDeepAnalysisEnabled() {
        return deepAnalysisEnabled;
    }

    public boolean isLuaProfilingEnabled() {
        return luaProfilingEnabled;
    }

    public boolean isDebugMode() {
        return debugMode;
    }
}
