package com.pulse.api.hook;

/**
 * Lua 호출 콜백 인터페이스.
 * 
 * Lua 함수 호출 시 알림을 받기 위한 콜백.
 * Echo 등 모드에서 구현하여 PulseHookRegistry에 등록.
 * 
 * @since Pulse 2.1
 */
public interface ILuaCallCallback {

    /**
     * Lua 함수 호출 시작 (기본)
     * 
     * @param function Lua 함수 객체
     */
    default void onLuaCallStart(Object function) {
    }

    /**
     * Lua 함수 호출 종료 (기본)
     * 
     * @param function Lua 함수 객체
     */
    default void onLuaCallEnd(Object function) {
    }

    /**
     * Lua 함수 호출 시작 (시간 측정용)
     * 
     * @param function   Lua 함수 객체
     * @param startNanos System.nanoTime() at call start
     */
    default void onLuaCallStart(Object function, long startNanos) {
        onLuaCallStart(function);
    }

    /**
     * Lua 함수 호출 종료 (시간 측정용)
     * 
     * @param function Lua 함수 객체
     * @param endNanos System.nanoTime() at call end
     */
    default void onLuaCallEnd(Object function, long endNanos) {
        onLuaCallEnd(function);
    }

    /**
     * 간편 콜백 - 함수 이름과 소요 시간으로 호출됨.
     * 이 메서드를 구현하면 start/end를 따로 처리할 필요 없음.
     * 
     * @param functionName  함수 이름
     * @param durationNanos 소요 시간 (나노초)
     */
    default void onLuaCall(String functionName, long durationNanos) {
    }
}
