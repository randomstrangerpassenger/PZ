package com.pulse.api.adapter;

import com.pulse.api.PulseSide;

/**
 * Side 감지 어댑터 인터페이스.
 * 
 * v4 Phase 2: 리플렉션 기반 감지 로직을 격리하여
 * Build41/Build42 간 호환성 관리.
 * 
 * @since Pulse 0.8.0
 */
public interface SideDetector {

    /**
     * 현재 실행 환경의 Side를 감지.
     * 
     * @return 감지된 Side (감지 실패 시 UNKNOWN)
     */
    PulseSide detect();

    /**
     * 이 감지기가 현재 환경에서 사용 가능한지 확인.
     * 
     * @return 사용 가능하면 true
     */
    default boolean isAvailable() {
        return true;
    }

    /**
     * 감지기 우선순위 (높을수록 먼저 시도).
     * 
     * @return 우선순위 값
     */
    default int getPriority() {
        return 0;
    }
}
