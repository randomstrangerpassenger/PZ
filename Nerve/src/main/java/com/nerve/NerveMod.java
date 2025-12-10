package com.nerve;

/**
 * Nerve - Network Enhancement for Project Zomboid
 * 
 * Main mod entry point that integrates with Pulse mod loader.
 */
public class NerveMod {
    
    public static final String MOD_ID = "Nerve";
    public static final String VERSION = "0.1.0";
    
    private static NerveMod instance;
    
    public static NerveMod getInstance() {
        return instance;
    }
    
    public void init() {
        instance = this;
        System.out.println("[Nerve] Initializing Nerve v" + VERSION);
        // TODO: Initialize network optimization systems
    }
    
    public void shutdown() {
        System.out.println("[Nerve] Shutting down...");
        // TODO: Cleanup resources
    }
}
