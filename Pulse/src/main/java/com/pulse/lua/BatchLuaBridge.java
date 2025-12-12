package com.pulse.lua;

import com.pulse.api.log.PulseLogger;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;

/**
 * Batched Lua Bridge.
 * Queues Lua calls and executes them in a single batch to reduce JNI/Reflection
 * overhead overhead frequency.
 * 
 * Note: Since PZ Lua engine (Kahlua) is fundamentally single-threaded,
 * this batching mainly helps with logical grouping and potential future
 * optimization
 * where we might construct a single Lua chunk to execute multiple calls.
 * 
 * @since 1.1.0
 */
public class BatchLuaBridge implements IBatchExecutor {

    private static final String LOG = PulseLogger.PULSE;
    private final int batchSize;
    private final ConcurrentLinkedQueue<LuaCall> pendingCalls = new ConcurrentLinkedQueue<>();

    private static class LuaCall {
        final String function;
        final Object[] args;

        LuaCall(String function, Object[] args) {
            this.function = function;
            this.args = args;
        }
    }

    /**
     * Creates a new BatchLuaBridge with default batch size of 100.
     */
    public BatchLuaBridge() {
        this(100);
    }

    /**
     * Creates a new BatchLuaBridge.
     * 
     * @param batchSize Number of calls to buffer before auto-flushing.
     */
    public BatchLuaBridge(int batchSize) {
        this.batchSize = batchSize;
    }

    /**
     * Queues a Lua function call.
     * Automatically flushes if batch size is reached.
     * 
     * @param function Function path (e.g. "print")
     * @param args     Arguments
     */
    public void queueCall(String function, Object... args) {
        pendingCalls.offer(new LuaCall(function, args));
        if (pendingCalls.size() >= batchSize) {
            flush();
        }
    }

    /**
     * Flushes all pending calls to the Lua engine.
     * This executes them one by one using the underlying LuaBridge.
     */
    public synchronized void flush() {
        if (pendingCalls.isEmpty()) {
            return;
        }

        if (!LuaBridge.isAvailable()) {
            // Cannot execute yet, keep in queue or clear?
            // For now, we wait until available, but warn if queue gets too large
            if (pendingCalls.size() > 1000) {
                PulseLogger.warn(LOG, "[BatchLua] Queue too large (1000+), clearing to prevent OOM. Lua not ready?");
                pendingCalls.clear();
            }
            return;
        }

        List<LuaCall> batch = new ArrayList<>();
        LuaCall call;
        while ((call = pendingCalls.poll()) != null) {
            batch.add(call);
        }

        // Execute batch
        // In the future, this could generate a single Lua script string:
        // "func1(args); func2(args); ..." for true batching.
        // For now, we iterate.
        int successCount = 0;
        for (LuaCall c : batch) {
            try {
                LuaBridge.call(c.function, c.args);
                successCount++;
            } catch (Exception e) {
                PulseLogger.error(LOG, "[BatchLua] Error executing batched call {}: {}", c.function, e.getMessage());
            }
        }

        PulseLogger.trace(LOG, "[BatchLua] Flushed {} calls", successCount);
    }

    /**
     * Current queue size.
     */
    public int getQueueSize() {
        return pendingCalls.size();
    }
}
