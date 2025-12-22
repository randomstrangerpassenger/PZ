package com.pulse.api.dto;

/**
 * Optimizer 상태 DTO.
 * 
 * <p>
 * Fuse, Nerve 등 최적화 모듈의 상태를 표현합니다.
 * </p>
 * 
 * @param enabled           활성화 여부
 * @param autoOptimize      자동 최적화 활성화 여부
 * @param optimizationLevel 최적화 레벨 (0-10)
 * @param lastUpdateMs      마지막 업데이트 시간 (epoch ms)
 * 
 * @since Pulse 1.6
 */
public record OptimizerStatus(
        boolean enabled,
        boolean autoOptimize,
        int optimizationLevel,
        long lastUpdateMs) {
    /**
     * 비활성화 상태 생성.
     */
    public static OptimizerStatus disabled() {
        return new OptimizerStatus(false, false, 0, 0);
    }

    /**
     * 기본 활성화 상태 생성.
     */
    public static OptimizerStatus defaultEnabled() {
        return new OptimizerStatus(true, true, 5, System.currentTimeMillis());
    }
}
