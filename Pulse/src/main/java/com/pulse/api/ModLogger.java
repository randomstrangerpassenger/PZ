package com.pulse.api;

import com.pulse.api.log.PulseLogger;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 모드별 로거.
 * 각 모드는 자신만의 로거를 사용하여 [Mod/{modId}] prefix로 로그 출력.
 * 
 * 사용 예:
 * ModLogger logger = ModLogger.getLogger("mymod");
 * logger.info("Mod initialized!");
 * // 출력: [Mod/mymod] Mod initialized!
 */
public class ModLogger {

    private static final Map<String, ModLogger> LOGGERS = new ConcurrentHashMap<>();

    private final String modId;
    private final String prefix;

    private ModLogger(String modId) {
        this.modId = modId;
        this.prefix = "Mod/" + modId;
    }

    // ─────────────────────────────────────────────────────────────
    // 팩토리 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드별 로거 가져오기 (캐싱됨)
     */
    public static ModLogger getLogger(String modId) {
        return LOGGERS.computeIfAbsent(modId, ModLogger::new);
    }

    // ─────────────────────────────────────────────────────────────
    // 로깅 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * INFO 레벨 로그
     */
    public void info(String message) {
        PulseLogger.info(prefix, message);
    }

    /**
     * INFO 레벨 로그 (포맷팅)
     */
    public void info(String format, Object... args) {
        PulseLogger.info(prefix, String.format(format, args));
    }

    /**
     * DEBUG 레벨 로그 (DevMode일 때만)
     */
    public void debug(String message) {
        if (DevMode.isEnabled()) {
            PulseLogger.debug(prefix, message);
        }
    }

    /**
     * DEBUG 레벨 로그 (포맷팅, DevMode일 때만)
     */
    public void debug(String format, Object... args) {
        if (DevMode.isEnabled()) {
            PulseLogger.debug(prefix, String.format(format, args));
        }
    }

    /**
     * WARN 레벨 로그
     */
    public void warn(String message) {
        PulseLogger.warn(prefix, message);
    }

    /**
     * WARN 레벨 로그 (포맷팅)
     */
    public void warn(String format, Object... args) {
        PulseLogger.warn(prefix, String.format(format, args));
    }

    /**
     * ERROR 레벨 로그
     */
    public void error(String message) {
        PulseLogger.error(prefix, message);
    }

    /**
     * ERROR 레벨 로그 (예외 포함)
     */
    public void error(String message, Throwable t) {
        PulseLogger.error(prefix, message, t);
    }

    /**
     * ERROR 레벨 로그 (포맷팅)
     */
    public void error(String format, Object... args) {
        PulseLogger.error(prefix, String.format(format, args));
    }

    // ─────────────────────────────────────────────────────────────
    // Getters
    // ─────────────────────────────────────────────────────────────

    public String getModId() {
        return modId;
    }

    public String getPrefix() {
        return prefix;
    }
}
