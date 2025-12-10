package com.pulse.event.npc;

/**
 * 좀비 AI 행동 결정 시 발생.
 * 취소 가능 - 행동을 막거나 변경할 수 있음.
 */
public class ZombieBehaviorEvent extends ZombieEvent {

    private BehaviorType behavior;
    private Object target; // 대상 (플레이어, 위치 등)

    public ZombieBehaviorEvent(Object zombie, BehaviorType behavior, Object target) {
        super(zombie);
        this.behavior = behavior;
        this.target = target;
    }

    public BehaviorType getBehavior() {
        return behavior;
    }

    public void setBehavior(BehaviorType behavior) {
        this.behavior = behavior;
    }

    public Object getTarget() {
        return target;
    }

    public void setTarget(Object target) {
        this.target = target;
    }

    @Override
    public String getEventName() {
        return "ZombieBehavior";
    }

    public enum BehaviorType {
        IDLE, // 대기
        WANDER, // 배회
        CHASE, // 추적
        ATTACK, // 공격
        INVESTIGATE, // 조사 (소리/시야)
        FEED, // 시체 먹기
        CLIMB, // 등반
        BREAK_DOOR, // 문 부수기
        BREAK_WINDOW // 창문 부수기
    }
}
