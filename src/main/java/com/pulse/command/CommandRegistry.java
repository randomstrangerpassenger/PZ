package com.pulse.command;

import java.lang.reflect.Method;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 명령어 레지스트리.
 * 모든 명령어를 등록하고 실행을 관리.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 어노테이션 기반 등록
 * CommandRegistry.register(new MyCommands());
 * 
 * // 람다 기반 등록
 * CommandRegistry.register("hello", ctx -> {
 *     ctx.reply("Hello, " + ctx.getSender().getName() + "!");
 * });
 * 
 * // 명령어 실행 (채팅 훅에서 호출)
 * CommandRegistry.execute(sender, "/hello world");
 * </pre>
 */
public class CommandRegistry {

    private static final CommandRegistry INSTANCE = new CommandRegistry();

    // 등록된 명령어
    private final Map<String, RegisteredCommand> commands = new ConcurrentHashMap<>();

    // 명령어 접두사
    private String prefix = "/";

    private CommandRegistry() {
    }

    public static CommandRegistry getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 정적 편의 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * 어노테이션 기반 명령어 클래스 등록
     */
    public static void register(Object commandHandler) {
        INSTANCE.registerHandler(commandHandler);
    }

    /**
     * 람다 기반 명령어 등록
     */
    public static void register(String name, CommandExecutor executor) {
        INSTANCE.registerCommand(name, executor);
    }

    /**
     * 람다 기반 명령어 등록 (설명 포함)
     */
    public static void register(String name, String description, CommandExecutor executor) {
        INSTANCE.registerCommand(name, description, executor);
    }

    /**
     * 명령어 실행
     * 
     * @return true if command was found and executed
     */
    public static boolean execute(CommandSender sender, String input) {
        return INSTANCE.executeCommand(sender, input);
    }

    /**
     * 모든 명령어 가져오기
     */
    public static Collection<RegisteredCommand> getAll() {
        return INSTANCE.getAllCommands();
    }

    // ─────────────────────────────────────────────────────────────
    // 인스턴스 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * 어노테이션 기반 핸들러 등록
     */
    public void registerHandler(Object handler) {
        Class<?> clazz = handler.getClass();

        for (Method method : clazz.getDeclaredMethods()) {
            Command annotation = method.getAnnotation(Command.class);
            if (annotation == null)
                continue;

            method.setAccessible(true);

            RegisteredCommand cmd = new RegisteredCommand(
                    annotation.name(),
                    annotation.description(),
                    annotation.usage(),
                    annotation.aliases(),
                    annotation.permission(),
                    annotation.playerOnly(),
                    annotation.consoleOnly(),
                    handler,
                    method);

            registerInternal(cmd);
        }
    }

    /**
     * 람다 기반 등록
     */
    public void registerCommand(String name, CommandExecutor executor) {
        registerCommand(name, "", executor);
    }

    public void registerCommand(String name, String description, CommandExecutor executor) {
        RegisteredCommand cmd = new RegisteredCommand(
                name, description, "", new String[0], "", false, false, executor, null);
        registerInternal(cmd);
    }

    private void registerInternal(RegisteredCommand cmd) {
        commands.put(cmd.getName().toLowerCase(), cmd);

        // 별칭 등록
        for (String alias : cmd.getAliases()) {
            commands.put(alias.toLowerCase(), cmd);
        }

        System.out.println("[Pulse/CMD] Registered command: /" + cmd.getName());
    }

    /**
     * 명령어 실행
     */
    public boolean executeCommand(CommandSender sender, String input) {
        // 접두사 확인
        if (!input.startsWith(prefix)) {
            return false;
        }

        // 파싱
        String withoutPrefix = input.substring(prefix.length()).trim();
        if (withoutPrefix.isEmpty()) {
            return false;
        }

        String[] parts = withoutPrefix.split("\\s+", 2);
        String cmdName = parts[0].toLowerCase();
        String[] args = parts.length > 1 ? parts[1].split("\\s+") : new String[0];

        // 명령어 찾기
        RegisteredCommand cmd = commands.get(cmdName);
        if (cmd == null) {
            return false;
        }

        // 권한 확인
        if (!cmd.getPermission().isEmpty() && !sender.hasPermission(cmd.getPermission())) {
            sender.sendError("You don't have permission to use this command.");
            return true;
        }

        // 플레이어 전용 확인
        if (cmd.isPlayerOnly() && !sender.isPlayer()) {
            sender.sendError("This command can only be used by players.");
            return true;
        }

        // 콘솔 전용 확인
        if (cmd.isConsoleOnly() && !sender.isConsole()) {
            sender.sendError("This command can only be used from console.");
            return true;
        }

        // 실행
        try {
            CommandContext ctx = new CommandContext(sender, cmdName, args);
            cmd.execute(ctx);
        } catch (Exception e) {
            sender.sendError("Error executing command: " + e.getMessage());
            e.printStackTrace();
        }

        return true;
    }

    public RegisteredCommand getCommand(String name) {
        return commands.get(name.toLowerCase());
    }

    public Collection<RegisteredCommand> getAllCommands() {
        // 중복 제거 (별칭으로 인해)
        return new HashSet<>(commands.values());
    }

    public void setPrefix(String prefix) {
        this.prefix = prefix;
    }

    public String getPrefix() {
        return prefix;
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스
    // ─────────────────────────────────────────────────────────────

    @FunctionalInterface
    public interface CommandExecutor {
        void execute(CommandContext ctx);
    }

    public static class RegisteredCommand {
        private final String name;
        private final String description;
        private final String usage;
        private final String[] aliases;
        private final String permission;
        private final boolean playerOnly;
        private final boolean consoleOnly;
        private final Object handler; // 어노테이션 기반
        private final Method method; // 어노테이션 기반
        private final CommandExecutor executor; // 람다 기반

        public RegisteredCommand(String name, String description, String usage,
                String[] aliases, String permission,
                boolean playerOnly, boolean consoleOnly,
                Object handler, Method method) {
            this.name = name;
            this.description = description;
            this.usage = usage;
            this.aliases = aliases;
            this.permission = permission;
            this.playerOnly = playerOnly;
            this.consoleOnly = consoleOnly;

            if (handler instanceof CommandExecutor exec) {
                this.handler = null;
                this.method = null;
                this.executor = exec;
            } else {
                this.handler = handler;
                this.method = method;
                this.executor = null;
            }
        }

        public void execute(CommandContext ctx) throws Exception {
            if (executor != null) {
                executor.execute(ctx);
            } else if (method != null && handler != null) {
                method.invoke(handler, ctx);
            }
        }

        // Getters
        public String getName() {
            return name;
        }

        public String getDescription() {
            return description;
        }

        public String getUsage() {
            return usage.isEmpty() ? "/" + name : usage;
        }

        public String[] getAliases() {
            return aliases;
        }

        public String getPermission() {
            return permission;
        }

        public boolean isPlayerOnly() {
            return playerOnly;
        }

        public boolean isConsoleOnly() {
            return consoleOnly;
        }
    }
}
