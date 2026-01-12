package com.pulse.adapter.zombie;

import com.pulse.api.version.IVersionAdapter;

/**
 * IsoZombie 관련 버전별 API 추상화 인터페이스.
 * 
 * IsoZombie 클래스의 메서드에 접근하는 표준화된 방법을 제공합니다.
 * 각 빌드 버전별로 다른 구현을 제공하여 버전 호환성을 보장합니다.
 * 
 * 사용 예:
 * 
 * <pre>
 * IZombieAdapter adapter = ZombieAdapterProvider.get();
 * int id = adapter.getZombieId(zombieInstance);
 * float dist = adapter.getDistanceToNearestPlayer(zombieInstance);
 * </pre>
 * 
 * @since Pulse 1.4
 */
public interface IZombieAdapter extends IVersionAdapter {

    // ═══════════════════════════════════════════════════════════════
    // Zombie ID Methods
    // ═══════════════════════════════════════════════════════════════

    /**
     * 좀비의 고유 ID를 반환.
     * 
     * MP 환경에서는 서버 동기화된 ID를 반환해야 합니다.
     * 
     * @param zombie IsoZombie 인스턴스
     * @return 좀비 ID (실패 시 hashCode)
     */
    int getZombieId(Object zombie);

    /**
     * 온라인 ID 반환 (MP 전용).
     * 
     * @param zombie IsoZombie 인스턴스
     * @return 온라인 ID, 없으면 -1
     */
    int getOnlineId(Object zombie);

    /**
     * 로컬 ID 반환.
     * 
     * @param zombie IsoZombie 인스턴스
     * @return 로컬 ID
     */
    int getLocalId(Object zombie);

    // ═══════════════════════════════════════════════════════════════
    // Position & Distance Methods
    // ═══════════════════════════════════════════════════════════════

    /**
     * 좀비의 X 좌표 반환.
     */
    float getX(Object zombie);

    /**
     * 좀비의 Y 좌표 반환.
     */
    float getY(Object zombie);

    /**
     * 좀비의 Z 좌표 반환.
     */
    float getZ(Object zombie);

    /**
     * 가장 가까운 플레이어와의 거리 제곱 반환.
     * 
     * @param zombie IsoZombie 인스턴스
     * @return 거리 제곱 (플레이어 없으면 MAX_VALUE)
     */
    float getDistanceSquaredToNearestPlayer(Object zombie);

    // ═══════════════════════════════════════════════════════════════
    // State Methods
    // ═══════════════════════════════════════════════════════════════

    /**
     * 좀비가 공격 중인지 확인.
     * 
     * @param zombie IsoZombie 인스턴스
     * @return 공격 중이면 true
     */
    boolean isAttacking(Object zombie);

    /**
     * 좀비가 타겟을 가지고 있는지 확인.
     * 
     * @param zombie IsoZombie 인스턴스
     * @return 타겟이 있으면 true
     */
    boolean hasTarget(Object zombie);

    /**
     * 좀비의 현재 타겟 반환.
     * 
     * @param zombie IsoZombie 인스턴스
     * @return 타겟 객체 (IsoMovingObject), 없으면 null
     */
    Object getTarget(Object zombie);

    /**
     * 좀비가 크롤러인지 확인.
     * 
     * @param zombie IsoZombie 인스턴스
     * @return 크롤러면 true
     */
    boolean isCrawler(Object zombie);

    /**
     * 좀비가 넘어져 있는지 확인.
     * 
     * @param zombie IsoZombie 인스턴스
     * @return 바닥에 있으면 true
     */
    boolean isOnFloor(Object zombie);

    // ═══════════════════════════════════════════════════════════════
    // Engagement Methods (throttle용)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 최근 피격 여부 확인.
     * 
     * hitTime이 양수이면 최근에 피격된 것으로 판단.
     * hitTime은 피격 후 감소하는 타이머로 추정됨.
     * 
     * @param zombie IsoZombie 인스턴스
     * @return true면 최근 피격됨
     */
    default boolean isRecentlyHit(Object zombie) {
        return getHitTime(zombie) > 0;
    }

    /**
     * hitTime 값 반환.
     * 
     * IsoZombie.getHitTime() 호출.
     * 피격 후 일정 시간 동안 양수로 유지됨.
     * 
     * @param zombie IsoZombie 인스턴스
     * @return hitTime 값 (0 이하면 피격 상태 아님)
     */
    int getHitTime(Object zombie);

    /**
     * 최근 교전 여부 (통합 판정).
     * 
     * 다음 중 하나라도 true면 recentlyEngaged:
     * - isRecentlyHit() == true
     * - hasTarget() == true
     * - isAttacking() == true
     * 
     * @param zombie IsoZombie 인스턴스
     * @return true면 즉시 FULL throttle 적용
     */
    default boolean isRecentlyEngaged(Object zombie) {
        return isRecentlyHit(zombie) || hasTarget(zombie) || isAttacking(zombie);
    }
}
