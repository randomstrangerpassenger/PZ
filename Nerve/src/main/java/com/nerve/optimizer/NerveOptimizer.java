package com.nerve.optimizer;

import com.echo.analysis.BottleneckDetector;
import com.echo.analysis.BottleneckDetector.*;
import com.echo.measure.NetworkMetrics;
import com.echo.measure.RenderMetrics;

import java.util.*;

/**
 * Nerve 네트워크/렌더링 최적화 컨트롤러.
 * 
 * Echo의 BottleneckDetector 분석 결과를 기반으로
 * 네트워크 및 렌더링 병목에 대한 최적화 결정을 내립니다.
 * 
 * @since 0.1.0
 */
public class NerveOptimizer {

    private static final NerveOptimizer INSTANCE = new NerveOptimizer();

    // 최적화 상태
    private boolean enabled = false;
    private boolean autoOptimize = false;
    private OptimizationPriority currentTarget = null;
    private long lastAnalysisTime = 0;
    private static final long ANALYSIS_INTERVAL_MS = 5000;

    // 활성 최적화
    private final Set<String> activeOptimizations = new HashSet<>();

    // 네트워크 최적화 설정
    private int packetBatchSize = 1;
    private boolean deltaCompression = false;

    // 렌더링 최적화 설정
    private boolean occlusionCulling = false;
    private boolean drawCallBatching = false;
    private int lodLevel = 0;

    // 통계
    private int optimizationsApplied = 0;

    public static NerveOptimizer getInstance() {
        return INSTANCE;
    }

    /**
     * 최적화 엔진 활성화
     */
    public void enable() {
        this.enabled = true;
        System.out.println("[Nerve] Optimizer enabled");
    }

    /**
     * 최적화 엔진 비활성화
     */
    public void disable() {
        this.enabled = false;
        revertAllOptimizations();
        System.out.println("[Nerve] Optimizer disabled");
    }

    /**
     * 자동 최적화 모드 설정
     */
    public void setAutoOptimize(boolean auto) {
        this.autoOptimize = auto;
        System.out.println("[Nerve] Auto-optimize: " + (auto ? "ON" : "OFF"));
    }

    /**
     * 틱마다 호출하여 병목 분석 및 최적화 적용
     */
    public void update() {
        if (!enabled)
            return;

        long now = System.currentTimeMillis();
        if (now - lastAnalysisTime < ANALYSIS_INTERVAL_MS)
            return;
        lastAnalysisTime = now;

        // Echo BottleneckDetector에서 Nerve 타겟 조회
        currentTarget = BottleneckDetector.getInstance().suggestNerveTarget();

        // 네트워크 품질 기반 자동 조절
        if (autoOptimize) {
            autoAdjustNetwork();
            autoAdjustRendering();

            if (currentTarget != null && currentTarget.priority > 50) {
                applyOptimization(currentTarget);
            }
        }
    }

    /**
     * 네트워크 품질에 따른 자동 조절
     */
    private void autoAdjustNetwork() {
        NetworkMetrics.ConnectionQuality quality = NetworkMetrics.getInstance().getConnectionQuality();

        switch (quality) {
            case POOR:
                // 연결 품질 나쁨 → 공격적 최적화
                if (packetBatchSize < 5) {
                    packetBatchSize = 5;
                    deltaCompression = true;
                    System.out
                            .println("[Nerve] Network quality POOR - enabling aggressive batching (5) and compression");
                }
                break;

            case FAIR:
                // 연결 품질 보통 → 중간 최적화
                if (packetBatchSize != 3) {
                    packetBatchSize = 3;
                    deltaCompression = true;
                    System.out.println("[Nerve] Network quality FAIR - moderate batching (3)");
                }
                break;

            case GOOD:
                // 연결 품질 양호 → 경량 최적화
                if (packetBatchSize != 2) {
                    packetBatchSize = 2;
                    deltaCompression = false;
                    System.out.println("[Nerve] Network quality GOOD - light batching (2)");
                }
                break;

            case EXCELLENT:
                // 연결 품질 최적 → 최적화 불필요
                if (packetBatchSize != 1) {
                    packetBatchSize = 1;
                    deltaCompression = false;
                    System.out.println("[Nerve] Network quality EXCELLENT - no batching needed");
                }
                break;
        }
    }

