package com.echo.lua;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

public class LuaFunctionStats {
    private final String name;
    private final LongAdder callCount = new LongAdder();
    private final LongAdder totalMicros = new LongAdder();
    private final AtomicLong maxMicros = new AtomicLong(0);

    public LuaFunctionStats(String name) {
        this.name = name;
    }

    public void record(long durationMicros) {
        callCount.increment();
        totalMicros.add(durationMicros);
        long current;
        do {
            current = maxMicros.get();
            if (durationMicros <= current)
                return;
        } while (!maxMicros.compareAndSet(current, durationMicros));
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

    public long getMaxMicros() {
        return maxMicros.get();
    }

    public double getTotalMs() {
        return totalMicros.sum() / 1000.0;
    }

    public double getAverageMs() {
        long count = callCount.sum();
        return count == 0 ? 0 : getTotalMs() / count;
    }

    public Map<String, Object> toMap(int rank) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("rank", rank);
        map.put("name", name);
        map.put("call_count", getCallCount());
        map.put("total_time_ms", Math.round(getTotalMs() * 100) / 100.0);
        map.put("average_time_ms", Math.round(getAverageMs() * 1000) / 1000.0);
        map.put("max_time_ms", Math.round(getMaxMicros() / 1000.0 * 100) / 100.0);
        return map;
    }
}
