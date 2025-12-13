package com.nerve;

import com.nerve.optimizer.NerveOptimizer;
import com.pulse.api.log.PulseLogger;

/**
 * Nerve - Network & Rendering Enhancement for Project Zomboid
 * 
 * Echo의 BottleneckDetector 분석 결과를 기반으로
 * 네트워크/렌더링 병목을 자동 최적화합니다.
 */
public class NerveMod {

    public static final String MOD_ID = "Nerve";
    public static final String VERSION = "0.2.0";
    private static final String LOG = "Nerve";

    private static NerveMod instance;
    private NerveOptimizer optimizer;
    private boolean initialized = false;

    public static NerveMod getInstance() {
        return instance;
    }

    public void init() {
        instance = this;
        PulseLogger.info(LOG, "");
        PulseLogger.info(LOG, "╔═══════════════════════════════════════════════╗");
        PulseLogger.info(LOG, "║     Nerve v{} - Network & Rendering       ║", VERSION);
        PulseLogger.info(LOG, "║     \"Adapt and Accelerate\"                    ║");
        PulseLogger.info(LOG, "╚═══════════════════════════════════════════════╝");

        // 옵티마이저 초기화
        optimizer = NerveOptimizer.getInstance();
        optimizer.enable();

        // Nerve는 네트워크 품질에 따라 자동 조절 권장
        optimizer.setAutoOptimize(true);

        initialized = true;
        PulseLogger.info(LOG, "Initialization complete");
        PulseLogger.info(LOG, "Auto-optimization enabled for network quality adaptation");
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
        optimizer.toggleAutoOptimize();
    }

    /** 현재 타겟에 수동 최적화 적용 */
    public void applyCurrentTarget() {
        var target = optimizer.getStatus().get("current_target");
        if (target != null) {
            PulseLogger.info(LOG, "Applying current target optimization...");
            // 타겟에 따라 적용
        } else {
            PulseLogger.info(LOG, "No optimization target available");
        }
    }

    /** 옵티마이저 상태 출력 */
    public void printStatus() {
        PulseLogger.info(LOG, "");
        PulseLogger.info(LOG, "╔═══════════════════════════════════════════════╗");
        PulseLogger.info(LOG, "║             NERVE OPTIMIZER STATUS            ║");
        PulseLogger.info(LOG, "╚═══════════════════════════════════════════════╝");

        var status = optimizer.getStatus();
        PulseLogger.info(LOG, "  Enabled:       {}", status.get("enabled"));
        PulseLogger.info(LOG, "  Auto-Optimize: {}", status.get("auto_optimize"));
        PulseLogger.info(LOG, "  Applied:       {}", status.get("optimizations_applied"));

        @SuppressWarnings("unchecked")
        var network = (java.util.Map<String, Object>) status.get("network_settings");
        PulseLogger.info(LOG, "");
        PulseLogger.info(LOG, "  Network Settings:");
        PulseLogger.info(LOG, "    Packet Batch Size:   {}", network.get("packet_batch_size"));
        PulseLogger.info(LOG, "    Delta Compression:   {}", network.get("delta_compression"));
        PulseLogger.info(LOG, "    Connection Quality:  {}", network.get("connection_quality"));

        @SuppressWarnings("unchecked")
        var render = (java.util.Map<String, Object>) status.get("render_settings");
        PulseLogger.info(LOG, "");
        PulseLogger.info(LOG, "  Render Settings:");
        PulseLogger.info(LOG, "    Occlusion Culling:   {}", render.get("occlusion_culling"));
        PulseLogger.info(LOG, "    DrawCall Batching:   {}", render.get("draw_call_batching"));
        PulseLogger.info(LOG, "    LOD Level:           {}", render.get("lod_level"));
        PulseLogger.info(LOG, "    Render Efficiency:   {}", render.get("render_efficiency"));
        PulseLogger.info(LOG, "");
    }

    public NerveOptimizer getOptimizer() {
        return optimizer;
    }

    public void shutdown() {
        PulseLogger.info(LOG, "Shutting down...");
        if (optimizer != null) {
            optimizer.disable();
        }
        initialized = false;
        PulseLogger.info(LOG, "Shutdown complete");
    }
}
