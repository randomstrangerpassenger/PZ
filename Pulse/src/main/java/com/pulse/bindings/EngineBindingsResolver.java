package com.pulse.bindings;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.version.GameVersion;

/**
 * Resolver for engine bindings.
 * 
 * <p>
 * Default implementation uses GameVersion.get().
 * Loader can replace this via setFactory() for testing or custom resolution.
 * </p>
 * 
 * <p>
 * Usage:
 * </p>
 * 
 * <pre>
 * EngineBindings bindings = EngineBindingsResolver.get();
 * </pre>
 * 
 * @since Pulse 0.9
 */
public final class EngineBindingsResolver {

    private static final String LOG = PulseLogger.PULSE;

    private static volatile EngineBindings instance;
    private static volatile EngineBindingsFactory factory = DefaultBindingsFactory.INSTANCE;

    private EngineBindingsResolver() {
        // Static utility class
    }

    /**
     * Get engine bindings for current game version.
     */
    public static EngineBindings get() {
        if (instance == null) {
            synchronized (EngineBindingsResolver.class) {
                if (instance == null) {
                    instance = factory.create();
                    PulseLogger.debug(LOG, "[Bindings] Created: {}", instance.getVersionString());
                }
            }
        }
        return instance;
    }

    /**
     * Set custom factory (for loader or testing).
     * Must be called before first get() call.
     * 
     * @param customFactory Custom factory implementation
     */
    public static void setFactory(EngineBindingsFactory customFactory) {
        if (customFactory != null) {
            factory = customFactory;
            instance = null; // Reset to use new factory
            PulseLogger.debug(LOG, "[Bindings] Custom factory set: {}", customFactory.getClass().getSimpleName());
        }
    }

    /**
     * Factory interface for creating bindings.
     */
    public interface EngineBindingsFactory {
        EngineBindings create();
    }

    /**
     * Default factory using GameVersion detection.
     */
    private enum DefaultBindingsFactory implements EngineBindingsFactory {
        INSTANCE;

        @Override
        public EngineBindings create() {
            int build = GameVersion.get();

            if (build >= GameVersion.BUILD_42) {
                return new Build42EngineBindings(build);
            }
            return new Build41EngineBindings(build);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Testing Support
    // ═══════════════════════════════════════════════════════════════

    /**
     * Reset for testing.
     */
    static void reset() {
        instance = null;
        factory = DefaultBindingsFactory.INSTANCE;
    }
}
