package com.pulse.event.multiplayer;

import com.pulse.api.event.Event;

/**
 * 플레이어 서버 접속 이벤트.
 * 취소 가능 - 접속을 거부할 수 있음.
 */
public class PlayerConnectEvent extends Event {

    private final Object connection; // UdpConnection
    private final String username;
    private final String steamId;
    private String kickReason;

    public PlayerConnectEvent(Object connection, String username, String steamId) {
        super(true); // cancellable
        this.connection = connection;
        this.username = username;
        this.steamId = steamId;
    }

    public Object getConnection() {
        return connection;
    }

    public String getUsername() {
        return username;
    }

    public String getSteamId() {
        return steamId;
    }

    /**
     * 접속 거부 - cancel()과 함께 사용.
     */
    public void kick(String reason) {
        this.kickReason = reason;
        cancel();
    }

    public String getKickReason() {
        return kickReason;
    }

    @Override
    public String getEventName() {
        return "PlayerConnect";
    }
}
