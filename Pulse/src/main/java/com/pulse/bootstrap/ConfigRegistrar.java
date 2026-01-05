package com.pulse.bootstrap;

import com.pulse.api.log.PulseLogger;
import org.spongepowered.asm.mixin.MixinEnvironment;
import org.spongepowered.asm.mixin.Mixins;

import java.io.InputStream;
import java.lang.reflect.Method;

/**
 * Step 3: Register Mixin configurations.
 */
public class ConfigRegistrar {
    private static final String LOG = PulseLogger.PULSE;
    private static final String CONFIG_FILE = "mixins.pulse.json";

    public void initialize(InitializationContext context) {
        PulseLogger.info(LOG, "Step 3: Registering Mixin configurations...");

        checkConfigFile();
        registerConfig();
        verifyRegistration();

        PulseLogger.info(LOG, "Step 3: Complete");
    }

    private void checkConfigFile() {
        try {
            InputStream configStream = getClass().getClassLoader().getResourceAsStream(CONFIG_FILE);
            if (configStream != null) {
                PulseLogger.info(LOG, "  - Found: {}", CONFIG_FILE);
                configStream.close();
            } else {
                PulseLogger.warn(LOG, "  - WARNING: {} not found in classpath!", CONFIG_FILE);
            }
        } catch (Exception e) {
            PulseLogger.error(LOG, "  - Error checking config file: {}", e.getMessage());
        }
    }

    private void registerConfig() {
        try {
            PulseLogger.info(LOG, "  [DEBUG] ===== Mixin Environment Analysis =====");

            // Check MixinEnvironment state
            debugMixinEnvironment();

            PulseLogger.debug(LOG, "  - Calling Mixins.addConfiguration()...");

            int beforeCount = Mixins.getConfigs().size();
            PulseLogger.info(LOG, "  [DEBUG] Configs before: {}", beforeCount);

            Mixins.addConfiguration(CONFIG_FILE);

            int afterCount = Mixins.getConfigs().size();
            PulseLogger.info(LOG, "  [DEBUG] Configs after: {}", afterCount);

            if (afterCount == beforeCount) {
                PulseLogger.warn(LOG, "  - WARNING: Config was not added! Trying alternative method...");
                registerViaInternalApi();
            }

            PulseLogger.debug(LOG, "  - addConfiguration() completed");
        } catch (Throwable t) {
            PulseLogger.error(LOG, "  - ERROR in addConfiguration(): {}", t.getClass().getName());
            PulseLogger.error(LOG, "  - Message: {}", t.getMessage());
            t.printStackTrace();

            // Fallback: Try with explicit environment binding
            PulseLogger.info(LOG, "  - Attempting fallback registration with explicit environment...");
            registerViaInternalApi();
        }
    }

    private void debugMixinEnvironment() {
        try {
            // 1. Check getDefaultEnvironment
            PulseLogger.info(LOG, "  [DEBUG] Checking MixinEnvironment.getDefaultEnvironment()...");
            MixinEnvironment defaultEnv = null;
            try {
                defaultEnv = MixinEnvironment.getDefaultEnvironment();
                PulseLogger.info(LOG, "  [DEBUG] getDefaultEnvironment() = {}", defaultEnv);
                if (defaultEnv != null) {
                    PulseLogger.info(LOG, "  [DEBUG]   Phase: {}", defaultEnv.getPhase());
                    PulseLogger.info(LOG, "  [DEBUG]   Side: {}", defaultEnv.getSide());
                }
            } catch (Throwable t) {
                PulseLogger.error(LOG, "  [DEBUG] getDefaultEnvironment() FAILED: {}", t.getMessage());
            }

            // 2. Check getCurrentEnvironment
            PulseLogger.info(LOG, "  [DEBUG] Checking MixinEnvironment.getCurrentEnvironment()...");
            try {
                MixinEnvironment currentEnv = MixinEnvironment.getCurrentEnvironment();
                PulseLogger.info(LOG, "  [DEBUG] getCurrentEnvironment() = {}", currentEnv);
            } catch (Throwable t) {
                PulseLogger.error(LOG, "  [DEBUG] getCurrentEnvironment() FAILED: {}", t.getMessage());
            }

            // 3. Check internal fields via reflection
            PulseLogger.info(LOG, "  [DEBUG] Checking internal Mixin state via reflection...");
            try {
                Class<?> envClass = MixinEnvironment.class;

                // Check currentEnvironment static field
                java.lang.reflect.Field currentEnvField = envClass.getDeclaredField("currentEnvironment");
                currentEnvField.setAccessible(true);
                Object currentEnvValue = currentEnvField.get(null);
                PulseLogger.info(LOG, "  [DEBUG] MixinEnvironment.currentEnvironment = {}", currentEnvValue);

                // Check currentPhase static field
                java.lang.reflect.Field currentPhaseField = envClass.getDeclaredField("currentPhase");
                currentPhaseField.setAccessible(true);
                Object currentPhaseValue = currentPhaseField.get(null);
                PulseLogger.info(LOG, "  [DEBUG] MixinEnvironment.currentPhase = {}", currentPhaseValue);

                // Check phases map
                java.lang.reflect.Field phasesField = envClass.getDeclaredField("phases");
                phasesField.setAccessible(true);
                Object phasesValue = phasesField.get(null);
                PulseLogger.info(LOG, "  [DEBUG] MixinEnvironment.phases = {}", phasesValue);

            } catch (Throwable t) {
                PulseLogger.warn(LOG, "  [DEBUG] Reflection check failed: {} - {}", t.getClass().getSimpleName(),
                        t.getMessage());
            }

            // 4. Check MixinService state
            PulseLogger.info(LOG, "  [DEBUG] Checking MixinService state...");
            try {
                var service = org.spongepowered.asm.service.MixinService.getService();
                PulseLogger.info(LOG, "  [DEBUG] MixinService = {}", service.getName());
                PulseLogger.info(LOG, "  [DEBUG] MixinService.getInitialPhase() = {}", service.getInitialPhase());
            } catch (Throwable t) {
                PulseLogger.error(LOG, "  [DEBUG] MixinService check failed: {}", t.getMessage());
            }

            PulseLogger.info(LOG, "  [DEBUG] ===== End Mixin Environment Analysis =====");
        } catch (Throwable t) {
            PulseLogger.error(LOG, "  [DEBUG] Debug analysis failed: {}", t.getMessage());
        }
    }

