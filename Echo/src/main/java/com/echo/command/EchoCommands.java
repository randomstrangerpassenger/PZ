package com.echo.command;

import com.echo.aggregate.SpikeLog;
import com.echo.config.EchoConfig;
import com.echo.measure.EchoProfiler;
import com.echo.measure.MemoryProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.monitor.EchoMonitorServer;
import com.echo.pulse.PulseEventAdapter;
import com.echo.pulse.TickProfiler;
import com.echo.pulse.RenderProfiler;
import com.echo.report.EchoReport;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

/**
 * Echo 콘솔 명령어
 * 
 * 사용 가능한 명령어:
 * - /echo help - 도움말
 * - /echo enable - 프로파일링 시작
 * - /echo disable - 프로파일링 중지
 * - /echo status - 현재 상태 출력
 * - /echo report - 리포트 생성
 * - /echo reset - 통계 초기화
 * - /echo lua on/off - Lua 프로파일링 토글
 * - /echo config threshold <ms> - 스파이크 임계값 설정
 * - /echo memory - 메모리 상태 출력
 */
public class EchoCommands {

    private static final Map<String, Consumer<String[]>> commands = new HashMap<>();
    private static boolean registered = false;

    /**
     * 명령어 등록
     */
    public static void register() {
        if (registered)
            return;

        commands.put("help", EchoCommands::cmdHelp);
        commands.put("enable", EchoCommands::cmdEnable);
        commands.put("disable", EchoCommands::cmdDisable);
        commands.put("status", EchoCommands::cmdStatus);
        commands.put("report", EchoCommands::cmdReport);
        commands.put("reset", EchoCommands::cmdReset);
        commands.put("lua", EchoCommands::cmdLua);
        commands.put("config", EchoCommands::cmdConfig);
        commands.put("memory", EchoCommands::cmdMemory);
        commands.put("test", EchoCommands::cmdTest);
        commands.put("stack", EchoCommands::cmdStack);
        commands.put("overhead", EchoCommands::cmdOverhead);
        commands.put("monitor", EchoCommands::cmdMonitor);

        registered = true;
        System.out.println("[Echo] Commands registered");
    }

    /**
     * 명령어 실행
     * 
     * @param args 명령어 인자 (첫 번째는 서브커맨드)
     * @return 처리 여부
     */
    public static boolean execute(String[] args) {
        if (args == null || args.length == 0) {
            cmdHelp(args);
            return true;
        }

        String subCommand = args[0].toLowerCase();
        Consumer<String[]> handler = commands.get(subCommand);

        if (handler != null) {
            handler.accept(args);
            return true;
        } else {
            System.out.println("[Echo] Unknown command: " + subCommand);
            System.out.println("[Echo] Use '/echo help' for available commands");
            return false;
        }
    }

    // ============================================================
    // Command Handlers
    // ============================================================

    private static void cmdHelp(String[] args) {
        System.out.println();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║           Echo Profiler Commands              ║");
        System.out.println("╠═══════════════════════════════════════════════╣");
        System.out.println("║  Basic Commands:                              ║");
        System.out.println("║  /echo help        - Show this help           ║");
        System.out.println("║  /echo enable      - Start profiling          ║");
        System.out.println("║  /echo disable     - Stop profiling           ║");
        System.out.println("║  /echo status      - Show current status      ║");
        System.out.println("║  /echo report      - Generate report          ║");
        System.out.println("║  /echo report json - Save JSON report         ║");
        System.out.println("║  /echo reset       - Reset all statistics     ║");
        System.out.println("╠═══════════════════════════════════════════════╣");
        System.out.println("║  Lua Profiling:                               ║");
        System.out.println("║  /echo lua on      - Enable Lua profiling     ║");
        System.out.println("║  /echo lua off     - Disable Lua profiling    ║");
        System.out.println("╠═══════════════════════════════════════════════╣");
        System.out.println("║  Configuration:                               ║");
        System.out.println("║  /echo config      - Show current config      ║");
        System.out.println("║  /echo config set threshold <ms>              ║");
        System.out.println("║  /echo memory      - Show memory status       ║");
        System.out.println("╠═══════════════════════════════════════════════╣");
        System.out.println("║  Advanced (Phase 4):                          ║");
        System.out.println("║  /echo stack on    - Enable spike stack trace ║");
        System.out.println("║  /echo overhead    - Measure profiler cost    ║");
        System.out.println("║  /echo monitor start [port] - Start HTTP API  ║");
        System.out.println("║  /echo test        - Run quick test           ║");
        System.out.println("╚═══════════════════════════════════════════════╝");
        System.out.println();
    }

    private static void cmdEnable(String[] args) {
        EchoProfiler.getInstance().enable();
    }

    private static void cmdDisable(String[] args) {
        EchoProfiler.getInstance().disable();
    }

    private static void cmdStatus(String[] args) {
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

    private static void cmdReport(String[] args) {
        EchoProfiler profiler = EchoProfiler.getInstance();
        EchoReport report = new EchoReport(profiler);
        String reportDir = EchoConfig.getInstance().getReportDirectory();

        if (args.length > 1) {
            String format = args[1].toLowerCase();
            try {
                switch (format) {
                    case "json":
                        String jsonPath = report.saveWithTimestamp(reportDir);
                        System.out.println("[Echo] JSON report saved: " + jsonPath);
                        break;
                    case "csv":
                        String csvPath = report.saveCsv(reportDir);
                        System.out.println("[Echo] CSV report saved: " + csvPath);
                        break;
                    case "html":
                        String htmlPath = report.saveHtml(reportDir);
                        System.out.println("[Echo] HTML report saved: " + htmlPath);
                        break;
                    default:
                        System.out.println("[Echo] Unknown format: " + format);
                        System.out.println("[Echo] Usage: /echo report [json|csv|html]");
                }
            } catch (Exception e) {
                System.err.println("[Echo] Failed to save report: " + e.getMessage());
            }
        } else {
            report.printToConsole();
        }
    }

    private static void cmdReset(String[] args) {
        EchoProfiler.getInstance().reset();
    }

    private static void cmdLua(String[] args) {
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

    private static void cmdConfig(String[] args) {
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

    private static void cmdMemory(String[] args) {
        MemoryProfiler.printStatus();
    }

    private static void cmdTest(String[] args) {
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

    /**
     * Smoke Test 결과를 파일로 저장 (회귀 테스트용)
     */
    private static void saveTestResult(EchoProfiler profiler, int iterations, int success, long durationMs) {
        try {
            java.io.File dir = new java.io.File("./echo_tests");
            if (!dir.exists()) {
                dir.mkdirs();
            }

            String timestamp = java.time.LocalDateTime.now()
                    .format(java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
            java.io.File file = new java.io.File(dir, "smoke_test_" + timestamp + ".txt");

            try (java.io.PrintWriter writer = new java.io.PrintWriter(file)) {
                writer.println("═══════════════════════════════════════════════════════");
                writer.println("  Echo Profiler Smoke Test Report");
                writer.println("  " + java.time.LocalDateTime.now());
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

    /**
     * Phase 4: 스파이크 스택 캡처 토글
     */
    private static void cmdStack(String[] args) {
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

    /**
     * Phase 4: 메타 프로파일링 (프로파일러 오버헤드 측정)
     */
    private static void cmdOverhead(String[] args) {
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

    /**
     * Phase 4: HTTP 모니터 서버 제어
     */
    private static void cmdMonitor(String[] args) {
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
}
