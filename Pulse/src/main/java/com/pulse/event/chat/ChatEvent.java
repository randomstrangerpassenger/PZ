package com.pulse.event.chat;

import com.pulse.api.event.Event;

/**
 * 채팅 관련 이벤트 기본 클래스.
 */
public abstract class ChatEvent extends Event {

    private final Object player; // IsoPlayer
    private String message;

    protected ChatEvent(Object player, String message) {
        this.player = player;
        this.message = message;
    }

    public Object getPlayer() {
        return player;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
