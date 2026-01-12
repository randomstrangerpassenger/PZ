package com.pulse.api.access;

import com.pulse.api.PublicAPI;
import com.pulse.api.util.ReflectionClassCache;

import java.lang.reflect.Method;

/**
 * 게임 상태(GameState) 접근 API.
 * 
 * 현재 게임이 메인 메뉴인지, 게임 중인지 확인할 수 있습니다.
 * 세션 관리에 활용됩니다.
 * 
 * @since 1.1.1
 */
@PublicAPI(since = "1.1.1", status = PublicAPI.Status.EXPERIMENTAL)
public final class GameStateAccess {

    private GameStateAccess() {
    }

    private static final ReflectionClassCache<Object> gsmCache = new ReflectionClassCache<>(
            "zombie.gameStates.GameStateMachine");

    // 캐시된 상태 (리플렉션 비용 절감)
    private static volatile String lastStateName = null;
    private static volatile long lastCheckTime = 0;
    private static final long CACHE_DURATION_MS = 100; // 100ms 캐시

    /**
     * 클래스 참조 갱신.
     */
    public static void refresh() {
        gsmCache.refresh();
        lastStateName = null;
        lastCheckTime = 0;
    }

    /**
     * 현재 게임 상태 이름 반환.
     * 
     * @return 상태 클래스 단순 이름 (예: "MainScreenState", "IngameState") 또는 null
     */
    public static String getCurrentStateName() {
        long now = System.currentTimeMillis();
        if (lastStateName != null && (now - lastCheckTime) < CACHE_DURATION_MS) {
            return lastStateName;
        }

        try {
            Class<?> gsmClass = gsmCache.get();
            if (gsmClass == null)
                return null;

            // GameStateMachine.instance
            Method instanceMethod = gsmClass.getMethod("instance");
            Object gsm = instanceMethod.invoke(null);
            if (gsm == null)
                return null;

            // getCurrent()
            Method getCurrentMethod = gsmClass.getMethod("getCurrent");
            Object currentState = getCurrentMethod.invoke(gsm);
            if (currentState == null)
                return null;

            lastStateName = currentState.getClass().getSimpleName();
            lastCheckTime = now;
            return lastStateName;
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 현재 게임 중인지 확인.
     * 
     * IngameState일 때 true.
     * 
     * @return 게임 중이면 true
     */
    public static boolean isInGame() {
        String state = getCurrentStateName();
        return "IngameState".equals(state);
    }

    /**
     * 현재 메인 메뉴인지 확인.
     * 
     * MainScreenState일 때 true.
     * 
     * @return 메인 메뉴면 true
     */
    public static boolean isOnMainMenu() {
        String state = getCurrentStateName();
        return "MainScreenState".equals(state);
    }

    /**
     * 게임 중이거나 월드가 로드된 상태인지 확인.
     * 
     * WorldAccess.isWorldLoaded()와 함께 사용하여 더 정확한 상태 감지.
     * 
     * @return 게임 중이고 월드가 로드되었으면 true
     */
    public static boolean isInGameWithWorld() {
        return isInGame() && WorldAccess.isWorldLoaded();
    }

    /**
     * 로딩 중인지 확인.
     * 
     * LoadingQueueState일 때 true.
     * 
     * @return 로딩 중이면 true
     */
    public static boolean isLoading() {
        String state = getCurrentStateName();
        return "LoadingQueueState".equals(state);
    }
}
