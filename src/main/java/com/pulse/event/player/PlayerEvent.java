package com.pulse.event.player;

import com.pulse.event.Event;

/**
 * 플레이어 관련 이벤트 기본 클래스
 */
public abstract class PlayerEvent extends Event {

    // TODO: IsoPlayer 타입으로 변경 (현재 빌드 환경에서 참조 불가)
    private final Object player;

    protected PlayerEvent(Object player, boolean cancellable) {
        super(cancellable);
        this.player = player;
    }

    public Object getPlayer() {
        return player;
    }
}
