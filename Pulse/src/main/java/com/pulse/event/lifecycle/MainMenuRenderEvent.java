package com.pulse.event.lifecycle;

import com.pulse.api.event.Event;

/**
 * 메인 메뉴 렌더 이벤트
 * 
 * MainScreenState.render()가 호출될 때 발생합니다.
 * 이 이벤트를 구독하여 게임에서 메뉴로 복귀했는지 감지할 수 있습니다.
 * 
 * @since Pulse 2.1
 */
public class MainMenuRenderEvent extends Event {

    private static long renderCount = 0;

    public MainMenuRenderEvent() {
        super(false);
        renderCount++;
    }

    /**
     * 현재 렌더 카운트 (게임 시작 후 메뉴 렌더 횟수)
     */
    public long getRenderCount() {
        return renderCount;
    }

    /**
     * 렌더 카운트 리셋 (게임 진입 시)
     */
    public static void resetRenderCount() {
        renderCount = 0;
    }
}
