package com.pulse.api.access;

/**
 * 게임 상태 접근 인터페이스.
 * 
 * 스냅샷/쿼리 기반 - 엔진 객체 직접 반환 금지.
 * 메인 메뉴 상태, 게임 진입 상태 등을 확인할 때 사용.
 * 
 * @since Pulse 2.0 - Phase 4
 */
public interface IGameStateAccess {

    /**
     * 메인 메뉴 상태 확인.
     * 
     * @return true if on main menu
     */
    boolean isOnMainMenu();

    /**
     * 게임 플레이 중 상태 확인.
     * 
     * @return true if in game (not on main menu, loading, etc)
     */
    boolean isInGame();

    /**
     * 멀티플레이어 상태 확인.
     * 
     * @return true if current session is multiplayer
     */
    boolean isMultiplayer();

    /**
     * 일시정지 상태 확인.
     * 
     * @return true if game is paused
     */
    boolean isPaused();
}
