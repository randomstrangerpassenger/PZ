package com.fuse;

import com.fuse.area7.FusePathfindingGuard;
import com.fuse.config.FuseConfig;
import com.fuse.governor.AdaptiveGate;
import com.fuse.governor.ItemGovernor;
import com.fuse.governor.RollingTickStats;
import com.fuse.governor.SpikePanicProtocol;
import com.fuse.governor.TickBudgetGovernor;
import com.fuse.guard.FailsoftController;
import com.fuse.guard.StreamingGuard;
import com.fuse.guard.VehicleGuard;
import com.fuse.hook.FuseHookAdapter;
import com.fuse.optimizer.FuseOptimizer;
import com.fuse.telemetry.FuseSnapshotProvider;
import com.fuse.telemetry.ReasonStats;
import com.fuse.telemetry.TelemetryReason;
import com.fuse.throttle.FuseStepPolicy;
import com.fuse.throttle.FuseThrottleController;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.ZombieHook;
import com.pulse.api.di.PulseServices;
import com.pulse.api.event.lifecycle.GameTickEndEvent;
import com.pulse.api.event.lifecycle.GameTickStartEvent;

import java.util.Map;

/**
 * Fuse 라이프사이클 관리자.
 * 
 * 모든 초기화, 틱 처리, 종료 로직을 담당합니다.
 * FuseMod에서 분리되어 단일 책임 원칙을 준수합니다.
 * 
 * @since Fuse 2.4.0
 */
public class FuseLifecycle {

    private static final String LOG = "Fuse";
    private static final long LOG_INTERVAL_TICKS = 3600; // 60초

    private final FuseComponentRegistry registry;
    private long tickCounter = 0;
    private boolean initialized = false;

    public FuseLifecycle(FuseComponentRegistry registry) {
        this.registry = registry;
    }

    // ═══════════════════════════════════════════════════════════════
    // Initialization
    // ═══════════════════════════════════════════════════════════════

    public void init() {
        System.out.println();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║     Fuse v" + FuseMod.VERSION + " - Stabilization Release     ║");
        System.out.println("║     \"Always Safe, Always Predictable\"         ║");
        System.out.println("╚═══════════════════════════════════════════════╝");

        FuseConfig config = FuseConfig.getInstance();

        initPhase1CoreSafety(config);
        initPhase2Guards(config);
        initPhase4HookAdapter();
        initPhase4ThrottleController(config);
        initPhase4ItemGovernor();
        initPhase5StepPolicy();
        initPhase5PathfindingGuard();
        initPhase6Optimizer();
        initPhase7EventSubscription();

        initialized = true;
        PulseLogger.info(LOG, "Initialization complete (v1.1 Stabilization)");
        PulseLogger.info(LOG, "Use /fuse status to view v1.1 component status");
    }

    private void initPhase1CoreSafety(FuseConfig config) {
        try {
            registry.setStats(new RollingTickStats());
            PulseLogger.info(LOG, "RollingTickStats initialized");

            TickBudgetGovernor governor = new TickBudgetGovernor();
            governor.setForceCutoffMs(config.getForceCutoffMs());
            governor.setBatchCheckSize(config.getBatchCheckSize());
            registry.setGovernor(governor);

            registry.setPanicProtocol(new SpikePanicProtocol());
            registry.setReasonStats(new ReasonStats());

            PulseLogger.info(LOG, "Core safety components initialized");
        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to initialize safety components: " + e.getMessage(), e);
        }
    }

    private void initPhase2Guards(FuseConfig config) {
        try {
            VehicleGuard vehicleGuard = new VehicleGuard();
            vehicleGuard.setSpeedEntryKmh(config.getVehicleSpeedEntryKmh());
            vehicleGuard.setSpeedExitKmh(config.getVehicleSpeedExitKmh());
            registry.setVehicleGuard(vehicleGuard);

            registry.setStreamingGuard(new StreamingGuard());

            FailsoftController failsoftController = new FailsoftController();
            failsoftController.setMaxConsecutiveErrors(config.getMaxConsecutiveErrors());
            registry.setFailsoftController(failsoftController);

            PulseLogger.info(LOG, "Guards initialized (v2.3 - IO/GC guards removed)");
        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to initialize guards: " + e.getMessage(), e);
        }
    }

    private void initPhase4HookAdapter() {
        try {
            registry.setHookAdapter(FuseHookAdapter.register());
            PulseLogger.info(LOG, "ZombieHook callback registered (Phase 4 - Direct API)");
        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to register ZombieHook: " + e.getMessage(), e);
        }
    }

