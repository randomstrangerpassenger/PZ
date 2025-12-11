package com.pulse.mixin;

import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.event.lifecycle.GameTickStartEvent;
import com.pulse.event.lifecycle.GameTickEndEvent;
import com.pulse.event.lifecycle.WorldLoadEvent;
import com.pulse.hook.HookTypes;
import com.pulse.hook.PulseHookRegistry;
import com.pulse.scheduler.PulseScheduler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * IsoWorld Mixin.
 * 월드 로드/언로드 및 게임 틱 이벤트 발생.
 * 
 * Note: IsoWorld.update()는 싱글플레이어와 멀티플레이어 모두에서 호출됨.
 * GameClient.update()는 멀티플레이어 전용이므로 여기서 GameTickEvent를 발생시킴.
 * 
 * @since Pulse 1.0
 * @since Pulse 1.2 - GameTickStartEvent/GameTickEndEvent, HookRegistry 통합
 */
@Mixin(targets = "zombie.iso.IsoWorld")
public abstract class IsoWorldMixin {

    @Shadow
    public abstract String getWorld();

    // Echo 2.0 Phase 2: LOS Hook
    @Inject(method = "checkLineOfSight(Lzombie/iso/IsoGridSquare;Lzombie/iso/IsoGridSquare;)Z", at = @At("HEAD"))
    private void Pulse$onCheckLineOfSightStart(CallbackInfoReturnable<Boolean> cir) {
        if (com.pulse.api.profiler.PathfindingHook.enabled) {
            com.pulse.api.profiler.PathfindingHook.onLosCalculationStart();
        }
    }

    @Inject(method = "checkLineOfSight(Lzombie/iso/IsoGridSquare;Lzombie/iso/IsoGridSquare;)Z", at = @At("RETURN"))
    private void Pulse$onCheckLineOfSightEnd(CallbackInfoReturnable<Boolean> cir) {
        if (com.pulse.api.profiler.PathfindingHook.enabled) {
            com.pulse.api.profiler.PathfindingHook.onLosCalculationEnd();
        }
    }

    @Unique
    private static long Pulse$tickCount = 0;

    @Unique
    private static long Pulse$lastTickTime = System.nanoTime();

    @Unique
    private static boolean Pulse$firstTickLogged = false;

    // Pulse 1.2: Tick 시작 시간 (정밀 측정용)
    @Unique
    private static long Pulse$tickStartNanos = -1;

    // Echo 1.0: SubProfiler 시작 시간
    @Unique
    private static long Pulse$worldUpdateStart = -1;

    /**
     * 월드 로드 완료 시점에 WorldLoadEvent 발생
     * init() 메서드 리턴 시점에 호출
     */
    @Inject(method = "init", at = @At("RETURN"))
    private void Pulse$onWorldInit(CallbackInfo ci) {
        String worldName = "Unknown";
        try {
            worldName = getWorld();
            if (worldName == null || worldName.isEmpty()) {
                worldName = "World";
            }
        } catch (Exception e) {
            // 월드 이름을 가져올 수 없는 경우 기본값 사용
        }

        // 틱 카운터 리셋
        Pulse$tickCount = 0;
        Pulse$lastTickTime = System.nanoTime();
        Pulse$firstTickLogged = false;

        System.out.println("[Pulse] World loaded: " + worldName);
        EventBus.post(new WorldLoadEvent(worldName));
    }

    /**
     * IsoWorld.update() 시작 시점
     */
    @Inject(method = "update", at = @At("HEAD"))
    private void Pulse$onUpdateStart(CallbackInfo ci) {
        // Pulse 1.2: 틱 시작 시간 기록
        Pulse$tickStartNanos = System.nanoTime();

        // Pulse 1.3: PulseMetrics 틱 시작 알림 (Echo 연동)
        com.pulse.api.PulseMetrics.onTickStart();

        // Pulse 1.2: GameTickStartEvent 발생
        EventBus.post(new GameTickStartEvent(Pulse$tickCount + 1));

        // Pulse 1.2: HookRegistry 콜백 호출
        final long tickNum = Pulse$tickCount + 1;
        PulseHookRegistry.broadcast(HookTypes.GAME_TICK, cb -> cb.onGameTickStart(tickNum));

        // Echo 1.0: WORLD_UPDATE Phase Start
        Pulse$worldUpdateStart = com.pulse.api.profiler.TickPhaseHook.startPhase("WORLD_UPDATE");
    }

    /**
     * IsoWorld.update()에서 GameTickEvent 발생
     * 이 메서드는 싱글플레이어와 멀티플레이어 모두에서 매 프레임 호출됨
     */
    @Inject(method = "update", at = @At("RETURN"))
    private void Pulse$onUpdate(CallbackInfo ci) {
        // Echo 1.0: WORLD_UPDATE Phase End
        com.pulse.api.profiler.TickPhaseHook.endPhase("WORLD_UPDATE", Pulse$worldUpdateStart);
        Pulse$worldUpdateStart = -1;

        long currentTime = System.nanoTime();

        // Pulse 1.2: 정밀 틱 소요 시간 계산
        long tickDurationNanos = currentTime - Pulse$tickStartNanos;

        // Pulse 1.3: PulseMetrics 틱 종료 알림 (Echo 연동)
        com.pulse.api.PulseMetrics.onTickEnd(tickDurationNanos);

        float deltaTime = (currentTime - Pulse$lastTickTime) / 1_000_000_000.0f;
        Pulse$lastTickTime = currentTime;

        Pulse$tickCount++;

        // 첫 틱 디버그 로그
        if (!Pulse$firstTickLogged) {
            Pulse$firstTickLogged = true;
            System.out.println("[Pulse] First IsoWorld.update() tick! GameTickEvent will now fire.");
        }

        // 매 1000번째 틱마다 상태 로그
        if (Pulse$tickCount % 1000 == 0) {
            System.out.printf("[Pulse/DEBUG] IsoWorld tick #%d, deltaTime=%.4f%n", Pulse$tickCount, deltaTime);
        }

        // 스케줄러 틱 처리
        PulseScheduler.getInstance().tick();

        // Tick Phase 완료 알림
        com.pulse.api.profiler.TickPhaseHook.onTickComplete();

        // Pulse 1.2: GameTickEndEvent 발생 (정밀 소요 시간 포함)
        EventBus.post(new GameTickEndEvent(Pulse$tickCount, tickDurationNanos));

        // Pulse 1.2: HookRegistry 콜백 호출
        final long tickNum = Pulse$tickCount;
        final long duration = tickDurationNanos;
        PulseHookRegistry.broadcast(HookTypes.GAME_TICK, cb -> cb.onGameTickEnd(tickNum, duration));

        // 기존 GameTickEvent 발생 (하위 호환성)
        EventBus.post(new GameTickEvent(Pulse$tickCount, deltaTime));
    }
}
