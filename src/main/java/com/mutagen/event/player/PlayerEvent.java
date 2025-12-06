package com.mutagen.event.player;

import com.mutagen.event.Event;

/**
 * 플레이어 관련 이벤트 기본 클래스
 */
public abstract class PlayerEvent extends Event {
    
    // TODO: IsoPlayer 타입으로 변경
    private final Object player;
    
    protected PlayerEvent(Object player, boolean cancellable) {
        super(cancellable);
        this.player = player;
    }
    
    public Object getPlayer() {
        return player;
    }
}
