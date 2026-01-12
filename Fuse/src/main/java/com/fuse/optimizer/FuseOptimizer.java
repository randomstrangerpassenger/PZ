package com.fuse.optimizer;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.spi.IOptimizationHintProvider;

import java.util.*;

/**
 * Fuse 최적화 컨트롤러.
 * 
 * CPU 최적화 결정을 관리합니다.
 * 
 * @since 0.1.0
 * @since 2.0 - 단순화 (IBottleneckDetector 삭제됨)
 * @since 2.1 - IOptimizationHintProvider SPI 연동
 * @since 3.0 - AUTO_OPTIMIZE_FROZEN: 동결 원칙에 의해 자동 최적화 비활성화
 */
public class FuseOptimizer {

    private static final FuseOptimizer INSTANCE = new FuseOptimizer();

    // [FROZEN] 자동 최적화 기능 영구 비활성화 - 동결 원칙 위반 방지
    private static final boolean AUTO_OPTIMIZE_FROZEN = true;

    // 최적화 상태
    private boolean enabled = false;
    private boolean autoOptimize = false;
    private String currentTargetName = null;
    private long lastAnalysisTime = 0;
    private static final long ANALYSIS_INTERVAL_MS = 5000;

    // [FROZEN] SPI 연동 - 동결 원칙에 의해 비활성화됨
    @SuppressWarnings("unused")
    private IOptimizationHintProvider hintProvider;

    // 활성 최적화
    private final Set<String> activeOptimizations = new HashSet<>();

    // 통계
    private int optimizationsApplied = 0;
    private int optimizationsReverted = 0;

    public static FuseOptimizer getInstance() {
        return INSTANCE;
    }

    /**
     * @deprecated 동결 원칙에 의해 비활성화됨. 자동 최적화 기능이 제거됨.
     */
    @Deprecated
    public void setHintProvider(IOptimizationHintProvider provider) {
        this.hintProvider = provider;
        if (provider != null) {
            PulseLogger.info("Fuse",
                    "HintProvider registered (FROZEN - not used): " + provider.getClass().getSimpleName());
        }
    }

    public void enable() {
        this.enabled = true;
        PulseLogger.info("Fuse", "Optimizer enabled");
    }

    public void disable() {
        this.enabled = false;
        revertAllOptimizations();
        PulseLogger.info("Fuse", "Optimizer disabled");
    }

    public void setAutoOptimize(boolean auto) {
        // [FROZEN] 자동 최적화 기능은 동결 원칙에 의해 비활성화됨
        if (AUTO_OPTIMIZE_FROZEN) {
            PulseLogger.warn("Fuse", "AUTO_OPTIMIZE_FROZEN: setAutoOptimize() ignored");
            return;
        }
        this.autoOptimize = auto;
        PulseLogger.info("Fuse", "Auto-optimize: " + (auto ? "ON" : "OFF"));
    }

    /**
     * 틱마다 호출 - 자동 최적화 적용
     */
    public void update() {
        if (!enabled)
            return;

        long now = System.currentTimeMillis();
        if (now - lastAnalysisTime < ANALYSIS_INTERVAL_MS)
            return;
        lastAnalysisTime = now;

        // [FROZEN] 자동 최적화 기능 영구 비활성화됨
        // AUTO_OPTIMIZE_FROZEN = true 이므로 호출되지 않음
    }

    // [REMOVED] applyAutoOptimizationFromHints() - 동결 원칙에 의해 제거
    // [REMOVED] determineAction() - 동결 원칙에 의해 제거

    /**
     * 수동으로 최적화 적용
     */
    public void applyOptimization(String targetId, String recommendation) {
        if (targetId == null || "NONE".equals(targetId))
            return;

        if (activeOptimizations.contains(targetId)) {
            PulseLogger.debug("Fuse", "Optimization already active: " + targetId);
            return;
        }

        boolean success = applyOptimizationLogic(targetId);
        if (success) {
            activeOptimizations.add(targetId);
            optimizationsApplied++;
            currentTargetName = targetId;
            PulseLogger.info("Fuse", "Applied optimization: " + targetId);
            if (recommendation != null) {
                PulseLogger.info("Fuse", "Recommendation: " + recommendation);
            }
        }
    }

    private boolean applyOptimizationLogic(String targetId) {
        // Normalize to lowercase for consistent matching with Echo's primitive API
        String normalized = targetId != null ? targetId.toLowerCase() : "";

        return switch (normalized) {
            case "zombie_ai" -> {
                PulseLogger.info("Fuse", "Applying Zombie AI LOD optimization...");
                yield true;
            }
            case "simulation" -> {
                PulseLogger.info("Fuse", "Applying Simulation batching...");
                yield true;
            }
            case "physics" -> {
                PulseLogger.info("Fuse", "Applying Physics LOD...");
                yield true;
            }
            case "pathfinding", "pathfinding_deep" -> {
                PulseLogger.info("Fuse", "Applying Pathfinding caching...");
                yield true;
            }
            case "zombie_processing" -> {
                PulseLogger.info("Fuse", "Applying Zombie processing pooling...");
                yield true;
            }
            default -> {
                PulseLogger.debug("Fuse", "No optimization available for: " + targetId);
                yield false;
            }
        };
    }

    public void revertOptimization(String optId) {
        if (!activeOptimizations.contains(optId))
            return;

        activeOptimizations.remove(optId);
        optimizationsReverted++;
        PulseLogger.info("Fuse", "Reverted optimization: " + optId);
    }

    public void revertAllOptimizations() {
        for (String optId : new ArrayList<>(activeOptimizations)) {
            revertOptimization(optId);
        }
        currentTargetName = null;
    }

    public Map<String, Object> getStatus() {
        Map<String, Object> status = new LinkedHashMap<>();
        status.put("enabled", enabled);
        status.put("auto_optimize", autoOptimize);
        status.put("active_optimizations", new ArrayList<>(activeOptimizations));
        status.put("optimizations_applied", optimizationsApplied);
        status.put("optimizations_reverted", optimizationsReverted);
        status.put("current_target", currentTargetName);
        return status;
    }

    public String getCurrentTargetName() {
        return currentTargetName;
    }

    public int getActiveOptimizationCount() {
        return activeOptimizations.size();
    }

    public boolean isEnabled() {
        return enabled;
    }

    public boolean isAutoOptimize() {
        return autoOptimize;
    }
}
