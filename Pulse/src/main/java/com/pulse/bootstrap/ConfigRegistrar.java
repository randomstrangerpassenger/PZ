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
            PulseLogger.debug(LOG, "  - Calling Mixins.addConfiguration()...");

            int beforeCount = Mixins.getConfigs().size();
            PulseLogger.debug(LOG, "  - Configs before: {}", beforeCount);

            Mixins.addConfiguration(CONFIG_FILE);

            int afterCount = Mixins.getConfigs().size();
            PulseLogger.debug(LOG, "  - Configs after: {}", afterCount);

            if (afterCount == beforeCount) {
                PulseLogger.warn(LOG, "  - WARNING: Config was not added! Trying alternative method...");
                registerViaInternalApi();
            }

            PulseLogger.debug(LOG, "  - addConfiguration() completed");
        } catch (Throwable t) {
            PulseLogger.error(LOG, "  - ERROR in addConfiguration(): {}", t.getClass().getName());
            PulseLogger.error(LOG, "  - Message: {}", t.getMessage());
            t.printStackTrace();
        }
    }

    private void registerViaInternalApi() {
        try {
            Class<?> mixinConfigClass = Class.forName("org.spongepowered.asm.mixin.transformer.MixinConfig");
            Method createMethod = mixinConfigClass.getDeclaredMethod("create", String.class, MixinEnvironment.class);
            createMethod.setAccessible(true);

            Object config = createMethod.invoke(null, CONFIG_FILE, MixinEnvironment.getDefaultEnvironment());
            PulseLogger.debug(LOG, "  - Direct MixinConfig.create() result: {}", config);

            if (config != null) {
                PulseLogger.info(LOG, "  - Config created successfully: {}", config);
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
