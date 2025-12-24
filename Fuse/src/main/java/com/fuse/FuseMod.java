package com.fuse;

import com.fuse.config.FuseConfig;
import com.fuse.governor.RollingTickStats;
import com.fuse.governor.SpikePanicProtocol;
import com.fuse.governor.TickBudgetGovernor;
import com.fuse.guard.FailsoftController;
import com.fuse.guard.IOGuard;
import com.fuse.guard.StreamingGuard;
import com.fuse.guard.VehicleGuard;
import com.fuse.hook.FuseHookAdapter;
import com.fuse.optimizer.FuseOptimizer;
import com.fuse.telemetry.ReasonStats;
import com.fuse.telemetry.TelemetryReason;
import com.fuse.throttle.FuseStepPolicy;
import com.fuse.throttle.FuseThrottleController;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.ZombieHook;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEndEvent;
import com.pulse.event.save.PostSaveEvent;
import com.pulse.event.save.PreSaveEvent;
import com.pulse.mod.PulseMod;

import java.util.Map;

/**
 * Fuse - Performance Optimizer for Project Zomboid
 * 
 * v1.1: 안정성과 예측 가능성 확보
 * - Tick Budget Governor (컷오프 스위치)
 * - Spike Panic Protocol (슬라이딩 윈도우 + 점진적 복구)
 * - Window-based Hysteresis
 * - Vehicle/Streaming Guards
 * - Failsoft Controller
 * 
 * @since Fuse 0.3.0
 * @since Fuse 1.1.0 - Stabilization Release
 */
public class FuseMod implements PulseMod {

    public static final String MOD_ID = "Fuse";
    public static final String VERSION = "2.0.0";

    private static FuseMod instance;

    // --- Core Components ---
    private FuseOptimizer optimizer;
    private FuseHookAdapter hookAdapter;
    private FuseThrottleController throttleController;
    private FuseStepPolicy stepPolicy;

    // --- v1.1 Stabilization Components ---
    private TickBudgetGovernor governor;
    private SpikePanicProtocol panicProtocol;
    private RollingTickStats stats;
    private VehicleGuard vehicleGuard;
    private StreamingGuard streamingGuard;
    private FailsoftController failsoftController;
    private ReasonStats reasonStats;

    // --- v2.0 IOGuard ---
    private IOGuard ioGuard;

    // --- 주기적 로깅 ---
    private long tickCounter = 0;
    private static final long LOG_INTERVAL_TICKS = 3600; // 60초 (60fps 기준)

    private boolean initialized = false;

    public static FuseMod getInstance() {
        return instance;
    }

    @Override
    public void onInitialize() {
        init();
    }

    @Override
    public void onUnload() {
        shutdown();
    }

