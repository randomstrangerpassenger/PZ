package com.echo.report;

import com.echo.measure.EchoProfiler;

import org.junit.jupiter.api.*;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Phase 0: Report Schema Snapshot
 * 
 * collect() 반환 Map의 키/중첩 구조를 스냅샷으로 저장하고
 * 리팩토링 후 동등성을 검증합니다.
 */
class ReportSchemaSnapshot {

    /**
     * 현재 Report 스키마의 키 구조 (v1.0.1 기준)
     * 리팩토링 후 이 구조가 유지되어야 함
     */
    private static final Set<String> EXPECTED_TOP_LEVEL_KEYS = Set.of(
            "echo_report");

    private static final Set<String> EXPECTED_ECHO_REPORT_KEYS = Set.of(
            "version",
            "generated_at",
            "session_duration_seconds",
            "summary",
            "subsystems",
            "heavy_functions",
            "tick_phase_breakdown",
            "tick_histogram",
            "spikes",
            "freeze_history",
            "memory",
            "lua_profiling",
            "lua_gc",
            "fuse_deep_analysis",
            "validation_status",
            "pulse_contract",
            "report_quality",
            "analysis",
            "metadata",
            "extended_analysis",
            "memory_timeseries",
            "bottleneck_detection",
            "network",
            "render",
            "timeseries_summary");

    private static final Set<String> EXPECTED_SUMMARY_KEYS = Set.of(
            "total_ticks",
            "average_tick_ms",
            "max_tick_spike_ms",
            "min_tick_ms",
            "target_tick_ms",
            "performance_score");

    private EchoProfiler profiler;
    private ReportDataCollector collector;

    @BeforeEach
    void setUp() {
        profiler = EchoProfiler.getInstance();
        profiler.reset();
        profiler.enable(true);
        collector = new ReportDataCollector(profiler, 10);
    }

    @AfterEach
    void tearDown() {
        profiler.disable();
    }

    @Test
    @DisplayName("Schema: Top-level keys must match")
    void schema_topLevelKeys() {
        Map<String, Object> report = collector.collect();

        assertEquals(EXPECTED_TOP_LEVEL_KEYS, report.keySet(),
                "Top-level keys must match expected schema");
    }

    @Test
    @DisplayName("Schema: echo_report keys must match")
    @SuppressWarnings("unchecked")
    void schema_echoReportKeys() {
        Map<String, Object> report = collector.collect();
        Map<String, Object> echoReport = (Map<String, Object>) report.get("echo_report");

        assertNotNull(echoReport, "echo_report must exist");

        // 모든 필수 키가 존재하는지 확인
        for (String key : EXPECTED_ECHO_REPORT_KEYS) {
            assertTrue(echoReport.containsKey(key),
                    "Missing required key: " + key);
        }
    }

    @Test
    @DisplayName("Schema: summary structure must be stable")
    @SuppressWarnings("unchecked")
    void schema_summaryStructure() {
        // 최소한의 데이터 생성
        profiler.push(com.echo.measure.ProfilingPoint.TICK);
        profiler.pop(com.echo.measure.ProfilingPoint.TICK);

        Map<String, Object> report = collector.collect();
        Map<String, Object> echoReport = (Map<String, Object>) report.get("echo_report");
        Map<String, Object> summary = (Map<String, Object>) echoReport.get("summary");

        assertNotNull(summary, "summary must exist");

        for (String key : EXPECTED_SUMMARY_KEYS) {
            assertTrue(summary.containsKey(key),
                    "Summary missing required key: " + key);
        }
    }

    @Test
    @DisplayName("Schema: version must be 1.0.1")
    @SuppressWarnings("unchecked")
    void schema_version() {
        Map<String, Object> report = collector.collect();
        Map<String, Object> echoReport = (Map<String, Object>) report.get("echo_report");

        assertEquals("1.0.1", echoReport.get("version"),
                "Report version must be 1.0.1");
    }

    @Test
    @DisplayName("Schema: collect() returns Map (not DTO)")
    void schema_returnTypeIsMap() {
        Object result = collector.collect();

        assertInstanceOf(Map.class, result,
                "collect() must return Map<String, Object>");
    }

    @Test
    @DisplayName("Snapshot: Print current schema for reference")
    @SuppressWarnings("unchecked")
    void snapshot_printSchema() {
        Map<String, Object> report = collector.collect();

        System.out.println("=== Report Schema Snapshot ===");
        System.out.println("Top-level keys: " + report.keySet());

        Map<String, Object> echoReport = (Map<String, Object>) report.get("echo_report");
        System.out.println("echo_report keys: " + echoReport.keySet());

        // 각 섹션의 타입 출력
        for (Map.Entry<String, Object> entry : echoReport.entrySet()) {
            String type = entry.getValue() == null ? "null" : entry.getValue().getClass().getSimpleName();
            System.out.println("  " + entry.getKey() + ": " + type);
        }
    }

    /**
     * 키 구조를 재귀적으로 추출 (디버깅용)
     */

}
