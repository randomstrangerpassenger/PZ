package com.pulse.api;

import java.util.function.Consumer;

/**
 * Pulse 이벤트 버스 인터페이스.
 * 이벤트 등록 및 발행을 위한 계약.
 */
public interface IPulseEventBus {

    /**
     * 이벤트 리스너 등록
     * 
     * @param eventType 이벤트 타입 클래스
     * @param listener  리스너 함수
     * @param <T>       이벤트 타입
     */
    <T extends IPulseEvent> void register(Class<T> eventType, Consumer<T> listener);

    /**
     * 이벤트 리스너 해제
     * 
     * @param eventType 이벤트 타입 클래스
     * @param listener  리스너 함수
     * @param <T>       이벤트 타입
     */
    <T extends IPulseEvent> void unregister(Class<T> eventType, Consumer<T> listener);

    /**
     * 이벤트 발행
     * 
     * @param event 발행할 이벤트
     * @param <T>   이벤트 타입
     * @return 이벤트 (체이닝용)
     */
    <T extends IPulseEvent> T post(T event);
}
