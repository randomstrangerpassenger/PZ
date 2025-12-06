package com.mutagen;

import org.spongepowered.asm.mixin.transformer.IMixinTransformer;

/**
 * Mutagen 전역 환경 상태 관리.
 * 
 * 다양한 컴포넌트 간에 공유되는 상태를 보관:
 * - Game ClassLoader
 * - Mixin Transformer
 * - Instrumentation 인스턴스
 * - 기타 환경 설정
 */
public class MutagenEnvironment {

    private static ClassLoader gameClassLoader;
    private static IMixinTransformer mixinTransformer;
    private static java.lang.instrument.Instrumentation instrumentation;
    
    private static boolean initialized = false;
    private static boolean mixinReady = false;

    // ================= Game ClassLoader =================

    public static void setGameClassLoader(ClassLoader cl) {
        if (gameClassLoader == null && cl != null) {
            gameClassLoader = cl;
            System.out.println("[Mutagen/Env] Game ClassLoader registered: " + cl);
            System.out.println("[Mutagen/Env] ClassLoader class: " + cl.getClass().getName());
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
            System.out.println("[Mutagen/Env] Mixin Transformer registered: " + 
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
        System.out.println("[Mutagen/Env] Instrumentation registered");
    }

    public static java.lang.instrument.Instrumentation getInstrumentation() {
        return instrumentation;
    }

    // ================= Lifecycle =================

    public static void markInitialized() {
        initialized = true;
        System.out.println("[Mutagen/Env] Environment marked as initialized");
    }

    public static boolean isInitialized() {
        return initialized;
    }

    // ================= Debug Info =================

    public static void printStatus() {
        System.out.println("==================================================");
        System.out.println("[Mutagen/Env] STATUS REPORT");
        System.out.println("  Initialized: " + initialized);
        System.out.println("  Game ClassLoader: " + (gameClassLoader != null ? gameClassLoader : "NOT SET"));
        System.out.println("  Mixin Ready: " + mixinReady);
        System.out.println("  Mixin Transformer: " + (mixinTransformer != null ? "SET" : "NOT SET"));
        System.out.println("  Instrumentation: " + (instrumentation != null ? "SET" : "NOT SET"));
        System.out.println("==================================================");
    }
}
