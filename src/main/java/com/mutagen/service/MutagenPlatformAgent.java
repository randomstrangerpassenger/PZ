package com.mutagen.service;

import org.spongepowered.asm.launch.platform.MixinPlatformAgentAbstract;
import org.spongepowered.asm.launch.platform.container.IContainerHandle;

/**
 * Mixin Platform Agent.
 */
public class MutagenPlatformAgent extends MixinPlatformAgentAbstract {

    public AcceptResult accept(IContainerHandle root, String className) {
        if (className != null && className.startsWith("com.mutagen.")) {
            return AcceptResult.ACCEPTED;
        }
        return AcceptResult.REJECTED;
    }

    public String getPhaseProvider() {
        return null;
    }

    public void prepare() {
        System.out.println("[Mutagen/PlatformAgent] prepare()");
    }

    public void initPrimaryContainer() {
        System.out.println("[Mutagen/PlatformAgent] initPrimaryContainer()");
    }

    public void inject() {
        System.out.println("[Mutagen/PlatformAgent] inject()");
    }

    public String getLaunchTarget() {
        return null;
    }
}