    public void init() {
        instance = this;
        System.out.println();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║     Fuse v" + VERSION + " - Stabilization Release     ║");
        System.out.println("║     \"Always Safe, Always Predictable\"         ║");
        System.out.println("╚═══════════════════════════════════════════════╝");

        // Config 초기화
        FuseConfig config = FuseConfig.getInstance();

        // ========================================
        // Phase 1: v1.1 Core Safety Components
        // ========================================

        try {
            // Rolling Tick Stats (윈도우 통계)
            stats = new RollingTickStats();
            PulseLogger.info("Fuse", "RollingTickStats initialized");

            // Tick Budget Governor (컷오프 스위치)
            governor = new TickBudgetGovernor();
            governor.setForceCutoffMs(config.getForceCutoffMs());
            governor.setBatchCheckSize(config.getBatchCheckSize());

            // Spike Panic Protocol (슬라이딩 윈도우 + 점진적 복구)
            panicProtocol = new SpikePanicProtocol();

            // Reason Stats (개입 이유 통계)
            reasonStats = new ReasonStats();

            PulseLogger.info("Fuse", "Core safety components initialized");
        } catch (Exception e) {
            PulseLogger.error("Fuse", "Failed to initialize safety components: " + e.getMessage(), e);
        }

        // ========================================
        // Phase 2: Guards
        // ========================================

        try {
            // Vehicle Guard
            vehicleGuard = new VehicleGuard();
            vehicleGuard.setSpeedEntryKmh(config.getVehicleSpeedEntryKmh());
            vehicleGuard.setSpeedExitKmh(config.getVehicleSpeedExitKmh());

            // Streaming Guard
            streamingGuard = new StreamingGuard();

            // Failsoft Controller
            failsoftController = new FailsoftController();
            failsoftController.setMaxConsecutiveErrors(config.getMaxConsecutiveErrors());

            // IOGuard (v2.0)
            ioGuard = new IOGuard();
            ioGuard.loadConfig(config);

            // IOGuard EventBus 구독
            EventBus.subscribe(PreSaveEvent.class, ioGuard::onPreSave, MOD_ID);
            EventBus.subscribe(PostSaveEvent.class, ioGuard::onPostSave, MOD_ID);

            PulseLogger.info("Fuse", "Guards initialized (v2.0 with IOGuard)");
        } catch (Exception e) {
            PulseLogger.error("Fuse", "Failed to initialize guards: " + e.getMessage(), e);
        }

        // ========================================
        // Phase 3: Hook Adapter 등록
        // ========================================

        try {
            hookAdapter = new FuseHookAdapter();
            ZombieHook.setCallback(hookAdapter);
            ZombieHook.profilingEnabled = true;
            PulseLogger.info("Fuse", "ZombieHook callback registered");
        } catch (Exception e) {
            PulseLogger.error("Fuse", "Failed to register ZombieHook: " + e.getMessage(), e);
        }

        // ========================================
        // Phase 4: Throttle Controller with v1.1 Integration
        // ========================================

        try {
            throttleController = new FuseThrottleController();

            // v1.1 컴포넌트 연동
            throttleController.setGovernor(governor);
            throttleController.setPanicProtocol(panicProtocol);
            throttleController.setStats(stats);
            throttleController.setGuards(vehicleGuard, streamingGuard);
            throttleController.setReasonStats(reasonStats);

            // v2.0 IOGuard 연동
            throttleController.setIOGuard(ioGuard);

            ZombieHook.setThrottlePolicy(throttleController);
            PulseLogger.info("Fuse", "ThrottleController registered (v2.0 with IOGuard)");
        } catch (Exception e) {
            PulseLogger.error("Fuse", "Failed to register ThrottlePolicy: " + e.getMessage(), e);
        }

        // ========================================
        // Phase 5: Step-level Throttle Policy
        // ========================================

        try {
            stepPolicy = new FuseStepPolicy();
            com.pulse.api.profiler.ZombieStepHook.setStepPolicy(stepPolicy);
            PulseLogger.info("Fuse", "StepPolicy registered");
        } catch (Exception e) {
            PulseLogger.error("Fuse", "Failed to register StepPolicy: " + e.getMessage(), e);
        }

        // ========================================
        // Phase 6: Optimizer
        // ========================================

        optimizer = FuseOptimizer.getInstance();
        optimizer.enable();
        optimizer.setAutoOptimize(false);

        // ========================================
        // Phase 7: Tick Event Subscription (로그 출력용)
        // ========================================
        try {
            EventBus.subscribe(GameTickEndEvent.class, event -> {
                onTick();
            }, MOD_ID);
            PulseLogger.info("Fuse", "GameTickEndEvent subscription active");
        } catch (Exception e) {
            PulseLogger.warn("Fuse", "Failed to subscribe to GameTickEndEvent: " + e.getMessage());
        }

        initialized = true;
        PulseLogger.info("Fuse", "Initialization complete (v1.1 Stabilization)");
        PulseLogger.info("Fuse", "Use /fuse status to view v1.1 component status");
    }

