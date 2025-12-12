package com.pulse.bootstrap;

import com.pulse.api.log.PulseLogger;
import com.pulse.mod.ModLoader;

/**
 * Step 7: Initialize mod loader (discovery & mixins).
 */
public class ModInitializer {
    private static final String LOG = PulseLogger.PULSE;
    private final ModLoader modLoader;

    public ModInitializer() {
        this(ModLoader.getInstance());
    }

    public ModInitializer(ModLoader modLoader) {
        this.modLoader = modLoader;
    }

    public void initialize(InitializationContext context) {
        PulseLogger.info(LOG, "Step 7: Initializing mod loader...");

        try {
            modLoader.discoverMods();
            modLoader.resolveDependencies();
            modLoader.registerMixins();

            PulseLogger.info(LOG, "Step 7: Complete");
        } catch (Throwable t) {
            PulseLogger.error(LOG, "Step 7: Mod loader error (non-fatal)");
            t.printStackTrace();
        }
    }
}
