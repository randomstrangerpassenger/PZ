package com.fuse.hook;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.ZombieHook;

/**
 * Fuse Hook Adapter - ZombieHook 콜백 구현.
 * 
 * Pulse API만 사용 (Echo 의존성 없음).
 * ZombieHook.IZombieCallback을 통해 데이터를 수집.
 * 
 * Phase 4: stub에서 복원 - IZombieCallback 구현
 * 
 * @since Fuse 0.3.0
 * @since Fuse 0.4.0 - Phase 4: IZombieCallback 구현 복원
 */
public class FuseHookAdapter implements ZombieHook.IZombieCallback {

    private static final String LOG = "Fuse";

    // 타이밍 측정용
    private long motionStartNanos = -1;
    private long perceptionStartNanos = -1;
    private long trackingStartNanos = -1;

    // 내부 통계
    private long zombieUpdateCount = 0;
    private long totalMotionMicros = 0;
    private long totalPerceptionMicros = 0;
    private long totalTrackingMicros = 0;

    // 현재 처리 중인 좀비
    private Object currentZombie = null;

    public FuseHookAdapter() {
        PulseLogger.info(LOG, "HookAdapter initialized (Phase 4 - IZombieCallback)");
    }

    // --- Registration ---

    public static FuseHookAdapter register() {
        FuseHookAdapter adapter = new FuseHookAdapter();
        ZombieHook.setCallback(adapter);
        ZombieHook.profilingEnabled = true;
        PulseLogger.info("Fuse", "ZombieHook callback registered");
        return adapter;
    }

    public static void unregister() {
        ZombieHook.clearCallback();
        ZombieHook.profilingEnabled = false;
        PulseLogger.info("Fuse", "ZombieHook callback unregistered");
    }

    // --- IZombieCallback Implementation ---

    @Override
    public void onZombieUpdateWithContext(Object zombie) {
        currentZombie = zombie;
        zombieUpdateCount++;
    }

    @Override
    public void onMotionUpdateStartWithContext(Object zombie) {
        currentZombie = zombie;
        motionStartNanos = System.nanoTime();
    }

    @Override
    public void onMotionUpdateEndWithContext(Object zombie) {
        if (motionStartNanos > 0) {
            long durationMicros = (System.nanoTime() - motionStartNanos) / 1000;
            totalMotionMicros += durationMicros;
            motionStartNanos = -1;
        }
        currentZombie = null;
    }

    @Override
    public void onSoundPerceptionStartWithContext(Object zombie) {
        currentZombie = zombie;
        perceptionStartNanos = System.nanoTime();
    }

    @Override
    public void onSoundPerceptionEndWithContext(Object zombie) {
        if (perceptionStartNanos > 0) {
            long durationMicros = (System.nanoTime() - perceptionStartNanos) / 1000;
            totalPerceptionMicros += durationMicros;
            perceptionStartNanos = -1;
        }
    }

    @Override
    public void onTargetTrackingStartWithContext(Object zombie) {
        currentZombie = zombie;
        trackingStartNanos = System.nanoTime();
    }

    @Override
    public void onTargetTrackingEndWithContext(Object zombie) {
        if (trackingStartNanos > 0) {
            long durationMicros = (System.nanoTime() - trackingStartNanos) / 1000;
            totalTrackingMicros += durationMicros;
            trackingStartNanos = -1;
        }
    }

    // --- Getters ---

    public Object getCurrentZombie() {
        return currentZombie;
    }

    public long getZombieUpdateCount() {
        return zombieUpdateCount;
    }

    public long getTotalMotionMicros() {
        return totalMotionMicros;
    }

    public long getTotalPerceptionMicros() {
        return totalPerceptionMicros;
    }

    public long getTotalTrackingMicros() {
        return totalTrackingMicros;
    }

    public void resetStats() {
        zombieUpdateCount = 0;
        totalMotionMicros = 0;
        totalPerceptionMicros = 0;
        totalTrackingMicros = 0;
    }

    public void printStatus() {
        PulseLogger.info(LOG, "HookAdapter Stats:");
        PulseLogger.info(LOG, "  Zombie Updates: " + zombieUpdateCount);
        PulseLogger.info(LOG, "  Motion: " + (totalMotionMicros / 1000) + "ms");
        PulseLogger.info(LOG, "  Perception: " + (totalPerceptionMicros / 1000) + "ms");
        PulseLogger.info(LOG, "  Tracking: " + (totalTrackingMicros / 1000) + "ms");
    }
}
