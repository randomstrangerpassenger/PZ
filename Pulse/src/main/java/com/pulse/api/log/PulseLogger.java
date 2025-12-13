package com.pulse.api.log;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/**
 * Pulse 로깅 파사드.
 * 
 * 모든 모듈에서 정적 메서드로 로깅을 수행할 수 있습니다.
 * 내부적으로 모듈별 로거를 관리합니다.
 * 
 * <p>
 * 사용 예시:
 * </p>
 * 
 * <pre>
 * // 기본 로깅
 * PulseLogger.info("Pulse", "Initialization complete");
 * 
 * // 포맷 문자열
 * PulseLogger.debug("Echo", "Tick {} took {}ms", tickNumber, duration);
 * 
 * // Lazy evaluation (성능 최적화)
 * PulseLogger.debug("Pulse", () -> "Heavy computation: " + expensiveCall());
 * </pre>
 * 
 * @since 1.1.0
 */
public final class PulseLogger {

    private static final Map<String, ModuleLogger> LOGGERS = new ConcurrentHashMap<>();

    /** 전역 기본 로그 레벨 */
    private static volatile PulseLogLevel globalLevel = PulseLogLevel.INFO;

    private PulseLogger() {
    }

    // --- 로거 관리---

    /**
     * 모듈별 로거를 가져오거나 생성합니다.
     */
    public static ModuleLogger getLogger(String moduleName) {
        return LOGGERS.computeIfAbsent(moduleName, name -> new ModuleLogger(name, globalLevel));
    }

    /**
     * 전역 로그 레벨 설정.
     * 이미 생성된 로거에도 적용됩니다.
     */
    public static void setGlobalLevel(PulseLogLevel level) {
        globalLevel = level;
        LOGGERS.values().forEach(logger -> logger.setLevel(level));
    }

    /**
     * 특정 모듈의 로그 레벨만 변경.
     */
    public static void setModuleLevel(String moduleName, PulseLogLevel level) {
        getLogger(moduleName).setLevel(level);
    }

    /**
     * 현재 전역 로그 레벨.
     */
    public static PulseLogLevel getGlobalLevel() {
        return globalLevel;
    }

    // --- 정적 로깅 메서드---

    public static void trace(String module, String message) {
        getLogger(module).trace(message);
    }

    public static void trace(String module, Supplier<String> messageSupplier) {
        getLogger(module).trace(messageSupplier);
    }

    public static void trace(String module, String format, Object... args) {
        getLogger(module).trace(format, args);
    }

    public static void debug(String module, String message) {
        getLogger(module).debug(message);
    }

    public static void debug(String module, Supplier<String> messageSupplier) {
        getLogger(module).debug(messageSupplier);
    }

    public static void debug(String module, String format, Object... args) {
        getLogger(module).debug(format, args);
    }

    public static void info(String module, String message) {
        getLogger(module).info(message);
    }

    public static void info(String module, String format, Object... args) {
        getLogger(module).info(format, args);
    }

    public static void warn(String module, String message) {
        getLogger(module).warn(message);
    }

    public static void warn(String module, String format, Object... args) {
        getLogger(module).warn(format, args);
    }

    public static void warn(String module, String message, Throwable t) {
        getLogger(module).warn(message, t);
    }

    public static void error(String module, String message) {
        getLogger(module).error(message);
    }

    public static void error(String module, String format, Object... args) {
        getLogger(module).error(format, args);
    }

    public static void error(String module, String message, Throwable t) {
        getLogger(module).error(message, t);
    }

    // --- 모듈별 상수---

    /** Pulse 코어 모듈 */
    public static final String PULSE = "Pulse";

    /** Echo 프로파일러 모듈 */
    public static final String ECHO = "Echo";

    /** Fuse 최적화 모듈 */
    public static final String FUSE = "Fuse";

    /** Nerve 모니터링 모듈 */
    public static final String NERVE = "Nerve";

    // --- 디버그 전용 헬퍼---

    /**
     * 디버그 레벨이 활성화되어 있는지 확인.
     * 무거운 로그 메시지 생성 전 체크용.
     */
    public static boolean isDebugEnabled(String module) {
        return getLogger(module).isEnabled(PulseLogLevel.DEBUG);
    }

    /**
     * 트레이스 레벨이 활성화되어 있는지 확인.
     */
    public static boolean isTraceEnabled(String module) {
        return getLogger(module).isEnabled(PulseLogLevel.TRACE);
    }
}
