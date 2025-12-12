package com.echo.command.impl;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;

public class EchoOverheadCmd {
    public static void execute(String[] args) {
        System.out.println("[Echo] Measuring profiler overhead...");

        EchoProfiler profiler = EchoProfiler.getInstance();
        boolean wasEnabled = profiler.isEnabled();

        if (!wasEnabled) {
            profiler.enable(false);
        }

        int iterations = 10000;

        // 오버헤드 없이 측정
        long baselineStart = System.nanoTime();
        for (int i = 0; i < iterations; i++) {
            // 빈 루프
        }
        long baselineTime = System.nanoTime() - baselineStart;

        // 프로파일링 오버헤드 측정
        long profiledStart = System.nanoTime();
        for (int i = 0; i < iterations; i++) {
            long start = profiler.startRaw(ProfilingPoint.ECHO_OVERHEAD);
            profiler.endRaw(ProfilingPoint.ECHO_OVERHEAD, start);
        }
        long profiledTime = System.nanoTime() - profiledStart;

        // scope() API 오버헤드 측정
        long scopeStart = System.nanoTime();
        for (int i = 0; i < iterations; i++) {
            try (var scope = profiler.scope(ProfilingPoint.ECHO_OVERHEAD)) {
                // 빈 루프
            }
        }
        long scopeTime = System.nanoTime() - scopeStart;

        if (!wasEnabled) {
            profiler.disable();
        }

        // 결과 출력
        double rawOverheadNs = (profiledTime - baselineTime) / (double) iterations;
        double scopeOverheadNs = (scopeTime - baselineTime) / (double) iterations;

        System.out.println();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║         Echo Profiler Overhead Report         ║");
        System.out.println("╠═══════════════════════════════════════════════╣");
        System.out.printf("║  Iterations:        %,d                   ║%n", iterations);
        System.out.printf("║  Raw API overhead:  %.2f ns/call           ║%n", rawOverheadNs);
        System.out.printf("║  Scope API overhead: %.2f ns/call          ║%n", scopeOverheadNs);
        System.out.println("╠═══════════════════════════════════════════════╣");
        System.out.println("║  💡 Lower is better. <100ns is excellent.     ║");
        System.out.println("╚═══════════════════════════════════════════════╝");
        System.out.println();
    }
}
