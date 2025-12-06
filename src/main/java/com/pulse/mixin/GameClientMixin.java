package com.pulse.mixin;

import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.scheduler.PulseScheduler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * GameClient Mixin.
 * 게임 클라이언트의 메인 업데이트 루프에 훅을 걸어 GameTickEvent 발생.
 */
@Mixin(targets = "zombie.network.GameClient")
public abstract class GameClientMixin {

    @Unique
    private static long Pulse$tickCount = 0;

    @Unique
    private static long Pulse$lastTickTime = System.nanoTime();

    /**
     * GameClient.update() 메서드 끝에서 GameTickEvent 발생 및 스케줄러 틱 처리
     */
    @Inject(method = "update", at = @At("RETURN"))
    private static void Pulse$onUpdate(CallbackInfo ci) {
        long currentTime = System.nanoTime();
        float deltaTime = (currentTime - Pulse$lastTickTime) / 1_000_000_000.0f;
        Pulse$lastTickTime = currentTime;

        Pulse$tickCount++;

        // 스케줄러 틱 처리
        PulseScheduler.getInstance().tick();

        // GameTickEvent 발생
        EventBus.post(new GameTickEvent(Pulse$tickCount, deltaTime));
    }
}
