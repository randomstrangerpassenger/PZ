package com.pulse.bootstrap;

import com.pulse.api.log.PulseLogger;
import org.spongepowered.asm.launch.MixinBootstrap;
import org.spongepowered.asm.mixin.MixinEnvironment;

import java.lang.reflect.Field;

/**
 * Step 2: Bootstrap Mixin subsystem.
 */
public class BootstrapLoader {
    private static final String LOG = PulseLogger.PULSE;

    public void initialize(InitializationContext context) {
        PulseLogger.info(LOG, "Step 2: Bootstrapping Mixin subsystem...");

        MixinBootstrap.init();

        checkEnvironment();
        inspectPhase();

        PulseLogger.info(LOG, "Step 2: Complete");

        checkMixinInternalState();
    }

    private void checkEnvironment() {
        MixinEnvironment env = MixinEnvironment.getDefaultEnvironment();
        PulseLogger.info(LOG, "  - Default Environment: {}", env);
        PulseLogger.info(LOG, "  - Side: {}", env.getSide());
        PulseLogger.info(LOG, "  - Phase (after init): {}", env.getPhase());
    }

    private void inspectPhase() {
        try {
            MixinEnvironment env = MixinEnvironment.getDefaultEnvironment();
            var currentPhase = env.getPhase();
            PulseLogger.debug(LOG, "  - Current phase: {}", currentPhase);
            PulseLogger.debug(LOG, "  - Attempting to check/set phase for config registration...");

            Field phaseField = MixinEnvironment.class.getDeclaredField("currentPhase");
            phaseField.setAccessible(true);
            PulseLogger.debug(LOG, "  - Internal currentPhase: {}", phaseField.get(null));
        } catch (Exception e) {
            PulseLogger.debug(LOG, "  - Could not inspect phase field: {}", e.getMessage());
        }
    }

    private void checkMixinInternalState() {
        PulseLogger.info(LOG, "Step 2.5: Checking Mixin internal state...");
        try {
            var mixinEnv = MixinEnvironment.getDefaultEnvironment();
            PulseLogger.debug(LOG, "  - Environment: {}", mixinEnv);
            PulseLogger.debug(LOG, "  - Phase: {}", mixinEnv.getPhase());
            PulseLogger.debug(LOG, "  - Side: {}", mixinEnv.getSide());

            var service = org.spongepowered.asm.service.MixinService.getService();
            PulseLogger.info(LOG, "  - Active Service: {}", service.getName());
            PulseLogger.debug(LOG, "  - Service Class: {}", service.getClass().getName());

            var testStream = service.getResourceAsStream("mixins.pulse.json");
            PulseLogger.info(LOG, "  - Service.getResourceAsStream(): {}",
                    (testStream != null ? "OK" : "FAILED"));
            if (testStream != null) {
                byte[] bytes = testStream.readAllBytes();
                PulseLogger.debug(LOG, "  - Config file size: {} bytes", bytes.length);
                PulseLogger.trace(LOG, () -> "  - Config content preview: " +
                        new String(bytes, 0, Math.min(200, bytes.length)));
                testStream.close();
            }
        } catch (Throwable t) {
            PulseLogger.error(LOG, "  - Error checking state: {}", t.getMessage());
            t.printStackTrace();
        }
    }
}
