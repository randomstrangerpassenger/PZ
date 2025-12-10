package com.example.testmod;

import com.pulse.api.Pulse;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameInitEvent;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.mod.PulseMod;

/**
 * Test Mod - Main mod class
 */
public class TestmodMod implements PulseMod {

    private static final String MOD_ID = "testmod";

    @Override
    public void onInitialize() {
        Pulse.log(MOD_ID, "Test Mod initializing...");
        
        // Register event listeners
        EventBus.subscribe(GameInitEvent.class, this::onGameInit, MOD_ID);
        EventBus.subscribe(GameTickEvent.class, this::onGameTick, MOD_ID);
        
        Pulse.log(MOD_ID, "Test Mod initialized!");
    }
    
    private void onGameInit(GameInitEvent event) {
        Pulse.log(MOD_ID, "Game initialization complete!");
    }
    
    private void onGameTick(GameTickEvent event) {
        // Called every game tick
        // Add your tick logic here
    }

    @Override
    public void onUnload() {
        Pulse.log(MOD_ID, "Test Mod unloading...");
    }
}
