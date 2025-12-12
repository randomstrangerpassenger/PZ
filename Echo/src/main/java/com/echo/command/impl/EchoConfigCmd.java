package com.echo.command.impl;

import com.echo.aggregate.SpikeLog;
import com.echo.measure.EchoProfiler;

public class EchoConfigCmd {
    public static void execute(String[] args) {
        EchoProfiler profiler = EchoProfiler.getInstance();
        SpikeLog spikeLog = profiler.getSpikeLog();

        // /echo config (no args) - show current config
        if (args.length < 2) {
            System.out.println();
            System.out.println("╔═══════════════════════════════════════════════╗");
            System.out.println("║           Echo Configuration                  ║");
            System.out.println("╠═══════════════════════════════════════════════╣");
            System.out.printf("║  Spike Threshold: %.2f ms                    ║%n", spikeLog.getThresholdMs());
            System.out.printf("║  Lua Profiling:   %s                      ║%n",
                    profiler.isLuaProfilingEnabled() ? "ON " : "OFF");
            System.out.println("╠═══════════════════════════════════════════════╣");
            System.out.println("║  Usage:                                       ║");
            System.out.println("║    /echo config get              - Show all   ║");
            System.out.println("║    /echo config set threshold <ms>            ║");
            System.out.println("╚═══════════════════════════════════════════════╝");
            System.out.println();
            return;
        }

        String action = args[1].toLowerCase();

        // /echo config get
        if ("get".equals(action)) {
            System.out.println("[Echo] Current Configuration:");
            System.out.printf("  spike.threshold = %.2f ms%n", spikeLog.getThresholdMs());
            System.out.printf("  lua.enabled = %s%n", profiler.isLuaProfilingEnabled());
            System.out.printf("  profiler.enabled = %s%n", profiler.isEnabled());
            return;
        }

        // /echo config set <key> <value>
        if ("set".equals(action)) {
            if (args.length < 4) {
                System.out.println("[Echo] Usage: /echo config set <key> <value>");
                System.out.println("[Echo]   Available keys: threshold");
                return;
            }

            String key = args[2].toLowerCase();
            String value = args[3];

            if ("threshold".equals(key)) {
                try {
                    double thresholdMs = Double.parseDouble(value);
                    if (thresholdMs <= 0) {
                        System.out.println("[Echo] Threshold must be positive");
                        return;
                    }
                    spikeLog.setThresholdMs(thresholdMs);
                    System.out.printf("[Echo] Spike threshold set to %.2f ms%n", thresholdMs);
                } catch (NumberFormatException e) {
                    System.out.println("[Echo] Invalid number: " + value);
                }
            } else {
                System.out.println("[Echo] Unknown config key: " + key);
                System.out.println("[Echo] Available keys: threshold");
            }
            return;
        }

        // Legacy: /echo config threshold <value> (backward compatibility)
        if ("threshold".equals(action)) {
            if (args.length < 3) {
                System.out.printf("[Echo] Current threshold: %.2f ms%n", spikeLog.getThresholdMs());
                return;
            }
            try {
                double thresholdMs = Double.parseDouble(args[2]);
                if (thresholdMs <= 0) {
                    System.out.println("[Echo] Threshold must be positive");
                    return;
                }
                spikeLog.setThresholdMs(thresholdMs);
            } catch (NumberFormatException e) {
                System.out.println("[Echo] Invalid number: " + args[2]);
            }
            return;
        }

        System.out.println("[Echo] Unknown config action: " + action);
        System.out.println("[Echo] Usage: /echo config [get|set <key> <value>]");
    }
}
