package com.pulse.api.hook;

/**
 * 훅 타입 열거형.
 * Pulse가 제공하는 훅 포인트 정의.
 * 
 * @since Pulse 2.0
 */
public enum HookType {
    /** Lua 함수 호출 훅 */
    LUA_CALL,

    /** 틱 시작/종료 훅 */
    TICK_START,
    TICK_END,

    /** 렌더 프레임 훅 */
    RENDER_FRAME,

    /** 좀비 업데이트 훅 */
    ZOMBIE_UPDATE,

    /** 경로찾기 훅 */
    PATHFINDING,

    /** IsoGrid 훅 */
    ISO_GRID,

    /** 세이브/로드 훅 */
    SAVE,
    LOAD
}
