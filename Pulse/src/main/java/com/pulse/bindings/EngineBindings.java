package com.pulse.bindings;

/**
 * Unified interface for engine bindings.
 * 
 * <p>
 * Abstracts B41/B42 differences behind a stable interface.
 * This is the primary access point for all engine interactions.
 * </p>
 * 
 * <p>
 * Usage:
 * </p>
 * 
 * <pre>
 * EngineBindings bindings = EngineBindingsResolver.get();
 * bindings.lua().registerCallback(...);
 * bindings.zombie().getZombieState(...);
 * </pre>
 * 
 * @since Pulse 0.9
 */
public interface EngineBindings {

    /**
     * Get Lua adapter for the current game version.
     */
    ILuaBindings lua();

    /**
     * Get Zombie/Entity adapter for the current game version.
     */
    IZombieBindings zombie();

    /**
     * Get detected game build version.
     */
    int getGameBuild();

    /**
     * Check if running on Build 41.
     */
    default boolean isBuild41() {
        return getGameBuild() < 42;
    }

    /**
     * Check if running on Build 42 or later.
     */
    default boolean isBuild42OrLater() {
        return getGameBuild() >= 42;
    }

    /**
     * Get human-readable version string.
     */
    default String getVersionString() {
        return "Build " + getGameBuild();
    }
}
