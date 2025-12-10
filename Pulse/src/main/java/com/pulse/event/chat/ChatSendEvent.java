package com.pulse.event.chat;

/**
 * 플레이어가 채팅 메시지를 보낼 때 발생.
 * 취소 가능 - 메시지 전송을 막을 수 있음.
 */
public class ChatSendEvent extends ChatEvent {

    private final ChatType chatType;

    public ChatSendEvent(Object player, String message, ChatType chatType) {
        super(player, message);
        this.chatType = chatType;
    }

    public ChatType getChatType() {
        return chatType;
    }

    @Override
    public String getEventName() {
        return "ChatSend";
    }

    public enum ChatType {
        SAY, // 일반 채팅
        SHOUT, // 외침
        WHISPER, // 속삭임
        RADIO, // 무전기
        ADMIN, // 관리자
        FACTION, // 팩션
        SAFEHOUSE // 세이프하우스
    }
}
