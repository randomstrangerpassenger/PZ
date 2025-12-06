package com.mutagen.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * MainScreenState Mixin.
 * 게임 메인 화면 렌더링에 훅을 건다.
 */
@Mixin(targets = "zombie.gameStates.MainScreenState")
public abstract class MainScreenStateMixin {

    @Inject(method = "render", at = @At("HEAD"))
    private void mutagen$onRenderHead(CallbackInfo ci) {
        // 렌더링 훅 - 필요시 여기에 로직 추가
    }

    @Inject(method = "render", at = @At("RETURN"))
    private void mutagen$onRenderReturn(CallbackInfo ci) {
        // 렌더링 완료 훅 - 필요시 여기에 로직 추가
    }
}
