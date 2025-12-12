package com.pulse.lua;

/**
 * Interface for batch execution of Lua calls.
 * Allows switching between different batching strategies (e.g. Iterative vs
 * Script Generation).
 */
public interface IBatchExecutor {

    /**
     * Queues a Lua function call.
     * 
     * @param function Function path (e.g. "print")
     * @param args     Arguments
     */
    void queueCall(String function, Object... args);

    /**
     * Flushes all pending calls to the Lua engine.
     */
    void flush();

    /**
     * Gets the current number of pending calls.
     */
    int getQueueSize();
}
