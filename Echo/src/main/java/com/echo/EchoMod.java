package com.echo;

import com.echo.command.EchoCommands;
import com.echo.measure.EchoProfiler;
import com.echo.pulse.PulseEventAdapter;
import com.echo.pulse.SubProfilerBridge;
import com.echo.pulse.PathfindingBridge;
import com.echo.pulse.ZombieBridge;
import com.echo.pulse.IsoGridBridge;
import com.echo.spi.EchoProfilerProvider;
import com.pulse.mod.PulseMod;

/**
 * Echo Mod 진입점
 * 
 * Pulse 모드 로더에서 로드되는 메인 클래스
 */
public class EchoMod implements PulseMod {

    public static final String MOD_ID = "echo";
    public static final String MOD_NAME = "Echo Profiler";
    public static final String VERSION = EchoConstants.VERSION;

    private static boolean initialized = false;

    public EchoMod() {
        // PulseMod에서 인스턴스 관리
    }

    @Override
    public void onInitialize() {
        init();
    }

    @Override
    public void onUnload() {
        shutdown();
    }

    /** 모드 초기화 */
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

            // JVM shutdown hook 등록 (게임 종료 시 리포트 자동 저장)
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                shutdown();
            }, "Echo-Shutdown-Hook"));

            System.out.println("[Echo] Profiling is now active - data will be saved on game exit");
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
            // Pulse API unavailable
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
            // Dev environment
        } catch (Exception e) {
            System.out.println("[Echo] Warning: Failed to check GameServer: " + e.getMessage());
        }

        return false;
    }

    /** 내부 초기화 로직 */
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

        // Echo 1.0: SubProfiler 브릿지 등록 (Pulse Mixin → Echo SubProfiler 연동)
        SubProfilerBridge.register();

        // Echo 1.0: TickPhase 브릿지 등록 (Pulse Mixin → Echo TickPhaseProfiler 연동)
        com.echo.pulse.TickPhaseBridge.register();

        // Echo 1.0 Phase 4: Fuse Deep Analysis 브릿지 등록
        PathfindingBridge.register();
        ZombieBridge.register();
        IsoGridBridge.register();

        // 키바인딩 등록
        com.echo.input.EchoKeyBindings.register();

        // HUD 레이어 등록 (Pulse Native UI)
        com.echo.ui.EchoHUD.register();
        com.echo.ui.HotspotPanel.register();

        // OptimizationPoint 동기화 (Pulse Registry에서 로드)
        com.echo.pulse.OptimizationPointSync.syncFromPulse();

        // SPI 프로바이더 등록 (Pulse가 있을 때만)
        registerSpiProvider();

        // Phase 5: Service Registration using PulseServiceLocator
        registerServices();

        // 자동 프로파일링 시작 - 항상 활성화 (데이터 손실 방지)
        com.echo.config.EchoConfig config = com.echo.config.EchoConfig.getInstance();
        com.echo.measure.EchoProfiler profiler = com.echo.measure.EchoProfiler.getInstance();

        if (!config.isAutoStartProfiling()) {
            System.out.println(
                    "[Echo] WARNING: autoStartProfiling is disabled in config, but enabling anyway for safety!");
            System.out.println("[Echo] To disable profiling, use /echo off command in-game.");
        }

        profiler.enable();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║  [Echo] ✓ PROFILER ENABLED - Collecting Data  ║");
        System.out.println("╚═══════════════════════════════════════════════╝");

        // 활성화 확인 로그
        if (!profiler.isEnabled()) {
            System.err.println("[Echo] CRITICAL ERROR: Profiler failed to enable!");
            System.err.println("[Echo] Check for initialization errors above.");
        }
    }

    /**
     * Pulse SPI에 EchoProfilerProvider 등록
     */
    private static void registerSpiProvider() {
        try {
            // Pulse API 존재 확인
            Class<?> pulseClass = Class.forName("com.pulse.api.Pulse");
            java.lang.reflect.Method getRegistry = pulseClass.getMethod("getProviderRegistry");
            Object registry = getRegistry.invoke(null);

            if (registry != null) {
                // 프로바이더 등록
                java.lang.reflect.Method registerMethod = registry.getClass()
                        .getMethod("register", Class.forName("com.pulse.api.spi.IProvider"));
                registerMethod.invoke(registry, new EchoProfilerProvider());
                System.out.println("[Echo] Registered as Pulse SPI provider");
            }
        } catch (ClassNotFoundException e) {
            // Pulse API unavailable - standalone mode
            System.out.println("[Echo] Running in standalone mode");
        } catch (Exception e) {
            System.out.println("[Echo] Warning: Failed to register SPI provider: " + e.getMessage());
        }
    }

    /**
     * Phase 5: Register Echo services to PulseServiceLocator
     */
    private static void registerServices() {
        try {
            com.pulse.di.PulseServiceLocator locator = com.pulse.di.PulseServiceLocator.getInstance();
            locator.registerService(com.pulse.api.service.echo.INetworkMetrics.class,
                    com.echo.measure.NetworkMetrics.getInstance());
            locator.registerService(com.pulse.api.service.echo.IRenderMetrics.class,
                    com.echo.measure.RenderMetrics.getInstance());
            locator.registerService(com.pulse.api.service.echo.IBottleneckDetector.class,
                    com.echo.analysis.BottleneckDetector.getInstance());
            System.out.println("[Echo] Registered services to PulseServiceLocator");
        } catch (NoClassDefFoundError e) {
            // Pulse unavailable
            System.out.println("[Echo] PulseServiceLocator not found");
        } catch (Exception e) {
            System.err.println("[Echo] Failed to register services: " + e.getMessage());
        }
    }

    /** 모드 종료 */
    public static void shutdown() {
        if (!initialized) {
            return;
        }

        EchoProfiler profiler = EchoProfiler.getInstance();
        com.echo.config.EchoConfig config = com.echo.config.EchoConfig.getInstance();

        // 리포트 자동 저장
        if (config.isAutoSaveReports()) {
            try {
                com.echo.report.EchoReport report = new com.echo.report.EchoReport(profiler);
                String reportPath = report.saveWithTimestamp(config.getReportDirectory());

                // Phase 6.2: Print Session Summary
                report.printQualitySummary();

                System.out.println("[Echo] Report saved: " + reportPath);
            } catch (Exception e) {
                System.err.println("[Echo] Failed to save report: " + e.getMessage());
            }
        }

        // 프로파일러 비활성화
        if (profiler.isEnabled()) {
            profiler.disable();
        }

        initialized = false;
    }

    /** 리포트 강제 저장 (종료 없이) */
    public static void flush() {
        if (!initialized)
            return;

        try {
            EchoProfiler profiler = EchoProfiler.getInstance();
            com.echo.config.EchoConfig config = com.echo.config.EchoConfig.getInstance();

            String reportPath = new com.echo.report.EchoReport(profiler)
                    .saveWithTimestamp(config.getReportDirectory());
            System.out.println("[Echo] Report flushed: " + reportPath);
        } catch (Exception e) {
            System.err.println("[Echo] Failed to flush report: " + e.getMessage());
        }
    }

    public static boolean isInitialized() {
        return initialized;
    }

    public static String getVersion() {
        return VERSION;
    }
}
