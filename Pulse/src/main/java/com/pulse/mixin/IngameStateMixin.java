package com.pulse.mixin;

import com.pulse.event.EventBus;
import com.pulse.api.event.gui.GuiRenderEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * IngameState Mixin.
 * 인게임 렌더링 훅을 제공합니다.
 * 
 * <p>
 * GuiRenderEvent를 발행하여 Echo가 FPS를 측정할 수 있도록 합니다.
 * </p>
 * 
 * @since Pulse 2.2 - 인게임 렌더링 이벤트 발행
 */
@Mixin(targets = "zombie.gameStates.IngameState")
public abstract class IngameStateMixin {

    @Unique
    private static long Pulse$frameCount = 0;

    @Unique
    private static long Pulse$lastLogTime = 0;

    /**
     * IngameState.render() 시작 시점에 GuiRenderEvent 발생.
     */
    @Inject(method = "render", at = @At("HEAD"))
    private void Pulse$onRenderHead(CallbackInfo ci) {
        try {
            Pulse$frameCount++;

            // PulseMetrics 프레임 시작 알림
            com.pulse.api.PulseMetrics.onFrameStart();

            // GuiRenderEvent 발행 - Echo RenderProfiler가 FPS 측정
            GuiRenderEvent event = new GuiRenderEvent(null, "IngameState", 0);
            EventBus.post(event);

            // 5초마다 프레임 카운트 로그 (디버그)
            long now = System.currentTimeMillis();
            if (now - Pulse$lastLogTime >= 5000) {
                if (Pulse$lastLogTime > 0) {
                    long elapsed = now - Pulse$lastLogTime;
                    double fps = (Pulse$frameCount * 1000.0) / elapsed;
                    com.pulse.api.log.PulseLogger.debug("Pulse",
                            String.format("IngameState render: %d frames, %.1f FPS", Pulse$frameCount, fps));
                }
                Pulse$lastLogTime = now;
                Pulse$frameCount = 0;
            }
        } catch (Throwable t) {
            PulseErrorHandler.reportMixinFailure("IngameStateMixin.onRenderHead", t);
        }
    }
}
