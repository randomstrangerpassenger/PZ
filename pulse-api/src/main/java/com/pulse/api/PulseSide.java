package com.pulse.api;

/**
 * Pulse 실행 환경 사이드.
 * 클라이언트/서버 구분을 위한 enum.
 * 
 * <pre>
 * // 사용 예시
 * if (Pulse.getSide().isClient()) {
 *     // 클라이언트 전용 코드
 * }
 * 
 * if (Pulse.isDedicatedServer()) {
 *     // 데디케이티드 서버 전용 코드
 * }
 * </pre>
 * 
 * @since 1.1.0
 */
public enum PulseSide {

    /**
     * 클라이언트 (싱글플레이어가 아닌 순수 클라이언트).
     */
    CLIENT,

    /**
     * 데디케이티드 서버 (헤드리스).
     */
    DEDICATED_SERVER,

    /**
     * 통합 서버 (싱글플레이어 또는 호스트+플레이).
     */
    INTEGRATED_SERVER,

    /**
     * 아직 감지되지 않음.
     */
    UNKNOWN;

    /**
     * 클라이언트 환경인지 확인.
     * INTEGRATED_SERVER도 클라이언트 역할을 포함.
     * 
     * @return 클라이언트면 true
     */
    public boolean isClient() {
        return this == CLIENT || this == INTEGRATED_SERVER;
    }

    /**
     * 서버 환경인지 확인.
     * INTEGRATED_SERVER도 서버 역할을 포함.
     * 
     * @return 서버면 true
     */
    public boolean isServer() {
        return this == DEDICATED_SERVER || this == INTEGRATED_SERVER;
    }

    /**
     * 데디케이티드(헤드리스) 서버인지 확인.
     * 
     * @return 데디케이티드 서버면 true
     */
    public boolean isDedicated() {
        return this == DEDICATED_SERVER;
    }

    /**
     * 데디케이티드 서버인지 확인 (별칭).
     * 
     * @return 데디케이티드 서버면 true
     */
    public boolean isDedicatedServer() {
        return this == DEDICATED_SERVER;
    }

    /**
     * 싱글플레이어 또는 호스트 모드인지 확인.
     * 
     * @return 통합 서버면 true
     */
    public boolean isIntegrated() {
        return this == INTEGRATED_SERVER;
    }

    /**
     * 사이드가 아직 감지되지 않았는지 확인.
     * 
     * @return 알 수 없으면 true
     */
    public boolean isUnknown() {
        return this == UNKNOWN;
    }
}
