package com.pulse.mixin;

import com.pulse.scheduler.PulseScheduler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * GameClient Mixin.
 * 멀티플레이어 전용 클라이언트 업데이트 훅.
 * 
 * Note: GameTickEvent는 IsoWorldMixin에서만 발행됨 (v0.9 중복 제거).
 * 여기서는 PulseScheduler 틱 처리만 수행.
 */
@Mixin(targets = "zombie.network.GameClient")
public abstract class GameClientMixin {

    /**
     * GameClient.update() 메서드 끝에서 스케줄러 틱 처리
     * Note: update()는 인스턴스 메서드이므로 핸들러도 인스턴스 메서드여야 함
     */
    @Inject(method = "update", at = @At("RETURN"))
    private void Pulse$onUpdate(CallbackInfo ci) {
        // 스케줄러 틱 처리 (멀티플레이어 전용)
        // GameTickEvent는 IsoWorld에서 발행되므로 여기서는 스케줄러만 처리
        PulseScheduler.getInstance().tick();
    }
}
