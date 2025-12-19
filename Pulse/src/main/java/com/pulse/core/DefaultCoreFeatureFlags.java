package com.pulse.core;

import java.util.Set;

/**
 * Default feature flags for mods-folder execution.
 * Enables stable features by default.
 * 
 * @since Pulse 0.9
 */
public enum DefaultCoreFeatureFlags implements CoreFeatureFlags {
    INSTANCE;

    private static final Set<String> ENABLED_BY_DEFAULT = Set.of(
            FEATURE_TICK_PHASE_HOOKS,
            FEATURE_LUA_PROFILING,
            FEATURE_CRASH_REPORTS);

    @Override
    public boolean isEnabled(String feature) {
        // Check system property override first: pulse.feature.<name>=true/false
        String override = System.getProperty("pulse.feature." + feature);
        if (override != null) {
            return Boolean.parseBoolean(override);
        }
        return ENABLED_BY_DEFAULT.contains(feature);
    }
}
