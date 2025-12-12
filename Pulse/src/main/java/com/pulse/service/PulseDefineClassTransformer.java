package com.pulse.service;

import com.pulse.api.log.PulseLogger;
import com.pulse.PulseEnvironment;

import java.lang.instrument.ClassFileTransformer;
import java.security.ProtectionDomain;

public class PulseDefineClassTransformer implements ClassFileTransformer {
    private static final String LOG = PulseLogger.PULSE;

    @Override
    public byte[] transform(
            Module module,
            ClassLoader loader,
            String className,
            Class<?> classBeingRedefined,
            ProtectionDomain protectionDomain,
            byte[] classfileBuffer) {

        // defineClass가 호출될 때 className은 null일 수 있다.
        if (className == null || loader == null)
            return null;

        // convert name style: "zombie/characters/IsoZombie"
        if (className.startsWith("zombie/")) {

            PulseLogger.info(LOG, "ClassLoader has loaded zombie class: {}", className);
            PulseLogger.info(LOG, "Registering Game ClassLoader: {}", loader);

            PulseEnvironment.setGameClassLoader(loader);

            // Once captured, we do NOT want to override or modify class bytes
            return null;
        }

        return null;
    }
}
