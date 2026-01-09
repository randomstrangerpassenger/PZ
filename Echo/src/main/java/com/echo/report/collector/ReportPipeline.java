package com.echo.report.collector;

import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 리포트 파이프라인.
 * 
 * <p>
 * SectionCollector들을 조합하여 전체 리포트를 생성합니다.
 * </p>
 * 
 * <h2>설계 원칙 (Phase 1-A)</h2>
 * <ul>
 * <li>레거시 ReportDataCollector와 호환 유지</li>
 * <li>점진적 마이그레이션 지원</li>
 * <li>각 섹션은 독립적으로 실패해도 리포트 생성 계속</li>
 * </ul>
 * 
 * @since Echo 2.1.0
 */
public class ReportPipeline {

    private static final String REPORT_VERSION = "2.1.0";

    private final List<SectionCollector> collectors;

    public ReportPipeline() {
        this.collectors = new ArrayList<>();
    }

    /**
     * Collector 등록.
     */
    public ReportPipeline register(SectionCollector collector) {
        collectors.add(collector);
        // 우선순위로 정렬
        collectors.sort(Comparator.comparingInt(SectionCollector::getPriority));
        return this;
    }

    /**
     * 전체 리포트 생성.
     * 
     * @param context 불변 리포트 컨텍스트
     * @return 전체 리포트 맵
     */
    public Map<String, Object> collect(ReportContext context) {
        Map<String, Object> report = new LinkedHashMap<>();
        Map<String, Object> echoReport = new LinkedHashMap<>();

        // 기본 메타데이터
        echoReport.put("version", REPORT_VERSION);
        echoReport.put("generated_at", formatInstant(context.getCaptureInstant()));
        echoReport.put("session_duration_seconds", context.getSessionDurationSeconds());

        // 각 섹션 수집
        for (SectionCollector collector : collectors) {
            if (!collector.isEnabled(context)) {
                continue;
            }

            try {
                Map<String, Object> sectionData = collector.collect(context);
                if (sectionData != null) {
                    echoReport.put(collector.getSectionKey(), sectionData);
                }
            } catch (Exception e) {
                // 섹션 실패해도 리포트 계속 생성
                Map<String, Object> errorData = new HashMap<>();
                errorData.put("error", "Section collection failed: " + e.getMessage());
                echoReport.put(collector.getSectionKey(), errorData);
            }
        }

        report.put("echo_report", echoReport);
        return report;
    }

    /**
     * 등록된 Collector 수.
     */
    public int getCollectorCount() {
        return collectors.size();
    }

    private String formatInstant(Instant instant) {
        return DateTimeFormatter.ISO_INSTANT.format(instant);
    }
}
