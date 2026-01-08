package com.echo;

/**
 * Echo 라이프사이클 단계
 * 
 * 핫패스 진입 차단에 사용됩니다.
 * NOT_INITIALIZED 또는 SHUTTING_DOWN 상태에서는 핫패스가 즉시 반환됩니다.
 * 
 * @since Bundle A - Hot Path 무음화
 */
public enum LifecyclePhase {
    /** 초기화 전 기본값 - 핫패스 진입 차단 */
    NOT_INITIALIZED,

    /** 초기화 진행 중 */
    INITIALIZING,

    /** 정상 동작 중 - 핫패스 접근 허용 */
    RUNNING,

    /** 종료 진행 중 - 핫패스 진입 차단 */
    SHUTTING_DOWN
}
