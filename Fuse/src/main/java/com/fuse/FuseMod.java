package com.fuse;

import com.fuse.config.FuseConfig;
import com.fuse.hook.FuseHookAdapter;
import com.fuse.optimizer.FuseOptimizer;
import com.fuse.throttle.FuseThrottleController;
import com.pulse.api.profiler.ZombieHook;
import com.pulse.mod.PulseMod;

/**
 * Fuse - Performance Optimizer for Project Zomboid
 * 
 * Echo의 BottleneckDetector 분석 결과를 기반으로
 * CPU 병목(좀비 AI, 시뮬레이션, 물리 등)을 자동 최적화합니다.
 */
public class FuseMod implements PulseMod {

    public static final String MOD_ID = "Fuse";
    public static final String VERSION = "0.3.0";

    private static FuseMod instance;
    private FuseOptimizer optimizer;
    private FuseHookAdapter hookAdapter;
    private FuseThrottleController throttleController;
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
        System.out.println("║     Fuse v" + VERSION + " - Performance Optimizer      ║");
        System.out.println("║     \"Detect and Optimize\"                     ║");
        System.out.println("╚═══════════════════════════════════════════════╝");

        // Config 초기화
        FuseConfig.getInstance();

        // Phase 1: Hook Adapter 등록 (계측)
        try {
            hookAdapter = new FuseHookAdapter();
            ZombieHook.setCallback(hookAdapter);
            ZombieHook.profilingEnabled = true;
            System.out.println("[Fuse] ZombieHook callback registered");
        } catch (Exception e) {
            System.err.println("[Fuse] Failed to register ZombieHook: " + e.getMessage());
        }

        // Phase 2: Throttle Controller 등록
        try {
            throttleController = new FuseThrottleController();
            ZombieHook.setThrottlePolicy(throttleController);
            System.out.println("[Fuse] ThrottlePolicy registered (disabled by default)");
        } catch (Exception e) {
            System.err.println("[Fuse] Failed to register ThrottlePolicy: " + e.getMessage());
        }

        // 옵티마이저 초기화
        optimizer = FuseOptimizer.getInstance();
        optimizer.enable();
        optimizer.setAutoOptimize(false);

        initialized = true;
        System.out.println("[Fuse] Initialization complete");
        System.out.println("[Fuse] Use /fuse throttle on|off to control throttling");
    }

    /**
     * 게임 틱에서 호출
     */
    public void onTick() {
        if (!initialized)
            return;
        optimizer.update();
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

    /** 옵티마이저 상태 출력 */
    public void printStatus() {
        System.out.println();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║              FUSE OPTIMIZER STATUS            ║");
        System.out.println("╚═══════════════════════════════════════════════╝");

        var status = optimizer.getStatus();
        System.out.println("  Enabled:       " + status.get("enabled"));
        System.out.println("  Auto-Optimize: " + status.get("auto_optimize"));
        System.out.println("  Applied:       " + status.get("optimizations_applied"));
        System.out.println("  Active:        " + status.get("active_optimizations"));

        if (status.containsKey("current_target")) {
            @SuppressWarnings("unchecked")
            var target = (java.util.Map<String, Object>) status.get("current_target");
            System.out.println();
            System.out.println("  Current Target: " + target.get("target"));
            System.out.println("  Priority:       " + target.get("priority"));
            System.out.println("  Recommendation: " + target.get("recommendation"));
        }
        System.out.println();
    }

    public FuseOptimizer getOptimizer() {
        return optimizer;
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
