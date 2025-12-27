package com.pulse.api.log;

import java.util.function.Supplier;

/**
 * Pulse 로거 인터페이스.
 * 
 * 경량 래퍼로 SLF4J 의존성 없이 로깅 기능을 제공합니다.
 * 향후 필요시 MDC 컨텍스트 확장 가능한 구조입니다.
 * 
 * @since 1.1.0
 */
public interface PulseLoggerInterface {

    /**
     * 로그 메시지를 출력합니다.
     */
    void log(PulseLogLevel level, String message);

    /**
     * 로그 메시지를 lazy evaluation으로 출력합니다.
     * 레벨이 비활성화되어 있으면 Supplier가 실행되지 않아 성능에 유리합니다.
     */
    void log(PulseLogLevel level, Supplier<String> messageSupplier);

    /**
     * 포맷 문자열로 로그 출력.
     */
    void log(PulseLogLevel level, String format, Object... args);

    /**
     * 예외와 함께 로그 출력.
     */
    void log(PulseLogLevel level, String message, Throwable throwable);

    /**
     * 해당 로그 레벨이 활성화되어 있는지 확인.
     */
    boolean isEnabled(PulseLogLevel level);

    // --- 편의 메서드---

    default void trace(String message) {
        log(PulseLogLevel.TRACE, message);
    }

    default void trace(Supplier<String> messageSupplier) {
        log(PulseLogLevel.TRACE, messageSupplier);
    }

    default void trace(String format, Object... args) {
        log(PulseLogLevel.TRACE, format, args);
    }

    default void debug(String message) {
        log(PulseLogLevel.DEBUG, message);
    }

    default void debug(Supplier<String> messageSupplier) {
        log(PulseLogLevel.DEBUG, messageSupplier);
    }

    default void debug(String format, Object... args) {
        log(PulseLogLevel.DEBUG, format, args);
    }

    default void info(String message) {
        log(PulseLogLevel.INFO, message);
    }

    default void info(String format, Object... args) {
        log(PulseLogLevel.INFO, format, args);
    }

    default void warn(String message) {
        log(PulseLogLevel.WARN, message);
    }

    default void warn(String format, Object... args) {
        log(PulseLogLevel.WARN, format, args);
    }

    default void warn(String message, Throwable throwable) {
        log(PulseLogLevel.WARN, message, throwable);
    }

    default void error(String message) {
        log(PulseLogLevel.ERROR, message);
    }

    default void error(String format, Object... args) {
        log(PulseLogLevel.ERROR, format, args);
    }

    default void error(String message, Throwable throwable) {
        log(PulseLogLevel.ERROR, message, throwable);
    }

    // --- 향후 MDC 컨텍스트 확장용 (Phase 1에서는 미구현)---
    // default void setContext(String key, String value) {}
    // default void clearContext() {}
}
