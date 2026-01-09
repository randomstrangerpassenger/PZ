package com.echo.report.collector;

import java.util.Map;

/**
 * Spikes 섹션 Collector.
 * 
 * <p>
 * 성능 스파이크 로그를 수집합니다.
 * </p>
 * 
 * @since Echo 2.1.0
 */
public class SpikesCollector implements SectionCollector {

    @Override
    public String getSectionKey() {
        return "spikes";
    }

    @Override
    public int getPriority() {
        return 30;
    }

    @Override
    public Map<String, Object> collect(ReportContext context) {
        return context.getProfiler().getSpikeLog().toMap();
    }
}
