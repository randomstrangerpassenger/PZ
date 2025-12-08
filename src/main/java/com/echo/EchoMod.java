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
    public static final String VERSION = "0.2.0";

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

        // Phase 0: 서버 환경 감지
        if (isServerEnvironment()) {
            EchoRuntime.enableSilentMode("Server environment detected");
            return;
        }

        // Fail-soft wrapper
        try {
            initInternal();
            initialized = true;
            System.out.println("[Echo] Use '/echo help' for available commands");
        } catch (Exception e) {
            EchoRuntime.recordError("init", e);
            System.err.println("[Echo] Initialization failed: " + e.getMessage());
        }
    }

    /**
     * 서버 환경 감지
     * GameServer.bServer 또는 Pulse API로 확인
     */
    private static boolean isServerEnvironment() {
        try {
            // Pulse API 우선 체크
            Class<?> pulseSide = Class.forName("com.pulse.api.PulseSide");
            java.lang.reflect.Method isServer = pulseSide.getMethod("isServer");
            Object result = isServer.invoke(null);
            if (Boolean.TRUE.equals(result)) {
                return true;
            }
        } catch (ClassNotFoundException e) {
            // Pulse API 없음 - 폴백으로 PZ API 체크
        } catch (Exception e) {
            System.out.println("[Echo] Warning: Failed to check Pulse API: " + e.getMessage());
        }

        try {
            // PZ GameServer.bServer 체크
            Class<?> gameServer = Class.forName("zombie.network.GameServer");
            java.lang.reflect.Field bServer = gameServer.getField("bServer");
            Object result = bServer.get(null);
            if (Boolean.TRUE.equals(result)) {
                return true;
            }
        } catch (ClassNotFoundException e) {
            // 개발 환경 - 서버 아님으로 간주
        } catch (Exception e) {
            System.out.println("[Echo] Warning: Failed to check GameServer: " + e.getMessage());
        }

        return false;
    }

    /**
     * 내부 초기화 로직
     */
    private static void initInternal() {
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

        // 키바인딩 등록
        com.echo.input.EchoKeyBindings.register();
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
                // Phase 2: 상세 에러 로깅
                System.err.println("[Echo] Failed to save report: " + e.getMessage());
                System.err.println("[Echo] Stack trace for debugging:");
                e.printStackTrace(System.err);
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
