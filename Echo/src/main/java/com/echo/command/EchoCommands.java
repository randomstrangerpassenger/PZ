package com.echo.command;

import com.echo.command.impl.*;
import com.echo.measure.EchoProfiler;
import com.pulse.api.command.ICommandContext;
import com.pulse.api.di.PulseServices;
import com.pulse.api.log.PulseLogger;

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
     * 명령어 등록 (Pulse API 통합)
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

        // Register with Pulse CommandRegistry via PulseServices API
        try {
            PulseServices.commands().register("echo", "Echo Profiler 명령어", EchoCommands::handleEchoCommand);
            PulseLogger.info("Echo", "Commands registered via Pulse API");
        } catch (IllegalStateException | NoClassDefFoundError e) {
            // Pulse not available, fallback to direct invocation
            PulseLogger.info("Echo", "Commands registered (standalone mode)");
        }

        registered = true;
    }

    /**
     * Pulse ICommandContext 기반 핸들러
     */
    private static void handleEchoCommand(ICommandContext ctx) {
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
            PulseLogger.warn("Echo", "Unknown command: " + subCommand);
            PulseLogger.warn("Echo", "Use '/echo help' for available commands");
            return false;
        }
    }

    // --- Command Handlers ---

    private static void cmdHelp(String[] args) {
        PulseLogger.info("Echo", "");
        PulseLogger.info("Echo", "╔═══════════════════════════════════════════════╗");
        PulseLogger.info("Echo", "║           Echo Profiler Commands              ║");
        PulseLogger.info("Echo", "╠═══════════════════════════════════════════════╣");
        PulseLogger.info("Echo", "║  Basic Commands:                              ║");
        PulseLogger.info("Echo", "║  /echo help        - Show this help           ║");
        PulseLogger.info("Echo", "║  /echo enable      - Start profiling          ║");
        PulseLogger.info("Echo", "║  /echo disable     - Stop profiling           ║");
        PulseLogger.info("Echo", "║  /echo status      - Show current status      ║");
        PulseLogger.info("Echo", "║  /echo report      - Generate report          ║");
        PulseLogger.info("Echo", "║  /echo report json - Save JSON report         ║");
        PulseLogger.info("Echo", "║  /echo reset       - Reset all statistics     ║");
        PulseLogger.info("Echo", "╠═══════════════════════════════════════════════╣");
        PulseLogger.info("Echo", "║  Lua Profiling:                               ║");
        PulseLogger.info("Echo", "║  /echo lua on      - Enable Lua profiling     ║");
        PulseLogger.info("Echo", "║  /echo lua off     - Disable Lua profiling    ║");
        PulseLogger.info("Echo", "╠═══════════════════════════════════════════════╣");
        PulseLogger.info("Echo", "║  Configuration:                               ║");
        PulseLogger.info("Echo", "║  /echo config      - Show current config      ║");
        PulseLogger.info("Echo", "║  /echo config set threshold <ms>              ║");
        PulseLogger.info("Echo", "║  /echo memory      - Show memory status       ║");
        PulseLogger.info("Echo", "╠═══════════════════════════════════════════════╣");
        PulseLogger.info("Echo", "║  Advanced (Phase 4):                          ║");
        PulseLogger.info("Echo", "║  /echo stack on    - Enable spike stack trace ║");
        PulseLogger.info("Echo", "║  /echo overhead    - Measure profiler cost    ║");
        PulseLogger.info("Echo", "║  /echo monitor start [port] - Start HTTP API  ║");
        PulseLogger.info("Echo", "║  /echo test        - Run quick test           ║");
        PulseLogger.info("Echo", "╚═══════════════════════════════════════════════╝");
        PulseLogger.info("Echo", "");
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
