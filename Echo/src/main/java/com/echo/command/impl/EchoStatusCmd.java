package com.echo.command.impl;

import com.echo.measure.EchoProfiler;
import com.echo.pulse.PulseEventAdapter;
import com.echo.pulse.TickProfiler;
import com.echo.pulse.RenderProfiler;

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

        // Pulse integration status
        if (PulseEventAdapter.isRegistered()) {
            TickProfiler tickProfiler = PulseEventAdapter.getTickProfiler();
            RenderProfiler renderProfiler = PulseEventAdapter.getRenderProfiler();

            System.out.println("📡 PULSE INTEGRATION");
            System.out.println("───────────────────────────────────────────────────────");
            if (tickProfiler != null) {
                System.out.printf("  Tick Count:     %,d%n", tickProfiler.getTickCount());
                System.out.printf("  Last Tick:      %.2f ms%n", tickProfiler.getLastTickDurationMs());
                System.out.printf("  Spike Threshold: %.2f ms%n", tickProfiler.getSpikeThresholdMs());
            }
            if (renderProfiler != null) {
                System.out.printf("  Frame Count:    %,d%n", renderProfiler.getFrameCount());
                System.out.printf("  Current FPS:    %.1f%n", renderProfiler.getCurrentFps());
                System.out.printf("  Last Frame:     %.2f ms%n", renderProfiler.getLastFrameDurationMs());
            }
            System.out.println();
        }
    }
}