    /**
     * 렌더링 성능에 따른 자동 조절
     */
    private void autoAdjustRendering() {
        RenderMetrics.RenderEfficiency efficiency = RenderMetrics.getInstance().getRenderEfficiency();
        double fps = RenderMetrics.getInstance().getFps();

        if (fps < 30 || efficiency == RenderMetrics.RenderEfficiency.POOR) {
            // FPS 낮음 → 공격적 최적화
            if (lodLevel < 2) {
                lodLevel = 2;
                occlusionCulling = true;
                drawCallBatching = true;
                System.out.println("[Nerve] FPS low (" + (int) fps + ") - enabling aggressive render optimizations");
            }
        } else if (fps < 45 || efficiency == RenderMetrics.RenderEfficiency.FAIR) {
            // FPS 보통 → 중간 최적화
            if (lodLevel != 1) {
                lodLevel = 1;
                occlusionCulling = true;
                drawCallBatching = false;
                System.out.println("[Nerve] FPS moderate (" + (int) fps + ") - enabling moderate render optimizations");
            }
        } else {
            // FPS 양호 → 최적화 축소
            if (lodLevel != 0) {
                lodLevel = 0;
                occlusionCulling = false;
                drawCallBatching = false;
                System.out.println("[Nerve] FPS good (" + (int) fps + ") - reducing render optimizations");
            }
        }
    }

    /**
     * 수동으로 최적화 적용
     */
    public void applyOptimization(OptimizationPriority target) {
        if (target == null || "NONE".equals(target.targetName))
            return;

        String optId = target.targetName;
        if (activeOptimizations.contains(optId))
            return;

        boolean success = applyOptimizationLogic(optId);
        if (success) {
            activeOptimizations.add(optId);
            optimizationsApplied++;
            System.out.println("[Nerve] Applied optimization: " + optId);
            System.out.println("[Nerve] Recommendation: " + target.recommendation);
        }
    }

    /**
     * 실제 최적화 로직 (확장 포인트)
     */
    private boolean applyOptimizationLogic(String targetId) {
        switch (targetId) {
            case "RENDER":
                // 렌더링 최적화: Draw Call 배칭
                drawCallBatching = true;
                System.out.println("[Nerve] Enabling DrawCall batching...");
                return true;

            case "RENDER_WORLD":
                // 월드 렌더링 최적화: Occlusion Culling + LOD
                occlusionCulling = true;
                lodLevel = Math.min(lodLevel + 1, 3);
                System.out.println("[Nerve] Enabling occlusion culling and LOD level " + lodLevel);
                return true;

            case "NETWORK":
                // 네트워크 최적화: 패킷 배칭 + 압축
                packetBatchSize = Math.min(packetBatchSize + 2, 10);
                deltaCompression = true;
                System.out.println("[Nerve] Enabling packet batching (" + packetBatchSize + ") and delta compression");
                return true;

            default:
                System.out.println("[Nerve] No optimization available for: " + targetId);
                return false;
        }
    }

    /**
     * 모든 최적화 취소
     */
    public void revertAllOptimizations() {
        activeOptimizations.clear();
        packetBatchSize = 1;
        deltaCompression = false;
        occlusionCulling = false;
        drawCallBatching = false;
        lodLevel = 0;
        System.out.println("[Nerve] All optimizations reverted");
    }

    /**
     * 현재 상태 조회
     */
    public Map<String, Object> getStatus() {
        Map<String, Object> status = new LinkedHashMap<>();
        status.put("enabled", enabled);
        status.put("auto_optimize", autoOptimize);
        status.put("active_optimizations", new ArrayList<>(activeOptimizations));
        status.put("optimizations_applied", optimizationsApplied);

        // 네트워크 설정
        Map<String, Object> network = new LinkedHashMap<>();
        network.put("packet_batch_size", packetBatchSize);
        network.put("delta_compression", deltaCompression);
        network.put("connection_quality", NetworkMetrics.getInstance().getConnectionQuality().name());
        status.put("network_settings", network);

        // 렌더링 설정
        Map<String, Object> render = new LinkedHashMap<>();
        render.put("occlusion_culling", occlusionCulling);
        render.put("draw_call_batching", drawCallBatching);
        render.put("lod_level", lodLevel);
        render.put("render_efficiency", RenderMetrics.getInstance().getRenderEfficiency().name());
        status.put("render_settings", render);

        if (currentTarget != null) {
            status.put("current_target", currentTarget.toMap());
        }

        return status;
    }

    // Getters
    public int getPacketBatchSize() {
        return packetBatchSize;
    }

    public boolean isDeltaCompression() {
        return deltaCompression;
    }

    public boolean isOcclusionCulling() {
        return occlusionCulling;
    }

    public boolean isDrawCallBatching() {
        return drawCallBatching;
    }

    public int getLodLevel() {
        return lodLevel;
    }

    public boolean isEnabled() {
        return enabled;
    }

    public boolean isAutoOptimize() {
        return autoOptimize;
    }
}
