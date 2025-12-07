package com.pulse.debug;

import com.pulse.mod.ModLoader;
import com.pulse.mod.ModContainer;
import com.pulse.mod.ModReloadManager;
import com.pulse.security.PermissionManager;
import com.pulse.security.PermissionManager.Permission;
import com.pulse.security.SideValidator;

import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.function.Consumer;

/**
 * 인게임 개발자 콘솔.
 * REPL 스타일 디버그 명령어 실행.
 * 
 * <p>
 * <b>멀티플레이어 보안:</b>
 * 서버 환경에서는 위험한 명령어(lua, mods reload/disable/enable)에 대해
 * 관리자 권한 검사를 수행합니다. 권한이 없는 유저는 해당 명령어를 실행할 수 없습니다.
 * </p>
 * 
 * 사용 예:
 * 
 * <pre>
 * DevConsole.execute("mods list");
 * DevConsole.execute("reload mymod");
 * DevConsole.execute("events monitor");
 * </pre>
 */
public class DevConsole {

    private static final DevConsole INSTANCE = new DevConsole();

    /** 위험 명령어 목록 - 서버에서 권한 검사 필요 */
    private static final Set<String> PRIVILEGED_COMMANDS = Set.of("lua");
    private static final Set<String> MOD_MANAGE_SUBCOMMANDS = Set.of("reload", "disable", "enable");

    private final Map<String, ConsoleCommand> commands = new LinkedHashMap<>();
    private final Queue<String> outputBuffer = new ConcurrentLinkedQueue<>();
    private Consumer<String> outputHandler;
    private boolean eventMonitoring = false;

    /** 현재 콘솔 사용자의 권한 (플레이어 ID 또는 "pulse:system") */
    private static String currentExecutor = "pulse:system";
    private static boolean currentExecutorIsAdmin = true;

    private DevConsole() {
        registerDefaultCommands();
    }

    public static DevConsole getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 권한 관리 (멀티플레이어 보안)
    // ─────────────────────────────────────────────────────────────

    /**
     * 현재 콘솔 실행자 설정.
     * 멀티플레이어 서버에서 콘솔 UI 열 때 호출해야 합니다.
     * 
     * @param executorId 플레이어 ID 또는 시스템 ID
     * @param isAdmin    관리자 권한 여부
     */
    public static void setCurrentExecutor(String executorId, boolean isAdmin) {
        currentExecutor = executorId != null ? executorId : "pulse:system";
        currentExecutorIsAdmin = isAdmin;
        System.out.println("[DevConsole] Executor set: " + currentExecutor + " (admin=" + isAdmin + ")");
    }

    /**
     * 현재 실행자가 관리자인지 확인.
     */
    public static boolean isCurrentExecutorAdmin() {
        return currentExecutorIsAdmin;
    }

    /**
     * 시스템 권한으로 리셋 (콘솔 UI 닫을 때 호출).
     */
    public static void resetExecutorToSystem() {
        currentExecutor = "pulse:system";
        currentExecutorIsAdmin = true;
    }

    // ─────────────────────────────────────────────────────────────
    // 명령어 실행
    // ─────────────────────────────────────────────────────────────

    /**
     * 명령어 실행.
     */
    public static String execute(String input) {
        return INSTANCE.executeInternal(input);
    }

