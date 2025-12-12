package com.pulse.service;

import com.pulse.api.log.PulseLogger;
import com.pulse.PulseEnvironment;

import java.lang.instrument.ClassFileTransformer;
import java.security.ProtectionDomain;

public class PulseGameClassTracker implements ClassFileTransformer {
    private static final String LOG = PulseLogger.PULSE;

    @Override
    public byte[] transform(
            Module module,
            ClassLoader loader,
            String className,
            Class<?> classBeingRedefined,
            ProtectionDomain protectionDomain,
            byte[] classfileBuffer) {
        // 예: className = "zombie/characters/IsoZombie"
        if (className != null && loader != null && className.startsWith("zombie/")) {
            PulseLogger.info(LOG, "[TRACKER] Detected zombie class: {}", className);
            PulseLogger.info(LOG, "[TRACKER] Loader: {}", loader);

            // 실제 게임 클래스 로더 등록
            PulseEnvironment.setGameClassLoader(loader);
        }

        // 클래스 바이트코드는 건드리지 않는다
        return null;
    }
}
