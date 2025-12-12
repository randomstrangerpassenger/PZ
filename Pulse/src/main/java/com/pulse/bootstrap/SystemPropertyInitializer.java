package com.pulse.bootstrap;

import com.pulse.api.log.PulseLogger;

/**
 * Step 1: Initialize system properties.
 */
public class SystemPropertyInitializer {
    private static final String LOG = PulseLogger.PULSE;

    public void initialize(InitializationContext context) {
        PulseLogger.info(LOG, "Step 1: Configuring system properties...");

        // Enable Mixin debugging
        System.setProperty("mixin.debug", "true");
        System.setProperty("mixin.debug.verbose", "true");
        System.setProperty("mixin.debug.export", "true");
        System.setProperty("mixin.debug.export.decompile", "false");
        System.setProperty("mixin.dumpTargetOnFailure", "true");
        System.setProperty("mixin.checks", "true");
        System.setProperty("mixin.hotSwap", "true");

        PulseLogger.info(LOG, "Step 1: Complete");
    }
}
