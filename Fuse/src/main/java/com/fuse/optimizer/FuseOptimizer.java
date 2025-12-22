package com.fuse.optimizer;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.service.echo.IBottleneckDetector;
import com.pulse.api.service.echo.OptimizationPriority;
import com.pulse.di.PulseServiceLocator;

import java.util.*;

/**
 * Fuse 자동 최적화 컨트롤러.
 * 
 * Echo의 BottleneckDetector 분석 결과를 기반으로
 * CPU 병목에 대한 최적화 결정을 내립니다.
 * 
 * @since 0.1.0
 */
public class FuseOptimizer {

    private static final FuseOptimizer INSTANCE = new FuseOptimizer();

    // 최적화 상태
    private boolean enabled = false;
    private boolean autoOptimize = false;
    private OptimizationPriority currentTarget = null;
    private long lastAnalysisTime = 0;
    private static final long ANALYSIS_INTERVAL_MS = 5000; // 5초마다

    // 활성 최적화
    private final Set<String> activeOptimizations = new HashSet<>();

    // 통계
    private int optimizationsApplied = 0;
    private int optimizationsReverted = 0;

    public static FuseOptimizer getInstance() {
        return INSTANCE;
    }

    /**
     * 최적화 엔진 활성화
     */
    public void enable() {
        this.enabled = true;
        PulseLogger.info("Fuse", "Optimizer enabled");
    }

    /**
     * 최적화 엔진 비활성화
     */
    public void disable() {
        this.enabled = false;
        revertAllOptimizations();
        PulseLogger.info("Fuse", "Optimizer disabled");
    }

    /**
     * 자동 최적화 모드 설정
     */
    public void setAutoOptimize(boolean auto) {
        this.autoOptimize = auto;
        PulseLogger.info("Fuse", "Auto-optimize: " + (auto ? "ON" : "OFF"));
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

        // Echo BottleneckDetector에서 Fuse 타겟 조회 (SPI)
        try {
            IBottleneckDetector detector = PulseServiceLocator.getInstance().getService(IBottleneckDetector.class);
            if (detector != null) {
                currentTarget = detector.suggestFuseTarget();
            } else {
                currentTarget = null;
            }
        } catch (Exception e) {
            currentTarget = null;
        }

        if (autoOptimize && currentTarget != null && currentTarget.priority > 50) {
            applyOptimization(currentTarget);
        }
    }

    /**
     * 수동으로 최적화 적용
     */
    public void applyOptimization(OptimizationPriority target) {
        if (target == null || "NONE".equals(target.targetName))
            return;

        String optId = target.targetName;
        if (activeOptimizations.contains(optId)) {
            PulseLogger.debug("Fuse", "Optimization already active: " + optId);
            return;
        }

        // 최적화 적용 (실제 로직은 각 최적화 모듈에서 구현)
        boolean success = applyOptimizationLogic(optId);
        if (success) {
            activeOptimizations.add(optId);
            optimizationsApplied++;
            PulseLogger.info("Fuse", "Applied optimization: " + optId);
            PulseLogger.info("Fuse", "Recommendation: " + target.recommendation);
        }
    }

    /**
     * 실제 최적화 로직 (확장 포인트)
     */
    private boolean applyOptimizationLogic(String targetId) {
        switch (targetId) {
            case "ZOMBIE_AI":
                PulseLogger.info("Fuse", "Applying Zombie AI LOD optimization...");
                return true;

            case "SIMULATION":
                PulseLogger.info("Fuse", "Applying Simulation batching...");
                return true;

            case "PHYSICS":
                PulseLogger.info("Fuse", "Applying Physics LOD...");
                return true;

            case "PATHFINDING_DEEP":
                PulseLogger.info("Fuse", "Applying Pathfinding caching...");
                return true;

            case "ZOMBIE_PROCESSING":
                PulseLogger.info("Fuse", "Applying Zombie processing pooling...");
                return true;

            default:
                PulseLogger.warn("Fuse", "No optimization available for: " + targetId);
                return false;
        }
    }

    /**
     * 특정 최적화 취소
     */
    public void revertOptimization(String optId) {
        if (!activeOptimizations.contains(optId))
            return;

        // 최적화 취소 로직
        activeOptimizations.remove(optId);
        optimizationsReverted++;
        PulseLogger.info("Fuse", "Reverted optimization: " + optId);
    }

    /**
     * 모든 최적화 취소
     */
    public void revertAllOptimizations() {
        for (String optId : new ArrayList<>(activeOptimizations)) {
            revertOptimization(optId);
        }
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
        status.put("optimizations_reverted", optimizationsReverted);

        if (currentTarget != null) {
            status.put("current_target", currentTarget.toMap());
        }

        return status;
    }

    /**
     * 현재 제안 타겟 조회
     */
    public OptimizationPriority getCurrentTarget() {
        return currentTarget;
    }

    /**
     * 활성 최적화 수
     */
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
