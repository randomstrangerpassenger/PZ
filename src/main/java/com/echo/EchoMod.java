package com.echo;

import com.echo.command.EchoCommands;
import com.echo.measure.EchoProfiler;
import com.echo.pulse.PulseEventAdapter;

/**
 * Echo Mod 진입점
 * 
 * Pulse 모드 로더에서 로드되는 메인 클래스
 */
public class EchoMod {

    public static final String MOD_ID = "echo";
    public static final String MOD_NAME = "Echo Profiler";
    public static final String VERSION = "0.1.0";

    private static boolean initialized = false;

    /**
     * 모드 초기화
     * Pulse에서 호출됨
     */
    public static void init() {
        if (initialized) {
            System.out.println("[Echo] Already initialized, skipping...");
            return;
        }

        System.out.println();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║     Echo Profiler v" + VERSION + " Initialized         ║");
        System.out.println("║     \"Observe, Don't Patch\"                    ║");
        System.out.println("╚═══════════════════════════════════════════════╝");
        System.out.println();

        // 명령어 등록
        EchoCommands.register();

        // Pulse 이벤트 어댑터 등록
        PulseEventAdapter.register();

        initialized = true;

        System.out.println("[Echo] Use '/echo help' for available commands");
    }

    /**
     * 모드 종료
     */
    public static void shutdown() {
        if (!initialized)
            return;

        EchoProfiler profiler = EchoProfiler.getInstance();
        if (profiler.isEnabled()) {
            System.out.println("[Echo] Auto-saving report before shutdown...");
            try {
                new com.echo.report.EchoReport(profiler)
                        .saveWithTimestamp("./echo_reports");
            } catch (Exception e) {
                System.err.println("[Echo] Failed to save report: " + e.getMessage());
            }
        }

        System.out.println("[Echo] Shutdown complete");
        initialized = false;
    }

    /**
     * 초기화 여부 확인
     */
    public static boolean isInitialized() {
        return initialized;
    }

    /**
     * 버전 문자열 반환
     */
    public static String getVersion() {
        return VERSION;
    }
}
