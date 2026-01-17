package com.echo.report.collector;

import com.echo.aggregate.TimingData;
import com.echo.measure.ProfilingPoint;
import com.echo.report.ReportUtils;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Summary 섹션 Collector.
 * 
 * <p>
 * 틱 성능 요약 정보를 수집합니다.
 * </p>
 * 
 * @since Echo 2.1.0
 */
public class SummaryCollector implements SectionCollector {

    @Override
    public String getSectionKey() {
        return "summary";
    }

    @Override
    public int getPriority() {
        return 10; // 가장 먼저 실행
    }

    @Override
    public Map<String, Object> collect(ReportContext context) {
        Map<String, Object> summary = new LinkedHashMap<>();
        TimingData tickData = context.getProfiler().getTimingData(ProfilingPoint.TICK);

        if (tickData != null) {
            summary.put("total_ticks", tickData.getCallCount());
            summary.put("average_tick_ms", ReportUtils.microsToMs(tickData.getAverageMicros()));
            summary.put("max_tick_spike_ms", ReportUtils.microsToMs(tickData.getMaxMicros()));
            summary.put("min_tick_ms", ReportUtils.microsToMs(tickData.getMinMicros()));
            summary.put("target_tick_ms", 16.67);

            double avgMs = tickData.getAverageMicros() / 1000.0;
            double score = Math.max(0, 100 - Math.max(0, avgMs - 16.67) * 5);
            summary.put("performance_score", ReportUtils.round(Math.min(100, score)));
        }

        return summary;
    }
}
