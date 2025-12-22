package com.fuse;

import com.fuse.config.FuseConfig;
import com.fuse.governor.RollingTickStats;
import com.fuse.governor.SpikePanicProtocol;
import com.fuse.governor.TickBudgetGovernor;
import com.fuse.guard.FailsoftController;
import com.fuse.guard.StreamingGuard;
import com.fuse.guard.VehicleGuard;
import com.fuse.hook.FuseHookAdapter;
import com.fuse.optimizer.FuseOptimizer;
import com.fuse.throttle.FuseStepPolicy;
import com.fuse.throttle.FuseThrottleController;
import com.pulse.api.profiler.ZombieHook;
import com.pulse.mod.PulseMod;

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
    public static final String VERSION = "1.1.0";

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
            System.out.println("[Fuse] RollingTickStats initialized");

            // Tick Budget Governor (컷오프 스위치)
            governor = new TickBudgetGovernor();
            governor.setForceCutoffMs(config.getForceCutoffMs());
            governor.setBatchCheckSize(config.getBatchCheckSize());

            // Spike Panic Protocol (슬라이딩 윈도우 + 점진적 복구)
            panicProtocol = new SpikePanicProtocol();

            System.out.println("[Fuse] Core safety components initialized");
        } catch (Exception e) {
            System.err.println("[Fuse] Failed to initialize safety components: " + e.getMessage());
            e.printStackTrace();
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

            System.out.println("[Fuse] Guards initialized");
        } catch (Exception e) {
            System.err.println("[Fuse] Failed to initialize guards: " + e.getMessage());
        }

        // ========================================
        // Phase 3: Hook Adapter 등록
        // ========================================

        try {
            hookAdapter = new FuseHookAdapter();
            ZombieHook.setCallback(hookAdapter);
            ZombieHook.profilingEnabled = true;
            System.out.println("[Fuse] ZombieHook callback registered");
        } catch (Exception e) {
            System.err.println("[Fuse] Failed to register ZombieHook: " + e.getMessage());
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

            ZombieHook.setThrottlePolicy(throttleController);
            System.out.println("[Fuse] ThrottleController registered (v1.1 with hysteresis)");
        } catch (Exception e) {
            System.err.println("[Fuse] Failed to register ThrottlePolicy: " + e.getMessage());
        }

        // ========================================
        // Phase 5: Step-level Throttle Policy
        // ========================================

        try {
            stepPolicy = new FuseStepPolicy();
            com.pulse.api.profiler.ZombieStepHook.setStepPolicy(stepPolicy);
            System.out.println("[Fuse] StepPolicy registered");
        } catch (Exception e) {
            System.err.println("[Fuse] Failed to register StepPolicy: " + e.getMessage());
        }

        // ========================================
        // Phase 6: Optimizer
        // ========================================

        optimizer = FuseOptimizer.getInstance();
        optimizer.enable();
        optimizer.setAutoOptimize(false);

        initialized = true;
        System.out.println("[Fuse] Initialization complete (v1.1 Stabilization)");
        System.out.println("[Fuse] Use /fuse status to view v1.1 component status");
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
            }

            // Failsoft 성공 기록
            if (failsoftController != null) {
                failsoftController.recordSuccess();
            }
        } catch (Throwable t) {
            // Failsoft 오류 기록
            if (failsoftController != null) {
                failsoftController.recordError(t);
            } else {
                System.err.println("[Fuse] onTick error: " + t.getMessage());
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
            System.out.println("[Fuse] No optimization target available");
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

        System.out.println();
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

    public void shutdown() {
        System.out.println("[Fuse] Shutting down...");

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
        System.out.println("[Fuse] Shutdown complete");
    }
}
