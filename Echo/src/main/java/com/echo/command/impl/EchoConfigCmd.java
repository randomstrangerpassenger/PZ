package com.echo.command.impl;

import com.echo.aggregate.SpikeLog;
import com.echo.measure.EchoProfiler;
import com.pulse.api.log.PulseLogger;

public class EchoConfigCmd {
    public static void execute(String[] args) {
        EchoProfiler profiler = EchoProfiler.getInstance();
        SpikeLog spikeLog = profiler.getSpikeLog();

        // /echo config (no args) - show current config
        if (args.length < 2) {
            PulseLogger.info("Echo", "");
            PulseLogger.info("Echo", "╔═══════════════════════════════════════════════╗");
            PulseLogger.info("Echo", "║           Echo Configuration                  ║");
            PulseLogger.info("Echo", "╠═══════════════════════════════════════════════╣");
            PulseLogger.info("Echo",
                    String.format("║  Spike Threshold: %.2f ms                    ║", spikeLog.getThresholdMs()));
            PulseLogger.info("Echo", String.format("║  Lua Profiling:   %s                      ║",
                    profiler.isLuaProfilingEnabled() ? "ON " : "OFF"));
            PulseLogger.info("Echo", "╠═══════════════════════════════════════════════╣");
            PulseLogger.info("Echo", "║  Usage:                                       ║");
            PulseLogger.info("Echo", "║    /echo config get              - Show all   ║");
            PulseLogger.info("Echo", "║    /echo config set threshold <ms>            ║");
            PulseLogger.info("Echo", "╚═══════════════════════════════════════════════╝");
            PulseLogger.info("Echo", "");
            return;
        }

        String action = args[1].toLowerCase();

        // /echo config get
        if ("get".equals(action)) {
            PulseLogger.info("Echo", "Current Configuration:");
            PulseLogger.info("Echo", String.format("  spike.threshold = %.2f ms", spikeLog.getThresholdMs()));
            PulseLogger.info("Echo", String.format("  lua.enabled = %s", profiler.isLuaProfilingEnabled()));
            PulseLogger.info("Echo", String.format("  profiler.enabled = %s", profiler.isEnabled()));
            return;
        }

        // /echo config set <key> <value>
        if ("set".equals(action)) {
            if (args.length < 4) {
                PulseLogger.info("Echo", "Usage: /echo config set <key> <value>");
                PulseLogger.info("Echo", "  Available keys: threshold");
                return;
            }

            String key = args[2].toLowerCase();
            String value = args[3];

            if ("threshold".equals(key)) {
                try {
                    double thresholdMs = Double.parseDouble(value);
                    if (thresholdMs <= 0) {
                        PulseLogger.warn("Echo", "Threshold must be positive");
                        return;
                    }
                    spikeLog.setThresholdMs(thresholdMs);
                    PulseLogger.info("Echo", String.format("Spike threshold set to %.2f ms", thresholdMs));
                } catch (NumberFormatException e) {
                    PulseLogger.warn("Echo", "Invalid number: " + value);
                }
            } else {
                PulseLogger.warn("Echo", "Unknown config key: " + key);
                PulseLogger.info("Echo", "Available keys: threshold");
            }
            return;
        }

        // Legacy: /echo config threshold <value> (backward compatibility)
        if ("threshold".equals(action)) {
            if (args.length < 3) {
                PulseLogger.info("Echo", String.format("Current threshold: %.2f ms", spikeLog.getThresholdMs()));
                return;
            }
            try {
                double thresholdMs = Double.parseDouble(args[2]);
                if (thresholdMs <= 0) {
                    PulseLogger.warn("Echo", "Threshold must be positive");
                    return;
                }
                spikeLog.setThresholdMs(thresholdMs);
            } catch (NumberFormatException e) {
                PulseLogger.warn("Echo", "Invalid number: " + args[2]);
            }
            return;
        }

        PulseLogger.warn("Echo", "Unknown config action: " + action);
        PulseLogger.info("Echo", "Usage: /echo config [get|set <key> <value>]");
    }
}
