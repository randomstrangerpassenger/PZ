package com.pulse.api.log;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.function.Supplier;

/**
 * 모듈별 로거 구현체.
 * 
 * 각 모듈(Pulse, Echo, Fuse, Nerve)에서 독립적인 로그 레벨을 설정할 수 있습니다.
 * 
 * @since 1.1.0
 */
public class ModuleLogger implements PulseLoggerInterface {

    private static final DateTimeFormatter TIME_FORMAT = DateTimeFormatter.ofPattern("HH:mm:ss.SSS");

    private final String moduleName;
    private volatile PulseLogLevel currentLevel;

    /**
     * 모듈 로거 생성.
     * 
     * @param moduleName 모듈 이름 (예: "Pulse", "Echo")
     */
    public ModuleLogger(String moduleName) {
        this(moduleName, PulseLogLevel.INFO);
    }

    /**
     * 모듈 로거 생성 (레벨 지정).
     * 
     * @param moduleName 모듈 이름
     * @param level      초기 로그 레벨
     */
    public ModuleLogger(String moduleName, PulseLogLevel level) {
        this.moduleName = moduleName;
        this.currentLevel = level;
    }

    /**
     * 로그 레벨 설정.
     */
    public void setLevel(PulseLogLevel level) {
        this.currentLevel = level;
    }

    /**
     * 현재 로그 레벨 조회.
     */
    public PulseLogLevel getLevel() {
        return currentLevel;
    }

    @Override
    public boolean isEnabled(PulseLogLevel level) {
        return level.isEnabled(currentLevel);
    }

    @Override
    public void log(PulseLogLevel level, String message) {
        if (!isEnabled(level))
            return;
        output(level, message);
    }

    @Override
    public void log(PulseLogLevel level, Supplier<String> messageSupplier) {
        if (!isEnabled(level))
            return;
        output(level, messageSupplier.get());
    }

    @Override
    public void log(PulseLogLevel level, String format, Object... args) {
        if (!isEnabled(level))
            return;
        output(level, formatMessage(format, args));
    }

    @Override
    public void log(PulseLogLevel level, String message, Throwable throwable) {
        if (!isEnabled(level))
            return;
        output(level, message + "\n" + getStackTrace(throwable));
    }

    private void output(PulseLogLevel level, String message) {
        String timestamp = LocalDateTime.now().format(TIME_FORMAT);
        String formattedMessage = String.format("[%s] [%s/%s] %s",
                timestamp, moduleName, level.name(), message);

        if (level.getLevel() >= PulseLogLevel.WARN.getLevel()) {
            System.err.println(formattedMessage);
        } else {
            System.out.println(formattedMessage);
        }
    }

    /**
     * SLF4J 스타일 {} 플레이스홀더 포맷팅.
     */
    private String formatMessage(String format, Object... args) {
        if (args == null || args.length == 0) {
            return format;
        }

        StringBuilder result = new StringBuilder();
        int argIndex = 0;
        int i = 0;

        while (i < format.length()) {
            if (i < format.length() - 1 && format.charAt(i) == '{' && format.charAt(i + 1) == '}') {
                if (argIndex < args.length) {
                    result.append(args[argIndex++]);
                } else {
                    result.append("{}");
                }
                i += 2;
            } else {
                result.append(format.charAt(i));
                i++;
            }
        }

        return result.toString();
    }

    private String getStackTrace(Throwable throwable) {
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        throwable.printStackTrace(pw);
        return sw.toString();
    }
}
