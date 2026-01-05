package com.fuse;

import com.fuse.governor.TickBudgetGovernor;
import com.fuse.governor.SpikePanicProtocol;
import com.fuse.guard.FailsoftController;
import com.fuse.hook.FuseHookAdapter;
import com.fuse.optimizer.FuseOptimizer;
import com.fuse.telemetry.ReasonStats;
import com.fuse.throttle.FuseThrottleController;

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
        System.out.println();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║         FUSE v2.4 DECOMPOSED STATUS           ║");
        System.out.println("╚═══════════════════════════════════════════════╝");

        FailsoftController failsoft = registry.getFailsoftController();
        if (failsoft != null && failsoft.isInterventionDisabled()) {
            System.out.println("\n  ⚠️  FAILSOFT: Intervention DISABLED");
            failsoft.printStatus();
            return;
        }

        SpikePanicProtocol panic = registry.getPanicProtocol();
        if (panic != null) {
            System.out.println("\n  Panic State: " + panic.getState());
            System.out.println("  Panic Multiplier: " + panic.getThrottleMultiplier());
        }

        TickBudgetGovernor gov = registry.getGovernor();
        if (gov != null) {
            System.out.println();
            gov.printStatus();
        }

        FuseThrottleController throttle = registry.getThrottleController();
        if (throttle != null) {
            System.out.println();
            throttle.printStatus();
        }

        FuseOptimizer opt = registry.getOptimizer();
        if (opt != null) {
            var status = opt.getStatus();
            System.out.println("\n  Optimizer:");
            System.out.println("    Enabled:       " + status.get("enabled"));
            System.out.println("    Auto-Optimize: " + status.get("auto_optimize"));
            System.out.println("    Applied:       " + status.get("optimizations_applied"));
        }

        ReasonStats reasons = registry.getReasonStats();
        if (reasons != null && reasons.getTotalCount() > 0) {
            System.out.println("\n  Intervention Reasons (Top 3):");
            var topReasons = reasons.getTop(3);
            int rank = 1;
            for (var entry : topReasons) {
                System.out.println("    " + rank + ". " + entry.getKey().name() + ": " + entry.getValue());
                rank++;
            }
            System.out.println("    Total: " + reasons.getTotalCount());
        }

        System.out.println();
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
