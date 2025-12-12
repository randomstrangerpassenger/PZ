package com.pulse.api;

import com.pulse.debug.CrashReporter;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Pulse 통합 로거.
 * 모든 Pulse 모드에서 일관된 로깅 API를 제공합니다.
 * 
 * <pre>
 * // 사용 예시
 * PulseLogger.info("mymod", "Initialized successfully");
 * PulseLogger.warn("mymod", "Config not found, using defaults");
 * PulseLogger.error("mymod", "Critical error occurred", exception);
 * 
 * // Rate Limiting (v1.1.0)
 * PulseLogger.infoRateLimited("tick_log", "Processing tick", 5000);
 * </pre>
 * 
 * @since 1.1.0
 */
@PublicAPI(since = "1.1.0")
public final class PulseLogger {

    private PulseLogger() {
    } // 인스턴스화 방지

    // ═══════════════════════════════════════════════════════════════
    // 로그 레벨 제어 (v1.1.0)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 로그 레벨.
     */
    public enum LogLevel {
        TRACE(0), DEBUG(1), INFO(2), WARN(3), ERROR(4), OFF(5);

        public final int priority;

        LogLevel(int priority) {
            this.priority = priority;
        }
    }

    private static volatile LogLevel currentLevel = LogLevel.INFO;

    /**
     * 현재 로그 레벨 설정.
     * 
     * @param level 로그 레벨
     */
    public static void setLevel(LogLevel level) {
        currentLevel = level;
        info("Pulse", "Log level set to: " + level.name());
    }

    /**
     * 현재 로그 레벨 조회.
     */
    public static LogLevel getLevel() {
        return currentLevel;
    }

    private static boolean shouldLog(LogLevel level) {
        return level.priority >= currentLevel.priority;
    }

    // ═══════════════════════════════════════════════════════════════
    // Rate Limiting (v1.1.0)
    // ═══════════════════════════════════════════════════════════════

    private static final Map<String, Long> lastLogTime = new ConcurrentHashMap<>();
    private static final long CLEANUP_THRESHOLD_MS = 60_000; // 1분

    /**
     * Rate Limited 정보 로그.
     * 지정된 간격 내에는 동일 태그의 로그가 무시됩니다.
     * 
     * @param tag        로그 태그 (중복 방지 키)
     * @param message    메시지
     * @param intervalMs 최소 로그 간격 (밀리초)
     */
    public static void infoRateLimited(String tag, String message, long intervalMs) {
        long now = System.currentTimeMillis();

        // 주기적 정리 (1% 확률)
        if (ThreadLocalRandom.current().nextInt(100) == 0) {
            lastLogTime.entrySet().removeIf(e -> now - e.getValue() > CLEANUP_THRESHOLD_MS);
        }

        Long last = lastLogTime.get(tag);
        if (last == null || now - last >= intervalMs) {
            lastLogTime.put(tag, now);
            info("Pulse", message);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 기본 로깅
    // ═══════════════════════════════════════════════════════════════

    /**
     * 트레이스 로그 (가장 상세한 레벨).
     * 
     * @param modId   모드 ID
     * @param message 메시지
     */
    public static void trace(String modId, String message) {
        if (!shouldLog(LogLevel.TRACE))
            return;
        String formatted = formatLog(modId, "TRACE", message);
        System.out.println(formatted);
        CrashReporter.addLogLine(formatted);
    }

    /**
     * 정보 로그.
     * 
     * @param modId   모드 ID
     * @param message 메시지
     */
    public static void info(String modId, String message) {
        if (!shouldLog(LogLevel.INFO))
            return;
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
        if (!shouldLog(LogLevel.WARN))
            return;
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
        if (!shouldLog(LogLevel.DEBUG))
            return;
        if (!DevMode.isEnabled())
            return;

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
