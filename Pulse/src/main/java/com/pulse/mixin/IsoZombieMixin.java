package com.pulse.mixin;

import com.pulse.api.profiler.SubProfilerHook;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * IsoZombie Mixin.
 * 좀비 업데이트 측정을 위한 SubProfiler 후킹.
 * 
 * @since Pulse 1.1 / Echo 1.0
 */
@Mixin(targets = "zombie.characters.IsoZombie")
public abstract class IsoZombieMixin {

    // Echo 1.0: SubProfiler 시작 시간
    @Unique
    private long Pulse$zombieUpdateStart = -1;

    /**
     * IsoZombie.update() 시작 시점
     */
    @Inject(method = "update", at = @At("HEAD"))
    private void Pulse$onZombieUpdateStart(CallbackInfo ci) {
        Pulse$zombieUpdateStart = SubProfilerHook.start("ZOMBIE_UPDATE");
        com.pulse.api.profiler.ZombieHook.onZombieUpdate();

        // Phase 2: Detailed Profiling
        // Currently wrapped at HEAD, so it effectively measures Total unless we move
        // this injection.
        // But we guard it nonetheless.
        if (com.pulse.api.profiler.ZombieHook.detailsEnabled) {
            com.pulse.api.profiler.ZombieHook.onMotionUpdateStart();
        }
    }

    /**
     * IsoZombie.update() 종료 시점
     */
    @Inject(method = "update", at = @At("RETURN"))
    private void Pulse$onZombieUpdateEnd(CallbackInfo ci) {
        if (com.pulse.api.profiler.ZombieHook.detailsEnabled) {
            com.pulse.api.profiler.ZombieHook.onMotionUpdateEnd();
        }
        SubProfilerHook.end("ZOMBIE_UPDATE", Pulse$zombieUpdateStart);
        Pulse$zombieUpdateStart = -1;
    }
}
