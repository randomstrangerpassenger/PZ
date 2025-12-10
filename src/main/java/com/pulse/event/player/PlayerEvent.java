package com.pulse.event.player;

import com.pulse.access.AccessWidener;
import com.pulse.event.Event;

/**
 * 플레이어 관련 이벤트 기본 클래스.
 * 
 * 플레이어 객체는 Object 타입으로 저장됩니다.
 * 이는 의도적인 설계로, Pulse가 PZ 클래스에 직접 의존하지 않고
 * 런타임에 리플렉션을 통해 접근하기 위함입니다.
 * 
 * IsoPlayer 메서드 접근 예시:
 * 
 * <pre>
 * PlayerEvent event = ...;
 * // 직접 캐스팅 (PZ 클래스패스 필요)
 * IsoPlayer player = (IsoPlayer) event.getPlayer();
 * 
 * // 또는 헬퍼 메서드 사용
 * String username = event.getPlayerUsername();
 * float x = event.getPlayerX();
 * </pre>
 */
public abstract class PlayerEvent extends Event {

    private final Object player;

    protected PlayerEvent(Object player, boolean cancellable) {
        super(cancellable);
        this.player = player;
    }

    /**
     * 플레이어 객체 반환.
     * 런타임에서 zombie.characters.IsoPlayer 타입입니다.
     * 
     * @return 플레이어 객체 (IsoPlayer)
     */
    public Object getPlayer() {
        return player;
    }

    // ─────────────────────────────────────────────────────────────
    // 플레이어 정보 헬퍼 메서드 (리플렉션 기반)
    // ─────────────────────────────────────────────────────────────

    /**
     * 플레이어 유저네임 반환.
     */
    public String getPlayerUsername() {
        if (player == null)
            return null;
        try {
            Object result = AccessWidener.invoke(player, "getUsername");
            return result != null ? result.toString() : null;
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 플레이어 X 좌표.
     */
    public float getPlayerX() {
        if (player == null)
            return 0;
        try {
            Object result = AccessWidener.invoke(player, "getX");
            return result instanceof Number n ? n.floatValue() : 0;
        } catch (Exception e) {
            return 0;
        }
    }

    /**
     * 플레이어 Y 좌표.
     */
    public float getPlayerY() {
        if (player == null)
            return 0;
        try {
            Object result = AccessWidener.invoke(player, "getY");
            return result instanceof Number n ? n.floatValue() : 0;
        } catch (Exception e) {
            return 0;
        }
    }

    /**
     * 플레이어 Z 좌표 (층).
     */
    public float getPlayerZ() {
        if (player == null)
            return 0;
        try {
            Object result = AccessWidener.invoke(player, "getZ");
            return result instanceof Number n ? n.floatValue() : 0;
        } catch (Exception e) {
            return 0;
        }
    }

    /**
     * 플레이어 체력.
     */
    public float getPlayerHealth() {
        if (player == null)
            return 0;
        try {
            Object bodyDamage = AccessWidener.invoke(player, "getBodyDamage");
            if (bodyDamage != null) {
                Object result = AccessWidener.invoke(bodyDamage, "getOverallBodyHealth");
                return result instanceof Number n ? n.floatValue() : 0;
            }
        } catch (Exception e) {
            // 무시
        }
        return 0;
    }

    /**
     * 플레이어 생존 여부.
     */
    public boolean isPlayerAlive() {
        if (player == null)
            return false;
        try {
            Object result = AccessWidener.invoke(player, "isDead");
            return !(result instanceof Boolean b && b);
        } catch (Exception e) {
            return true;
        }
    }

    /**
     * 플레이어가 멀티플레이어 클라이언트인지.
     */
    public boolean isLocalPlayer() {
        if (player == null)
            return false;
        try {
            Object result = AccessWidener.invoke(player, "isLocalPlayer");
            return result instanceof Boolean b && b;
        } catch (Exception e) {
            return false;
        }
    }
}
