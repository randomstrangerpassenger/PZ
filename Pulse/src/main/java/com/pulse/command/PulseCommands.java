package com.pulse.command;

import com.pulse.api.log.PulseLogger;

import com.pulse.diagnostics.HotspotMap;
import com.pulse.diagnostics.PulseThreadGuard;
import com.pulse.diagnostics.PulseTickContext;
import com.pulse.event.EventBus;
import com.pulse.hook.PulseHookRegistry;
import com.pulse.mixin.PulseErrorHandler;
import com.pulse.mixin.SafeMixinWrapper;
import com.pulse.runtime.PulseRuntime;
import com.pulse.PulseInfo;

import java.util.List;

/**
 * Pulse 콘솔 명령어 모음.
 * 
 * 로드맵의 "Pulse Console Commands" 요구사항을 충족합니다.
 * 
 * @since Pulse 1.2
 */
public final class PulseCommands {
    private static final String LOG = PulseLogger.PULSE;

    private PulseCommands() {
    }

    /**
     * 모든 /pulse 명령어 등록
     */
    public static void registerAll() {
        CommandRegistry.register("pulse", "Pulse 메인 명령어", PulseCommands::handlePulse);
        PulseLogger.info(LOG, "Registered /pulse commands");
    }

    /**
     * /pulse 명령어 핸들러
     */
    private static void handlePulse(CommandContext ctx) {
        String[] args = ctx.getRawArgs();

        if (args.length == 0) {
            showHelp(ctx);
            return;
        }

        String subCommand = args[0].toLowerCase();
        switch (subCommand) {
            case "status" -> showStatus(ctx);
            case "debug" -> handleDebug(ctx, args);
            case "mixins" -> showMixins(ctx);
            case "events" -> showEvents(ctx);
            case "errors" -> showErrors(ctx);
            case "hotspots" -> showHotspots(ctx);
            case "version" -> showVersion(ctx);
            case "help" -> showHelp(ctx);
            default -> ctx.reply("Unknown subcommand: " + subCommand + ". Use /pulse help");
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 서브 명령어 구현
    // ─────────────────────────────────────────────────────────────

    private static void showHelp(CommandContext ctx) {
        ctx.reply("§a=== Pulse Commands ===");
        ctx.reply("§e/pulse status§r - Pulse 상태 출력");
        ctx.reply("§e/pulse debug on/off§r - 디버그 모드 토글");
        ctx.reply("§e/pulse mixins§r - 로드된 Mixin 정보");
        ctx.reply("§e/pulse events§r - 등록된 이벤트 리스너");
        ctx.reply("§e/pulse errors§r - Mixin 오류 목록");
        ctx.reply("§e/pulse hotspots§r - 핫스팟 함수 목록");
        ctx.reply("§e/pulse version§r - 게임/Pulse 버전");
    }

    private static void showStatus(CommandContext ctx) {
        ctx.reply("§a=== Pulse Status ===");
        ctx.reply("§7Version:§r " + getPulseVersion());
        ctx.reply("§7Game:§r " + PulseRuntime.getVersionString());
        ctx.reply("§7Hook Types:§r " + PulseHookRegistry.getRegisteredTypeCount());
        ctx.reply("§7Mixin Errors:§r " + PulseErrorHandler.getTotalErrorCount());
        ctx.reply("§7Thread:§r " + PulseThreadGuard.getStatus());
        ctx.reply("§7Tick Context:§r " + PulseTickContext.get().getSnapshot());
    }

    private static void handleDebug(CommandContext ctx, String[] args) {
        if (args.length < 2) {
            ctx.reply("Usage: /pulse debug on/off");
            return;
        }

        boolean enable = args[1].equalsIgnoreCase("on");

        // 디버그 모드 설정
        PulseHookRegistry.setDebugEnabled(enable);
        SafeMixinWrapper.setDebugMode(enable);
        EventBus.getInstance().setDebug(enable);
        HotspotMap.setEnabled(enable);

        ctx.reply("§aDebug mode: " + (enable ? "§aENABLED" : "§cDISABLED"));
    }

    private static void showMixins(CommandContext ctx) {
        ctx.reply("§a=== Loaded Mixins ===");
        ctx.reply("§7Running Mixins:§r");
        ctx.reply("  - IsoWorldMixin (GameTick, LOS)");
        ctx.reply("  - IsoZombieMixin (ZombieUpdate)");
        ctx.reply("  - IsoPlayerMixin (PlayerUpdate)");
        ctx.reply("  - PathfindingMixin (Pathfinding)");
        ctx.reply("  - IsoGridMixin (IsoGrid)");
        ctx.reply("  - GameWindowMixin (Render)");

        if (PulseErrorHandler.getTotalErrorCount() > 0) {
            ctx.reply("§cMixins with errors:§r " + PulseErrorHandler.getErrorCounts().size());
        }
    }

    private static void showEvents(CommandContext ctx) {
        ctx.reply("§a=== Event Listeners ===");
        ctx.reply(PulseHookRegistry.getStatusSummary());
    }

    private static void showErrors(CommandContext ctx) {
        ctx.reply("§a=== Mixin Errors ===");
        int total = PulseErrorHandler.getTotalErrorCount();
        if (total == 0) {
            ctx.reply("§aNo errors recorded.");
            return;
        }

        ctx.reply("§cTotal errors: " + total);
        PulseErrorHandler.getErrorCounts().forEach((mixin, count) -> ctx.reply("  §7" + mixin + ":§r " + count));

        List<PulseErrorHandler.MixinError> recent = PulseErrorHandler.getRecentErrors();
        if (!recent.isEmpty()) {
            ctx.reply("§7Recent:§r");
            recent.stream().limit(5).forEach(e -> ctx.reply("  " + e));
        }
    }

    private static void showHotspots(CommandContext ctx) {
        ctx.reply("§a=== Top Hotspots ===");
        List<HotspotMap.HotspotEntry> top = HotspotMap.getTopHotspots(10);

        if (top.isEmpty()) {
            ctx.reply("§7No hotspots recorded yet.");
            return;
        }

        for (int i = 0; i < top.size(); i++) {
            HotspotMap.HotspotEntry e = top.get(i);
            ctx.reply(String.format("§7%d.§r %s §8(%.2fms total, %.3fms avg, %d calls)",
                    i + 1, e.getFunction(), e.getTotalMs(), e.getAverageMs(), e.getCount()));
        }
    }

    private static void showVersion(CommandContext ctx) {
        ctx.reply("§a=== Version Info ===");
        ctx.reply("§7Pulse:§r " + getPulseVersion());
        ctx.reply("§7Game Version:§r " + PulseRuntime.getVersionString());
        ctx.reply("§7Detected:§r " + PulseRuntime.getVersion().getDisplayName());
        ctx.reply("§7Java:§r " + System.getProperty("java.version"));
    }

    private static String getPulseVersion() {
        return PulseInfo.getVersion();
    }
}
