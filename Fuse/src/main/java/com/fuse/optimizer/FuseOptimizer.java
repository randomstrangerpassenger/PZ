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
 */
public class FuseOptimizer {

    private static final FuseOptimizer INSTANCE = new FuseOptimizer();

    // 최적화 상태
    private boolean enabled = false;
    private boolean autoOptimize = false;
    private String currentTargetName = null;
    private long lastAnalysisTime = 0;
    private static final long ANALYSIS_INTERVAL_MS = 5000;

    // SPI 연동
    private IOptimizationHintProvider hintProvider;

    // 활성 최적화
    private final Set<String> activeOptimizations = new HashSet<>();

    // 통계
    private int optimizationsApplied = 0;
    private int optimizationsReverted = 0;

    public static FuseOptimizer getInstance() {
        return INSTANCE;
    }

    public void setHintProvider(IOptimizationHintProvider provider) {
        this.hintProvider = provider;
        if (provider != null) {
            PulseLogger.info("Fuse", "HintProvider registered: " + provider.getClass().getSimpleName());
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

        // IOptimizationHintProvider 연동 - 자동 최적화 (리플렉션 사용)
        if (autoOptimize) {
            applyAutoOptimizationFromHints();
        }
    }

    /**
     * SPI를 통한 자동 최적화 적용.
     * IOptimizationHintProvider로 힌트를 가져와 적용.
     */
    private void applyAutoOptimizationFromHints() {
        if (hintProvider == null)
            return;

        try {
            var hints = hintProvider.getTopHints(1);
            if (hints.isEmpty())
                return;

            // 상위 힌트 가져오기
            var topHint = hints.get(0);

            // priority가 50 이상이고 활성화되지 않은 경우 적용
            if (topHint.priority > 50 && !activeOptimizations.contains(topHint.targetName)) {
                applyOptimization(topHint.targetName, topHint.recommendation);
            }
        } catch (Exception e) {
            // Fail-soft: SPI 호출 실패 시 무시
        }
    }

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
        return switch (targetId) {
            case "ZOMBIE_AI" -> {
                PulseLogger.info("Fuse", "Applying Zombie AI LOD optimization...");
                yield true;
            }
            case "SIMULATION" -> {
                PulseLogger.info("Fuse", "Applying Simulation batching...");
                yield true;
            }
            case "PHYSICS" -> {
                PulseLogger.info("Fuse", "Applying Physics LOD...");
                yield true;
            }
            case "PATHFINDING_DEEP" -> {
                PulseLogger.info("Fuse", "Applying Pathfinding caching...");
                yield true;
            }
            case "ZOMBIE_PROCESSING" -> {
                PulseLogger.info("Fuse", "Applying Zombie processing pooling...");
                yield true;
            }
            default -> {
                PulseLogger.warn("Fuse", "No optimization available for: " + targetId);
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
