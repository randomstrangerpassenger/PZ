package com.pulse.api;

/**
 * Pulse Stable API v1 Reference
 * 
 * This class documents the stable public API that Echo, Fuse, and Nerve
 * can safely depend on. These APIs are guaranteed to maintain backward
 * compatibility within major versions.
 * 
 * <h2>Stable APIs (v1.0)</h2>
 * 
 * <h3>1. EventBus</h3>
 * <ul>
 * <li>{@link com.pulse.event.EventBus#post(Object)} - Post an event to all
 * subscribers</li>
 * <li>{@link com.pulse.event.EventBus#subscribe(Class, java.util.function.Consumer, String)}
 * - Subscribe to events</li>
 * <li>{@link com.pulse.event.EventBus#unsubscribe(Class, String)} - Unsubscribe
 * from events</li>
 * </ul>
 * 
 * <h3>2. TickPhaseHook</h3>
 * <ul>
 * <li>{@link com.pulse.api.profiler.TickPhaseHook#startPhase(String)} - Start
 * timing a phase</li>
 * <li>{@link com.pulse.api.profiler.TickPhaseHook#endPhase(String, long)} - End
 * timing a phase</li>
 * <li>{@link com.pulse.api.profiler.TickPhaseHook#onTickComplete()} - Called
 * when tick finishes</li>
 * <li>Phase constants: PHASE_WORLD_UPDATE, PHASE_AI_UPDATE, etc.</li>
 * </ul>
 * 
 * <h3>3. PulseHookRegistry</h3>
 * <ul>
 * <li>{@link com.pulse.hook.PulseHookRegistry#register} - Register a hook
 * callback</li>
 * <li>{@link com.pulse.hook.PulseHookRegistry#unregister} - Unregister a
 * callback</li>
 * <li>{@link com.pulse.hook.PulseHookRegistry#broadcast} - Broadcast to all
 * callbacks</li>
 * <li>Priority constants: PRIORITY_LOWEST to PRIORITY_HIGHEST</li>
 * </ul>
 * 
 * <h3>4. LuaBudgetManager</h3>
 * <ul>
 * <li>{@link com.pulse.runtime.LuaBudgetManager#checkBudget} - Check if Lua
 * execution is within budget</li>
 * <li>{@link com.pulse.runtime.LuaBudgetManager#recordUsage} - Record Lua
 * execution time</li>
 * </ul>
 * 
 * <h3>5. FailsoftPolicy</h3>
 * <ul>
 * <li>{@link com.pulse.api.FailsoftPolicy#handle} - Handle an error with
 * fail-soft action</li>
 * <li>{@link com.pulse.api.FailsoftPolicy#handlePhaseSequenceError} - Handle
 * phase sequence violations</li>
 * <li>{@link com.pulse.api.FailsoftPolicy#handleUnsafeWorldstateAccess} -
 * Handle unsafe world access</li>
 * </ul>
 * 
 * <h3>6. Logging</h3>
 * <ul>
 * <li>{@link Pulse#info(String, String)} - Log info message</li>
 * <li>{@link Pulse#warn(String, String)} - Log warning message</li>
 * <li>{@link Pulse#error(String, String)} - Log error message</li>
 * </ul>
 * 
 * <h3>7. Utilities (v0.9+)</h3>
 * <ul>
 * <li>{@link com.pulse.api.util.PulseExceptionFormatter#format} - Format
 * exceptions for mods</li>
 * <li>{@link com.pulse.api.util.PulseExceptionFormatter#oneLiner} - One-line
 * exception summary</li>
 * </ul>
 * 
 * <h2>Internal APIs (Not Stable)</h2>
 * <p>
 * The following packages are internal and may change without notice:
 * </p>
 * <ul>
 * <li>com.pulse.mixin.* - Mixin implementations</li>
 * <li>com.pulse.scheduler.* - Internal scheduler</li>
 * <li>com.pulse.compat.* - Version compatibility</li>
 * </ul>
 * 
 * @since Pulse 0.9
 * @version 1.0
 */
public final class PulseStableAPI {

    /** API Version */
    public static final String API_VERSION = "1.0";

    /** Minimum compatible Pulse version */
    public static final String MIN_PULSE_VERSION = "0.9.0";

    private PulseStableAPI() {
        // Documentation class only
    }

    /**
     * Check if the current Pulse version supports the stable API.
     * 
     * @return true if stable API is available
     */
    public static boolean isAvailable() {
        try {
            // Check key classes exist
            Class.forName("com.pulse.event.EventBus");
            Class.forName("com.pulse.api.profiler.TickPhaseHook");
            Class.forName("com.pulse.hook.PulseHookRegistry");
            return true;
        } catch (ClassNotFoundException e) {
            return false;
        }
    }

    /**
     * Get stable API version.
     */
    public static String getVersion() {
        return API_VERSION;
    }
}
