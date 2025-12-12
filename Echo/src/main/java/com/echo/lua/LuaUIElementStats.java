package com.echo.lua;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

public class LuaUIElementStats {
    private final LuaUICategory category;
    private final String elementName;
    private final LongAdder drawCount = new LongAdder();
    private final LongAdder totalMicros = new LongAdder();
    private final AtomicLong maxMicros = new AtomicLong(0);

    public LuaUIElementStats(LuaUICategory category, String elementName) {
        this.category = category;
        this.elementName = elementName;
    }

    public void record(long durationMicros) {
        drawCount.increment();
        totalMicros.add(durationMicros);
        long current;
        do {
            current = maxMicros.get();
            if (durationMicros <= current)
                return;
        } while (!maxMicros.compareAndSet(current, durationMicros));
    }

    public LuaUICategory getCategory() {
        return category;
    }

    public String getElementName() {
        return elementName;
    }

    public long getDrawCount() {
        return drawCount.sum();
    }

    public long getTotalMicros() {
        return totalMicros.sum();
    }

    public double getTotalMs() {
        return totalMicros.sum() / 1000.0;
    }

    public double getAverageMs() {
        long count = drawCount.sum();
        return count == 0 ? 0 : getTotalMs() / count;
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("category", category.name());
        map.put("element", elementName);
        map.put("draw_count", getDrawCount());
        map.put("total_ms", Math.round(getTotalMs() * 100) / 100.0);
        map.put("avg_ms", Math.round(getAverageMs() * 1000) / 1000.0);
        return map;
    }
}
