package com.pulse.mod.mixin;

import com.pulse.api.log.PulseLogger;
import com.pulse.mod.ModContainer;
import com.pulse.mod.ModMetadata;
import org.spongepowered.asm.mixin.Mixins;

import java.util.List;

/**
 * Handles registration of Mixin configurations from mods.
 */
public class MixinRegistrar {
    private static final String LOG = PulseLogger.PULSE;

    public void registerMixins(List<ModContainer> loadOrder) {
        PulseLogger.info(LOG, "Registering mod mixins...");

        for (ModContainer container : loadOrder) {
            ModMetadata metadata = container.getMetadata();
            List<String> mixinConfigs = metadata.getMixins();

            if (mixinConfigs == null || mixinConfigs.isEmpty()) {
                continue;
            }

            for (String mixinConfig : mixinConfigs) {
                try {
                    PulseLogger.info(LOG, "Registered mixin config {} from {}",
                            mixinConfig, metadata.getId());
                    Mixins.addConfiguration(mixinConfig);
                } catch (Exception e) {
                    PulseLogger.error(LOG, "✗ Failed to register {} from {}: {}",
                            mixinConfig, metadata.getId(), e.getMessage());
                }
            }

            container.setState(ModContainer.ModState.MIXINS_APPLIED);
        }
    }
}