    private void initPhase4ThrottleController(FuseConfig config) {
        try {
            FuseThrottleController throttleController = new FuseThrottleController();
            throttleController.setGovernor(registry.getGovernor());
            throttleController.setPanicProtocol(registry.getPanicProtocol());
            throttleController.setStats(registry.getStats());
            throttleController.setGuards(registry.getVehicleGuard(), registry.getStreamingGuard());
            throttleController.setReasonStats(registry.getReasonStats());

            // v2.5: AdaptiveGate 연동
            if (config.isEnableAdaptiveGate()) {
                AdaptiveGate adaptiveGate = new AdaptiveGate(
                        registry.getStats(),
                        registry.getPanicProtocol(),
                        registry.getReasonStats());
                throttleController.setAdaptiveGate(adaptiveGate);
                registry.setAdaptiveGate(adaptiveGate);
                registry.getGovernor().setReasonStats(registry.getReasonStats());
                PulseLogger.info(LOG, "AdaptiveGate enabled (v2.5)");

                // v2.5: FuseSnapshotProvider 초기화
                FuseSnapshotProvider snapshotProvider = new FuseSnapshotProvider(
                        registry.getHookAdapter(),
                        registry.getReasonStats(),
                        adaptiveGate,
                        registry.getGovernor());
                registry.setSnapshotProvider(snapshotProvider);

                // Bundle B v4: Pulse Registry에 SPI provider 등록 (1회만 시도)
                try {
                    snapshotProvider.updateStatus();
                    com.pulse.api.Pulse.getProviderRegistry().register(snapshotProvider);
                    PulseLogger.info(LOG, "FuseSnapshotProvider registered to Pulse SPI (Bundle B)");
                } catch (Exception e) {
                    // v4: 재등록 시도 없음 - 실패만 마킹
                    snapshotProvider.setFailed("REGISTRATION_FAILED", e.getMessage());
                    PulseLogger.warn(LOG, "Failed to register FuseSnapshotProvider: " + e.getMessage());
                }

                PulseLogger.info(LOG, "FuseSnapshotProvider initialized (v2.5)");
            }

            registry.setThrottleController(throttleController);

            try {
                ZombieHook.getInstance().setThrottlePolicy(throttleController);
                PulseLogger.info(LOG, "ThrottleController registered via IZombieHook (v2.1)");
            } catch (Exception e) {
                PulseLogger.warn(LOG, "ZombieHook.setThrottlePolicy failed: " + e.getMessage());
            }
        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to register ThrottlePolicy: " + e.getMessage(), e);
        }
    }

    private void initPhase4ItemGovernor() {
        try {
            ItemGovernor itemGovernor = new ItemGovernor();
            registry.setItemGovernor(itemGovernor);

            try {
                Class<?> targetClass = Class.forName("zombie.iso.objects.IsoWorldInventoryObject");
                java.lang.reflect.Method setPolicyMethod = targetClass.getDeclaredMethod(
                        "Pulse$setPolicy",
                        com.pulse.api.world.IWorldObjectThrottlePolicy.class);
                setPolicyMethod.setAccessible(true);
                setPolicyMethod.invoke(null, itemGovernor);
                PulseLogger.info(LOG, "ItemGovernor injected into WorldItemMixin (Phase 4 - Direct API)");
            } catch (ClassNotFoundException e) {
                PulseLogger.debug(LOG, "WorldItemMixin not found - item throttling not available");
            } catch (Exception e) {
                PulseLogger.error(LOG, "Failed to inject policy into WorldItemMixin: " + e.getMessage());
            }

            PulseLogger.info(LOG, "ItemGovernor initialized (Phase 4 - IWorldObjectThrottlePolicy)");
        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to register ThrottlePolicy: " + e.getMessage(), e);
        }
    }

    private void initPhase5StepPolicy() {
        try {
            FuseStepPolicy stepPolicy = new FuseStepPolicy();
            registry.setStepPolicy(stepPolicy);

            try {
                com.pulse.api.profiler.ZombieStepHook.setStepPolicy(stepPolicy);
                PulseLogger.info(LOG, "StepPolicy registered via ZombieStepHook (Direct API)");
            } catch (Exception e) {
                PulseLogger.warn(LOG, "ZombieStepHook.setStepPolicy failed: " + e.getMessage());
            }
        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to register StepPolicy: " + e.getMessage(), e);
        }
    }

