package com.echo.pulse;

import com.echo.fuse.ZombieProfiler;
import com.pulse.api.profiler.ZombieHook;

/**
 * Bridge for Zombie profiling hooks.
 */
public class ZombieBridge implements ZombieHook.IZombieCallback {

    private static ZombieBridge INSTANCE;

    private final ThreadLocal<Long> motionStart = new ThreadLocal<>();
    private final ThreadLocal<Long> soundStart = new ThreadLocal<>();
    private final ThreadLocal<Long> trackingStart = new ThreadLocal<>();

    private ZombieBridge() {
    }

    public static void register() {
        if (INSTANCE != null)
            return;
        INSTANCE = new ZombieBridge();
        ZombieHook.setCallback(INSTANCE);

        // Phase 2: Sync fast-flag
        boolean detailsEnabled = com.echo.config.EchoConfig.getInstance().isEnableZombieDetails();

        System.out.println("[Echo] ZombieBridge registered with Pulse (Details: " + detailsEnabled + ")");
    }

    @Override
    public void onMotionUpdateStart() {
        long t = com.echo.measure.SubProfiler.getInstance()
                .startRaw(com.echo.measure.SubProfiler.SubLabel.ZOMBIE_MOTION);
        motionStart.set(t);
    }

    @Override
    public void onMotionUpdateEnd() {
        Long start = motionStart.get();
        if (start != null && start != -1) {
            com.echo.measure.SubProfiler.getInstance().endRaw(com.echo.measure.SubProfiler.SubLabel.ZOMBIE_MOTION,
                    start);
        }
    }

    @Override
    public void onSoundPerceptionStart() {
        long t = com.echo.measure.SubProfiler.getInstance()
                .startRaw(com.echo.measure.SubProfiler.SubLabel.ZOMBIE_PERCEPTION);
        soundStart.set(t);
    }

    @Override
    public void onSoundPerceptionEnd() {
        Long start = soundStart.get();
        if (start != null && start != -1) {
            com.echo.measure.SubProfiler.getInstance().endRaw(com.echo.measure.SubProfiler.SubLabel.ZOMBIE_PERCEPTION,
                    start);
        }
    }

    @Override
    public void onTargetTrackingStart() {
        // Mapping TargetTracking to Perception for now, or Behavior if preferred.
        // Using Perception as it relates to sensing.
        long t = com.echo.measure.SubProfiler.getInstance()
                .startRaw(com.echo.measure.SubProfiler.SubLabel.ZOMBIE_PERCEPTION);
        trackingStart.set(t);
    }

    @Override
    public void onTargetTrackingEnd() {
        Long start = trackingStart.get();
        if (start != null && start != -1) {
            com.echo.measure.SubProfiler.getInstance().endRaw(com.echo.measure.SubProfiler.SubLabel.ZOMBIE_PERCEPTION,
                    start);
        }
    }

    @Override
    public void onZombieUpdate() {
        // Just a counter or check. SubProfiler ZOMBIE_UPDATE is handled by mixin
        // wrapper directly.
        // But for consistency we could increment a counter if needed.
        ZombieProfiler.getInstance().incrementZombieUpdates();
    }
}
