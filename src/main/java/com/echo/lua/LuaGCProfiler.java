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

    private final AtomicLong heapDeltaPerTick = new AtomicLong(0);

    private LuaGCProfiler() {
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
    }

    public long getHeapDelta() {
        return heapDeltaPerTick.get();
    }

    public long getUsedMemory() {
        Runtime rt = Runtime.getRuntime();
        return rt.totalMemory() - rt.freeMemory();
    }

    public void reset() {
        heapDeltaPerTick.set(0);
        lastTotalMemory = 0;
        lastFreeMemory = 0;
    }

    public java.util.Map<String, Object> toMap() {
        java.util.Map<String, Object> map = new java.util.HashMap<>();
        map.put("heap_delta_bytes", getHeapDelta());
        map.put("used_memory_bytes", getUsedMemory());
        return map;
    }
}
