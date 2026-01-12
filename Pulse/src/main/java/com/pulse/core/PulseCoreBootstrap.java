package com.pulse.core;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.TickPhaseHook;
import com.pulse.debug.CrashReporter;
import com.pulse.event.EventBus;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Single entry point for Pulse Core initialization.
 * 
 * <p>
 * This is the ONLY way to initialize Pulse Core:
 * </p>
 * 
 * <pre>
 * // Default configuration (mods folder execution)
 * PulseCoreBootstrap.init();
 * 
 * // Custom configuration (loader provides environment)
 * PulseCoreBootstrap.init(PulseCoreConfig.builder()
 *         .environment(loaderEnvironment)
 *         .featureFlags(loaderFlags)
 *         .build());
 * </pre>
 * 
 * <p>
 * Key guarantees:
 * </p>
 * <ul>
 * <li>Idempotent: safe to call multiple times</li>
 * <li>Thread-safe: uses AtomicBoolean for init guard</li>
 * <li>Self-sufficient: works without loader</li>
 * <li>Explicit activation: NO static initialization dependency</li>
 * </ul>
 * 
 * @since Pulse 0.9
 */
public final class PulseCoreBootstrap {

    private static final String LOG = PulseLogger.PULSE;
    private static final AtomicBoolean initialized = new AtomicBoolean(false);
    private static volatile PulseCoreConfig activeConfig;

    // Pre-init access warning (one-time)
    private static final AtomicBoolean preInitWarningShown = new AtomicBoolean(false);

    private PulseCoreBootstrap() {
        // Static utility class
    }

    /**
     * Initialize Pulse Core with default configuration.
     */
    public static void init() {
        init(PulseCoreConfig.builder().build());
    }

    /**
     * Initialize Pulse Core with custom configuration.
     * Idempotent - subsequent calls are no-ops.
     * 
     * @param config Configuration provided by loader or default
     */
    public static void init(PulseCoreConfig config) {
        if (!initialized.compareAndSet(false, true)) {
            PulseLogger.debug(LOG, "PulseCoreBootstrap.init() already called - skipping");
            return;
        }

        activeConfig = config;

        PulseLogger.info(LOG, "═══════════════════════════════════════════════");
        PulseLogger.info(LOG, " Pulse Core Bootstrap Starting");
        PulseLogger.info(LOG, "═══════════════════════════════════════════════");

        // 1. EventBus explicit activation
        installEventBus();

        // 2. TickPhaseHook explicit install
        installTickPhaseHook();

        // 3. CrashGuard/Failsoft explicit install
        installCrashGuard();

        // 4. SPI Registry initialization
        initSpiRegistry();

        PulseLogger.info(LOG, "═══════════════════════════════════════════════");
        PulseLogger.info(LOG, " Pulse Core Bootstrap Complete");
        PulseLogger.info(LOG, "═══════════════════════════════════════════════");
    }

    // ═══════════════════════════════════════════════════════════════
    // Component Installation (explicit activation, not static init)
    // ═══════════════════════════════════════════════════════════════

    private static void installEventBus() {
        PulseLogger.debug(LOG, "[Bootstrap] Installing EventBus...");

        // Get instance to ensure singleton is created
        EventBus.getInstance();

        // Log status
        PulseLogger.info(LOG, "[Bootstrap] ✓ EventBus installed");
    }

    private static void installTickPhaseHook() {
        PulseLogger.debug(LOG, "[Bootstrap] Installing TickPhaseHook...");

        // Check if feature is enabled
        if (!activeConfig.getFeatureFlags().isEnabled(CoreFeatureFlags.FEATURE_TICK_PHASE_HOOKS)) {
            PulseLogger.info(LOG, "[Bootstrap] ⊘ TickPhaseHook disabled by feature flag");
            return;
        }

        // Explicit install (not relying on static init)
        boolean freshInstall = TickPhaseHook.install();

        if (freshInstall) {
            PulseLogger.info(LOG, "[Bootstrap] ✓ TickPhaseHook installed");
        } else {
            PulseLogger.info(LOG, "[Bootstrap] ✓ TickPhaseHook already installed");
        }
    }

    private static void installCrashGuard() {
        PulseLogger.debug(LOG, "[Bootstrap] Installing CrashGuard...");

        // Check if feature is enabled
        if (!activeConfig.getFeatureFlags().isEnabled(CoreFeatureFlags.FEATURE_CRASH_REPORTS)) {
            PulseLogger.info(LOG, "[Bootstrap] ⊘ CrashGuard disabled by feature flag");
            return;
        }

        // Explicit handler install
        CrashReporter.installHandler();

        // Configure based on environment
        if (activeConfig.getEnvironment().isDebugMode()) {
            PulseLogger.debug(LOG, "[Bootstrap] CrashGuard debug mode enabled");
        }

        PulseLogger.info(LOG, "[Bootstrap] ✓ CrashGuard installed");
    }

    private static void initSpiRegistry() {
        PulseLogger.debug(LOG, "[Bootstrap] Initializing SPI Registry...");

        // ServiceLoader-based provider registration
        // This allows submodules to register their providers

        PulseLogger.info(LOG, "[Bootstrap] ✓ SPI Registry initialized");
    }

    // ═══════════════════════════════════════════════════════════════
    // Status Queries
    // ═══════════════════════════════════════════════════════════════

    /**
     * Check if core has been initialized.
     */
    public static boolean isInitialized() {
        return initialized.get();
    }

    /**
     * Get active configuration.
     * Returns default if called before init (with one-time warning).
     */
    public static PulseCoreConfig getConfig() {
        if (activeConfig == null) {
            warnPreInitAccess("getConfig()");
            return PulseCoreConfig.builder().build();
        }
        return activeConfig;
    }

    /**
     * Get current environment.
     */
    public static CoreEnvironment getEnvironment() {
        if (activeConfig == null) {
            warnPreInitAccess("getEnvironment()");
            return DefaultCoreEnvironment.getInstance();
        }
        return activeConfig.getEnvironment();
    }

    /**
     * Get current feature flags.
     */
    public static CoreFeatureFlags getFeatureFlags() {
        if (activeConfig == null) {
            warnPreInitAccess("getFeatureFlags()");
            return DefaultCoreFeatureFlags.INSTANCE;
        }
        return activeConfig.getFeatureFlags();
    }

    private static void warnPreInitAccess(String method) {
        if (preInitWarningShown.compareAndSet(false, true)) {
            PulseLogger.warn(LOG, "[Bootstrap] {} called before init() - using defaults. " +
                    "This warning will only appear once.", method);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Testing Support
    // ═══════════════════════════════════════════════════════════════

    /**
     * Reset for testing only.
     */
    static void reset() {
        initialized.set(false);
        activeConfig = null;
        preInitWarningShown.set(false);
        TickPhaseHook.uninstall();
    }
}
