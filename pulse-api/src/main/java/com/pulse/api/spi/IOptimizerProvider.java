package com.pulse.api.spi;

import java.util.Collection;
import java.util.Map;

/**
 * 최적화 프로바이더 인터페이스.
 * Fuse와 같은 최적화 모드가 구현.
 * 
 * 다른 모드도 동일한 인터페이스를 구현하여 최적화 기능 제공 가능.
 */
public interface IOptimizerProvider extends IProvider {

    /**
     * 최적화 가능한 영역 목록 조회
     */
    Collection<String> getOptimizableAreas();

    /**
     * 특정 영역 최적화 적용
     * 
     * @param area 최적화 영역 이름
     * @return 적용 성공 여부
     */
    boolean applyOptimization(String area);

    /**
     * 특정 영역 최적화 해제
     * 
     * @param area 최적화 영역 이름
     * @return 해제 성공 여부
     */
    boolean removeOptimization(String area);

    /**
     * 현재 적용된 최적화 목록
     */
    Collection<String> getActiveOptimizations();

    /**
     * 모든 최적화 적용
     */
    void applyAllOptimizations();

    /**
     * 모든 최적화 해제
     */
    void removeAllOptimizations();

    /**
     * 최적화 통계 조회
     * 
     * @return 영역별 개선율 (%)
     */
    Map<String, Double> getOptimizationStats();

    /**
     * 최적화로 인한 전체 성능 개선율 (%)
     */
    double getTotalImprovementPercent();

    /**
     * 병목 지점 힌트 받기 (프로파일러 연동)
     * 
     * @param bottlenecks 병목 영역 목록
     */
    default void receiveBottleneckHints(Collection<String> bottlenecks) {
        // 기본 구현: 무시
    }
}
