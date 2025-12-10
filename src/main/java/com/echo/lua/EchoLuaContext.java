package com.echo.lua;

/**
 * Manages the current UI/Logic context for Lua profiling.
 * 
 * Used to group Lua function calls by high-level context (e.g., "Inventory",
 * "HealthPanel", "Combat")
 * without the overhead of deep stack inspection.
 */
public class EchoLuaContext {

    private static final ThreadLocal<String> currentContext = ThreadLocal.withInitial(() -> "Unknown");

    /**
     * Set the current context.
     * 
     * @param context Context name (e.g., "Inventory", "HUD")
     */
    public static void setContext(String context) {
        currentContext.set(context != null ? context : "Unknown");
    }

    /**
     * Get the current context.
     * 
     * @return Current context name
     */
    public static String getContext() {
        return currentContext.get();
    }

    /**
     * Clear context (reset to Unknown or Default).
     */
    public static void clearContext() {
        currentContext.set("Unknown");
    }
}
