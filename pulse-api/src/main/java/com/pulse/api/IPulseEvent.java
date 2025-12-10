package com.pulse.api;

/**
 * Pulse 이벤트 기본 인터페이스.
 * 모든 Pulse 이벤트가 구현해야 하는 기본 계약.
 */
public interface IPulseEvent {

    /**
     * 이벤트 이름 반환
     */
    String getEventName();

    /**
     * 이벤트가 취소 가능한지 여부
     */
    boolean isCancellable();

    /**
     * 이벤트가 취소되었는지 여부
     */
    boolean isCancelled();

    /**
     * 이벤트 취소 (취소 가능한 이벤트만)
     */
    void cancel();
}