    private void registerViaInternalApi() {
        PulseLogger.info(LOG, "  [DEBUG] registerViaInternalApi - using Mixin 0.8.7 API");
        try {
            MixinEnvironment env = MixinEnvironment.getDefaultEnvironment();
            PulseLogger.info(LOG, "  [DEBUG] Environment for config: {}", env);

            if (env == null) {
                PulseLogger.error(LOG, "  [DEBUG] Environment is NULL! Cannot proceed.");
                return;
            }

            Class<?> configClass = Class.forName("org.spongepowered.asm.mixin.transformer.Config");

            // Method 1: Try Config.create(String, MixinEnvironment, IMixinConfigSource)
            Object config = null;
            try {
                Class<?> sourceInterface = Class
                        .forName("org.spongepowered.asm.mixin.extensibility.IMixinConfigSource");
                Method createMethod = configClass.getDeclaredMethod("create", String.class, MixinEnvironment.class,
                        sourceInterface);
                createMethod.setAccessible(true);
                config = createMethod.invoke(null, CONFIG_FILE, env, null);
                PulseLogger.info(LOG, "  [DEBUG] Config.create(String, Env, Source) result: {}", config);
            } catch (NoSuchMethodException e) {
                PulseLogger.warn(LOG, "  [DEBUG] Method 1 not found: {}", e.getMessage());
            }

            // Method 2: Try Config.create(String, IMixinConfigSource) - uses
            // getDefaultEnvironment internally
            if (config == null) {
                try {
                    Class<?> sourceInterface = Class
                            .forName("org.spongepowered.asm.mixin.extensibility.IMixinConfigSource");
                    Method createMethod = configClass.getDeclaredMethod("create", String.class, sourceInterface);
                    createMethod.setAccessible(true);
                    config = createMethod.invoke(null, CONFIG_FILE, (Object) null);
                    PulseLogger.info(LOG, "  [DEBUG] Config.create(String, Source) result: {}", config);
                } catch (NoSuchMethodException e) {
                    PulseLogger.warn(LOG, "  [DEBUG] Method 2 not found: {}", e.getMessage());
                }
            }

            // Method 3: Try deprecated Config.create(String, MixinEnvironment)
            if (config == null) {
                try {
                    Method createMethod = configClass.getDeclaredMethod("create", String.class, MixinEnvironment.class);
                    createMethod.setAccessible(true);
                    config = createMethod.invoke(null, CONFIG_FILE, env);
                    PulseLogger.info(LOG, "  [DEBUG] Config.create(String, Env) result: {}", config);
                } catch (NoSuchMethodException e) {
                    PulseLogger.warn(LOG, "  [DEBUG] Method 3 not found: {}", e.getMessage());
                }
            }

            if (config != null) {
                // Add to Mixins.getConfigs() set directly
                try {
                    @SuppressWarnings("unchecked")
                    java.util.Set<Object> configs = (java.util.Set<Object>) (java.util.Set<?>) Mixins.getConfigs();
                    if (configs != null) {
                        configs.add(config);
                        PulseLogger.info(LOG, "  [DEBUG] Config added to Mixins.getConfigs() set. New size: {}",
                                configs.size());
                    }
                } catch (Exception e) {
                    PulseLogger.warn(LOG, "  [DEBUG] Could not add to getConfigs(): {}", e.getMessage());
                }
            } else {
                PulseLogger.error(LOG, "  [DEBUG] All Config.create() methods failed!");
            }
        } catch (Exception ex) {
            PulseLogger.error(LOG, "  - Alternative method failed: {}", ex.getMessage());
            ex.printStackTrace();
        }
    }

    private void verifyRegistration() {
        try {
            PulseLogger.debug(LOG, "  - Calling Mixins.getConfigs()...");
            var configs = Mixins.getConfigs();
            PulseLogger.info(LOG, "  - Registered configs: {}", (configs != null ? configs.size() : "null"));

            if (configs != null) {
                for (var config : configs) {
                    PulseLogger.debug(LOG, "  - Config: {}", config);
                }
            }
        } catch (Throwable t) {
            PulseLogger.error(LOG, "  - ERROR in getConfigs(): {}", t.getClass().getName());
            PulseLogger.error(LOG, "  - Message: {}", t.getMessage());
            t.printStackTrace();
        }
    }
}
