package com.mutagen.event.player;

/**
 * 플레이어가 데미지를 받을 때 발생 (취소 가능)
 */
public class PlayerDamageEvent extends PlayerEvent {
    
    private float damage;
    private final String damageType;
    
    public PlayerDamageEvent(Object player, float damage, String damageType) {
        super(player, true);  // 취소 가능
        this.damage = damage;
        this.damageType = damageType;
    }
    
    public float getDamage() {
        return damage;
    }
    
    /**
     * 데미지 양 수정
     */
    public void setDamage(float damage) {
        this.damage = Math.max(0, damage);
    }
    
    public String getDamageType() {
        return damageType;
    }
}
