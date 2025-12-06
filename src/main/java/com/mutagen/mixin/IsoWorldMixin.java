package com.mutagen.mixin;

import com.mutagen.event.EventBus;
import com.mutagen.event.lifecycle.WorldLoadEvent;
import com.mutagen.event.lifecycle.WorldUnloadEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * IsoWorld Mixin.
 * 월드 로드/언로드 시 이벤트 발생.
 */
@Mixin(targets = "zombie.iso.IsoWorld")
public abstract class IsoWorldMixin {

    @Shadow
    public abstract String getWorld();

    /**
     * 월드 로드 완료 시점에 WorldLoadEvent 발생
     * init() 메서드 리턴 시점에 호출
     */
    @Inject(method = "init", at = @At("RETURN"))
    private void mutagen$onWorldInit(CallbackInfo ci) {
        String worldName = "Unknown";
        try {
            worldName = getWorld();
            if (worldName == null || worldName.isEmpty()) {
                worldName = "World";
            }
        } catch (Exception e) {
            // 월드 이름을 가져올 수 없는 경우 기본값 사용
        }

        System.out.println("[Mutagen] World loaded: " + worldName);
        EventBus.post(new WorldLoadEvent(worldName));
    }

    /**
     * 월드 언로드 시점에 WorldUnloadEvent 발생
     */
    @Inject(method = "endWorld", at = @At("HEAD"))
    private void mutagen$onWorldEnd(CallbackInfo ci) {
        System.out.println("[Mutagen] World unloading...");
        EventBus.post(new WorldUnloadEvent());
    }
}
