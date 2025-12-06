package com.pulse.service;

import org.spongepowered.asm.logging.ILogger;
import org.spongepowered.asm.logging.Level;

/**
 * Pulse용 Mixin 로거 구현.
 */
public class PulseLogger implements ILogger {
    private final String name;

    public PulseLogger(String name) {
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
        return String.format("[Pulse/%s] [%s] %s", level, name, formatted);
    }

    @Override
    public void debug(String message, Object... params) {
        System.out.println(format("DEBUG", message, params));
    }

    @Override
    public void debug(String message, Throwable t) {
        System.out.println(format("DEBUG", message));
        t.printStackTrace(System.out);
    }

    @Override
    public void trace(String message, Object... params) {
        // Trace 레벨은 더 상세한 디버깅용
        System.out.println(format("TRACE", message, params));
    }

    @Override
    public void trace(String message, Throwable t) {
        System.out.println(format("TRACE", message));
        t.printStackTrace(System.out);
    }

    @Override
    public void info(String message, Object... params) {
        System.out.println(format("INFO", message, params));
    }

    @Override
    public void info(String message, Throwable t) {
        System.out.println(format("INFO", message));
        t.printStackTrace(System.out);
    }

    @Override
    public void warn(String message, Object... params) {
        System.out.println(format("WARN", message, params));
    }

    @Override
    public void warn(String message, Throwable t) {
        System.out.println(format("WARN", message));
        t.printStackTrace(System.out);
    }

    @Override
    public void error(String message, Object... params) {
        System.err.println(format("ERROR", message, params));
    }

    @Override
    public void error(String message, Throwable t) {
        System.err.println(format("ERROR", message));
        t.printStackTrace(System.err);
    }

    @Override
    public void fatal(String message, Object... params) {
        System.err.println(format("FATAL", message, params));
    }

    @Override
    public void fatal(String message, Throwable t) {
        System.err.println(format("FATAL", message));
        t.printStackTrace(System.err);
    }

    @Override
    public void log(Level level, String message, Object... params) {
        switch (level) {
            case DEBUG: debug(message, params); break;
            case TRACE: trace(message, params); break;
            case INFO: info(message, params); break;
            case WARN: warn(message, params); break;
            case ERROR: error(message, params); break;
            case FATAL: fatal(message, params); break;
            default: info(message, params);
        }
    }

    @Override
    public void log(Level level, String message, Throwable t) {
        switch (level) {
            case DEBUG: debug(message, t); break;
            case TRACE: trace(message, t); break;
            case INFO: info(message, t); break;
            case WARN: warn(message, t); break;
            case ERROR: error(message, t); break;
            case FATAL: fatal(message, t); break;
            default: info(message, t);
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
