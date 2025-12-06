package com.pulse.transformer;

import com.pulse.PulseEnvironment;
import org.spongepowered.asm.mixin.MixinEnvironment;
import org.spongepowered.asm.mixin.transformer.IMixinTransformer;

import java.lang.instrument.ClassFileTransformer;
import java.security.ProtectionDomain;
import java.util.HashSet;
import java.util.Set;

/**
 * Pulse의 핵심 클래스 트랜스포머.
 * Java Instrumentation API와 Sponge Mixin을 연결한다.
 *
 * 역할:
 * 1. zombie.* 클래스 로딩을 감지
 * 2. Mixin 변환을 적용
 * 3. 향후 추가될 다른 transformer들과 체이닝
 */
public class PulseClassTransformer implements ClassFileTransformer {

    private final Set<String> transformedClasses = new HashSet<>();
    private final Set<String> excludedPrefixes = new HashSet<>();

    private IMixinTransformer mixinTransformer;
    private boolean mixinReady = false;

    public PulseClassTransformer() {
        // Mixin 적용 제외 패키지
        excludedPrefixes.add("java/");
        excludedPrefixes.add("javax/");
        excludedPrefixes.add("sun/");
        excludedPrefixes.add("jdk/");
        excludedPrefixes.add("com.pulse/");
        excludedPrefixes.add("org/spongepowered/");
        excludedPrefixes.add("org/objectweb/asm/");
    }

    /**
     * Mixin Transformer를 연결한다.
     * MixinBootstrap.init() 이후에 호출되어야 함.
     */
    public void connectMixinTransformer(IMixinTransformer transformer) {
        this.mixinTransformer = transformer;
        this.mixinReady = (transformer != null);

        if (mixinReady) {
            System.out.println("[Pulse/Transformer] Mixin transformer connected successfully");
        } else {
            System.err.println("[Pulse/Transformer] WARNING: Mixin transformer is null!");
        }
    }

    @Override
    public byte[] transform(
            ClassLoader loader,
            String className,
            Class<?> classBeingRedefined,
            ProtectionDomain protectionDomain,
            byte[] classfileBuffer) {
        if (className == null || classfileBuffer == null) {
            return null;
        }

        // 제외 패키지 체크
        for (String prefix : excludedPrefixes) {
            if (className.startsWith(prefix)) {
                return null;
            }
        }

        // Game ClassLoader 등록 (최초 zombie 클래스 발견 시)
        if (className.startsWith("zombie/") && loader != null) {
            if (PulseEnvironment.getGameClassLoader() == null) {
                PulseEnvironment.setGameClassLoader(loader);
            }
        }

        // Mixin 변환 적용
        byte[] transformed = applyMixinTransform(className, classfileBuffer);

        return transformed;
    }

    // Java 9+ module-aware 버전
    @Override
    public byte[] transform(
            Module module,
            ClassLoader loader,
            String className,
            Class<?> classBeingRedefined,
            ProtectionDomain protectionDomain,
            byte[] classfileBuffer) {
        return transform(loader, className, classBeingRedefined, protectionDomain, classfileBuffer);
    }

    private byte[] applyMixinTransform(String className, byte[] classfileBuffer) {
        if (!mixinReady || mixinTransformer == null) {
            return null;
        }

        // zombie 패키지만 Mixin 대상
        if (!className.startsWith("zombie/")) {
            return null;
        }

        String dotName = className.replace('/', '.');

        try {
            // Mixin 환경 가져오기
            MixinEnvironment env = MixinEnvironment.getDefaultEnvironment();

            // 변환 수행
            byte[] result = mixinTransformer.transformClass(env, dotName, classfileBuffer);

            if (result != null && result != classfileBuffer) {
                transformedClasses.add(dotName);
                System.out.println("[Pulse/Transformer] ✓ Mixin applied to: " + dotName);
                return result;
            }

        } catch (Throwable t) {
            System.err.println("[Pulse/Transformer] Error transforming: " + dotName);
            t.printStackTrace();
        }

        return null;
    }

    public Set<String> getTransformedClasses() {
        return new HashSet<>(transformedClasses);
    }

    public boolean isMixinReady() {
        return mixinReady;
    }
}
