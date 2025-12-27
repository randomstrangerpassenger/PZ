package com.pulse.event.lifecycle;

import com.pulse.api.event.Event;

/**
 * 게임 라이프사이클 이벤트들
 */

// ─────────────────────────────────────────────────────────────
// 게임 시작/종료
// ─────────────────────────────────────────────────────────────

/**
 * 게임 초기화 완료 시 발생
 */
public class GameInitEvent extends Event {
    public GameInitEvent() {
        super(false);
    }
}
