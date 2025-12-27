package com.pulse.mixin;

import com.pulse.event.EventBus;
import com.pulse.api.event.lifecycle.GameInitEvent;
import com.pulse.api.log.PulseLogger;
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
    private static final String Pulse$LOG = PulseLogger.PULSE;

    @Unique
    private static boolean Pulse$initEventFired = false;

    /**
     * 게임 윈도우 초기화 완료 시 GameInitEvent 발생 (한 번만)
     */
    @Inject(method = "init", at = @At("RETURN"))
    private static void Pulse$onInit(CallbackInfo ci) {
        if (!Pulse$initEventFired) {
            Pulse$initEventFired = true;
            PulseLogger.info(Pulse$LOG, "Game initialization complete, firing GameInitEvent");
            EventBus.post(new GameInitEvent());
        }
    }
}
