package com.pulse.api.profiler;

import com.pulse.api.Pulse;
import com.pulse.diagnostics.PulseThreadGuard;

import java.util.ArrayDeque;
import java.util.Deque;

/**
 * Tick Phase Hooks for Profiler.
 * 
 * Allows profilers to receive phase-level timing events from Pulse mixins.
 * 
 * <h2>v5.1 Update: ThreadLocal Stack for Nested Phases</h2>
 * <p>
 * Supports nested phases (e.g., WORLD_UPDATE containing AI_UPDATE).
 * Uses ThreadLocal stack for thread safety and proper LIFO ordering.
 * </p>
 * 
 * <h2>Iron Rules</h2>
 * <ol>
 * <li>ThreadLocal Stack - thread-independent stacks</li>
 * <li>Main Thread Guard - non-main thread calls are no-ops</li>
 * <li>Single Source of Truth - stack's internal time is authoritative</li>
 * <li>Fail-soft Recovery - mismatch clears stack, next tick is clean</li>
 * </ol>
 * 
 * @since Pulse 1.1
 * @since Pulse 0.9 - Added phase validation and predefined phases
 * @since Pulse 1.3 - ThreadLocal Stack for nested phases
 */
public class TickPhaseHook {

    // ═══════════════════════════════════════════════════════════════
    // Predefined Phase Constants (for submodule integration)
    // ═══════════════════════════════════════════════════════════════

    public static final String PHASE_WORLD_UPDATE = "world_update";
    public static final String PHASE_PLAYER_UPDATE = "player_update";
    public static final String PHASE_ZOMBIE_UPDATE = "zombie_update";
    public static final String PHASE_GRID_UPDATE = "grid_update";
    public static final String PHASE_CHUNK_UPDATE = "chunk_update";
    public static final String PHASE_PATHFINDING = "pathfinding";
    public static final String PHASE_LOS_CHECK = "los_check";
    public static final String PHASE_RENDER = "render";

    // v0.9: Additional phases for TickPhaseProfiler mapping
    public static final String PHASE_AI_UPDATE = "ai_update";
    public static final String PHASE_PHYSICS_UPDATE = "physics_update";
    public static final String PHASE_RENDER_PREP = "render_prep";
    public static final String PHASE_ISOGRID_UPDATE = "isogrid_update";

    // ═══════════════════════════════════════════════════════════════
    // v5.1: ThreadLocal Stack for Nested Phase Support
    // ═══════════════════════════════════════════════════════════════

    /**
     * Phase state for stack entries.
     */
    private static class PhaseState {
        final String phase;
        final long startTime;

        PhaseState(String phase, long startTime) {
            this.phase = phase;
            this.startTime = startTime;
        }
    }

    /**
     * [Rule 1] ThreadLocal Stack - each thread gets its own stack.
     */
    private static final ThreadLocal<Deque<PhaseState>> phaseStack = ThreadLocal.withInitial(ArrayDeque::new);

    // Rate-limit for warnings (max 5 warnings per session)
    private static int errorWarningCount = 0;
    private static final int MAX_ERROR_WARNINGS = 5;
    private static int phaseErrorCount = 0;

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
     */
    public static boolean install() {
        if (installed) {
            return false;
        }

        resetWarnings();
        phaseStack.get().clear();

        installed = true;
        Pulse.log("pulse", "[TickPhaseHook] Installed with ThreadLocal Stack support");
        return true;
    }

    public static boolean isInstalled() {
        return installed;
    }

    public static void uninstall() {
        clearCallback();
        resetWarnings();
        phaseStack.get().clear();
        installed = false;
    }

    public static void setCallback(ITickPhaseCallback cb) {
        callback = cb;
    }

    public static void clearCallback() {
        callback = null;
    }

    // ═══════════════════════════════════════════════════════════════
    // Phase API (v5.1: Stack-based)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Start a phase. Supports nested phases via stack.
     * 
     * @param phase Phase name (use PHASE_* constants when possible)
     * @return Start time in nanoseconds, or -1 if not on main thread
     */
    public static long startPhase(String phase) {
        // [Rule 2] Main Thread Guard
        if (!PulseThreadGuard.isMainThread()) {
            return -1;
        }

        long now = System.nanoTime();
        Deque<PhaseState> stack = phaseStack.get();
        stack.push(new PhaseState(phase, now));

        ITickPhaseCallback cb = callback;
        if (cb != null) {
            return cb.startPhase(phase);
        }
        return now;
    }

    /**
     * End a phase. Validates LIFO ordering.
     * 
     * @param phase            Phase name
     * @param ignoredStartTime Ignored - stack's internal time is used [Rule 3]
     */
    public static void endPhase(String phase, long ignoredStartTime) {
        // [Rule 2] Main Thread Guard
        if (!PulseThreadGuard.isMainThread()) {
            return;
        }

        Deque<PhaseState> stack = phaseStack.get();
        ITickPhaseCallback cb = callback;

        if (stack.isEmpty()) {
            reportError("Stack underflow: endPhase('" + phase + "') called but stack is empty");
            // v5.2: Still notify callback with -1 startTime so profiler can skip
            // measurement
            // but maintain heartbeat balance
            if (cb != null) {
                cb.endPhase(phase, -1);
            }
            return;
        }

        PhaseState top = stack.peek();
        if (!top.phase.equals(phase)) {
            // [Rule 4] Mismatch → clear stack for fail-soft recovery
            reportError("Phase mismatch: endPhase('" + phase + "') but top is '" + top.phase + "'");
            stack.clear();
            // v5.2: Notify callback with -1 to maintain heartbeat balance
            if (cb != null) {
                cb.endPhase(phase, -1);
            }
            return;
        }

        stack.pop();

        if (cb != null) {
            // [Rule 3] Use stack's internal startTime, not the ignored parameter
            cb.endPhase(phase, top.startTime);
        }
    }

    /**
     * Called when a complete tick finishes.
     * Clears any unclosed phases (fail-soft).
     */
    public static void onTickComplete() {
        // [Rule 2] Main Thread Guard
        if (!PulseThreadGuard.isMainThread()) {
            return;
        }

        Deque<PhaseState> stack = phaseStack.get();

        if (!stack.isEmpty()) {
            // [Rule 4] Clear unclosed phases
            StringBuilder unclosed = new StringBuilder();
            while (!stack.isEmpty()) {
                PhaseState state = stack.pop();
                if (unclosed.length() > 0)
                    unclosed.append(", ");
                unclosed.append(state.phase);
            }
            reportError("Tick ended with " + stack.size() + " unclosed phases: " + unclosed);
        }

        ITickPhaseCallback cb = callback;
        if (cb != null) {
            cb.onTickComplete();
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Diagnostics & Testing
    // ═══════════════════════════════════════════════════════════════

    /**
     * Get current active phase (top of stack, for debugging)
     */
    public static String getCurrentPhase() {
        Deque<PhaseState> stack = phaseStack.get();
        if (stack.isEmpty()) {
            return null;
        }
        return stack.peek().phase;
    }

    /**
     * Get current stack depth (for debugging)
     */
    public static int getStackDepth() {
        return phaseStack.get().size();
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
        errorWarningCount = 0;
        phaseErrorCount = 0;
    }

    /**
     * Report error with rate limiting.
     */
    private static void reportError(String message) {
        phaseErrorCount++;

        if (errorWarningCount < MAX_ERROR_WARNINGS) {
            errorWarningCount++;
            Pulse.warn("pulse", "[TickPhaseHook] " + message
                    + " (warning " + errorWarningCount + "/" + MAX_ERROR_WARNINGS + ")");
        }
    }
}
