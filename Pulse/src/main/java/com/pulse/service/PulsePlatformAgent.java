package com.pulse.service;

import com.pulse.api.log.PulseLogger;
import org.spongepowered.asm.launch.platform.MixinPlatformAgentAbstract;
import org.spongepowered.asm.launch.platform.container.IContainerHandle;

/**
 * Mixin Platform Agent.
 */
public class PulsePlatformAgent extends MixinPlatformAgentAbstract {
    private static final String LOG = PulseLogger.PULSE;

    public AcceptResult accept(IContainerHandle root, String className) {
        if (className != null && className.startsWith("com.pulse.")) {
            return AcceptResult.ACCEPTED;
        }
        return AcceptResult.REJECTED;
    }

    public String getPhaseProvider() {
        return null;
    }

    public void prepare() {
        PulseLogger.info(LOG, "[PlatformAgent] prepare()");
    }

    public void initPrimaryContainer() {
        PulseLogger.info(LOG, "[PlatformAgent] initPrimaryContainer()");
    }

    public void inject() {
        PulseLogger.info(LOG, "[PlatformAgent] inject()");
    }

    public String getLaunchTarget() {
        return null;
    }
}
