package com.echo.report.collector;

import com.echo.validation.SelfValidation;

import java.util.Map;

/**
 * Validation 섹션 Collector.
 * 
 * <p>
 * 자가 검증 상태를 수집합니다.
 * </p>
 * 
 * @since Echo 2.1.0
 */
public class ValidationCollector implements SectionCollector {

    @Override
    public String getSectionKey() {
        return "validation_status";
    }

    @Override
    public int getPriority() {
        return 80;
    }

    @Override
    public Map<String, Object> collect(ReportContext context) {
        return SelfValidation.getInstance().toMap();
    }
}
