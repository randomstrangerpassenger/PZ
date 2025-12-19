package com.pulse.core;

import java.nio.file.Path;

/**
 * Environment abstraction for Pulse Core.
 * 
 * <p>
 * Allows loader to provide custom paths/sinks, while core remains
 * self-sufficient.
 * </p>
 * 
 * <p>
 * Default implementation: {@link DefaultCoreEnvironment}
 * </p>
 * 
 * @since Pulse 0.9
 */
public interface CoreEnvironment {

    /**
     * Get the base path for Pulse data storage.
     * This is NOT necessarily the game installation path.
     */
    Path getBasePath();

    /**
     * Get the configuration directory.
     */
    Path getConfigPath();

    /**
     * Get the log output directory.
     */
    Path getLogPath();

    /**
     * Check if running in server mode.
     */
    boolean isServer();

    /**
     * Check if debug mode is enabled.
     */
    boolean isDebugMode();

    /**
     * Get detected game path (best effort, may be null).
     * For actual game path detection, use bindings layer.
     */
    Path getGamePath();
}
