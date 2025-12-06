package com.pulse.network;

/**
 * 네트워크 사이드.
 * 패킷이 어느 방향으로 전송되는지 정의.
 */
public enum NetworkSide {
    /**
     * 클라이언트 → 서버
     */
    SERVER,

    /**
     * 서버 → 클라이언트
     */
    CLIENT,

    /**
     * 양방향
     */
    BOTH
}
