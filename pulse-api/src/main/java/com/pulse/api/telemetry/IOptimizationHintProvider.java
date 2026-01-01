package com.pulse.api.telemetry;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 최적화 힌트 제공자 SPI.
 * 
 * 프로파일러 모드가 구현하여 측정 결과를 제공.
 * 최적화 모드가 이를 소비하여 자체적으로 판단.
 * 
 * 금지: suggest, recommend, priority 같은 정책 어휘
 * 
 * @since Pulse 2.0
 */
public interface IOptimizationHintProvider {

    /**
     * 현재 수집된 모든 힌트 반환.
     */
    List<OptimizationHint> getHints();

    /**
     * 특정 카테고리의 힌트만 반환.
     */
    default List<OptimizationHint> getHintsByCategory(String category) {
        return getHints().stream()
                .filter(h -> h.category().equals(category))
                .collect(Collectors.toList());
    }

    /**
     * 최상위 심각도 힌트 반환.
     */
    default OptimizationHint getTopHint() {
        return getHints().stream()
                .max((a, b) -> Double.compare(a.severity(), b.severity()))
                .orElse(null);
    }
}
