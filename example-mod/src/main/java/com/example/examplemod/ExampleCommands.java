package com.example.examplemod;

import com.mutagen.command.Arg;
import com.mutagen.command.Command;
import com.mutagen.command.CommandContext;
import com.mutagen.command.CommandRegistry;

/**
 * 예제 명령어 클래스.
 * 
 * @Command 어노테이션을 사용한 명령어 정의 예제.
 */
public class ExampleCommands {

    /**
     * 명령어 등록
     */
    public static void register() {
        // 어노테이션 기반 등록
        CommandRegistry.register(new ExampleCommands());

        // 람다 기반 등록
        CommandRegistry.register("examplehelp", "Show example mod help", ctx -> {
            ctx.reply("═══════════════════════════════════════");
            ctx.reply("  Example Mod Commands");
            ctx.reply("═══════════════════════════════════════");
            ctx.reply("/examplestatus - Show current status");
            ctx.reply("/exampleheal [amount] - Heal player");
            ctx.reply("/exampletoggle <feature> - Toggle feature");
            ctx.reply("/examplehelp - Show this help");
            ctx.reply("═══════════════════════════════════════");
        });
    }

    // ─────────────────────────────────────────────────────────────
    // 명령어 핸들러
    // ─────────────────────────────────────────────────────────────

    @Command(name = "examplestatus", description = "Show example mod status", aliases = { "exstatus" })
    public void statusCommand(CommandContext ctx) {
        ctx.reply("Example Mod Status:");
        ctx.reply("  Debug Mode: " + ExampleConfig.debugMode);
        ctx.reply("  Log Interval: " + ExampleConfig.logInterval + " ticks");
        ctx.reply("  Damage Reduction: " + (ExampleConfig.damageReduction * 100) + "%");
        ctx.reply("  Fire Immunity: " + ExampleConfig.fireImmunity);
    }

    @Command(name = "exampleheal", description = "Heal the player", usage = "/exampleheal [amount]", playerOnly = true)
    public void healCommand(CommandContext ctx, @Arg(value = "amount", optional = true) Float amount) {
        float healAmount = amount != null ? amount : 100.0f;

        // 실제 힐 로직은 GameAccess API를 통해 구현
        // GameAccess.setPlayerHealth(GameAccess.getPlayerHealth() + healAmount);

        ctx.reply("Healed for " + healAmount + " HP!");
    }

    @Command(name = "exampletoggle", description = "Toggle a feature", usage = "/exampletoggle <debug|fire|nightvision>")
    public void toggleCommand(CommandContext ctx, @Arg(value = "feature") String feature) {
        switch (feature.toLowerCase()) {
            case "debug":
                ExampleConfig.debugMode = !ExampleConfig.debugMode;
                ctx.reply("Debug mode: " + (ExampleConfig.debugMode ? "ON" : "OFF"));
                break;

            case "fire":
                ExampleConfig.fireImmunity = !ExampleConfig.fireImmunity;
                ctx.reply("Fire immunity: " + (ExampleConfig.fireImmunity ? "ON" : "OFF"));
                break;

            case "nightvision":
            case "nv":
                ExampleConfig.nightVision = !ExampleConfig.nightVision;
                ctx.reply("Night vision: " + (ExampleConfig.nightVision ? "ON" : "OFF"));
                break;

            default:
                ctx.reply("Unknown feature: " + feature);
                ctx.reply("Available: debug, fire, nightvision");
                break;
        }
    }
}
