package com.mutagen.event;

/**
 * 이벤트 리스너 우선순위.
 * 높은 우선순위가 먼저 실행됨.
 */
public enum EventPriority {
    
    /**
     * 가장 먼저 실행 (모니터링, 로깅용)
     */
    HIGHEST(100),
    
    /**
     * 높은 우선순위
     */
    HIGH(75),
    
    /**
     * 기본 우선순위
     */
    NORMAL(50),
    
    /**
     * 낮은 우선순위
     */
    LOW(25),
    
    /**
     * 가장 나중에 실행 (최종 처리용)
     */
    LOWEST(0);
    
    private final int value;
    
    EventPriority(int value) {
        this.value = value;
    }
    
    public int getValue() {
        return value;
    }
}
