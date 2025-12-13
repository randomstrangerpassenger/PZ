package com.pulse.api.spi;

/**
 * SPI interface for profiler providers.
 * 
 * Allows external modules like Echo to integrate with Pulse's profiling system.
 * 
 * @since Pulse 1.0
 */
public interface IProfilerProvider extends IProvider {

    /**
     * Called at the start of each game tick.
     */
    void onTickStart();

    /**
     * Called at the end of each game tick.
     * 
     * @param tickTimeNanos Time taken by the tick in nanoseconds
     */
    void onTickEnd(long tickTimeNanos);

    /**
     * Called at the start of each frame.
     */
    void onFrameStart();

    /**
     * Called at the end of each frame.
     * 
     * @param frameTimeNanos Time taken by the frame in nanoseconds
     */
    void onFrameEnd(long frameTimeNanos);

    /**
     * Get the current FPS.
     */
    double getCurrentFps();

    /**
     * Get the average tick time in milliseconds.
     */
    double getAverageTickTimeMs();

    /**
     * Get the average frame time in milliseconds.
     */
    double getAverageFrameTimeMs();

    /**
     * Start profiling.
     */
    void startProfiling();

    /**
     * Stop profiling.
     */
    void stopProfiling();

    /**
     * Check if profiling is active.
     */
    boolean isProfiling();

    /**
     * Reset all profiling data.
     */
    void resetData();
}
