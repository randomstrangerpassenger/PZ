package com.echo.lua;

import com.echo.config.EchoConfig;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Tracks Memory/GC pressure during the game loop.
 * 
 * Note: This tracks JVM Heap Delta, which is an *estimation* of general GC
 * pressure,
 * including both Java and Lua (since Kahlua objects are Java objects).
 */
public class LuaGCProfiler {

    private static final LuaGCProfiler INSTANCE = new LuaGCProfiler();

    private long lastTotalMemory = 0;
    private long lastFreeMemory = 0;

    private final java.util.List<java.lang.management.GarbageCollectorMXBean> gcBeans;
    private long lastTotalGcTime = 0;
    private final AtomicLong gcPausePerTick = new AtomicLong(0);
    private final java.util.concurrent.atomic.AtomicLong heapDeltaPerTick = new java.util.concurrent.atomic.AtomicLong(
            0);

    private LuaGCProfiler() {
        gcBeans = java.lang.management.ManagementFactory.getGarbageCollectorMXBeans();
    }

    public static LuaGCProfiler getInstance() {
        return INSTANCE;
    }

    /**
     * Called at the start of a profiling period (e.g., start of Tick).
     */
    public void onTickStart() {
        if (!EchoConfig.getInstance().isLuaProfilingEnabled())
            return;

        Runtime rt = Runtime.getRuntime();
        lastTotalMemory = rt.totalMemory();
        lastFreeMemory = rt.freeMemory();

        // Capture GC time at start
        long totalGc = 0;
        for (java.lang.management.GarbageCollectorMXBean bean : gcBeans) {
            long time = bean.getCollectionTime();
            if (time != -1)
                totalGc += time;
        }
        lastTotalGcTime = totalGc;
    }

    /**
     * Called at the end of a profiling period.
     * Calculates the "Heap Delta" (Allocation - GC).
     * Positive means allocation, Negative/Zero usually means GC happened or static.
     */
    public void onTickEnd() {
        if (!EchoConfig.getInstance().isLuaProfilingEnabled())
            return;

        Runtime rt = Runtime.getRuntime();
        long currentTotal = rt.totalMemory();
        long currentFree = rt.freeMemory();

        long usedBefore = lastTotalMemory - lastFreeMemory;
        long usedNow = currentTotal - currentFree;

        long delta = usedNow - usedBefore;
        heapDeltaPerTick.set(delta);

        // Calculate GC Pause (difference in collection time)
        long totalGc = 0;
        for (java.lang.management.GarbageCollectorMXBean bean : gcBeans) {
            long time = bean.getCollectionTime();
            if (time != -1)
                totalGc += time;
        }

        long pause = totalGc - lastTotalGcTime;
        gcPausePerTick.set(pause > 0 ? pause : 0);
    }

    public long getHeapDelta() {
        return heapDeltaPerTick.get();
    }

    public long getGcPauseTime() {
        return gcPausePerTick.get();
    }

    public long getUsedMemory() {
        Runtime rt = Runtime.getRuntime();
        return rt.totalMemory() - rt.freeMemory();
    }

    public void reset() {
        heapDeltaPerTick.set(0);
        gcPausePerTick.set(0);
        lastTotalMemory = 0;
        lastFreeMemory = 0;
        lastTotalGcTime = 0;
    }

    public java.util.Map<String, Object> toMap() {
        java.util.Map<String, Object> map = new java.util.HashMap<>();
        map.put("heap_delta_bytes", getHeapDelta());
        map.put("used_memory_bytes", getUsedMemory());
        map.put("gc_pause_ms", getGcPauseTime());
        return map;
    }
}
