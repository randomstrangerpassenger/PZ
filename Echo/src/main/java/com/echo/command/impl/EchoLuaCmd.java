package com.echo.command.impl;

import com.echo.measure.EchoProfiler;

public class EchoLuaCmd {
    public static void execute(String[] args) {
        if (args.length < 2) {
            System.out.println("[Echo] Usage: /echo lua <on|off>");
            return;
        }

        String toggle = args[1].toLowerCase();
        EchoProfiler profiler = EchoProfiler.getInstance();

        if ("on".equals(toggle)) {
            profiler.enableLuaProfiling();
        } else if ("off".equals(toggle)) {
            profiler.disableLuaProfiling();
        } else {
            System.out.println("[Echo] Usage: /echo lua <on|off>");
        }
    }
}
