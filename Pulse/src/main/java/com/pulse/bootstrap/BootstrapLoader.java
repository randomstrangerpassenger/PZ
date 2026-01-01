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

        // Mixin 0.8.7: Force transition to DEFAULT phase to ensure environment is
        // initialized
        // This prevents "this.env is null" errors in MixinConfig.onLoad()
        forceDefaultPhase();

        checkEnvironment();
        inspectPhase();

        PulseLogger.info(LOG, "Step 2: Complete");

        checkMixinInternalState();
    }

    private void forceDefaultPhase() {
        PulseLogger.info(LOG, "  [DEBUG] Forcing transition to DEFAULT phase...");

        try {
            Class<?> envClass = MixinEnvironment.class;

            // Method 1 (Priority): Get DEFAULT environment and set it as current
            // This is the most direct approach
            try {
                MixinEnvironment defaultEnv = MixinEnvironment.getDefaultEnvironment();
                if (defaultEnv != null) {
                    Field currentEnvField = envClass.getDeclaredField("currentEnvironment");
                    currentEnvField.setAccessible(true);
                    Object oldEnv = currentEnvField.get(null);
                    currentEnvField.set(null, defaultEnv);
                    PulseLogger.info(LOG, "  [DEBUG] Set currentEnvironment: {} -> {}", oldEnv, defaultEnv);
                } else {
                    PulseLogger.warn(LOG, "  [DEBUG] getDefaultEnvironment() returned null!");
                }
            } catch (Exception e) {
                PulseLogger.warn(LOG, "  [DEBUG] Could not set currentEnvironment: {}", e.getMessage());
            }

            // Method 2: Try to get Phase.DEFAULT via static field access
            Object defaultPhase = null;
            try {
                Class<?> phaseClass = Class.forName("org.spongepowered.asm.mixin.MixinEnvironment$Phase");

                // Try to get DEFAULT as a static field
                try {
                    Field defaultField = phaseClass.getDeclaredField("DEFAULT");
                    defaultField.setAccessible(true);
                    defaultPhase = defaultField.get(null);
                    PulseLogger.info(LOG, "  [DEBUG] Got Phase.DEFAULT via field: {}", defaultPhase);
                } catch (NoSuchFieldException e) {
                    // Try enum constants as fallback
                    Object[] enumConstants = phaseClass.getEnumConstants();
                    if (enumConstants != null) {
                        for (Object enumVal : enumConstants) {
                            if ("DEFAULT".equals(enumVal.toString())) {
                                defaultPhase = enumVal;
                                break;
                            }
                        }
                    }
                }

                if (defaultPhase != null) {
                    // Set currentPhase field
                    try {
                        Field currentPhaseField = envClass.getDeclaredField("currentPhase");
                        currentPhaseField.setAccessible(true);
                        Object oldPhase = currentPhaseField.get(null);
                        currentPhaseField.set(null, defaultPhase);
                        PulseLogger.info(LOG, "  [DEBUG] Set currentPhase: {} -> {}", oldPhase, defaultPhase);
                    } catch (Exception e) {
                        PulseLogger.warn(LOG, "  [DEBUG] Could not set currentPhase: {}", e.getMessage());
                    }

                    // Try gotoPhase() method
                    try {
                        java.lang.reflect.Method gotoPhase = envClass.getDeclaredMethod("gotoPhase", phaseClass);
                        gotoPhase.setAccessible(true);
                        gotoPhase.invoke(null, defaultPhase);
                        PulseLogger.info(LOG, "  [DEBUG] gotoPhase(DEFAULT) called successfully");
                    } catch (Exception e) {
                        PulseLogger.warn(LOG, "  [DEBUG] gotoPhase() failed: {}", e.getMessage());
                    }
                }
            } catch (ClassNotFoundException e) {
                PulseLogger.warn(LOG, "  [DEBUG] Phase class not found: {}", e.getMessage());
            }

            // Verify the change
            try {
                MixinEnvironment currentEnv = MixinEnvironment.getCurrentEnvironment();
                PulseLogger.info(LOG, "  [DEBUG] Verification: getCurrentEnvironment() = {}", currentEnv);
            } catch (Exception e) {
                PulseLogger.warn(LOG, "  [DEBUG] Verification failed: {}", e.getMessage());
            }

        } catch (Exception e) {
            PulseLogger.error(LOG, "  [DEBUG] forceDefaultPhase failed: {}", e.getMessage());
            e.printStackTrace();
        }
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
