package com.mutagen.event.lifecycle;

import com.mutagen.event.Event;

/**
 * 게임 틱마다 발생하는 이벤트
 */
public class GameTickEvent extends Event {
    
    private final long tick;
    private final float deltaTime;
    
    public GameTickEvent(long tick, float deltaTime) {
        super(false);  // 취소 불가
        this.tick = tick;
        this.deltaTime = deltaTime;
    }
    
    /**
     * 현재 틱 번호
     */
    public long getTick() {
        return tick;
    }
    
    /**
     * 이전 틱과의 시간 간격 (초)
     */
    public float getDeltaTime() {
        return deltaTime;
    }
}
