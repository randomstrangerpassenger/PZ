package com.pulse.api;

/**
 * Echo → Nerve 성능 경보 이벤트 인터페이스.
 * 
 * Echo에서 성능 문제를 감지하면 이 이벤트를 발행하고,
 * Nerve에서 수신하여 자동 최적화 또는 사용자 알림을 처리합니다.
 * 
 * @since 1.0.1
 */
public interface PerformanceAlertEvent extends IPulseEvent {

    /**
     * 경보 유형
     */
    AlertType getAlertType();

    /**
     * 심각도 (0.0 ~ 1.0)
     * 0.0 = 정보성, 1.0 = 치명적
     */
    double getSeverity();

    /**
     * 경보 메시지
     */
    String getMessage();

    /**
     * 발생 타임스탬프 (epoch ms)
     */
    long getTimestamp();

    /**
     * 스레드 컨텍스트 (Nerve/Fuse 필터링용)
     */
    ThreadContext getThreadContext();

    /**
     * 발생 소스 ID (예: "FreezeDetector", "TickHistogram")
     */
    String getSourceId();

    /**
     * 경보 유형 열거형
     */
    enum AlertType {
        /** 틱 스파이크 감지 */
        LAG_SPIKE,
        /** 프리즈 경고 */
        FREEZE_WARNING,
        /** 메모리 압박 */
        MEMORY_PRESSURE,
        /** TPS 저하 */
        TPS_DROP,
        /** GC 일시정지 */
        GC_PAUSE,
        /** 엔티티 과부하 */
        ENTITY_OVERLOAD
    }

    /**
     * 스레드 컨텍스트 열거형
     */
    enum ThreadContext {
        /** 메인 게임 스레드 */
        MAIN,
        /** 렌더링 스레드 */
        RENDER,
        /** 네트워크 스레드 */
        NETWORK,
        /** I/O 스레드 */
        IO,
        /** 워커 스레드 */
        WORKER,
        /** 알 수 없음 */
        UNKNOWN
    }
}
