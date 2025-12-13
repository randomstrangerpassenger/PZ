package com.fuse;

import com.fuse.optimizer.FuseOptimizer;

/**
 * Fuse - Performance Optimizer for Project Zomboid
 * 
 * Echo의 BottleneckDetector 분석 결과를 기반으로
 * CPU 병목(좀비 AI, 시뮬레이션, 물리 등)을 자동 최적화합니다.
 */
public class FuseMod {

    public static final String MOD_ID = "Fuse";
    public static final String VERSION = "0.2.0";

    private static FuseMod instance;
    private FuseOptimizer optimizer;
    private boolean initialized = false;

    public static FuseMod getInstance() {
        return instance;
    }

    public void init() {
        instance = this;
        System.out.println();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║     Fuse v" + VERSION + " - Performance Optimizer      ║");
        System.out.println("║     \"Detect and Optimize\"                     ║");
        System.out.println("╚═══════════════════════════════════════════════╝");

        // 옵티마이저 초기화
        optimizer = FuseOptimizer.getInstance();
        optimizer.enable();

        // 자동 최적화는 기본적으로 비활성화 (수동 제어 권장)
        optimizer.setAutoOptimize(false);

        initialized = true;
        System.out.println("[Fuse] Initialization complete");
        System.out.println("[Fuse] Use /fuse commands to control optimizations");
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
        if (optimizer != null) {
            optimizer.disable();
        }
        initialized = false;
        System.out.println("[Fuse] Shutdown complete");
    }
}
