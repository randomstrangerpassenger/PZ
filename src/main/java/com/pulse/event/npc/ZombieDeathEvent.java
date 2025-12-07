package com.pulse.event.npc;

/**
 * 좀비가 사망할 때 발생.
 */
public class ZombieDeathEvent extends ZombieEvent {

    private final Object killer; // IsoGameCharacter (플레이어 또는 다른 NPC)
    private final Object weapon; // 사용된 무기 (null 가능)

    public ZombieDeathEvent(Object zombie, Object killer, Object weapon) {
        super(zombie);
        this.killer = killer;
        this.weapon = weapon;
    }

    public Object getKiller() {
        return killer;
    }

    public Object getWeapon() {
        return weapon;
    }

    public boolean hasKiller() {
        return killer != null;
    }

    @Override
    public String getEventName() {
        return "ZombieDeath";
    }
}
