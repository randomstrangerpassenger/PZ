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

    // --- Game ClassLoader ---

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

    // --- Mixin Transformer ---

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

    // --- Instrumentation ---

    public static void setInstrumentation(java.lang.instrument.Instrumentation inst) {
        instrumentation = inst;
        PulseLogger.info(PulseLogger.PULSE, "Instrumentation registered");
    }

    public static java.lang.instrument.Instrumentation getInstrumentation() {
        return instrumentation;
    }

    // --- Lifecycle ---

    public static void markInitialized() {
        initialized = true;
        PulseLogger.info(PulseLogger.PULSE, "Environment marked as initialized");
    }

    public static boolean isInitialized() {
        return initialized;
    }

    // --- Development Mode ---

    private static volatile Boolean developmentModeCache = null;

    /**
     * 개발 모드 여부 확인.
     * 
     * 다음 조건 중 하나라도 만족하면 개발 모드:
     * <ul>
     * <li>시스템 프로퍼티 {@code pulse.dev=true}</li>
     * <li>환경 변수 {@code PULSE_DEV} 설정됨</li>
     * <li>실행 디렉토리에 {@code pulse_dev.lock} 파일 존재</li>
     * </ul>
     * 
     * 개발 모드에서는 Mixin 에러가 전파되어 디버깅이 용이함.
     * 프로덕션에서는 에러가 격리되어 게임 안정성 유지.
     * 
     * @return 개발 모드이면 true
     */
    public static boolean isDevelopmentMode() {
        if (developmentModeCache != null) {
            return developmentModeCache;
        }

        // System property check
        if (Boolean.getBoolean("pulse.dev")) {
            developmentModeCache = true;
            return true;
        }

        // Environment variable check
        String envVar = System.getenv("PULSE_DEV");
        if (envVar != null && !envVar.isEmpty()) {
            developmentModeCache = true;
            return true;
        }

        // Lock file check
        java.io.File lockFile = new java.io.File("pulse_dev.lock");
        if (lockFile.exists()) {
            developmentModeCache = true;
            return true;
        }

        developmentModeCache = false;
        return false;
    }

    /**
     * 개발 모드 캐시 초기화 (테스트용).
     */
    public static void resetDevelopmentModeCache() {
        developmentModeCache = null;
    }

    // --- Debug Info ---

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