    /**
     * 게임 틱에서 호출
     */
    public void onTick() {
        if (!initialized) {
            return;
        }

        // Failsoft 체크 - 개입 비활성화 시 바닐라 동작
        if (failsoftController != null && failsoftController.isInterventionDisabled()) {
            return;
        }

        try {
            // Governor: 틱 시작
            if (governor != null) {
                governor.beginTick();
            }

            // 옵티마이저 업데이트
            optimizer.update();

            // Governor: 틱 종료
            if (governor != null) {
                governor.endTick();
                double lastTickMs = governor.getLastTickMs();

                // 통계 기록
                if (stats != null) {
                    stats.record(lastTickMs);
                }

                // Panic Protocol 기록
                if (panicProtocol != null) {
                    panicProtocol.recordTickDuration((long) lastTickMs);
                }

                // Streaming Guard 기록
                if (streamingGuard != null) {
                    streamingGuard.recordTickDuration((long) lastTickMs);
                }

                // IOGuard 틱 (v2.0)
                if (ioGuard != null) {
                    ioGuard.tick();
                }
            }

            if (failsoftController != null) {
                failsoftController.recordSuccess();
            }

            // 주기적 상태 로깅 (60초마다)
            tickCounter++;
            if (tickCounter % LOG_INTERVAL_TICKS == 0) {
                logStatusSummary();
            }
        } catch (Throwable t) {
            // Failsoft 오류 기록
            if (failsoftController != null) {
                failsoftController.recordError(t);
            } else {
                PulseLogger.error("Fuse", "onTick error: " + t.getMessage(), t);
            }
        }
    }

    /** 자동 최적화 토글 */
    public void toggleAutoOptimize() {
        optimizer.setAutoOptimize(!optimizer.isAutoOptimize());
    }

    /** 현재 타겟에 수동 최적화 적용 */
    public void applyCurrentTarget() {
        var target = optimizer.getCurrentTarget();
        if (target != null) {
            optimizer.applyOptimization(target);
        } else {
            PulseLogger.info("Fuse", "No optimization target available");
        }
    }

    /** 상태 출력 (v1.1 확장) */
    public void printStatus() {
        System.out.println();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║         FUSE v1.1 STABILIZATION STATUS        ║");
        System.out.println("╚═══════════════════════════════════════════════╝");

        // Failsoft 상태
        if (failsoftController != null && failsoftController.isInterventionDisabled()) {
            System.out.println();
            System.out.println("  ⚠️  FAILSOFT: Intervention DISABLED");
            failsoftController.printStatus();
            return;
        }

        // Panic 상태
        if (panicProtocol != null) {
            System.out.println();
            System.out.println("  Panic State: " + panicProtocol.getState());
            System.out.println("  Panic Multiplier: " + panicProtocol.getThrottleMultiplier());
        }

        // Governor 상태
        if (governor != null) {
            System.out.println();
            governor.printStatus();
        }

        // Guards 상태
        System.out.println();
        System.out.println("  Guards:");
        if (vehicleGuard != null) {
            System.out.println("    Vehicle: " + (vehicleGuard.isPassiveMode() ? "PASSIVE" : "normal"));
        }
        if (streamingGuard != null) {
            System.out.println("    Streaming: " + (streamingGuard.isYieldMode() ? "YIELD" : "normal"));
        }
        if (ioGuard != null) {
            System.out.println("    IOGuard: " + ioGuard.getCurrentState() +
                    " (multiplier=" + String.format("%.2f", ioGuard.getBudgetMultiplier()) + ")");
        }

        // Throttle Controller 상태
        if (throttleController != null) {
            System.out.println();
            throttleController.printStatus();
        }

        // Optimizer 상태
        var status = optimizer.getStatus();
        System.out.println();
        System.out.println("  Optimizer:");
        System.out.println("    Enabled:       " + status.get("enabled"));
        System.out.println("    Auto-Optimize: " + status.get("auto_optimize"));
        System.out.println("    Applied:       " + status.get("optimizations_applied"));

        // v1.1: Reason 통계
        if (reasonStats != null && reasonStats.getTotalCount() > 0) {
            System.out.println();
            System.out.println("  Intervention Reasons (Top 3):");
            var topReasons = reasonStats.getTop(3);
            int rank = 1;
            for (Map.Entry<TelemetryReason, Long> entry : topReasons) {
                System.out.println("    " + rank + ". " + entry.getKey().name() + ": " + entry.getValue());
                rank++;
            }
            System.out.println("    Total: " + reasonStats.getTotalCount());
        }

        System.out.println();
    }

