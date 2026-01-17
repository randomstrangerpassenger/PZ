package com.echo.command.impl;

import com.echo.aggregate.SpikeLog;
import com.echo.measure.EchoProfiler;
import com.echo.measure.MemoryProfiler;
import com.echo.monitor.EchoMonitorServer;
import com.pulse.api.log.PulseLogger;

public class EchoMonitoringCmd {

    public static void executeMonitor(String[] args) {
        EchoMonitorServer server = EchoMonitorServer.getInstance();

        if (args.length < 2) {
            PulseLogger.info("Echo", "Monitor server: " + (server.isRunning() ? "RUNNING" : "STOPPED"));
            PulseLogger.info("Echo", "Usage: /echo monitor <start|stop>");
            return;
        }

        String action = args[1].toLowerCase();
        switch (action) {
            case "start":
                if (args.length > 2) {
                    try {
                        int port = Integer.parseInt(args[2]);
                        server.start(port);
                    } catch (NumberFormatException e) {
                        PulseLogger.warn("Echo", "Invalid port: " + args[2]);
                    }
                } else {
                    server.start();
                }
                break;
            case "stop":
                server.stop();
                break;
            default:
                PulseLogger.info("Echo", "Usage: /echo monitor <start|stop>");
        }
    }

    public static void executeMemory(String[] args) {
        MemoryProfiler.printStatus();
    }

    public static void executeStack(String[] args) {
        SpikeLog spikeLog = EchoProfiler.getInstance().getSpikeLog();

        if (args.length < 2) {
            PulseLogger.info("Echo", "Stack capture: " +
                    (spikeLog.isStackCaptureEnabled() ? "ENABLED" : "DISABLED"));
            PulseLogger.info("Echo", "Usage: /echo stack <on|off>");
            PulseLogger.warn("Echo", "⚠️ Warning: Stack capture has significant performance cost!");
            return;
        }

        String toggle = args[1].toLowerCase();
        if ("on".equals(toggle)) {
            spikeLog.setStackCaptureEnabled(true);
        } else if ("off".equals(toggle)) {
            spikeLog.setStackCaptureEnabled(false);
        } else {
            PulseLogger.info("Echo", "Usage: /echo stack <on|off>");
        }
    }
}
