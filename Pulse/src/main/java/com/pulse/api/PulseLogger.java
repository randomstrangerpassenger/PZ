package com.pulse.api;

import com.pulse.debug.CrashReporter;

/**
 * Pulse 통합 로거.
 * 모든 Pulse 모드에서 일관된 로깅 API를 제공합니다.
 * 
 * <pre>
 * // 사용 예시
 * PulseLogger.info("mymod", "Initialized successfully");
 * PulseLogger.warn("mymod", "Config not found, using defaults");
 * PulseLogger.error("mymod", "Critical error occurred", exception);
 * </pre>
 * 
 * @since 1.1.0
 */
@PublicAPI(since = "1.1.0")
public final class PulseLogger {

    private PulseLogger() {
    } // 인스턴스화 방지

    // ═══════════════════════════════════════════════════════════════
    // 기본 로깅
    // ═══════════════════════════════════════════════════════════════

    /**
     * 정보 로그.
     * 
     * @param modId   모드 ID
     * @param message 메시지
     */
    public static void info(String modId, String message) {
        String formatted = formatLog(modId, "INFO", message);
        System.out.println(formatted);
        CrashReporter.addLogLine(formatted);
    }

    /**
     * 경고 로그.
     * 
     * @param modId   모드 ID
     * @param message 메시지
     */
    public static void warn(String modId, String message) {
        String formatted = formatLog(modId, "WARN", message);
        System.out.println(formatted);
        CrashReporter.addLogLine(formatted);
    }

    /**
     * 에러 로그.
     * 
     * @param modId   모드 ID
     * @param message 메시지
     */
    public static void error(String modId, String message) {
        String formatted = formatLog(modId, "ERROR", message);
        System.err.println(formatted);
        CrashReporter.addLogLine(formatted);
    }

    /**
     * 에러 로그 (예외 포함).
     * 
     * @param modId   모드 ID
     * @param message 메시지
     * @param t       예외
     */
    public static void error(String modId, String message, Throwable t) {
        String formatted = formatLog(modId, "ERROR", message);
        System.err.println(formatted);
        CrashReporter.addLogLine(formatted);

        if (t != null) {
            CrashReporter.addLogLine("  Exception: " + t.getClass().getName() + ": " + t.getMessage());
            if (DevMode.isEnabled()) {
                t.printStackTrace();
            }
        }
    }

    /**
     * 디버그 로그 (DevMode에서만 출력).
     * 
     * @param modId   모드 ID
     * @param message 메시지
     */
    public static void debug(String modId, String message) {
        if (!DevMode.isEnabled()) {
            return;
        }

        String formatted = formatLog(modId, "DEBUG", message);
        System.out.println(formatted);
        CrashReporter.addLogLine(formatted);
    }

    // ═══════════════════════════════════════════════════════════════
    // 구조화된 이벤트 로깅 (CrashReporter 연동)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 구조화된 이벤트 기록.
     * CrashReporter에 이벤트로 기록됨.
     * 
     * @param eventType 이벤트 타입
     * @param source    발생 소스
     * @param message   메시지
     */
    public static void event(String eventType, String source, String message) {
        CrashReporter.recordEvent(eventType, source, message);
    }

    /**
     * Mixin 실패 이벤트 기록.
     * 
     * @param mixinClass  Mixin 클래스
     * @param targetClass 대상 클래스
     * @param error       오류 메시지
     */
    public static void mixinFailed(String mixinClass, String targetClass, String error) {
        CrashReporter.recordEvent(
                CrashReporter.EVENT_MIXIN_FAILURE,
                mixinClass,
                "Target: " + targetClass + ", Error: " + error);
    }

    /**
     * Lua 예산 초과 이벤트 기록.
     * 
     * @param contextId    컨텍스트 ID
     * @param actualMicros 실제 사용 시간
     * @param budgetMicros 예산 시간
     */
    public static void luaBudgetExceeded(String contextId, long actualMicros, long budgetMicros) {
        double actualMs = actualMicros / 1000.0;
        double budgetMs = budgetMicros / 1000.0;

        CrashReporter.recordEvent(
                CrashReporter.EVENT_LUA_BUDGET_EXCEEDED,
                contextId,
                String.format("%.2fms / %.2fms", actualMs, budgetMs));
    }

    // ═══════════════════════════════════════════════════════════════
    // 내부 헬퍼
    // ═══════════════════════════════════════════════════════════════

    private static String formatLog(String modId, String level, String message) {
        return String.format("[%s/%s] %s", modId, level, message);
    }

    /**
     * Pulse 기본 로거 (modId = "Pulse").
     * 
     * @param message 메시지
     */
    public static void pulse(String message) {
        info("Pulse", message);
    }

    /**
     * Pulse 경고 (modId = "Pulse").
     * 
     * @param message 메시지
     */
    public static void pulseWarn(String message) {
        warn("Pulse", message);
    }

    /**
     * Pulse 에러 (modId = "Pulse").
     * 
     * @param message 메시지
     * @param t       예외
     */
    public static void pulseError(String message, Throwable t) {
        error("Pulse", message, t);
    }
}
