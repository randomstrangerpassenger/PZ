package com.pulse.transformer;

import com.pulse.api.log.PulseLogger;
import com.pulse.PulseEnvironment;
import com.pulse.mixin.MixinDiagnostics;
import org.spongepowered.asm.mixin.MixinEnvironment;
import org.spongepowered.asm.mixin.transformer.IMixinTransformer;

import java.lang.instrument.ClassFileTransformer;
import java.security.ProtectionDomain;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

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

    private static final String LOG = PulseLogger.PULSE;

    private final Set<String> transformedClasses = ConcurrentHashMap.newKeySet();
    private final Set<String> excludedPrefixes = ConcurrentHashMap.newKeySet();

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
            PulseLogger.info(LOG, "Mixin transformer connected successfully");
        } else {
            PulseLogger.warn(LOG, "WARNING: Mixin transformer is null!");
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

        // Mixin 대상 패키지: zombie, se.krka.kahlua (Lua VM)
        boolean isTargetPackage = className.startsWith("zombie/") ||
                className.startsWith("se/krka/kahlua/");
        if (!isTargetPackage) {
            return null;
        }

        String dotName = className.replace('/', '.');

        try {
            // Mixin 환경 가져오기
            MixinEnvironment env = MixinEnvironment.getDefaultEnvironment();

            long startTime = System.nanoTime();

            // 변환 수행
            byte[] result = mixinTransformer.transformClass(env, dotName, classfileBuffer);

            if (result != null && result != classfileBuffer) {
                long elapsedMs = (System.nanoTime() - startTime) / 1_000_000;

                transformedClasses.add(dotName);

                // MixinDiagnostics 연동
                MixinDiagnostics.getInstance().recordMixinApplied(
                        dotName, "PulseTransformer", "pulse", 1000);

                // MixinInjectionValidator 성공 기록
                com.pulse.api.mixin.MixinInjectionValidator.recordSuccess(
                        "PulseTransformer", dotName, elapsedMs);

                PulseLogger.debug(LOG, "✓ Mixin applied to: {}", dotName);
                return result;
            }

        } catch (Throwable t) {
            // Fail-soft 처리 - 실패해도 게임 계속
            MixinDiagnostics.getInstance().recordMixinFailed(
                    "Unknown", "pulse", dotName, t.getMessage());

            // MixinInjectionValidator 실패 기록
            com.pulse.api.mixin.MixinInjectionValidator.recordFailure(
                    "PulseTransformer", dotName, t.getMessage());

            // FailsoftPolicy로 처리 (크래시 대신 경고)
            com.pulse.api.FailsoftPolicy.handleMixinFailure(
                    "PulseTransformer", dotName, t);

            PulseLogger.warn(LOG, "Error transforming: {} (fail-soft applied)", dotName);
        }

        return null;
    }

    public Set<String> getTransformedClasses() {
        return new java.util.HashSet<>(transformedClasses);
    }

    public boolean isMixinReady() {
        return mixinReady;
    }
}
