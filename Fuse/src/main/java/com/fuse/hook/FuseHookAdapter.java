package com.fuse.hook;

import com.pulse.api.profiler.ProfilerBridge;
import com.pulse.api.profiler.ZombieHook;

/**
 * Fuse Hook Adapter - ZombieHook 콜백 구현.
 * 
 * Pulse API만 사용 (Echo 의존성 없음).
 * ProfilerBridge를 통해 데이터를 Echo로 전달.
 * 
 * Phase 1.5: WithContext 메서드로 zombie 객체 접근 가능
 * 
 * @since Fuse 0.3.0
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

    // Phase 1.5: 현재 처리 중인 좀비 (Phase 2 throttling용)
    private Object currentZombie = null;

    public FuseHookAdapter() {
        System.out.println("[" + LOG + "] HookAdapter initialized (Phase 1.5 - WithContext)");
    }

    // --- Phase 1.5: WithContext 오버라이드 ---

    @Override
    public void onZombieUpdateWithContext(Object zombie) {
        currentZombie = zombie;
        zombieUpdateCount++;
        ProfilerBridge.incrementZombieUpdates();

        // Phase 2: 여기서 shouldSkip(zombie) 체크 가능
        // if (throttleController.shouldSkip(zombie)) { return; }
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

            ProfilerBridge.recordZombieStep("MOTION_UPDATE", durationMicros);
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

            ProfilerBridge.recordZombieStep("SOUND_PERCEPTION", durationMicros);
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

            ProfilerBridge.recordZombieStep("TARGET_TRACKING", durationMicros);
        }
    }

    // --- Original methods (delegate to WithContext) ---

    @Override
    public void onZombieUpdate() {
        onZombieUpdateWithContext(null);
    }

    @Override
    public void onMotionUpdateStart() {
        onMotionUpdateStartWithContext(null);
    }

    @Override
    public void onMotionUpdateEnd() {
        onMotionUpdateEndWithContext(null);
    }

    @Override
    public void onSoundPerceptionStart() {
        onSoundPerceptionStartWithContext(null);
    }

    @Override
    public void onSoundPerceptionEnd() {
        onSoundPerceptionEndWithContext(null);
    }

    @Override
    public void onTargetTrackingStart() {
        onTargetTrackingStartWithContext(null);
    }

    @Override
    public void onTargetTrackingEnd() {
        onTargetTrackingEndWithContext(null);
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
        System.out.println("[" + LOG + "] HookAdapter Stats:");
        System.out.println("  Zombie Updates: " + zombieUpdateCount);
        System.out.println("  Motion: " + (totalMotionMicros / 1000) + "ms");
        System.out.println("  Perception: " + (totalPerceptionMicros / 1000) + "ms");
        System.out.println("  Tracking: " + (totalTrackingMicros / 1000) + "ms");
        System.out.println("  ProfilerBridge Sink: " + ProfilerBridge.hasSink());
    }
}
