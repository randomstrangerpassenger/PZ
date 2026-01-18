package com.pulse.api;

/**
 * Pulse 이벤트 기본 인터페이스.
 * 모든 Pulse 이벤트가 구현해야 하는 기본 계약.
 * 
 * @deprecated v0.8.0부터 {@link com.pulse.api.event.Event} 사용을 권장합니다.
 *             이 인터페이스는 v1.0에서 제거될 예정입니다.
 * @see com.pulse.api.event.Event
 */
@Deprecated
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
