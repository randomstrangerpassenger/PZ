package com.pulse.event.multiplayer;

import com.pulse.api.event.Event;

/**
 * 플레이어 서버 연결 종료 이벤트.
 */
public class PlayerDisconnectEvent extends Event {

    private final Object connection;
    private final String username;
    private final DisconnectReason reason;

    public PlayerDisconnectEvent(Object connection, String username, DisconnectReason reason) {
        this.connection = connection;
        this.username = username;
        this.reason = reason;
    }

    public Object getConnection() {
        return connection;
    }

    public String getUsername() {
        return username;
    }

    public DisconnectReason getReason() {
        return reason;
    }

    @Override
    public String getEventName() {
        return "PlayerDisconnect";
    }

    public enum DisconnectReason {
        QUIT, // 정상 종료
        TIMEOUT, // 타임아웃
        KICKED, // 강퇴
        BANNED, // 밴
        SERVER_FULL, // 서버 가득 참
        CONNECTION_LOST // 연결 끊김
    }
}
