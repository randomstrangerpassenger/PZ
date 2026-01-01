package com.pulse.api.hook;

/**
 * Zombie 콜백 인터페이스.
 * 
 * 프로파일러 모드가 구현하여 좀비 관련 이벤트를 수신합니다.
 * 
 * @since Pulse 2.0
 */
public interface IZombieCallback {

    default void onZombieUpdate() {
    }

    default void onMotionUpdateStart() {
    }

    default void onMotionUpdateEnd() {
    }

    default void onSoundPerceptionStart() {
    }

    default void onSoundPerceptionEnd() {
    }

    default void onTargetTrackingStart() {
    }

    default void onTargetTrackingEnd() {
    }

    default void onZombieUpdateWithContext(Object zombie) {
        onZombieUpdate();
    }

    default void onMotionUpdateStartWithContext(Object zombie) {
        onMotionUpdateStart();
    }

    default void onMotionUpdateEndWithContext(Object zombie) {
        onMotionUpdateEnd();
    }

    default void onSoundPerceptionStartWithContext(Object zombie) {
        onSoundPerceptionStart();
    }

    default void onSoundPerceptionEndWithContext(Object zombie) {
        onSoundPerceptionEnd();
    }

    default void onTargetTrackingStartWithContext(Object zombie) {
        onTargetTrackingStart();
    }

    default void onTargetTrackingEndWithContext(Object zombie) {
        onTargetTrackingEnd();
    }

    // Phase 2: New Event Hooks
    default void onZombieSpotted(Object target, boolean forced) {
    }

    default void onZombieSpottedWithContext(Object zombie, Object target, boolean forced) {
        onZombieSpotted(target, forced);
    }

    default void onZombieHit(Object attacker, float damage) {
    }

    default void onZombieHitWithContext(Object zombie, Object attacker, float damage) {
        onZombieHit(attacker, damage);
    }

    default void onZombieKill(Object killer) {
    }

    default void onZombieKillWithContext(Object zombie, Object killer) {
        onZombieKill(killer);
    }
}
