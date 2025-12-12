package com.pulse.api;

import com.pulse.api.access.*;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * GameAccess 및 분리된 Access 클래스 회귀 테스트.
 * 리팩토링 후 기존 동작이 유지되는지 검증.
 */
class GameAccessTest {

    @Test
    void worldAccess_isWorldLoaded_returnsFalseWhenNotLoaded() {
        // 게임 실행 전에는 월드가 로드되지 않음
        assertFalse(WorldAccess.isWorldLoaded());
    }

    @Test
    void playerAccess_getLocalPlayer_returnsNullWhenNotInGame() {
        // 게임 실행 전에는 플레이어가 없음
        assertNull(PlayerAccess.getLocalPlayer());
    }

    @Test
    void timeAccess_getGameHour_returnsZeroWhenNotLoaded() {
        // GameTime이 없으면 0 반환
        assertEquals(0, TimeAccess.getGameHour());
    }

    @Test
    void networkAccess_isMultiplayer_returnsFalseByDefault() {
        // 게임 실행 전에는 싱글플레이어
        assertFalse(NetworkAccess.isMultiplayer());
    }

    @Test
    void networkAccess_isSinglePlayer_returnsTrueByDefault() {
        assertTrue(NetworkAccess.isSinglePlayer());
    }

    @Test
    void gameAccess_legacy_isWorldLoaded_matchesWorldAccess() {
        // 레거시 GameAccess와 새 WorldAccess가 동일한 결과 반환
        assertEquals(GameAccess.isWorldLoaded(), WorldAccess.isWorldLoaded());
    }
}
