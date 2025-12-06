package com.mutagen.mixin;

import com.mutagen.event.EventBus;
import com.mutagen.event.lifecycle.GameTickEvent;
import com.mutagen.scheduler.MutagenScheduler;
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
    private static long mutagen$tickCount = 0;

    @Unique
    private static long mutagen$lastTickTime = System.nanoTime();

    /**
     * GameClient.update() 메서드 끝에서 GameTickEvent 발생 및 스케줄러 틱 처리
     */
    @Inject(method = "update", at = @At("RETURN"))
    private static void mutagen$onUpdate(CallbackInfo ci) {
        long currentTime = System.nanoTime();
        float deltaTime = (currentTime - mutagen$lastTickTime) / 1_000_000_000.0f;
        mutagen$lastTickTime = currentTime;

        mutagen$tickCount++;

        // 스케줄러 틱 처리
        MutagenScheduler.getInstance().tick();

        // GameTickEvent 발생
        EventBus.post(new GameTickEvent(mutagen$tickCount, deltaTime));
    }
}
