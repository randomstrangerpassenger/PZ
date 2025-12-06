package com.pulse.mixin;

import com.pulse.event.EventBus;
import com.pulse.event.player.PlayerDamageEvent;
import com.pulse.event.player.PlayerUpdateEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * IsoPlayer Mixin.
 * 플레이어 업데이트 및 데미지 처리 훅.
 */
@Mixin(targets = "zombie.characters.IsoPlayer")
public abstract class IsoPlayerMixin {

    /**
     * 플레이어 업데이트 시 PlayerUpdateEvent 발생
     */
    @Inject(method = "update", at = @At("HEAD"))
    private void Pulse$onUpdate(CallbackInfo ci) {
        // this는 IsoPlayer 인스턴스
        EventBus.post(new PlayerUpdateEvent(this));
    }

    /**
     * 플레이어가 데미지를 받을 때 PlayerDamageEvent 발생
     * Hit() 메서드 시작 시점에 호출
     *
     * 참고: Project Zomboid의 실제 데미지 메서드 시그니처에 따라 조정 필요
     */
    @Inject(method = "Hit", at = @At("HEAD"), cancellable = true)
    private void Pulse$onHit(
            /* 실제 파라미터는 게임 버전에 따라 다를 수 있음 */
            CallbackInfo ci) {

        // 기본 데미지 값 (실제로는 파라미터에서 가져와야 함)
        float damage = 10.0f;
        String damageType = "unknown";

        PlayerDamageEvent event = new PlayerDamageEvent(this, damage, damageType);
        EventBus.post(event);

        // 이벤트가 취소되었으면 원래 메서드 실행 취소
        if (event.isCancelled()) {
            ci.cancel();
        }
    }
}
