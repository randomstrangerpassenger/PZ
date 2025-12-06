package com.mutagen.service;

import com.mutagen.MutagenEnvironment;

import java.lang.instrument.ClassFileTransformer;
import java.security.ProtectionDomain;

public class MutagenGameClassTracker implements ClassFileTransformer {

    @Override
    public byte[] transform(
            Module module,
            ClassLoader loader,
            String className,
            Class<?> classBeingRedefined,
            ProtectionDomain protectionDomain,
            byte[] classfileBuffer
    ) {
        // 예: className = "zombie/characters/IsoZombie"
        if (className != null && loader != null && className.startsWith("zombie/")) {
            System.out.println("[Mutagen/TRACKER] Detected zombie class: " + className);
            System.out.println("[Mutagen/TRACKER] Loader: " + loader);

            // 실제 게임 클래스 로더 등록
            MutagenEnvironment.setGameClassLoader(loader);
        }

        // 클래스 바이트코드는 건드리지 않는다
        return null;
    }
}
