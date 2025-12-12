package com.echo.lua;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.LongAdder;

public class LuaEventStats {
    private final String name;
    private final LongAdder fireCount = new LongAdder();
    private final LongAdder totalHandlers = new LongAdder();
    private final LongAdder totalMicros = new LongAdder();

    public LuaEventStats(String name) {
        this.name = name;
    }

    public void record(long durationMicros, int handlerCount) {
        fireCount.increment();
        totalHandlers.add(handlerCount);
        totalMicros.add(durationMicros);
    }

    public String getName() {
        return name;
    }

    public long getFireCount() {
        return fireCount.sum();
    }

    public long getTotalHandlers() {
        return totalHandlers.sum();
    }

    public double getTotalMs() {
        return totalMicros.sum() / 1000.0;
    }

    public double getAverageHandlersPerFire() {
        long count = fireCount.sum();
        return count == 0 ? 0 : (double) totalHandlers.sum() / count;
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("name", name);
        map.put("fire_count", getFireCount());
        map.put("total_handlers", getTotalHandlers());
        map.put("avg_handlers_per_fire", Math.round(getAverageHandlersPerFire() * 10) / 10.0);
        map.put("total_time_ms", Math.round(getTotalMs() * 100) / 100.0);
        return map;
    }
}
