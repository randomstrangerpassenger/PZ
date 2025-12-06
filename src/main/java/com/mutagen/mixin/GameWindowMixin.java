package com.mutagen.mixin;

import com.mutagen.event.EventBus;
import com.mutagen.event.lifecycle.GameInitEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * GameWindow Mixin.
 * 게임 윈도우 초기화 시점에 GameInitEvent 발생.
 */
@Mixin(targets = "zombie.GameWindow")
public abstract class GameWindowMixin {

    @Unique
    private static boolean mutagen$initEventFired = false;

    /**
     * 게임 윈도우 초기화 완료 시 GameInitEvent 발생 (한 번만)
     */
    @Inject(method = "init", at = @At("RETURN"))
    private static void mutagen$onInit(CallbackInfo ci) {
        if (!mutagen$initEventFired) {
            mutagen$initEventFired = true;
            System.out.println("[Mutagen] Game initialization complete, firing GameInitEvent");
            EventBus.post(new GameInitEvent());
        }
    }
}
