package com.pulse.event.chat;

/**
 * 채팅 메시지를 수신할 때 발생.
 */
public class ChatReceiveEvent extends ChatEvent {

    private final Object sender; // 메시지를 보낸 플레이어 (또는 null if system)

    public ChatReceiveEvent(Object player, String message, Object sender) {
        super(player, message);
        this.sender = sender;
    }

    public Object getSender() {
        return sender;
    }

    public boolean isSystemMessage() {
        return sender == null;
    }

    @Override
    public String getEventName() {
        return "ChatReceive";
    }
}
