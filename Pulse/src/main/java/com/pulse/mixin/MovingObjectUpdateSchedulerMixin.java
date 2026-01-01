package com.pulse.mixin;

import com.pulse.api.profiler.TickPhaseHook;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * MovingObjectUpdateScheduler Mixin.
 * 
 * AI_PHASE 측정을 위한 훅을 제공합니다.
 * 
 * <p>
 * MovingObjectUpdateScheduler.update()는 틱당 1회 호출되며,
 * 모든 MovingObject (좀비, 플레이어, 차량 등)의 update()를 실행합니다.
 * 이는 AI/게임 로직 업데이트의 총 시간을 측정하기에 이상적인 지점입니다.
 * </p>
 * 
 * @since Pulse 1.3
 */
@Mixin(targets = "zombie.MovingObjectUpdateScheduler")
public abstract class MovingObjectUpdateSchedulerMixin {

    /**
     * AI_PHASE 시작 시간 (startPhase 반환값).
     */
    @Unique
    private long pulse$aiPhaseStart = -1;

    /**
     * MovingObjectUpdateScheduler.update() 시작 시 AI_PHASE 측정 시작.
     */
    @Inject(method = "update", at = @At("HEAD"))
    private void pulse$onAiUpdateStart(CallbackInfo ci) {
        pulse$aiPhaseStart = TickPhaseHook.startPhase(TickPhaseHook.PHASE_AI_UPDATE);
    }

    /**
     * MovingObjectUpdateScheduler.update() 종료 시 AI_PHASE 측정 종료.
     */
    @Inject(method = "update", at = @At("RETURN"))
    private void pulse$onAiUpdateEnd(CallbackInfo ci) {
        TickPhaseHook.endPhase(TickPhaseHook.PHASE_AI_UPDATE, pulse$aiPhaseStart);
        pulse$aiPhaseStart = -1;
    }
}
