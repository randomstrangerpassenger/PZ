package com.pulse.mixin;

import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.MainMenuRenderEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * MainScreenState Mixin.
 * 게임 메인 화면 렌더링에 훅을 건다.
 * 
 * @since Pulse 2.1 - MainMenuRenderEvent 발생 (Echo에서 세션 종료 감지)
 */
@Mixin(targets = "zombie.gameStates.MainScreenState")
public abstract class MainScreenStateMixin {

    @Inject(method = "render", at = @At("HEAD"))
    private void Pulse$onRenderHead(CallbackInfo ci) {
        try {
            // Pulse 1.3: 프레임 시작 알림 (Echo PulseMetrics 연동)
            com.pulse.api.PulseMetrics.onFrameStart();

            // v2.1: MainMenuRenderEvent 발생 - Echo가 세션 종료 감지
            EventBus.post(new MainMenuRenderEvent());
        } catch (Throwable t) {
            if (com.pulse.PulseEnvironment.isDevelopmentMode()) {
                throw t;
            }
            PulseErrorHandler.reportMixinFailure("MainScreenStateMixin.onRenderHead", t);
        }
    }

    @Inject(method = "render", at = @At("RETURN"))
    private void Pulse$onRenderReturn(CallbackInfo ci) {
        // 렌더링 완료 훅 - 필요시 여기에 로직 추가
    }
}
