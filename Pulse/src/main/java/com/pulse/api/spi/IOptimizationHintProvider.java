package com.pulse.api.spi;

/**
 * SPI interface for optimization hint providers.
 * 
 * Provides primitive-only metrics from analysis modules (e.g., profiler)
 * to optimization modules (e.g., optimizer) without object coupling.
 * 
 * Hub & Spoke 원칙:
 * - Provider(프로파일러): 관측치만 제공 (severity, category)
 * - Consumer(옵티마이저): 판단/정책 결정 (임계값, 조치)
 * 
 * @since Pulse 1.1.0
 * @since Pulse 2.0.0 - Primitive-only API
 * @since Pulse 3.0.0 - 헌법 정화: deprecated 메서드 제거
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
    // Primitive-only API (v2.0+)
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
}
