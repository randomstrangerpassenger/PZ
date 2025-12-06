package com.mutagen.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * IsoZombie Mixin.
 * 좀비 업데이트 로직에 훅을 건다.
 */
@Mixin(targets = "zombie.characters.IsoZombie")
public abstract class ZombieMixin {

    @Inject(method = "update", at = @At("HEAD"))
    private void mutagen$onUpdate(CallbackInfo ci) {
        // 좀비가 많으니 가끔만 로그
        if (Math.random() < 0.0001) {
            System.out.println("[Mutagen/Mixin] 🧟 IsoZombie.update() hooked!");
        }
    }
}
