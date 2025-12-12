package com.echo.command.impl;

import com.echo.aggregate.SpikeLog;
import com.echo.measure.EchoProfiler;
import com.echo.measure.MemoryProfiler;
import com.echo.monitor.EchoMonitorServer;

public class EchoMonitoringCmd {

    public static void executeMonitor(String[] args) {
        EchoMonitorServer server = EchoMonitorServer.getInstance();

        if (args.length < 2) {
            System.out.println("[Echo] Monitor server: " + (server.isRunning() ? "RUNNING" : "STOPPED"));
            System.out.println("[Echo] Usage: /echo monitor <start|stop>");
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
                        System.out.println("[Echo] Invalid port: " + args[2]);
                    }
                } else {
                    server.start();
                }
                break;
            case "stop":
                server.stop();
                break;
            default:
                System.out.println("[Echo] Usage: /echo monitor <start|stop>");
        }
    }

    public static void executeMemory(String[] args) {
        MemoryProfiler.printStatus();
    }

    public static void executeStack(String[] args) {
        SpikeLog spikeLog = EchoProfiler.getInstance().getSpikeLog();

        if (args.length < 2) {
            System.out.println("[Echo] Stack capture: " +
                    (spikeLog.isStackCaptureEnabled() ? "ENABLED" : "DISABLED"));
            System.out.println("[Echo] Usage: /echo stack <on|off>");
            System.out.println("[Echo] ⚠️ Warning: Stack capture has significant performance cost!");
            return;
        }

        String toggle = args[1].toLowerCase();
        if ("on".equals(toggle)) {
            spikeLog.setStackCaptureEnabled(true);
        } else if ("off".equals(toggle)) {
            spikeLog.setStackCaptureEnabled(false);
        } else {
            System.out.println("[Echo] Usage: /echo stack <on|off>");
        }
    }
}
