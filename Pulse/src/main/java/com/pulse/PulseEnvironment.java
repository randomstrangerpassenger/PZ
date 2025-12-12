package com.pulse;

import com.pulse.api.log.PulseLogger;
import org.spongepowered.asm.mixin.transformer.IMixinTransformer;

/**
 * Pulse 전역 환경 상태 관리.
 * 
 * 다양한 컴포넌트 간에 공유되는 상태를 보관:
 * - Game ClassLoader
 * - Mixin Transformer
 * - Instrumentation 인스턴스
 * - 기타 환경 설정
 */
public class PulseEnvironment {

    private static ClassLoader gameClassLoader;
    private static IMixinTransformer mixinTransformer;
    private static java.lang.instrument.Instrumentation instrumentation;

    private static boolean initialized = false;
    private static boolean mixinReady = false;

    // ================= Game ClassLoader =================

    public static void setGameClassLoader(ClassLoader cl) {
        if (gameClassLoader == null && cl != null) {
            gameClassLoader = cl;
            PulseLogger.info(PulseLogger.PULSE, "Game ClassLoader registered: {}", cl);
            PulseLogger.debug(PulseLogger.PULSE, "ClassLoader class: {}", cl.getClass().getName());
        }
    }

    public static ClassLoader getGameClassLoader() {
        return gameClassLoader;
    }

    // ================= Mixin Transformer =================

    public static void setMixinTransformer(IMixinTransformer transformer) {
        if (mixinTransformer == null && transformer != null) {
            mixinTransformer = transformer;
            mixinReady = true;
            PulseLogger.info(PulseLogger.PULSE, "Mixin Transformer registered: {}",
                    transformer.getClass().getName());
        }
    }

    public static IMixinTransformer getMixinTransformer() {
        return mixinTransformer;
    }

    public static boolean isMixinReady() {
        return mixinReady;
    }

    // ================= Instrumentation =================

    public static void setInstrumentation(java.lang.instrument.Instrumentation inst) {
        instrumentation = inst;
        PulseLogger.info(PulseLogger.PULSE, "Instrumentation registered");
    }

    public static java.lang.instrument.Instrumentation getInstrumentation() {
        return instrumentation;
    }

    // ================= Lifecycle =================

    public static void markInitialized() {
        initialized = true;
        PulseLogger.info(PulseLogger.PULSE, "Environment marked as initialized");
    }

    public static boolean isInitialized() {
        return initialized;
    }

    // ================= Debug Info =================

    public static void printStatus() {
        PulseLogger.info(PulseLogger.PULSE, "==================================================");
        PulseLogger.info(PulseLogger.PULSE, "STATUS REPORT");
        PulseLogger.info(PulseLogger.PULSE, "  Initialized: {}", initialized);
        PulseLogger.info(PulseLogger.PULSE, "  Game ClassLoader: {}",
                (gameClassLoader != null ? gameClassLoader : "NOT SET"));
        PulseLogger.info(PulseLogger.PULSE, "  Mixin Ready: {}", mixinReady);
        PulseLogger.info(PulseLogger.PULSE, "  Mixin Transformer: {}",
                (mixinTransformer != null ? "SET" : "NOT SET"));
        PulseLogger.info(PulseLogger.PULSE, "  Instrumentation: {}",
                (instrumentation != null ? "SET" : "NOT SET"));
        PulseLogger.info(PulseLogger.PULSE, "==================================================");
    }
}
