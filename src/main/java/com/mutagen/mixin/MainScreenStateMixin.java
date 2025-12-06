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
        System.out.println("[Mutagen/Mixin] MainScreenState.render() - HEAD");
    }

    @Inject(method = "render", at = @At("RETURN"))
    private void mutagen$onRenderReturn(CallbackInfo ci) {
        // 너무 많은 로그 방지 - 가끔만 출력
        if (Math.random() < 0.01) {
            System.out.println("[Mutagen/Mixin] MainScreenState.render() - RETURN");
        }
    }
}
