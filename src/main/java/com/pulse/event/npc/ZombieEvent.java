package com.pulse.event.npc;

import com.pulse.event.Event;

/**
 * 좀비/NPC 관련 이벤트 기본 클래스.
 */
public abstract class ZombieEvent extends Event {

    private final Object zombie; // IsoZombie

    protected ZombieEvent(Object zombie) {
        this.zombie = zombie;
    }

    public Object getZombie() {
        return zombie;
    }
}
