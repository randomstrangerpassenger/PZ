package com.pulse.api.telemetry;

/**
 * 최적화 힌트 - 순수 측정치만 포함.
 * 
 * severity는 "심각도 측정치"이지 "우선순위 정책"이 아님.
 * 어떤 모드가 어떻게 처리할지는 소비측이 결정.
 * 
 * @since Pulse 2.0
 */
public record OptimizationHint(
        String category, // "CPU", "MEMORY", "RENDER", "NETWORK"
        String target, // "zombie_ai", "pathfinding", "chunk_streaming"
        double severity, // 0.0 ~ 1.0 (측정된 부하 수준)
        long sampleCount, // 측정 샘플 수
        String description // 사람이 읽을 수 있는 설명
) {
    public static final String CATEGORY_CPU = "CPU";
    public static final String CATEGORY_MEMORY = "MEMORY";
    public static final String CATEGORY_RENDER = "RENDER";
    public static final String CATEGORY_NETWORK = "NETWORK";
}
