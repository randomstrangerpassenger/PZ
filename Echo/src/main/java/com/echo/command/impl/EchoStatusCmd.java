package com.echo.command.impl;

import com.echo.measure.EchoProfiler;

public class EchoStatusCmd {
    public static void execute(String[] args) {
        EchoProfiler profiler = EchoProfiler.getInstance();
        profiler.printStatus();

        // Enhanced Phase 3: 추가 상태 정보
        System.out.println("⚙️ CONFIGURATION");
        System.out.println("───────────────────────────────────────────────────────");
        System.out.printf("  Lua Profiling:   %s%n",
                profiler.isLuaProfilingEnabled() ? "✅ ENABLED" : "❌ DISABLED");
        System.out.printf("  Spike Threshold: %.2f ms%n",
                profiler.getSpikeLog().getThresholdMs());
        System.out.printf("  Stack Depth:     %d (current thread)%n",
                profiler.getCurrentStackDepth());
        System.out.printf("  Session Time:    %d seconds%n",
                profiler.getSessionDurationSeconds());
        System.out.println();

        // TODO: Pulse integration requires profiler API alignment
    }
}
