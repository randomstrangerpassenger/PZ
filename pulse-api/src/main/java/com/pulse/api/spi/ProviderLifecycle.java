package com.pulse.api.spi;

/**
 * 프로바이더 생명주기 상태.
 */
public enum ProviderLifecycle {

    /** 등록됨, 아직 초기화 안 됨 */
    REGISTERED,

    /** 초기화 중 */
    INITIALIZING,

    /** 활성화됨, 정상 동작 중 */
    ACTIVE,

    /** 일시 정지됨 */
    SUSPENDED,

    /** 종료 중 */
    SHUTTING_DOWN,

    /** 종료됨 */
    TERMINATED,

    /** 오류 발생 */
    ERROR
}
