package com.echo.lua;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

/**
 * Lua 함수 통계 (v2.1)
 * 
 * 호출 횟수, 총 시간, self-time (자기 시간, 하위 호출 제외)을 추적합니다.
 * P2: context 태깅 지원 추가
 */
public class LuaFunctionStats {
    private final String name;
    private final LongAdder callCount = new LongAdder();
    private final LongAdder totalMicros = new LongAdder();
    private final LongAdder selfTimeMicros = new LongAdder(); // Phase 2: self-time
    private final AtomicLong maxMicros = new AtomicLong(0);

    // P2: Context 태깅
    private volatile String context = "Unknown";

    public LuaFunctionStats(String name) {
        this.name = name;
    }

    /**
     * 호출 기록 (legacy - total time만)
     */
    public void record(long durationMicros) {
        callCount.increment();
        totalMicros.add(durationMicros);
        updateMax(durationMicros);
    }

    /**
     * 호출 기록 (self-time 포함)
     * 
     * @param totalMicros 전체 실행 시간 (하위 호출 포함)
     * @param selfMicros  자기 시간 (하위 호출 제외)
     */
    public void record(long totalMicros, long selfMicros) {
        callCount.increment();
        this.totalMicros.add(totalMicros);
        this.selfTimeMicros.add(selfMicros);
        updateMax(totalMicros);
    }

    private void updateMax(long durationMicros) {
        long current;
        do {
            current = maxMicros.get();
            if (durationMicros <= current)
                return;
        } while (!maxMicros.compareAndSet(current, durationMicros));
    }

    /**
     * Context 설정 (마지막 호출의 컨텍스트로 덮어씀)
     */
    public void setContext(String context) {
        if (context != null && !context.isEmpty()) {
            this.context = context;
        }
    }

    public String getContext() {
        return context;
    }

    public String getName() {
        return name;
    }

    public long getCallCount() {
        return callCount.sum();
    }

    public long getTotalMicros() {
        return totalMicros.sum();
    }

    public long getSelfTimeMicros() {
        return selfTimeMicros.sum();
    }

    public long getMaxMicros() {
        return maxMicros.get();
    }

    public double getTotalMs() {
        return totalMicros.sum() / 1000.0;
    }

    public double getSelfTimeMs() {
        return selfTimeMicros.sum() / 1000.0;
    }

    public double getAverageMs() {
        long count = callCount.sum();
        return count == 0 ? 0 : getTotalMs() / count;
    }

    public Map<String, Object> toMap(int rank) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("rank", rank);
        map.put("name", name);
        map.put("context", context); // P2: context 포함
        map.put("call_count", getCallCount());
        map.put("total_time_ms", Math.round(getTotalMs() * 100) / 100.0);
        map.put("self_time_ms", Math.round(getSelfTimeMs() * 100) / 100.0);
        map.put("average_time_ms", Math.round(getAverageMs() * 1000) / 1000.0);
        map.put("max_time_ms", Math.round(getMaxMicros() / 1000.0 * 100) / 100.0);
        return map;
    }
}
