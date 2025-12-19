package com.pulse.core;

/**
 * Feature flag interface for experimental/optional features.
 * 
 * <p>
 * Allows loader to enable/disable features, while core has stable defaults.
 * </p>
 * 
 * @since Pulse 0.9
 */
public interface CoreFeatureFlags {

    /**
     * Check if a specific feature is enabled.
     * 
     * @param feature Feature name (use constants below)
     * @return true if enabled
     */
    boolean isEnabled(String feature);

    // ═══════════════════════════════════════════════════════════════
    // Standard Feature Flags
    // ═══════════════════════════════════════════════════════════════

    /** Lua call profiling (Echo integration) */
    String FEATURE_LUA_PROFILING = "lua_profiling";

    /** Tick phase timing hooks */
    String FEATURE_TICK_PHASE_HOOKS = "tick_phase_hooks";

    /** Network optimization features (Nerve) */
    String FEATURE_NETWORK_OPTIMIZATION = "network_optimization";

    /** Zombie update throttling (Fuse) */
    String FEATURE_ZOMBIE_THROTTLE = "zombie_throttle";

    /** Detailed crash reporting */
    String FEATURE_CRASH_REPORTS = "crash_reports";
}
