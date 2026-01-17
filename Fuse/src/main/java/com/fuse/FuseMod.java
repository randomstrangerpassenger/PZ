package com.fuse;

import com.fuse.governor.TickBudgetGovernor;
import com.fuse.governor.SpikePanicProtocol;
import com.fuse.guard.FailsoftController;
import com.fuse.hook.FuseHookAdapter;
import com.fuse.optimizer.FuseOptimizer;
import com.fuse.telemetry.ReasonStats;
import com.fuse.throttle.FuseThrottleController;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.mod.PulseMod;

/**
 * Fuse - Performance Optimizer for Project Zomboid
 * 
 * v2.4: God Class 분해 완료
 * - FuseComponentRegistry: 컴포넌트 저장/접근
 * - FuseLifecycle: 초기화/틱/종료 로직
 * - FuseMod: Thin Facade (이 클래스)
 * 
 * @since Fuse 0.3.0
 * @since Fuse 2.4.0 - God Class Decomposition
 */
public class FuseMod implements PulseMod {

    public static final String MOD_ID = "Fuse";
    public static final String VERSION = "2.4.0";

    private static FuseMod instance;

    private FuseComponentRegistry registry;
    private FuseLifecycle lifecycle;

    public static FuseMod getInstance() {
        return instance;
    }

    @Override
    public void onInitialize() {
        instance = this;
        registry = new FuseComponentRegistry();
        lifecycle = new FuseLifecycle(registry);
        lifecycle.init();
    }

    @Override
    public void onUnload() {
        if (lifecycle != null) {
            lifecycle.shutdown();
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Public API (delegate to registry)
    // ═══════════════════════════════════════════════════════════════

    public FuseOptimizer getOptimizer() {
        return registry.getOptimizer();
    }

    public FuseThrottleController getThrottleController() {
        return registry.getThrottleController();
    }

    public TickBudgetGovernor getGovernor() {
        return registry.getGovernor();
    }

    public SpikePanicProtocol getPanicProtocol() {
        return registry.getPanicProtocol();
    }

    public FailsoftController getFailsoftController() {
        return registry.getFailsoftController();
    }

    public ReasonStats getReasonStats() {
        return registry.getReasonStats();
    }

    public FuseHookAdapter getHookAdapter() {
        return registry.getHookAdapter();
    }

    // ═══════════════════════════════════════════════════════════════
    // Control Methods
    // ═══════════════════════════════════════════════════════════════

    public void toggleAutoOptimize() {
        FuseOptimizer opt = registry.getOptimizer();
        if (opt != null) {
            opt.setAutoOptimize(!opt.isAutoOptimize());
        }
    }

    public void applyCurrentTarget() {
        FuseOptimizer opt = registry.getOptimizer();
        if (opt != null) {
            var targetName = opt.getCurrentTargetName();
            if (targetName != null) {
                opt.applyOptimization(targetName, null);
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Status Display
    // ═══════════════════════════════════════════════════════════════

    public void printStatus() {
        PulseLogger.info("Fuse", "");
        PulseLogger.info("Fuse", "╔═══════════════════════════════════════════════╗");
        PulseLogger.info("Fuse", "║         FUSE v2.4 DECOMPOSED STATUS           ║");
        PulseLogger.info("Fuse", "╚═══════════════════════════════════════════════╝");

        FailsoftController failsoft = registry.getFailsoftController();
        if (failsoft != null) {
            if (failsoft.isInterventionDisabled()) { // Assuming this is the intended check
                PulseLogger.warn("Fuse", "\n  ⚠️  FAILSOFT: Intervention DISABLED");
                failsoft.printStatus();
                return;
            }
        }

        SpikePanicProtocol panic = registry.getPanicProtocol();
        if (panic != null) { // Added null check for panic
            PulseLogger.info("Fuse", "\n  Panic State: " + panic.getState());
            PulseLogger.info("Fuse", "  Panic Multiplier: " + panic.getThrottleMultiplier());
        }

        TickBudgetGovernor gov = registry.getGovernor();
        if (gov != null) {
            PulseLogger.info("Fuse", ""); // Changed System.out.println() to PulseLogger.info()
            gov.printStatus();
        }

        FuseThrottleController throttle = registry.getThrottleController();
        if (throttle != null) {
            PulseLogger.info("Fuse", ""); // Changed System.out.println() to PulseLogger.info()
            throttle.printStatus();
        }

        FuseOptimizer opt = registry.getOptimizer();
        if (opt != null) {
            var status = opt.getStatus();
            PulseLogger.info("Fuse", "");
            PulseLogger.info("Fuse", "  Optimizer:");
            PulseLogger.info("Fuse", "    Enabled:       " + status.get("enabled"));
            PulseLogger.info("Fuse", "    Auto-Optimize: " + status.get("auto_optimize"));
            PulseLogger.info("Fuse", "    Applied:       " + status.get("optimizations_applied"));
        }

        ReasonStats reasons = registry.getReasonStats(); // Kept original ReasonStats type
        if (reasons != null && reasons.getTotalCount() > 0) {
            PulseLogger.info("Fuse", "\n  Intervention Reasons (Top 3):");
            var topReasons = reasons.getTop(3); // Kept original getTop method
            int rank = 1;
            for (var entry : topReasons) { // Kept original iteration
                PulseLogger.info("Fuse", "    " + rank + ". " + entry.getKey().name() + ": " + entry.getValue());
                rank++;
            }
            PulseLogger.info("Fuse", "    Total: " + reasons.getTotalCount());
        }

        PulseLogger.info("Fuse", ""); // Changed System.out.println() to PulseLogger.info()
    }

    // ═══════════════════════════════════════════════════════════════
    // Internal Access (for testing)
    // ═══════════════════════════════════════════════════════════════

    public FuseComponentRegistry getRegistry() {
        return registry;
    }

    public FuseLifecycle getLifecycle() {
        return lifecycle;
    }
}
