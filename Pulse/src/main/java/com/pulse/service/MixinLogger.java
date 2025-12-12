package com.pulse.service;

import com.pulse.api.log.PulseLogger;
import org.spongepowered.asm.logging.ILogger;
import org.spongepowered.asm.logging.Level;

/**
 * Pulse용 Mixin ILogger 구현.
 * Sponge Mixin이 필요로 하는 ILogger 인터페이스 구현체.
 * 
 * Note: com.pulse.api.log.PulseLogger와 구분을 위해 MixinLogger로 명명.
 */
public class MixinLogger implements ILogger {
    private static final String LOG = PulseLogger.PULSE;
    private final String name;

    public MixinLogger(String name) {
        this.name = name;
    }

    @Override
    public String getId() {
        return this.name;
    }

    @Override
    public String getType() {
        return "Pulse";
    }

    public String getName() {
        return this.name;
    }

    private String format(String level, String message, Object... params) {
        String formatted = message;
        if (params != null && params.length > 0) {
            // 간단한 {} 치환
            for (Object param : params) {
                int idx = formatted.indexOf("{}");
                if (idx >= 0) {
                    formatted = formatted.substring(0, idx) + param + formatted.substring(idx + 2);
                }
            }
        }
        return String.format("[Mixin/%s] [%s] %s", level, name, formatted);
    }

    @Override
    public void debug(String message, Object... params) {
        PulseLogger.debug(LOG, format("DEBUG", message, params));
    }

    @Override
    public void debug(String message, Throwable t) {
        PulseLogger.debug(LOG, format("DEBUG", message), t);
    }

    @Override
    public void trace(String message, Object... params) {
        PulseLogger.trace(LOG, format("TRACE", message, params));
    }

    @Override
    public void trace(String message, Throwable t) {
        PulseLogger.trace(LOG, format("TRACE", message), t);
    }

    @Override
    public void info(String message, Object... params) {
        PulseLogger.info(LOG, format("INFO", message, params));
    }

    @Override
    public void info(String message, Throwable t) {
        PulseLogger.info(LOG, format("INFO", message), t);
    }

    @Override
    public void warn(String message, Object... params) {
        PulseLogger.warn(LOG, format("WARN", message, params));
    }

    @Override
    public void warn(String message, Throwable t) {
        PulseLogger.warn(LOG, format("WARN", message), t);
    }

    @Override
    public void error(String message, Object... params) {
        PulseLogger.error(LOG, format("ERROR", message, params));
    }

    @Override
    public void error(String message, Throwable t) {
        PulseLogger.error(LOG, format("ERROR", message), t);
    }

    @Override
    public void fatal(String message, Object... params) {
        PulseLogger.error(LOG, format("FATAL", message, params));
    }

    @Override
    public void fatal(String message, Throwable t) {
        PulseLogger.error(LOG, format("FATAL", message), t);
    }

    @Override
    public void log(Level level, String message, Object... params) {
        switch (level) {
            case DEBUG:
                debug(message, params);
                break;
            case TRACE:
                trace(message, params);
                break;
            case INFO:
                info(message, params);
                break;
            case WARN:
                warn(message, params);
                break;
            case ERROR:
                error(message, params);
                break;
            case FATAL:
                fatal(message, params);
                break;
            default:
                info(message, params);
        }
    }

    @Override
    public void log(Level level, String message, Throwable t) {
        switch (level) {
            case DEBUG:
                debug(message, t);
                break;
            case TRACE:
                trace(message, t);
                break;
            case INFO:
                info(message, t);
                break;
            case WARN:
                warn(message, t);
                break;
            case ERROR:
                error(message, t);
                break;
            case FATAL:
                fatal(message, t);
                break;
            default:
                info(message, t);
        }
    }

    @Override
    public <T extends Throwable> T throwing(T t) {
        error("Throwing", t);
        return t;
    }

    @Override
    public void catching(Throwable t) {
        catching(Level.ERROR, t);
    }

    @Override
    public void catching(Level level, Throwable t) {
        log(level, "Catching exception: " + t.getClass().getName(), t);
    }
}
