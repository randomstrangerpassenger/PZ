package com.pulse.api;

import java.io.PrintStream;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Pulse 로깅 API.
 * 
 * 모드에서 일관된 로그 형식을 사용할 수 있도록 합니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * PulseLog.info("MyMod", "Initialization complete");
 * PulseLog.warn("MyMod", "Config file not found, using defaults");
 * PulseLog.error("MyMod", "Failed to load", exception);
 * }</pre>
 * 
 * @since Pulse 1.2
 */
public final class PulseLog {

    private static final DateTimeFormatter TIME_FORMAT = DateTimeFormatter.ofPattern("HH:mm:ss");

    private static volatile boolean includeTimestamp = true;
    private static volatile boolean debugEnabled = false;
    private static PrintStream out = System.out;
    private static PrintStream err = System.err;

    private PulseLog() {
    }

    /**
     * INFO 레벨 로그
     */
    public static void info(String tag, String message) {
        log("INFO", tag, message);
    }

    /**
     * 포맷 문자열을 사용한 INFO 로그
     */
    public static void info(String tag, String format, Object... args) {
        log("INFO", tag, String.format(format, args));
    }

    /**
     * DEBUG 레벨 로그 (debugEnabled = true일 때만 출력)
     */
    public static void debug(String tag, String message) {
        if (debugEnabled) {
            log("DEBUG", tag, message);
        }
    }

    /**
     * DEBUG 로그 (포맷)
     */
    public static void debug(String tag, String format, Object... args) {
        if (debugEnabled) {
            log("DEBUG", tag, String.format(format, args));
        }
    }

    /**
     * WARN 레벨 로그
     */
    public static void warn(String tag, String message) {
        log("WARN", tag, message);
    }

    /**
     * WARN 로그 (포맷)
     */
    public static void warn(String tag, String format, Object... args) {
        log("WARN", tag, String.format(format, args));
    }

    /**
     * ERROR 레벨 로그
     */
    public static void error(String tag, String message) {
        logError("ERROR", tag, message, null);
    }

    /**
     * ERROR 로그 (예외 포함)
     */
    public static void error(String tag, String message, Throwable t) {
        logError("ERROR", tag, message, t);
    }

    /**
     * ERROR 로그 (포맷)
     */
    public static void error(String tag, String format, Object... args) {
        logError("ERROR", tag, String.format(format, args), null);
    }

    // ─────────────────────────────────────────────────────────────
    // 설정
    // ─────────────────────────────────────────────────────────────

    /**
     * 디버그 로그 활성화
     */
    public static void setDebugEnabled(boolean enabled) {
        debugEnabled = enabled;
    }

    /**
     * 타임스탬프 포함 여부
     */
    public static void setIncludeTimestamp(boolean include) {
        includeTimestamp = include;
    }

    /**
     * 출력 스트림 변경
     */
    public static void setOutput(PrintStream out, PrintStream err) {
        PulseLog.out = out != null ? out : System.out;
        PulseLog.err = err != null ? err : System.err;
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 구현
    // ─────────────────────────────────────────────────────────────

    private static void log(String level, String tag, String message) {
        String formatted = formatMessage(level, tag, message);
        out.println(formatted);
    }

    private static void logError(String level, String tag, String message, Throwable t) {
        String formatted = formatMessage(level, tag, message);
        err.println(formatted);
        if (t != null) {
            t.printStackTrace(err);
        }
    }

    private static String formatMessage(String level, String tag, String message) {
        StringBuilder sb = new StringBuilder();

        if (includeTimestamp) {
            sb.append("[").append(LocalDateTime.now().format(TIME_FORMAT)).append("] ");
        }

        sb.append("[").append(level).append("] ");
        sb.append("[").append(tag).append("] ");
        sb.append(message);

        return sb.toString();
    }
}
