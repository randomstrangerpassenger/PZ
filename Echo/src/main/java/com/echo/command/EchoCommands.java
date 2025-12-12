package com.echo.command;

import com.echo.command.impl.*;
import com.echo.measure.EchoProfiler;
import com.pulse.command.CommandContext;
import com.pulse.command.CommandRegistry;

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
     * 명령어 등록 (Pulse CommandRegistry 통합)
     */
    public static void register() {
        if (registered)
            return;

        // Register internal command map for dispatch
        commands.put("help", EchoCommands::cmdHelp);
        commands.put("enable", EchoCommands::cmdEnable);
        commands.put("disable", EchoCommands::cmdDisable);

        // Delegated Commands
        commands.put("status", EchoStatusCmd::execute);
        commands.put("report", EchoReportCmd::execute);
        commands.put("config", EchoConfigCmd::execute);
        commands.put("lua", EchoLuaCmd::execute);
        commands.put("test", EchoTestCmd::execute);
        commands.put("overhead", EchoOverheadCmd::execute);
        commands.put("memory", EchoMonitoringCmd::executeMemory);
        commands.put("stack", EchoMonitoringCmd::executeStack);
        commands.put("monitor", EchoMonitoringCmd::executeMonitor);

        commands.put("reset", EchoCommands::cmdReset);

        // Register with Pulse CommandRegistry (if available)
        try {
            CommandRegistry.register("echo", "Echo Profiler 명령어", EchoCommands::handleEchoCommand);
            System.out.println("[Echo] Commands registered via Pulse CommandRegistry");
        } catch (NoClassDefFoundError e) {
            // Pulse not available, fallback to direct invocation
            System.out.println("[Echo] Commands registered (standalone mode)");
        }

        registered = true;
    }

    /**
     * Pulse CommandContext 기반 핸들러
     */
    private static void handleEchoCommand(CommandContext ctx) {
        String[] args = ctx.getRawArgs();
        if (args.length == 0) {
            cmdHelp(new String[0]);
            return;
        }

        String subCommand = args[0].toLowerCase();
        Consumer<String[]> handler = commands.get(subCommand);

        if (handler != null) {
            handler.accept(args);
        } else {
            ctx.reply("[Echo] Unknown command: " + subCommand);
            ctx.reply("[Echo] Use '/echo help' for available commands");
        }
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

    private static void cmdReset(String[] args) {
        EchoProfiler.getInstance().reset();
    }
}
