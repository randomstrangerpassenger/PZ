package com.pulse.api.spi;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

/**
 * SPI interface for optimization hint providers.
 * 
 * Provides primitive-only metrics from analysis modules (e.g., Echo)
 * to optimization modules (e.g., Fuse) without object coupling.
 * 
 * Hub & Spoke 원칙:
 * - Provider(Echo): 관측치만 제공 (severity, category)
 * - Consumer(Fuse): 판단/정책 결정 (임계값, 조치)
 * 
 * @since Pulse 1.1.0
 * @since Pulse 2.0.0 - Primitive-only API
 */
public interface IOptimizationHintProvider extends IProvider {

    // ═══════════════════════════════════════════════════════════════
    // Category Constants
    // ═══════════════════════════════════════════════════════════════

    String CATEGORY_CPU = "CPU";
    String CATEGORY_MEMORY = "MEMORY";
    String CATEGORY_IO = "IO";
    String CATEGORY_RENDER = "RENDER";
    String CATEGORY_NETWORK = "NETWORK";

    // ═══════════════════════════════════════════════════════════════
    // Primitive-only API (v2.0)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 최상위 병목 타겟 ID.
     * 
     * @return 타겟 ID (예: "zombie_ai", "pathfinding"), 없으면 null
     */
    String getTopTargetId();

    /**
     * 심각도 (관측치).
     * 
     * @return 0-100 범위, 타겟 없으면 0
     */
    int getTopTargetSeverity();

    /**
     * 카테고리 코드.
     * 
     * @return CATEGORY_* 상수 중 하나, 타겟 없으면 null
     */
    String getTopTargetCategory();

    // ═══════════════════════════════════════════════════════════════
    // Deprecated (하위 호환용, 다음 메이저에서 제거)
    // ═══════════════════════════════════════════════════════════════

    /**
     * @deprecated Use {@link #getTopTargetId()} instead
     */
    @Deprecated
    default Optional<OptimizationHint> suggestTarget(String category) {
        return Optional.empty();
    }

    /**
     * @deprecated Use primitive methods instead
     */
    @Deprecated
    default List<OptimizationHint> getTopHints(int n) {
        return Collections.emptyList();
    }

    /**
     * @deprecated Fuse should determine pressure threshold
     */
    @Deprecated
    default boolean isUnderPressure() {
        return false;
    }
}
