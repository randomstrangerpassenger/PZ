package com.pulse.api.access;

/**
 * 월드 상태 접근 인터페이스.
 * 
 * 스냅샷/쿼리 기반 - 엔진 객체 직접 반환 금지.
 * Echo/Fuse/Nerve가 월드 상태를 확인할 때 사용.
 * 
 * @since Pulse 2.0 - Phase 4
 */
public interface IWorldAccess {

    /**
     * 월드 로드 상태 확인.
     * 
     * @return true if world is loaded and has at least one cell
     */
    boolean isWorldLoaded();

    /**
     * 현재 월드 이름 조회.
     * 
     * @return world name or null if not loaded
     */
    String getWorldName();

    /**
     * 월드 나이 (시간) 조회.
     * 
     * @return world age in in-game hours
     */
    int getWorldAgeHours();

    /**
     * 접속 플레이어 수 조회.
     * 
     * @return number of connected players (1 for singleplayer)
     */
    int getPlayerCount();
}
