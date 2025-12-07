package com.pulse.debug;

import com.pulse.mod.ModLoader;
import com.pulse.mod.ModContainer;
import com.pulse.mod.ModReloadManager;

import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.function.Consumer;

/**
 * 인게임 개발자 콘솔.
 * REPL 스타일 디버그 명령어 실행.
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
