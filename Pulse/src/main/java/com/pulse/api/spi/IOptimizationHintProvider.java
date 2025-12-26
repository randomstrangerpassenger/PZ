package com.pulse.api.spi;

import java.util.List;
import java.util.Optional;

/**
 * SPI interface for optimization hint providers.
 * 
 * Allows analysis modules to provide optimization suggestions
 * to optimization modules without direct coupling.
 * 
 * Label format: area/subsystem/detail (e.g., cpu/zombie/ai, io/network/sync)
 * 
 * @since Pulse 1.1.0
 */
public interface IOptimizationHintProvider extends IProvider {

    /**
     * Optimization category constants.
     */
    String CATEGORY_CPU = "CPU";
    String CATEGORY_MEMORY = "MEMORY";
    String CATEGORY_IO = "IO";
    String CATEGORY_RENDER = "RENDER";
    String CATEGORY_NETWORK = "NETWORK";

    /**
     * Suggest an optimization target for the given category.
     *
     * @param category Category constant (CATEGORY_CPU, CATEGORY_IO, etc.)
     * @return Optimization hint, or empty if no suggestion
     */
    Optional<OptimizationHint> suggestTarget(String category);

    /**
     * Get top N optimization hints across all categories.
     *
     * @param n Number of hints to return
     * @return List of optimization hints, sorted by priority
     */
    List<OptimizationHint> getTopHints(int n);

    /**
     * Check if the system is currently under performance pressure.
     *
     * @return true if performance is degraded
     */
    boolean isUnderPressure();
}
