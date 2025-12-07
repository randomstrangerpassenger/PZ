package com.pulse.event.npc;

/**
 * 좀비가 스폰될 때 발생.
 * 취소 가능 - 스폰을 막을 수 있음.
 */
public class ZombieSpawnEvent extends ZombieEvent {

    private final float x, y, z;
    private final SpawnReason reason;

    public ZombieSpawnEvent(Object zombie, float x, float y, float z, SpawnReason reason) {
        super(zombie);
        this.x = x;
        this.y = y;
        this.z = z;
        this.reason = reason;
    }

    public float getX() {
        return x;
    }

    public float getY() {
        return y;
    }

    public float getZ() {
        return z;
    }

    public SpawnReason getReason() {
        return reason;
    }

    @Override
    public String getEventName() {
        return "ZombieSpawn";
    }

    public enum SpawnReason {
        NATURAL, // 자연 스폰
        MIGRATION, // 이동/마이그레이션
        SOUND, // 소리로 인한 스폰
        META, // 메타 이벤트
        RESPAWN, // 리스폰
        SCRIPTED // 스크립트에 의한 스폰
    }
}
