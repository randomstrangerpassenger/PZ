package com.echo.command.impl;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;

import java.io.File;
import java.io.PrintWriter;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class EchoTestCmd {
    public static void execute(String[] args) {
        System.out.println("[Echo] Running quick profiling test...");

        EchoProfiler profiler = EchoProfiler.getInstance();
        boolean wasEnabled = profiler.isEnabled();
        long testStartTime = System.currentTimeMillis();

        if (!wasEnabled) {
            profiler.enable();
        }

        int testIterations = 100;
        int successCount = 0;

        // Simulate some profiling
        for (int i = 0; i < testIterations; i++) {
            try (var scope = profiler.scope(ProfilingPoint.TICK)) {
                // Simulate tick work
                Thread.sleep(1);

                try (var aiScope = profiler.scope(ProfilingPoint.ZOMBIE_AI, "pathfinding")) {
                    Thread.sleep(0, 500000); // 0.5ms
                }

                try (var renderScope = profiler.scope(ProfilingPoint.RENDER)) {
                    Thread.sleep(0, 300000); // 0.3ms
                }
                successCount++;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }

        long testDuration = System.currentTimeMillis() - testStartTime;

        System.out.println("[Echo] Test complete! " + successCount + "/" + testIterations + " ticks recorded.");
        profiler.printStatus();

        // Phase 3: 결과 파일 저장
        saveTestResult(profiler, testIterations, successCount, testDuration);

        if (!wasEnabled) {
            profiler.disable();
        }
    }

    private static void saveTestResult(EchoProfiler profiler, int iterations, int success, long durationMs) {
        try {
            File dir = new File("./echo_tests");
            if (!dir.exists()) {
                dir.mkdirs();
            }

            String timestamp = LocalDateTime.now()
                    .format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
            File file = new File(dir, "smoke_test_" + timestamp + ".txt");

            try (PrintWriter writer = new PrintWriter(file)) {
                writer.println("═══════════════════════════════════════════════════════");
                writer.println("  Echo Profiler Smoke Test Report");
                writer.println("  " + LocalDateTime.now());
                writer.println("═══════════════════════════════════════════════════════");
                writer.println();
                writer.println("TEST SUMMARY");
                writer.println("───────────────────────────────────────────────────────");
                writer.println("  Iterations:    " + iterations);
                writer.println("  Success:       " + success);
                writer.println("  Duration:      " + durationMs + " ms");
                writer.println("  Result:        " + (success == iterations ? "✅ PASS" : "❌ FAIL"));
                writer.println();
                writer.println("PROFILER METRICS");
                writer.println("───────────────────────────────────────────────────────");

                for (ProfilingPoint point : ProfilingPoint.values()) {
                    var data = profiler.getTimingData(point);
                    if (data != null && data.getCallCount() > 0) {
                        writer.printf("  %-15s | calls: %,8d | avg: %6.2f ms | max: %6.2f ms%n",
                                point.getDisplayName(),
                                data.getCallCount(),
                                data.getAverageMicros() / 1000.0,
                                data.getMaxMicros() / 1000.0);
                    }
                }

                writer.println();
                writer.println("CONFIGURATION");
                writer.println("───────────────────────────────────────────────────────");
                writer.println("  Spike Threshold: " + profiler.getSpikeLog().getThresholdMs() + " ms");
                writer.println("  Lua Profiling:   " + profiler.isLuaProfilingEnabled());
                writer.println();
                writer.println("═══════════════════════════════════════════════════════");
            }

            System.out.println("[Echo] Test result saved: " + file.getAbsolutePath());
        } catch (Exception e) {
            System.err.println("[Echo] Failed to save test result: " + e.getMessage());
        }
    }
}
