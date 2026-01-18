package com.echo.report;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Heavy Function 랭킹 데이터.
 * 
 * v4 Phase 3: ReportDataCollector에서 분리.
 * 프로파일러 함수별 성능 통계를 담는 불변 DTO.
 * 
 * @since Echo 0.8.0
 */
public class RankedFunction {

    private final String label;
    private final String parentPoint;
    private final long callCount;
    private final long totalMicros;
    private final long maxMicros;

    public RankedFunction(String label, String parentPoint, long callCount,
            long totalMicros, long maxMicros) {
        this.label = label;
        this.parentPoint = parentPoint;
        this.callCount = callCount;
        this.totalMicros = totalMicros;
        this.maxMicros = maxMicros;
    }

    public String getLabel() {
        return label;
    }

    public String getParentPoint() {
        return parentPoint;
    }

    public long getCallCount() {
        return callCount;
    }

    public long getTotalMicros() {
        return totalMicros;
    }

    public long getMaxMicros() {
        return maxMicros;
    }

    /**
     * 랭킹 정보를 Map으로 변환.
     * 
     * @param rank 순위 (1부터 시작)
     * @return Map 표현
     */
    public Map<String, Object> toMap(int rank) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("rank", rank);
        map.put("label", label);
        map.put("parent_point", parentPoint);
        map.put("call_count", callCount);
        map.put("total_time_ms", Math.round(totalMicros / 10.0) / 100.0);
        map.put("average_time_ms", callCount > 0
                ? Math.round((double) totalMicros / callCount / 10.0) / 100.0
                : 0);
        map.put("max_time_ms", Math.round(maxMicros / 10.0) / 100.0);
        return map;
    }
}