    private String executeInternal(String input) {
        if (input == null || input.trim().isEmpty()) {
            return "";
        }

        String[] parts = input.trim().split("\\s+", 2);
        String cmdName = parts[0].toLowerCase();
        String args = parts.length > 1 ? parts[1] : "";

        // ═══════════════════════════════════════════════════════════════
        // 멀티플레이어 보안 검사
        // ═══════════════════════════════════════════════════════════════

        // 1. 서버 환경에서 권한 검사 강화
        if (!SideValidator.isClient()) {
            // 1a. Lua 명령어: CONSOLE_LUA_EXEC 권한 필요
            if (PRIVILEGED_COMMANDS.contains(cmdName)) {
                if (!currentExecutorIsAdmin &&
                        !PermissionManager.hasPermission(currentExecutor, Permission.CONSOLE_LUA_EXEC)) {
                    System.err.println("[DevConsole] BLOCKED: User '" + currentExecutor +
                            "' attempted privileged command: " + cmdName);
                    return "§c[보안] 권한 부족: '" + cmdName + "' 명령어는 관리자만 사용할 수 있습니다.";
                }
            }

            // 1b. 모드 관리 명령어: CONSOLE_MOD_MANAGE 권한 필요
            if ("mods".equals(cmdName) && args.length() > 0) {
                String subCmd = args.split("\\s+")[0].toLowerCase();
                if (MOD_MANAGE_SUBCOMMANDS.contains(subCmd)) {
                    if (!currentExecutorIsAdmin &&
                            !PermissionManager.hasPermission(currentExecutor, Permission.CONSOLE_MOD_MANAGE)) {
                        System.err.println("[DevConsole] BLOCKED: User '" + currentExecutor +
                                "' attempted mod management: mods " + subCmd);
                        return "§c[보안] 권한 부족: 'mods " + subCmd + "'는 관리자만 사용할 수 있습니다.";
                    }
                }
            }
        }
        // ═══════════════════════════════════════════════════════════════

        ConsoleCommand cmd = commands.get(cmdName);
        if (cmd == null) {
            return "Unknown command: " + cmdName + ". Type 'help' for available commands.";
        }

        try {
            return cmd.execute(args);
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 기본 명령어 등록
    // ─────────────────────────────────────────────────────────────

    private void registerDefaultCommands() {
        // help
        register("help", "Show available commands", args -> {
            StringBuilder sb = new StringBuilder("Available commands:\n");
            for (var entry : commands.entrySet()) {
                sb.append("  ").append(entry.getKey())
                        .append(" - ").append(entry.getValue().getDescription())
                        .append("\n");
            }
            return sb.toString();
        });

        // mods
        register("mods", "Mod management (list/info/reload/disable/enable)", args -> {
            String[] parts = args.split("\\s+", 2);
            String subCmd = parts.length > 0 ? parts[0] : "list";
            String modId = parts.length > 1 ? parts[1] : null;

            switch (subCmd) {
                case "list":
                    return listMods();
                case "info":
                    return modInfo(modId);
                case "reload":
                    return reloadMod(modId);
                case "disable":
                    return disableMod(modId);
                case "enable":
                    return enableMod(modId);
                default:
                    return "Usage: mods [list|info|reload|disable|enable] [modId]";
            }
        });

        // events
        register("events", "Event system (monitor/stats)", args -> {
            if (args.startsWith("monitor")) {
                eventMonitoring = !eventMonitoring;
                return "Event monitoring: " + (eventMonitoring ? "ON" : "OFF");
            }
            return "Usage: events [monitor|stats]";
        });

        // clear
        register("clear", "Clear output buffer", args -> {
            outputBuffer.clear();
            return "Output cleared.";
        });

        // lua
        register("lua", "Execute Lua code", args -> {
            try {
                Object result = com.pulse.lua.LuaBridge.call(args);
                return result != null ? result.toString() : "nil";
            } catch (Exception e) {
                return "Lua error: " + e.getMessage();
            }
        });
    }

    private String listMods() {
        StringBuilder sb = new StringBuilder("Loaded mods:\n");
        ModLoader loader = ModLoader.getInstance();
        for (String modId : loader.getLoadedModIds()) {
            ModContainer mod = loader.getMod(modId);
            String status = ModReloadManager.isEnabled(modId) ? "✓" : "✗";
            sb.append("  [").append(status).append("] ")
                    .append(modId).append(" v").append(mod.getMetadata().getVersion())
                    .append("\n");
        }
        return sb.toString();
    }

    private String modInfo(String modId) {
        if (modId == null)
            return "Usage: mods info <modId>";
        ModContainer mod = ModLoader.getInstance().getMod(modId);
        if (mod == null)
            return "Mod not found: " + modId;

        var meta = mod.getMetadata();
        return String.format(
                "=== %s ===\n" +
                        "ID: %s\n" +
                        "Version: %s\n" +
                        "Author: %s\n" +
                        "Description: %s\n" +
                        "State: %s\n",
                meta.getName(), meta.getId(), meta.getVersion(),
                meta.getAuthor(), meta.getDescription(), mod.getState());
    }

    private String reloadMod(String modId) {
        if (modId == null)
            return "Usage: mods reload <modId>";
        boolean success = ModReloadManager.softReload(modId);
        return success ? "Reloaded: " + modId : "Failed to reload: " + modId;
    }

    private String disableMod(String modId) {
        if (modId == null)
            return "Usage: mods disable <modId>";
        boolean success = ModReloadManager.disable(modId);
        return success ? "Disabled: " + modId : "Failed to disable: " + modId;
    }

    private String enableMod(String modId) {
        if (modId == null)
            return "Usage: mods enable <modId>";
        boolean success = ModReloadManager.enable(modId);
        return success ? "Enabled: " + modId : "Failed to enable: " + modId;
    }

    // ─────────────────────────────────────────────────────────────
    // 명령어 등록 API
    // ─────────────────────────────────────────────────────────────

    /**
     * 커스텀 명령어 등록.
     */
    public static void register(String name, String description, CommandExecutor executor) {
        INSTANCE.commands.put(name.toLowerCase(), new ConsoleCommand(description, executor));
    }

    /**
     * 출력 핸들러 설정 (UI 연동용).
     */
    public static void setOutputHandler(Consumer<String> handler) {
        INSTANCE.outputHandler = handler;
    }

    /**
     * 콘솔에 출력.
     */
    public static void print(String message) {
        INSTANCE.outputBuffer.offer(message);
        if (INSTANCE.outputHandler != null) {
            INSTANCE.outputHandler.accept(message);
        }
        System.out.println("[DevConsole] " + message);
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스
    // ─────────────────────────────────────────────────────────────

    @FunctionalInterface
    public interface CommandExecutor {
        String execute(String args);
    }

    private static class ConsoleCommand {
        private final String description;
        private final CommandExecutor executor;

        ConsoleCommand(String description, CommandExecutor executor) {
            this.description = description;
            this.executor = executor;
        }

        String getDescription() {
            return description;
        }

        String execute(String args) {
            return executor.execute(args);
        }
    }
}
