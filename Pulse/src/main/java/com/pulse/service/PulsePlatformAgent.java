package com.pulse.service;

import org.spongepowered.asm.launch.platform.MixinPlatformAgentAbstract;
import org.spongepowered.asm.launch.platform.container.IContainerHandle;

/**
 * Mixin Platform Agent.
 */
public class PulsePlatformAgent extends MixinPlatformAgentAbstract {

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
        System.out.println("[Pulse/PlatformAgent] prepare()");
    }

    public void initPrimaryContainer() {
        System.out.println("[Pulse/PlatformAgent] initPrimaryContainer()");
    }

    public void inject() {
        System.out.println("[Pulse/PlatformAgent] inject()");
    }

    public String getLaunchTarget() {
        return null;
    }
}
