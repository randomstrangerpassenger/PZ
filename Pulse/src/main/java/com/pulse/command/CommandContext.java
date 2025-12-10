package com.pulse.command;

import java.util.*;

/**
 * 명령어 실행 컨텍스트.
 * 명령어 핸들러에 전달되는 정보.
 */
public class CommandContext {

    private final CommandSender sender;
    private final String commandName;
    private final String[] rawArgs;
    private int argIndex = 0;

    public CommandContext(CommandSender sender, String commandName, String[] args) {
        this.sender = sender;
        this.commandName = commandName;
        this.rawArgs = args != null ? args : new String[0];
    }

    // ─────────────────────────────────────────────────────────────
    // 기본 정보
    // ─────────────────────────────────────────────────────────────

    public CommandSender getSender() {
        return sender;
    }

    public String getCommandName() {
        return commandName;
    }

    public String[] getRawArgs() {
        return rawArgs;
    }

    public int getArgCount() {
        return rawArgs.length;
    }

    // ─────────────────────────────────────────────────────────────
    // 인자 접근
    // ─────────────────────────────────────────────────────────────

    /**
     * 인자가 있는지 확인
     */
    public boolean hasArg(int index) {
        return index >= 0 && index < rawArgs.length;
    }

    /**
     * 인덱스로 인자 가져오기
     */
    public String getArg(int index) {
        if (index < 0 || index >= rawArgs.length) {
            return null;
        }
        return rawArgs[index];
    }

    /**
     * 인덱스로 인자 가져오기 (기본값)
     */
    public String getArg(int index, String defaultValue) {
        String arg = getArg(index);
        return arg != null ? arg : defaultValue;
    }

    /**
     * 다음 인자 가져오기
     */
    public String nextArg() {
        if (argIndex >= rawArgs.length) {
            return null;
        }
        return rawArgs[argIndex++];
    }

    /**
     * 다음 인자 가져오기 (기본값)
     */
    public String nextArg(String defaultValue) {
        String arg = nextArg();
        return arg != null ? arg : defaultValue;
    }

    /**
     * 나머지 인자 모두 합치기
     */
    public String getRemainingArgs() {
        if (argIndex >= rawArgs.length) {
            return "";
        }
        return String.join(" ", Arrays.copyOfRange(rawArgs, argIndex, rawArgs.length));
    }

    /**
     * 인덱스 이후 모든 인자 합치기
     */
    public String getArgsFrom(int index) {
        if (index >= rawArgs.length) {
            return "";
        }
        return String.join(" ", Arrays.copyOfRange(rawArgs, index, rawArgs.length));
    }

    // ─────────────────────────────────────────────────────────────
    // 타입 변환
    // ─────────────────────────────────────────────────────────────

    public Integer getInt(int index) {
        String arg = getArg(index);
        if (arg == null)
            return null;
        try {
            return Integer.parseInt(arg);
        } catch (NumberFormatException e) {
            return null;
        }
    }

    public int getInt(int index, int defaultValue) {
        Integer val = getInt(index);
        return val != null ? val : defaultValue;
    }

    public Double getDouble(int index) {
        String arg = getArg(index);
        if (arg == null)
            return null;
        try {
            return Double.parseDouble(arg);
        } catch (NumberFormatException e) {
            return null;
        }
    }

    public double getDouble(int index, double defaultValue) {
        Double val = getDouble(index);
        return val != null ? val : defaultValue;
    }

    public Boolean getBoolean(int index) {
        String arg = getArg(index);
        if (arg == null)
            return null;
        return "true".equalsIgnoreCase(arg) || "yes".equalsIgnoreCase(arg) || "1".equals(arg);
    }

    public boolean getBoolean(int index, boolean defaultValue) {
        Boolean val = getBoolean(index);
        return val != null ? val : defaultValue;
    }

    // ─────────────────────────────────────────────────────────────
    // 응답 헬퍼
    // ─────────────────────────────────────────────────────────────

    public void reply(String message) {
        sender.sendMessage(message);
    }

    public void replyError(String message) {
        sender.sendError(message);
    }

    public void replyFormat(String format, Object... args) {
        sender.sendMessage(String.format(format, args));
    }
}
