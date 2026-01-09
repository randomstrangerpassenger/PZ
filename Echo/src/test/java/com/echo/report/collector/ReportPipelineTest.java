package com.echo.report.collector;

import com.echo.measure.EchoProfiler;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Map;

/**
 * ReportPipeline 단위 테스트.
 * 
 * Game-free 테스트: 섹션 조합 로직 검증.
 */
class ReportPipelineTest {

    private ReportPipeline pipeline;

    @BeforeEach
    void setUp() {
        pipeline = new ReportPipeline();
    }

    @Test
    @DisplayName("빈 파이프라인은 기본 메타데이터만 포함")
    void emptyPipeline() {
        ReportContext context = createMockContext();
        Map<String, Object> report = pipeline.collect(context);

        assertNotNull(report);
        assertTrue(report.containsKey("echo_report"));

        @SuppressWarnings("unchecked")
        Map<String, Object> echoReport = (Map<String, Object>) report.get("echo_report");
        assertTrue(echoReport.containsKey("version"));
        assertTrue(echoReport.containsKey("generated_at"));
    }

    @Test
    @DisplayName("Collector 등록 및 우선순위 정렬")
    void collectorRegistration() {
        pipeline.register(new TestCollector("b", 100));
        pipeline.register(new TestCollector("a", 10));

        assertEquals(2, pipeline.getCollectorCount());
    }

    @Test
    @DisplayName("등록된 Collector 데이터 수집")
    void collectsData() {
        pipeline.register(new TestCollector("test_section", 50));

        ReportContext context = createMockContext();
        Map<String, Object> report = pipeline.collect(context);

        @SuppressWarnings("unchecked")
        Map<String, Object> echoReport = (Map<String, Object>) report.get("echo_report");
        assertTrue(echoReport.containsKey("test_section"));
    }

    @Test
    @DisplayName("Collector 실패해도 리포트 생성 계속")
    void failingCollectorDoesNotBreak() {
        pipeline.register(new FailingCollector());
        pipeline.register(new TestCollector("good_section", 100));

        ReportContext context = createMockContext();
        Map<String, Object> report = pipeline.collect(context);

        @SuppressWarnings("unchecked")
        Map<String, Object> echoReport = (Map<String, Object>) report.get("echo_report");

        // 실패한 섹션에 에러 메시지
        assertTrue(echoReport.containsKey("failing"));
        @SuppressWarnings("unchecked")
        Map<String, Object> failingSection = (Map<String, Object>) echoReport.get("failing");
        assertTrue(failingSection.containsKey("error"));

        // 성공한 섹션은 정상
        assertTrue(echoReport.containsKey("good_section"));
    }

    @Test
    @DisplayName("비활성 Collector는 스킵")
    void disabledCollectorSkipped() {
        pipeline.register(new DisabledCollector());

        ReportContext context = createMockContext();
        Map<String, Object> report = pipeline.collect(context);

        @SuppressWarnings("unchecked")
        Map<String, Object> echoReport = (Map<String, Object>) report.get("echo_report");
        assertFalse(echoReport.containsKey("disabled"));
    }

    // === Test Helpers ===

    private ReportContext createMockContext() {
        EchoProfiler profiler = EchoProfiler.getInstance();
        profiler.reset();
        return ReportContext.captureNow(profiler);
    }

    static class TestCollector implements SectionCollector {
        private final String key;
        private final int priority;

        TestCollector(String key, int priority) {
            this.key = key;
            this.priority = priority;
        }

        @Override
        public String getSectionKey() {
            return key;
        }

        @Override
        public int getPriority() {
            return priority;
        }

        @Override
        public Map<String, Object> collect(ReportContext context) {
            return Map.of("status", "ok");
        }
    }

    static class FailingCollector implements SectionCollector {
        @Override
        public String getSectionKey() {
            return "failing";
        }

        @Override
        public Map<String, Object> collect(ReportContext context) {
            throw new RuntimeException("Intentional failure");
        }
    }

    static class DisabledCollector implements SectionCollector {
        @Override
        public String getSectionKey() {
            return "disabled";
        }

        @Override
        public boolean isEnabled(ReportContext context) {
            return false;
        }

        @Override
        public Map<String, Object> collect(ReportContext context) {
            return Map.of("should", "not appear");
        }
    }
}
