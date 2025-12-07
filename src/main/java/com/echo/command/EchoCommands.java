package com.echo.command;

import com.echo.aggregate.SpikeLog;
import com.echo.measure.EchoProfiler;
import com.echo.measure.MemoryProfiler;
import com.echo.measure.ProfilingPoint;
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
        System.out.println("║  /echo help        - Show this help           ║");
        System.out.println("║  /echo enable      - Start profiling          ║");
        System.out.println("║  /echo disable     - Stop profiling           ║");
        System.out.println("║  /echo status      - Show current status      ║");
        System.out.println("║  /echo report      - Generate report          ║");
        System.out.println("║  /echo report json - Save JSON report         ║");
        System.out.println("║  /echo reset       - Reset all statistics     ║");
        System.out.println("║  /echo lua on      - Enable Lua profiling     ║");
        System.out.println("║  /echo lua off     - Disable Lua profiling    ║");
        System.out.println("║  /echo config threshold <ms> - Set spike threshold ║");
        System.out.println("║  /echo memory      - Show memory status       ║");
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

        if (args.length > 1 && "json".equalsIgnoreCase(args[1])) {
            try {
                String path = report.saveWithTimestamp("./echo_reports");
                System.out.println("[Echo] JSON report saved: " + path);
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
        if (args.length < 3) {
            System.out.println("[Echo] Usage: /echo config threshold <ms>");
            System.out.println("[Echo]   Example: /echo config threshold 50");
            return;
        }

        String option = args[1].toLowerCase();
        if ("threshold".equals(option)) {
            try {
                double thresholdMs = Double.parseDouble(args[2]);
                if (thresholdMs <= 0) {
                    System.out.println("[Echo] Threshold must be positive");
                    return;
                }
                SpikeLog spikeLog = EchoProfiler.getInstance().getSpikeLog();
                spikeLog.setThresholdMs(thresholdMs);
            } catch (NumberFormatException e) {
                System.out.println("[Echo] Invalid number: " + args[2]);
            }
        } else {
            System.out.println("[Echo] Unknown config option: " + option);
            System.out.println("[Echo] Available: threshold");
        }
    }

    private static void cmdMemory(String[] args) {
        MemoryProfiler.printStatus();
    }

    private static void cmdTest(String[] args) {
        System.out.println("[Echo] Running quick profiling test...");

        EchoProfiler profiler = EchoProfiler.getInstance();
        boolean wasEnabled = profiler.isEnabled();

        if (!wasEnabled) {
            profiler.enable();
        }

        // Simulate some profiling
        for (int i = 0; i < 100; i++) {
            try (var scope = profiler.scope(ProfilingPoint.TICK)) {
                // Simulate tick work
                Thread.sleep(1);

                try (var aiScope = profiler.scope(ProfilingPoint.ZOMBIE_AI, "pathfinding")) {
                    Thread.sleep(0, 500000); // 0.5ms
                }

                try (var renderScope = profiler.scope(ProfilingPoint.RENDER)) {
                    Thread.sleep(0, 300000); // 0.3ms
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }

        System.out.println("[Echo] Test complete! 100 simulated ticks recorded.");
        profiler.printStatus();

        if (!wasEnabled) {
            profiler.disable();
        }
    }
}