    private void initPhase5PathfindingGuard() {
        try {
            FusePathfindingGuard pathfindingGuard = new FusePathfindingGuard(registry.getReasonStats());
            pathfindingGuard.register();
            registry.setPathfindingGuard(pathfindingGuard);
            PulseLogger.info(LOG, "Area 7 PathfindingGuard initialized");
        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to initialize PathfindingGuard: " + e.getMessage(), e);
        }
    }

    private void initPhase6Optimizer() {
        FuseOptimizer optimizer = FuseOptimizer.getInstance();
        optimizer.enable();
        optimizer.setAutoOptimize(false);
        registry.setOptimizer(optimizer);

        connectHintProvider(optimizer);
    }

    private void connectHintProvider(FuseOptimizer optimizer) {
        try {
            com.pulse.api.Pulse.getProviderRegistry()
                    .getProviders(com.pulse.api.spi.IOptimizationHintProvider.class)
                    .stream()
                    .filter(p -> "echo.hints".equals(p.getId()))
                    .findFirst()
                    .ifPresent(provider -> {
                        optimizer.setHintProvider(provider);
                        PulseLogger.info(LOG, "Connected to EchoHintProvider (id: " + provider.getId() + ")");
                    });
        } catch (Exception e) {
            PulseLogger.debug(LOG, "EchoHintProvider not available: " + e.getMessage());
        }
    }

