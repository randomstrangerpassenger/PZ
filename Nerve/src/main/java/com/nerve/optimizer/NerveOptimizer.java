package com.nerve.optimizer;

import com.pulse.api.di.PulseServices;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.service.echo.ConnectionQuality;
import com.pulse.api.service.echo.INetworkMetrics;
import com.pulse.api.service.echo.IRenderMetrics;
import com.pulse.api.service.echo.RenderEfficiency;
import com.pulse.api.spi.IOptimizationHintProvider;

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

    private static final String LOG = "Nerve";
    private static final NerveOptimizer INSTANCE = new NerveOptimizer();

    // 최적화 상태
    private boolean enabled = false;
    private boolean autoOptimize = false;
    private String currentTargetId = null;
    private int currentSeverity = 0;
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
        PulseLogger.info(LOG, "Optimizer enabled");
    }

    /**
     * 최적화 엔진 비활성화
     */
    public void disable() {
        this.enabled = false;
        revertAllOptimizations();
        PulseLogger.info(LOG, "Optimizer disabled");
    }

    /**
     * 자동 최적화 모드 설정
     */
    public void setAutoOptimize(boolean auto) {
        this.autoOptimize = auto;
        PulseLogger.info(LOG, "Auto-optimize: {}", auto ? "ON" : "OFF");
    }

    /**
     * 자동 최적화 모드 토글
     */
    public void toggleAutoOptimize() {
        setAutoOptimize(!autoOptimize);
    }

    /**
     * 틱마다 호출하여 병목 분석 및 최적화 적용
     * 
     * @since 3.0 - IOptimizationHintProvider primitive API 사용
     */
    public void update() {
        if (!enabled)
            return;

        long now = System.currentTimeMillis();
        if (now - lastAnalysisTime < ANALYSIS_INTERVAL_MS)
            return;
        lastAnalysisTime = now;

        // Echo로부터 원시 관측 데이터만 수신 (SPI primitive API)
        try {
            IOptimizationHintProvider provider = com.pulse.api.Pulse.getProviderRegistry()
                    .getProviders(IOptimizationHintProvider.class)
                    .stream()
                    .filter(p -> "echo.hints".equals(p.getId()))
                    .findFirst()
                    .orElse(null);

            if (provider != null) {
                currentTargetId = provider.getTopTargetId();
                currentSeverity = provider.getTopTargetSeverity();
                String category = provider.getTopTargetCategory();

                // Nerve는 RENDER, NETWORK 카테고리만 처리
                if (category != null &&
                        !IOptimizationHintProvider.CATEGORY_RENDER.equals(category) &&
                        !IOptimizationHintProvider.CATEGORY_NETWORK.equals(category)) {
                    currentTargetId = null;
                    currentSeverity = 0;
                }
            } else {
                currentTargetId = null;
                currentSeverity = 0;
            }
        } catch (Exception e) {
            PulseLogger.debug(LOG, "HintProvider not available: {}", e.getMessage());
            currentTargetId = null;
            currentSeverity = 0;
        }

        // 네트워크 품질 기반 자동 조절
        if (autoOptimize) {
            autoAdjustNetwork();
            autoAdjustRendering();

            // Nerve 내부 정책: severity 50 이상이면 최적화 적용
            if (currentTargetId != null && currentSeverity > 50) {
                applyOptimization(currentTargetId);
            }
        }
    }

    /**
     * 네트워크 품질에 따른 자동 조절
     */
    private void autoAdjustNetwork() {
        INetworkMetrics metrics = PulseServices.getServiceLocator().getService(INetworkMetrics.class);
        if (metrics == null)
            return;

        ConnectionQuality quality = metrics.getConnectionQuality();

        switch (quality) {
            case POOR:
                // 연결 품질 나쁨 → 공격적 최적화
                if (packetBatchSize < 5) {
                    packetBatchSize = 5;
                    deltaCompression = true;
                    PulseLogger.info(LOG, "Network quality POOR - enabling aggressive batching (5) and compression");
                }
                break;

            case FAIR:
                // 연결 품질 보통 → 중간 최적화
                if (packetBatchSize != 3) {
                    packetBatchSize = 3;
                    deltaCompression = true;
                    PulseLogger.info(LOG, "Network quality FAIR - moderate batching (3)");
                }
                break;

            case GOOD:
                // 연결 품질 양호 → 경량 최적화
                if (packetBatchSize != 2) {
                    packetBatchSize = 2;
                    deltaCompression = false;
                    PulseLogger.info(LOG, "Network quality GOOD - light batching (2)");
                }
                break;

            case EXCELLENT:
                // 연결 품질 최적 → 최적화 불필요
                if (packetBatchSize != 1) {
                    packetBatchSize = 1;
                    deltaCompression = false;
                    PulseLogger.debug(LOG, "Network quality EXCELLENT - no batching needed");
                }
                break;
        }
    }

    /**
     * 렌더링 성능에 따른 자동 조절
     */
    private void autoAdjustRendering() {
        IRenderMetrics metrics = PulseServices.getServiceLocator().getService(IRenderMetrics.class);
        if (metrics == null)
            return;

        RenderEfficiency efficiency = metrics.getRenderEfficiency();
        double fps = metrics.getFps();

        if (fps < 30 || efficiency == RenderEfficiency.POOR) {
            // FPS 낮음 → 공격적 최적화
            if (lodLevel < 2) {
                lodLevel = 2;
                occlusionCulling = true;
                drawCallBatching = true;
                PulseLogger.warn(LOG, "FPS low ({}) - enabling aggressive render optimizations", (int) fps);
            }
        } else if (fps < 45 || efficiency == RenderEfficiency.FAIR) {
            // FPS 보통 → 중간 최적화
            if (lodLevel != 1) {
                lodLevel = 1;
                occlusionCulling = true;
                drawCallBatching = false;
                PulseLogger.info(LOG, "FPS moderate ({}) - enabling moderate render optimizations", (int) fps);
            }
        } else {
            // FPS 양호 → 최적화 축소
            if (lodLevel != 0) {
                lodLevel = 0;
                occlusionCulling = false;
                drawCallBatching = false;
                PulseLogger.debug(LOG, "FPS good ({}) - reducing render optimizations", (int) fps);
            }
        }
    }

    /**
     * 수동으로 최적화 적용
     * 
     * @param targetId 타겟 ID (예: "RENDER", "NETWORK")
     */
    public void applyOptimization(String targetId) {
        if (targetId == null || "NONE".equalsIgnoreCase(targetId))
            return;

        if (activeOptimizations.contains(targetId))
            return;

        boolean success = applyOptimizationLogic(targetId);
        if (success) {
            activeOptimizations.add(targetId);
            optimizationsApplied++;
            PulseLogger.info(LOG, "Applied optimization: {}", targetId);
            // Nerve 내부 정책 결정 로그
            PulseLogger.info(LOG, "Policy applied: {}", determineAction(targetId, currentSeverity));
        }
    }

    /**
     * Nerve 내부 정책 - Echo가 아닌 Nerve가 판단.
     */
    private String determineAction(String targetId, int severity) {
        return switch (targetId.toUpperCase()) {
            case "RENDER" -> "Enable DrawCall batching";
            case "RENDER_WORLD" -> "Enable occlusion culling + LOD";
            case "NETWORK" -> "Enable packet batching + compression";
            default -> "Apply generic optimization";
        };
    }

    /**
     * 실제 최적화 로직 (확장 포인트)
     */
    private boolean applyOptimizationLogic(String targetId) {
        switch (targetId) {
            case "RENDER":
                // 렌더링 최적화: Draw Call 배칭
                drawCallBatching = true;
                PulseLogger.info(LOG, "Enabling DrawCall batching...");
                return true;

            case "RENDER_WORLD":
                // 월드 렌더링 최적화: Occlusion Culling + LOD
                occlusionCulling = true;
                lodLevel = Math.min(lodLevel + 1, 3);
                PulseLogger.info(LOG, "Enabling occlusion culling and LOD level {}", lodLevel);
                return true;

            case "NETWORK":
                // 네트워크 최적화: 패킷 배칭 + 압축
                packetBatchSize = Math.min(packetBatchSize + 2, 10);
                deltaCompression = true;
                PulseLogger.info(LOG, "Enabling packet batching ({}) and delta compression", packetBatchSize);
                return true;

            default:
                PulseLogger.debug(LOG, "No optimization available for: {}", targetId);
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
        PulseLogger.info(LOG, "All optimizations reverted");
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

        INetworkMetrics netMetrics = PulseServices.getServiceLocator().getService(INetworkMetrics.class);
        if (netMetrics != null) {
            network.put("connection_quality", netMetrics.getConnectionQuality().name());
        }
        status.put("network_settings", network);

        // 렌더링 설정
        Map<String, Object> render = new LinkedHashMap<>();
        render.put("occlusion_culling", occlusionCulling);
        render.put("draw_call_batching", drawCallBatching);
        render.put("lod_level", lodLevel);

        IRenderMetrics renderMetrics = PulseServices.getServiceLocator().getService(IRenderMetrics.class);
        if (renderMetrics != null) {
            render.put("render_efficiency", renderMetrics.getRenderEfficiency().name());
        }
        status.put("render_settings", render);

        if (currentTargetId != null) {
            Map<String, Object> targetInfo = new LinkedHashMap<>();
            targetInfo.put("target_id", currentTargetId);
            targetInfo.put("severity", currentSeverity);
            status.put("current_target", targetInfo);
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
