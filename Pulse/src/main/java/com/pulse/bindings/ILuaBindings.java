package com.pulse.bindings;

/**
 * Lua operations binding interface.
 * 
 * <p>
 * Abstracts Lua-related operations that may differ between B41/B42.
 * </p>
 * 
 * @since Pulse 0.9
 */
public interface ILuaBindings {

    // ═══════════════════════════════════════════════════════════════
    // Class Information
    // ═══════════════════════════════════════════════════════════════

    /**
     * Get LuaEventManager class name.
     */
    String getEventManagerClassName();

    /**
     * Get LuaManager class name.
     */
    String getLuaManagerClassName();

    // ═══════════════════════════════════════════════════════════════
    // Event System
    // ═══════════════════════════════════════════════════════════════

    /**
     * Get max triggerEvent argument count.
     */
    int getMaxTriggerEventArgs();

    /**
     * Signal event start for profiling.
     */
    void onEventStart(String eventName);

    /**
     * Signal event end for profiling.
     */
    void onEventEnd();

    // ═══════════════════════════════════════════════════════════════
    // Lua State Access
    // ═══════════════════════════════════════════════════════════════

    /**
     * Check if global Lua access is available.
     */
    boolean hasGlobalLuaAccess();

    /**
     * Get a global Lua variable value.
     * 
     * @param name Variable name
     * @return Value, or null if not found
     */
    Object getGlobalLuaValue(String name);
}