    private void initPhase7EventSubscription() {
        try {
            PulseServices.events().subscribe(GameTickStartEvent.class, event -> {
                FusePathfindingGuard guard = registry.getPathfindingGuard();
                if (guard != null) {
                    guard.onTickStart(tickCounter);
                }
            }, FuseMod.MOD_ID);

            PulseServices.events().subscribe(GameTickEndEvent.class, event -> {
                onTick();
                FusePathfindingGuard guard = registry.getPathfindingGuard();
                if (guard != null) {
                    guard.onTickEnd(tickCounter);
                }
            }, FuseMod.MOD_ID);

            PulseLogger.info(LOG, "GameTick event subscriptions active (with Area 7)");
        } catch (Exception e) {
            PulseLogger.warn(LOG, "Failed to subscribe to GameTick events: " + e.getMessage());
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Tick Processing
    // ═══════════════════════════════════════════════════════════════

    public void onTick() {
        if (!initialized) {
            return;
        }

        FailsoftController failsoft = registry.getFailsoftController();
        if (failsoft != null && failsoft.isInterventionDisabled()) {
            return;
        }

        try {
            TickBudgetGovernor governor = registry.getGovernor();
            if (governor != null) {
                governor.beginTick();
            }

            // v2.5: AdaptiveGate 평가 (틱당 1회)
            AdaptiveGate gate = registry.getAdaptiveGate();
            if (gate != null) {
                gate.evaluateThisTick();
            }

            FuseOptimizer optimizer = registry.getOptimizer();
            if (optimizer != null) {
                optimizer.update();
            }

            if (governor != null) {
                governor.endTick();
                double lastTickMs = governor.getLastTickMs();

                RollingTickStats stats = registry.getStats();
                if (stats != null) {
                    stats.record(lastTickMs);
                }

                SpikePanicProtocol panic = registry.getPanicProtocol();
                if (panic != null) {
                    panic.recordTickDuration((long) lastTickMs);
                }

                StreamingGuard streaming = registry.getStreamingGuard();
                if (streaming != null) {
                    streaming.recordTickDuration((long) lastTickMs);
                }

                ItemGovernor item = registry.getItemGovernor();
                if (item != null && panic != null) {
                    boolean isShellShock = panic.getState() != SpikePanicProtocol.State.NORMAL;
                    item.setShellShockActive(isShellShock);
                }
            }

            if (failsoft != null) {
                failsoft.recordSuccess();
            }

            FuseStepPolicy step = registry.getStepPolicy();
            FuseThrottleController throttle = registry.getThrottleController();
            if (step != null && throttle != null) {
                step.setCurrentThrottleLevel(throttle.getCurrentLevel());
            }

            tickCounter++;
            if (tickCounter % LOG_INTERVAL_TICKS == 0) {
                logStatusSummary();
            }
        } catch (Throwable t) {
            if (failsoft != null) {
                failsoft.recordError(t);
            } else {
                PulseLogger.error(LOG, "onTick error: " + t.getMessage(), t);
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Status Logging
    // ═══════════════════════════════════════════════════════════════

    private void logStatusSummary() {
        StringBuilder sb = new StringBuilder();
        sb.append("\n========== [Fuse v2.4] 60s Status Summary ==========\n");
        sb.append("  Ticks: ").append(tickCounter).append("\n");

        FailsoftController failsoft = registry.getFailsoftController();
        if (failsoft != null && failsoft.isInterventionDisabled()) {
            sb.append("  ⚠️  FAILSOFT: Intervention DISABLED\n");
        }

        SpikePanicProtocol panic = registry.getPanicProtocol();
        if (panic != null) {
            sb.append("  Panic: ").append(panic.getState())
                    .append(" (multiplier=").append(String.format("%.2f", panic.getThrottleMultiplier()))
                    .append(")\n");
        }

        TickBudgetGovernor governor = registry.getGovernor();
        if (governor != null) {
            sb.append("  Governor: cutoffs=").append(governor.getTotalCutoffs())
                    .append(", last=").append(String.format("%.2f", governor.getLastTickMs())).append("ms")
                    .append(", fuseOverhead=").append(String.format("%.3f", governor.getFuseConsumedMs()))
                    .append("ms\n");
        }

        // v2.5: AdaptiveGate 상태
        AdaptiveGate gate = registry.getAdaptiveGate();
        if (gate != null) {
            sb.append("  AdaptiveGate: ").append(gate.getState())
                    .append(" (transitions=").append(gate.getStateTransitions())
                    .append(", stability=").append(gate.getStabilityCounter())
                    .append(")\n");
        }

        VehicleGuard vehicle = registry.getVehicleGuard();
        StreamingGuard streaming = registry.getStreamingGuard();
        sb.append("  Guards: vehicle=")
                .append(vehicle != null && vehicle.isPassiveMode() ? "PASSIVE" : "normal")
                .append(", streaming=")
                .append(streaming != null && streaming.isYieldMode() ? "YIELD" : "normal").append("\n");

        ItemGovernor item = registry.getItemGovernor();
        if (item != null) {
            sb.append("  ItemGovernor: throttled=").append(item.getThrottleCount())
                    .append(", full=").append(item.getFullUpdateCount())
                    .append(", shellShock=").append(item.getShellShockThrottleCount())
                    .append(", starvation=").append(item.getStarvationPreventCount())
                    .append(", active=").append(item.isActive() ? "YES" : "NO")
                    .append("\n");
        }

        FuseThrottleController throttle = registry.getThrottleController();
        if (throttle != null) {
            sb.append("  ZombieThrottle: FULL=").append(throttle.getFullCount())
                    .append(", REDUCED=").append(throttle.getReducedCount())
                    .append(", LOW=").append(throttle.getLowCount())
                    .append(", MINIMAL=").append(throttle.getMinimalCount())
                    .append("\n");
        }

        ReasonStats reasons = registry.getReasonStats();
        if (reasons != null && reasons.getTotalCount() > 0) {
            sb.append("  Intervention Reasons (Top 3):\n");
            var topReasons = reasons.getTop(3);
            int rank = 1;
            for (Map.Entry<TelemetryReason, Long> entry : topReasons) {
                sb.append("    ").append(rank).append(". ").append(entry.getKey().name())
                        .append(": ").append(entry.getValue()).append("\n");
                rank++;
            }
            sb.append("    Total: ").append(reasons.getTotalCount()).append("\n");
        }

        sb.append("=====================================================\n");
        PulseLogger.info(LOG, sb.toString());

        if (throttle != null) {
            throttle.resetNoInterventionMetrics();
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Shutdown
    // ═══════════════════════════════════════════════════════════════

    public void shutdown() {
        PulseLogger.info(LOG, "Shutting down...");

        try {
            FuseHookAdapter.unregister();
        } catch (Exception ignored) {
        }

        FuseOptimizer optimizer = registry.getOptimizer();
        if (optimizer != null) {
            optimizer.disable();
        }

        initialized = false;
        PulseLogger.info(LOG, "Shutdown complete");
    }

    // ═══════════════════════════════════════════════════════════════
    // Accessors
    // ═══════════════════════════════════════════════════════════════

    public boolean isInitialized() {
        return initialized;
    }

    public long getTickCounter() {
        return tickCounter;
    }

    public FuseComponentRegistry getRegistry() {
        return registry;
    }
}
