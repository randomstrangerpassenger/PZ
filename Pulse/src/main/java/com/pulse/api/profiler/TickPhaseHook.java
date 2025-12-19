package com.pulse.api.profiler;

import com.pulse.api.Pulse;

/**
 * Tick Phase Hooks for Echo.
 * 
 * Allows Echo to receive phase-level timing events from Pulse mixins.
 * 
 * @since Pulse 1.1
 * @since Pulse 0.9 - Added phase validation and predefined phases
 */
public class TickPhaseHook {

    // ═══════════════════════════════════════════════════════════════
    // Predefined Phase Constants (for Fuse/Nerve integration)
    // ═══════════════════════════════════════════════════════════════

    public static final String PHASE_WORLD_UPDATE = "world_update";
    public static final String PHASE_PLAYER_UPDATE = "player_update";
    public static final String PHASE_ZOMBIE_UPDATE = "zombie_update";
    public static final String PHASE_GRID_UPDATE = "grid_update";
    public static final String PHASE_CHUNK_UPDATE = "chunk_update";
    public static final String PHASE_PATHFINDING = "pathfinding";
    public static final String PHASE_LOS_CHECK = "los_check";
    public static final String PHASE_RENDER = "render";

    // v0.9: Additional phases for Echo TickPhaseProfiler mapping
    public static final String PHASE_AI_UPDATE = "ai_update";
    public static final String PHASE_PHYSICS_UPDATE = "physics_update";
    public static final String PHASE_RENDER_PREP = "render_prep";
    public static final String PHASE_ISOGRID_UPDATE = "isogrid_update";

    // ═══════════════════════════════════════════════════════════════
    // Phase Tracking for Validation
    // ═══════════════════════════════════════════════════════════════

    private static String currentPhase = null;
    private static long currentPhaseStart = -1;

    // Rate-limit for warnings (max 5 warnings per session)
    private static int autoCloseWarningCount = 0;
    private static final int MAX_AUTO_CLOSE_WARNINGS = 5;

    public interface ITickPhaseCallback {
        long startPhase(String phase);

        void endPhase(String phase, long startTime);

        void onTickComplete();
    }

    private static volatile ITickPhaseCallback callback;
    private static volatile boolean installed = false;

    // ═══════════════════════════════════════════════════════════════
    // Bootstrap Activation (explicit install)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Install TickPhaseHook (called by PulseCoreBootstrap).
     * 
     * <p>
     * This provides explicit activation instead of relying on static
     * initialization.
     * Safe to call multiple times (idempotent).
     * </p>
     * 
     * @return true if successfully installed, false if already installed
     */
    public static boolean install() {
        if (installed) {
            return false;
        }

        // Reset state for clean start
        resetWarnings();
        currentPhase = null;
        currentPhaseStart = -1;

        installed = true;
        Pulse.log("pulse", "[TickPhaseHook] Installed and ready");
        return true;
    }

    /**
     * Check if TickPhaseHook has been installed by Bootstrap.
     */
    public static boolean isInstalled() {
        return installed;
    }

    /**
     * Uninstall TickPhaseHook (for testing/cleanup).
     */
    public static void uninstall() {
        clearCallback();
        resetWarnings();
        installed = false;
    }

    public static void setCallback(ITickPhaseCallback cb) {
        callback = cb;
    }

    public static void clearCallback() {
        callback = null;
    }

    // Use AtomicInteger for thread safety if needed, though usually on main thread
    private static int phaseErrorCount = 0;

    /**
     * Start a phase. Auto-closes any unclosed previous phase.
     * 
     * @param phase Phase name (use PHASE_* constants when possible)
     * @return Start time in nanoseconds
     */
    public static long startPhase(String phase) {
        // Auto-close unclosed phase (with rate-limited warning)
        if (currentPhase != null) {
            phaseErrorCount++; // Increment error count
            if (autoCloseWarningCount < MAX_AUTO_CLOSE_WARNINGS) {
                autoCloseWarningCount++;
                Pulse.warn("pulse", "[TickPhaseHook] Auto-closing unclosed phase: " + currentPhase
                        + " (warning " + autoCloseWarningCount + "/" + MAX_AUTO_CLOSE_WARNINGS + ")");
            }
            endPhase(currentPhase, currentPhaseStart);
        }

        currentPhase = phase;
        currentPhaseStart = System.nanoTime();

        if (callback != null) {
            return callback.startPhase(phase);
        }
        return currentPhaseStart;
    }

    /**
     * End a phase. Validates phase matches current phase.
     * 
     * @param phase     Phase name
     * @param startTime Start time from startPhase()
     */
    public static void endPhase(String phase, long startTime) {
        // Validate phase matches
        if (currentPhase != null && !currentPhase.equals(phase)) {
            phaseErrorCount++; // Increment error count
            Pulse.warn("pulse", "[TickPhaseHook] Phase mismatch: ending '" + phase
                    + "' but current is '" + currentPhase + "'");
        }

        currentPhase = null;
        currentPhaseStart = -1;

        if (callback != null) {
            callback.endPhase(phase, startTime);
        }
    }

    /**
     * Called when a complete tick finishes.
     */
    public static void onTickComplete() {
        // Auto-close any unclosed phase at tick end
        if (currentPhase != null) {
            phaseErrorCount++; // Increment error count
            if (autoCloseWarningCount < MAX_AUTO_CLOSE_WARNINGS) {
                autoCloseWarningCount++;
                Pulse.warn("pulse", "[TickPhaseHook] Phase '" + currentPhase
                        + "' not closed before tick complete");
            }
            endPhase(currentPhase, currentPhaseStart);
        }

        if (callback != null) {
            callback.onTickComplete();
        }
    }

    /**
     * Get current active phase (for debugging)
     */
    public static String getCurrentPhase() {
        return currentPhase;
    }

    /**
     * Get total phase errors (mismatches + unclosed phases)
     */
    public static int getPhaseErrorCount() {
        return phaseErrorCount;
    }

    /**
     * Reset warning counter (for testing)
     */
    public static void resetWarnings() {
        autoCloseWarningCount = 0;
        phaseErrorCount = 0;
    }
}
