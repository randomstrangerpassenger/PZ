package com.pulse.api;

/**
 * Pulse 실행 환경 사이드.
 * 클라이언트/서버 구분에 사용.
 */
public enum PulseSide {

    /**
     * 순수 클라이언트 (싱글플레이어 포함)
     */
    CLIENT,

    /**
     * 통합 서버 (싱글플레이어 호스트)
     */
    INTEGRATED_SERVER,

    /**
     * 데디케이티드 서버
     */
    DEDICATED_SERVER,

    /**
     * 알 수 없음 (초기화 전)
     */
    UNKNOWN;

    /**
     * 클라이언트 역할을 수행하는지 확인
     */
    public boolean isClient() {
        return this == CLIENT || this == INTEGRATED_SERVER;
    }

    /**
     * 서버 역할을 수행하는지 확인
     */
    public boolean isServer() {
        return this == DEDICATED_SERVER || this == INTEGRATED_SERVER;
    }

    /**
     * 데디케이티드 서버인지 확인
     */
    public boolean isDedicatedServer() {
        return this == DEDICATED_SERVER;
    }
}
