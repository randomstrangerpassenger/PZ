package com.echo;

import com.echo.command.EchoCommands;
import com.echo.measure.EchoProfiler;
import com.echo.session.SessionManager;
import com.echo.pulse.PulseEventAdapter;
import com.echo.pulse.SubProfilerBridge;
import com.echo.pulse.PathfindingBridge;
import com.echo.pulse.ZombieBridge;
import com.echo.pulse.IsoGridBridge;
import com.echo.spi.EchoProfilerProvider;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.mod.PulseMod;

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
            PulseLogger.debug("Echo", "Already initialized, skipping...");
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

            // v2.1: Shutdown hook - 비정상 종료 시에만 저장 (Alt+F4 등)
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                SessionManager manager = SessionManager.getInstance();
                manager.saveSync(); // 조건부 저장 (미저장 데이터가 있을 때만)
                manager.shutdownExecutor(); // Executor 정리
            }, "Echo-Shutdown-Hook"));

            PulseLogger.info("Echo", "Profiling is now active - session-based saving enabled");
        } catch (Exception e) {
            EchoRuntime.recordError("init", e);
            PulseLogger.error("Echo", "Initialization failed: " + e.getMessage(), e);
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
            PulseLogger.warn("Echo", "Warning: Failed to check Pulse API: " + e.getMessage());
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
            PulseLogger.warn("Echo", "Warning: Failed to check GameServer: " + e.getMessage());
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

        // Phase 0: Profiler 선 활성화 (다른 컴포넌트들이 상태를 체크하기 전에)
        com.echo.config.EchoConfig config = com.echo.config.EchoConfig.getInstance();
        com.echo.measure.EchoProfiler profiler = com.echo.measure.EchoProfiler.getInstance();

        profiler.enable();

        // Lua 프로파일링 설정 동기화 (EchoConfig → EchoProfiler)
        if (config.isLuaProfilingEnabled()) {
            profiler.enableLuaProfiling();
            PulseLogger.info("Echo", "✓ Lua Profiling PRE-ENABLED (from config)");
        }

        // 명령어 등록
        try {
            EchoCommands.register();
            PulseLogger.info("Echo", "✓ EchoCommands registered");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ EchoCommands.register() FAILED: " + t.getMessage(), t);
        }

        // Pulse 이벤트 어댑터 등록
        try {
            PulseEventAdapter.register();
            PulseLogger.info("Echo", "✓ PulseEventAdapter registered");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ PulseEventAdapter.register() FAILED: " + t.getMessage(), t);
        }

        // Echo 1.0: SubProfiler 브릿지 등록 (Pulse Mixin → Echo SubProfiler 연동)
        try {
            SubProfilerBridge.register();
            PulseLogger.info("Echo", "✓ SubProfilerBridge registered");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ SubProfilerBridge.register() FAILED: " + t.getMessage(), t);
        }

        // Echo 1.0: TickPhase 브릿지 등록 (Pulse Mixin → Echo TickPhaseProfiler 연동)
        try {
            com.echo.pulse.TickPhaseBridge.register();
            PulseLogger.info("Echo", "✓ TickPhaseBridge registered");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ TickPhaseBridge.register() FAILED: " + t.getMessage(), t);
        }

        // Echo 2.0: Lua Path Hit 프로브 등록 (30초 후 검증 로그)
        try {
            com.echo.lua.LuaPathHitBridge.register();
            PulseLogger.info("Echo", "✓ LuaPathHitBridge registered");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ LuaPathHitBridge.register() FAILED: " + t.getMessage(), t);
        }

        // Echo 1.0 Phase 4: Fuse Deep Analysis 브릿지 등록
        try {
            PathfindingBridge.register();
            PulseLogger.info("Echo", "✓ PathfindingBridge registered");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ PathfindingBridge.register() FAILED: " + t.getMessage(), t);
        }

        try {
            ZombieBridge.register();
            PulseLogger.info("Echo", "✓ ZombieBridge registered");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ ZombieBridge.register() FAILED: " + t.getMessage(), t);
        }

        try {
            IsoGridBridge.register();
            PulseLogger.info("Echo", "✓ IsoGridBridge registered");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ IsoGridBridge.register() FAILED: " + t.getMessage(), t);
        }

        // Echo 2.0: ProfilerBridge Sink 등록 (Fuse → Pulse → Echo 데이터 경로)
        try {
            com.echo.pulse.EchoProfilerSink.register();
            PulseLogger.info("Echo", "✓ EchoProfilerSink registered");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ EchoProfilerSink.register() FAILED: " + t.getMessage(), t);
        }

        // 키바인딩 등록
        try {
            com.echo.input.EchoKeyBindings.register();
            PulseLogger.info("Echo", "✓ EchoKeyBindings registered");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ EchoKeyBindings.register() FAILED: " + t.getMessage(), t);
        }

        // HUD 레이어 등록 (Pulse Native UI)
        try {
            com.echo.ui.EchoHUD.register();
            com.echo.ui.HotspotPanel.register();
            PulseLogger.info("Echo", "✓ EchoHUD, HotspotPanel registered");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ HUD registration FAILED: " + t.getMessage(), t);
        }

        // OptimizationPoint 동기화 (Pulse Registry에서 로드)
        try {
            com.echo.pulse.OptimizationPointSync.syncFromPulse();
            PulseLogger.info("Echo", "✓ OptimizationPointSync completed");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "✗ OptimizationPointSync FAILED: " + t.getMessage(), t);
        }

        // SPI 프로바이더 등록 (Pulse가 있을 때만)
        registerSpiProvider();

        // Phase 5: Service Registration using PulseServiceLocator
        registerServices();

        // 프로파일러 상태 최종 확인 (이미 Phase 0에서 활성화됨)
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║  [Echo] ✓ PROFILER ENABLED - Collecting Data  ║");
        System.out.println("╚═══════════════════════════════════════════════╝");

        // 활성화 확인 로그
        if (!profiler.isEnabled()) {
            PulseLogger.error("Echo", "CRITICAL ERROR: Profiler failed to enable!");
            PulseLogger.error("Echo", "Check for initialization errors above.");
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
                java.lang.reflect.Method registerMethod = registry.getClass()
                        .getMethod("register", Class.forName("com.pulse.api.spi.IProvider"));

                // EchoProfilerProvider 등록
                registerMethod.invoke(registry, new EchoProfilerProvider());
                PulseLogger.info("Echo", "Registered EchoProfilerProvider");

                // EchoHintProvider 등록 (Fuse 연동용)
                registerMethod.invoke(registry, com.echo.spi.EchoHintProvider.getInstance());
                PulseLogger.info("Echo", "Registered EchoHintProvider (id: echo.hints)");
            }
        } catch (ClassNotFoundException e) {
            PulseLogger.debug("Echo", "Running in standalone mode");
        } catch (Exception e) {
            PulseLogger.warn("Echo", "Warning: Failed to register SPI provider: " + e.getMessage());
        }
    }

    /**
     * Phase 5: Register Echo services to PulseServiceLocator
     * 
     * Note: INetworkMetrics, IRenderMetrics, IBottleneckDetector는
     * Pulse 정화 후 pulse-api에서 삭제되어 Echo 내부로 이동됨.
     * 서비스 등록은 더 이상 필요하지 않음.
     */
    private static void registerServices() {
        // Pulse 정화 후 서비스 등록 불필요
        // Echo 내부 클래스로 직접 접근 가능:
        // - com.echo.measure.NetworkMetrics
        // - com.echo.measure.RenderMetrics
        // - com.echo.analysis.BottleneckDetector
        PulseLogger.debug("Echo", "Service registration skipped (Pulse 2.0 purification)");
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

                report.printQualitySummary();

                PulseLogger.info("Echo", "Report saved: " + reportPath);
            } catch (Exception e) {
                PulseLogger.error("Echo", "Failed to save report: " + e.getMessage());
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
            PulseLogger.info("Echo", "Report flushed: " + reportPath);
        } catch (Exception e) {
            PulseLogger.error("Echo", "Failed to flush report: " + e.getMessage());
        }
    }

    public static boolean isInitialized() {
        return initialized;
    }

    public static String getVersion() {
        return VERSION;
    }
}
