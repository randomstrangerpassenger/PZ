package com.pulse.api.profiler;

import java.util.Collection;

/**
 * 최적화 포인트 레지스트리 인터페이스.
 * 
 * Pulse Core가 관리하는 최적화 포인트에 대한 읽기 전용 접근을 제공합니다.
 * Echo는 이 인터페이스를 통해 최적화 포인트 정보를 수집합니다.
 * 
 * @since Pulse 2.0 - Phase 4
 */
public interface IOptimizationPointRegistry {

    /**
     * 모든 최적화 포인트 ID 반환.
     * 
     * @return 등록된 포인트 ID 컬렉션 (읽기 전용)
     */
    Collection<String> getPointIds();

    /**
     * 특정 포인트의 활성화 상태 확인.
     * 
     * @param pointId 포인트 ID
     * @return 활성화되어 있으면 true
     */
    boolean isPointEnabled(String pointId);

    /**
     * 특정 포인트의 현재 측정값 반환.
     * 
     * @param pointId 포인트 ID
     * @return 측정값 (나노초), 포인트가 없으면 -1
     */
    long getPointValue(String pointId);

    /**
     * 등록된 포인트 개수.
     * 
     * @return 총 포인트 수
     */
    int getPointCount();

    /**
     * 포인트 존재 여부 확인.
     * 
     * @param pointId 포인트 ID
     * @return 존재하면 true
     */
    boolean hasPoint(String pointId);
}