    /**
     * 주기적 상태 요약 로깅 (콘솔 확인용).
     * 60초마다 자동 출력.
     */
    private void logStatusSummary() {
        StringBuilder sb = new StringBuilder();
        sb.append("\n========== [Fuse v2.0] 60s Status Summary ==========\n");

        // Tick 카운터
        sb.append("  Ticks: ").append(tickCounter).append("\n");

        // Failsoft 상태
        if (failsoftController != null && failsoftController.isInterventionDisabled()) {
            sb.append("  ⚠️  FAILSOFT: Intervention DISABLED\n");
        }

        // Panic 상태
        if (panicProtocol != null) {
            sb.append("  Panic: ").append(panicProtocol.getState())
                    .append(" (multiplier=").append(String.format("%.2f", panicProtocol.getThrottleMultiplier()))
                    .append(")\n");
        }

        // Governor 상태
        if (governor != null) {
            sb.append("  Governor: cutoffs=").append(governor.getTotalCutoffs())
                    .append(", last=").append(String.format("%.2f", governor.getLastTickMs())).append("ms\n");
        }

        // Guards 상태
        sb.append("  Guards: vehicle=")
                .append(vehicleGuard != null && vehicleGuard.isPassiveMode() ? "PASSIVE" : "normal")
                .append(", streaming=")
                .append(streamingGuard != null && streamingGuard.isYieldMode() ? "YIELD" : "normal").append("\n");

        // IOGuard 상태 (v2.0)
        if (ioGuard != null) {
            sb.append("  IOGuard: ").append(ioGuard.getCurrentState())
                    .append(" (multiplier=").append(String.format("%.2f", ioGuard.getBudgetMultiplier()))
                    .append(", events=").append(ioGuard.getTotalIOEvents())
                    .append(", avgMs=").append(ioGuard.getAverageIOTimeMs())
                    .append(", timeouts=").append(ioGuard.getTimeoutCount())
                    .append(")\n");
        }

        // v1.1: Reason 통계
        if (reasonStats != null && reasonStats.getTotalCount() > 0) {
            sb.append("  Intervention Reasons (Top 3):\n");
            var topReasons = reasonStats.getTop(3);
            int rank = 1;
            for (Map.Entry<TelemetryReason, Long> entry : topReasons) {
                sb.append("    ").append(rank).append(". ").append(entry.getKey().name())
                        .append(": ").append(entry.getValue()).append("\n");
                rank++;
            }
            sb.append("    Total: ").append(reasonStats.getTotalCount()).append("\n");
        } else {
            sb.append("  Intervention Reasons: (none yet)\n");
        }

        sb.append("=====================================================\n");

        PulseLogger.info("Fuse", sb.toString());
    }

    // --- Getters ---

    public FuseOptimizer getOptimizer() {
        return optimizer;
    }

    public FuseThrottleController getThrottleController() {
        return throttleController;
    }

    public TickBudgetGovernor getGovernor() {
        return governor;
    }

    public SpikePanicProtocol getPanicProtocol() {
        return panicProtocol;
    }

    public FailsoftController getFailsoftController() {
        return failsoftController;
    }

    public ReasonStats getReasonStats() {
        return reasonStats;
    }

    public IOGuard getIOGuard() {
        return ioGuard;
    }

    public void shutdown() {
        PulseLogger.info("Fuse", "Shutting down...");

        // Cleanup hook callback
        try {
            ZombieHook.setCallback(null);
            ZombieHook.profilingEnabled = false;
        } catch (Exception ignored) {
        }

        if (optimizer != null) {
            optimizer.disable();
        }

        initialized = false;
        PulseLogger.info("Fuse", "Shutdown complete");
    }
}
