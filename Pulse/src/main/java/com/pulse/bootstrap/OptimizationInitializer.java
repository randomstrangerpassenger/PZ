package com.pulse.bootstrap;

import com.pulse.api.log.PulseLogger;

/**
 * Step 6.5: Initialize optimization extensions.
 */
public class OptimizationInitializer {
    private static final String LOG = PulseLogger.PULSE;

    public void initialize(InitializationContext context) {
        PulseLogger.info(LOG, "Step 6.5: Initializing optimization extensions...");
        try {
            com.pulse.api.CapabilityFlags.initialize();
            com.pulse.api.optimization.OptimizationPointRegistry.initialize();
            com.pulse.api.SafeGameAccess.setMainThread(Thread.currentThread());

            PulseLogger.info(LOG, "Step 6.5: Complete");
        } catch (Throwable t) {
            PulseLogger.error(LOG, "Step 6.5: Optimization extensions init error (non-fatal)");
            t.printStackTrace();
        }
    }
}
