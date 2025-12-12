package com.nerve;

import com.nerve.optimizer.NerveOptimizer;

/**
 * Nerve - Network & Rendering Enhancement for Project Zomboid
 * 
 * Echo의 BottleneckDetector 분석 결과를 기반으로
 * 네트워크/렌더링 병목을 자동 최적화합니다.
 */
public class NerveMod {

    public static final String MOD_ID = "Nerve";
    public static final String VERSION = "0.2.0";

    private static NerveMod instance;
    private NerveOptimizer optimizer;
    private boolean initialized = false;

    public static NerveMod getInstance() {
        return instance;
    }

    public void init() {
        instance = this;
        System.out.println();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║     Nerve v" + VERSION + " - Network & Rendering       ║");
        System.out.println("║     \"Adapt and Accelerate\"                    ║");
        System.out.println("╚═══════════════════════════════════════════════╝");

        // 옵티마이저 초기화
        optimizer = NerveOptimizer.getInstance();
        optimizer.enable();

        // Nerve는 네트워크 품질에 따라 자동 조절 권장
        optimizer.setAutoOptimize(true);

        initialized = true;
        System.out.println("[Nerve] Initialization complete");
        System.out.println("[Nerve] Auto-optimization enabled for network quality adaptation");
    }

    /**
     * 게임 틱에서 호출
     */
    public void onTick() {
        if (!initialized)
            return;
        optimizer.update();
    }

    /**
     * 자동 최적화 토글
     */
    public void toggleAutoOptimize() {
        optimizer.setAutoOptimize(!optimizer.isAutoOptimize());
    }

    /**
     * 현재 타겟에 대해 수동 최적화 적용
     */
    public void applyCurrentTarget() {
        var target = optimizer.getStatus().get("current_target");
        if (target != null) {
            System.out.println("[Nerve] Applying current target optimization...");
            // 타겟에 따라 적용
        } else {
            System.out.println("[Nerve] No optimization target available");
        }
    }

    /**
     * 옵티마이저 상태 출력
     */
    public void printStatus() {
        System.out.println();
        System.out.println("╔═══════════════════════════════════════════════╗");
        System.out.println("║             NERVE OPTIMIZER STATUS            ║");
        System.out.println("╚═══════════════════════════════════════════════╝");

        var status = optimizer.getStatus();
        System.out.println("  Enabled:       " + status.get("enabled"));
        System.out.println("  Auto-Optimize: " + status.get("auto_optimize"));
        System.out.println("  Applied:       " + status.get("optimizations_applied"));

        @SuppressWarnings("unchecked")
        var network = (java.util.Map<String, Object>) status.get("network_settings");
        System.out.println();
        System.out.println("  Network Settings:");
        System.out.println("    Packet Batch Size:   " + network.get("packet_batch_size"));
        System.out.println("    Delta Compression:   " + network.get("delta_compression"));
        System.out.println("    Connection Quality:  " + network.get("connection_quality"));

        @SuppressWarnings("unchecked")
        var render = (java.util.Map<String, Object>) status.get("render_settings");
        System.out.println();
        System.out.println("  Render Settings:");
        System.out.println("    Occlusion Culling:   " + render.get("occlusion_culling"));
        System.out.println("    DrawCall Batching:   " + render.get("draw_call_batching"));
        System.out.println("    LOD Level:           " + render.get("lod_level"));
        System.out.println("    Render Efficiency:   " + render.get("render_efficiency"));
        System.out.println();
    }

    public NerveOptimizer getOptimizer() {
        return optimizer;
    }

    public void shutdown() {
        System.out.println("[Nerve] Shutting down...");
        if (optimizer != null) {
            optimizer.disable();
        }
        initialized = false;
        System.out.println("[Nerve] Shutdown complete");
    }
}
