package com.pulse.event.player;

/**
 * 플레이어 업데이트 시 발생
 */
public class PlayerUpdateEvent extends PlayerEvent {
    
    public PlayerUpdateEvent(Object player) {
        super(player, false);
    }
}
