package com.pulse.adapter;

import com.pulse.api.PulseSide;
import com.pulse.api.adapter.SideDetector;
import com.pulse.api.log.PulseLogger;

/**
 * Build41용 Side 감지기.
 * 
 * v4 Phase 2: 기존 Pulse.detectSide() 로직을 격리.
 * 리플렉션 기반으로 zombie.network.GameServer 접근.
 * 
 * @since Pulse 0.8.0
 */
public class Build41SideDetector implements SideDetector {

    private static final String LOG = PulseLogger.PULSE;

    @Override
    public PulseSide detect() {
        try {
            // GameServer 클래스 로드 시도
            Class<?> gameServerClass = Class.forName("zombie.network.GameServer");
            java.lang.reflect.Field bServerField = gameServerClass.getDeclaredField("bServer");
            bServerField.setAccessible(true);
            boolean isServer = bServerField.getBoolean(null);

            if (isServer) {
                // 서버 모드 - 헤드리스인지 확인
                try {
                    Class<?> gameWindowClass = Class.forName("zombie.GameWindow");
                    java.lang.reflect.Field bNoRenderField = gameWindowClass.getDeclaredField("bNoRender");
                    bNoRenderField.setAccessible(true);
                    boolean noRender = bNoRenderField.getBoolean(null);

                    return noRender ? PulseSide.DEDICATED_SERVER : PulseSide.INTEGRATED_SERVER;
                } catch (Exception e) {
                    // 렌더링 체크 실패 - 아마도 데디케이티드
                    return PulseSide.DEDICATED_SERVER;
                }
            } else {
                // 클라이언트 모드
                return PulseSide.CLIENT;
            }
        } catch (ClassNotFoundException e) {
            // 게임 클래스 로드 전 - 나중에 다시 감지
            return PulseSide.UNKNOWN;
        } catch (Exception e) {
            PulseLogger.warn(LOG, "Side detection failed: {}", e.getMessage());
            return PulseSide.UNKNOWN;
        }
    }

    @Override
    public boolean isAvailable() {
        try {
            Class.forName("zombie.network.GameServer");
            return true;
        } catch (ClassNotFoundException e) {
            return false;
        }
    }

    @Override
    public int getPriority() {
        return 100; // Build41은 기본 우선순위
    }
}
