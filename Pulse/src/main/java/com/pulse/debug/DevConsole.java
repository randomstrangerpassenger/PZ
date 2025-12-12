package com.pulse.debug;

import com.pulse.mod.ModLoader;
import com.pulse.mod.ModContainer;
import com.pulse.mod.ModReloadManager;
import com.pulse.api.log.PulseLogger;

import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.function.Consumer;

/**
 * 인게임 개발자 콘솔.
 * REPL 스타일 디버그 명령어 실행.
 * 
 * <p>
 * <b>멀티플레이어 보안:</b>
 * PermissionValidator를 통해 관리자 권한을 엄격하게 검사합니다.
 * </p>
 */
public class DevConsole {

    private static final DevConsole INSTANCE = new DevConsole();
    private static final String LOG = PulseLogger.PULSE;

    private final Map<String, ConsoleCommand> commands = new LinkedHashMap<>();
    private final Queue<String> outputBuffer = new ConcurrentLinkedQueue<>();
    private Consumer<String> outputHandler;
    private boolean eventMonitoring = false;

    private DevConsole() {
        registerDefaultCommands();
    }

    public static DevConsole getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 권한 관리 (Delegated to PermissionValidator)
    // ─────────────────────────────────────────────────────────────

    public static void setCurrentExecutor(String executorId, boolean isAdmin) {
        PermissionValidator.getInstance().setCurrentExecutor(executorId, isAdmin);
    }

    public static boolean isCurrentExecutorAdmin() {
        return PermissionValidator.getInstance().isCurrentExecutorAdmin();
    }

    public static void resetExecutorToSystem() {
        PermissionValidator.getInstance().resetExecutorToSystem();
    }

    public static void setDebugMode(boolean enabled) {
        PermissionValidator.getInstance().setDebugMode(enabled);
    }

    public static boolean isDebugModeEnabled() {
        return PermissionValidator.getInstance().isDebugModeEnabled();
    }

    public static void onMultiplayerSessionStart() {
        PermissionValidator.getInstance().onMultiplayerSessionStart();
    }

    public static void onMultiplayerSessionEnd() {
        PermissionValidator.getInstance().onMultiplayerSessionEnd();
    }

    public static boolean isInMultiplayerSession() {
        return PermissionValidator.getInstance().isInMultiplayerSession();
    }

    // ─────────────────────────────────────────────────────────────
    // 명령어 실행
    // ─────────────────────────────────────────────────────────────

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

        // 보안 검사 위임
        String error = PermissionValidator.getInstance().validateCommand(cmdName, args);
        if (error != null) {
            return error;
        }

        ConsoleCommand cmd = commands.get(cmdName);
        if (cmd == null) {
            return "Unknown command: " + cmdName + ". Type 'help' for available commands.";
        }

        try {
            return cmd.execute(args);
        } catch (Exception e) {
            PulseLogger.error(LOG, "Command execution failed: " + cmdName, e);
            return "Error: " + e.getMessage();
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 기본 명령어 등록
    // ─────────────────────────────────────────────────────────────

    private void registerDefaultCommands() {
        // help
        registerCommand("help", "Show available commands", args -> {
            StringBuilder sb = new StringBuilder("Available commands:\n");
            for (var entry : commands.entrySet()) {
                sb.append("  ").append(entry.getKey())
                        .append(" - ").append(entry.getValue().getDescription())
                        .append("\n");
            }
            return sb.toString();
        });

        // mods
        registerCommand("mods", "Mod management (list/info/reload/disable/enable)", args -> {
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
        registerCommand("events", "Event system (monitor/stats)", args -> {
            if (args.startsWith("monitor")) {
                eventMonitoring = !eventMonitoring;
                return "Event monitoring: " + (eventMonitoring ? "ON" : "OFF");
            }
            return "Usage: events [monitor|stats]";
        });

        // clear
        registerCommand("clear", "Clear output buffer", args -> {
            outputBuffer.clear();
            return "Output cleared.";
        });

        // lua
        registerCommand("lua", "Execute Lua code (Admin only in multiplayer)", args -> {
            // PermissionValidator에서 이미 권한 및 SandboxOptions 검사를 수행했으므로 바로 실행
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
        INSTANCE.registerCommand(name, description, executor);
    }

    private void registerCommand(String name, String description, CommandExecutor executor) {
        commands.put(name.toLowerCase(), new ConsoleCommand(description, executor));
    }

    public static void setOutputHandler(Consumer<String> handler) {
        INSTANCE.outputHandler = handler;
    }

    public static void print(String message) {
        INSTANCE.outputBuffer.offer(message);
        if (INSTANCE.outputHandler != null) {
            INSTANCE.outputHandler.accept(message);
        }
        PulseLogger.info(LOG, "[DevConsole] {}", message);
    }
}
